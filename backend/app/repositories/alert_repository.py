
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.alert import Alert
from .base import AsyncRepository


class AlertRepository(AsyncRepository[Alert]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Alert)

    async def get_alerts_by_sensor_id(self, sensor_id: int) -> AsyncIterator[Alert]:
        result = await self._session.execute(
            select(self._model).where(self._model.sensor_id == sensor_id)
        )
        return result.scalars().all()
