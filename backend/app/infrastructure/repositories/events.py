from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import JobEventModel

class EventRepository:
    # Repository for monotonic append-only job events
    def __init__(self, session: AsyncSession):
        self.session = session

    async def emit_event(
        self,
        job_id: str,
        agent: str,
        level: str,
        event_type: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> JobEventModel:
        # Determine next monotonic sequence number for this job
        stmt = select(func.coalesce(func.max(JobEventModel.seq), 0)).where(JobEventModel.job_id == job_id)
        res = await self.session.execute(stmt)
        max_seq = res.scalar() or 0
        next_seq = max_seq + 1

        event = JobEventModel(
            job_id=job_id,
            seq=next_seq,
            agent=agent,
            level=level,
            type=event_type,
            message=message,
            payload=payload or {},
            at=datetime.utcnow(),
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_events(
        self,
        job_id: str,
        after_seq: int = 0,
        limit: int = 200,
    ) -> List[JobEventModel]:
        stmt = (
            select(JobEventModel)
            .where(JobEventModel.job_id == job_id, JobEventModel.seq > after_seq)
            .order_by(JobEventModel.seq.asc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
