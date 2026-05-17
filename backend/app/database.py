# backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from loguru import logger
from backend.app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.env == "development",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # auto-reconnect on stale connections
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Enable pgvector extension and create all tables."""
    async with engine.begin() as conn:
        # Must enable pgvector BEFORE creating tables with VECTOR columns
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        from backend.app import models  # noqa: F401 — registers models
        await conn.run_sync(Base.metadata.create_all)
    logger.success("Database initialised with pgvector extension.")


async def close_db():
    await engine.dispose()


async def get_session():
    """FastAPI dependency for route handlers."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
