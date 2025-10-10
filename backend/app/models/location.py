"""SQLAlchemy model capturing campus or field locations."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .timestamp_mixin import TimestampMixin


class Location(TimestampMixin, Base):
    """
    Describe physical or logical locations for ICT assets.

    Locations may represent computer labs, comms rooms, or remote sensor sites.
    Capturing coordinates assists mapping efforts led by the GIS module.
    """

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campus: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        doc="Campus or regional site (e.g., 'Kampala Main').",
    )
    building: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
        doc="Named building or facility.",
    )
    room: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Room or rack identifier within the building.",
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Latitude in decimal degrees for GIS overlays.",
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Longitude in decimal degrees for GIS overlays.",
    )

    resources: Mapped[List["ICTResource"]] = relationship(
        "ICTResource",
        back_populates="location",
    )
    sensor_sites: Mapped[List["SensorSite"]] = relationship(
        "SensorSite",
        back_populates="location",
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """Representation for logging and debugging."""

        return (
            "<Location id={0.id} campus={0.campus!r} building={0.building!r}>"
        ).format(self)
