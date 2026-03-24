"""Pytest fixtures for the LifeLine-ICT backend."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Generator
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from ..app import create_app
from ..app.api.deps import get_db_session
from ..app.core.database import Base


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    """Create an in-memory SQLite engine for tests."""

    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(test_engine: AsyncEngine) -> AsyncIterator[None]:
    """Create all tables before running tests."""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Yield a database session backed by the test engine."""

    SessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def app(session: AsyncSession) -> AsyncIterator[FastAPI]:
    """Create a FastAPI app instance with test overrides."""

    app = create_app()

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_db_session] = get_test_session
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTPX client bound to the FastAPI test app."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
