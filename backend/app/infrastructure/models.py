import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    Float,
    ForeignKey,
    JSON,
    LargeBinary,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.infrastructure.db import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class StudentProfileModel(Base):
    __tablename__ = "student_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    data = Column(JSON, nullable=False)  # Normalized StudentProfile
    access_token_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    documents = relationship("StudentDocumentModel", back_populates="profile", cascade="all, delete-orphan")
    jobs = relationship("ResearchJobModel", back_populates="profile", cascade="all, delete-orphan")


class StudentDocumentModel(Base):
    __tablename__ = "student_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(32), nullable=False)  # resume | transcript | other
    filename = Column(String(255), nullable=False)
    mime = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    content = Column(LargeBinary, nullable=True)
    extracted_text = Column(Text, nullable=True)
    extraction_status = Column(String(32), default="pending", nullable=False)  # pending | completed | failed
    extraction_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("StudentProfileModel", back_populates="documents")


class ResearchJobModel(Base):
    __tablename__ = "research_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), default="queued", nullable=False, index=True)
    params = Column(JSON, default=dict, nullable=False)
    profile_snapshot = Column(JSON, default=dict, nullable=False)
    warnings = Column(JSON, default=list, nullable=False)
    error = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    heartbeat_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("StudentProfileModel", back_populates="jobs")
    events = relationship("JobEventModel", back_populates="job", cascade="all, delete-orphan")
    opportunities = relationship("OpportunityModel", back_populates="job", cascade="all, delete-orphan")
    rankings = relationship("RankingModel", back_populates="job", cascade="all, delete-orphan")
    drafts = relationship("ApplicationDraftModel", back_populates="job", cascade="all, delete-orphan")


class AgentRunModel(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    agent = Column(String(64), nullable=False)
    scope = Column(String(64), default="global", nullable=False)
    status = Column(String(32), nullable=False)  # running | completed | failed | retrying
    attempt = Column(Integer, default=1, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    error_category = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    provider_used = Column(String(64), nullable=True)
    tokens_in = Column(Integer, default=0, nullable=False)
    tokens_out = Column(Integer, default=0, nullable=False)


class JobEventModel(Base):
    __tablename__ = "job_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    seq = Column(Integer, nullable=False)
    agent = Column(String(64), nullable=False)
    level = Column(String(16), default="info", nullable=False)  # info | warning | error | success
    type = Column(String(64), nullable=False)  # started | progress | verified | evaluated | failed | completed
    message = Column(Text, nullable=False)
    payload = Column(JSON, default=dict, nullable=False)
    at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("ResearchJobModel", back_populates="events")

    __table_args__ = (
        UniqueConstraint("job_id", "seq", name="uq_job_seq"),
    )


class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    canonical_url = Column(Text, nullable=False)
    source_type = Column(String(32), default="unknown", nullable=False)  # official | aggregator | news | unknown
    fetch_status = Column(String(32), default="ok", nullable=False)
    http_status = Column(Integer, nullable=True)
    content_hash = Column(String(64), nullable=True)
    text_content = Column(Text, nullable=True)
    extraction_method = Column(String(32), nullable=True)
    error = Column(Text, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_sources_job_url", "job_id", "canonical_url"),
    )


class OpportunityModel(Base):
    __tablename__ = "opportunities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    verification_status = Column(String(32), default="unverified", nullable=False)
    deadline = Column(String(32), nullable=True)
    dedupe_key = Column(String(64), nullable=False)
    data = Column(JSON, nullable=False)  # Full Opportunity model
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("ResearchJobModel", back_populates="opportunities")

    __table_args__ = (
        UniqueConstraint("job_id", "dedupe_key", name="uq_opportunity_dedupe"),
    )


class EligibilityAssessmentModel(Base):
    __tablename__ = "eligibility_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(String(36), nullable=False, unique=True, index=True)
    overall = Column(String(32), nullable=False)
    assessments = Column(JSON, nullable=False)  # List of CriterionAssessment
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RankingModel(Base):
    __tablename__ = "rankings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(String(36), nullable=False, index=True)
    rank = Column(Integer, nullable=True)
    score = Column(Float, nullable=False)
    breakdown = Column(JSON, nullable=False)
    rationale = Column(Text, nullable=False)
    data = Column(JSON, nullable=False)

    job = relationship("ResearchJobModel", back_populates="rankings")

    __table_args__ = (
        UniqueConstraint("job_id", "opportunity_id", name="uq_job_opportunity_rank"),
    )


class ApplicationDraftModel(Base):
    __tablename__ = "application_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(String(36), nullable=False, index=True)
    content_md = Column(Text, nullable=False)
    citations = Column(JSON, default=list, nullable=False)
    model_used = Column(String(64), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("ResearchJobModel", back_populates="drafts")
