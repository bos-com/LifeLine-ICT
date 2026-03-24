"""Repository for location entities."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Location
from .base import AsyncRepository


class LocationRepository(AsyncRepository[Location]):
    """Persist and query location entities."""

    searchable_fields = (Location.campus, Location.building, Location.room)

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Location)
