"""
AI Support Platform Database - Async SQLAlchemy engine, session factory, and Base model.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings


# Async engine for FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

_sync_engine = None

def get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        try:
            _sync_engine = create_engine(
                settings.DATABASE_URL_SYNC,
                echo=settings.DEBUG,
                pool_size=5,
            )
        except Exception as e:
            print(f"Sync engine initialization deferred: {e}")
    return _sync_engine


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables on startup if database is available."""
    try:
        async with async_engine.begin() as conn:
            # Create pgvector extension
            await conn.execute(
                __import__("sqlalchemy").text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            )
            await conn.execute(
                __import__("sqlalchemy").text('CREATE EXTENSION IF NOT EXISTS "vector"')
            )
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"[WARN] PostgreSQL connection skipped (Operating in standalone demo mode): {e}")
