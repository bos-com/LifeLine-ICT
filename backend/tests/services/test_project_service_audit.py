"""Tests verifying project service audit logging integration."""

from __future__ import annotations

import pytest

from sqlalchemy import select

from ...app.models import AuditAction, AuditEntityType, AuditLog
from ...app.schemas import ProjectCreate
from ...app.services import ProjectService


@pytest.mark.asyncio
async def test_create_project_records_audit_entry(session) -> None:
    """Creating a project should emit an audit log entry."""

    service = ProjectService(session)
    payload = ProjectCreate(
        name="Campus Fibre Rollout",
        description="Deploy fibre backbone across campuses.",
        primary_contact_email="ict@example.edu",
    )

    project = await service.create_project(payload)

    assert project.id is not None
    logs = await session.execute(
        select(AuditLog).where(AuditLog.entity_id == str(project.id))
    )
    entries = logs.scalars().all()
    assert entries, "Expected audit log entry to be created."
    assert entries[0].action == AuditAction.CREATE
    assert entries[0].entity_type == AuditEntityType.PROJECT
