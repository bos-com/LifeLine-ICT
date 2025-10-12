# Email & SMS Notification Service

This document describes the implementation of the Email & SMS Notification Service for LifeLine-ICT, addressing [GitHub Issue #8](https://github.com/bos-com/LifeLine-ICT/issues/8).

## Overview

The notification service provides a comprehensive solution for sending email and SMS notifications with the following features:

- **Email notifications** via SMTP
- **SMS notifications** via Twilio
- **Template system** for HTML/text emails and SMS messages
- **Retry logic** for failed notifications
- **Delivery tracking** and status monitoring
- **Integration** with existing alert system
- **API endpoints** for notification management

## Architecture

### Core Components

1. **Notification Model** (`app/models/notification.py`)
   - Database model for tracking notifications
   - Status tracking (pending, sent, delivered, failed)
   - Retry logic and error handling
   - Context data for templates

2. **Email Service** (`app/services/email_service.py`)
   - SMTP integration with aiosmtplib
   - HTML and text email support
   - Template rendering with Jinja2
   - Built-in email templates

3. **SMS Service** (`app/services/sms_service.py`)
   - Twilio integration
   - Phone number validation and formatting
   - Template support for SMS messages
   - Delivery status tracking

4. **Notification Service** (`app/services/notification_service.py`)
   - Orchestrates email and SMS services
   - Handles retry logic and error recovery
   - Integrates with existing alert system
   - Provides unified API for notifications

5. **API Router** (`app/api/notification_router.py`)
   - RESTful endpoints for notification management
   - Bulk notification support
   - Statistics and monitoring endpoints

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Email/SMTP Configuration
LIFELINE_SMTP_HOST=smtp.gmail.com
LIFELINE_SMTP_PORT=587
LIFELINE_SMTP_USERNAME=your-email@gmail.com
LIFELINE_SMTP_PASSWORD=your-app-password
LIFELINE_SMTP_USE_TLS=true
LIFELINE_FROM_EMAIL=noreply@lifeline.edu
LIFELINE_FROM_NAME=LifeLine-ICT

# SMS/Twilio Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

### Email Templates

The service includes built-in templates for common notification types:

- **Welcome** - User registration confirmation
- **Password Reset** - Password reset requests
- **Alert Notification** - System alerts and warnings
- **Maintenance Reminder** - Scheduled maintenance notifications
- **Verification Code** - Two-factor authentication codes
- **Ticket Update** - Maintenance ticket status updates

### SMS Templates

SMS templates are optimized for 160-character limits:

- **Welcome** - Registration confirmation
- **Password Reset** - Reset link notifications
- **Alert Notification** - Critical system alerts
- **Maintenance Reminder** - Maintenance notifications
- **Verification Code** - Authentication codes
- **Ticket Update** - Status updates

## API Endpoints

### Send Notifications

```http
POST /notifications/send
Content-Type: application/json

{
  "notification_type": "email",
  "recipient": "user@example.com",
  "subject": "Welcome to LifeLine-ICT",
  "template_name": "welcome",
  "context_data": {
    "user_name": "John Doe",
    "user_email": "user@example.com"
  },
  "priority": "medium"
}
```

### Bulk Notifications

```http
POST /notifications/send/bulk
Content-Type: application/json

[
  {
    "notification_type": "email",
    "recipient": "user1@example.com",
    "template_name": "alert_notification",
    "context_data": {"alert_type": "Temperature Alert"}
  },
  {
    "notification_type": "sms",
    "recipient": "+256700000000",
    "template_name": "alert_notification",
    "context_data": {"alert_type": "Temperature Alert"}
  }
]
```

### List Notifications

```http
GET /notifications/?limit=20&offset=0&notification_type=email&status=sent
```

### Notification Statistics

```http
GET /notifications/stats/overview
```

### Retry Failed Notifications

```http
POST /notifications/retry?limit=100
```

## Integration with Alert System

The notification service integrates seamlessly with the existing alert system:

```python
# Enhanced alert service with notifications
alert_service = AlertService(alert_repository, session)

# Create alert with automatic notifications
await alert_service.create_alert(
    sensor_id=1,
    metric="temperature",
    value=85.5,
    threshold=80.0,
    send_notifications=True,
    notification_recipients=["admin@example.com", "+256700000000"],
    notification_types=[NotificationType.EMAIL, NotificationType.SMS]
)
```

## Database Schema

The notification table includes:

- **Basic Info**: ID, type, recipient, subject, message
- **Status Tracking**: Status, retry count, max retries
- **Timestamps**: Created, sent, delivered, failed
- **Error Handling**: Error messages and failure tracking
- **Context**: Template data and related entity IDs
- **Priority**: Low, medium, high, urgent

## Error Handling and Retry Logic

- **Automatic Retries**: Failed notifications are automatically retried up to 3 times
- **Exponential Backoff**: Retry delays increase with each attempt
- **Error Logging**: Comprehensive error tracking and logging
- **Manual Retry**: API endpoint to manually retry failed notifications
- **Status Tracking**: Real-time status updates for all notifications

## Testing

Run the notification service tests:

```bash
cd backend
python -m pytest tests/services/test_notification_service.py -v
```

## Dependencies

The notification service requires the following additional packages:

- `aiosmtplib>=2.0.0` - Async SMTP client
- `jinja2>=3.1.0` - Template engine
- `twilio>=8.10.0` - SMS service provider
- `python-multipart>=0.0.6` - Multipart form support

## Usage Examples

### Send Welcome Email

```python
notification_service = NotificationService(session)

await notification_service.send_email_notification(
    to_email="newuser@example.com",
    subject="Welcome to LifeLine-ICT",
    template_name="welcome",
    context={
        "user_name": "Jane Doe",
        "user_email": "newuser@example.com",
        "registration_date": "2024-01-15"
    }
)
```

### Send Alert SMS

```python
await notification_service.send_sms_notification(
    to_number="+256700000000",
    template_name="alert_notification",
    context={
        "alert_type": "Temperature Alert",
        "severity": "HIGH",
        "location": "Building A",
        "description": "Temperature exceeded 80°C"
    },
    priority=NotificationPriority.HIGH
)
```

### Send Bulk Notifications

```python
requests = [
    NotificationRequest(
        notification_type=NotificationType.EMAIL,
        recipient="admin@example.com",
        template_name="maintenance_reminder",
        context_data={"resource_name": "Server A", "scheduled_date": "2024-01-20"}
    ),
    NotificationRequest(
        notification_type=NotificationType.SMS,
        recipient="+256700000000",
        template_name="maintenance_reminder",
        context_data={"resource_name": "Server A", "scheduled_date": "2024-01-20"}
    )
]

notifications = await notification_service.send_bulk_notifications(requests)
```

## Monitoring and Maintenance

- **Health Checks**: Use `/notifications/test` endpoint to verify service connectivity
- **Statistics**: Monitor notification delivery rates and failure patterns
- **Retry Management**: Regularly retry failed notifications
- **Template Updates**: Update templates as needed for different notification types

## Security Considerations

- **SMTP Credentials**: Use app-specific passwords for email services
- **Twilio Tokens**: Secure storage of Twilio authentication tokens
- **Phone Number Validation**: Proper validation of phone number formats
- **Email Validation**: Email address validation before sending
- **Rate Limiting**: Consider implementing rate limiting for notification endpoints

## Future Enhancements

- **Webhook Support**: Add webhook notifications for real-time updates
- **Push Notifications**: Mobile push notification support
- **Advanced Templates**: Rich HTML templates with images and styling
- **Notification Preferences**: User-configurable notification preferences
- **Delivery Confirmations**: Enhanced delivery status tracking
- **Analytics Dashboard**: Web interface for notification analytics
