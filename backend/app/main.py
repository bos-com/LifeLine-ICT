"""
Entry point for the LifeLine-ICT FastAPI application.

The application factory centralises configuration, router registration, and
exception handling. Using a factory enables future test suites and scripts to
instantiate isolated application instances while injecting database overrides.
"""

from fastapi import FastAPI

from .core.config import settings
from .core.logging import configure_logging
from .api import (
    errors,
    document_router,
    locations_router,
    maintenance_tickets_router,
    notification_router,
    projects_router,
    resources_router,
    sensor_sites_router,
    analytics_router,
    alert_router,
    auth_router,
)


def create_app() -> FastAPI:
    """
    Create and configure a FastAPI application instance.

    Returns
    -------
    FastAPI
        An application primed with global metadata and ready for router
        inclusion. Routers live under ``app.api`` and are registered during the
        bootstrapping phase inside this function once they are implemented.
    """

    configure_logging()

    app = FastAPI(
        title="LifeLine ICT Backend",
        description=(
            "CRUD APIs that manage campus ICT projects, assets, and support "
            "workflows for the Uganda University ICT initiative."
        ),
        version=settings.api_version,
        contact={
            "name": "LifeLine-ICT Core Team",
            "email": settings.contact_email,
        },
        license_info={
            "name": "MIT License",
            "identifier": "MIT",
        },
    )

    errors.register_exception_handlers(app)

    app.include_router(projects_router)
    app.include_router(resources_router)
    app.include_router(locations_router)
    app.include_router(maintenance_tickets_router)
    app.include_router(notification_router)
    app.include_router(sensor_sites_router)
    app.include_router(analytics_router)
    app.include_router(alert_router)
    app.include_router(auth_router)
    app.include_router(document_router)

    @app.get("/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        """
        Provide a basic health indicator confirming application availability.

        Returns
        -------
        dict[str, str]
            JSON payload with a static status. The endpoint is intentionally
            lightweight to support campus monitoring systems and classroom
            demonstrations.
        """

        return {"status": "ok"}

    return app


app = create_app()
