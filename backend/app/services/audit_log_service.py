"""Service encapsulating audit log business logic."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..models import AuditLog
from ..repositories import AuditLogRepository
from ..schemas import AuditLogCreate, AuditLogRead, AuditLogQuery, PaginatedResponse
from .base import BaseService
from .exceptions import NotFoundError


class AuditLogService(BaseService):
    """Coordinate persistence and retrieval of audit events."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = AuditLogRepository(session)

    async def record_event(self, payload: AuditLogCreate) -> AuditLogRead:
        """
        Persist a new audit entry and return the serialised representation.
        """

        audit_log = await self.repository.create(payload.dict())
        return AuditLogRead.from_orm(audit_log)

    async def list_logs(self, query: AuditLogQuery) -> PaginatedResponse[AuditLogRead]:
        """
        Return a paginated collection of audit logs matching the query filters.
        """

        limit = query.limit or settings.pagination_default_limit
        limit = min(limit, settings.pagination_max_limit)
        offset = query.offset or 0

        items, total = await self.repository.list_logs(
            limit=limit,
            offset=offset,
            search=query.search,
            action=query.action,
            entity_type=query.entity_type,
            actor_type=query.actor_type,
            date_from=query.date_from,
            date_to=query.date_to,
        )
        return self.build_paginated_response(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            schema=AuditLogRead,
        )

    async def get_log(self, log_id: int) -> AuditLogRead:
        """
        Fetch a single audit entry or raise ``NotFoundError`` if missing.
        """

        log: Optional[AuditLog] = await self.repository.get(log_id)
        if log is None:
            raise NotFoundError(f"Audit log {log_id} not found.")
        return AuditLogRead.from_orm(log)
