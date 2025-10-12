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
from .document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentRead,
    DocumentSummary,
    DocumentUploadResponse,
    DocumentDownloadResponse,
    DocumentSearchQuery,
    DocumentStats,
)
from .ict_resource import ResourceCreate, ResourceRead, ResourceUpdate
from .location import LocationCreate, LocationRead, LocationUpdate
from .maintenance_ticket import TicketCreate, TicketRead, TicketUpdate
from .notification import (
    NotificationBase,
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
    NotificationTemplate,
    NotificationRequest,
    NotificationStats,
)
from .project import ProjectCreate, ProjectRead, ProjectUpdate
from .sensor_site import SensorSiteCreate, SensorSiteRead, SensorSiteUpdate

__all__ = [
    "BaseSchema",
    "PaginatedResponse",
    "PaginationMeta",
    "PaginationQuery",
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentRead",
    "DocumentSummary",
    "DocumentUploadResponse",
    "DocumentDownloadResponse",
    "DocumentSearchQuery",
    "DocumentStats",
    "ResourceCreate",
    "ResourceRead",
    "ResourceUpdate",
    "LocationCreate",
    "LocationRead",
    "LocationUpdate",
    "TicketCreate",
    "TicketRead",
    "TicketUpdate",
    "NotificationBase",
    "NotificationCreate",
    "NotificationRead",
    "NotificationUpdate",
    "NotificationTemplate",
    "NotificationRequest",
    "NotificationStats",
    "ProjectCreate",
    "ProjectRead",
    "ProjectUpdate",
    "SensorSiteCreate",
    "SensorSiteRead",
    "SensorSiteUpdate",
]
