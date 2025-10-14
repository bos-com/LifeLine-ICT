"""Repository for persisting and querying audit logs."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence, Tuple

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AuditLog, AuditAction, AuditActorType, AuditEntityType
from .base import AsyncRepository


class AuditLogRepository(AsyncRepository[AuditLog]):
    """Provide filtered queries and persistence helpers for audit logs."""

    searchable_fields = (
        AuditLog.summary,
        AuditLog.entity_name,
        AuditLog.entity_id,
        AuditLog.actor_name,
        AuditLog.actor_id,
    )

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)

    def _apply_filters(
        self,
        stmt: Select[tuple[AuditLog]],
        *,
        action: Optional[AuditAction],
        entity_type: Optional[AuditEntityType],
        actor_type: Optional[AuditActorType],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Select[tuple[AuditLog]]:
        """
        Apply structured filters to an audit log query.
        """

        if action:
            stmt = stmt.where(AuditLog.action == action)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if actor_type:
            stmt = stmt.where(AuditLog.actor_type == actor_type)
        if date_from:
            stmt = stmt.where(AuditLog.created_at >= date_from)
        if date_to:
            stmt = stmt.where(AuditLog.created_at <= date_to)
        return stmt

    async def list_logs(
        self,
        *,
        limit: int,
        offset: int,
        search: Optional[str],
        action: Optional[AuditAction],
        entity_type: Optional[AuditEntityType],
        actor_type: Optional[AuditActorType],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Tuple[Sequence[AuditLog], int]:
        """
        Retrieve a paginated subset of audit logs matching the supplied filters.
        """

        stmt = self._apply_search(self._base_select(), search)
        stmt = self._apply_filters(
            stmt,
            action=action,
            entity_type=entity_type,
            actor_type=actor_type,
            date_from=date_from,
            date_to=date_to,
        ).order_by(AuditLog.created_at.desc())

        result = await self.session.execute(
            stmt.offset(offset).limit(limit)
        )
        items = result.scalars().all()

        count_stmt = select(func.count()).select_from(AuditLog)
        count_stmt = self._apply_search(count_stmt, search)  # type: ignore[arg-type]
        count_stmt = self._apply_filters(
            count_stmt,  # type: ignore[arg-type]
            action=action,
            entity_type=entity_type,
            actor_type=actor_type,
            date_from=date_from,
            date_to=date_to,
        )
        total = await self.session.scalar(count_stmt)

        return items, int(total or 0)
