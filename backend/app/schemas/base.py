"""Shared Pydantic schema utilities."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


class BaseSchema(BaseModel):
    """Base schema that enables ORM compatibility."""

    class Config:
        orm_mode = True


class PaginationQuery(BaseModel):
    """
    Standard pagination query parameters.

    Attributes
    ----------
    limit:
        Number of items to return. Defaults to the configured service value.
    offset:
        Starting index of the page.
    search:
        Optional free-text search term applied to select fields.
    """

    limit: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of items to return.",
    )
    offset: Optional[int] = Field(
        default=None,
        ge=0,
        description="Zero-based offset from which to return items.",
    )
    search: Optional[str] = Field(
        default=None,
        description="Case-insensitive free-text search phrase.",
    )


class PaginationMeta(BaseModel):
    """Metadata describing a paginated result set."""

    total: int = Field(..., ge=0, description="Total number of matching items.")
    limit: int = Field(..., ge=1, description="Page size returned.")
    offset: int = Field(..., ge=0, description="Zero-based offset that produced the page.")


T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    """
    Envelope for paginated API responses.

    Parameters
    ----------
    data:
        List of items returned.
    pagination:
        Metadata describing pagination state.
    """

    data: List[T]
    pagination: PaginationMeta
