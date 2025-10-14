"""API tests for audit log endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_audit_logs(client: AsyncClient) -> None:
    """Ensure audit log endpoints allow creation and retrieval."""

    payload = {
        "action": "create",
        "entity_type": "project",
        "entity_id": "101",
        "entity_name": "Library WiFi Upgrade",
        "summary": "Project record created",
        "context": {"sponsor": "Library Board"},
    }

    create_response = await client.post("/api/v1/audit-logs", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["summary"] == payload["summary"]
    log_id = created["id"]

    list_response = await client.get("/api/v1/audit-logs")
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["pagination"]["total"] >= 1
    assert any(item["id"] == log_id for item in body["data"])

    detail_response = await client.get(f"/api/v1/audit-logs/{log_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == log_id
    assert detail["entity_type"] == payload["entity_type"]
