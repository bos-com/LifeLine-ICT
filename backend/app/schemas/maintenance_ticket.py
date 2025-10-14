"""Pydantic schemas for maintenance ticket entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from ..models import TicketSeverity, TicketStatus
from .base import BaseSchema


class TicketBase(BaseSchema):
    """Common attributes for maintenance tickets."""

    resource_id: int = Field(
        ...,
        description="Identifier of the affected resource.",
    )
    reported_by: str = Field(
        ...,
        max_length=255,
        description="Reporter name or email.",
    )
    issue_summary: str = Field(
        ...,
        description="Description of the reported issue.",
    )
    severity: TicketSeverity = Field(
        default=TicketSeverity.MEDIUM,
        description="Operational severity level.",
    )
    status: TicketStatus = Field(
        default=TicketStatus.OPEN,
        description="Ticket workflow status.",
    )
    opened_at: datetime = Field(
        ...,
        description="Timestamp when the issue was reported.",
    )
    closed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the ticket was closed.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes or resolution details.",
    )


class TicketCreate(TicketBase):
    """Payload for creating a maintenance ticket."""

    pass


class TicketUpdate(BaseSchema):
    """Payload for partially updating a maintenance ticket."""

    reported_by: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Reporter name or email.",
    )
    issue_summary: Optional[str] = Field(
        default=None,
        description="Description of the reported issue.",
    )
    severity: Optional[TicketSeverity] = Field(
        default=None,
        description="Operational severity level.",
    )
    status: Optional[TicketStatus] = Field(
        default=None,
        description="Ticket workflow status.",
    )
    opened_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the issue was reported.",
    )
    closed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the ticket was closed.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes or resolution details.",
    )


class TicketRead(TicketBase):
    """Representation returned by the API."""

    id: int = Field(..., description="Unique identifier.")
