from datetime import date
from typing import Optional, List, Dict
from pydantic import BaseModel, HttpUrl
from app.domain.enums import DegreeLevel


class Grade(BaseModel):
    value: float
    scale: float  # e.g., 8.2 / 10.0 or 3.5 / 4.0


class LanguageTest(BaseModel):
    test: str  # IELTS, TOEFL, Duolingo, etc.
    score: Optional[float] = None
    taken_on: Optional[date] = None


class Project(BaseModel):
    name: str
    summary: str
    skills: List[str] = []
    url: Optional[HttpUrl] = None
    evidence: str  # e.g. "github.com/rahul/ai-agent"


class StudentProfile(BaseModel):
    full_name: str
    nationality: str  # ISO country name (e.g. India)
    degree_level_held: Optional[DegreeLevel] = None  # bachelor | master | phd
    degree_level_target: DegreeLevel  # target degree
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    grade: Optional[Grade] = None
    language_tests: List[LanguageTest] = []
    target_countries: List[str] = []
    interests: List[str] = []
    budget_note: Optional[str] = None
    needs_funding: bool = True
    skills: List[str] = []
    projects: List[Project] = []
    achievements: List[str] = []
    github_url: Optional[HttpUrl] = None
    missing_information: List[str] = []  # Discovered missing requirements (e.g., "language_test")
    provenance: Dict[str, str] = {}  # field -> "form" | "resume" | "transcript" | "github"
