"""Business logic for managing locations."""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shapely.geometry import Point
from geoalchemy2.shape import from_shape

from ..models import ICTResource, Location, SensorSite
from ..repositories import LocationRepository
from ..schemas import (
    LocationCreate,
    LocationRead,
    LocationUpdate,
    PaginatedResponse,
)
from .base import BaseService
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class LocationService(BaseService):
    """Coordinate location-related workflows."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = LocationRepository(session)

    async def list_locations(
        self,
        *,
        limit: int,
        offset: int,
        search: Optional[str],
    ) -> PaginatedResponse[LocationRead]:
        """Return a paginated list of locations."""

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
            schema=LocationRead,
        )

    async def get_location(self, location_id: int) -> LocationRead:
        """Retrieve a location by ID."""

        location = self.ensure_entity(
            await self.repository.get(location_id),
            f"Location {location_id} not found.",
        )
        return LocationRead.from_orm(location)

    async def create_location(self, payload: LocationCreate) -> LocationRead:
        """Create a new location."""

        data = payload.dict()
        if geom := data.pop("geom", None):
            point = Point(geom["lon"], geom["lat"])
            data["geom"] = from_shape(point, srid=4326)

        location = await self.repository.create(data)
        logger.info("Created location %s - %s", location.campus, location.building)
        return LocationRead.from_orm(location)

    async def update_location(
        self,
        location_id: int,
        payload: LocationUpdate,
    ) -> LocationRead:
        """Update an existing location."""

        location = self.ensure_entity(
            await self.repository.get(location_id),
            f"Location {location_id} not found.",
        )

        data = payload.dict(exclude_unset=True)
        if geom := data.pop("geom", None):
            point = Point(geom["lon"], geom["lat"])
            data["geom"] = from_shape(point, srid=4326)

        updated = await self.repository.update(
            location,
            data,
        )
        logger.info("Updated location %s", location_id)
        return LocationRead.from_orm(updated)

    async def delete_location(self, location_id: int) -> None:
        """Delete a location when no dependent records exist."""

        location: Location = self.ensure_entity(
            await self.repository.get(location_id),
            f"Location {location_id} not found.",
        )

        blocking_resource = await self.session.scalar(
            select(ICTResource.id)
            .where(ICTResource.location_id == location_id)
            .limit(1)
        )
        blocking_site = await self.session.scalar(
            select(SensorSite.id)
            .where(SensorSite.location_id == location_id)
            .limit(1)
        )
        if blocking_resource or blocking_site:
            raise ValidationError(
                "Cannot delete a location while resources or sensor sites are attached."
            )

        await self.repository.delete(location)
        logger.info("Deleted location %s", location_id)
