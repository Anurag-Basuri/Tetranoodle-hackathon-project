import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.jobs import JobRepository
from app.infrastructure.repositories.profiles import ProfileRepository
from app.infrastructure.models import ResearchJobModel
from app.domain.errors import NotFoundError
from app.application.job_runner import execute_research_job

async def start_research_use_case(
    session: AsyncSession,
    profile_id: str,
    params: Optional[Dict[str, Any]] = None,
) -> ResearchJobModel:
    # Use case initiating autonomous scholarship research pipeline
    job_repo = JobRepository(session)
    profile_repo = ProfileRepository(session)

    profile_model = await profile_repo.get_by_id(profile_id)
    if not profile_model:
        raise NotFoundError(f"Profile {profile_id} not found")

    # Idempotency: return active running job if already in progress
    active_job = await job_repo.get_active_job_for_profile(profile_id)
    if active_job:
        return active_job

    # Create new queued job snapshotting current profile
    job_params = params or {}
    job = await job_repo.create(
        profile_id=profile_id,
        params=job_params,
        profile_snapshot=profile_model.data,
    )

    # Spawn asynchronous background task to run research swarm
    asyncio.create_task(execute_research_job(job.id))

    return job
