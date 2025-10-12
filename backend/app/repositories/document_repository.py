"""
Repository for document database operations.

This repository handles all database interactions for the Document model,
including CRUD operations, advanced querying, relationship management,
and search functionality. It provides a clean abstraction layer between
the service layer and the database for document-related operations.

The repository follows the existing patterns in the LifeLine-ICT system
and provides comprehensive querying capabilities for document management.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.document import Document, DocumentStatus, DocumentType
from ..schemas.document import DocumentSearchQuery
from .base import AsyncRepository


class DocumentRepository(AsyncRepository[Document]):
    """
    Repository for document database operations.
    
    Provides comprehensive CRUD operations and advanced querying capabilities
    for document management in the LifeLine-ICT system. Includes support for
    complex searches, relationship loading, and aggregation queries.
    
    Attributes
    ----------
    session : AsyncSession
        Database session for operations.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize document repository.
        
        Parameters
        ----------
        session : AsyncSession
            Database session for operations.
        """
        super().__init__(session, Document)
    
    async def create_document(
        self,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        file_extension: str,
        document_type: DocumentType = DocumentType.GENERAL_DOCUMENT,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        checksum: Optional[str] = None,
        is_public: bool = False,
        project_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        maintenance_ticket_id: Optional[int] = None,
        location_id: Optional[int] = None,
        sensor_site_id: Optional[int] = None,
        uploaded_by_user_id: Optional[int] = None,
    ) -> Document:
        """
        Create a new document record.
        
        Parameters
        ----------
        filename : str
            Original filename.
        original_filename : str
            Sanitized filename.
        file_path : str
            Relative path to stored file.
        file_size : int
            File size in bytes.
        mime_type : str
            MIME type of the file.
        file_extension : str
            File extension.
        document_type : DocumentType
            Type of document.
        description : str, optional
            Document description.
        tags : str, optional
            Comma-separated tags.
        checksum : str, optional
            File checksum.
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
            ID of user who uploaded the document.
            
        Returns
        -------
        Document
            Created document instance.
        """
        document = Document(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
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
            uploaded_by_user_id=uploaded_by_user_id,
            status=DocumentStatus.AVAILABLE,
        )
        
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        
        return document
    
    async def get_document_with_relationships(
        self, 
        document_id: int
    ) -> Optional[Document]:
        """
        Get document with all relationships loaded.
        
        Parameters
        ----------
        document_id : int
            Document ID to retrieve.
            
        Returns
        -------
        Document, optional
            Document with relationships or None if not found.
        """
        query = select(Document).options(
            selectinload(Document.project),
            selectinload(Document.resource),
            selectinload(Document.maintenance_ticket),
            selectinload(Document.location),
            selectinload(Document.sensor_site),
            selectinload(Document.uploaded_by_user),
        ).where(Document.id == document_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def search_documents(
        self,
        search_query: DocumentSearchQuery,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Document], int]:
        """
        Search documents with advanced filtering.
        
        Parameters
        ----------
        search_query : DocumentSearchQuery
            Search criteria and filters.
        limit : int
            Maximum number of results.
        offset : int
            Number of results to skip.
            
        Returns
        -------
        Tuple[List[Document], int]
            Tuple containing (documents, total_count).
        """
        query = select(Document).options(
            selectinload(Document.project),
            selectinload(Document.resource),
            selectinload(Document.maintenance_ticket),
            selectinload(Document.location),
            selectinload(Document.sensor_site),
            selectinload(Document.uploaded_by_user),
        )
        
        # Apply filters
        conditions = []
        
        # Text search
        if search_query.search:
            search_term = f"%{search_query.search}%"
            conditions.append(
                or_(
                    Document.filename.ilike(search_term),
                    Document.description.ilike(search_term),
                    Document.tags.ilike(search_term),
                )
            )
        
        # Document type filter
        if search_query.document_type:
            conditions.append(Document.document_type == search_query.document_type)
        
        # Status filter
        if search_query.status:
            conditions.append(Document.status == search_query.status)
        
        # MIME type filter
        if search_query.mime_type:
            conditions.append(Document.mime_type == search_query.mime_type)
        
        # File extension filter
        if search_query.file_extension:
            conditions.append(Document.file_extension == search_query.file_extension)
        
        # Public access filter
        if search_query.is_public is not None:
            conditions.append(Document.is_public == search_query.is_public)
        
        # Tags filter
        if search_query.tags:
            for tag in search_query.tags:
                conditions.append(Document.tags.ilike(f"%{tag}%"))
        
        # Relationship filters
        if search_query.project_id:
            conditions.append(Document.project_id == search_query.project_id)
        
        if search_query.resource_id:
            conditions.append(Document.resource_id == search_query.resource_id)
        
        if search_query.maintenance_ticket_id:
            conditions.append(Document.maintenance_ticket_id == search_query.maintenance_ticket_id)
        
        if search_query.location_id:
            conditions.append(Document.location_id == search_query.location_id)
        
        if search_query.sensor_site_id:
            conditions.append(Document.sensor_site_id == search_query.sensor_site_id)
        
        if search_query.uploaded_by_user_id:
            conditions.append(Document.uploaded_by_user_id == search_query.uploaded_by_user_id)
        
        # Date filters
        if search_query.created_after:
            conditions.append(Document.created_at >= search_query.created_after)
        
        if search_query.created_before:
            conditions.append(Document.created_at <= search_query.created_before)
        
        if search_query.accessed_after:
            conditions.append(Document.last_accessed_at >= search_query.accessed_after)
        
        # Size filters
        if search_query.min_file_size:
            conditions.append(Document.file_size >= search_query.min_file_size)
        
        if search_query.max_file_size:
            conditions.append(Document.file_size <= search_query.max_file_size)
        
        # Apply conditions
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply sorting
        sort_column = getattr(Document, search_query.sort_by, Document.created_at)
        if search_query.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await self.session.execute(query)
        documents = result.scalars().all()
        
        return documents, total_count
    
    async def get_documents_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Document], int]:
        """
        Get documents associated with a specific entity.
        
        Parameters
        ----------
        entity_type : str
            Type of entity ('project', 'resource', 'maintenance_ticket', etc.).
        entity_id : int
            ID of the entity.
        limit : int
            Maximum number of results.
        offset : int
            Number of results to skip.
            
        Returns
        -------
        Tuple[List[Document], int]
            Tuple containing (documents, total_count).
        """
        query = select(Document)
        
        # Map entity type to document field
        entity_field_map = {
            'project': Document.project_id,
            'resource': Document.resource_id,
            'maintenance_ticket': Document.maintenance_ticket_id,
            'location': Document.location_id,
            'sensor_site': Document.sensor_site_id,
            'user': Document.uploaded_by_user_id,
        }
        
        if entity_type not in entity_field_map:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        field = entity_field_map[entity_type]
        query = query.where(field == entity_id)
        
        # Get total count
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(desc(Document.created_at))
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        documents = result.scalars().all()
        
        return documents, total_count
    
    async def get_documents_by_type(
        self,
        document_type: DocumentType,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Document], int]:
        """
        Get documents by type.
        
        Parameters
        ----------
        document_type : DocumentType
            Type of documents to retrieve.
        limit : int
            Maximum number of results.
        offset : int
            Number of results to skip.
            
        Returns
        -------
        Tuple[List[Document], int]
            Tuple containing (documents, total_count).
        """
        query = select(Document).where(Document.document_type == document_type)
        
        # Get total count
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(desc(Document.created_at))
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        documents = result.scalars().all()
        
        return documents, total_count
    
    async def get_documents_by_status(
        self,
        status: DocumentStatus,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Document], int]:
        """
        Get documents by status.
        
        Parameters
        ----------
        status : DocumentStatus
            Status of documents to retrieve.
        limit : int
            Maximum number of results.
        offset : int
            Number of results to skip.
            
        Returns
        -------
        Tuple[List[Document], int]
            Tuple containing (documents, total_count).
        """
        query = select(Document).where(Document.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(desc(Document.created_at))
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        documents = result.scalars().all()
        
        return documents, total_count
    
    async def get_most_downloaded_documents(
        self,
        limit: int = 10
    ) -> List[Document]:
        """
        Get most downloaded documents.
        
        Parameters
        ----------
        limit : int
            Maximum number of results.
            
        Returns
        -------
        List[Document]
            List of most downloaded documents.
        """
        query = select(Document).order_by(
            desc(Document.download_count)
        ).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_recent_documents(
        self,
        limit: int = 10
    ) -> List[Document]:
        """
        Get recently uploaded documents.
        
        Parameters
        ----------
        limit : int
            Maximum number of results.
            
        Returns
        -------
        List[Document]
            List of recent documents.
        """
        query = select(Document).order_by(
            desc(Document.created_at)
        ).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def increment_download_count(
        self,
        document_id: int
    ) -> Optional[Document]:
        """
        Increment download count for a document.
        
        Parameters
        ----------
        document_id : int
            Document ID.
            
        Returns
        -------
        Document, optional
            Updated document or None if not found.
        """
        document = await self.get_by_id(document_id)
        if document:
            document.increment_download_count()
            await self.session.commit()
            await self.session.refresh(document)
        
        return document
    
    async def update_document_status(
        self,
        document_id: int,
        status: DocumentStatus
    ) -> Optional[Document]:
        """
        Update document status.
        
        Parameters
        ----------
        document_id : int
            Document ID.
        status : DocumentStatus
            New status.
            
        Returns
        -------
        Document, optional
            Updated document or None if not found.
        """
        document = await self.get_by_id(document_id)
        if document:
            document.status = status
            await self.session.commit()
            await self.session.refresh(document)
        
        return document
    
    async def get_document_statistics(self) -> dict:
        """
        Get document statistics and aggregations.
        
        Returns
        -------
        dict
            Dictionary containing various document statistics.
        """
        # Total documents
        total_query = select(func.count(Document.id))
        total_result = await self.session.execute(total_query)
        total_documents = total_result.scalar()
        
        # Total size
        size_query = select(func.sum(Document.file_size))
        size_result = await self.session.execute(size_query)
        total_size = size_result.scalar() or 0
        
        # Documents by type
        type_query = select(
            Document.document_type,
            func.count(Document.id).label('count')
        ).group_by(Document.document_type)
        type_result = await self.session.execute(type_query)
        documents_by_type = {row.document_type: row.count for row in type_result}
        
        # Documents by status
        status_query = select(
            Document.status,
            func.count(Document.id).label('count')
        ).group_by(Document.status)
        status_result = await self.session.execute(status_query)
        documents_by_status = {row.status: row.count for row in status_result}
        
        # Documents by MIME type
        mime_query = select(
            Document.mime_type,
            func.count(Document.id).label('count')
        ).group_by(Document.mime_type)
        mime_result = await self.session.execute(mime_query)
        documents_by_mime_type = {row.mime_type: row.count for row in mime_result}
        
        # Storage usage by entity
        entity_usage = {}
        for entity_type in ['project_id', 'resource_id', 'maintenance_ticket_id', 
                           'location_id', 'sensor_site_id']:
            field = getattr(Document, entity_type)
            usage_query = select(
                field,
                func.count(Document.id).label('count'),
                func.sum(Document.file_size).label('total_size')
            ).where(field.isnot(None)).group_by(field)
            usage_result = await self.session.execute(usage_query)
            
            entity_usage[entity_type.replace('_id', '')] = {
                'count': sum(row.count for row in usage_result),
                'total_size': sum(row.total_size or 0 for row in usage_result)
            }
        
        return {
            'total_documents': total_documents,
            'total_size_bytes': total_size,
            'documents_by_type': documents_by_type,
            'documents_by_status': documents_by_status,
            'documents_by_mime_type': documents_by_mime_type,
            'storage_usage_by_entity': entity_usage,
        }
    
    async def get_orphaned_documents(self) -> List[Document]:
        """
        Get documents that may be orphaned (no file in storage).
        
        Returns
        -------
        List[Document]
            List of potentially orphaned documents.
        """
        # This would typically involve checking file existence
        # For now, return documents with validation_failed status
        query = select(Document).where(
            Document.status == DocumentStatus.VALIDATION_FAILED
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def delete_documents_by_status(
        self,
        status: DocumentStatus
    ) -> int:
        """
        Delete documents with a specific status.
        
        Parameters
        ----------
        status : DocumentStatus
            Status of documents to delete.
            
        Returns
        -------
        int
            Number of deleted documents.
        """
        query = select(Document).where(Document.status == status)
        result = await self.session.execute(query)
        documents = result.scalars().all()
        
        count = 0
        for document in documents:
            await self.delete(document.id)
            count += 1
        
        return count
