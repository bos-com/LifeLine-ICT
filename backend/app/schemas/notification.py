"""Pydantic schemas for notification operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, EmailStr

from ..models.notification import NotificationType, NotificationStatus, NotificationPriority


class NotificationBase(BaseModel):
    """Base schema for notification data."""
    
    notification_type: NotificationType = Field(
        ...,
        description="Type of notification (email or SMS)."
    )
    
    recipient: str = Field(
        ...,
        description="Recipient address (email or phone number).",
        max_length=255
    )
    
    subject: Optional[str] = Field(
        None,
        description="Subject line for email notifications.",
        max_length=255
    )
    
    message: str = Field(
        ...,
        description="Notification message content."
    )
    
    priority: NotificationPriority = Field(
        NotificationPriority.MEDIUM,
        description="Notification priority level."
    )
    
    template_name: Optional[str] = Field(
        None,
        description="Template used for this notification.",
        max_length=255
    )
    
    context_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Template context data."
    )
    
    user_id: Optional[int] = Field(
        None,
        description="ID of user this notification relates to."
    )
    
    alert_id: Optional[int] = Field(
        None,
        description="ID of alert this notification relates to."
    )
    
    maintenance_ticket_id: Optional[int] = Field(
        None,
        description="ID of maintenance ticket this notification relates to."
    )


class NotificationCreate(NotificationBase):
    """Schema for creating a new notification."""
    pass


class NotificationUpdate(BaseModel):
    """Schema for updating notification status."""
    
    status: Optional[NotificationStatus] = Field(
        None,
        description="Updated notification status."
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error message if notification failed."
    )
    
    sent_at: Optional[datetime] = Field(
        None,
        description="Timestamp when notification was sent."
    )
    
    delivered_at: Optional[datetime] = Field(
        None,
        description="Timestamp when notification was delivered."
    )
    
    failed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when notification failed."
    )


class NotificationRead(NotificationBase):
    """Schema for reading notification data."""
    
    id: int = Field(..., description="Unique notification ID.")
    
    status: NotificationStatus = Field(
        ...,
        description="Current delivery status."
    )
    
    retry_count: int = Field(
        ...,
        description="Number of retry attempts made."
    )
    
    max_retries: int = Field(
        ...,
        description="Maximum number of retry attempts."
    )
    
    created_at: datetime = Field(
        ...,
        description="Timestamp when notification was created."
    )
    
    updated_at: datetime = Field(
        ...,
        description="Timestamp when notification was last updated."
    )
    
    sent_at: Optional[datetime] = Field(
        None,
        description="Timestamp when notification was sent."
    )
    
    delivered_at: Optional[datetime] = Field(
        None,
        description="Timestamp when notification was delivered."
    )
    
    failed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when notification failed."
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error message if notification failed."
    )
    
    class Config:
        from_attributes = True


class NotificationTemplate(BaseModel):
    """Schema for notification templates."""
    
    name: str = Field(
        ...,
        description="Template name identifier.",
        max_length=255
    )
    
    notification_type: NotificationType = Field(
        ...,
        description="Type of notification this template is for."
    )
    
    subject_template: Optional[str] = Field(
        None,
        description="Subject line template (for emails)."
    )
    
    message_template: str = Field(
        ...,
        description="Message content template."
    )
    
    html_template: Optional[str] = Field(
        None,
        description="HTML version of the template."
    )
    
    description: Optional[str] = Field(
        None,
        description="Template description."
    )


class NotificationRequest(BaseModel):
    """Schema for sending notifications via API."""
    
    notification_type: NotificationType = Field(
        ...,
        description="Type of notification to send."
    )
    
    recipient: str = Field(
        ...,
        description="Recipient address (email or phone number)."
    )
    
    template_name: Optional[str] = Field(
        None,
        description="Template to use for this notification."
    )
    
    subject: Optional[str] = Field(
        None,
        description="Subject line (for emails, overrides template)."
    )
    
    message: Optional[str] = Field(
        None,
        description="Message content (overrides template)."
    )
    
    context_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Template context data."
    )
    
    priority: NotificationPriority = Field(
        NotificationPriority.MEDIUM,
        description="Notification priority level."
    )
    
    user_id: Optional[int] = Field(
        None,
        description="ID of user this notification relates to."
    )
    
    alert_id: Optional[int] = Field(
        None,
        description="ID of alert this notification relates to."
    )
    
    maintenance_ticket_id: Optional[int] = Field(
        None,
        description="ID of maintenance ticket this notification relates to."
    )


class NotificationStats(BaseModel):
    """Schema for notification statistics."""
    
    total_notifications: int = Field(
        ...,
        description="Total number of notifications."
    )
    
    pending_notifications: int = Field(
        ...,
        description="Number of pending notifications."
    )
    
    sent_notifications: int = Field(
        ...,
        description="Number of successfully sent notifications."
    )
    
    failed_notifications: int = Field(
        ...,
        description="Number of failed notifications."
    )
    
    email_notifications: int = Field(
        ...,
        description="Number of email notifications."
    )
    
    sms_notifications: int = Field(
        ...,
        description="Number of SMS notifications."
    )
    
    retry_rate: float = Field(
        ...,
        description="Percentage of notifications that required retries."
    )
