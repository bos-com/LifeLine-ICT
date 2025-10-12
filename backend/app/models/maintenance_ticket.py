"""SQLAlchemy model representing maintenance tickets."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .enums import TicketSeverity, TicketStatus
from .timestamp_mixin import TimestampMixin


class MaintenanceTicket(TimestampMixin, Base):
    """
    Record maintenance interventions and support requests.

    Tickets bridge operational support activities with the asset inventory,
    allowing teams to review lifecycle histories during audits.
    """

    __tablename__ = "maintenance_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("ict_resources.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key referencing the affected ICT resource.",
    )
    reported_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Name or email of the reporter.",
    )
    issue_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Concise description of the reported issue.",
    )
    severity: Mapped[TicketSeverity] = mapped_column(
        Enum(TicketSeverity, name="ticket_severity"),
        nullable=False,
        default=TicketSeverity.MEDIUM,
        doc="Operational severity assigned by the help-desk.",
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status"),
        nullable=False,
        default=TicketStatus.OPEN,
        doc="Current state of the ticket workflow.",
    )
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when the issue was first reported.",
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when the ticket was formally closed.",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Additional notes or resolution details.",
    )

    resource: Mapped["ICTResource"] = relationship(
        "ICTResource",
        back_populates="maintenance_tickets",
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="maintenance_ticket",
        cascade="all, delete-orphan",
        doc="Documents associated with this maintenance ticket.",
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """Representation for logging and debugging."""

        return (
            "<MaintenanceTicket id={0.id} resource_id={0.resource_id} "
            "status={0.status}>"
        ).format(self)
