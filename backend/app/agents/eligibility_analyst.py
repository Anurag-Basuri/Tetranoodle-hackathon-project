from typing import Dict, Any, List
from app.domain.enums import AgentName, CriterionKind, CriterionStatus
from app.domain.opportunity import Opportunity
from app.domain.profile import StudentProfile
from app.domain.evidence import CriterionAssessment
from app.domain.criteria_rules import evaluate_criterion, derive_overall
from app.agents.base import run_agent
from app.agents.state import AgentWarning

async def assess_candidate_pipeline(
    opportunity: Opportunity,
    profile: StudentProfile,
) -> Dict[str, Any]:
    # Eligibility Analyst node: evaluates student criteria deterministically
    warnings: List[AgentWarning] = []

    async def execute():
        assessments: List[CriterionAssessment] = []

        for criterion in opportunity.criteria:
            assessment = evaluate_criterion(criterion, profile)
            assessments.append(assessment)

        overall = derive_overall(assessments, opportunity.verification_status)

        return {
            "assessments": {str(opportunity.id): assessments},
            "overall": overall,
            "warnings": warnings,
        }

    def fallback(err: Exception) -> Dict[str, Any]:
        return {
            "assessments": {str(opportunity.id): []},
            "warnings": [AgentWarning(
                agent=AgentName.ELIGIBILITY,
                scope=str(opportunity.id),
                message=f"Eligibility assessment degraded: {err}",
            )],
        }

    return await run_agent(AgentName.ELIGIBILITY, str(opportunity.id), execute, fallback)
