"""Service-layer tests for ICT resources."""

from __future__ import annotations

from datetime import datetime

import pytest

from ...app.schemas import (
    LocationCreate,
    ProjectCreate,
    ResourceCreate,
    TicketCreate,
    TicketUpdate,
)
from ...app.services import (
    LocationService,
    MaintenanceTicketService,
    ProjectService,
    ResourceService,
    ValidationError,
)
from ...app.models import LifecycleState, TicketSeverity, TicketStatus
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_resource_deletion_requires_closed_tickets(session: AsyncSession) -> None:
    """Ensure resources with unresolved tickets cannot be deleted."""

    project_service = ProjectService(session)
    location_service = LocationService(session)
    resource_service = ResourceService(session)
    ticket_service = MaintenanceTicketService(session)

    project = await project_service.create_project(
        ProjectCreate(
            name="Data Centre Upgrade",
            description="Modernise servers and UPS units.",
            primary_contact_email="ops@example.edu",
        )
    )
    location = await location_service.create_location(
        LocationCreate(
            campus="Main Campus",
            building="ICT Block",
            room="Server Room",
        )
    )
    resource = await resource_service.create_resource(
        ResourceCreate(
            name="Core Switch",
            category="network",
            lifecycle_state=LifecycleState.ACTIVE,
            project_id=project.id,
            location_id=location.id,
        )
    )

    ticket = await ticket_service.create_ticket(
        TicketCreate(
            resource_id=resource.id,
            reported_by="technician@example.edu",
            issue_summary="Intermittent port failures",
            severity=TicketSeverity.HIGH,
            status=TicketStatus.OPEN,
            opened_at=datetime.utcnow(),
        )
    )

    with pytest.raises(ValidationError):
        await resource_service.delete_resource(resource.id)

    await ticket_service.update_ticket(
        ticket.id,
        TicketUpdate(
            status=TicketStatus.CLOSED,
            notes="Replaced faulty module.",
            closed_at=datetime.utcnow(),
        ),
    )

    await resource_service.delete_resource(resource.id)
