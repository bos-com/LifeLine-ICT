from pydantic import BaseModel
from typing import Optional

# ===========================
# Project Model
# ===========================
class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    owner: str
    status: str  # e.g. "active", "pending", "completed"

# ===========================
# ICT Resource Model
# ===========================
class ICTResource(BaseModel):
    id: Optional[int] = None
    name: str
    type: str       # e.g. "Server", "Router", "Laptop"
    location: str
    available: bool
