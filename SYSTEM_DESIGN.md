# ScholarPilot AI: System Design

Evidence-backed scholarship and university research by a team of cooperating agents.
Built for the TetraNoodle AI Hackathon 2026. **This document is the contract: if something is decided here, do not re-decide it while coding.** Anything marked **GAP** is listed in §21 with a default so you are never blocked.

---

## 1. What we are building (and not building)

**Product statement.** A student supplies a profile, documents and preferences. Agents research opportunities, verify requirements against official sources, assess eligibility criterion by criterion, and produce an evidence-backed plan. The centrepiece is the **Evidence-Backed Eligibility Report**, not a chatbot.

| In scope | Out of scope |
|---|---|
| Intake form, resume/transcript upload, GitHub enrichment | User accounts, passwords, OAuth |
| 5 agent roles, parallel research, per-candidate failure isolation | Submitting real applications |
| ≥10 candidates, verified sources, criterion-level eligibility | Admission or scholarship probability claims |
| Top-5 ranking with documented score, application draft (SOP) | Payments, email notifications, multi-user collaboration |
| Live agent progress UI, crash recovery, provider fallback | Mobile app, i18n, real-time websockets |

**Rubric mapping.**

| Rubric (marks) | Where we earn it |
|---|---|
| Agents work together autonomously (30) | §8 graph, typed state, parallel + fan-out, distinct tools per agent |
| Real internet research and enrichment (25) | §8.1 GitHub, §8.2 Tavily/Brave search, §11 live page fetch |
| Correct results, trustworthy sources (20) | §9 deterministic eligibility, §11 quote verification, official-source rule |
| Working website and demo (10) | §16 frontend, live timeline |
| Creativity and failure handling (15) | §15 failure matrix, provider router, checkpoint resume, "adapt to new profile" |

---

## 2. Core principles (the rules every file follows)

1. **Discovery is not verification.** A search hit is a *candidate*. Only an official page, fetched and quote-checked, becomes *evidence*.
2. **Eligibility is deterministic where it can be.** LLMs extract and interpret text. Python decides statuses (§9).
3. **No claim without evidence.** Every criterion stores `source_url`, `source_excerpt`, `verified_at`. An excerpt that is not found in the fetched page is discarded and the criterion becomes `unknown`.
4. **Outage never equals ineligible.** Provider or fetch failures produce `unknown` / `unverified`, never `does_not_meet`.
5. **One failure never kills the job.** Failures are isolated per candidate and per source.
6. **No student-specific logic in code.** Rahul is a fixture, not a branch. The "final surprise" profile must run unchanged.
7. **Prompts return Pydantic models.** Invalid output gets one repair retry, then a recoverable error state.

---

## 3. Architecture

```
React + TS (Vercel)  ── HTTPS/JSON, polling ──►  FastAPI (Render)
                                                   │
        routers (controllers) → use cases (application) → domain + repositories
                                                   │
                         ┌─────────────────────────┴───────────────────────────┐
                         │ Job Runner (asyncio task, 1 per job, global cap = 2) │
                         │   LangGraph  (AsyncPostgresSaver checkpoints)        │
                         └──────┬──────────────┬────────────────┬───────────────┘
                          Providers          Tools           PostgreSQL
                     LLM: Gemini→Groq   Fetcher, Parsers   (Render managed)
                     Search: Tavily→Brave  GitHub client
```

**Layers** (imports only point downward):

| Layer | Folder | Owns | May import |
|---|---|---|---|
| API | `api/` | HTTP, validation, auth dependency, error mapping | application, schemas |
| Application | `application/` | Use cases: StartResearch, GetResults, GenerateDraft, RecoverJobs | domain, infrastructure, agents |
| Agents | `agents/` | 5 agent roles, graph, state | domain, providers, tools |
| Providers | `providers/` | LLM and search abstractions, router, circuit breaker | domain (errors only) |
| Tools | `tools/` | Fetcher, PDF/HTML extractors, GitHub client, chunk retrieval | domain |
| Domain | `domain/` | Pydantic models, enums, eligibility rules, ranking, no I/O | nothing |
| Infrastructure | `infrastructure/` | SQLAlchemy models, repositories, Alembic, logging | domain |

**Execution model (decision, not a gap).** The job runs as an `asyncio` task inside the API process. State is checkpointed to Postgres after each LangGraph step, so a restart resumes it (§14). No Redis, no Celery, no separate worker.

---

## 4. Tech stack (fixed)

| Area | Choice |
|---|---|
| Language / API | Python 3.12, FastAPI, Uvicorn, Pydantic v2 + pydantic-settings |
| Orchestration | LangGraph + `langgraph-checkpoint-postgres` |
| LLM adapters | `langchain-google-genai`, `langchain-groq`, using `with_structured_output(PydanticModel)` behind our own `LLMProvider` interface |
| Search | Tavily (`tavily-python`) primary; Brave Search API fallback (§10) |
| HTTP | `httpx` (async) |
| Parsing | `trafilatura` (HTML), `pypdf` then `pdfplumber` (PDF), `rank_bm25` (chunk selection), `rapidfuzz` (quote check) |
| DB | PostgreSQL 16, SQLAlchemy 2.0 async + `asyncpg`, Alembic |
| Quality | `ruff`, `mypy` (domain + providers strict), `pytest`, `pytest-asyncio`, `respx` (HTTP mocks) |
| Frontend | React 18, TypeScript, Vite, TanStack Query v5, Tailwind CSS, `react-router`, `react-hook-form` + `zod`, `openapi-typescript` |
| Deploy | Render (web service + Postgres), Vercel (static frontend) |

Model ids are **config, never hard-coded**: `GEMINI_MODEL`, `GROQ_MODEL` (verify available models and quotas on your accounts on day 0).

---

## 5. Repository structure

