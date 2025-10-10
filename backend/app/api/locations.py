"""Location API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from ..core.config import settings
from ..schemas import (
    LocationCreate,
    LocationRead,
    LocationUpdate,
    PaginatedResponse,
    PaginationQuery,
)
from ..services import LocationService
from .deps import get_location_service, get_pagination_params

router = APIRouter(prefix="/api/v1/locations", tags=["Locations"])


@router.get(
    "",
    response_model=PaginatedResponse[LocationRead],
    status_code=status.HTTP_200_OK,
)
async def list_locations(
    pagination: PaginationQuery = Depends(get_pagination_params),
    service: LocationService = Depends(get_location_service),
) -> PaginatedResponse[LocationRead]:
    """
    List locations with optional search and pagination.
    """

    limit = pagination.limit or settings.pagination_default_limit
    offset = pagination.offset or 0
    return await service.list_locations(
        limit=limit,
        offset=offset,
        search=pagination.search,
    )


@router.get(
    "/{location_id}",
    response_model=LocationRead,
    status_code=status.HTTP_200_OK,
)
async def get_location(
    location_id: int,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    """
    Retrieve a location by its identifier.
    """

    return await service.get_location(location_id)


@router.post(
    "",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_location(
    payload: LocationCreate,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    """
    Create a new location.
    """

    return await service.create_location(payload)


@router.put(
    "/{location_id}",
    response_model=LocationRead,
    status_code=status.HTTP_200_OK,
)
async def update_location(
    location_id: int,
    payload: LocationCreate,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    """
    Replace an existing location.
    """

    return await service.update_location(location_id, LocationUpdate(**payload.dict()))


@router.patch(
    "/{location_id}",
    response_model=LocationRead,
    status_code=status.HTTP_200_OK,
)
async def partial_update_location(
    location_id: int,
    payload: LocationUpdate,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    """
    Apply a partial update to an existing location.
    """

    return await service.update_location(location_id, payload)


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_location(
    location_id: int,
    service: LocationService = Depends(get_location_service),
) -> Response:
    """
    Delete a location once dependent resources have been removed.
    """

    await service.delete_location(location_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
