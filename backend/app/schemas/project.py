"""Pydantic schemas for project entities."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import EmailStr, Field

from ..models import ProjectStatus
from .base import BaseSchema


class ProjectBase(BaseSchema):
    """Common attributes shared by create and update operations."""

    name: str = Field(
        ...,
        max_length=255,
        description="Unique project name.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed narrative about the initiative.",
    )
    status: ProjectStatus = Field(
        default=ProjectStatus.PLANNED,
        description="Lifecycle stage of the project.",
    )
    sponsor: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Funding agency or sponsoring department.",
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Date when the project activities begin.",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Date when the project ends.",
    )
    primary_contact_email: EmailStr = Field(
        ...,
        description="Primary coordination contact.",
    )


class ProjectCreate(ProjectBase):
    """Payload for creating a project."""

    pass


class ProjectUpdate(BaseSchema):
    """Payload for partially updating a project."""

    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Unique project name.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed narrative about the initiative.",
    )
    status: Optional[ProjectStatus] = Field(
        default=None,
        description="Lifecycle stage of the project.",
    )
    sponsor: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Funding agency or sponsoring department.",
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Date when the project activities begin.",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Date when the project ends.",
    )
    primary_contact_email: Optional[EmailStr] = Field(
        default=None,
        description="Primary coordination contact.",
    )


class ProjectRead(ProjectBase):
    """Representation returned by the API."""

    id: int = Field(..., description="Unique identifier.")
