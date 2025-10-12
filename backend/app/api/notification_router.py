"""API router for notification operations."""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ..api.deps import get_session
from ..models.notification import NotificationType, NotificationStatus, NotificationPriority
from ..schemas.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationRequest,
    NotificationStats,
)
from ..schemas.base import PaginationQuery, PaginatedResponse
from ..services.notification_service import NotificationService
from ..repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/send", response_model=NotificationRead)
async def send_notification(
    request: NotificationRequest,
    session=Depends(get_session)
) -> NotificationRead:
    """
    Send a notification (email or SMS).
    
    This endpoint allows sending individual notifications with optional templates.
    """
    try:
        notification_service = NotificationService(session)
        notification = await notification_service.send_notification(request)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send notification"
            )
        
        return NotificationRead.from_orm(notification)
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.post("/send/bulk", response_model=List[NotificationRead])
async def send_bulk_notifications(
    requests: List[NotificationRequest],
    session=Depends(get_session)
) -> List[NotificationRead]:
    """
    Send multiple notifications in parallel.
    
    This endpoint allows sending multiple notifications efficiently.
    """
    try:
        notification_service = NotificationService(session)
        notifications = await notification_service.send_bulk_notifications(requests)
        
        return [NotificationRead.from_orm(notification) for notification in notifications]
        
    except Exception as e:
        logger.error(f"Error sending bulk notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send bulk notifications: {str(e)}"
        )


@router.get("/", response_model=PaginatedResponse[NotificationRead])
async def list_notifications(
    pagination: PaginationQuery = Depends(),
    notification_type: Optional[NotificationType] = None,
    status: Optional[NotificationStatus] = None,
    session=Depends(get_session)
) -> PaginatedResponse[NotificationRead]:
    """
    List notifications with optional filtering.
    
    Filter by notification type, status, or both.
    """
    try:
        repository = NotificationRepository(session)
        
        # Get notifications based on filters
        if status and notification_type:
            # Filter by both status and type
            notifications, total = await repository.list(
                limit=pagination.limit,
                offset=pagination.offset
            )
            # Apply filters (this would need to be implemented in repository)
            filtered_notifications = [
                n for n in notifications 
                if n.status == status and n.notification_type == notification_type
            ]
            total = len(filtered_notifications)
        elif status:
            notifications, total = await repository.get_notifications_by_status(
                status, pagination.limit, pagination.offset
            )
        elif notification_type:
            notifications, total = await repository.get_notifications_by_type(
                notification_type, pagination.limit, pagination.offset
            )
        else:
            notifications, total = await repository.list(
                limit=pagination.limit,
                offset=pagination.offset
            )
        
        return PaginatedResponse(
            items=[NotificationRead.from_orm(notification) for notification in notifications],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset
        )
        
    except Exception as e:
        logger.error(f"Error listing notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list notifications: {str(e)}"
        )


@router.get("/{notification_id}", response_model=NotificationRead)
async def get_notification(
    notification_id: int,
    session=Depends(get_session)
) -> NotificationRead:
    """Get a specific notification by ID."""
    try:
        repository = NotificationRepository(session)
        notification = await repository.get(notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {notification_id} not found"
            )
        
        return NotificationRead.from_orm(notification)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification {notification_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification: {str(e)}"
        )


