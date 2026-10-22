import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import (
    OpportunityModel,
    EligibilityAssessmentModel,
    RankingModel,
    ResearchJobModel,
)
from app.domain.opportunity import Opportunity, RankedOpportunity
from app.domain.evidence import CriterionAssessment
from app.domain.enums import VerificationStatus, OverallEligibility

def compute_dedupe_key(institution: Optional[str], name: str) -> str:
    # Deterministic SHA1 hash of lowercase institution and program name
    raw = f"{(institution or '').strip().lower()}:{(name or '').strip().lower()}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()

class OpportunityRepository:
    # Repository for persisting crawled opportunities, criteria assessments, and rankings
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_opportunities(self, job_id: str, opportunities: List[Opportunity]) -> None:
        for opp in opportunities:
            key = compute_dedupe_key(opp.institution, opp.name)
            model = OpportunityModel(
                id=str(opp.id),
                job_id=job_id,
                name=opp.name,
                institution=opp.institution,
                country=opp.country,
                verification_status=opp.verification_status.value,
                deadline=str(opp.deadline) if opp.deadline else None,
                dedupe_key=key,
                data=opp.model_dump(mode="json"),
                created_at=datetime.utcnow(),
            )
            self.session.add(model)
        await self.session.commit()

    async def save_assessments(
        self,
        job_id: str,
        assessments_by_opp: Dict[str, List[CriterionAssessment]],
        overall_by_opp: Dict[str, OverallEligibility],
    ) -> None:
        for opp_id, assessments in assessments_by_opp.items():
            overall = overall_by_opp.get(opp_id, OverallEligibility.NEEDS_INFO)
            model = EligibilityAssessmentModel(
                job_id=job_id,
                opportunity_id=opp_id,
                overall=overall.value,
                assessments=[a.model_dump(mode="json") for a in assessments],
                computed_at=datetime.utcnow(),
            )
            self.session.add(model)
        await self.session.commit()

    async def save_rankings(self, job_id: str, ranked_list: List[RankedOpportunity]) -> None:
        for r in ranked_list:
            model = RankingModel(
                job_id=job_id,
                opportunity_id=str(r.opportunity_id),
                rank=r.rank,
                score=r.score,
                breakdown=r.score_breakdown,
                rationale=r.rationale,
                data=r.model_dump(mode="json"),
            )
            self.session.add(model)
        await self.session.commit()

    async def get_results_summary(self, job_id: str) -> Dict[str, Any]:
        # Aggregate statistics and load Top 5 ranked results
        job_stmt = select(ResearchJobModel).where(ResearchJobModel.id == job_id)
        job_res = await self.session.execute(job_stmt)
        job = job_res.scalar_one_or_none()
        if not job:
            return {}

        # Load opportunities
        opps_stmt = select(OpportunityModel).where(OpportunityModel.job_id == job_id)
        opps_res = await self.session.execute(opps_stmt)
        all_opps = list(opps_res.scalars().all())

        # Load assessments
        ass_stmt = select(EligibilityAssessmentModel).where(EligibilityAssessmentModel.job_id == job_id)
        ass_res = await self.session.execute(ass_stmt)
        assessments_map = {a.opportunity_id: a for a in ass_res.scalars().all()}

        # Load rankings
        rnk_stmt = select(RankingModel).where(RankingModel.job_id == job_id).order_by(RankingModel.rank.asc())
        rnk_res = await self.session.execute(rnk_stmt)
        rankings = list(rnk_res.scalars().all())

        # Calculate summary numbers
        verified = sum(1 for o in all_opps if o.verification_status == VerificationStatus.VERIFIED.value)
        partial = sum(1 for o in all_opps if o.verification_status == VerificationStatus.PARTIAL.value)
        unverified = sum(1 for o in all_opps if o.verification_status == VerificationStatus.UNVERIFIED.value)
        not_eligible = sum(1 for a in assessments_map.values() if a.overall == OverallEligibility.NOT_ELIGIBLE.value)

        summary = {
            "candidates": len(all_opps),
            "verified": verified,
            "partially_verified": partial,
            "unverified": unverified,
            "not_eligible": not_eligible,
        }

        # Build top ranked opportunity items with criterion assessments
        top_items = []
        opps_by_id = {o.id: o for o in all_opps}

        for r in rankings:
            opp_model = opps_by_id.get(r.opportunity_id)
            ass_model = assessments_map.get(r.opportunity_id)

            top_items.append({
                "rank": r.rank,
                "score": r.score,
                "score_breakdown": r.breakdown,
                "overall": ass_model.overall if ass_model else "needs_info",
                "rationale": r.rationale,
                "trade_offs": r.data.get("trade_offs", []),
                "next_actions": r.data.get("next_actions", []),
                "opportunity": opp_model.data if opp_model else {},
                "assessments": ass_model.assessments if ass_model else [],
            })

        all_items = [
            {
                "id": o.id,
                "name": o.name,
                "institution": o.institution,
                "country": o.country,
                "verification_status": o.verification_status,
                "deadline": o.deadline,
                "overall": assessments_map.get(o.id).overall if o.id in assessments_map else "needs_info",
            }
            for o in all_opps
        ]

        return {
            "job": {
                "id": job.id,
                "status": job.status,
                "partial": job.status in ("queued", "running"),
            },
            "summary": summary,
            "profile": job.profile_snapshot,
            "top": top_items,
            "all": all_items,
            "warnings": job.warnings or [],
        }
