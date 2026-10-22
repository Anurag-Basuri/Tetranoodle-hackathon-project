from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.infrastructure.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables if not exist
    await init_db()
    yield
    # Shutdown


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ScholarPilot AI API",
        description="Evidence-backed scholarship and university research by a team of cooperating agents.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
