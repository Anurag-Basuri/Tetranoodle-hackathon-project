from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, HttpUrl
from app.domain.enums import CriterionKind, CriterionStatus


class EvidenceRef(BaseModel):
    source_id: UUID
    source_url: HttpUrl
    source_excerpt: str  # verbatim, quote-checked text
    verified_at: datetime
    quote_verified: bool = False  # False -> excerpt could not be verified in page text


class Criterion(BaseModel):
    id: str  # stable: "{opportunity_id}:{kind}:{n}"
    kind: CriterionKind
    description: str
    required_value: Optional[str] = None
    params: Dict[str, Any] = {}
    is_hard: bool = True  # False = "preferred" / nice-to-have
    evidence: Optional[EvidenceRef] = None


class CriterionAssessment(BaseModel):
    criterion_id: str
    criterion: str
    required_value: Optional[str] = None
    student_value: Optional[str] = None
    status: CriterionStatus
    reason: str
    next_action: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    source_excerpt: Optional[str] = None
    verified_at: Optional[datetime] = None
