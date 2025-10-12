"""Business logic for managing maintenance tickets."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    AuditAction,
    AuditEntityType,
    ICTResource,
    MaintenanceTicket,
    TicketStatus,
    User,
)
from ..repositories import MaintenanceTicketRepository
from ..schemas import (
    PaginatedResponse,
    TicketCreate,
    TicketRead,
    TicketUpdate,
)
from .base import BaseService
from .exceptions import ValidationError
from .audit_trail import AuditTrailRecorder

logger = logging.getLogger(__name__)


class MaintenanceTicketService(BaseService):
    """Coordinate maintenance ticket workflows."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = MaintenanceTicketRepository(session)
        self.audit_trail = AuditTrailRecorder(session, AuditEntityType.MAINTENANCE_TICKET)

    async def list_tickets(
        self,
        *,
        limit: int,
        offset: int,
        search: Optional[str],
    ) -> PaginatedResponse[TicketRead]:
        """Return a paginated list of maintenance tickets."""

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
            schema=TicketRead,
        )

    async def get_ticket(self, ticket_id: int) -> TicketRead:
        """Retrieve a ticket by ID."""

        ticket = self.ensure_entity(
            await self.repository.get(ticket_id),
            f"Maintenance ticket {ticket_id} not found.",
        )
        return TicketRead.from_orm(ticket)

    async def create_ticket(
        self,
        payload: TicketCreate,
        *,
        actor: Optional[User] = None,
    ) -> TicketRead:
        """Create a new maintenance ticket."""

        await self._validate_resource(payload.resource_id)
        self._validate_resolution_fields(
            status=payload.status,
            notes=payload.notes,
            closed_at=payload.closed_at,
        )

        data = payload.dict()
        ticket = await self.repository.create(data)
        logger.info("Created maintenance ticket %s", ticket.id)
        result = TicketRead.from_orm(ticket)
        await self.audit_trail.record(
            action=AuditAction.CREATE,
            entity_id=ticket.id,
            entity_name=f"Ticket {ticket.id}",
            summary="Maintenance ticket created",
            actor=actor,
            context={"payload": data},
        )
        return result

    async def update_ticket(
        self,
        ticket_id: int,
        payload: TicketUpdate,
        *,
        actor: Optional[User] = None,
    ) -> TicketRead:
        """Update an existing maintenance ticket."""

        ticket = self.ensure_entity(
            await self.repository.get(ticket_id),
            f"Maintenance ticket {ticket_id} not found.",
        )

        data = payload.dict(exclude_unset=True)
        if "resource_id" in data:
            await self._validate_resource(data["resource_id"])

        status = data.get("status", ticket.status)
        notes = data.get("notes", ticket.notes)
        closed_at = data.get("closed_at", ticket.closed_at)
        self._validate_resolution_fields(
            status=status,
            notes=notes,
            closed_at=closed_at,
        )

        updated = await self.repository.update(ticket, data)
        logger.info("Updated maintenance ticket %s", ticket_id)
        result = TicketRead.from_orm(updated)
        await self.audit_trail.record(
            action=AuditAction.UPDATE,
            entity_id=ticket.id,
            entity_name=f"Ticket {ticket.id}",
            summary="Maintenance ticket updated",
            actor=actor,
            context={"changes": data},
        )
        return result

    async def delete_ticket(
        self,
        ticket_id: int,
        *,
        actor: Optional[User] = None,
    ) -> None:
        """Delete a maintenance ticket."""

        ticket: MaintenanceTicket = self.ensure_entity(
            await self.repository.get(ticket_id),
            f"Maintenance ticket {ticket_id} not found.",
        )
        await self.repository.delete(ticket)
        logger.info("Deleted maintenance ticket %s", ticket_id)
        await self.audit_trail.record(
            action=AuditAction.DELETE,
            entity_id=ticket.id,
            entity_name=f"Ticket {ticket.id}",
            summary="Maintenance ticket deleted",
            actor=actor,
            description="Ticket removed from the system.",
        )

    async def _validate_resource(self, resource_id: int) -> None:
        """Ensure the referenced resource exists."""

        exists = await self.session.scalar(
            select(ICTResource.id).where(ICTResource.id == resource_id)
        )
        if not exists:
            raise ValidationError(f"ICT resource {resource_id} does not exist.")

    @staticmethod
    def _validate_resolution_fields(
        *,
        status: TicketStatus,
        notes: Optional[str],
        closed_at: Optional[datetime],
    ) -> None:
        """Ensure closure metadata is present when required."""

        if status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            if closed_at is None:
                raise ValidationError(
                    "Resolved or closed tickets must include a closed_at timestamp."
                )
            if not notes:
                raise ValidationError(
                    "Resolved or closed tickets must provide resolution notes."
                )
