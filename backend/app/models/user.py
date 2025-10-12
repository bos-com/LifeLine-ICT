
from __future__ import annotations

from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    This model represents users who can access the LifeLine-ICT system
    and upload documents. It includes relationships to track uploaded
    documents and user activity.
    """
    
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    
    uploaded_documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="uploaded_by_user",
        cascade="all, delete-orphan",
        doc="Documents uploaded by this user.",
    )
