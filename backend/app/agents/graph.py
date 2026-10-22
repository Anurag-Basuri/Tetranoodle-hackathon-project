from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from app.agents.state import ResearchState
from app.agents.profile_analyst import analyze_profile_node
from app.agents.opportunity_scout import scout_opportunities_node
from app.agents.verification_agent import verify_candidate_pipeline
from app.agents.eligibility_analyst import assess_candidate_pipeline
from app.agents.ranking_application_agent import rank_and_select_node

async def run_candidate_pipeline_node(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Isolated pipeline execution for a single candidate: verify then assess
    candidate = payload["candidate"]
    job_id = payload["job_id"]
    profile = payload["profile"]

    # 1. Verify candidate details on official page
    verify_res = await verify_candidate_pipeline(candidate, job_id)
    opps_dict = verify_res.get("opportunities", {})
    warnings = list(verify_res.get("warnings", []))

    assessments_dict = {}
    if opps_dict:
        opp = list(opps_dict.values())[0]
        # 2. Assess eligibility deterministically
        assess_res = await assess_candidate_pipeline(opp, profile)
        assessments_dict = assess_res.get("assessments", {})
        warnings.extend(assess_res.get("warnings", []))

    return {
        "opportunities": opps_dict,
        "assessments": assessments_dict,
        "warnings": warnings,
    }

def fan_out_candidates(state: ResearchState) -> List[Send]:
    # Fan out candidates into parallel isolated evaluation pipelines
    candidates = state.get("candidates", [])
    profile = state.get("profile") or state["profile_input"]
    job_id = state.get("job_id", "")

    # Limit maximum concurrent candidates to 15 to stay within resource budgets
    return [
        Send(
            "candidate_pipeline",
            {
                "candidate": c,
                "profile": profile,
                "job_id": job_id,
            },
        )
        for c in candidates[:15]
    ]

def build_research_graph(checkpointer: Any = None):
    # Construct compiled LangGraph for the ScholarPilot swarm
    builder = StateGraph(ResearchState)

    # 1. Register graph nodes
    builder.add_node("profile_analyst", analyze_profile_node)
    builder.add_node("opportunity_scout", scout_opportunities_node)
    builder.add_node("candidate_pipeline", run_candidate_pipeline_node)
    builder.add_node("rank_and_select", rank_and_select_node)

    # 2. Add edges for parallel start
    builder.add_edge(START, "profile_analyst")
    builder.add_edge(START, "opportunity_scout")

    # 3. Conditional fan out from opportunity scout to candidate pipelines
    builder.add_conditional_edges(
        "opportunity_scout",
        fan_out_candidates,
        ["candidate_pipeline"],
    )

    # 4. Join pipelines into ranking selection
    builder.add_edge("candidate_pipeline", "rank_and_select")
    builder.add_edge("profile_analyst", "rank_and_select")
    builder.add_edge("rank_and_select", END)

    return builder.compile(checkpointer=checkpointer)
