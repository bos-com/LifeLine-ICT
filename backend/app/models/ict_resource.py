"""SQLAlchemy model describing ICT resources/assets."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .enums import LifecycleState
from .timestamp_mixin import TimestampMixin


class ICTResource(TimestampMixin, Base):
    """
    Represent a tangible or virtual ICT asset.

    Resources include servers, network devices, software licences, and cloud
    subscriptions tied to LifeLine-ICT projects. Linking resources to locations
    and maintenance tickets streamlines support operations.
    """

    __tablename__ = "ict_resources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Official resource name used in inventory reports.",
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Category label (e.g., 'network', 'sensor', 'software').",
    )
    lifecycle_state: Mapped[LifecycleState] = mapped_column(
        Enum(LifecycleState, name="resource_lifecycle_state"),
        nullable=False,
        default=LifecycleState.DRAFT,
        doc="Lifecycle phase of the asset.",
    )
    serial_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        doc="Manufacturer or institutional serial number.",
    )
    procurement_date: Mapped[Optional[date]] = mapped_column(
        nullable=True,
        doc="Date the resource was procured or commissioned.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Supplementary description for technicians.",
    )
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        doc="Optional reference to the parent project.",
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        doc="Physical or virtual location identifier.",
    )

    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="resources",
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="resources",
    )
    maintenance_tickets: Mapped[List["MaintenanceTicket"]] = relationship(
        "MaintenanceTicket",
        back_populates="resource",
        cascade="all, delete-orphan",
    )
    sensor_sites: Mapped[List["SensorSite"]] = relationship(
        "SensorSite",
        back_populates="resource",
        cascade="all, delete-orphan",
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="resource",
        cascade="all, delete-orphan",
        doc="Documents associated with this ICT resource.",
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """Representation for logging and debugging."""

        return (
            "<ICTResource id={0.id} name={0.name!r} state={0.lifecycle_state}>"
        ).format(self)
