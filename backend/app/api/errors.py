"""Exception handler registration for FastAPI."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..services import NotFoundError, ServiceError, ValidationError


def register_exception_handlers(app: FastAPI) -> None:
    """
    Configure exception handlers for custom service errors.
    """

    @app.exception_handler(NotFoundError)
    async def handle_not_found(
        request: Request,  # noqa: ARG001
        exc: NotFoundError,
    ) -> JSONResponse:
        """Return a 404 response when an entity is missing."""

        return JSONResponse(
            status_code=404,
            content={"detail": str(exc), "code": "RESOURCE_NOT_FOUND"},
        )

    @app.exception_handler(ValidationError)
    async def handle_validation(
        request: Request,  # noqa: ARG001
        exc: ValidationError,
    ) -> JSONResponse:
        """Return a 400 response when validation fails."""

        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "code": "VALIDATION_ERROR"},
        )

    @app.exception_handler(ServiceError)
    async def handle_service_error(
        request: Request,  # noqa: ARG001
        exc: ServiceError,
    ) -> JSONResponse:
        """Return a generic 500 response for unexpected service errors."""

        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "code": "SERVICE_ERROR"},
        )