```
scholarpilot/
├── README.md  SYSTEM_DESIGN.md  AGENT_DESIGN_NOTE.md  .env.example  docker-compose.yml  Makefile
├── backend/
│   ├── pyproject.toml  alembic.ini  Dockerfile
│   ├── alembic/versions/
│   ├── app/
│   │   ├── main.py                  # app factory, lifespan (recover jobs), middleware, routers
│   │   ├── config.py                # Settings (pydantic-settings)
│   │   ├── api/
│   │   │   ├── deps.py              # db session, current_profile (token auth), rate limit
│   │   │   ├── errors.py            # exception → Problem Details
│   │   │   ├── schemas.py           # request/response DTOs only
│   │   │   └── routers/ profiles.py documents.py research_jobs.py drafts.py health.py
│   │   ├── application/
│   │   │   ├── start_research.py  get_results.py  generate_draft.py
│   │   │   ├── job_runner.py        # launches/limits/cancels graph runs
│   │   │   └── recover_jobs.py      # startup recovery
│   │   ├── agents/
│   │   │   ├── state.py             # ResearchState (TypedDict + reducers)
│   │   │   ├── graph.py             # build_graph(): nodes, edges, Send fan-out
│   │   │   ├── base.py              # run_agent(): events, retries, timing, error categories
│   │   │   ├── profile_analyst.py  opportunity_scout.py  verification_agent.py
│   │   │   ├── eligibility_analyst.py  ranking_application_agent.py
│   │   │   └── prompts/             # one .md or .py per agent, versioned
│   │   ├── domain/
│   │   │   ├── enums.py  profile.py  opportunity.py  evidence.py  eligibility.py
│   │   │   ├── criteria_rules.py    # deterministic evaluators (§9)
│   │   │   ├── ranking.py           # documented score (§9.4)
│   │   │   └── errors.py            # DomainError, provider error taxonomy
│   │   ├── providers/
│   │   │   ├── base.py              # LLMProvider, SearchProvider protocols
│   │   │   ├── llm_gemini.py  llm_groq.py  search_tavily.py  search_brave.py
│   │   │   ├── router.py            # call_with_fallback, circuit breaker, budgets
│   │   │   └── fakes.py             # deterministic fakes for tests
│   │   ├── tools/
│   │   │   ├── fetcher.py           # SSRF guard, retries, size cap
│   │   │   ├── extractors.py        # html/pdf/text → clean text
│   │   │   ├── retrieval.py         # chunk + BM25 selection
│   │   │   ├── quote_check.py       # excerpt verification
│   │   │   ├── github.py            # public profile enrichment
│   │   │   └── documents.py         # uploaded resume/transcript → text
│   │   └── infrastructure/
│   │       ├── db.py  models.py  repositories/{profiles,jobs,opportunities,events}.py
│   │       └── logging.py           # structured JSON logs + request/job ids
│   └── tests/ unit/ integration/ fixtures/{rahul.json, second_profile.json, pages/*.html}
├── frontend/
│   ├── package.json  vite.config.ts  tailwind.config.ts
│   └── src/
│       ├── main.tsx  App.tsx  routes.tsx
│       ├── api/ client.ts (fetch + token header)  types.ts (generated)  hooks.ts
│       ├── pages/ IntakePage.tsx  JobPage.tsx  DraftPage.tsx
│       ├── components/ AgentTimeline  OpportunityCard  EligibilityTable  EvidenceDrawer
│       │               StatusPill  ProviderBadge  FileDropzone  ErrorState  Skeletons
│       └── lib/ format.ts  tokenStore.ts
└── scripts/ eval_profiles.py  seed_demo.py  smoke_providers.py
```

---

## 6. Domain model (`domain/`)

### 6.1 Enums

```python
class CriterionKind(StrEnum):
    DEGREE_LEVEL="degree_level"; FIELD_OF_STUDY="field_of_study"; MIN_GRADE="min_grade"
    LANGUAGE="language"; NATIONALITY="nationality"; DEADLINE="deadline"
    WORK_EXPERIENCE="work_experience"; DOCUMENTS="documents"; OTHER="other"

class CriterionStatus(StrEnum):
    MEETS="meets"; LIKELY_MEETS="likely_meets"; DOES_NOT_MEET="does_not_meet"
    UNKNOWN="unknown"; NEEDS_REVIEW="needs_review"

class OverallEligibility(StrEnum):          # derived, never produced by an LLM
    NOT_ELIGIBLE="not_eligible"; MEETS_ALL_STATED="meets_all_stated"
    LIKELY_ELIGIBLE="likely_eligible"; NEEDS_INFO="needs_info"

class FundingType(StrEnum):
    FULL="full"; PARTIAL="partial"; TUITION_ONLY="tuition_only"; UNSPECIFIED="unspecified"; NONE="none"

class OpportunityKind(StrEnum): SCHOLARSHIP="scholarship"; PROGRAM="program"; PROGRAM_WITH_FUNDING="program_with_funding"
class SourceType(StrEnum): OFFICIAL="official"; AGGREGATOR="aggregator"; NEWS="news"; UNKNOWN="unknown"
class FetchStatus(StrEnum): OK="ok"; FAILED="failed"; PARSE_FAILED="parse_failed"; BLOCKED="blocked"
class VerificationStatus(StrEnum): VERIFIED="verified"; PARTIAL="partial"; UNVERIFIED="unverified"; CONFLICT="conflict"
class JobStatus(StrEnum): QUEUED="queued"; RUNNING="running"; COMPLETED="completed"; COMPLETED_WITH_WARNINGS="completed_with_warnings"; FAILED="failed"; CANCELLED="cancelled"
class AgentName(StrEnum): PROFILE="profile_analyst"; SCOUT="opportunity_scout"; VERIFY="verification_agent"; ELIGIBILITY="eligibility_analyst"; RANKING="ranking_application_agent"; COORDINATOR="coordinator"
```

### 6.2 Student profile (all fields optional except those marked)

