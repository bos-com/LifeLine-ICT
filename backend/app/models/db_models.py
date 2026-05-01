from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    owner = Column(String)
    status = Column(String)


class ICTResource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    location = Column(String)
    available = Column(Boolean, default=True)
