
from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from backend.app.models.alert import Alert
from backend.app.repositories.alert_repository import AlertRepository
from backend.app.services.alert_service import AlertService


@pytest.fixture
def alert_repository() -> AlertRepository:
    return AsyncMock(spec=AlertRepository)


@pytest.mark.asyncio
async def test_create_alert_when_value_exceeds_threshold(
    alert_repository: AlertRepository,
) -> None:
    alert_service = AlertService(alert_repository)
    alert_repository.create.return_value = Alert(
        id=1,
        sensor_id=1,
        metric="temperature",
        value=30.0,
        threshold=25.0,
        timestamp=datetime.utcnow(),
    )

    alert = await alert_service.create_alert(
        sensor_id=1,
        metric="temperature",
        value=30.0,
        threshold=25.0,
    )

    assert alert is not None
    alert_repository.create.assert_called_once()
    assert alert.sensor_id == 1
    assert alert.metric == "temperature"
    assert alert.value == 30.0
    assert alert.threshold == 25.0


@pytest.mark.asyncio
async def test_create_alert_when_value_does_not_exceed_threshold(
    alert_repository: AlertRepository,
) -> None:
    alert_service = AlertService(alert_repository)
    alert = await alert_service.create_alert(
        sensor_id=1,
        metric="temperature",
        value=20.0,
        threshold=25.0,
    )

    assert alert is None
    alert_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_alerts_by_sensor_id(alert_repository: AlertRepository) -> None:
    alert_service = AlertService(alert_repository)
    alerts = [
        Alert(
            id=1,
            sensor_id=1,
            metric="temperature",
            value=30.0,
            threshold=25.0,
            timestamp=datetime.utcnow(),
        ),
        Alert(
            id=2,
            sensor_id=1,
            metric="humidity",
            value=80.0,
            threshold=70.0,
            timestamp=datetime.utcnow(),
        ),
    ]
    alert_repository.get_alerts_by_sensor_id.return_value = alerts

    result = await alert_service.get_alerts_by_sensor_id(1)

    assert len(result) == 2
    assert result[0].metric == "temperature"
    assert result[1].metric == "humidity"
    alert_repository.get_alerts_by_sensor_id.assert_called_once_with(1)
