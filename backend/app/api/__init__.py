"""
API routers and dependency declarations for the LifeLine-ICT backend.

Routers are grouped by domain entity to keep endpoints organised and to make it
easy for faculties to locate relevant operations during demos.
"""

from . import errors
from .locations import router as locations_router
from .maintenance_tickets import router as maintenance_tickets_router
from .notification_router import router as notification_router
from .projects import router as projects_router
from .resources import router as resources_router
from .sensor_sites import router as sensor_sites_router
from .analytics import router as analytics_router
from .alert_router import router as alert_router
from .auth_router import router as auth_router

__all__ = [
    "errors",
    "locations_router",
    "maintenance_tickets_router",
    "notification_router",
    "projects_router",
    "resources_router",
    "sensor_sites_router",
    "analytics_router",
    "alert_router",
    "auth_router",
]