```python
class Grade(BaseModel):  value: float; scale: float              # 8.2 / 10
class LanguageTest(BaseModel): test: str; score: float | None; taken_on: date | None
class Project(BaseModel): name: str; summary: str; skills: list[str]; url: HttpUrl | None; evidence: str  # where we saw it

class StudentProfile(BaseModel):
    full_name: str                                   # required
    nationality: str                                 # required (ISO country name)
    degree_level_held: DegreeLevel | None            # bachelor | master | phd
    degree_level_target: DegreeLevel                 # required: what they want to study next
    field_of_study: str | None
    institution: str | None
    graduation_year: int | None
    grade: Grade | None
    language_tests: list[LanguageTest] = []
    target_countries: list[str] = []
    interests: list[str] = []
    budget_note: str | None                          # "family cannot afford fees" → needs_funding
    needs_funding: bool = True
    skills: list[str] = []
    projects: list[Project] = []
    achievements: list[str] = []
    github_url: HttpUrl | None
    missing_information: list[str] = []              # produced by Profile Analyst
    provenance: dict[str, str] = {}                  # field → "resume" | "transcript" | "form" | "github"
```
Form values always override extracted values; conflicts are recorded in `missing_information` as `"conflict: …"`.

### 6.3 Evidence and criteria

```python
class EvidenceRef(BaseModel):
    source_id: UUID
    source_url: HttpUrl
    source_excerpt: str            # verbatim, quote-checked
    verified_at: datetime
    quote_verified: bool           # False → excerpt could not be matched in page text

class Criterion(BaseModel):
    id: str                        # stable: "{opportunity_id}:{kind}:{n}"
    kind: CriterionKind
    description: str
    required_value: str | None
    params: dict[str, Any] = {}    # typed per kind, see §9.2
    is_hard: bool = True           # false = "preferred"
    evidence: EvidenceRef | None

class CriterionAssessment(BaseModel):
    criterion_id: str; criterion: str; required_value: str | None
    student_value: str | None
    status: CriterionStatus
    reason: str
    next_action: str | None
    source_url: HttpUrl | None; source_excerpt: str | None; verified_at: datetime | None
```
This is exactly the JSON shape from your brief, with `criterion_id`, `reason` and `next_action` added.

### 6.4 Opportunity

```python
class Opportunity(BaseModel):
    id: UUID; job_id: UUID
    name: str; institution: str | None; country: str | None
    kind: OpportunityKind; official_url: HttpUrl | None
    funding_type: FundingType; funding_detail: str | None; funding_evidence: EvidenceRef | None
    deadline: date | None; deadline_evidence: EvidenceRef | None
    intake: str | None; application_url: HttpUrl | None; application_steps: list[str] = []
    criteria: list[Criterion] = []
    verification_status: VerificationStatus
    conflicts: list[FieldConflict] = []              # §15 scenario D
    discovery_sources: list[str]                     # URLs where we first found it
    candidate_notes: str | None

class FieldConflict(BaseModel): field: str; values: list[ConflictValue]  # each with source_url + excerpt

class RankedOpportunity(BaseModel):
    opportunity_id: UUID; rank: int | None           # None = assessed but not in top 5
    score: float; score_breakdown: dict[str, float]  # §9.4
    overall: OverallEligibility
    rationale: str                                   # grounded in assessments, validated (§8.5)
    trade_offs: list[str]; next_actions: list[str]
```

---

## 7. Database schema (PostgreSQL, Alembic)

JSONB is used for nested documents that are always read whole. Everything queried or constrained is a real column.

| Table | Columns (PK `id UUID` unless noted) | Constraints / indexes |
|---|---|---|
| `student_profiles` | `data JSONB` (StudentProfile), `access_token_hash`, `created_at`, `updated_at` | idx `access_token_hash` |
| `student_documents` | `profile_id FK`, `kind` (resume\|transcript\|other), `filename`, `mime`, `size_bytes`, `content BYTEA`, `extracted_text`, `extraction_status`, `extraction_error`, `created_at` | idx `profile_id`; size ≤ 5 MB |
| `research_jobs` | `profile_id FK`, `status`, `params JSONB` (countries, limits), `profile_snapshot JSONB`, `warnings JSONB`, `error JSONB`, `created_at`, `started_at`, `finished_at`, `heartbeat_at` | idx `(status)`, `(profile_id, created_at desc)`; **partial unique** `(profile_id) WHERE status IN ('queued','running')` (one active job per profile) |
| `agent_runs` | `job_id FK`, `agent`, `scope` (e.g. opportunity id or "global"), `status`, `attempt`, `started_at`, `duration_ms`, `error_category`, `error_message`, `provider_used`, `tokens_in`, `tokens_out` | idx `(job_id, agent)` |
| `job_events` | `job_id FK`, `seq BIGINT`, `agent`, `level`, `type`, `message`, `payload JSONB`, `at` | **unique `(job_id, seq)`**, used for `?after_seq=` polling |
| `sources` | `job_id FK`, `url`, `canonical_url`, `source_type`, `fetch_status`, `http_status`, `content_hash`, `text_content`, `extraction_method`, `error`, `fetched_at` | unique `(job_id, canonical_url)`; fetch cache within a job; global reuse allowed if `fetched_at` < 24 h |
| `opportunities` | `job_id FK`, `data JSONB` (Opportunity), `name`, `country`, `verification_status`, `deadline`, `created_at` | idx `(job_id)`; unique `(job_id, dedupe_key)` where `dedupe_key = sha1(lower(institution)+lower(name))` |
| `eligibility_assessments` | `opportunity_id FK`, `job_id FK`, `overall`, `assessments JSONB` (list[CriterionAssessment]), `computed_at` | unique `(opportunity_id)` |
| `rankings` | `job_id FK`, `opportunity_id FK`, `rank`, `score`, `breakdown JSONB`, `rationale`, `data JSONB` | unique `(job_id, opportunity_id)` |
| `application_drafts` | `job_id FK`, `opportunity_id FK`, `content_md`, `citations JSONB`, `model_used`, `created_at`, `version` | idx `(job_id, opportunity_id)` |
| LangGraph checkpoint tables | created by `AsyncPostgresSaver.setup()` | `thread_id = job_id` |

Write rule: every agent node **upserts** its output keyed by natural keys above, so a resumed node is idempotent.

---

## 8. Agents and the graph

### 8.1 Agent contracts

