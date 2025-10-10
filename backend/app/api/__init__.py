"""
API routers and dependency declarations for the LifeLine-ICT backend.

Routers are grouped by domain entity to keep endpoints organised and to make it
easy for faculties to locate relevant operations during demos.
"""

from . import errors
from .locations import router as locations_router
from .maintenance_tickets import router as maintenance_tickets_router
from .projects import router as projects_router
from .resources import router as resources_router
from .sensor_sites import router as sensor_sites_router

__all__ = [
    "errors",
    "locations_router",
    "maintenance_tickets_router",
    "projects_router",
    "resources_router",
    "sensor_sites_router",
]
