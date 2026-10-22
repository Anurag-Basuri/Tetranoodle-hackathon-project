from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db import get_db
from app.infrastructure.repositories.jobs import JobRepository
from app.infrastructure.repositories.events import EventRepository
from app.application.start_research import start_research_use_case
from app.application.get_results import get_results_use_case
from app.domain.errors import NotFoundError
from app.api.schemas import JobCreateRequest, JobOut, EventsResponse, EventOut

router = APIRouter(prefix="/research-jobs", tags=["Research Jobs"])

@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=JobOut)
async def create_research_job(
    payload: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    # Initiate multi agent scholarship search for profile
    params = {}
    if payload.countries:
        params["countries"] = payload.countries
    if payload.max_candidates:
        params["max_candidates"] = payload.max_candidates

    job = await start_research_use_case(db, payload.profile_id, params)
    return JobOut(
        id=job.id,
        profile_id=job.profile_id,
        status=job.status,
        params=job.params,
        warnings=job.warnings,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )

@router.get("/{job_id}", response_model=JobOut)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    # Poll current job lifecycle status and heartbeat
    repo = JobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise NotFoundError(f"Job {job_id} not found")

    return JobOut(
        id=job.id,
        profile_id=job.profile_id,
        status=job.status,
        params=job.params,
        warnings=job.warnings,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )

@router.get("/{job_id}/events", response_model=EventsResponse)
async def get_job_events(
    job_id: str,
    after_seq: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    # Stream/poll incremental agent execution events
    repo = EventRepository(db)
    events = await repo.get_events(job_id, after_seq=after_seq, limit=limit)
    last_seq = max([e.seq for e in events], default=after_seq)

    return EventsResponse(
        job_id=job_id,
        events=[
            EventOut(
                seq=e.seq,
                agent=e.agent,
                level=e.level,
                type=e.type,
                message=e.message,
                payload=e.payload,
                at=e.at,
            )
            for e in events
        ],
        last_seq=last_seq,
    )

@router.get("/{job_id}/results")
async def get_job_results(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    # Retrieve final Evidence-Backed Eligibility Report
    return await get_results_use_case(db, job_id)
