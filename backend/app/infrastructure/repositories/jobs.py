from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import ResearchJobModel
from app.domain.enums import JobStatus

class JobRepository:
    # Database repository managing research jobs and lifecycle status
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile_id: str, params: dict, profile_snapshot: dict) -> ResearchJobModel:
        job = ResearchJobModel(
            profile_id=profile_id,
            status=JobStatus.QUEUED.value,
            params=params,
            profile_snapshot=profile_snapshot,
            warnings=[],
            created_at=datetime.utcnow(),
            heartbeat_at=datetime.utcnow(),
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: str) -> Optional[ResearchJobModel]:
        stmt = select(ResearchJobModel).where(ResearchJobModel.id == job_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_active_job_for_profile(self, profile_id: str) -> Optional[ResearchJobModel]:
        # Enforce single active job constraint per profile
        active_statuses = [JobStatus.QUEUED.value, JobStatus.RUNNING.value]
        stmt = select(ResearchJobModel).where(
            and_(
                ResearchJobModel.profile_id == profile_id,
                ResearchJobModel.status.in_(active_statuses),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        warnings: Optional[List[Dict[str, Any]]] = None,
        error: Optional[Dict[str, Any]] = None,
    ) -> Optional[ResearchJobModel]:
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.status = status.value
        job.heartbeat_at = datetime.utcnow()
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in (JobStatus.COMPLETED, JobStatus.COMPLETED_WITH_WARNINGS, JobStatus.FAILED, JobStatus.CANCELLED):
            job.finished_at = datetime.utcnow()

        if warnings is not None:
            job.warnings = warnings
        if error is not None:
            job.error = error

        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update_heartbeat(self, job_id: str) -> None:
        job = await self.get_by_id(job_id)
        if job:
            job.heartbeat_at = datetime.utcnow()
            await self.session.commit()
