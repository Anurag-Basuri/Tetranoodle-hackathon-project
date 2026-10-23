import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, List
from app.infrastructure.db import AsyncSessionLocal
from app.infrastructure.repositories.jobs import JobRepository
from app.infrastructure.repositories.events import EventRepository
from app.infrastructure.repositories.opportunities import OpportunityRepository
from app.agents.graph import build_research_graph
from app.domain.enums import JobStatus, AgentName
from app.domain.profile import StudentProfile

async def execute_research_job(job_id: str) -> None:
    # Phase 1: Retrieve job snapshot and transition status to RUNNING in a short-lived session
    profile_input = None
    docs = []
    async with AsyncSessionLocal() as session:
        job_repo = JobRepository(session)
        event_repo = EventRepository(session)

        job = await job_repo.get_by_id(job_id)
        if not job:
            return

        await job_repo.update_status(job_id, JobStatus.RUNNING)
        await event_repo.emit_event(
            job_id=job_id,
            agent=AgentName.COORDINATOR.value,
            level="info",
            event_type="started",
            message="ScholarPilot research agents initialized and started.",
        )
        await event_repo.emit_event(
            job_id=job_id,
            agent=AgentName.COORDINATOR.value,
            level="info",
            event_type="progress",
            message="Launching parallel Profile Analyst and Opportunity Scout agents.",
        )

        profile_input = StudentProfile.model_validate(job.profile_snapshot)
        docs = job.params.get("documents", [])

    # Phase 2: Execute pure in-memory LangGraph multi-agent pipeline
    try:
        initial_state = {
            "job_id": job_id,
            "profile_input": profile_input,
            "documents": docs,
            "profile": None,
            "candidates": [],
            "opportunities": {},
            "assessments": {},
            "ranking": [],
            "warnings": [],
            "stats": {},
        }

        graph = build_research_graph()
        final_state = await graph.ainvoke(initial_state)

        # Extract results from state
        opportunities = list(final_state.get("opportunities", {}).values())
        assessments_by_opp = final_state.get("assessments", {})
        ranking = final_state.get("ranking", [])
        warnings = final_state.get("warnings", [])

        from app.domain.criteria_rules import derive_overall
        overall_by_opp = {}
        for opp in opportunities:
            ass_list = assessments_by_opp.get(str(opp.id), [])
            overall_by_opp[str(opp.id)] = derive_overall(ass_list, opp.verification_status)

        # Phase 3: Persist outputs in a fresh, dedicated database session
        async with AsyncSessionLocal() as session:
            opp_repo = OpportunityRepository(session)
            job_repo = JobRepository(session)
            event_repo = EventRepository(session)

            if opportunities:
                await opp_repo.save_opportunities(job_id, opportunities)
            if assessments_by_opp:
                await opp_repo.save_assessments(job_id, assessments_by_opp, overall_by_opp)
            if ranking:
                await opp_repo.save_rankings(job_id, ranking)

            final_status = JobStatus.COMPLETED_WITH_WARNINGS if warnings else JobStatus.COMPLETED
            await job_repo.update_status(
                job_id=job_id,
                status=final_status,
                warnings=[dict(w) if isinstance(w, dict) else {"message": str(w)} for w in warnings],
            )
            await event_repo.emit_event(
                job_id=job_id,
                agent=AgentName.RANKING.value,
                level="success",
                event_type="completed",
                message=f"Research completed successfully with {len(opportunities)} opportunities analyzed and Top {len(ranking)} ranked.",
                payload={"ranked_count": len(ranking), "candidate_count": len(opportunities)},
            )

    except Exception as e:
        # Phase 4: Handle any errors using a dedicated error session to ensure clean state
        trace = traceback.format_exc()
        try:
            async with AsyncSessionLocal() as err_session:
                job_repo = JobRepository(err_session)
                event_repo = EventRepository(err_session)
                await job_repo.update_status(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    error={"message": str(e), "trace": trace[:400]},
                )
                await event_repo.emit_event(
                    job_id=job_id,
                    agent=AgentName.COORDINATOR.value,
                    level="error",
                    event_type="failed",
                    message=f"Research job encountered failure: {e}",
                )
        except Exception:
            pass
