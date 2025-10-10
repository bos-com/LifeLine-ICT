"""Business logic for managing sensor sites."""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ICTResource, Location, Project, SensorSite
from ..repositories import SensorSiteRepository
from ..schemas import (
    PaginatedResponse,
    SensorSiteCreate,
    SensorSiteRead,
    SensorSiteUpdate,
)
from .base import BaseService
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class SensorSiteService(BaseService):
    """Coordinate sensor site workflows."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = SensorSiteRepository(session)

    async def list_sensor_sites(
        self,
        *,
        limit: int,
        offset: int,
        search: Optional[str],
    ) -> PaginatedResponse[SensorSiteRead]:
        """Return a paginated list of sensor sites."""

        items, total = await self.repository.list(
            limit=limit,
            offset=offset,
            search=search,
        )
        return self.build_paginated_response(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            schema=SensorSiteRead,
        )

    async def get_sensor_site(self, site_id: int) -> SensorSiteRead:
        """Retrieve a sensor site by ID."""

        site = self.ensure_entity(
            await self.repository.get(site_id),
            f"Sensor site {site_id} not found.",
        )
        return SensorSiteRead.from_orm(site)

    async def create_sensor_site(
        self,
        payload: SensorSiteCreate,
    ) -> SensorSiteRead:
        """Create a new sensor site."""

        await self._validate_relationships(
            resource_id=payload.resource_id,
            project_id=payload.project_id,
            location_id=payload.location_id,
        )
        site = await self.repository.create(payload.dict())
        logger.info("Created sensor site %s", site.id)
        return SensorSiteRead.from_orm(site)

    async def update_sensor_site(
        self,
        site_id: int,
        payload: SensorSiteUpdate,
    ) -> SensorSiteRead:
        """Update an existing sensor site."""

        site = self.ensure_entity(
            await self.repository.get(site_id),
            f"Sensor site {site_id} not found.",
        )

        data = payload.dict(exclude_unset=True)
        await self._validate_relationships(
            resource_id=site.resource_id,
            project_id=data.get("project_id", site.project_id),
            location_id=data.get("location_id", site.location_id),
        )

        updated = await self.repository.update(site, data)
        logger.info("Updated sensor site %s", site_id)
        return SensorSiteRead.from_orm(updated)

    async def delete_sensor_site(self, site_id: int) -> None:
        """Delete a sensor site."""

        site: SensorSite = self.ensure_entity(
            await self.repository.get(site_id),
            f"Sensor site {site_id} not found.",
        )
        await self.repository.delete(site)
        logger.info("Deleted sensor site %s", site_id)

    async def _validate_relationships(
        self,
        *,
        resource_id: int,
        project_id: Optional[int],
        location_id: Optional[int],
    ) -> None:
        """Ensure referenced entities exist prior to persistence."""

        resource_exists = await self.session.scalar(
            select(ICTResource.id).where(ICTResource.id == resource_id)
        )
        if not resource_exists:
            raise ValidationError(f"ICT resource {resource_id} does not exist.")

        if project_id is not None:
            project_exists = await self.session.scalar(
                select(Project.id).where(Project.id == project_id)
            )
            if not project_exists:
                raise ValidationError(f"Project {project_id} does not exist.")

        if location_id is not None:
            location_exists = await self.session.scalar(
                select(Location.id).where(Location.id == location_id)
            )
            if not location_exists:
                raise ValidationError(
                    f"Location {location_id} does not exist."
                )
