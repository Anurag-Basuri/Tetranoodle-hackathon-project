from datetime import date
from typing import Optional, List, Dict
from uuid import UUID, uuid4
from pydantic import BaseModel, HttpUrl, Field
from app.domain.enums import OpportunityKind, FundingType, VerificationStatus, OverallEligibility
from app.domain.evidence import Criterion, EvidenceRef


class ConflictValue(BaseModel):
    value: str
    source_url: HttpUrl
    excerpt: str


class FieldConflict(BaseModel):
    field: str
    values: List[ConflictValue] = []


class Candidate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    institution: Optional[str] = None
    country: Optional[str] = None
    url: HttpUrl
    snippet: Optional[str] = None
    discovery_provider: str = "tavily"


class Opportunity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    name: str
    institution: Optional[str] = None
    country: Optional[str] = None
    kind: OpportunityKind = OpportunityKind.SCHOLARSHIP
    official_url: Optional[HttpUrl] = None
    funding_type: FundingType = FundingType.UNSPECIFIED
    funding_detail: Optional[str] = None
    funding_evidence: Optional[EvidenceRef] = None
    deadline: Optional[date] = None
    deadline_evidence: Optional[EvidenceRef] = None
    intake: Optional[str] = None
    application_url: Optional[HttpUrl] = None
    application_steps: List[str] = []
    criteria: List[Criterion] = []
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    conflicts: List[FieldConflict] = []
    discovery_sources: List[str] = []
    candidate_notes: Optional[str] = None


class RankedOpportunity(BaseModel):
    opportunity_id: UUID
    rank: Optional[int] = None
    score: float
    score_breakdown: Dict[str, float]
    overall: OverallEligibility
    rationale: str
    trade_offs: List[str] = []
    next_actions: List[str] = []
