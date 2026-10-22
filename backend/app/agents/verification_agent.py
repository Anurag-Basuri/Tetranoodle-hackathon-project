import uuid
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, HttpUrl
from app.domain.enums import AgentName, CriterionKind, FundingType, VerificationStatus, OpportunityKind, SourceType
from app.domain.opportunity import Candidate, Opportunity
from app.domain.evidence import Criterion, EvidenceRef
from app.agents.base import run_agent
from app.agents.state import AgentWarning
from app.tools.fetcher import fetch_page_content
from app.tools.retrieval import select_chunks
from app.tools.quote_check import verify_excerpt
from app.providers.router import call_with_fallback
from app.config import get_settings

class RawCriterion(BaseModel):
    kind: CriterionKind
    description: str
    required_value: Optional[str] = None
    source_excerpt: Optional[str] = None
    is_hard: bool = True

class ExtractedCriteriaBundle(BaseModel):
    # LLM extraction model for official admissions pages
    program_name: Optional[str] = None
    institution: Optional[str] = None
    country: Optional[str] = None
    funding_type: FundingType = FundingType.UNSPECIFIED
    funding_detail: Optional[str] = None
    funding_excerpt: Optional[str] = None
    deadline_date: Optional[str] = None
    deadline_excerpt: Optional[str] = None
    application_steps: List[str] = []
    criteria: List[RawCriterion] = []

