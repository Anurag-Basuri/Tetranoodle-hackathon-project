# ScholarPilot AI - Deployment Guide

This guide walks you through deploying **ScholarPilot AI** to production:
- **Backend**: Deployed on [Render](https://render.com) as a Python Web Service.
- **Frontend**: Deployed on [Vercel](https://vercel.com) as a modern Vite SPA.
- **Database**: Hosted on [Neon](https://neon.tech) Serverless PostgreSQL.

---

## Architecture Topology

```
+--------------------------------------------------------+
|                   Vercel (Frontend)                    |
|      https://scholarpilot.vercel.app                   |
|      - Vite + React + TailwindCSS                      |
|      - vercel.json SPA Route Rewrites                  |
+---------------------------+----------------------------+
                            |
                     HTTPS / JSON / SSE
                            |
                            v
+--------------------------------------------------------+
|                    Render (Backend)                    |
|      https://scholarpilot-api.onrender.com             |
|      - FastAPI + Uvicorn (Python 3.11)                 |
|      - LangGraph 5-Agent Pipeline                      |
|      - In-Memory Capability Tokens & CORS Regex        |
+---------------------------+----------------------------+
                            |
                 asyncpg SSL Connection
                            |
                            v
+--------------------------------------------------------+
|                 Neon Serverless PostgreSQL             |
|      - PostgreSQL 16 + Connection Pooling              |
|      - 6 Core Relational Tables                        |
+--------------------------------------------------------+
```

---

## Part 1: Deploy Backend to Render

You can deploy the backend using either **Render Blueprint** (automated) or **Manual Web Service**.

### Option A: Render Blueprint (Recommended - 1-Click)

1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top navigation and select **Blueprint**.
3. Connect your GitHub account and select repository: `Anurag-Basuri/Tetranoodle-hackathon-project`.
4. Render detects the `render.yaml` at the root and prompts you to fill in the required environment variables:
   - `DATABASE_URL`: Your Neon PostgreSQL asyncpg connection string.
     ```
     postgresql+asyncpg://neondb_owner:YOUR_PASSWORD@ep-xxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `GROQ_API_KEY`: Your Groq API key (optional/fallback).
   - `TAVILY_API_KEY`: Your Tavily Search API key.
   - `BRAVE_API_KEY`: Your Brave Search API key (optional/fallback).
   - `FRONTEND_ORIGIN`: Your planned Vercel URL (e.g. `https://scholarpilot.vercel.app`).
5. Click **Apply**. Render will build and start your service automatically.

---

### Option B: Manual Web Service Setup on Render

If you prefer setting it up manually:

1. Click **New +** -> **Web Service**.
2. Connect repository: `Anurag-Basuri/Tetranoodle-hackathon-project`.
3. Configure service details:
   - **Name**: `scholarpilot-api`
   - **Region**: Choose the region closest to your Neon database (e.g., `Ohio (US East)`).
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
4. Under **Advanced** -> **Health Check Path**, enter:
   ```
   /health
   ```
5. In the **Environment Variables** section, add:
   | Key | Value | Description |
   |---|---|---|
   | `PYTHON_VERSION` | `3.11.9` | Ensures Python 3.11 compatibility |
   | `ENV` | `production` | Production mode |
   | `LOG_LEVEL` | `INFO` | Standard logging |
   | `DATABASE_URL` | `postgresql+asyncpg://neondb_owner:...` | Neon DB string with `sslmode=require` |
   | `GEMINI_API_KEY` | `AIzaSy...` | Gemini API key |
   | `GEMINI_MODEL` | `gemini-2.5-flash` | Primary extraction model |
   | `GROQ_API_KEY` | `gsk_...` | Optional fallback LLM |
   | `TAVILY_API_KEY` | `tvly-...` | Web search provider |
   | `FRONTEND_ORIGIN` | `https://scholarpilot.vercel.app` | Vercel domain |
   | `MIN_CANDIDATES` | `12` | Research pipeline candidate target |
   | `MAX_CANDIDATES` | `18` | Research pipeline max candidates |
6. Click **Create Web Service**.
7. Once deployed, copy your Render service URL:
   `https://scholarpilot-api.onrender.com`

---

### Verifying Backend Health

Verify that the backend is responding before deploying the frontend:

```bash
curl -s https://scholarpilot-api.onrender.com/health
```

Expected response:
```json
{"status":"ok","version":"1.0.0","env":"production"}
```

> **Note on Render Free Tier**: If the service has been idle for 15 minutes, Render will put it to sleep. The first request after a sleep period may take ~40-50 seconds to spin up. Subsequent requests respond instantly.

---

## Part 2: Deploy Frontend to Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository: `Anurag-Basuri/Tetranoodle-hackathon-project`.
4. Configure the Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click **Edit** and select `frontend`.
   - **Build and Output Settings**:
     - Build Command: `npm run build`
     - Output Directory: `dist`
     - Install Command: `npm install`
5. Expand **Environment Variables** and add:
   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://scholarpilot-api.onrender.com` |

   *(Replace with your actual Render backend URL without trailing slash)*

6. Click **Deploy**.
7. Vercel builds the bundle and deploys it with automatic SSL and CDN distribution.
8. Your frontend will be live at:
   `https://scholarpilot.vercel.app` (or your assigned Vercel project domain).

---

## Part 3: SPA Routing & CORS Verification

1. **SPA Routing**:
   The repository includes [frontend/vercel.json](file:///d:/projects/Tetranoodle%20hackathon%20project/frontend/vercel.json):
   ```json
   {
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```
   This ensures direct navigations or page refreshes on `/jobs/:id` or `/drafts/:id` load seamlessly without 404 errors.

2. **CORS Configuration**:
   The backend's CORS policy in [backend/app/main.py](file:///d:/projects/Tetranoodle%20hackathon%20project/backend/app/main.py) allows:
   - The explicit origin in `FRONTEND_ORIGIN`.
   - Any Vercel deployment matching the regex `https://.*\.vercel\.app` (supporting staging and preview deployments).
   - Local development origins (`http://localhost:5173`, `http://127.0.0.1:5173`).

---

## Part 4: End-to-End Sanity Checklist

After deploying both:

1. **Visit Frontend URL**: Open your Vercel deployment in your browser.
2. **Submit a Test Profile**:
   - Use the **Demo Profile 1 (CS/AI - Canada/Germany)** quick pre-fill button.
   - Click **Start Research Pipeline**.
3. **Monitor Live Pipeline**:
   - Confirm the 5-agent timeline tracks progress through Profiler, Discovery, Eligibility, Ranking, and Verification.
   - Verify that matched opportunities appear with verified quotes and capability links.
4. **Test Draft Statement Generation**:
   - Click **Draft Statement** on any matched opportunity.
   - Verify the drafted statement loads with inline citations and rubric breakdown.
5. **Test Refresh**:
   - Refresh the page while viewing `/jobs/<job-id>`.
   - Verify the report reloads with all stored data from Neon PostgreSQL.
