from enum import StrEnum


class DegreeLevel(StrEnum):
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"


class CriterionKind(StrEnum):
    DEGREE_LEVEL = "degree_level"
    FIELD_OF_STUDY = "field_of_study"
    MIN_GRADE = "min_grade"
    LANGUAGE = "language"
    NATIONALITY = "nationality"
    DEADLINE = "deadline"
    WORK_EXPERIENCE = "work_experience"
    DOCUMENTS = "documents"
    OTHER = "other"


class CriterionStatus(StrEnum):
    MEETS = "meets"
    LIKELY_MEETS = "likely_meets"
    DOES_NOT_MEET = "does_not_meet"
    UNKNOWN = "unknown"
    NEEDS_REVIEW = "needs_review"


class OverallEligibility(StrEnum):
    NOT_ELIGIBLE = "not_eligible"
    MEETS_ALL_STATED = "meets_all_stated"
    LIKELY_ELIGIBLE = "likely_eligible"
    NEEDS_INFO = "needs_info"


class FundingType(StrEnum):
    FULL = "full"
    PARTIAL = "partial"
    TUITION_ONLY = "tuition_only"
    UNSPECIFIED = "unspecified"
    NONE = "none"


class OpportunityKind(StrEnum):
    SCHOLARSHIP = "scholarship"
    PROGRAM = "program"
    PROGRAM_WITH_FUNDING = "program_with_funding"


class SourceType(StrEnum):
    OFFICIAL = "official"
    AGGREGATOR = "aggregator"
    NEWS = "news"
    UNKNOWN = "unknown"


class FetchStatus(StrEnum):
    OK = "ok"
    FAILED = "failed"
    PARSE_FAILED = "parse_failed"
    BLOCKED = "blocked"


class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    UNVERIFIED = "unverified"
    CONFLICT = "conflict"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentName(StrEnum):
    PROFILE = "profile_analyst"
    SCOUT = "opportunity_scout"
    VERIFY = "verification_agent"
    ELIGIBILITY = "eligibility_analyst"
    RANKING = "ranking_application_agent"
    COORDINATOR = "coordinator"
