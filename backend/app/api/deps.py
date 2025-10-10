"""
Dependency injection helpers for FastAPI routers.

The dependency functions construct service instances per request while reusing
the shared database session provided by `get_session`.
"""

from __future__ import annotations

from typing import AsyncIterator, Optional

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import get_session
from ..schemas import PaginationQuery
from ..services import (
    LocationService,
    MaintenanceTicketService,
    ProjectService,
    ResourceService,
    SensorSiteService,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Yield an async SQLAlchemy session for request handlers.
    """

    async for session in get_session():
        yield session


def get_pagination_params(
    limit: Optional[int] = Query(
        default=None,
        ge=1,
        le=settings.pagination_max_limit,
        description="Maximum number of items to return.",
    ),
    offset: Optional[int] = Query(
        default=None,
        ge=0,
        description="Starting index of the page.",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Case-insensitive search term.",
    ),
) -> PaginationQuery:
    """
    Parse pagination query parameters into a schema.
    """

    return PaginationQuery(limit=limit, offset=offset, search=search)


async def get_project_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncIterator[ProjectService]:
    """Provide a `ProjectService` instance per request."""

    yield ProjectService(session)


async def get_resource_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncIterator[ResourceService]:
    """Provide a `ResourceService` instance per request."""

    yield ResourceService(session)


async def get_location_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncIterator[LocationService]:
    """Provide a `LocationService` instance per request."""

    yield LocationService(session)


async def get_ticket_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncIterator[MaintenanceTicketService]:
    """Provide a `MaintenanceTicketService` instance per request."""

    yield MaintenanceTicketService(session)


async def get_sensor_site_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncIterator[SensorSiteService]:
    """Provide a `SensorSiteService` instance per request."""

    yield SensorSiteService(session)
