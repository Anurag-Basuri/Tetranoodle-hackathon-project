from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # Database: Supports SQLite (aiosqlite) for lightweight local dev and PostgreSQL (asyncpg) for production/Render
    DATABASE_URL: str = "sqlite+aiosqlite:///./scholarpilot.db"

    # LLM Providers
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Search Providers
    TAVILY_API_KEY: str = ""
    BRAVE_API_KEY: str = ""

    # Optional GitHub Token for enrichment rate limits (60/hr -> 5000/hr)
    GITHUB_TOKEN: str = ""

    # Pipeline Budgets & Limits
    MIN_CANDIDATES: int = 12
    MAX_CANDIDATES: int = 18
    FETCH_CONCURRENCY: int = 3
    LLM_CONCURRENCY: int = 2
    MAX_LLM_CALLS_PER_JOB: int = 120
    JOB_TIMEOUT_S: int = 720
    AGENT_TIMEOUT_S: int = 90

    # Rate Limiting
    MAX_PROFILES_PER_HOUR: int = 20
    MAX_JOBS_PER_HOUR: int = 5
    MAX_DRAFTS_PER_HOUR: int = 10
    GLOBAL_MAX_RUNNING_JOBS: int = 2

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
