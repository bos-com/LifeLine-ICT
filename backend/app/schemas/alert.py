
from __future__ import annotations

from datetime import datetime

from .base import BaseSchema


class AlertRead(BaseSchema):
    id: int
    sensor_id: int
    metric: str
    value: float
    threshold: float
    created_at: datetime
