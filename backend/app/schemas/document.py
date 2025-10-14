"""
Pydantic schemas for document upload and management operations.

This module defines the request and response models for the document management
API, including validation rules for file uploads, metadata handling, and
relationship management with other entities in the LifeLine-ICT system.

The schemas ensure type safety, data validation, and clear API contracts
for document-related operations across the university's ICT infrastructure.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from ..models.document import DocumentType, DocumentStatus


class DocumentBase(BaseModel):
    """
    Base schema for document-related operations.
    
    Contains common fields shared across document operations and provides
    validation rules for document metadata and categorization.
    """
    
    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original filename of the uploaded document."
    )
    document_type: DocumentType = Field(
        default=DocumentType.GENERAL_DOCUMENT,
        description="Categorized type of document for organizational purposes."
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="User-provided description of the document's contents or purpose."
    )
    tags: Optional[str] = Field(
        None,
        max_length=500,
        description="Comma-separated tags for additional categorization and searchability."
    )
    is_public: bool = Field(
        default=False,
        description="Whether the document can be accessed without authentication."
    )
    
    # Relationship fields
    project_id: Optional[int] = Field(
        None,
        description="ID of the associated project if applicable."
    )
    resource_id: Optional[int] = Field(
        None,
        description="ID of the associated ICT resource if applicable."
    )
    maintenance_ticket_id: Optional[int] = Field(
        None,
        description="ID of the associated maintenance ticket if applicable."
    )
    location_id: Optional[int] = Field(
        None,
        description="ID of the associated location if applicable."
    )
    sensor_site_id: Optional[int] = Field(
        None,
        description="ID of the associated sensor site if applicable."
    )
    
    @validator('tags')
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and sanitize tags input.
        
        Parameters
        ----------
        v : str, optional
            Raw tags input from user.
            
        Returns
        -------
        str, optional
            Sanitized tags string.
            
        Raises
        ------
        ValueError
            If tags contain invalid characters or format.
        """
        if v is None:
            return v
        
        # Remove extra whitespace and normalize
        tags = [tag.strip().lower() for tag in v.split(',') if tag.strip()]
        
        # Validate individual tags
        for tag in tags:
            if len(tag) > 50:
                raise ValueError("Individual tags cannot exceed 50 characters")
            if not tag.replace('-', '').replace('_', '').isalnum():
                raise ValueError("Tags can only contain alphanumeric characters, hyphens, and underscores")
        
        return ', '.join(tags)
    
    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate description content.
        
        Parameters
        ----------
        v : str, optional
            Raw description input from user.
            
        Returns
        -------
        str, optional
            Sanitized description string.
        """
        if v is None:
            return v
        
        # Basic content validation - could be enhanced with profanity filters
        return v.strip()


class DocumentCreate(DocumentBase):
    """
    Schema for creating new documents.
    
    Extends the base document schema with additional fields specific to
    the document creation process, including file metadata validation.
    """
    
    file_size: int = Field(
        ...,
        gt=0,
        le=100 * 1024 * 1024,  # 100MB max
        description="Size of the uploaded file in bytes."
    )
    mime_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="MIME type of the uploaded file."
    )
    file_extension: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="File extension extracted from the filename."
    )
    
    @validator('file_size')
    def validate_file_size(cls, v: int) -> int:
        """
        Validate file size against system limits.
        
        Parameters
        ----------
        v : int
            File size in bytes.
            
        Returns
        -------
        int
            Validated file size.
            
        Raises
        ------
        ValueError
            If file size exceeds system limits.
        """
        if v <= 0:
            raise ValueError("File size must be greater than 0")
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError("File size cannot exceed 100MB")
        return v
    
    @validator('mime_type')
    def validate_mime_type(cls, v: str) -> str:
        """
        Validate MIME type format.
        
        Parameters
        ----------
        v : str
            Raw MIME type string.
            
        Returns
        -------
        str
            Validated MIME type.
            
        Raises
        ------
        ValueError
            If MIME type format is invalid.
        """
        if not v or '/' not in v:
            raise ValueError("Invalid MIME type format")
        return v.lower()
    
    @validator('file_extension')
    def validate_file_extension(cls, v: str) -> str:
        """
        Validate file extension.
        
        Parameters
        ----------
        v : str
            Raw file extension.
            
        Returns
        -------
        str
            Validated file extension.
            
        Raises
        ------
        ValueError
            If file extension is invalid.
        """
        # Remove leading dot if present
        ext = v.lstrip('.').lower()
        if not ext.isalnum():
            raise ValueError("File extension can only contain alphanumeric characters")
        return ext


class DocumentUpdate(BaseModel):
    """
    Schema for updating existing documents.
    
    Allows partial updates to document metadata while preserving
    file content and core identification fields.
    """
    
    document_type: Optional[DocumentType] = Field(
        None,
        description="Updated document type."
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Updated description of the document."
    )
    tags: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated tags for the document."
    )
    is_public: Optional[bool] = Field(
        None,
        description="Updated public access setting."
    )
    
    # Relationship updates
    project_id: Optional[int] = Field(
        None,
        description="Updated project association."
    )
    resource_id: Optional[int] = Field(
        None,
        description="Updated resource association."
    )
    maintenance_ticket_id: Optional[int] = Field(
        None,
        description="Updated maintenance ticket association."
    )
    location_id: Optional[int] = Field(
        None,
        description="Updated location association."
    )
    sensor_site_id: Optional[int] = Field(
        None,
        description="Updated sensor site association."
    )
    
    @validator('tags')
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        """Validate tags input for updates."""
        if v is None:
            return v
        return DocumentBase.validate_tags(cls, v)
    
    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description input for updates."""
        if v is None:
            return v
        return DocumentBase.validate_description(cls, v)


