"""
LifeLine-ICT backend application package.

This module intentionally exposes the application factory to keep imports
concise throughout the codebase. The backend follows a layered architecture
documented in ``docs/backend_crud_plan.md`` where API routers, services,
repositories, and models are separated to match the university's governance
expectations.
"""

from .main import create_app

__all__ = ["create_app"]
