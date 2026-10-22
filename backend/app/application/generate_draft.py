import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import ApplicationDraftModel, OpportunityModel, EligibilityAssessmentModel, ResearchJobModel
from app.domain.opportunity import Opportunity
from app.domain.profile import StudentProfile
from app.domain.evidence import CriterionAssessment
from app.domain.errors import NotFoundError
from app.agents.ranking_application_agent import generate_application_draft

async def generate_draft_use_case(
    session: AsyncSession,
    job_id: str,
    opportunity_id: str,
) -> ApplicationDraftModel:
    # Use case preparing tailored Statement of Purpose for an opportunity
    opp_stmt = select(OpportunityModel).where(OpportunityModel.id == opportunity_id, OpportunityModel.job_id == job_id)
    opp_res = await session.execute(opp_stmt)
    opp_model = opp_res.scalar_one_or_none()
    if not opp_model:
        raise NotFoundError(f"Opportunity {opportunity_id} not found for job {job_id}")

    job_stmt = select(ResearchJobModel).where(ResearchJobModel.id == job_id)
    job_res = await session.execute(job_stmt)
    job_model = job_res.scalar_one_or_none()
    if not job_model:
        raise NotFoundError(f"Job {job_id} not found")

    ass_stmt = select(EligibilityAssessmentModel).where(EligibilityAssessmentModel.opportunity_id == opportunity_id)
    ass_res = await session.execute(ass_stmt)
    ass_model = ass_res.scalar_one_or_none()

    opp = Opportunity.model_validate(opp_model.data)
    profile = StudentProfile.model_validate(job_model.profile_snapshot)
    assessments = [CriterionAssessment.model_validate(a) for a in ass_model.assessments] if ass_model else []

    draft_output = await generate_application_draft(opp, profile, assessments)

    draft_model = ApplicationDraftModel(
        id=str(uuid.uuid4()),
        job_id=job_id,
        opportunity_id=opportunity_id,
        content_md=draft_output.content_markdown,
        citations=draft_output.cited_evidence,
        model_used="scholarpilot-llm",
        version=1,
        created_at=datetime.utcnow(),
    )
    session.add(draft_model)
    await session.commit()
    await session.refresh(draft_model)
    return draft_model