class DocumentRead(DocumentBase):
    """
    Schema for reading document information.
    
    Provides comprehensive document metadata for API responses,
    including computed fields and relationship information.
    """
    
    id: int = Field(
        ...,
        description="Unique identifier for the document."
    )
    original_filename: str = Field(
        ...,
        description="Sanitized filename used for storage."
    )
    file_path: str = Field(
        ...,
        description="Relative path to the stored file."
    )
    file_size: int = Field(
        ...,
        description="Size of the file in bytes."
    )
    mime_type: str = Field(
        ...,
        description="MIME type of the file."
    )
    file_extension: str = Field(
        ...,
        description="File extension."
    )
    status: DocumentStatus = Field(
        ...,
        description="Current processing status of the document."
    )
    checksum: Optional[str] = Field(
        None,
        description="Cryptographic hash of the file contents."
    )
    download_count: int = Field(
        ...,
        description="Number of times the document has been downloaded."
    )
    last_accessed_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the most recent access."
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the document was created."
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the document was last updated."
    )
    uploaded_by_user_id: Optional[int] = Field(
        None,
        description="ID of the user who uploaded the document."
    )
    
    # Computed fields
    file_size_human: str = Field(
        ...,
        description="Human-readable file size representation."
    )
    is_image: bool = Field(
        ...,
        description="Whether the document is an image file."
    )
    is_document: bool = Field(
        ...,
        description="Whether the document is a text-based document."
    )
    
    # Relationship information
    project_name: Optional[str] = Field(
        None,
        description="Name of the associated project."
    )
    resource_name: Optional[str] = Field(
        None,
        description="Name of the associated ICT resource."
    )
    location_campus: Optional[str] = Field(
        None,
        description="Campus of the associated location."
    )
    uploaded_by_username: Optional[str] = Field(
        None,
        description="Username of the user who uploaded the document."
    )
    
    class Config:
        """Pydantic configuration for the schema."""
        from_attributes = True


class DocumentSummary(BaseModel):
    """
    Lightweight schema for document summaries.
    
    Used in list views and relationship displays where full
    document details are not required.
    """
    
    id: int = Field(
        ...,
        description="Unique identifier for the document."
    )
    filename: str = Field(
        ...,
        description="Original filename of the document."
    )
    document_type: DocumentType = Field(
        ...,
        description="Type of the document."
    )
    file_size: int = Field(
        ...,
        description="Size of the file in bytes."
    )
    file_size_human: str = Field(
        ...,
        description="Human-readable file size."
    )
    mime_type: str = Field(
        ...,
        description="MIME type of the file."
    )
    status: DocumentStatus = Field(
        ...,
        description="Current status of the document."
    )
    created_at: datetime = Field(
        ...,
        description="When the document was created."
    )
    download_count: int = Field(
        ...,
        description="Number of downloads."
    )
    
    class Config:
        """Pydantic configuration for the schema."""
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """
    Response schema for document upload operations.
    
    Provides immediate feedback on upload success and includes
    essential document information for client processing.
    """
    
    success: bool = Field(
        ...,
        description="Whether the upload was successful."
    )
    document_id: int = Field(
        ...,
        description="ID of the created document record."
    )
    filename: str = Field(
        ...,
        description="Original filename of the uploaded document."
    )
    file_size: int = Field(
        ...,
        description="Size of the uploaded file."
    )
    file_size_human: str = Field(
        ...,
        description="Human-readable file size."
    )
    document_type: DocumentType = Field(
        ...,
        description="Assigned document type."
    )
    status: DocumentStatus = Field(
        ...,
        description="Current processing status."
    )
    message: str = Field(
        ...,
        description="Human-readable status message."
    )
    download_url: str = Field(
        ...,
        description="URL for downloading the document."
    )


