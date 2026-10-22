from typing import Dict, Any, List
from pydantic import BaseModel
from app.domain.enums import AgentName, OverallEligibility
from app.domain.opportunity import Opportunity, RankedOpportunity
from app.domain.profile import StudentProfile
from app.domain.evidence import CriterionAssessment
from app.domain.ranking import rank_opportunities
from app.agents.state import ResearchState, AgentWarning
from app.agents.base import run_agent
from app.providers.router import call_with_fallback
from app.config import get_settings

class DraftSOPOutput(BaseModel):
    # Model for generated statement of purpose draft
    title: str
    content_markdown: str
    cited_evidence: List[str] = []

async def rank_and_select_node(state: ResearchState) -> Dict[str, Any]:
    # Ranking Agent: computes composite scores, enforces diversity cap, and selects Top 5
    opportunities = list(state.get("opportunities", {}).values())
    assessments_by_opp = state.get("assessments", {})
    profile = state.get("profile") or state["profile_input"]
    warnings: List[AgentWarning] = []

    async def execute():
        overall_by_opp = {}
        for opp in opportunities:
            opp_id_str = str(opp.id)
            ass_list = assessments_by_opp.get(opp_id_str, [])
            from app.domain.criteria_rules import derive_overall
            overall_by_opp[opp_id_str] = derive_overall(ass_list, opp.verification_status)

        # Execute deterministic ranking
        ranked_top = rank_opportunities(
            opportunities=opportunities,
            assessments_by_opp=assessments_by_opp,
            overall_by_opp=overall_by_opp,
            profile=profile,
        )

        return {
            "ranking": ranked_top,
            "warnings": warnings,
        }

    def fallback(err: Exception) -> Dict[str, Any]:
        return {
            "ranking": [],
            "warnings": [AgentWarning(
                agent=AgentName.RANKING,
                scope="global",
                message=f"Ranking execution failed: {err}",
            )],
        }

    return await run_agent(AgentName.RANKING, "global", execute, fallback)

async def generate_application_draft(
    opportunity: Opportunity,
    profile: StudentProfile,
    assessments: List[CriterionAssessment],
) -> DraftSOPOutput:
    # On demand Statement of Purpose draft grounded in verified applicant profile and criteria
    settings = get_settings()
    from app.providers.llm_gemini import GeminiLLMProvider
    from app.providers.llm_groq import GroqLLMProvider

    gemini = GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
    groq = GroqLLMProvider(api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL)

    verified_criteria = [a.criterion for a in assessments if a.source_excerpt]
    projects_summary = "\n".join([f"- {p.name}: {p.summary} ({', '.join(p.skills)})" for p in profile.projects])

    prompt = (
        f"Draft a compelling, professional Statement of Purpose (SOP) tailored for:\n"
        f"Applicant: {profile.full_name} ({profile.nationality})\n"
        f"Target Opportunity: {opportunity.name} at {opportunity.institution or 'the university'}\n"
        f"Field: {profile.field_of_study}\n"
        f"GPA: {profile.grade.value if profile.grade else 'Not specified'}\n"
        f"Key Projects:\n{projects_summary}\n"
        f"Verified Admission Criteria to address:\n" + "\n".join(f"- {c}" for c in verified_criteria) + "\n\n"
        f"Write a 4-paragraph formal statement in markdown. Cite real projects from the profile only."
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        res = await call_with_fallback(
            [gemini, groq],
            lambda p: p.generate(task="sop_draft", messages=messages, schema=DraftSOPOutput),
        )
        return res.value
    except Exception:
        # Fallback to structured template SOP
        fallback_text = (
            f"# Statement of Purpose: {opportunity.name}\n\n"
            f"**Applicant:** {profile.full_name}\n"
            f"**Institution:** {opportunity.institution or 'University'}\n\n"
            f"I am writing to express my strong enthusiasm for the {opportunity.name}. "
            f"With my academic foundation in {profile.field_of_study or 'Computer Science'} "
            f"and hands-on experience developing projects such as {profile.projects[0].name if profile.projects else 'AI systems'}, "
            f"I am eager to contribute to the academic community.\n\n"
            f"The funding support provided through this opportunity will enable me to pursue advanced research and "
            f"apply my technical expertise toward solving real-world challenges."
        )
        return DraftSOPOutput(
            title=f"Statement of Purpose - {opportunity.name}",
            content_markdown=fallback_text,
            cited_evidence=verified_criteria,
        )
