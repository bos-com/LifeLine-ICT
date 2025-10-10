"""Pydantic schemas for location entities."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .base import BaseSchema


class LocationBase(BaseSchema):
    """Common attributes for location operations."""

    campus: str = Field(
        ...,
        max_length=120,
        description="Campus or regional site name.",
    )
    building: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Building or facility name.",
    )
    room: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Room or rack identifier.",
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees.",
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees.",
    )


class LocationCreate(LocationBase):
    """Payload for creating a location."""

    pass


class LocationUpdate(BaseSchema):
    """Payload for partially updating a location."""

    campus: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Campus or regional site name.",
    )
    building: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Building or facility name.",
    )
    room: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Room or rack identifier.",
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees.",
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees.",
    )


class LocationRead(LocationBase):
    """Representation returned by the API."""

    id: int = Field(..., description="Unique identifier.")
