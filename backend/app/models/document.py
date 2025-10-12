"""
SQLAlchemy model representing uploaded documents and files.

This model captures file metadata and relationships to other entities in the
LifeLine-ICT system. Documents can be attached to projects, resources, maintenance
tickets, locations, or sensor sites to provide supporting documentation, photos,
reports, and other relevant files.

The model includes comprehensive metadata tracking, security features, and
relationship management to support the university's document management needs.
"""

from __future__ import annotations

import os
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from .timestamp_mixin import TimestampMixin


class DocumentType(str, Enum):
    """
    Enumeration of supported document types for the LifeLine-ICT system.
    
    This enum defines the categories of documents that can be uploaded,
    helping with organization, validation, and appropriate handling of
    different file types across the university's ICT infrastructure.
    """
    
    # Project-related documents
    PROJECT_PROPOSAL = "project_proposal"
    PROJECT_REPORT = "project_report"
    PROJECT_PRESENTATION = "project_presentation"
    PROJECT_PHOTO = "project_photo"
    
    # Resource-related documents
    MANUAL = "manual"
    WARRANTY = "warranty"
    CERTIFICATE = "certificate"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    SPECIFICATION = "specification"
    RESOURCE_PHOTO = "resource_photo"
    
    # Maintenance-related documents
    MAINTENANCE_REPORT = "maintenance_report"
    WORK_ORDER = "work_order"
    TROUBLESHOOTING_GUIDE = "troubleshooting_guide"
    MAINTENANCE_PHOTO = "maintenance_photo"
    
    # Location-related documents
    FLOOR_PLAN = "floor_plan"
    LOCATION_PHOTO = "location_photo"
    SITE_DOCUMENTATION = "site_documentation"
    
    # Sensor-related documents
    CALIBRATION_DATA = "calibration_data"
    INSTALLATION_PHOTO = "installation_photo"
    SENSOR_SPECIFICATION = "sensor_specification"
    
    # General documents
    GENERAL_DOCUMENT = "general_document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    IMAGE = "image"
    ARCHIVE = "archive"


class DocumentStatus(str, Enum):
    """
    Enumeration of document processing and availability statuses.
    
    Tracks the lifecycle of uploaded documents from initial upload through
    processing, validation, and potential issues that may require attention.
    """
    
    UPLOADING = "uploading"
    PROCESSING = "processing"
    AVAILABLE = "available"
    VALIDATION_FAILED = "validation_failed"
    CORRUPTED = "corrupted"
    QUARANTINED = "quarantined"
    DELETED = "deleted"


