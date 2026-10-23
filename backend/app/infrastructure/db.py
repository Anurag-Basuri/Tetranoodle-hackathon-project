from typing import AsyncGenerator, Tuple, Dict, Any
from urllib.parse import urlparse, parse_qs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from app.config import get_settings


class Base(DeclarativeBase):
    pass


def normalize_database_url(raw_url: str) -> Tuple[str, Dict[str, Any]]:
    connect_args: Dict[str, Any] = {}
    
    if raw_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        return raw_url, connect_args

    url = raw_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if "asyncpg" in url:
        # asyncpg requires statement_cache_size=0 for pgBouncer and Neon transaction poolers
        connect_args["statement_cache_size"] = 0
        # asyncpg does not accept sslmode query parameter; pass ssl=require via connect_args
        if "?" in url:
            base_url, query_str = url.split("?", 1)
            parsed_query = parse_qs(query_str)
            if "sslmode" in parsed_query or "ssl" in parsed_query:
                connect_args["ssl"] = "require"
            url = base_url
        else:
            connect_args["ssl"] = "require"

    return url, connect_args


settings = get_settings()
db_url, connect_args = normalize_database_url(settings.DATABASE_URL)

engine = create_async_engine(
    db_url,
    echo=settings.ENV == "dev" and settings.LOG_LEVEL == "DEBUG",
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Enable foreign keys for SQLite if SQLite is used
if db_url.startswith("sqlite"):
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    import app.infrastructure.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
