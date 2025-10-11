
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..models.alert import Alert
from ..repositories.alert_repository import AlertRepository
from ..services.alert_service import AlertService

from ..models.user import User
from .deps import get_current_user

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Alerts"],
    dependencies=[Depends(get_current_user)],
)


def get_alert_service(session: AsyncSession = Depends(get_session)) -> AlertService:
    alert_repository = AlertRepository(session)
    return AlertService(alert_repository)


@router.post("", response_model=Alert)
async def create_alert(
    sensor_id: int,
    metric: str,
    value: float,
    threshold: float,
    alert_service: AlertService = Depends(get_alert_service),
) -> Alert | None:
    return await alert_service.create_alert(sensor_id, metric, value, threshold)


@router.get("/{sensor_id}", response_model=list[Alert])
async def get_alerts_by_sensor_id(
    sensor_id: int, alert_service: AlertService = Depends(get_alert_service)
) -> list[Alert]:
    return await alert_service.get_alerts_by_sensor_id(sensor_id)
