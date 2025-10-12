"""Enumerations describing canonical states for LifeLine-ICT entities."""

from __future__ import annotations

import enum


class ProjectStatus(str, enum.Enum):
    """Lifecycle states for university ICT projects."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LifecycleState(str, enum.Enum):
    """Lifecycle phases for ICT resources."""

    DRAFT = "draft"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class TicketSeverity(str, enum.Enum):
    """Severity levels used by the ICT help-desk."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    """Operational states for maintenance tickets."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