@router.get("/recipient/{recipient}", response_model=PaginatedResponse[NotificationRead])
async def get_notifications_by_recipient(
    recipient: str,
    pagination: PaginationQuery = Depends(),
    session=Depends(get_session)
) -> PaginatedResponse[NotificationRead]:
    """Get all notifications for a specific recipient."""
    try:
        repository = NotificationRepository(session)
        notifications, total = await repository.get_notifications_by_recipient(
            recipient, pagination.limit, pagination.offset
        )
        
        return PaginatedResponse(
            items=[NotificationRead.from_orm(notification) for notification in notifications],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset
        )
        
    except Exception as e:
        logger.error(f"Error getting notifications for recipient {recipient}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications for recipient: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=PaginatedResponse[NotificationRead])
async def get_notifications_by_user(
    user_id: int,
    pagination: PaginationQuery = Depends(),
    session=Depends(get_session)
) -> PaginatedResponse[NotificationRead]:
    """Get all notifications for a specific user."""
    try:
        repository = NotificationRepository(session)
        notifications, total = await repository.get_notifications_by_user(
            user_id, pagination.limit, pagination.offset
        )
        
        return PaginatedResponse(
            items=[NotificationRead.from_orm(notification) for notification in notifications],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset
        )
        
    except Exception as e:
        logger.error(f"Error getting notifications for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications for user: {str(e)}"
        )


@router.get("/alert/{alert_id}", response_model=List[NotificationRead])
async def get_notifications_by_alert(
    alert_id: int,
    session=Depends(get_session)
) -> List[NotificationRead]:
    """Get all notifications related to a specific alert."""
    try:
        repository = NotificationRepository(session)
        notifications = await repository.get_notifications_by_alert(alert_id)
        
        return [NotificationRead.from_orm(notification) for notification in notifications]
        
    except Exception as e:
        logger.error(f"Error getting notifications for alert {alert_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications for alert: {str(e)}"
        )


@router.get("/maintenance-ticket/{ticket_id}", response_model=List[NotificationRead])
async def get_notifications_by_maintenance_ticket(
    ticket_id: int,
    session=Depends(get_session)
) -> List[NotificationRead]:
    """Get all notifications related to a specific maintenance ticket."""
    try:
        repository = NotificationRepository(session)
        notifications = await repository.get_notifications_by_maintenance_ticket(ticket_id)
        
        return [NotificationRead.from_orm(notification) for notification in notifications]
        
    except Exception as e:
        logger.error(f"Error getting notifications for ticket {ticket_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications for ticket: {str(e)}"
        )


@router.post("/retry", response_model=List[NotificationRead])
async def retry_failed_notifications(
    limit: int = 100,
    session=Depends(get_session)
) -> List[NotificationRead]:
    """
    Retry failed notifications.
    
    This endpoint attempts to resend notifications that have failed.
    """
    try:
        notification_service = NotificationService(session)
        notifications = await notification_service.retry_failed_notifications(limit)
        
        return [NotificationRead.from_orm(notification) for notification in notifications]
        
    except Exception as e:
        logger.error(f"Error retrying failed notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry notifications: {str(e)}"
        )


@router.get("/stats/overview", response_model=NotificationStats)
async def get_notification_stats(
    session=Depends(get_session)
) -> NotificationStats:
    """Get notification statistics and metrics."""
    try:
        notification_service = NotificationService(session)
        stats = await notification_service.get_notification_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification stats: {str(e)}"
        )


@router.post("/test", response_model=dict)
async def test_notification_services(
    session=Depends(get_session)
) -> dict:
    """Test email and SMS service connections."""
    try:
        notification_service = NotificationService(session)
        test_results = await notification_service.test_services()
        
        return {
            "message": "Service connection tests completed",
            "results": test_results
        }
        
    except Exception as e:
        logger.error(f"Error testing notification services: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test services: {str(e)}"
        )


@router.post("/email/send", response_model=NotificationRead)
async def send_email_notification(
    to_email: str,
    subject: str,
    message: str,
    html_message: Optional[str] = None,
    template_name: Optional[str] = None,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    user_id: Optional[int] = None,
    alert_id: Optional[int] = None,
    maintenance_ticket_id: Optional[int] = None,
    session=Depends(get_session)
) -> NotificationRead:
    """
    Send an email notification directly.
    
    Convenience endpoint for sending email notifications.
    """
    try:
        notification_service = NotificationService(session)
        notification = await notification_service.send_email_notification(
            to_email=to_email,
            subject=subject,
            message=message,
            html_message=html_message,
            template_name=template_name,
            priority=priority,
            user_id=user_id,
            alert_id=alert_id,
            maintenance_ticket_id=maintenance_ticket_id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email notification"
            )
        
        return NotificationRead.from_orm(notification)
        
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email notification: {str(e)}"
        )


@router.post("/sms/send", response_model=NotificationRead)
async def send_sms_notification(
    to_number: str,
    message: str,
    template_name: Optional[str] = None,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    user_id: Optional[int] = None,
    alert_id: Optional[int] = None,
    maintenance_ticket_id: Optional[int] = None,
    session=Depends(get_session)
) -> NotificationRead:
    """
    Send an SMS notification directly.
    
    Convenience endpoint for sending SMS notifications.
    """
    try:
        notification_service = NotificationService(session)
        notification = await notification_service.send_sms_notification(
            to_number=to_number,
            message=message,
            template_name=template_name,
            priority=priority,
            user_id=user_id,
            alert_id=alert_id,
            maintenance_ticket_id=maintenance_ticket_id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send SMS notification"
            )
        
        return NotificationRead.from_orm(notification)
        
    except Exception as e:
        logger.error(f"Error sending SMS notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS notification: {str(e)}"
        )
