"""Tests for the health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check_returns_ok(client: TestClient) -> None:
    """Health endpoint should return status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirects_to_docs(client: TestClient) -> None:
    """Root URL should redirect to API documentation."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"
