"""SQLAlchemy model representing LifeLine-ICT projects."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import CheckConstraint, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .enums import ProjectStatus
from .timestamp_mixin import TimestampMixin


class Project(TimestampMixin, Base):
    """
    Capture ICT projects overseen by the university.

    Projects group together assets, deployments, and maintenance activities.
    Each project must provide a contact email so that field technicians and
    student volunteers know whom to reach for clarifications.
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        doc="Human friendly project name.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed narrative about the project's objectives.",
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.PLANNED,
        doc="Lifecycle stage of the project.",
    )
    sponsor: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Funding agency or department sponsoring the initiative.",
    )
    start_date: Mapped[Optional[date]] = mapped_column(
        nullable=True,
        doc="Date when the project activities begin.",
    )
    end_date: Mapped[Optional[date]] = mapped_column(
        nullable=True,
        doc="Date when the project formally concludes.",
    )
    primary_contact_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Primary email for project coordination.",
    )

    resources: Mapped[List["ICTResource"]] = relationship(
        "ICTResource",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    sensor_sites: Mapped[List["SensorSite"]] = relationship(
        "SensorSite",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan",
        doc="Documents associated with this project.",
    )

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="ck_project_dates_valid",
        ),
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """Representation for logging and debugging."""

        return f"<Project id={self.id} name={self.name!r} status={self.status}>"
