from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# -------------------------------
# PROJECT SCHEMAS
# -------------------------------

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = "active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -------------------------------
# ICT RESOURCE SCHEMAS
# -------------------------------

class ResourceBase(BaseModel):
    name: str
    type: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "available"

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(ResourceBase):
    pass

class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
