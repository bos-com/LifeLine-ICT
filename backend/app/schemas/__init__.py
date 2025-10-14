"""
Pydantic schemas for request validation and response serialization.

The schemas mirror the ORM models while providing validation metadata that
feeds directly into FastAPI's generated OpenAPI documentation.
"""

from .base import (
    BaseSchema,
    PaginatedResponse,
    PaginationMeta,
    PaginationQuery,
)
from .ict_resource import ResourceCreate, ResourceRead, ResourceUpdate
from .location import LocationCreate, LocationRead, LocationUpdate
from .maintenance_ticket import TicketCreate, TicketRead, TicketUpdate
from .project import ProjectCreate, ProjectRead, ProjectUpdate
from .sensor_site import SensorSiteCreate, SensorSiteRead, SensorSiteUpdate

__all__ = [
    "BaseSchema",
    "PaginatedResponse",
    "PaginationMeta",
    "PaginationQuery",
    "ResourceCreate",
    "ResourceRead",
    "ResourceUpdate",
    "LocationCreate",
    "LocationRead",
    "LocationUpdate",
    "TicketCreate",
    "TicketRead",
    "TicketUpdate",
    "ProjectCreate",
    "ProjectRead",
    "ProjectUpdate",
    "SensorSiteCreate",
    "SensorSiteRead",
    "SensorSiteUpdate",
]
