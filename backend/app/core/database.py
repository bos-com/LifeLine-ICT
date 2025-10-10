"""
Database session management utilities.

The backend uses SQLAlchemy's async engine to keep the event loop responsive
when handling concurrent requests. Sessions are supplied through a dependency
that automatically commits transactions for successful operations and rolls
back any errors, ensuring the integrity of institutional data.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    pass


engine: AsyncEngine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """
    Provide a transactional scope around a series of operations.

    Yields
    ------
    AsyncSession
        Database session bound to the configured engine.
    """

    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:  # pragma: no cover - safeguard path
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_session() -> AsyncIterator[AsyncSession]:
    """
    FastAPI dependency wrapper that yields an async session.

    This helper allows routers and services to access the database through
    dependency injection without duplicating session management code.
    """

    async with session_scope() as session:
        yield session
