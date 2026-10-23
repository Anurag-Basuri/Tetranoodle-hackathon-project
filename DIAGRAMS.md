# ScholarPilot AI - System & Agent Architecture Diagrams

This document provides visual diagrams explaining the end-to-end architecture of **ScholarPilot AI**:
1. **Diagram 1: End-to-End System Flow Diagram** — Shows how users, the frontend, the REST API, the **Agent Swarm Node**, external services, and the database communicate.
2. **Diagram 2: Autonomous Multi-Agent Swarm Workflow** — Deep-dive into the internal execution graph of the cooperating AI agents.

---

## Diagram 1: End-to-End System Flow Diagram

This diagram displays the full application lifecycle. The **Autonomous Multi-Agent Swarm** sits at the center as the intelligence engine.

```mermaid
flowchart LR
    classDef client fill:#18181b,stroke:#3f3f46,stroke-width:1px,color:#f4f4f5;
    classDef api fill:#1e1b4b,stroke:#4338ca,stroke-width:1px,color:#e0e7ff;
    classDef agentNode fill:#042f2e,stroke:#0d9488,stroke-width:2px,color:#ccfbf1;
    classDef ext fill:#18181b,stroke:#3f3f46,stroke-width:1px,color:#f4f4f5;
    classDef db fill:#311042,stroke:#7e22ce,stroke-width:1px,color:#f3e8ff;

    subgraph Client ["1. Frontend Client (Vercel)"]
        User(["Student / Evaluator"]):::client
        UI["ScholarPilot UI\n(React 19 + TypeScript)\n• Intake Form\n• Live Agent Pipeline\n• Evidence Report"]:::client
    end

    subgraph Backend ["2. Backend Service (Render)"]
        API["FastAPI REST API\n• Token Guard (X-Access-Token)\n• SSE Event Stream (/events)\n• Results Endpoint (/results)"]:::api
        
        AgentSwarm[["★ Autonomous Multi-Agent Swarm ★\n(LangGraph State Machine Engine)\n• 5 Cooperating AI Agents\n• Parallel Fan-Out\n• Checkpoint Recovery"]]:::agentNode
    end

    subgraph External ["3. External Services & Live Web"]
        Search["Search Engines\n(Tavily / Brave APIs)"]:::ext
        Websites["Official University Pages\n(.edu / .gov / DAAD)\nLive HTML & PDF Crawling"]:::ext
        GitHub["GitHub REST API\n(Public Repos, Stars, Topics)"]:::ext
        LLM["LLM Providers\n(Gemini 2.5 Flash / Groq LLaMA)"]:::ext
    end

    subgraph Storage ["4. Database (Neon PostgreSQL)"]
        NeonDB[("Neon Serverless Postgres\n• Profiles & Jobs\n• Live Agent Events\n• Opportunities & Proofs\n• 6-Factor Rankings")]:::db
    end

    User -->|1. Submit Profile & Docs| UI
    UI -->|2. POST /profiles & /research-jobs| API
    API -->|3. Save Initial State| NeonDB
    API -->|4. Launch Async Job| AgentSwarm
    
    AgentSwarm <-->|Enrich Developer Profile| GitHub
    AgentSwarm <-->|Search Programs (≥12)| Search
    AgentSwarm <-->|Fetch Official Pages| Websites
    AgentSwarm <-->|Reasoning & Extraction| LLM
    
    AgentSwarm -->|5. Stream Progress Events| NeonDB
    AgentSwarm -->|6. Persist Final Verified Report| NeonDB
    
    NeonDB -.->|7. Real-Time SSE Stream| API
    API -.->|8. Live Progress & Final Report| UI
    UI -.->|9. Interactive Report & Evidence Drawer| User
```

### Data Flow Steps in the System:
1. **Intake**: The student enters their profile and uploads a resume or transcript via the React UI.
2. **API Registration**: FastAPI validates inputs, generates a tamper-proof capability token (`X-Access-Token`), and records the job.
3. **Agent Delegation**: The API hands execution to the **Autonomous Multi-Agent Swarm** running in the background.
4. **Live Research**: The agents query Tavily/Brave, scrape official university domains with SSRF protection, query GitHub for developer stats, and consult LLMs for structured extraction.
5. **Streaming & Storage**: Every milestone is logged to Neon PostgreSQL and streamed back to the user interface via Server-Sent Events (SSE).
6. **Delivery**: The user inspects the final Top 5 ranked opportunities, criteria evaluation tables, and slide-over evidence audit drawer.

---

## Diagram 2: Autonomous Multi-Agent Swarm Workflow

This diagram zooms inside the **★ Autonomous Multi-Agent Swarm ★** node to illustrate how the 5 specialized agents collaborate autonomously via LangGraph.

