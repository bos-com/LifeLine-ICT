"""SQLAlchemy model linking IoT deployment sites to ICT assets."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .timestamp_mixin import TimestampMixin


class SensorSite(TimestampMixin, Base):
    """
    Anchor IoT sensor deployments to resources and projects.

    The model supplements the Arduino and logging components by recording where
    data originates, enabling administrators to cross-reference field equipment
    with institutional records.
    """

    __tablename__ = "sensor_sites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("ict_resources.id", ondelete="CASCADE"),
        nullable=False,
        doc="ICT resource powering or hosting the sensor.",
    )
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        doc="Project that the sensor deployment contributes to.",
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        doc="Optional link to a dedicated location record.",
    )
    data_collection_endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="URL or identifier for the data ingestion endpoint.",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Operational notes such as maintenance instructions.",
    )

    resource: Mapped["ICTResource"] = relationship(
        "ICTResource",
        back_populates="sensor_sites",
    )
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="sensor_sites",
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="sensor_sites",
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """Representation for logging and debugging."""

        return (
            "<SensorSite id={0.id} resource_id={0.resource_id} "
            "endpoint={0.data_collection_endpoint!r}>"
        ).format(self)
