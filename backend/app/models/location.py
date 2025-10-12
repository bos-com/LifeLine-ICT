"""SQLAlchemy model capturing campus or field locations."""

from __future__ import annotations

from typing import List, Optional

from geoalchemy2 import Geometry
from sqlalchemy import String
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
    geom: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
        doc="Geographic coordinates (Point) for GIS overlays.",
    )

    resources: Mapped[List["ICTResource"]] = relationship(
        "ICTResource",
        back_populates="location",
    )
    sensor_sites: Mapped[List["SensorSite"]] = relationship(
        "SensorSite",
        back_populates="location",
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="location",
        cascade="all, delete-orphan",
        doc="Documents associated with this location.",
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """Representation for logging and debugging."""

        return (
            "<Location id={0.id} campus={0.campus!r} building={0.building!r}>"
        ).format(self)
