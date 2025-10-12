"""Project API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from ..core.config import settings
from ..schemas import (
    PaginatedResponse,
    PaginationQuery,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from ..services import ProjectService
from .deps import get_pagination_params, get_project_service

from ..models.user import User
from .deps import get_current_user

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectRead],
    status_code=status.HTTP_200_OK,
)
async def list_projects(
    pagination: PaginationQuery = Depends(get_pagination_params),
    service: ProjectService = Depends(get_project_service),
) -> PaginatedResponse[ProjectRead]:
    """
    List projects with optional search and pagination.
    """

    limit = pagination.limit or settings.pagination_default_limit
    offset = pagination.offset or 0
    return await service.list_projects(
        limit=limit,
        offset=offset,
        search=pagination.search,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """
    Retrieve a single project by its identifier.
    """

    return await service.get_project(project_id)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    """
    Create a new project record.
    """

    return await service.create_project(payload, actor=current_user)


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: int,
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    """
    Replace an existing project using a full payload.
    """

    return await service.update_project(
        project_id,
        ProjectUpdate(**payload.dict()),
        actor=current_user,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
)
async def partial_update_project(
    project_id: int,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    """
    Apply a partial update to an existing project.
    """

    return await service.update_project(
        project_id,
        payload,
        actor=current_user,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Delete a project once dependencies have been cleared.
    """

    await service.delete_project(project_id, actor=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
