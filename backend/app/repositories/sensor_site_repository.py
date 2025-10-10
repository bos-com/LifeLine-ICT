"""Repository for sensor site entities."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SensorSite
from .base import AsyncRepository


class SensorSiteRepository(AsyncRepository[SensorSite]):
    """Persist and query sensor site entities."""

    searchable_fields = (SensorSite.data_collection_endpoint,)

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SensorSite)
