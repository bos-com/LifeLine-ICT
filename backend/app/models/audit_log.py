"""SQLAlchemy model capturing audit trail events."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import Enum, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base
from .enums import AuditAction, AuditActorType, AuditEntityType
from .timestamp_mixin import TimestampMixin


class AuditLog(TimestampMixin, Base):
    """
    Persist immutable records describing security-relevant actions.

    Each entry captures who performed an action, what entity was touched, and
    contextual metadata that simplifies compliance reviews for the university's
    ICT oversight teams.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action"),
        nullable=False,
        doc="Action performed (create/update/delete/etc.).",
    )
    entity_type: Mapped[AuditEntityType] = mapped_column(
        Enum(AuditEntityType, name="audit_entity_type"),
        nullable=False,
        doc="Domain entity that was affected.",
    )
    entity_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Identifier of the affected entity stored as text for flexibility.",
    )
    entity_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Human-readable name or title of the entity, when available.",
    )
    actor_type: Mapped[AuditActorType] = mapped_column(
        Enum(AuditActorType, name="audit_actor_type"),
        nullable=False,
        default=AuditActorType.SYSTEM,
        doc="Classification of the actor who triggered the event.",
    )
    actor_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Identifier for the actor (e.g., user ID or service name).",
    )
    actor_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Display name for the actor, if available.",
    )
    summary: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Short summary describing the activity.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Optional detailed narrative of the action.",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        doc="IP address from which the action originated.",
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Trace identifier to correlate events across services.",
    )
    context: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Structured metadata (field deltas, payload excerpts, etc.).",
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """Representation for logging and debugging."""

        return (
            "<AuditLog id={0.id} action={0.action} entity_type={0.entity_type} "
            "entity_id={0.entity_id}>"
        ).format(self)
