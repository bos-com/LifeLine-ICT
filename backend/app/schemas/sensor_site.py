"""Pydantic schemas for sensor site entities."""

from __future__ import annotations

from typing import Optional

from pydantic import AnyHttpUrl, Field

from .base import BaseSchema


class SensorSiteBase(BaseSchema):
    """Common attributes for sensor site operations."""

    resource_id: int = Field(
        ...,
        description="ICT resource powering the sensor.",
    )
    project_id: Optional[int] = Field(
        default=None,
        description="Optional project association.",
    )
    location_id: Optional[int] = Field(
        default=None,
        description="Optional location association.",
    )
    data_collection_endpoint: AnyHttpUrl = Field(
        ...,
        description="Endpoint receiving sensor data.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Operational notes for technicians.",
    )


class SensorSiteCreate(SensorSiteBase):
    """Payload for creating a sensor site."""

    pass


class SensorSiteUpdate(BaseSchema):
    """Payload for partially updating a sensor site."""

    project_id: Optional[int] = Field(
        default=None,
        description="Optional project association.",
    )
    location_id: Optional[int] = Field(
        default=None,
        description="Optional location association.",
    )
    data_collection_endpoint: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Endpoint receiving sensor data.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Operational notes for technicians.",
    )


class SensorSiteRead(SensorSiteBase):
    """Representation returned by the API."""

    id: int = Field(..., description="Unique identifier.")
