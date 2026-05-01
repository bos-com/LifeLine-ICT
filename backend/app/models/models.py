from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 🧩 Project Model
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    owner = Column(String(100))
    status = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 🧩 ICT Resource Model
class ICTResource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))
    location = Column(String(255))
    status = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
