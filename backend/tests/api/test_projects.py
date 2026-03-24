"""API tests for project endpoints."""

from __future__ import annotations

from datetime import date

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_retrieve_project(client: AsyncClient) -> None:
    """Ensure project creation and retrieval endpoints function correctly."""

    payload = {
        "name": "Campus Network Upgrade",
        "description": "Upgrade backbone links for the main campus.",
        "status": "planned",
        "sponsor": "ICT Directorate",
        "start_date": date.today().isoformat(),
        "primary_contact_email": "ict-directorate@example.edu",
    }

    response = await client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    project = response.json()
    assert project["name"] == payload["name"]
    project_id = project["id"]

    get_response = await client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == project_id
    assert fetched["primary_contact_email"] == payload["primary_contact_email"]


@pytest.mark.asyncio
async def test_list_projects_with_pagination(client: AsyncClient) -> None:
    """Ensure pagination metadata is returned."""

    response = await client.get("/api/v1/projects?limit=5&offset=0")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body
    assert body["pagination"]["limit"] == 5
