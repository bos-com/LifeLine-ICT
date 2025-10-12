"""Reusable mixin that adds timestamp metadata to entities."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Attach created/updated timestamp columns to an ORM model.

    The timestamps use UTC so that cross-campus deployments stay consistent,
    especially when comparing IoT sensor activity to administrative actions.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="UTC timestamp describing when the record was created.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="UTC timestamp describing when the record was last updated.",
    )
