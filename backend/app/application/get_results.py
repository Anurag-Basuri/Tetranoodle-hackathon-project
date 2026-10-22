from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.opportunities import OpportunityRepository
from app.domain.errors import NotFoundError

async def get_results_use_case(
    session: AsyncSession,
    job_id: str,
) -> Dict[str, Any]:
    # Use case retrieving aggregated results summary and ranked recommendations
    opp_repo = OpportunityRepository(session)
    results = await opp_repo.get_results_summary(job_id)
    if not results:
        raise NotFoundError(f"Job {job_id} not found")
    return results
