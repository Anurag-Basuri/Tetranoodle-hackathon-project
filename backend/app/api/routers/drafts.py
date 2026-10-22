from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db import get_db
from app.infrastructure.models import ApplicationDraftModel
from app.application.generate_draft import generate_draft_use_case
from app.domain.errors import NotFoundError
from app.api.schemas import DraftCreateRequest, DraftOut

router = APIRouter(prefix="/research-jobs/{job_id}/drafts", tags=["Application Drafts"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=DraftOut)
async def create_application_draft(
    job_id: str,
    payload: DraftCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    # Generate on demand grounded Statement of Purpose draft
    draft_model = await generate_draft_use_case(
        session=db,
        job_id=job_id,
        opportunity_id=payload.opportunity_id,
    )
    return DraftOut(
        id=draft_model.id,
        job_id=draft_model.job_id,
        opportunity_id=draft_model.opportunity_id,
        content_md=draft_model.content_md,
        citations=draft_model.citations,
        created_at=draft_model.created_at,
    )

@router.get("/{draft_id}", response_model=DraftOut)
async def get_application_draft(
    job_id: str,
    draft_id: str,
    db: AsyncSession = Depends(get_db),
):
    # Retrieve prepared application draft
    stmt = select(ApplicationDraftModel).where(
        ApplicationDraftModel.id == draft_id,
        ApplicationDraftModel.job_id == job_id,
    )
    res = await db.execute(stmt)
    draft = res.scalar_one_or_none()
    if not draft:
        raise NotFoundError(f"Draft {draft_id} not found")

    return DraftOut(
        id=draft.id,
        job_id=draft.job_id,
        opportunity_id=draft.opportunity_id,
        content_md=draft.content_md,
        citations=draft.citations,
        created_at=draft.created_at,
    )
