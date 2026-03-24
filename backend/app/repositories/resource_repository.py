"""Repository for ICT resource entities."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ICTResource
from .base import AsyncRepository


class ResourceRepository(AsyncRepository[ICTResource]):
    """Persist and query ICT resource entities."""

    searchable_fields = (
        ICTResource.name,
        ICTResource.category,
        ICTResource.serial_number,
    )

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ICTResource)
