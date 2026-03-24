"""
Repository abstractions encapsulating database CRUD operations.

Each repository exposes async helpers tailored to a domain entity, keeping the
service layer focused on higher-order business rules.
"""

from .base import AsyncRepository
from .location_repository import LocationRepository
from .maintenance_ticket_repository import MaintenanceTicketRepository
from .project_repository import ProjectRepository
from .resource_repository import ResourceRepository
from .sensor_site_repository import SensorSiteRepository

__all__ = [
    "AsyncRepository",
    "LocationRepository",
    "MaintenanceTicketRepository",
    "ProjectRepository",
    "ResourceRepository",
    "SensorSiteRepository",
]