| Agent | Receives | Tools | Produces | On failure |
|---|---|---|---|---|
| **Profile Analyst** | form profile, uploaded text, GitHub URL | `documents`, `github.py`, LLM | normalized `StudentProfile` with `provenance`, `missing_information` | Missing/unparseable document → note in `missing_information`, continue with form data. GitHub rate limit → skip enrichment, record warning. LLM failure → fall back to form-only profile |
| **Opportunity Scout** | form preferences (countries, level, interests, funding need) | Search router, LLM | ≥ `MIN_CANDIDATES` (12) deduped `Candidate`s | A search provider failing → fallback provider. < 10 candidates after one query-widening pass → continue with fewer and add a job warning |
| **Verification Agent** (per candidate) | one `Candidate` | `fetcher`, `extractors`, `retrieval`, `quote_check`, LLM | `Opportunity` with typed `Criterion`s, funding, deadline, application steps, all with `EvidenceRef` | Fetch/parse failure → `verification_status=unverified` + preserved discovery data. Conflicts → both values stored |
| **Eligibility Analyst** (per candidate) | `Opportunity`, final `StudentProfile` | deterministic `criteria_rules`, LLM only for `OTHER` and field matching | `list[CriterionAssessment]` + derived `overall` | Never marks `does_not_meet` from an error. LLM failure → `needs_review` |
| **Ranking & Application Agent** | all opportunities + assessments | `ranking.py`, LLM for rationale | Top 5 `RankedOpportunity`; the SOP draft is generated **on demand** by `POST /drafts` | Rationale LLM failure → template rationale built from the assessments |

The Profile Analyst and the Scout start in parallel. The Scout is driven by **form preferences**, so it does not wait for document parsing. Profile relevance is applied at ranking, using the enriched profile.

### 8.2 Graph topology

```
START ─┬─► profile_analyst ───────────────┐
       └─► opportunity_scout ─► dedupe ───┤
                                          ▼
                                   join_candidates
                                          │  Send() per candidate (max concurrency = 3)
                                          ▼
                    ┌────────────── candidate_pipeline ──────────────┐
                    │  verify_candidate ─► assess_candidate          │   ← failures isolated here
                    └────────────────────────────────────────────────┘
                                          ▼
                                   collect_results ─► rank_and_select ─► finalize ─► END
```
`assess_candidate` runs only after both the final profile and that candidate's verification exist (guaranteed by the join).

### 8.3 State (`agents/state.py`)

```python
class ResearchState(TypedDict):
    job_id: str
    profile_input: StudentProfile
    documents: list[DocText]
    profile: StudentProfile | None
    candidates: Annotated[list[Candidate], add]
    opportunities: Annotated[dict[str, Opportunity], merge_dicts]     # by opportunity id
    assessments: Annotated[dict[str, list[CriterionAssessment]], merge_dicts]
    ranking: list[RankedOpportunity]
    warnings: Annotated[list[Warning], add]
    stats: dict[str, int]
```
Only small JSON-serialisable data lives in state; page text lives in `sources`.

### 8.4 Node wrapper (`agents/base.py`)

Every node is wrapped by `run_agent(agent, scope, fn)`, which: writes `agent_runs`, emits `job_events` (`started`, `progress`, `retrying`, `failed`, `completed`), applies `AGENT_TIMEOUT_S`, retries **retryable** errors up to 2 times with exponential backoff and jitter, categorises errors (`provider`, `fetch`, `parse`, `validation`, `timeout`, `bug`), and **returns a degraded result instead of raising** when the agent contract defines one. Only a genuine bug or `Cancelled` propagates.

### 8.5 Grounded rationale

The ranking rationale is generated from a JSON bundle of that opportunity's assessments. A validator rejects any sentence that mentions a number, date, or funding amount not present in the bundle (regex check), then falls back to the template rationale. The LLM never receives web text at this stage.

---

## 9. Eligibility and ranking (deterministic core)

### 9.1 Flow

1. Verification Agent extracts `Criterion` objects (LLM, structured output) from **BM25-selected chunks** of the official page.
2. `quote_check` validates each excerpt (§11.3). Failed → `evidence.quote_verified=False`.
3. Eligibility Analyst calls `criteria_rules.evaluate(criterion, profile, today)`.
4. `derive_overall(assessments)` computes `OverallEligibility`.

### 9.2 Rules per `CriterionKind` (`domain/criteria_rules.py`)

| Kind | `params` | Rule |
|---|---|---|
| `degree_level` | `min_level` | Ordinal compare with `degree_level_held`. Missing → `unknown` |
| `field_of_study` | `allowed_fields[]` | Normalised exact/synonym match → `likely_meets`. Otherwise `needs_review`. Never `meets` and never `does_not_meet` on semantic similarity alone |
| `min_grade` | `min_value`, `scale`, `rule_text` | Same scale on both sides and both numeric → compare (`meets` / `does_not_meet`). Different scale or "equivalent to…" wording → `needs_review` with next action "check the university's grade conversion rule". Missing grade → `unknown`. **An 8.2/10 is never auto-converted** |
| `language` | `tests_accepted[]`, `min_score`, `exemptions[]` | No test on profile → `unknown`. Test and score present → compare. Exemption text present → note it in `next_action` |
| `nationality` | `eligible[]`, `excluded[]`, `international_ok` | Explicit match → `meets`. Excluded → `does_not_meet`. Ambiguous wording → `needs_review` |
| `deadline` | `date` | Date in the past → `does_not_meet` ("closed; next intake unverified"). Future → `meets` with next action "confirm on the official page". No date → `unknown` |
| `work_experience` | `min_years` | Compare with profile if present, else `unknown` |
| `documents`, `other` | free text | LLM may return at most `likely_meets` / `needs_review` / `unknown`, with a reason. It cannot return `meets` or `does_not_meet` |

Hard criteria with `quote_verified=False` are downgraded to `unknown` with reason "evidence could not be verified".

### 9.3 Overall

