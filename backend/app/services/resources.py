"""Business logic for managing ICT resources."""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    AuditAction,
    AuditEntityType,
    ICTResource,
    Location,
    MaintenanceTicket,
    Project,
    TicketStatus,
    User,
)
from ..repositories import ResourceRepository
from ..schemas import (
    PaginatedResponse,
    ResourceCreate,
    ResourceRead,
    ResourceUpdate,
)
from .base import BaseService
from .exceptions import ValidationError
from .audit_trail import AuditTrailRecorder

logger = logging.getLogger(__name__)


class ResourceService(BaseService):
    """Coordinate ICT resource workflows."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = ResourceRepository(session)
        self.audit_trail = AuditTrailRecorder(session, AuditEntityType.RESOURCE)

    async def list_resources(
        self,
        *,
        limit: int,
        offset: int,
        search: Optional[str],
    ) -> PaginatedResponse[ResourceRead]:
        """Return a paginated list of resources."""

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
            schema=ResourceRead,
        )

    async def get_resource(self, resource_id: int) -> ResourceRead:
        """Retrieve a single resource."""

        resource = self.ensure_entity(
            await self.repository.get(resource_id),
            f"ICT resource {resource_id} not found.",
        )
        return ResourceRead.from_orm(resource)

    async def create_resource(
        self,
        payload: ResourceCreate,
        *,
        actor: Optional[User] = None,
    ) -> ResourceRead:
        """Create a new resource after validating foreign keys."""

        await self._validate_relationships(
            project_id=payload.project_id,
            location_id=payload.location_id,
        )
        data = payload.dict()
        resource = await self.repository.create(data)
        logger.info("Created resource %s", resource.name)
        result = ResourceRead.from_orm(resource)
        await self.audit_trail.record(
            action=AuditAction.CREATE,
            entity_id=resource.id,
            entity_name=resource.name,
            summary="Resource created",
            actor=actor,
            context={"payload": data},
        )
        return result

    async def update_resource(
        self,
        resource_id: int,
        payload: ResourceUpdate,
        *,
        actor: Optional[User] = None,
    ) -> ResourceRead:
        """Update an existing resource."""

        resource = self.ensure_entity(
            await self.repository.get(resource_id),
            f"ICT resource {resource_id} not found.",
        )

        data = payload.dict(exclude_unset=True)
        await self._validate_relationships(
            project_id=data.get("project_id"),
            location_id=data.get("location_id"),
        )

        updated = await self.repository.update(resource, data)
        logger.info("Updated resource %s", resource_id)
        result = ResourceRead.from_orm(updated)
        await self.audit_trail.record(
            action=AuditAction.UPDATE,
            entity_id=resource.id,
            entity_name=resource.name,
            summary="Resource updated",
            actor=actor,
            context={"changes": data},
        )
        return result

    async def delete_resource(
        self,
        resource_id: int,
        *,
        actor: Optional[User] = None,
    ) -> None:
        """Delete a resource when no active maintenance tickets exist."""

        resource: ICTResource = self.ensure_entity(
            await self.repository.get(resource_id),
            f"ICT resource {resource_id} not found.",
        )

        unresolved_ticket = await self.session.scalar(
            select(MaintenanceTicket.id)
            .where(
                MaintenanceTicket.resource_id == resource_id,
                MaintenanceTicket.status != TicketStatus.CLOSED,
            )
            .limit(1)
        )
        if unresolved_ticket:
            raise ValidationError(
                "Cannot delete a resource with unresolved maintenance tickets."
            )

        await self.repository.delete(resource)
        logger.info("Deleted resource %s", resource_id)
        await self.audit_trail.record(
            action=AuditAction.DELETE,
            entity_id=resource.id,
            entity_name=resource.name,
            summary="Resource deleted",
            actor=actor,
            description="Resource removed after maintenance ticket checks.",
        )

    async def _validate_relationships(
        self,
        *,
        project_id: Optional[int],
        location_id: Optional[int],
    ) -> None:
        """Ensure referenced entities exist before persisting."""

        if project_id is not None:
            exists = await self.session.scalar(
                select(Project.id).where(Project.id == project_id)
            )
            if not exists:
                raise ValidationError(
                    f"Project {project_id} does not exist."
                )

        if location_id is not None:
            exists = await self.session.scalar(
                select(Location.id).where(Location.id == location_id)
            )
            if not exists:
                raise ValidationError(
                    f"Location {location_id} does not exist."
                )
