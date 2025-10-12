"""Custom service-layer exceptions."""


class ServiceError(Exception):
    """Base class for service-layer exceptions."""


class NotFoundError(ServiceError):
    """Raised when an entity could not be found."""


class ValidationError(ServiceError):
    """Raised when a service-level validation rule fails."""


class FileValidationError(ServiceError):
    """Raised when file validation fails."""


class FileNotFoundError(ServiceError):
    """Raised when a file is not found."""


class StorageError(ServiceError):
    """Raised when file storage operations fail."""


class DocumentNotFoundError(NotFoundError):
    """Raised when a document could not be found."""


class QuarantineError(ServiceError):
    """Raised when file quarantine operations fail."""
