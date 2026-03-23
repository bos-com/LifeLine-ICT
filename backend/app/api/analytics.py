"""Analytics API routes for metrics and reporting."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    tags=["analytics"],
)
async def get_dashboard_summary() -> dict[str, str]:
    """
    Provide a summary of key metrics for the dashboard.

    Returns
    -------
    dict[str, str]
        Summary statistics for projects, resources, and tickets.
    """

    return {"status": "dashboard_endpoint_placeholder"}
