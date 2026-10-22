from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from app.domain.enums import DegreeLevel, JobStatus
from app.domain.profile import Grade, LanguageTest, Project

class ProfileCreate(BaseModel):
    # Form payload for registering student profile
    full_name: str
    nationality: str
    degree_level_held: Optional[DegreeLevel] = None
    degree_level_target: DegreeLevel = DegreeLevel.MASTER
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    grade: Optional[Grade] = None
    language_tests: List[LanguageTest] = []
    target_countries: List[str] = []
    interests: List[str] = []
    budget_note: Optional[str] = None
    needs_funding: bool = True
    github_url: Optional[HttpUrl] = None

class ProfileCreateResponse(BaseModel):
    # Response returned once upon creation containing capability access token
    id: str
    access_token: str
    profile: Dict[str, Any]

class ProfileResponse(BaseModel):
    id: str
    profile: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class DocumentOut(BaseModel):
    id: str
    profile_id: str
    kind: str
    filename: str
    size_bytes: int
    extraction_status: str
    created_at: datetime

class JobCreateRequest(BaseModel):
    profile_id: str
    countries: Optional[List[str]] = None
    max_candidates: Optional[int] = None

class JobOut(BaseModel):
    id: str
    profile_id: str
    status: str
    params: Dict[str, Any] = {}
    warnings: List[Dict[str, Any]] = []
    error: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

class EventOut(BaseModel):
    seq: int
    agent: str
    level: str
    type: str
    message: str
    payload: Dict[str, Any] = {}
    at: datetime

class EventsResponse(BaseModel):
    job_id: str
    events: List[EventOut]
    last_seq: int

class DraftCreateRequest(BaseModel):
    opportunity_id: str

class DraftOut(BaseModel):
    id: str
    job_id: str
    opportunity_id: str
    content_md: str
    citations: List[str] = []
    created_at: datetime
