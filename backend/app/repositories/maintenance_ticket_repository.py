"""Repository for maintenance ticket entities."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import MaintenanceTicket
from .base import AsyncRepository


class MaintenanceTicketRepository(AsyncRepository[MaintenanceTicket]):
    """Persist and query maintenance ticket entities."""

    searchable_fields = (
        MaintenanceTicket.reported_by,
        MaintenanceTicket.issue_summary,
    )

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MaintenanceTicket)