```mermaid
flowchart TD
    classDef startNode fill:#18181b,stroke:#52525b,stroke-width:1px,color:#f4f4f5;
    classDef agent1 fill:#172554,stroke:#2563eb,stroke-width:1.5px,color:#dbeafe;
    classDef agent2 fill:#14532d,stroke:#16a34a,stroke-width:1.5px,color:#dcfce7;
    classDef agent3 fill:#701a75,stroke:#c026d3,stroke-width:1.5px,color:#fae8ff;
    classDef agent4 fill:#7c2d12,stroke:#ea580c,stroke-width:1.5px,color:#ffedd5;
    classDef agent5 fill:#042f2e,stroke:#0d9488,stroke-width:2px,color:#ccfbf1;
    classDef draftAgent fill:#1f2937,stroke:#4b5563,stroke-width:1.5px,color:#f3f4f6;

    Start(["START: Intake Job\n(Student Profile + Uploaded Transcripts/Resumes)"]):::startNode

    subgraph ParallelStage1 ["Stage 1: Parallel Profile Analysis & Discovery"]
        direction LR
        A1["Agent 1: Profile Analyst\n• Extract Degree, CGPA, Target Field\n• Normalize Grade Scale (e.g. 8.2/10)\n• Enrich GitHub repos, stars, topics"]:::agent1
        A2["Agent 2: Opportunity Scout\n• Expand country & subject search queries\n• Query Tavily / Brave Search APIs\n• Discover ≥ 12 Candidate Programs"]:::agent2
    end

    subgraph FanOutStage2 ["Stage 2: Parallel Candidate Verification & Eligibility (LangGraph Send)"]
        direction TB
        subgraph CandidateBranch ["Executed in parallel for each candidate (1 .. N)"]
            A3["Agent 3: Verification Agent\n• Filter Aggregator Denylist (Shiksha, etc.)\n• SSRF Guard & Official Domain Classification\n• Crawl Official Page HTML/PDF via Trafilatura\n• RapidFuzz Verbatim Quote Check (≥ 92%)\n• Tag as Verified, Partial, or Unverified"]:::agent3
            
            A4["Agent 4: Eligibility Analyst\n• Deterministic Python Rules (No LLM math!)\n• Grade Comparison against minimum\n• Degree level ordinal prerequisite check\n• Nationality whitelist/blacklist check\n• Deadline comparison vs today\n• Tag: Meets, Fails, or Unknown"]:::agent4

            A3 -->|Verified Evidence & Excerpts| A4
        end
    end

    subgraph JoinStage3 ["Stage 3: Multi-Criteria Ranking & Application Synthesis"]
        A5["Agent 5: Ranking & Selection Agent\n• Compute Transparent 6-Factor Score (0 - 100):\n  - Funding Fit (30%)\n  - Academic Fit (25%)\n  - Program Relevance (20%)\n  - Country Preference (10%)\n  - Deadline Feasibility (10%)\n  - Evidence Confidence (5%)\n• Apply Diversity Cap: max 2 per institution\n• Select Top 5 Ranked Opportunities"]:::agent5
        
        SOP["SOP Drafting Agent (On Demand)\n• Generate Grounded Statement of Purpose\n• Map Student Strengths to Program Specs\n• Insert Verbatim Inline Bracketed Citations"]:::draftAgent
    end

    End(["END: Evidence-Backed Eligibility Report\n(Top 5 Ranked + Verbatim Excerpts + Grounded SOP)"]):::startNode

    Start --> A1
    Start --> A2
    A1 -->|Student Academic Baseline| A4
    A2 -->|LangGraph Send() Fan-Out| A3
    A4 -->|Individual Opportunity Assessments| A5
    A1 -->|Student Research Profile| A5
    A5 --> SOP
    A5 --> End
    SOP --> End
```

### Key Architectural Highlights:
1. **Parallel Start**: The Profile Analyst and Opportunity Scout run simultaneously at job initiation to eliminate sequential bottleneck delays.
2. **Dynamic Fan-Out**: The pipeline uses LangGraph's `Send()` API to evaluate candidates in parallel isolated workers. A fetch failure on one candidate never crashes the overall swarm.
3. **Zero Hallucination Division of Labor**:
   - LLMs are used solely for unstructured text reading and structured schema extraction.
   - Deterministic Python rules evaluate grade mathematics, prerequisite degree levels, and date comparisons.
   - RapidFuzz token matching ($\ge 92\%$) discards any quote that cannot be found verbatim in the source text.
4. **Transparent Explainability**: Every ranked opportunity contains a granular 6-factor score strip, specific trade-offs, and clear next actions.
