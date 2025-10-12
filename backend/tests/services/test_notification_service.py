"""Tests for the notification service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationStatus, NotificationPriority
from app.schemas.notification import NotificationRequest


@pytest.fixture
async def notification_service(session):
    """Create a notification service instance for testing."""
    return NotificationService(session)


@pytest.fixture
def sample_notification_request():
    """Create a sample notification request for testing."""
    return NotificationRequest(
        notification_type=NotificationType.EMAIL,
        recipient="test@example.com",
        subject="Test Notification",
        message="This is a test notification",
        priority=NotificationPriority.MEDIUM
    )


class TestNotificationService:
    """Test cases for the notification service."""

    @pytest.mark.asyncio
    async def test_send_email_notification(
        self, 
        notification_service, 
        sample_notification_request
    ):
        """Test sending an email notification."""
        # Mock the email service
        with patch.object(notification_service.email_service, 'send_email') as mock_send:
            mock_send.return_value = True
            
            # Mock the repository create method
            with patch.object(notification_service.repository, 'create') as mock_create:
                mock_notification = MagicMock()
                mock_notification.id = 1
                mock_create.return_value = mock_notification
                
                # Mock the mark as sent method
                with patch.object(notification_service.repository, 'mark_notification_sent') as mock_mark_sent:
                    result = await notification_service.send_notification(sample_notification_request)
                    
                    assert result is not None
                    mock_create.assert_called_once()
                    mock_send.assert_called_once()
                    mock_mark_sent.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_sms_notification(self, notification_service):
        """Test sending an SMS notification."""
        sms_request = NotificationRequest(
            notification_type=NotificationType.SMS,
            recipient="+256700000000",
            message="Test SMS notification",
            priority=NotificationPriority.HIGH
        )
        
        # Mock the SMS service
        with patch.object(notification_service.sms_service, 'send_sms') as mock_send:
            mock_send.return_value = True
            
            # Mock the repository methods
            with patch.object(notification_service.repository, 'create') as mock_create:
                mock_notification = MagicMock()
                mock_notification.id = 2
                mock_create.return_value = mock_notification
                
                with patch.object(notification_service.repository, 'mark_notification_sent') as mock_mark_sent:
                    result = await notification_service.send_notification(sms_request)
                    
                    assert result is not None
                    mock_create.assert_called_once()
                    mock_send.assert_called_once()
                    mock_mark_sent.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_templated_email_notification(self, notification_service):
        """Test sending a templated email notification."""
        templated_request = NotificationRequest(
            notification_type=NotificationType.EMAIL,
            recipient="user@example.com",
            template_name="welcome",
            context_data={"user_name": "John Doe", "user_email": "user@example.com"},
            priority=NotificationPriority.MEDIUM
        )
        
        # Mock the email service templated method
        with patch.object(notification_service.email_service, 'send_templated_email') as mock_send:
            mock_send.return_value = True
            
            # Mock the repository methods
            with patch.object(notification_service.repository, 'create') as mock_create:
                mock_notification = MagicMock()
                mock_notification.id = 3
                mock_create.return_value = mock_notification
                
                with patch.object(notification_service.repository, 'mark_notification_sent') as mock_mark_sent:
                    result = await notification_service.send_notification(templated_request)
                    
                    assert result is not None
                    mock_create.assert_called_once()
                    mock_send.assert_called_once()
                    mock_mark_sent.assert_called_once()

    @pytest.mark.asyncio
    async def test_notification_failure_handling(self, notification_service, sample_notification_request):
        """Test handling of notification failures."""
        # Mock the email service to return failure
        with patch.object(notification_service.email_service, 'send_email') as mock_send:
            mock_send.return_value = False
            
            # Mock the repository methods
            with patch.object(notification_service.repository, 'create') as mock_create:
                mock_notification = MagicMock()
                mock_notification.id = 4
                mock_create.return_value = mock_notification
                
                with patch.object(notification_service.repository, 'mark_notification_failed') as mock_mark_failed:
                    result = await notification_service.send_notification(sample_notification_request)
                    
                    assert result is not None
                    mock_create.assert_called_once()
                    mock_send.assert_called_once()
                    mock_mark_failed.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_bulk_notifications(self, notification_service):
        """Test sending multiple notifications."""
        requests = [
            NotificationRequest(
                notification_type=NotificationType.EMAIL,
                recipient="user1@example.com",
                subject="Bulk Test 1",
                message="First notification",
                priority=NotificationPriority.LOW
            ),
            NotificationRequest(
                notification_type=NotificationType.SMS,
                recipient="+256700000001",
                message="Second notification",
                priority=NotificationPriority.MEDIUM
            )
        ]
        
        # Mock the send_notification method
        with patch.object(notification_service, 'send_notification') as mock_send:
            mock_send.return_value = MagicMock(id=1)
            
            results = await notification_service.send_bulk_notifications(requests)
            
            assert len(results) == 2
            assert mock_send.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_failed_notifications(self, notification_service):
        """Test retrying failed notifications."""
        # Mock the repository to return pending notifications
        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.retry_count = 1
        mock_notification.max_retries = 3
        
        with patch.object(notification_service.repository, 'get_pending_notifications') as mock_get_pending:
            mock_get_pending.return_value = [mock_notification]
            
            # Mock the send notification async method
            with patch.object(notification_service, '_send_notification_async') as mock_send:
                mock_send.return_value = True
                
                # Mock repository methods
                with patch.object(notification_service.repository, 'increment_retry_count') as mock_increment:
                    with patch.object(notification_service.repository, 'mark_notification_sent') as mock_mark_sent:
                        results = await notification_service.retry_failed_notifications()
                        
                        assert len(results) == 1
                        mock_increment.assert_called_once()
                        mock_send.assert_called_once()
                        mock_mark_sent.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_alert_notification(self, notification_service):
        """Test sending alert notifications."""
        alert_data = {
            'alert_id': 1,
            'type': 'Temperature Alert',
            'severity': 'HIGH',
            'location': 'Building A',
            'alert_time': datetime.now().isoformat(),
            'description': 'Temperature exceeded threshold'
        }
        
        recipients = ["admin@example.com", "+256700000000"]
        notification_types = [NotificationType.EMAIL, NotificationType.SMS]
        
        # Mock the send_notification method
        with patch.object(notification_service, 'send_notification') as mock_send:
            mock_send.return_value = MagicMock(id=1)
            
            results = await notification_service.send_alert_notification(
                alert_data, recipients, notification_types
            )
            
            # Should create 4 notifications (2 recipients × 2 types)
            assert len(results) == 4
            assert mock_send.call_count == 4

    @pytest.mark.asyncio
    async def test_get_notification_stats(self, notification_service):
        """Test getting notification statistics."""
        mock_stats = {
            'total_notifications': 100,
            'status_counts': {
                NotificationStatus.PENDING: 5,
                NotificationStatus.SENT: 90,
                NotificationStatus.FAILED: 5
            },
            'type_counts': {
                NotificationType.EMAIL: 80,
                NotificationType.SMS: 20
            },
            'retry_rate': 10.0
        }
        
        with patch.object(notification_service.repository, 'get_notification_stats') as mock_get_stats:
            mock_get_stats.return_value = mock_stats
            
            stats = await notification_service.get_notification_stats()
            
            assert stats.total_notifications == 100
            assert stats.pending_notifications == 5
            assert stats.sent_notifications == 90
            assert stats.failed_notifications == 5
            assert stats.email_notifications == 80
            assert stats.sms_notifications == 20
            assert stats.retry_rate == 10.0

    @pytest.mark.asyncio
    async def test_test_services(self, notification_service):
        """Test service connection testing."""
        with patch.object(notification_service.email_service, 'test_connection') as mock_email_test:
            with patch.object(notification_service.sms_service, 'test_connection') as mock_sms_test:
                mock_email_test.return_value = True
                mock_sms_test.return_value = False
                
                results = await notification_service.test_services()
                
                assert results['email_service'] is True
                assert results['sms_service'] is False
