"""Tests for the audit log service layer."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from ...app.models import AuditAction, AuditEntityType
from ...app.schemas import AuditLogCreate, AuditLogQuery
from ...app.services import AuditLogService
from ...app.models.audit_log import AuditLog


@pytest.mark.asyncio
async def test_record_event_persists_log(session) -> None:
    """Ensure audit events are persisted and serialised correctly."""

    service = AuditLogService(session)
    payload = AuditLogCreate(
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.PROJECT,
        entity_id="42",
        entity_name="Network Expansion",
        summary="Project created for campus network expansion",
        context={"payload": {"name": "Network Expansion"}},
    )

    result = await service.record_event(payload)

    assert result.id is not None
    assert result.action == AuditAction.CREATE
    stored = await session.get(AuditLog, result.id)
    assert stored is not None
    assert stored.summary == payload.summary


@pytest.mark.asyncio
async def test_list_logs_supports_filters(session) -> None:
    """Verify list endpoint supports filters for action and date range."""

    service = AuditLogService(session)

    await service.record_event(
        AuditLogCreate(
            action=AuditAction.CREATE,
            entity_type=AuditEntityType.RESOURCE,
            entity_id="1",
            entity_name="Core Switch",
            summary="Resource created",
        )
    )
    await service.record_event(
        AuditLogCreate(
            action=AuditAction.DELETE,
            entity_type=AuditEntityType.RESOURCE,
            entity_id="2",
            entity_name="Old Switch",
            summary="Resource deleted",
        )
    )

    query = AuditLogQuery(
        limit=10,
        offset=0,
        action=AuditAction.DELETE,
        date_from=datetime.utcnow() - timedelta(days=1),
        date_to=datetime.utcnow() + timedelta(days=1),
    )
    response = await service.list_logs(query)

    assert response.pagination.total == 1
    assert len(response.data) == 1
    assert response.data[0].action == AuditAction.DELETE