```
not_eligible      if any hard criterion == does_not_meet
meets_all_stated  if every hard criterion == meets AND verification_status == verified
likely_eligible   if all hard in {meets, likely_meets}
needs_info        otherwise
```
The UI never uses the word "eligible" without the qualifier (`Meets all stated criteria`, `Likely eligible, verify the flagged items`, `Needs more information`, `Not eligible`).

### 9.4 Ranking score (prioritisation only, not a probability)

| Factor | Max | Computation |
|---|---|---|
| Funding fit | 25 | full 25 · partial 15 · tuition_only 12 · unspecified 5 · none 0 (halved if `needs_funding=false`) |
| Academic fit | 25 | share of academic criteria (`degree_level`, `min_grade`, `field_of_study`) that are `meets` (1.0) or `likely_meets` (0.7), `unknown`/`needs_review` (0.3) |
| Program relevance | 20 | LLM relevance 0–1 (profile interests/skills vs programme description), clamped, with a stored reason |
| Country preference | 10 | 10 in `target_countries`, 4 if none given, 0 otherwise |
| Deadline feasibility | 10 | > 60 d: 10 · 30–60: 7 · 14–30: 4 · < 14: 1 · closed or unknown: 0 |
| Evidence confidence | 10 | verified-quote hard criteria ÷ hard criteria |

Selection: exclude `not_eligible`, sort by score, allow at most 2 per institution, take 5. Each entry shows its `score_breakdown`. Opportunities that are assessed but not selected remain in the "Full list" with their status.

---

## 10. Provider layer and fallback

### 10.1 Interfaces

```python
class LLMProvider(Protocol):
    name: str
    async def generate(self, *, task: str, messages: list[Msg], schema: type[T], timeout_s: float) -> T: ...

class SearchProvider(Protocol):
    name: str
    async def search(self, query: str, *, max_results: int, include_domains: list[str] | None = None) -> list[SearchHit]: ...
# SearchHit(url, title, snippet, published: date|None, provider: str)   ← the one normalised shape
```

### 10.2 Error taxonomy (`domain/errors.py`)

```
ProviderError
├── RetryableProviderError (timeout, 429 with retry_after, 5xx, network)
├── PermanentProviderError (401/403 invalid key, 400 bad request, model not found)
└── InvalidOutputError (JSON/schema validation failed after one repair attempt)
```

### 10.3 Router (`providers/router.py`)

```python
async def call_with_fallback(providers, op, *, task, validate):
    errors = []
    for p in providers:
        if breaker.is_open(p.name):                    # opens after 3 consecutive failures, 60 s cool-down
            errors.append((p.name, "circuit_open")); continue
        for attempt in range(MAX_ATTEMPTS):            # 2 attempts per provider
            try:
                result = await asyncio.wait_for(op(p), TIMEOUT[task])
                validate(result)                       # pydantic + task contract
                breaker.success(p.name); return Result(value=result, provider=p.name)
            except RetryableProviderError as e:
                breaker.failure(p.name); await sleep(backoff(attempt, e.retry_after))
            except (PermanentProviderError, InvalidOutputError) as e:
                breaker.failure(p.name); errors.append((p.name, repr(e))); break
        errors.append((p.name, "exhausted"))
    raise AllProvidersFailed(errors)
```
Rules: the fallback receives the **same schema** (a fallback that cannot produce it fails over, it is never accepted as prose). `Retry-After` is honoured, capped at 20 s. A per-job **LLM call budget** (`MAX_LLM_CALLS_PER_JOB`, default 120) and a global concurrency semaphore (`LLM_CONCURRENCY=2`) protect free quotas. Search results from either provider are normalised to `SearchHit`, then deduped by canonical URL. `GET /health/providers` reports configured, breaker state, last error and last success.

**GAP-4 default:** Tavily is primary. Brave is used only if `BRAVE_API_KEY` is set. If it is not, the secondary search path is Tavily with a rewritten query, and the health endpoint states that no independent fallback is configured.

---

## 11. Evidence pipeline (`tools/`)

### 11.1 Official-source rule

Each fetched page gets a `SourceType`:
1. Host on `AGGREGATOR_DENYLIST` (scholars4dev, shiksha, studyportals, leverageedu, etc.): `aggregator`.
2. Host matches a **known-official** pattern (`*.edu`, `*.edu.*`, `*.ac.*`, `*.gov`, `*.gov.*`, `*.uni-*.de`, `*.tu-*.de`, `daad.de`, `chevening.org`, and entries in `OFFICIAL_ALLOWLIST`): `official`.
3. Otherwise a **classifier prompt** answers "is this the page of the awarding body or institution itself?" with a one-line reason: `official` or `unknown`.

Only `official` pages create `verified` evidence. Aggregator content may seed a candidate but is never quoted as proof. If an aggregator is the only source, `verification_status = unverified`.

### 11.2 Fetcher (`tools/fetcher.py`)

- Allow `http`/`https` only. Resolve the host and **block private, loopback and link-local IPs** (SSRF), because URLs come from search results.
- `httpx.AsyncClient`, connect 5 s, total 15 s, max body 5 MB, max 3 redirects, polite `User-Agent`, `Accept-Language: en`.
- Retries: 2 on timeout, 429 (honour `Retry-After`), 5xx, with exponential backoff and jitter.
- Content-type switch: HTML → `trafilatura.extract` (fallback: `selectolax` text); PDF → `pypdf`, then `pdfplumber`; both failed → `Tavily extract` for that URL; all failed → `FetchStatus.PARSE_FAILED` with the error recorded.
- Cache by `(job_id, canonical_url)`, plus reuse of a global entry less than 24 h old.

### 11.3 Chunk selection and quote verification

- `retrieval.select_chunks(text, query_terms)`: split into ~800-character chunks with overlap, rank with BM25 using terms such as *eligibility, requirements, deadline, funding, tuition, scholarship, language, IELTS, GPA, international*, keep the top chunks within ~6k tokens. Prompts include the chunk text and its URL.
- `quote_check.verify(excerpt, page_text)`: normalise both (casefold, collapse whitespace, normalise quotes and dashes). Accept on an exact substring match, else on a `rapidfuzz.partial_ratio ≥ 92`. Otherwise `quote_verified=False` and the field is demoted (§9.2). The stored excerpt is the **matched span from the page**, not the LLM's text.

