import asyncio
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select, and_
from app.infrastructure.db import AsyncSessionLocal
from app.infrastructure.models import ResearchJobModel
from app.infrastructure.repositories.jobs import JobRepository
from app.infrastructure.repositories.events import EventRepository
from app.domain.enums import JobStatus, AgentName
from app.application.job_runner import execute_research_job

async def recover_stale_jobs_on_startup(stale_threshold_seconds: int = 60) -> List[str]:
    # Checkpoint recovery: scan for interrupted jobs after server restarts and resume them
    recovered_job_ids: List[str] = []
    threshold_time = datetime.utcnow() - timedelta(seconds=stale_threshold_seconds)

    async with AsyncSessionLocal() as session:
        job_repo = JobRepository(session)
        event_repo = EventRepository(session)

        # Query jobs left in running state with stale heartbeat
        stmt = select(ResearchJobModel).where(
            and_(
                ResearchJobModel.status == JobStatus.RUNNING.value,
                ResearchJobModel.heartbeat_at < threshold_time,
            )
        )
        res = await session.execute(stmt)
        stale_jobs = res.scalars().all()

        for job in stale_jobs:
            recovered_job_ids.append(job.id)

            # Record recovery event in job timeline
            await event_repo.emit_event(
                job_id=job.id,
                agent=AgentName.COORDINATOR.value,
                level="warning",
                event_type="recovered",
                message="Server reboot or interruption detected; resuming research job from last checkpoint.",
            )

            # Resume execution in background task
            asyncio.create_task(execute_research_job(job.id))

    return recovered_job_ids
