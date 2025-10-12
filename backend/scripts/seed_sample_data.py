"""
Seed sample data for the LifeLine-ICT backend.

Running this script is optional but helps lecturers and demonstration teams
bootstrap the API with realistic records that showcase projects, resources,
sensor sites, and maintenance tickets.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..app.core.config import settings
from ..app.core.database import Base
from ..app.models import (
    ICTResource,
    LifecycleState,
    Location,
    MaintenanceTicket,
    Project,
    ProjectStatus,
    SensorSite,
    TicketSeverity,
    TicketStatus,
)


async def seed() -> None:
    """Populate the database with illustrative entities."""

    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        await session.execute(delete(MaintenanceTicket))
        await session.execute(delete(SensorSite))
        await session.execute(delete(ICTResource))
        await session.execute(delete(Location))
        await session.execute(delete(Project))
        await session.commit()

        project = Project(
            name="Smart Campus Connectivity",
            description="Deploy resilient Wi-Fi and wired networks across all faculties.",
            status=ProjectStatus.IN_PROGRESS,
            sponsor="ICT Directorate",
            primary_contact_email=settings.contact_email,
        )

        location = Location(
            campus="Kampala Main",
            building="Innovation Hub",
            room="Lab 3",
            latitude=0.3476,
            longitude=32.5825,
        )

        resource = ICTResource(
            name="Main Core Switch",
            category="network",
            lifecycle_state=LifecycleState.ACTIVE,
            serial_number="SW-UG-001",
            description="Handles backbone aggregation for the central campus.",
            project=project,
            location=location,
        )

        sensor_site = SensorSite(
            resource=resource,
            project=project,
            location=location,
            data_collection_endpoint="http://127.0.0.1:5000/data",
            notes="Feeds rainfall telemetry into analytics modules.",
        )

        ticket = MaintenanceTicket(
            resource=resource,
            reported_by="noc@lifeline.example.edu",
            issue_summary="Observed intermittent packet loss during peak hours.",
            severity=TicketSeverity.MEDIUM,
            status=TicketStatus.IN_PROGRESS,
            opened_at=datetime.utcnow(),
            notes="Monitoring in progress by network operations.",
        )

        session.add_all([project, location, resource, sensor_site, ticket])
        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