### 11.4 GitHub enrichment (`tools/github.py`)

`GET /users/{u}`, `/users/{u}/repos?sort=updated&per_page=30`, README of the top 5 by stars/recency, language stats. Optional `GITHUB_TOKEN` raises the limit from 60 to 5,000 requests/hour. The Profile Analyst turns this into `Project`/`skills` entries, each with an `evidence` string (repo URL). Never invent projects.

---

## 12. API contract (`/api/v1`, JSON, `snake_case`)

### 12.1 Conventions

| Topic | Rule |
|---|---|
| Auth | `X-Access-Token` header (§13). Returned once by `POST /profiles` |
| Errors | `application/problem+json`: `{type, title, status, code, detail, request_id, errors[]}` |
| Request id | `X-Request-ID` in and out |
| Timestamps | ISO-8601 UTC |
| Idempotency | `POST /research-jobs` returns the existing active job (`200`) if the profile already has one running (enforced by the partial unique index) |
| Pagination | Events use `?after_seq=&limit=` (max 200). Results are bounded (≤ 30 opportunities) |

### 12.2 Endpoints

| Method | Path | Auth | Body → Response | Errors |
|---|---|---|---|---|
| POST | `/profiles` | none | `ProfileCreate` → `201 {profile, access_token}` | 422 |
| GET | `/profiles/{id}` | token | → `Profile` | 401, 404 |
| PUT | `/profiles/{id}` | token | `ProfileUpdate` → `Profile` | 404, 409 (job running) |
| POST | `/profiles/{id}/documents` | token | multipart (`kind`, `file`) → `201 DocumentOut {id, extraction_status, preview}` | 413, 415, 422 |
| GET | `/profiles/{id}/documents` | token | → `[DocumentOut]` | |
| POST | `/research-jobs` | token | `{profile_id, countries?, max_candidates?}` → `202 JobOut` | 404, 429 |
| GET | `/research-jobs/{id}` | token | → `JobOut {status, progress{stage, done, total}, warnings, error}` | 404 |
| GET | `/research-jobs/{id}/events` | token | `?after_seq` → `{events[], last_seq}` | 404 |
| GET | `/research-jobs/{id}/results` | token | → `ResultsOut` (§12.3) | 404, 409 (not ready, partial results returned with `partial=true` when available) |
| POST | `/research-jobs/{id}/retry` | token | → `202 JobOut` (resumes from checkpoint) | 409 |
| POST | `/research-jobs/{id}/cancel` | token | → `JobOut` | 409 |
| POST | `/research-jobs/{id}/drafts` | token | `{opportunity_id, tone?}` → `201 DraftOut` | 404, 409 (opportunity not assessed), 503 (`ALL_PROVIDERS_FAILED`) |
| GET | `/research-jobs/{id}/drafts/{draft_id}` | token | → `DraftOut` | 404 |
| GET | `/health` | none | `{status, version}` | |
| GET | `/health/providers` | none | per provider `{configured, breaker, last_ok_at, last_error}` | |

### 12.3 `ResultsOut`

```json
{
  "job": { "id": "…", "status": "completed_with_warnings", "partial": false },
  "summary": { "candidates": 14, "verified": 9, "partially_verified": 3, "unverified": 2, "not_eligible": 2 },
  "profile": { "…normalised StudentProfile with provenance…": "" },
  "top": [ { "rank": 1, "score": 81.5, "score_breakdown": {"funding": 25, "academic": 20.4, "relevance": 15, "country": 10, "deadline": 7, "evidence": 4.1},
             "overall": "likely_eligible", "rationale": "…", "trade_offs": ["…"], "next_actions": ["Submit an IELTS score"],
             "opportunity": { "id": "…", "name": "…", "institution": "…", "country": "Germany", "funding_type": "partial",
                              "deadline": "2026-12-15", "deadline_evidence": { "source_url": "…", "source_excerpt": "…", "verified_at": "…" },
                              "application_url": "…", "application_steps": ["…"] },
             "assessments": [ { "criterion": "English proficiency", "required_value": "Accepted English-language test or exemption",
                                "student_value": null, "status": "unknown", "reason": "No test result supplied",
                                "next_action": "Provide IELTS/TOEFL or check exemption", "source_url": "…", "source_excerpt": "…", "verified_at": "…" } ] } ],
  "all": [ { "…same row shape without assessments, plus verification_status and overall…": "" } ],
  "warnings": [ { "agent": "verification_agent", "scope": "…", "message": "Official page unreachable; kept discovery data (unverified)" } ]
}
```

### 12.4 Controllers (routers) are thin

A router does exactly: parse/validate DTO → resolve `current_profile` dependency → call **one** use case → map the result to a DTO. No SQL, no business rules, no provider calls in routers. Exceptions inherit `DomainError` and are mapped centrally in `api/errors.py`:

| Exception | Status | `code` |
|---|---|---|
| `NotFound`, token mismatch | 404 | `NOT_FOUND` |
| `MissingToken` | 401 | `UNAUTHENTICATED` |
| `ActiveJobExists` / `NotReady` / `Conflict` | 409 | `CONFLICT` / `NOT_READY` |
| `AllProvidersFailed` | 503 | `ALL_PROVIDERS_FAILED` |
| `RateLimited` | 429 | `RATE_LIMITED` |
| Pydantic validation | 422 | `VALIDATION_ERROR` |
| anything else | 500 | `INTERNAL` (no stack trace in the body) |

---

## 13. Authentication and security

Accounts are unnecessary for a demo and would add risk. We use **capability tokens**:

