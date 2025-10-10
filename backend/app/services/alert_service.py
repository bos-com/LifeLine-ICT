
from __future__ import annotations

from ..models.alert import Alert
from ..repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, alert_repository: AlertRepository):
        self._alert_repository = alert_repository

    async def create_alert(self, sensor_id: int, metric: str, value: float, threshold: float) -> Alert | None:
        if value > threshold:
            alert = Alert(
                sensor_id=sensor_id,
                metric=metric,
                value=value,
                threshold=threshold,
            )
            return await self._alert_repository.create(alert)
        return None

    async def get_alerts_by_sensor_id(self, sensor_id: int) -> list[Alert]:
        return await self._alert_repository.get_alerts_by_sensor_id(sensor_id)
