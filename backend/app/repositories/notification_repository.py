"""Repository for notification database operations."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.notification import Notification, NotificationStatus, NotificationType
from .base import AsyncRepository

logger = logging.getLogger(__name__)


class NotificationRepository(AsyncRepository[Notification]):
    """Handle database operations for notifications."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Notification)

    async def get_pending_notifications(
        self, 
        limit: int = 100
    ) -> List[Notification]:
        """Get notifications that are pending or need retry."""
        query = select(Notification).where(
            or_(
                Notification.status == NotificationStatus.PENDING,
                and_(
                    Notification.status == NotificationStatus.FAILED,
                    Notification.retry_count < Notification.max_retries
                )
            )
        ).order_by(Notification.priority.desc(), Notification.created_at.asc())
        
        if limit > 0:
            query = query.limit(limit)
            
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_notifications_by_status(
        self, 
        status: NotificationStatus,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Notification], int]:
        """Get notifications by status with pagination."""
        # Count query
        count_query = select(func.count(Notification.id)).where(
            Notification.status == status
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Notification).where(
            Notification.status == status
        ).order_by(Notification.created_at.desc())
        
        if limit > 0:
            query = query.limit(limit).offset(offset)
            
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())
        
        return notifications, total

    async def get_notifications_by_type(
        self, 
        notification_type: NotificationType,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Notification], int]:
        """Get notifications by type with pagination."""
        # Count query
        count_query = select(func.count(Notification.id)).where(
            Notification.notification_type == notification_type
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Notification).where(
            Notification.notification_type == notification_type
        ).order_by(Notification.created_at.desc())
        
        if limit > 0:
            query = query.limit(limit).offset(offset)
            
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())
        
        return notifications, total

    async def get_notifications_by_recipient(
        self, 
        recipient: str,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Notification], int]:
        """Get notifications for a specific recipient."""
        # Count query
        count_query = select(func.count(Notification.id)).where(
            Notification.recipient == recipient
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Notification).where(
            Notification.recipient == recipient
        ).order_by(Notification.created_at.desc())
        
        if limit > 0:
            query = query.limit(limit).offset(offset)
            
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())
        
        return notifications, total

    async def get_notifications_by_user(
        self, 
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Notification], int]:
        """Get notifications for a specific user."""
        # Count query
        count_query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Notification).where(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc())
        
        if limit > 0:
            query = query.limit(limit).offset(offset)
            
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())
        
        return notifications, total

    async def get_notifications_by_alert(
        self, 
        alert_id: int
    ) -> List[Notification]:
        """Get all notifications related to a specific alert."""
        query = select(Notification).where(
            Notification.alert_id == alert_id
        ).order_by(Notification.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_notifications_by_maintenance_ticket(
        self, 
        ticket_id: int
    ) -> List[Notification]:
        """Get all notifications related to a specific maintenance ticket."""
        query = select(Notification).where(
            Notification.maintenance_ticket_id == ticket_id
        ).order_by(Notification.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_notification_stats(self) -> dict:
        """Get notification statistics."""
        # Total notifications
        total_query = select(func.count(Notification.id))
        total_result = await self.session.execute(total_query)
        total = total_result.scalar()

        # Notifications by status
        status_query = select(
            Notification.status,
            func.count(Notification.id).label('count')
        ).group_by(Notification.status)
        status_result = await self.session.execute(status_query)
        status_counts = {row.status: row.count for row in status_result}

        # Notifications by type
        type_query = select(
            Notification.notification_type,
            func.count(Notification.id).label('count')
        ).group_by(Notification.notification_type)
        type_result = await self.session.execute(type_query)
        type_counts = {row.notification_type: row.count for row in type_result}

        # Retry rate
        retry_query = select(func.count(Notification.id)).where(
            Notification.retry_count > 0
        )
        retry_result = await self.session.execute(retry_query)
        retry_count = retry_result.scalar()
        retry_rate = (retry_count / total * 100) if total > 0 else 0

        return {
            'total_notifications': total,
            'status_counts': status_counts,
            'type_counts': type_counts,
            'retry_rate': retry_rate
        }

    async def mark_notification_sent(
        self, 
        notification_id: int
    ) -> Optional[Notification]:
        """Mark a notification as sent."""
        notification = await self.get(notification_id)
        if notification:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(notification)
        return notification

    async def mark_notification_delivered(
        self, 
        notification_id: int
    ) -> Optional[Notification]:
        """Mark a notification as delivered."""
        notification = await self.get(notification_id)
        if notification:
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(notification)
        return notification

    async def mark_notification_failed(
        self, 
        notification_id: int, 
        error_message: str
    ) -> Optional[Notification]:
        """Mark a notification as failed."""
        notification = await self.get(notification_id)
        if notification:
            notification.status = NotificationStatus.FAILED
            notification.failed_at = datetime.utcnow()
            notification.error_message = error_message
            notification.retry_count += 1
            await self.session.commit()
            await self.session.refresh(notification)
        return notification

    async def increment_retry_count(
        self, 
        notification_id: int
    ) -> Optional[Notification]:
        """Increment the retry count for a notification."""
        notification = await self.get(notification_id)
        if notification:
            notification.retry_count += 1
            notification.status = NotificationStatus.RETRYING
            await self.session.commit()
            await self.session.refresh(notification)
        return notification