async def verify_candidate_pipeline(candidate: Candidate, job_id: str) -> Dict[str, Any]:
    # Verification Agent: crawls official page, validates quotes, and extracts structured criteria
    settings = get_settings()
    warnings: List[AgentWarning] = []

    async def execute():
        fetch_res = await fetch_page_content(str(candidate.url))

        # Handle crawl failure gracefully without killing job
        if fetch_res.status != "ok" or not fetch_res.text_content:
            warnings.append(AgentWarning(
                agent=AgentName.VERIFY,
                scope=str(candidate.id),
                message=f"Could not fetch {candidate.url} ({fetch_res.error or 'empty text'}); kept unverified discovery data.",
            ))
            unverified_opp = Opportunity(
                id=candidate.id,
                job_id=uuid.UUID(job_id) if isinstance(job_id, str) else job_id,
                name=candidate.name,
                institution=candidate.institution,
                country=candidate.country,
                kind=OpportunityKind.SCHOLARSHIP,
                official_url=candidate.url,
                funding_type=FundingType.UNSPECIFIED,
                verification_status=VerificationStatus.UNVERIFIED,
                discovery_sources=[str(candidate.url)],
                candidate_notes=candidate.snippet,
            )
            return {"opportunities": {str(candidate.id): unverified_opp}, "warnings": warnings}

        # BM25 chunk selection to fit within model prompt budget
        top_chunks = select_chunks(fetch_res.text_content, max_tokens=4000)
        context_text = "\n\n--- Chunk ---\n\n".join(top_chunks)

        from app.providers.llm_gemini import GeminiLLMProvider
        from app.providers.llm_groq import GroqLLMProvider

        gemini = GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
        groq = GroqLLMProvider(api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL)

        prompt = (
            f"Extract structured eligibility criteria, funding terms, deadline, and application steps "
            f"for '{candidate.name}' from the official web page excerpt below.\n\n"
            f"For each criterion, copy the EXACT verbatim excerpt from the text that proves it.\n\n"
            f"Web Page Context:\n{context_text}"
        )
        messages = [{"role": "user", "content": prompt}]

        try:
            res = await call_with_fallback(
                [gemini, groq],
                lambda p: p.generate(task="verification", messages=messages, schema=ExtractedCriteriaBundle),
            )
            bundle: ExtractedCriteriaBundle = res.value
        except Exception as e:
            # Fallback to unverified candidate if LLM extraction fails
            warnings.append(AgentWarning(
                agent=AgentName.VERIFY,
                scope=str(candidate.id),
                message=f"Criteria extraction failed for {candidate.name}: {e}",
            ))
            opp = Opportunity(
                id=candidate.id,
                job_id=uuid.UUID(job_id) if isinstance(job_id, str) else job_id,
                name=candidate.name,
                institution=candidate.institution,
                country=candidate.country,
                verification_status=VerificationStatus.UNVERIFIED,
                discovery_sources=[str(candidate.url)],
            )
            return {"opportunities": {str(candidate.id): opp}, "warnings": warnings}

        now_utc = datetime.utcnow()
        source_id = uuid.uuid4()

        # Quote verification on funding evidence
        funding_ev = None
        if bundle.funding_excerpt:
            f_ok, _ = verify_excerpt(bundle.funding_excerpt, fetch_res.text_content)
            funding_ev = EvidenceRef(
                source_id=source_id,
                source_url=candidate.url,
                source_excerpt=bundle.funding_excerpt,
                verified_at=now_utc,
                quote_verified=f_ok,
            )

        # Parse and quote-verify deadline
        deadline_date = None
        deadline_ev = None
        if bundle.deadline_date:
            try:
                deadline_date = date.fromisoformat(bundle.deadline_date[:10])
            except ValueError:
                deadline_date = None

        if bundle.deadline_excerpt:
            d_ok, _ = verify_excerpt(bundle.deadline_excerpt, fetch_res.text_content)
            deadline_ev = EvidenceRef(
                source_id=source_id,
                source_url=candidate.url,
                source_excerpt=bundle.deadline_excerpt,
                verified_at=now_utc,
                quote_verified=d_ok,
            )

        # Validate each individual criterion excerpt against raw page
        verified_criteria: List[Criterion] = []
        for idx, raw_c in enumerate(bundle.criteria):
            crit_id = f"{candidate.id}:{raw_c.kind.value}:{idx + 1}"
            crit_ev = None

            if raw_c.source_excerpt:
                q_ok, _ = verify_excerpt(raw_c.source_excerpt, fetch_res.text_content)
                crit_ev = EvidenceRef(
                    source_id=source_id,
                    source_url=candidate.url,
                    source_excerpt=raw_c.source_excerpt,
                    verified_at=now_utc,
                    quote_verified=q_ok,
                )

            params = {}
            if raw_c.kind == CriterionKind.DEGREE_LEVEL and raw_c.required_value:
                params["min_level"] = raw_c.required_value
            elif raw_c.kind == CriterionKind.MIN_GRADE and raw_c.required_value:
                params["rule_text"] = raw_c.required_value
            elif raw_c.kind == CriterionKind.DEADLINE and deadline_date:
                params["date"] = str(deadline_date)

            verified_criteria.append(Criterion(
                id=crit_id,
                kind=raw_c.kind,
                description=raw_c.description,
                required_value=raw_c.required_value,
                params=params,
                is_hard=raw_c.is_hard,
                evidence=crit_ev,
            ))

        # Classify overall verification status
        if fetch_res.source_type == SourceType.OFFICIAL:
            verified_count = sum(1 for c in verified_criteria if c.evidence and c.evidence.quote_verified)
            if verified_count == len(verified_criteria) and len(verified_criteria) > 0:
                v_status = VerificationStatus.VERIFIED
            else:
                v_status = VerificationStatus.PARTIAL
        else:
            # Aggregator sources remain unverified per official source rule
            v_status = VerificationStatus.UNVERIFIED

        final_opp = Opportunity(
            id=candidate.id,
            job_id=uuid.UUID(job_id) if isinstance(job_id, str) else job_id,
            name=bundle.program_name or candidate.name,
            institution=bundle.institution or candidate.institution,
            country=bundle.country or candidate.country,
            kind=OpportunityKind.SCHOLARSHIP,
            official_url=candidate.url,
            funding_type=bundle.funding_type,
            funding_detail=bundle.funding_detail,
            funding_evidence=funding_ev,
            deadline=deadline_date,
            deadline_evidence=deadline_ev,
            application_steps=bundle.application_steps,
            criteria=verified_criteria,
            verification_status=v_status,
            discovery_sources=[str(candidate.url)],
            candidate_notes=candidate.snippet,
        )

        return {
            "opportunities": {str(candidate.id): final_opp},
            "warnings": warnings,
        }

    def fallback(err: Exception) -> Dict[str, Any]:
        return {
            "opportunities": {},
            "warnings": [AgentWarning(
                agent=AgentName.VERIFY,
                scope=str(candidate.id),
                message=f"Candidate verification failed: {err}",
            )],
        }

    return await run_agent(AgentName.VERIFY, str(candidate.id), execute, fallback)
