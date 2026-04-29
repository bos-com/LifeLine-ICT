"""Role-Based Access Control (RBAC) utilities."""

from __future__ import annotations

from functools import wraps
from fastapi import HTTPException, status, Depends