class Document(TimestampMixin, Base):
    """
    Represents an uploaded document or file in the LifeLine-ICT system.
    
    This model stores comprehensive metadata about uploaded files including
    file information, security details, relationships to other entities,
    and processing status. Documents can be attached to multiple entity
    types to support various use cases across the university's ICT operations.
    
    Attributes
    ----------
    id : int
        Primary key identifier for the document record.
    filename : str
        Original filename as uploaded by the user.
    original_filename : str
        Sanitized version of the filename for safe storage.
    file_path : str
        Relative path to the stored file within the configured storage directory.
    file_size : int
        Size of the file in bytes.
    mime_type : str
        MIME type of the uploaded file as detected by the system.
    file_extension : str
        File extension extracted from the original filename.
    document_type : DocumentType
        Categorized type of document for organizational purposes.
    status : DocumentStatus
        Current processing status of the document.
    description : str, optional
        User-provided description of the document's contents or purpose.
    tags : str, optional
        Comma-separated tags for additional categorization and searchability.
    checksum : str, optional
        Cryptographic hash of the file contents for integrity verification.
    is_public : bool
        Whether the document can be accessed without authentication.
    download_count : int
        Number of times the document has been downloaded.
    last_accessed_at : datetime, optional
        Timestamp of the most recent access to the document.
    
    Relationship Fields
    -------------------
    project_id : int, optional
        Foreign key to the associated project if applicable.
    resource_id : int, optional
        Foreign key to the associated ICT resource if applicable.
    maintenance_ticket_id : int, optional
        Foreign key to the associated maintenance ticket if applicable.
    location_id : int, optional
        Foreign key to the associated location if applicable.
    sensor_site_id : int, optional
        Foreign key to the associated sensor site if applicable.
    uploaded_by_user_id : int, optional
        Foreign key to the user who uploaded the document.
    
    Relationships
    ------------
    project : Project, optional
        Associated project if the document is project-related.
    resource : ICTResource, optional
        Associated ICT resource if the document is resource-related.
    maintenance_ticket : MaintenanceTicket, optional
        Associated maintenance ticket if the document is ticket-related.
    location : Location, optional
        Associated location if the document is location-related.
    sensor_site : SensorSite, optional
        Associated sensor site if the document is sensor-related.
    uploaded_by_user : User, optional
        User who uploaded the document.
    """
    
    __tablename__ = "documents"
    
    # Primary identifier
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key identifier for the document record."
    )
    
    # File information
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original filename as uploaded by the user."
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Sanitized version of the filename for safe storage."
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        doc="Relative path to the stored file within the configured storage directory."
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Size of the file in bytes."
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="MIME type of the uploaded file as detected by the system."
    )
    file_extension: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="File extension extracted from the original filename."
    )
    
    # Categorization and status
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, name="document_type"),
        nullable=False,
        default=DocumentType.GENERAL_DOCUMENT,
        doc="Categorized type of document for organizational purposes."
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus, name="document_status"),
        nullable=False,
        default=DocumentStatus.UPLOADING,
        doc="Current processing status of the document."
    )
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User-provided description of the document's contents or purpose."
    )
    tags: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Comma-separated tags for additional categorization and searchability."
    )
    checksum: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc="Cryptographic hash of the file contents for integrity verification."
    )
    
    # Access control and usage tracking
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether the document can be accessed without authentication."
    )
    download_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of times the document has been downloaded."
    )
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of the most recent access to the document."
    )
    
    # Relationship foreign keys
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        doc="Foreign key to the associated project if applicable."
    )
    resource_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("ict_resources.id", ondelete="SET NULL"),
        nullable=True,
        doc="Foreign key to the associated ICT resource if applicable."
    )
    maintenance_ticket_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("maintenance_tickets.id", ondelete="SET NULL"),
        nullable=True,
        doc="Foreign key to the associated maintenance ticket if applicable."
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        doc="Foreign key to the associated location if applicable."
    )
    sensor_site_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("sensor_sites.id", ondelete="SET NULL"),
        nullable=True,
        doc="Foreign key to the associated sensor site if applicable."
    )
    uploaded_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="Foreign key to the user who uploaded the document."
    )
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="documents",
        doc="Associated project if the document is project-related."
    )
    resource: Mapped[Optional["ICTResource"]] = relationship(
        "ICTResource",
        back_populates="documents",
        doc="Associated ICT resource if the document is resource-related."
    )
    maintenance_ticket: Mapped[Optional["MaintenanceTicket"]] = relationship(
        "MaintenanceTicket",
        back_populates="documents",
        doc="Associated maintenance ticket if the document is ticket-related."
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="documents",
        doc="Associated location if the document is location-related."
    )
    sensor_site: Mapped[Optional["SensorSite"]] = relationship(
        "SensorSite",
        back_populates="documents",
        doc="Associated sensor site if the document is sensor-related."
    )
    uploaded_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="uploaded_documents",
        doc="User who uploaded the document."
    )
    
    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        """
        Representation for logging and debugging.
        
        Returns
        -------
        str
            String representation showing document ID, filename, and status.
        """
        return (
            f"<Document id={self.id} filename={self.filename!r} "
            f"type={self.document_type} status={self.status}>"
        )
    
    @property
    def file_size_human(self) -> str:
        """
        Get human-readable file size representation.
        
        Returns
        -------
        str
            Human-readable file size (e.g., "1.5 MB", "500 KB").
        """
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    @property
    def is_image(self) -> bool:
        """
        Check if the document is an image file.
        
        Returns
        -------
        bool
            True if the document is an image file.
        """
        image_types = {
            DocumentType.PROJECT_PHOTO,
            DocumentType.RESOURCE_PHOTO,
            DocumentType.MAINTENANCE_PHOTO,
            DocumentType.LOCATION_PHOTO,
            DocumentType.INSTALLATION_PHOTO,
            DocumentType.IMAGE,
        }
        return self.document_type in image_types
    
    @property
    def is_document(self) -> bool:
        """
        Check if the document is a text-based document file.
        
        Returns
        -------
        bool
            True if the document is a text-based file.
        """
        document_types = {
            DocumentType.PROJECT_PROPOSAL,
            DocumentType.PROJECT_REPORT,
            DocumentType.MANUAL,
            DocumentType.CERTIFICATE,
            DocumentType.MAINTENANCE_REPORT,
            DocumentType.WORK_ORDER,
            DocumentType.TROUBLESHOOTING_GUIDE,
            DocumentType.GENERAL_DOCUMENT,
        }
        return self.document_type in document_types
    
    def increment_download_count(self) -> None:
        """
        Increment the download count and update last accessed timestamp.
        
        This method should be called whenever the document is accessed
        for download to maintain accurate usage statistics.
        """
        self.download_count += 1
        self.last_accessed_at = datetime.utcnow()
    
    def get_full_file_path(self, storage_base_path: str) -> str:
        """
        Get the absolute file path for the stored document.
        
        Parameters
        ----------
        storage_base_path : str
            Base directory path for document storage.
            
        Returns
        -------
        str
            Absolute path to the stored document file.
        """
        return os.path.join(storage_base_path, self.file_path)
    
    def is_accessible_by_user(self, user_id: Optional[int] = None) -> bool:
        """
        Check if the document is accessible by the given user.
        
        Parameters
        ----------
        user_id : int, optional
            ID of the user requesting access.
            
        Returns
        -------
        bool
            True if the document is accessible by the user.
        """
        # Public documents are accessible to everyone
        if self.is_public:
            return True
        
        # Private documents require authentication
        if user_id is None:
            return False
        
        # TODO: Implement role-based access control
        # For now, authenticated users can access private documents
        return True
