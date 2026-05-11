"""Pytest fixtures for the LifeLine-ICT backend."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Generator
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from geoalchemy2 import Geography, Geometry
from geoalchemy2.admin.dialects import sqlite as geoalchemy_sqlite
from geoalchemy2.admin.dialects.common import _check_spatial_type
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from ..app import create_app
from ..app.api.deps import get_current_user, get_db_session
from ..app.core.database import Base
from ..app.models.user import User


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    """Create an in-memory SQLite engine for tests."""

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def register_spatial_functions(dbapi_connection, connection_record) -> None:
        dbapi_connection.create_function("GeomFromEWKT", 1, lambda value: value)
        dbapi_connection.create_function("AsEWKB", 1, lambda value: value)

    return engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(test_engine: AsyncEngine) -> AsyncIterator[None]:
    """Create all tables before running tests."""

    after_create = geoalchemy_sqlite.after_create
    before_drop = geoalchemy_sqlite.before_drop
    after_drop = geoalchemy_sqlite.after_drop

    def after_create_without_spatialite(table, bind, **kw):
        table.columns = table.info.pop("_saved_columns")
        table.info.pop("_after_create_indexes", None)

        for col in table.columns:
            if _check_spatial_type(col.type, (Geometry, Geography), bind.dialect):
                col.type = col._actual_type
                del col._actual_type

    geoalchemy_sqlite.after_create = after_create_without_spatialite
    geoalchemy_sqlite.before_drop = lambda table, bind, **kw: None
    geoalchemy_sqlite.after_drop = lambda table, bind, **kw: None
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    finally:
        geoalchemy_sqlite.after_create = after_create
        geoalchemy_sqlite.before_drop = before_drop
        geoalchemy_sqlite.after_drop = after_drop


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

    async def get_test_user() -> User:
        return User(id=1, username="testuser", hashed_password="unused")

    app.dependency_overrides[get_db_session] = get_test_session
    app.dependency_overrides[get_current_user] = get_test_user
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTPX client bound to the FastAPI test app."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
