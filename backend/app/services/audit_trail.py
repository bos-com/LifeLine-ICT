"""Helper utilities to streamline audit trail recordings."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AuditAction, AuditActorType, AuditEntityType, User
from ..schemas import AuditLogCreate
from .audit_log_service import AuditLogService


class AuditTrailRecorder:
    """
    Lightweight helper that encapsulates audit logging boilerplate.

    Services construct a recorder with their default entity type and then call
    ``record`` whenever an auditable action occurs. The recorder takes care of
    serialising contextual metadata and tagging the actor correctly.
    """

    def __init__(self, session: AsyncSession, entity_type: AuditEntityType) -> None:
        self._service = AuditLogService(session)
        self._entity_type = entity_type

    async def record(
        self,
        *,
        action: AuditAction,
        entity_id: int | str,
        summary: str,
        actor: Optional[User] = None,
        entity_name: Optional[str] = None,
        description: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Persist an audit event with the supplied metadata.
        """

        actor_type = AuditActorType.USER if actor else AuditActorType.SYSTEM
        actor_id = str(actor.id) if actor else None
        actor_name = actor.username if actor else None
        encoded_context = (
            jsonable_encoder(context) if context is not None else None
        )

        payload = AuditLogCreate(
            action=action,
            entity_type=self._entity_type,
            entity_id=str(entity_id),
            entity_name=entity_name,
            summary=summary,
            description=description,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            context=encoded_context,
        )

        await self._service.record_event(payload)