class DocumentDownloadResponse(BaseModel):
    """
    Response schema for document download operations.
    
    Provides metadata about the document being downloaded
    along with download instructions.
    """
    
    document_id: int = Field(
        ...,
        description="ID of the document being downloaded."
    )
    filename: str = Field(
        ...,
        description="Original filename of the document."
    )
    mime_type: str = Field(
        ...,
        description="MIME type of the file."
    )
    file_size: int = Field(
        ...,
        description="Size of the file in bytes."
    )
    file_size_human: str = Field(
        ...,
        description="Human-readable file size."
    )
    download_url: str = Field(
        ...,
        description="URL for downloading the document."
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="When the download URL expires (if applicable)."
    )


class DocumentSearchQuery(BaseModel):
    """
    Schema for document search and filtering operations.
    
    Provides flexible querying capabilities for finding documents
    based on various criteria and metadata fields.
    """
    
    search: Optional[str] = Field(
        None,
        max_length=255,
        description="Text search across filename, description, and tags."
    )
    document_type: Optional[DocumentType] = Field(
        None,
        description="Filter by document type."
    )
    status: Optional[DocumentStatus] = Field(
        None,
        description="Filter by document status."
    )
    mime_type: Optional[str] = Field(
        None,
        description="Filter by MIME type."
    )
    file_extension: Optional[str] = Field(
        None,
        description="Filter by file extension."
    )
    is_public: Optional[bool] = Field(
        None,
        description="Filter by public access setting."
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Filter by tags (all tags must match)."
    )
    
    # Relationship filters
    project_id: Optional[int] = Field(
        None,
        description="Filter by associated project."
    )
    resource_id: Optional[int] = Field(
        None,
        description="Filter by associated ICT resource."
    )
    maintenance_ticket_id: Optional[int] = Field(
        None,
        description="Filter by associated maintenance ticket."
    )
    location_id: Optional[int] = Field(
        None,
        description="Filter by associated location."
    )
    sensor_site_id: Optional[int] = Field(
        None,
        description="Filter by associated sensor site."
    )
    uploaded_by_user_id: Optional[int] = Field(
        None,
        description="Filter by uploader."
    )
    
    # Date filters
    created_after: Optional[datetime] = Field(
        None,
        description="Filter documents created after this date."
    )
    created_before: Optional[datetime] = Field(
        None,
        description="Filter documents created before this date."
    )
    accessed_after: Optional[datetime] = Field(
        None,
        description="Filter documents accessed after this date."
    )
    
    # Size filters
    min_file_size: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum file size in bytes."
    )
    max_file_size: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum file size in bytes."
    )
    
    # Sorting
    sort_by: str = Field(
        default="created_at",
        description="Field to sort by."
    )
    sort_order: str = Field(
        default="desc",
        description="Sort order (asc or desc)."
    )
    
    @validator('sort_by')
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort field."""
        allowed_fields = {
            'created_at', 'updated_at', 'filename', 'file_size',
            'download_count', 'document_type', 'status'
        }
        if v not in allowed_fields:
            raise ValueError(f"Sort field must be one of: {', '.join(allowed_fields)}")
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order."""
        if v not in ['asc', 'desc']:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v
    
    @validator('tags')
    def validate_tags_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags list."""
        if v is None:
            return v
        
        validated_tags = []
        for tag in v:
            if not tag.strip():
                continue
            clean_tag = tag.strip().lower()
            if len(clean_tag) > 50:
                raise ValueError("Individual tags cannot exceed 50 characters")
            if not clean_tag.replace('-', '').replace('_', '').isalnum():
                raise ValueError("Tags can only contain alphanumeric characters, hyphens, and underscores")
            validated_tags.append(clean_tag)
        
        return validated_tags if validated_tags else None


class DocumentStats(BaseModel):
    """
    Schema for document statistics and analytics.
    
    Provides aggregated information about documents in the system
    for reporting and monitoring purposes.
    """
    
    total_documents: int = Field(
        ...,
        description="Total number of documents in the system."
    )
    total_size_bytes: int = Field(
        ...,
        description="Total size of all documents in bytes."
    )
    total_size_human: str = Field(
        ...,
        description="Human-readable total size."
    )
    documents_by_type: Dict[DocumentType, int] = Field(
        ...,
        description="Count of documents by type."
    )
    documents_by_status: Dict[DocumentStatus, int] = Field(
        ...,
        description="Count of documents by status."
    )
    documents_by_mime_type: Dict[str, int] = Field(
        ...,
        description="Count of documents by MIME type."
    )
    most_downloaded: List[DocumentSummary] = Field(
        ...,
        description="Most downloaded documents."
    )
    recent_uploads: List[DocumentSummary] = Field(
        ...,
        description="Recently uploaded documents."
    )
    storage_usage_by_entity: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Storage usage broken down by entity type."
    )
