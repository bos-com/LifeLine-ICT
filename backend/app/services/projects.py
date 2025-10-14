"""Business logic for managing projects."""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    AuditAction,
    AuditEntityType,
    ICTResource,
    Project,
    User,
)
from ..repositories import ProjectRepository
from ..schemas import (
    PaginatedResponse,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from .base import BaseService
from .exceptions import ValidationError
from .audit_trail import AuditTrailRecorder

logger = logging.getLogger(__name__)


class ProjectService(BaseService):
    """Coordinate project-related workflows."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = ProjectRepository(session)
        self.audit_trail = AuditTrailRecorder(session, AuditEntityType.PROJECT)

    async def list_projects(
        self,
        *,
        limit: int,
        offset: int,
        search: Optional[str],
    ) -> PaginatedResponse[ProjectRead]:
        """
        Return a paginated list of projects.
        """

        items, total = await self.repository.list(
            limit=limit,
            offset=offset,
            search=search,
        )
        return self.build_paginated_response(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            schema=ProjectRead,
        )

    async def get_project(self, project_id: int) -> ProjectRead:
        """
        Retrieve a single project by ID.
        """

        project = self.ensure_entity(
            await self.repository.get(project_id),
            f"Project {project_id} not found.",
        )
        return ProjectRead.from_orm(project)

    async def create_project(
        self,
        payload: ProjectCreate,
        *,
        actor: Optional[User] = None,
    ) -> ProjectRead:
        """
        Create a new project.
        """

        data = payload.dict()
        project = await self.repository.create(data)
        logger.info("Created project %s", project.name)
        result = ProjectRead.from_orm(project)
        await self.audit_trail.record(
            action=AuditAction.CREATE,
            entity_id=project.id,
            entity_name=project.name,
            summary="Project created",
            actor=actor,
            context={"payload": data},
        )
        return result

    async def update_project(
        self,
        project_id: int,
        payload: ProjectUpdate,
        *,
        actor: Optional[User] = None,
    ) -> ProjectRead:
        """
        Update an existing project.
        """

        project = self.ensure_entity(
            await self.repository.get(project_id),
            f"Project {project_id} not found.",
        )
        changes = payload.dict(exclude_unset=True)
        updated = await self.repository.update(project, changes)
        logger.info("Updated project %s", project_id)
        result = ProjectRead.from_orm(updated)
        await self.audit_trail.record(
            action=AuditAction.UPDATE,
            entity_id=project.id,
            entity_name=project.name,
            summary="Project updated",
            actor=actor,
            context={"changes": changes},
        )
        return result

    async def delete_project(
        self,
        project_id: int,
        *,
        actor: Optional[User] = None,
    ) -> None:
        """
        Delete a project after verifying no unresolved dependencies exist.
        """

        project: Project = self.ensure_entity(
            await self.repository.get(project_id),
            f"Project {project_id} not found.",
        )

        resource_exists = await self.session.scalar(
            select(ICTResource.id)
            .where(ICTResource.project_id == project_id)
            .limit(1)
        )
        if resource_exists:
            raise ValidationError(
                "Cannot delete a project while resources remain attached."
            )

        await self.repository.delete(project)
        logger.info("Deleted project %s", project_id)
        await self.audit_trail.record(
            action=AuditAction.DELETE,
            entity_id=project.id,
            entity_name=project.name,
            summary="Project deleted",
            actor=actor,
            context=None,
            description="Project removed after dependency checks.",
        )
