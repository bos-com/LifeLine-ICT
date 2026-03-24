"""Custom service-layer exceptions."""


class ServiceError(Exception):
    """Base class for service-layer exceptions."""


class NotFoundError(ServiceError):
    """Raised when an entity could not be found."""


class ValidationError(ServiceError):
    """Raised when a service-level validation rule fails."""