- `POST /profiles` generates `secrets.token_urlsafe(32)`, stores only its SHA-256, and returns the token **once**. The frontend keeps it in `localStorage` keyed by profile id and sends `X-Access-Token`.
- The `current_profile` dependency loads the profile by id, compares hashes with `hmac.compare_digest`, and returns **404** (not 403) on mismatch. Jobs, documents, drafts and events are reachable only through the owning profile.
- Upload limits: 5 MB; allowed MIME `application/pdf`, `text/plain`, `text/markdown`; extension and magic-byte check; files are never executed or served back raw.
- Rate limits (`slowapi`, per IP): 20 profile creates/hour, 5 research jobs/hour, 10 drafts/hour. Global concurrency: 2 running jobs; extra jobs wait as `queued`.
- CORS: only `FRONTEND_ORIGIN`. Secrets only in env vars, never in logs. Logs redact tokens and API keys. User text sent to LLMs is wrapped as **data** with an instruction not to follow instructions inside it, and fetched page text is treated as untrusted in the same way.
- PII: demo data only (the brief requires fictional or consented profiles). `DELETE /profiles/{id}` is **not** built; a `scripts/purge.py` clears old data.

---

## 14. Job execution and recovery

**Start.** `StartResearch` creates the job (`queued`), snapshots the profile, returns `202`. `JobRunner` starts an `asyncio` task when a global slot is free. The graph runs with `config={"configurable": {"thread_id": job_id}}`.

**Heartbeat.** The runner updates `research_jobs.heartbeat_at` every 10 s.

**Crash recovery (`recover_jobs.py`, run in the FastAPI lifespan).** On startup, find jobs in `running` with `heartbeat_at` older than 60 s, then resume each with `graph.ainvoke(None, config)` (LangGraph continues from its last checkpoint). Nodes are idempotent (§7 write rule), so re-run branches are safe. If resume raises, mark `failed` with a message, and keep the partial results readable. The user can press **Retry**, which calls the same resume path.

**Render free-tier note.** The service sleeps after ~15 minutes idle and can be restarted. The recovery path above is what makes that safe. Before the demo, hit `/health` to warm it (**GAP-2**).

**Completion.** `completed` if no warnings, `completed_with_warnings` if any candidate was unverified or an agent degraded, `failed` only if no opportunity could be assessed at all.

**Time budget.** Target ≤ 6 minutes per job: scout ≤ 45 s, verification ≤ 4 min total at concurrency 3, ranking ≤ 30 s. A hard job timeout of 12 minutes marks remaining candidates `unverified` and finishes with what exists.

---

## 15. Failure matrix

| Failure | Detection | Behaviour | Visible to user |
|---|---|---|---|
| **A** University site down/timeouts | `httpx` timeout, 5xx | 2 retries with backoff → `FetchStatus.FAILED`; opportunity `unverified`; earlier cached evidence kept with its `verified_at`; other candidates continue | Warning chip "Couldn't reach official page; showing earlier data (retrieved …)" |
| **B** PDF unparseable | `pypdf` error / empty text | Try `pdfplumber` → Tavily extract → record `extraction_error` | "Source unreadable; criteria unknown" |
| **C** Malformed agent output | Pydantic `ValidationError` | One repair retry with the validation error in the prompt → fallback provider → `degraded` result | Event log `retrying (validation)` |
| **D** Sources contradict | Same field, different values from ≥ 2 sources | Prefer official; store both in `conflicts`; field flagged `needs_review`; never auto-pick | Conflict badge with both excerpts |
| E Provider quota/outage | 429/5xx/timeouts, breaker | Fallback provider, same schema; both down → degrade per agent contract | `ProviderBadge` shows state |
| F Search returns junk | < 10 candidates, mostly aggregators | One query-widening pass (broaden countries/level), then continue with warning | "Found N candidates" warning |
| G Backend restart | stale heartbeat | Resume from checkpoint | Timeline continues |
| H Uploaded document unreadable | extraction fails | Mark `extraction_status=failed`; proceed with form data | "We couldn't read transcript.pdf" |
| I Hallucinated number in rationale | validator | Replace with template rationale | none |
| J Candidate lacks any official page | classifier | `unverified`, excluded from Top 5, listed in full list | "Unverified" label |

---

## 16. Frontend

### 16.1 Pages and flow

| Route | Purpose |
|---|---|
| `/` IntakePage | Form (name, nationality, degree held/target, field, institution, CGPA + scale, language tests, target countries, interests, funding need, GitHub URL) + `FileDropzone` (resume, transcript) + "Load demo profile (Rahul)" button + **Start research** |
| `/jobs/:id` JobPage | Header with status and progress. Left: `AgentTimeline` (five lanes with state: waiting / running / retrying / done / degraded, live event log). Right/below: tabs **Top 5**, **All opportunities**, **Profile**, **Warnings** |
| `/jobs/:id/draft/:draftId` DraftPage | Rendered SOP with a citations panel, copy and download as `.md` |

### 16.2 Components

`OpportunityCard` (rank, score with breakdown tooltip, funding, deadline with verified date, overall label) · `EligibilityTable` (criterion, student value, status pill, reason, "View source") · `EvidenceDrawer` (URL, verbatim excerpt, verified-at, `quote_verified` flag) · `StatusPill` · `ProviderBadge` · `ErrorState` · skeletons.

### 16.3 State and data

- **TanStack Query only** for server state. `useJob(id)` polls every 1.5 s while `status ∈ {queued, running}`, then stops. `useEvents(id)` polls with `after_seq`, appending to a local list. `useResults(id)` enabled when the job is terminal (and also fetched as `partial` on demand).
- Forms: `react-hook-form` + `zod` mirroring the backend DTO.
- Types generated with `openapi-typescript` from `/openapi.json` (`npm run gen:api`).
- `api/client.ts`: base URL from `VITE_API_URL`, injects `X-Access-Token`, parses Problem Details into a typed `ApiError`, never retries 4xx.
- Persisted client state: `{profileId, accessToken, lastJobId}` in `localStorage`, so a refresh resumes the job view.
- UX rules: status text is always a label plus colour (accessibility), every table scrolls horizontally on small screens, loading uses skeletons, every error has a retry or next step.

---

