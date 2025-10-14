"""
SQLAlchemy ORM models representing LifeLine-ICT domain entities.

The models defined in this package reflect the data contracts shared by campus
ICT departments, research coordinators, and IoT operators. Enumerations and
mixins live alongside the models so they can be imported consistently across
repositories, services, and schema definitions.
"""

from .enums import LifecycleState, ProjectStatus, TicketSeverity, TicketStatus
from .location import Location
from .maintenance_ticket import MaintenanceTicket
from .project import Project
from .sensor_site import SensorSite
from .timestamp_mixin import TimestampMixin
from .ict_resource import ICTResource

__all__ = [
    "LifecycleState",
    "Project",
    "ProjectStatus",
    "ICTResource",
    "Location",
    "MaintenanceTicket",
    "SensorSite",
    "TicketSeverity",
    "TicketStatus",
    "TimestampMixin",
]
