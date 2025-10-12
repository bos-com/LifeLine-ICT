"""
Document service for business logic and orchestration.

This service orchestrates document operations including upload, validation,
storage management, and business rule enforcement. It coordinates between
the repository layer, file storage service, and external systems to provide
a comprehensive document management solution for the LifeLine-ICT system.

The service implements business rules, security policies, and operational
procedures for document handling across the university's ICT infrastructure.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import BinaryIO, List, Optional, Tuple

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..models import (
    AuditAction,
    AuditEntityType,
    Document,
    DocumentStatus,
    DocumentType,
    ICTResource,
    Location,
    MaintenanceTicket,
    Project,
    SensorSite,
    User,
)
from ..repositories.document_repository import DocumentRepository
from ..schemas.base import PaginatedResponse, PaginationQuery
from ..schemas.document import (
    DocumentCreate,
    DocumentRead,
    DocumentSearchQuery,
    DocumentStats,
    DocumentSummary,
    DocumentUpdate,
    DocumentUploadResponse,
)
from ..services.file_storage import FileStorageService
from .base import BaseService
from .exceptions import (
    DocumentNotFoundError,
    FileValidationError,
    StorageError,
    ValidationError,
)
from .audit_trail import AuditTrailRecorder

logger = logging.getLogger(__name__)


class DocumentService(BaseService):
    """
    Service for document management operations.
    
    Provides comprehensive document management including upload, validation,
    storage, retrieval, and business rule enforcement. Coordinates between
    the repository layer, file storage service, and external systems.
    
    Attributes
    ----------
    repository : DocumentRepository
        Repository for document database operations.
    storage_service : FileStorageService
        Service for file storage operations.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize document service.
        
        Parameters
        ----------
        session : AsyncSession
            Database session for operations.
        """
        super().__init__(session)
        self.repository = DocumentRepository(session)
        self.storage_service = FileStorageService()
        self.audit_trail = AuditTrailRecorder(session, AuditEntityType.DOCUMENT)
    
    async def upload_document(
        self,
        file: UploadFile,
        document_type: DocumentType = DocumentType.GENERAL_DOCUMENT,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        is_public: bool = False,
        project_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        maintenance_ticket_id: Optional[int] = None,
        location_id: Optional[int] = None,
        sensor_site_id: Optional[int] = None,
        uploaded_by_user_id: Optional[int] = None,
        actor: Optional[User] = None,
    ) -> DocumentUploadResponse:
        """
        Upload and process a new document.
        
        Parameters
        ----------
        file : UploadFile
            The uploaded file.
        document_type : DocumentType
            Type of document being uploaded.
        description : str, optional
            Description of the document.
        tags : str, optional
            Comma-separated tags.
        is_public : bool
            Whether document is publicly accessible.
        project_id : int, optional
            Associated project ID.
        resource_id : int, optional
            Associated resource ID.
        maintenance_ticket_id : int, optional
            Associated maintenance ticket ID.
        location_id : int, optional
            Associated location ID.
        sensor_site_id : int, optional
            Associated sensor site ID.
        uploaded_by_user_id : int, optional
            ID of user uploading the document.
            
        Returns
        -------
        DocumentUploadResponse
            Response containing upload details and document information.
            
        Raises
        ------
        FileValidationError
            If file validation fails.
        StorageError
            If file storage fails.
        ValidationError
            If business validation fails.
        """
        try:
            logger.info(f"Starting upload for file: {file.filename}")
            
            # Validate file
            filename, mime_type, file_extension, file_size = self.storage_service.validate_file(
                file, document_type
            )
            
            # Read file content
            content = await file.read()
            
            # Generate storage path
            storage_path, original_filename = self.storage_service.generate_storage_path(
                filename, document_type
            )
            
            # Calculate checksum
            checksum = self.storage_service.calculate_checksum(content)
            
            # Validate relationships
            await self._validate_relationships(
                project_id=project_id,
                resource_id=resource_id,
                maintenance_ticket_id=maintenance_ticket_id,
                location_id=location_id,
                sensor_site_id=sensor_site_id,
            )
            
            uploader_id = uploaded_by_user_id or (actor.id if actor else None)

            # Create document record
            document = await self.repository.create_document(
                filename=filename,
                original_filename=original_filename,
                file_path=storage_path,
                file_size=file_size,
                mime_type=mime_type,
                file_extension=file_extension,
                document_type=document_type,
                description=description,
                tags=tags,
                checksum=checksum,
                is_public=is_public,
                project_id=project_id,
                resource_id=resource_id,
                maintenance_ticket_id=maintenance_ticket_id,
                location_id=location_id,
                sensor_site_id=sensor_site_id,
                uploaded_by_user_id=uploader_id,
            )
            
            # Save file to storage
            self.storage_service.save_file(file, storage_path, content)
            
            # Update status to available
            document.status = DocumentStatus.AVAILABLE
            await self.repository.session.commit()

            await self.audit_trail.record(
                action=AuditAction.ATTACHMENT,
                entity_id=document.id,
                entity_name=document.filename,
                summary="Document uploaded",
                actor=actor,
                context={
                    "document_type": document_type.value,
                    "is_public": is_public,
                    "project_id": project_id,
                    "resource_id": resource_id,
                    "maintenance_ticket_id": maintenance_ticket_id,
                    "location_id": location_id,
                    "sensor_site_id": sensor_site_id,
                    "uploaded_by_user_id": uploader_id,
                },
            )
            
            logger.info(f"Successfully uploaded document: {document.id}")
            
            return DocumentUploadResponse(
                success=True,
                document_id=document.id,
                filename=document.filename,
                file_size=document.file_size,
                file_size_human=document.file_size_human,
                document_type=document.document_type,
                status=document.status,
                message="Document uploaded successfully",
                download_url=f"/api/v1/documents/{document.id}/download",
            )
            
        except (FileValidationError, StorageError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise StorageError(f"Upload failed: {e}")
    
    async def get_document(
        self,
        document_id: int,
        user_id: Optional[int] = None
    ) -> DocumentRead:
        """
        Get document information with access control.
        
        Parameters
        ----------
        document_id : int
            Document ID to retrieve.
        user_id : int, optional
            ID of user requesting access.
            
        Returns
        -------
        DocumentRead
            Document information.
            
        Raises
        ------
        DocumentNotFoundError
            If document is not found.
        ValidationError
            If user doesn't have access.
        """
        document = await self.repository.get_document_with_relationships(document_id)
        
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        
        # Check access permissions
        if not document.is_accessible_by_user(user_id):
            raise ValidationError("Access denied to document")
        
        # Convert to response schema
        return self._document_to_read_schema(document)
    
    async def download_document(
        self,
        document_id: int,
        user_id: Optional[int] = None
    ) -> Tuple[bytes, str, str]:
        """
        Download document content.
        
        Parameters
        ----------
        document_id : int
            Document ID to download.
        user_id : int, optional
            ID of user requesting download.
            
        Returns
        -------
        Tuple[bytes, str, str]
            Tuple containing (content, filename, mime_type).
            
        Raises
        ------
        DocumentNotFoundError
            If document is not found.
        ValidationError
            If user doesn't have access.
        StorageError
            If file cannot be read.
        """
        document = await self.repository.get_by_id(document_id)
        
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        
        # Check access permissions
        if not document.is_accessible_by_user(user_id):
            raise ValidationError("Access denied to document")
        
        # Check if file exists
        if not self.storage_service.file_exists(document):
            raise StorageError("Document file not found in storage")
        
        # Increment download count
        await self.repository.increment_download_count(document_id)
        
        # Get file content
        content = self.storage_service.get_file_content(document)

        await self.audit_trail.record(
            action=AuditAction.ACCESS,
            entity_id=document.id,
            entity_name=document.filename,
            summary="Document downloaded",
            actor=None,
            context={"requested_by_user_id": user_id},
        )
        
        return content, document.filename, document.mime_type
    
    async def search_documents(
        self,
        search_query: DocumentSearchQuery,
        pagination: PaginationQuery,
        user_id: Optional[int] = None
    ) -> PaginatedResponse[DocumentRead]:
        """
        Search documents with filtering and pagination.
        
        Parameters
        ----------
        search_query : DocumentSearchQuery
            Search criteria and filters.
        pagination : PaginationQuery
            Pagination parameters.
        user_id : int, optional
            ID of user performing search.
            
        Returns
        -------
        PaginatedResponse[DocumentRead]
            Paginated search results.
        """
        documents, total_count = await self.repository.search_documents(
            search_query, pagination.limit, pagination.offset
        )
        
        # Convert to response schemas
        document_reads = [self._document_to_read_schema(doc) for doc in documents]
        
        return PaginatedResponse[DocumentRead](
            items=document_reads,
            total=total_count,
            page=pagination.page,
            per_page=pagination.limit,
            pages=(total_count + pagination.limit - 1) // pagination.limit,
        )
    
    async def update_document(
        self,
        document_id: int,
        update_data: DocumentUpdate,
        user_id: Optional[int] = None,
        actor: Optional[User] = None,
    ) -> DocumentRead:
        """
        Update document metadata.
        
        Parameters
        ----------
        document_id : int
            Document ID to update.
        update_data : DocumentUpdate
            Update data.
        user_id : int, optional
            ID of user performing update.
            
        Returns
        -------
        DocumentRead
            Updated document information.
            
        Raises
        ------
        DocumentNotFoundError
            If document is not found.
        ValidationError
            If user doesn't have access or validation fails.
        """
        document = await self.repository.get_by_id(document_id)
        
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        
        # Check access permissions (only owner or admin can update)
        if not document.is_accessible_by_user(user_id):
            raise ValidationError("Access denied to document")
        
        # Validate relationships if being updated
        if any([
            update_data.project_id,
            update_data.resource_id,
            update_data.maintenance_ticket_id,
            update_data.location_id,
            update_data.sensor_site_id,
        ]):
            await self._validate_relationships(
                project_id=update_data.project_id,
                resource_id=update_data.resource_id,
                maintenance_ticket_id=update_data.maintenance_ticket_id,
                location_id=update_data.location_id,
                sensor_site_id=update_data.sensor_site_id,
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(document, field):
                setattr(document, field, value)
        
        await self.repository.session.commit()
        await self.repository.session.refresh(document)

        await self.audit_trail.record(
            action=AuditAction.UPDATE,
            entity_id=document.id,
            entity_name=document.filename,
            summary="Document metadata updated",
            actor=actor,
            context={"changes": update_dict},
        )
        
        return self._document_to_read_schema(document)
    
    async def delete_document(
        self,
        document_id: int,
        user_id: Optional[int] = None,
        actor: Optional[User] = None,
    ) -> bool:
        """
        Delete document and associated file.
        
        Parameters
        ----------
        document_id : int
            Document ID to delete.
        user_id : int, optional
            ID of user performing deletion.
            
        Returns
        -------
        bool
            True if deletion was successful.
            
        Raises
        ------
        DocumentNotFoundError
            If document is not found.
        ValidationError
            If user doesn't have access.
        StorageError
            If file deletion fails.
        """
        document = await self.repository.get_by_id(document_id)
        
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        
        # Check access permissions (only owner or admin can delete)
        if not document.is_accessible_by_user(user_id):
            raise ValidationError("Access denied to document")
        
        try:
            # Delete file from storage
            if self.storage_service.file_exists(document):
                self.storage_service.delete_file(document)
            
            # Delete database record
            await self.repository.delete(document)
            await self.repository.session.commit()
            
            logger.info(f"Successfully deleted document: {document_id}")
            await self.audit_trail.record(
                action=AuditAction.DELETE,
                entity_id=document.id,
                entity_name=document.filename,
                summary="Document deleted",
                actor=actor,
                context={
                    "file_path": document.file_path,
                    "mime_type": document.mime_type,
                },
            )
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise StorageError(f"Failed to delete document: {e}")
    
    async def get_documents_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        pagination: PaginationQuery,
        user_id: Optional[int] = None
    ) -> PaginatedResponse[DocumentSummary]:
        """
        Get documents associated with a specific entity.
        
        Parameters
        ----------
        entity_type : str
            Type of entity.
        entity_id : int
            ID of the entity.
        pagination : PaginationQuery
            Pagination parameters.
        user_id : int, optional
            ID of user requesting documents.
            
        Returns
        -------
        PaginatedResponse[DocumentSummary]
            Paginated list of document summaries.
        """
        documents, total_count = await self.repository.get_documents_by_entity(
            entity_type, entity_id, pagination.limit, pagination.offset
        )
        
        # Convert to summary schemas
        document_summaries = [self._document_to_summary_schema(doc) for doc in documents]
        
        return PaginatedResponse[DocumentSummary](
            items=document_summaries,
            total=total_count,
            page=pagination.page,
            per_page=pagination.limit,
            pages=(total_count + pagination.limit - 1) // pagination.limit,
        )
    
    async def get_document_statistics(self) -> DocumentStats:
        """
        Get comprehensive document statistics.
        
        Returns
        -------
        DocumentStats
            Document statistics and analytics.
        """
        stats = await self.repository.get_document_statistics()
        
        # Get most downloaded documents
        most_downloaded = await self.repository.get_most_downloaded_documents(limit=10)
        most_downloaded_schemas = [
            self._document_to_summary_schema(doc) for doc in most_downloaded
        ]
        
        # Get recent documents
        recent_documents = await self.repository.get_recent_documents(limit=10)
        recent_schemas = [
            self._document_to_summary_schema(doc) for doc in recent_documents
        ]
        
        # Calculate human-readable total size
        total_size_human = self._bytes_to_human_readable(stats['total_size_bytes'])
        
        return DocumentStats(
            total_documents=stats['total_documents'],
            total_size_bytes=stats['total_size_bytes'],
            total_size_human=total_size_human,
            documents_by_type=stats['documents_by_type'],
            documents_by_status=stats['documents_by_status'],
            documents_by_mime_type=stats['documents_by_mime_type'],
            most_downloaded=most_downloaded_schemas,
            recent_uploads=recent_schemas,
            storage_usage_by_entity=stats['storage_usage_by_entity'],
        )
    
    async def cleanup_orphaned_files(self) -> List[str]:
        """
        Clean up orphaned files in storage.
        
        Returns
        -------
        List[str]
            List of cleaned up file paths.
        """
        return self.storage_service.cleanup_orphaned_files()
    
    async def quarantine_document(
        self,
        document_id: int,
        reason: str
    ) -> bool:
        """
        Quarantine a document due to security concerns.
        
        Parameters
        ----------
        document_id : int
            Document ID to quarantine.
        reason : str
            Reason for quarantine.
            
        Returns
        -------
        bool
            True if quarantine was successful.
        """
        document = await self.repository.get_by_id(document_id)
        
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")
        
        try:
            # Move file to quarantine
            self.storage_service.quarantine_file(document, reason)
            
            # Update document status
            await self.repository.update_document_status(
                document_id, DocumentStatus.QUARANTINED
            )
            
            logger.warning(f"Document {document_id} quarantined: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to quarantine document {document_id}: {e}")
            return False
    
    async def _validate_relationships(
        self,
        project_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        maintenance_ticket_id: Optional[int] = None,
        location_id: Optional[int] = None,
        sensor_site_id: Optional[int] = None,
    ) -> None:
        """
        Validate that referenced entities exist.
        
        Parameters
        ----------
        project_id : int, optional
            Project ID to validate.
        resource_id : int, optional
            Resource ID to validate.
        maintenance_ticket_id : int, optional
            Maintenance ticket ID to validate.
        location_id : int, optional
            Location ID to validate.
        sensor_site_id : int, optional
            Sensor site ID to validate.
            
        Raises
        ------
        ValidationError
            If any referenced entity doesn't exist.
        """
        entity_checks = [
            (project_id, Project, "Project"),
            (resource_id, ICTResource, "ICT resource"),
            (maintenance_ticket_id, MaintenanceTicket, "Maintenance ticket"),
            (location_id, Location, "Location"),
            (sensor_site_id, SensorSite, "Sensor site"),
        ]
        
        for entity_id, model, label in entity_checks:
            if entity_id is None:
                continue
            
            entity = await self.session.get(model, entity_id)
            if entity is None:
                raise ValidationError(f"{label} {entity_id} does not exist")
    
    def _document_to_read_schema(self, document: Document) -> DocumentRead:
        """
        Convert Document model to DocumentRead schema.
        
        Parameters
        ----------
        document : Document
            Document model instance.
            
        Returns
        -------
        DocumentRead
            Document read schema.
        """
        return DocumentRead(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_path=document.file_path,
            file_size=document.file_size,
            mime_type=document.mime_type,
            file_extension=document.file_extension,
            document_type=document.document_type,
            status=document.status,
            description=document.description,
            tags=document.tags,
            checksum=document.checksum,
            is_public=document.is_public,
            download_count=document.download_count,
            last_accessed_at=document.last_accessed_at,
            created_at=document.created_at,
            updated_at=document.updated_at,
            project_id=document.project_id,
            resource_id=document.resource_id,
            maintenance_ticket_id=document.maintenance_ticket_id,
            location_id=document.location_id,
            sensor_site_id=document.sensor_site_id,
            uploaded_by_user_id=document.uploaded_by_user_id,
            file_size_human=document.file_size_human,
            is_image=document.is_image,
            is_document=document.is_document,
            project_name=document.project.name if document.project else None,
            resource_name=document.resource.name if document.resource else None,
            location_campus=document.location.campus if document.location else None,
            uploaded_by_username=document.uploaded_by_user.username if document.uploaded_by_user else None,
        )
    
    def _document_to_summary_schema(self, document: Document) -> DocumentSummary:
        """
        Convert Document model to DocumentSummary schema.
        
        Parameters
        ----------
        document : Document
            Document model instance.
            
        Returns
        -------
        DocumentSummary
            Document summary schema.
        """
        return DocumentSummary(
            id=document.id,
            filename=document.filename,
            document_type=document.document_type,
            file_size=document.file_size,
            file_size_human=document.file_size_human,
            mime_type=document.mime_type,
            status=document.status,
            created_at=document.created_at,
            download_count=document.download_count,
        )
    
    def _bytes_to_human_readable(self, bytes_value: int) -> str:
        """
        Convert bytes to human-readable format.
        
        Parameters
        ----------
        bytes_value : int
            Number of bytes.
            
        Returns
        -------
        str
            Human-readable size string.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
