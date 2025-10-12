"""SQLAlchemy model for notification tracking."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Enum as SQLEnum, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base
from .timestamp_mixin import TimestampMixin


class NotificationType(str, Enum):
    """Types of notifications that can be sent."""
    EMAIL = "email"
    SMS = "sms"


class NotificationStatus(str, Enum):
    """Status of notification delivery."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class NotificationPriority(str, Enum):
    """Priority levels for notifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(TimestampMixin, Base):
    """
    Track notification delivery attempts and status.
    
    This model stores all notification attempts including emails and SMS,
    allowing for delivery tracking, retry logic, and audit trails.
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Notification details
    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type"),
        nullable=False,
        doc="Type of notification (email or SMS)."
    )
    
    recipient: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Recipient address (email or phone number)."
    )
    
    subject: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Subject line for email notifications."
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Notification message content."
    )
    
    # Delivery tracking
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus, name="notification_status"),
        nullable=False,
        default=NotificationStatus.PENDING,
        doc="Current delivery status."
    )
    
    priority: Mapped[NotificationPriority] = mapped_column(
        SQLEnum(NotificationPriority, name="notification_priority"),
        nullable=False,
        default=NotificationPriority.MEDIUM,
        doc="Notification priority level."
    )
    
    # Retry logic
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of retry attempts made."
    )
    
    max_retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        doc="Maximum number of retry attempts."
    )
    
    # Timestamps
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when notification was successfully sent."
    )
    
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when notification was delivered (if available)."
    )
    
    failed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when notification failed."
    )
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Error message if notification failed."
    )
    
    # Context information
    template_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Template used for this notification."
    )
    
    context_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="JSON string of template context data."
    )
    
    # Related entities
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="ID of user this notification relates to."
    )
    
    alert_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="ID of alert this notification relates to."
    )
    
    maintenance_ticket_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="ID of maintenance ticket this notification relates to."
    )
