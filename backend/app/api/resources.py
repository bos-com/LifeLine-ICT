"""ICT resource API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from ..core.config import settings
from ..schemas import (
    PaginatedResponse,
    PaginationQuery,
    ResourceCreate,
    ResourceRead,
    ResourceUpdate,
)
from ..services import ResourceService
from .deps import get_pagination_params, get_resource_service

router = APIRouter(prefix="/api/v1/resources", tags=["ICT Resources"])


@router.get(
    "",
    response_model=PaginatedResponse[ResourceRead],
    status_code=status.HTTP_200_OK,
)
async def list_resources(
    pagination: PaginationQuery = Depends(get_pagination_params),
    service: ResourceService = Depends(get_resource_service),
) -> PaginatedResponse[ResourceRead]:
    """
    List ICT resources with optional search and pagination.
    """

    limit = pagination.limit or settings.pagination_default_limit
    offset = pagination.offset or 0
    return await service.list_resources(
        limit=limit,
        offset=offset,
        search=pagination.search,
    )


@router.get(
    "/{resource_id}",
    response_model=ResourceRead,
    status_code=status.HTTP_200_OK,
)
async def get_resource(
    resource_id: int,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceRead:
    """
    Retrieve a single resource by its identifier.
    """

    return await service.get_resource(resource_id)


@router.post(
    "",
    response_model=ResourceRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_resource(
    payload: ResourceCreate,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceRead:
    """
    Create a new ICT resource.
    """

    return await service.create_resource(payload)


@router.put(
    "/{resource_id}",
    response_model=ResourceRead,
    status_code=status.HTTP_200_OK,
)
async def update_resource(
    resource_id: int,
    payload: ResourceCreate,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceRead:
    """
    Replace an existing ICT resource.
    """

    return await service.update_resource(
        resource_id,
        ResourceUpdate(**payload.dict()),
    )


@router.patch(
    "/{resource_id}",
    response_model=ResourceRead,
    status_code=status.HTTP_200_OK,
)
async def partial_update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceRead:
    """
    Apply a partial update to an existing ICT resource.
    """

    return await service.update_resource(resource_id, payload)


@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_resource(
    resource_id: int,
    service: ResourceService = Depends(get_resource_service),
) -> Response:
    """
    Delete a resource once unresolved tickets have been cleared.
    """

    await service.delete_resource(resource_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
