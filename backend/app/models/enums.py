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


class AuditAction(str, enum.Enum):
    """Canonical actions captured by the audit trail."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"
    STATUS_CHANGE = "status_change"
    ATTACHMENT = "attachment"


class AuditActorType(str, enum.Enum):
    """Identity categories describing who triggered the event."""

    USER = "user"
    SYSTEM = "system"
    SERVICE = "service"
    ADMIN = "admin"


class AuditEntityType(str, enum.Enum):
    """Domain entities monitored by the audit log."""

    PROJECT = "project"
    RESOURCE = "resource"
    MAINTENANCE_TICKET = "maintenance_ticket"
    DOCUMENT = "document"
    LOCATION = "location"
    SENSOR_SITE = "sensor_site"
    NOTIFICATION = "notification"
    USER = "user"
    ALERT = "alert"
