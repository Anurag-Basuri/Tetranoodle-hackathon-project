from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import get_settings
from app.infrastructure.db import init_db
from app.domain.errors import DomainError
from app.api.errors import domain_error_handler, validation_error_handler
from app.api.routers import profiles, documents, research_jobs, drafts

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on server startup
    await init_db()
    # Checkpoint recovery: scan for interrupted jobs after server restarts and resume them
    try:
        from app.application.recover_jobs import recover_stale_jobs_on_startup
        await recover_stale_jobs_on_startup()
    except Exception:
        pass
    yield

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ScholarPilot AI API",
        description="Evidence-backed scholarship and university research by a team of cooperating agents.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS for local dev, custom production domains, and Vercel deployments
    allowed_origins = [o.strip() for o in settings.FRONTEND_ORIGIN.split(",") if o.strip()]
    for local_origin in ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]:
        if local_origin not in allowed_origins:
            allowed_origins.append(local_origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register central error handlers for domain and validation exceptions
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    # Mount v1 API routers
    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(profiles.router)
    v1_router.include_router(documents.router)
    v1_router.include_router(research_jobs.router)
    v1_router.include_router(drafts.router)
    app.include_router(v1_router)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "ok",
            "version": "1.0.0",
            "env": settings.ENV,
        }

    @app.get("/health/providers", tags=["Health"])
    async def health_providers():
        return {
            "gemini": {
                "configured": bool(settings.GEMINI_API_KEY),
                "model": settings.GEMINI_MODEL,
                "status": "ready" if settings.GEMINI_API_KEY else "unconfigured",
            },
            "groq": {
                "configured": bool(settings.GROQ_API_KEY),
                "model": settings.GROQ_MODEL,
                "status": "ready" if settings.GROQ_API_KEY else "unconfigured",
            },
            "tavily": {
                "configured": bool(settings.TAVILY_API_KEY),
                "status": "ready" if settings.TAVILY_API_KEY else "unconfigured",
            },
            "brave": {
                "configured": bool(settings.BRAVE_API_KEY),
                "status": "ready" if settings.BRAVE_API_KEY else "unconfigured (optional fallback)",
            },
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
