"""API tests for resource endpoints."""

from __future__ import annotations

from datetime import date

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_resource_creation_rejects_invalid_project(client: AsyncClient) -> None:
    """API should reject resource creation when referencing unknown project."""

    payload = {
        "name": "Edge Sensor",
        "category": "sensor",
        "lifecycle_state": "active",
        "serial_number": "SN-001",
        "procurement_date": date.today().isoformat(),
        "project_id": 9999,
    }
    response = await client.post("/api/v1/resources", json=payload)
    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "Project 9999" in body["detail"]
