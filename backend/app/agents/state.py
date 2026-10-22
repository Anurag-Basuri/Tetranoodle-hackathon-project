from typing import TypedDict, Annotated, List, Dict, Optional, Any
from operator import add
from app.domain.profile import StudentProfile
from app.domain.opportunity import Candidate, Opportunity, RankedOpportunity
from app.domain.evidence import CriterionAssessment

def merge_dict_entries(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    # Combine dictionary entries from parallel branch reductions
    merged = dict(a) if a else {}
    if b:
        merged.update(b)
    return merged

class DocText(TypedDict):
    filename: str
    kind: str
    text: str

class AgentWarning(TypedDict):
    agent: str
    scope: str
    message: str

class ResearchState(TypedDict):
    # Global state payload passed through LangGraph nodes
    job_id: str
    profile_input: StudentProfile
    documents: List[DocText]
    profile: Optional[StudentProfile]
    candidates: Annotated[List[Candidate], add]
    opportunities: Annotated[Dict[str, Opportunity], merge_dict_entries]
    assessments: Annotated[Dict[str, List[CriterionAssessment]], merge_dict_entries]
    ranking: List[RankedOpportunity]
    warnings: Annotated[List[AgentWarning], add]
    stats: Dict[str, int]
