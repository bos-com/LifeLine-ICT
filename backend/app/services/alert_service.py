
from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.alert import Alert
from ..models.notification import NotificationType, NotificationPriority
from ..repositories.alert_repository import AlertRepository
from ..schemas.alert import AlertRead
from .notification_service import NotificationService

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, alert_repository: AlertRepository, session: Optional[AsyncSession] = None):
        self._alert_repository = alert_repository
        self._session = session
        self._notification_service = None
        if session:
            self._notification_service = NotificationService(session)

    async def create_alert(
        self, 
        sensor_id: int, 
        metric: str, 
        value: float, 
        threshold: float,
        send_notifications: bool = True,
        notification_recipients: Optional[List[str]] = None,
        notification_types: Optional[List[NotificationType]] = None
    ) -> AlertRead | None:
        """
        Create an alert and optionally send notifications.
        
        Args:
            sensor_id: ID of the sensor that triggered the alert
            metric: Name of the metric that exceeded threshold
            value: Current value of the metric
            threshold: Threshold value that was exceeded
            send_notifications: Whether to send notifications for this alert
            notification_recipients: List of email addresses/phone numbers to notify
            notification_types: Types of notifications to send (email, SMS)
        """
        if value > threshold:
            alert = Alert(
                sensor_id=sensor_id,
                metric=metric,
                value=value,
                threshold=threshold,
            )
            created_alert = await self._alert_repository.create(alert)
            alert_read = AlertRead.from_orm(created_alert)
            
            # Send notifications if requested
            if send_notifications and self._notification_service:
                try:
                    await self._send_alert_notifications(
                        alert_read,
                        notification_recipients or [],
                        notification_types or [NotificationType.EMAIL]
                    )
                except Exception as e:
                    logger.error(f"Failed to send alert notifications: {str(e)}")
            
            return alert_read
        return None

    async def get_alerts_by_sensor_id(self, sensor_id: int) -> list[AlertRead]:
        alerts = await self._alert_repository.get_alerts_by_sensor_id(sensor_id)
        return [AlertRead.from_orm(alert) for alert in alerts]

    async def _send_alert_notifications(
        self,
        alert: AlertRead,
        recipients: List[str],
        notification_types: List[NotificationType]
    ) -> None:
        """Send notifications for an alert."""
        if not recipients or not notification_types:
            logger.warning("No recipients or notification types specified for alert notifications")
            return

        alert_data = {
            'alert_id': alert.id,
            'type': f"{alert.metric} Alert",
            'severity': self._determine_alert_severity(alert.value, alert.threshold),
            'location': f"Sensor {alert.sensor_id}",  # Could be enhanced with actual location
            'alert_time': alert.created_at.isoformat(),
            'description': f"{alert.metric} value {alert.value} exceeded threshold {alert.threshold}",
            'metric': alert.metric,
            'value': alert.value,
            'threshold': alert.threshold,
            'sensor_id': alert.sensor_id
        }

        await self._notification_service.send_alert_notification(
            alert_data=alert_data,
            recipients=recipients,
            notification_types=notification_types
        )

    def _determine_alert_severity(self, value: float, threshold: float) -> str:
        """Determine alert severity based on how much the threshold was exceeded."""
        ratio = value / threshold if threshold > 0 else 0
        
        if ratio >= 2.0:
            return "CRITICAL"
        elif ratio >= 1.5:
            return "HIGH"
        elif ratio >= 1.2:
            return "MEDIUM"
        else:
            return "LOW"
