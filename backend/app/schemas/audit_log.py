"""Pydantic schemas for audit log operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from ..models import AuditAction, AuditActorType, AuditEntityType
from .base import BaseSchema, PaginationQuery


class AuditLogBase(BaseSchema):
    """Shared attributes describing an audit trail entry."""

    action: AuditAction = Field(
        ...,
        description="Action that was performed against the entity.",
    )
    entity_type: AuditEntityType = Field(
        ...,
        description="Domain entity that the action targeted.",
    )
    entity_id: str = Field(
        ...,
        max_length=100,
        description="Identifier of the impacted entity, stored as text.",
    )
    entity_name: Optional[str] = Field(
        default=None,
        description="Human-readable name of the entity, if available.",
    )
    actor_type: AuditActorType = Field(
        default=AuditActorType.SYSTEM,
        description="Classification of the actor that triggered the action.",
    )
    actor_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Identifier for the actor (e.g., user ID or service name).",
    )
    actor_name: Optional[str] = Field(
        default=None,
        description="Friendly display name for the actor.",
    )
    summary: str = Field(
        ...,
        max_length=255,
        description="Concise summary that describes the action.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional narrative providing additional context.",
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        description="Source IP address captured for network traceability.",
    )
    request_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Correlation identifier for cross-service tracing.",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured metadata such as field changes or payload excerpts.",
    )


class AuditLogCreate(AuditLogBase):
    """Payload accepted when recording a new audit event."""

    pass


class AuditLogRead(AuditLogBase):
    """Representation returned to API consumers."""

    id: int = Field(..., description="Unique identifier of the audit record.")
    created_at: datetime = Field(
        ..., description="Timestamp indicating when the event occurred."
    )
    updated_at: datetime = Field(
        ..., description="Timestamp of the last persistence operation."
    )


class AuditLogQuery(PaginationQuery):
    """Query parameters for listing audit logs."""

    action: Optional[AuditAction] = Field(
        default=None,
        description="Filter by a specific action type.",
    )
    entity_type: Optional[AuditEntityType] = Field(
        default=None,
        description="Restrict results to a particular entity type.",
    )
    actor_type: Optional[AuditActorType] = Field(
        default=None,
        description="Filter by the type of actor that performed the action.",
    )
    date_from: Optional[datetime] = Field(
        default=None,
        description="Return entries captured at or after this timestamp.",
    )
    date_to: Optional[datetime] = Field(
        default=None,
        description="Return entries captured at or before this timestamp.",
    )
