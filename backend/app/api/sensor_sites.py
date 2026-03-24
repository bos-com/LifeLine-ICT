"""Sensor site API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from ..core.config import settings
from ..schemas import (
    PaginatedResponse,
    PaginationQuery,
    SensorSiteCreate,
    SensorSiteRead,
    SensorSiteUpdate,
)
from ..services import SensorSiteService
from .deps import get_pagination_params, get_sensor_site_service

from ..models.user import User
from .deps import get_current_user

router = APIRouter(
    prefix="/api/v1/sensor-sites",
    tags=["Sensor Sites"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "",
    response_model=PaginatedResponse[SensorSiteRead],
    status_code=status.HTTP_200_OK,
)
async def list_sensor_sites(
    pagination: PaginationQuery = Depends(get_pagination_params),
    service: SensorSiteService = Depends(get_sensor_site_service),
) -> PaginatedResponse[SensorSiteRead]:
    """
    List sensor sites with optional search and pagination.
    """

    limit = pagination.limit or settings.pagination_default_limit
    offset = pagination.offset or 0
    return await service.list_sensor_sites(
        limit=limit,
        offset=offset,
        search=pagination.search,
    )


@router.get(
    "/{site_id}",
    response_model=SensorSiteRead,
    status_code=status.HTTP_200_OK,
)
async def get_sensor_site(
    site_id: int,
    service: SensorSiteService = Depends(get_sensor_site_service),
) -> SensorSiteRead:
    """
    Retrieve a sensor site by its identifier.
    """

    return await service.get_sensor_site(site_id)


@router.post(
    "",
    response_model=SensorSiteRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_sensor_site(
    payload: SensorSiteCreate,
    service: SensorSiteService = Depends(get_sensor_site_service),
) -> SensorSiteRead:
    """
    Create a new sensor site record.
    """

    return await service.create_sensor_site(payload)


@router.put(
    "/{site_id}",
    response_model=SensorSiteRead,
    status_code=status.HTTP_200_OK,
)
async def update_sensor_site(
    site_id: int,
    payload: SensorSiteCreate,
    service: SensorSiteService = Depends(get_sensor_site_service),
) -> SensorSiteRead:
    """
    Replace an existing sensor site.
    """

    return await service.update_sensor_site(
        site_id,
        SensorSiteUpdate(**payload.dict()),
    )


@router.patch(
    "/{site_id}",
    response_model=SensorSiteRead,
    status_code=status.HTTP_200_OK,
)
async def partial_update_sensor_site(
    site_id: int,
    payload: SensorSiteUpdate,
    service: SensorSiteService = Depends(get_sensor_site_service),
) -> SensorSiteRead:
    """
    Apply a partial update to an existing sensor site.
    """

    return await service.update_sensor_site(site_id, payload)


@router.delete(
    "/{site_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_sensor_site(
    site_id: int,
    service: SensorSiteService = Depends(get_sensor_site_service),
) -> Response:
    """
    Delete a sensor site from the registry.
    """

    await service.delete_sensor_site(site_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
