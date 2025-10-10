"""Analytics API routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get(
    "/health",
    tags=["health"],
)
async def healthcheck() -> dict[str, str]:
    """
    Provide a basic health indicator confirming application availability.

    Returns
    -------
    dict[str, str]
        JSON payload with a static status. The endpoint is intentionally
        lightweight to support campus monitoring systems and classroom
        demonstrations.
    """

    return {"status": "ok"}
