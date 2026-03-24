"""Pydantic schemas for ICT resource entities."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import Field

from ..models import LifecycleState
from .base import BaseSchema


class ResourceBase(BaseSchema):
    """Common attributes for ICT resources."""

    name: str = Field(
        ...,
        max_length=255,
        description="Inventory-friendly resource name.",
    )
    category: str = Field(
        ...,
        max_length=100,
        description="Category label (e.g., 'network', 'sensor').",
    )
    lifecycle_state: LifecycleState = Field(
        default=LifecycleState.DRAFT,
        description="Lifecycle phase of the asset.",
    )
    serial_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Manufacturer or institutional serial number.",
    )
    procurement_date: Optional[date] = Field(
        default=None,
        description="Date the asset was procured.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Additional notes useful for technicians.",
    )
    project_id: Optional[int] = Field(
        default=None,
        description="Optional project association.",
    )
    location_id: Optional[int] = Field(
        default=None,
        description="Optional location association.",
    )


class ResourceCreate(ResourceBase):
    """Payload for creating a resource."""

    pass


class ResourceUpdate(BaseSchema):
    """Payload for partially updating a resource."""

    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Inventory-friendly resource name.",
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Category label (e.g., 'network', 'sensor').",
    )
    lifecycle_state: Optional[LifecycleState] = Field(
        default=None,
        description="Lifecycle phase of the asset.",
    )
    serial_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Manufacturer or institutional serial number.",
    )
    procurement_date: Optional[date] = Field(
        default=None,
        description="Date the asset was procured.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Additional notes useful for technicians.",
    )
    project_id: Optional[int] = Field(
        default=None,
        description="Optional project association.",
    )
    location_id: Optional[int] = Field(
        default=None,
        description="Optional location association.",
    )


class ResourceRead(ResourceBase):
    """Representation returned by the API."""

    id: int = Field(..., description="Unique identifier.")
