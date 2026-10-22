// Domain and API response TypeScript definitions

export type DegreeLevel = 'bachelor' | 'master' | 'phd';
export type FundingType = 'full' | 'partial' | 'tuition_only' | 'unspecified' | 'none';
export type CriterionStatus = 'meets' | 'likely_meets' | 'does_not_meet' | 'unknown' | 'needs_review';
export type OverallEligibility = 'not_eligible' | 'meets_all_stated' | 'likely_eligible' | 'needs_info';
export type VerificationStatus = 'verified' | 'partial' | 'unverified' | 'conflict';
export type JobStatus = 'queued' | 'running' | 'completed' | 'completed_with_warnings' | 'failed' | 'cancelled';

export interface Grade {
  value: number;
  scale: number;
}

export interface LanguageTest {
  test: string;
  score?: number | null;
  taken_on?: string | null;
}

export interface Project {
  name: string;
  summary: string;
  skills: string[];
  url?: string | null;
  evidence: string;
}

export interface StudentProfile {
  full_name: string;
  nationality: string;
  degree_level_held?: DegreeLevel | null;
  degree_level_target: DegreeLevel;
  field_of_study?: string | null;
  institution?: string | null;
  graduation_year?: number | null;
  grade?: Grade | null;
  language_tests: LanguageTest[];
  target_countries: string[];
  interests: string[];
  budget_note?: string | null;
  needs_funding: boolean;
  skills?: string[];
  projects?: Project[];
  achievements?: string[];
  github_url?: string | null;
  missing_information?: string[];
  provenance?: Record<string, string>;
}

export interface ProfileCreateResponse {
  id: string;
  access_token: string;
  profile: StudentProfile;
}

export interface DocumentOut {
  id: string;
  profile_id: string;
  kind: string;
  filename: string;
  size_bytes: number;
  extraction_status: string;
  created_at: string;
}

export interface JobOut {
  id: string;
  profile_id: string;
  status: JobStatus;
  params: Record<string, any>;
  warnings: Array<Record<string, any>>;
  error?: Record<string, any> | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface JobEvent {
  seq: number;
  agent: string;
  level: 'info' | 'warning' | 'error' | 'success';
  type: string;
  message: string;
  payload?: Record<string, any>;
  at: string;
}

export interface EventsResponse {
  job_id: string;
  events: JobEvent[];
  last_seq: number;
}

export interface EvidenceRef {
  source_id?: string;
  source_url: string;
  source_excerpt: string;
  verified_at: string;
  quote_verified?: boolean;
}

export interface CriterionAssessment {
  criterion_id: string;
  criterion: string;
  required_value?: string | null;
  student_value?: string | null;
  status: CriterionStatus;
  reason: string;
  next_action?: string | null;
  source_url?: string | null;
  source_excerpt?: string | null;
  verified_at?: string | null;
}

export interface ScoreBreakdown {
  funding_fit: number;
  academic_fit: number;
  program_relevance: number;
  country_preference: number;
  deadline_feasibility: number;
  evidence_confidence: number;
}

export interface OpportunityData {
  id: string;
  name: string;
  institution?: string | null;
  country?: string | null;
  official_url?: string | null;
  funding_type: FundingType;
  funding_detail?: string | null;
  deadline?: string | null;
  deadline_evidence?: EvidenceRef | null;
  application_url?: string | null;
  application_steps?: string[];
  verification_status: VerificationStatus;
}

export interface RankedOpportunity {
  rank: number;
  score: number;
  score_breakdown: ScoreBreakdown;
  overall: OverallEligibility;
  rationale: string;
  trade_offs: string[];
  next_actions: string[];
  opportunity: OpportunityData;
  assessments: CriterionAssessment[];
}

export interface CandidateRow {
  id: string;
  name: string;
  institution?: string | null;
  country?: string | null;
  funding_type: FundingType;
  deadline?: string | null;
  verification_status: VerificationStatus;
  overall: OverallEligibility;
  official_url?: string | null;
}

export interface ResultsOut {
  job: {
    id: string;
    status: JobStatus;
    partial?: boolean;
  };
  summary: {
    candidates: number;
    verified: number;
    partially_verified: number;
    unverified: number;
    not_eligible: number;
  };
  profile: StudentProfile;
  top: RankedOpportunity[];
  all: CandidateRow[];
  warnings: Array<{ agent: string; scope?: string; message: string }>;
}

export interface DraftOut {
  id: string;
  job_id: string;
  opportunity_id: string;
  content: string;
  word_count: number;
  citations: Array<{ source_url?: string; excerpt?: string; claim?: string }>;
  created_at: string;
}
