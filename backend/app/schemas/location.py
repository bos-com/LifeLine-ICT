"""Pydantic schemas for location entities."""

from __future__ import annotations

from typing import Optional

from pydantic import Field, validator
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape

from .base import BaseSchema


class PointSchema(BaseSchema):
    """Schema for representing a point geometry."""

    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


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
    geom: Optional[PointSchema] = Field(
        default=None,
        description="Geographic coordinates.",
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
    geom: Optional[PointSchema] = Field(
        default=None,
        description="Geographic coordinates.",
    )


class LocationRead(LocationBase):
    """Representation returned by the API."""

    id: int = Field(..., description="Unique identifier.")

    @validator("geom", pre=True)
    def translate_geom(cls, v):
        if isinstance(v, WKBElement):
            shape = to_shape(v)
            return {"lat": shape.y, "lon": shape.x}
        return v
