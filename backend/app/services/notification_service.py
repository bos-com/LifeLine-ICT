"""Main notification service orchestrating email and SMS notifications."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.notification import Notification, NotificationStatus, NotificationType, NotificationPriority
from ..repositories.notification_repository import NotificationRepository
from ..schemas.notification import NotificationCreate, NotificationRequest, NotificationStats
from .email_service import EmailService
from .sms_service import SMSService
from .base import BaseService

logger = logging.getLogger(__name__)


class NotificationService(BaseService):
    """Orchestrate email and SMS notifications with tracking and retry logic."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = NotificationRepository(session)
        self.email_service = EmailService()
        self.sms_service = SMSService()

    async def send_notification(self, request: NotificationRequest) -> Optional[Notification]:
        """
        Send a notification (email or SMS) and track it in the database.
        
        Args:
            request: Notification request details
            
        Returns:
            Created notification record or None if failed
        """
        try:
            # Create notification record
            notification_data = NotificationCreate(
                notification_type=request.notification_type,
                recipient=request.recipient,
                subject=request.subject,
                message=request.message or "",
                priority=request.priority,
                template_name=request.template_name,
                context_data=request.context_data,
                user_id=request.user_id,
                alert_id=request.alert_id,
                maintenance_ticket_id=request.maintenance_ticket_id
            )
            
            notification = await self.repository.create(notification_data.dict())
            
            # Send the notification
            success = await self._send_notification_async(notification)
            
            if success:
                await self.repository.mark_notification_sent(notification.id)
                logger.info(f"Notification {notification.id} sent successfully")
            else:
                await self.repository.mark_notification_failed(
                    notification.id, 
                    "Failed to send notification"
                )
                logger.error(f"Notification {notification.id} failed to send")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error in send_notification: {str(e)}")
            return None

    async def send_bulk_notifications(self, requests: List[NotificationRequest]) -> List[Notification]:
        """
        Send multiple notifications in parallel.
        
        Args:
            requests: List of notification requests
            
        Returns:
            List of created notification records
        """
        notifications = []
        
        # Create all notification records first
        for request in requests:
            try:
                notification = await self.send_notification(request)
                if notification:
                    notifications.append(notification)
            except Exception as e:
                logger.error(f"Failed to create notification for {request.recipient}: {str(e)}")
        
        return notifications

    async def retry_failed_notifications(self, limit: int = 100) -> List[Notification]:
        """
        Retry notifications that have failed.
        
        Args:
            limit: Maximum number of notifications to retry
            
        Returns:
            List of notifications that were retried
        """
        # Get failed notifications that can be retried
        failed_notifications = await self.repository.get_pending_notifications(limit)
        retried_notifications = []
        
        for notification in failed_notifications:
            try:
                # Increment retry count
                await self.repository.increment_retry_count(notification.id)
                
                # Attempt to send again
                success = await self._send_notification_async(notification)
                
                if success:
                    await self.repository.mark_notification_sent(notification.id)
                    logger.info(f"Notification {notification.id} sent successfully on retry")
                else:
                    if notification.retry_count >= notification.max_retries:
                        await self.repository.mark_notification_failed(
                            notification.id,
                            "Max retries exceeded"
                        )
                        logger.error(f"Notification {notification.id} failed permanently after {notification.retry_count} retries")
                    else:
                        await self.repository.mark_notification_failed(
                            notification.id,
                            "Retry attempt failed"
                        )
                        logger.warning(f"Notification {notification.id} retry failed, will retry again")
                
                retried_notifications.append(notification)
                
            except Exception as e:
                logger.error(f"Error retrying notification {notification.id}: {str(e)}")
        
        return retried_notifications

    async def send_email_notification(
        self,
        to_email: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        user_id: Optional[int] = None,
        alert_id: Optional[int] = None,
        maintenance_ticket_id: Optional[int] = None
    ) -> Optional[Notification]:
        """Send an email notification."""
        request = NotificationRequest(
            notification_type=NotificationType.EMAIL,
            recipient=to_email,
            subject=subject,
            message=message,
            template_name=template_name,
            context_data=context,
            priority=priority,
            user_id=user_id,
            alert_id=alert_id,
            maintenance_ticket_id=maintenance_ticket_id
        )
        
        return await self.send_notification(request)

    async def send_sms_notification(
        self,
        to_number: str,
        message: str,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        user_id: Optional[int] = None,
        alert_id: Optional[int] = None,
        maintenance_ticket_id: Optional[int] = None
    ) -> Optional[Notification]:
        """Send an SMS notification."""
        request = NotificationRequest(
            notification_type=NotificationType.SMS,
            recipient=to_number,
            message=message,
            template_name=template_name,
            context_data=context,
            priority=priority,
            user_id=user_id,
            alert_id=alert_id,
            maintenance_ticket_id=maintenance_ticket_id
        )
        
        return await self.send_notification(request)

    async def send_alert_notification(
        self,
        alert_data: Dict[str, Any],
        recipients: List[str],
        notification_types: List[NotificationType]
    ) -> List[Notification]:
        """
        Send alert notifications to multiple recipients via multiple channels.
        
        Args:
            alert_data: Alert information (type, severity, location, etc.)
            recipients: List of recipient addresses (emails/phone numbers)
            notification_types: List of notification types to send
            
        Returns:
            List of created notifications
        """
        notifications = []
        
        for recipient in recipients:
            for notification_type in notification_types:
                try:
                    if notification_type == NotificationType.EMAIL:
                        notification = await self.send_email_notification(
                            to_email=recipient,
                            subject=f"ALERT: {alert_data.get('type', 'System Alert')}",
                            message="",  # Will be filled by template
                            template_name="alert_notification",
                            context=alert_data,
                            priority=NotificationPriority.HIGH,
                            alert_id=alert_data.get('alert_id')
                        )
                    elif notification_type == NotificationType.SMS:
                        notification = await self.send_sms_notification(
                            to_number=recipient,
                            message="",  # Will be filled by template
                            template_name="alert_notification",
                            context=alert_data,
                            priority=NotificationPriority.HIGH,
                            alert_id=alert_data.get('alert_id')
                        )
                    
                    if notification:
                        notifications.append(notification)
                        
                except Exception as e:
                    logger.error(f"Failed to send alert notification to {recipient}: {str(e)}")
        
        return notifications

    async def get_notification_stats(self) -> NotificationStats:
        """Get notification statistics."""
        stats_data = await self.repository.get_notification_stats()
        
        return NotificationStats(
            total_notifications=stats_data['total_notifications'],
            pending_notifications=stats_data['status_counts'].get(NotificationStatus.PENDING, 0),
            sent_notifications=stats_data['status_counts'].get(NotificationStatus.SENT, 0),
            failed_notifications=stats_data['status_counts'].get(NotificationStatus.FAILED, 0),
            email_notifications=stats_data['type_counts'].get(NotificationType.EMAIL, 0),
            sms_notifications=stats_data['type_counts'].get(NotificationType.SMS, 0),
            retry_rate=stats_data['retry_rate']
        )

    async def _send_notification_async(self, notification: Notification) -> bool:
        """Send notification using the appropriate service."""
        try:
            if notification.notification_type == NotificationType.EMAIL:
                return await self._send_email(notification)
            elif notification.notification_type == NotificationType.SMS:
                return await self._send_sms(notification)
            else:
                logger.error(f"Unknown notification type: {notification.notification_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")
            return False

    async def _send_email(self, notification: Notification) -> bool:
        """Send email notification."""
        try:
            # If template is specified, use templated email
            if notification.template_name:
                context = json.loads(notification.context_data) if notification.context_data else {}
                return await self.email_service.send_templated_email(
                    to_email=notification.recipient,
                    template_name=notification.template_name,
                    subject=notification.subject or "LifeLine-ICT Notification",
                    context=context
                )
            else:
                # Send plain email
                return await self.email_service.send_email(
                    to_email=notification.recipient,
                    subject=notification.subject or "LifeLine-ICT Notification",
                    message=notification.message
                )
                
        except Exception as e:
            logger.error(f"Failed to send email notification {notification.id}: {str(e)}")
            return False

    async def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification."""
        try:
            # If template is specified, use templated SMS
            if notification.template_name:
                context = json.loads(notification.context_data) if notification.context_data else {}
                return await self.sms_service.send_templated_sms(
                    to_number=notification.recipient,
                    template_name=notification.template_name,
                    context=context
                )
            else:
                # Send plain SMS
                return await self.sms_service.send_sms(
                    to_number=notification.recipient,
                    message=notification.message
                )
                
        except Exception as e:
            logger.error(f"Failed to send SMS notification {notification.id}: {str(e)}")
            return False

    async def test_services(self) -> Dict[str, bool]:
        """Test email and SMS service connections."""
        return {
            'email_service': await self.email_service.test_connection(),
            'sms_service': await self.sms_service.test_connection()
        }