## 17. Configuration (`.env.example`)

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/scholarpilot
FRONTEND_ORIGIN=http://localhost:5173
GEMINI_API_KEY=   GEMINI_MODEL=
GROQ_API_KEY=     GROQ_MODEL=
TAVILY_API_KEY=   BRAVE_API_KEY=            # optional
GITHUB_TOKEN=                               # optional
MIN_CANDIDATES=12  MAX_CANDIDATES=18  FETCH_CONCURRENCY=3  LLM_CONCURRENCY=2
MAX_LLM_CALLS_PER_JOB=120  JOB_TIMEOUT_S=720  AGENT_TIMEOUT_S=90
LOG_LEVEL=INFO  ENV=dev
```

---

## 18. Testing (risk-driven, run in CI with fakes and `respx`)

| ID | Behaviour | Level |
|---|---|---|
| T-ELG-1 | Every `CriterionKind` × status path; 8.2/10 vs "min 3.0 on 4.0 scale" → `needs_review`, never `meets` | unit |
| T-ELG-2 | LLM `OTHER` criterion cannot return `meets` | unit |
| T-ELG-3 | `derive_overall` truth table | unit |
| T-EVD-1 | `quote_check`: exact, whitespace/quote variants pass, invented text fails | unit |
| T-EVD-2 | Aggregator-only candidate stays `unverified` and out of the Top 5 | integration |
| T-RNK-1 | Score breakdown sums, ordering, institution cap, `not_eligible` excluded | unit |
| T-PRV-1 | Router: primary timeout → fallback; both fail → `AllProvidersFailed`; breaker opens/closes; fallback invalid schema is rejected | unit |
| T-FET-1 | SSRF guard blocks `127.0.0.1`, `169.254.169.254`, private ranges | unit |
| T-FET-2 | Timeout → retries → `FAILED` while other candidates still finish | integration (`respx`) |
| T-FET-3 | PDF fallback chain | integration |
| T-GRP-1 | Full graph with fake LLM/search on `fixtures/pages`: ≥ 10 candidates, Top 5, warnings present when one page is removed | integration |
| T-GRP-2 | Kill the runner mid-graph, call recovery, the job completes and no duplicates exist | integration |
| T-API-1 | Token auth: wrong token → 404, active-job uniqueness, upload limits | integration |
| T-ADP-1 | `scripts/eval_profiles.py` runs **two different fixtures** (Rahul and a non-CS profile) through the same graph with fakes, asserting no code path is profile-specific | integration |

---

## 19. Demo and submission plan

**Demo script (5 minutes).** (1) Load Rahul, upload resume and transcript, start. (2) Narrate the timeline: parallel Profile and Scout lanes, fan-out verification. (3) **Induce a failure live**: set one candidate URL to an unreachable host via `DEMO_FAIL_HOSTS` and show the warning plus the others finishing. (4) Open the #1 card, show the criterion table and the **EvidenceDrawer** with the verbatim excerpt. (5) Point out the `unknown` English-proficiency row ("we don't invent"). (6) Generate the SOP draft. (7) Load the second profile to show adaptation.

**Fallback if live APIs fail during the final demo.** `scripts/seed_demo.py` stores a completed job; `/jobs/{id}` renders from the database. Say so openly.

**Deliverables.** Repo, deployed URL, 5-minute recording, a diagram (use your two images), and `AGENT_DESIGN_NOTE.md`: *most interesting experiment* = quote-verified evidence plus deterministic eligibility; *biggest challenge* = making agent output trustworthy under free-tier limits.

---

## 20. Build order (do not reorder)

| Phase | Work | Gate |
|---|---|---|
| 0 (≈1.5 h) | Repo, config, DB + Alembic, health endpoints, deploy skeleton to Render and Vercel, `smoke_providers.py` (one call each to Gemini, Groq, Tavily) | Both deploys live; all providers answer |
| 1 (≈2.5 h) | Domain models and enums, `criteria_rules`, `ranking`, `quote_check`, unit tests | T-ELG, T-EVD-1, T-RNK green |
| 2 (≈2.5 h) | Providers + router + fetcher/extractors/retrieval, tests | T-PRV, T-FET green |
| 3 (≈4 h) | Agents, graph, `base.run_agent`, job runner, events, repositories, API routers | T-GRP-1 green; a real job runs end to end locally |
| 4 (≈1.5 h) | Recovery, retry/cancel, draft endpoint | T-GRP-2, T-API-1 green |
| 5 (≈4 h) | Frontend: intake, job page, timeline, report, drafts | Real job viewable on the deployed site |
| 6 (≈2 h) | Second-profile run, demo seed, README, diagram, recording | Checklist below |

**Cut line if time runs short (cut from the bottom):** Brave fallback → GitHub README fetching → job cancel → `partial` results → recovery endpoint UI. **Never cut:** quote verification, deterministic eligibility, per-candidate failure isolation, the timeline, the draft.

**Final checklist.** ≥ 10 candidates on both profiles · every Top-5 card has verified evidence or an explicit `unverified` tag · failure demo works · `.env` not committed · README gives exact local and deployed steps · recording shows an agent failing and recovering.

---

## 21. Known limitations and open gaps

**Limitations.** Free-tier quotas cap throughput. Pages needing JavaScript rendering are not supported (flagged as `parse_failed`). Deadlines are as published on the day fetched. Non-English pages are only handled when the LLM can read them. Not a source of admission advice.

**Gaps to confirm (defaults are in force until you change them).**

| # | Gap | Default |
|---|---|---|
| GAP-1 | GitHub token | Optional; 60 req/h is enough for one profile |
| GAP-2 | Render free tier sleeps | Warm `/health` before the demo; recovery covers restarts |
| GAP-3 | Exact Gemini/Groq model ids and daily quotas | Check on day 0 and set in `.env`; the smoke script reports them |
| GAP-4 | Brave needs a card | Brave optional; otherwise the fallback is Tavily with a rewritten query |
| GAP-5 | Draft target | The user picks any Top-5 opportunity; the draft cites only the profile and verified criteria |
| GAP-6 | Document scope | PDF and plain text only; image-only scans are flagged, not OCR'd |
