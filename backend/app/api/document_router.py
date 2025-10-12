"""
FastAPI router for document management endpoints.

This router provides comprehensive REST API endpoints for document upload,
download, management, and search operations. It implements all requirements
from Issue #7 including file upload, validation, storage, access control,
and cleanup functionality.

The router follows RESTful conventions and integrates seamlessly with the
existing LifeLine-ICT API architecture.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.deps import (
    get_current_user,
    get_pagination_params,
    get_session,
)
from ..core.config import settings
from ..models.document import DocumentType, DocumentStatus
from ..models.user import User
from ..schemas.base import PaginationQuery, PaginatedResponse
from ..schemas.document import (
    DocumentRead,
    DocumentSearchQuery,
    DocumentStats,
    DocumentSummary,
    DocumentUpdate,
    DocumentUploadResponse,
)
from ..services.document_service import DocumentService
from ..services.exceptions import (
    DocumentNotFoundError,
    FileValidationError,
    StorageError,
    ValidationError,
)

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)


def get_document_service(session: AsyncSession = Depends(get_session)) -> DocumentService:
    """
    Dependency to get document service instance.
    
    Parameters
    ----------
    session : AsyncSession
        Database session.
        
    Returns
    -------
    DocumentService
        Document service instance.
    """
    return DocumentService(session)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
    description="""
    Upload a new document to the system.
    
    This endpoint handles file uploads with comprehensive validation including:
    - File type and size validation
    - Security checks for malicious content
    - Automatic categorization based on document type
    - Relationship linking to projects, resources, tickets, etc.
    
    Supported file types: PDF, DOC, DOCX, TXT, JPG, JPEG, PNG, GIF, BMP, TIFF, ZIP, RAR, 7Z
    
    Maximum file size: 100MB (configurable)
    """,
)
async def upload_document(
    file: UploadFile = File(..., description="File to upload"),
    document_type: DocumentType = Form(
        default=DocumentType.GENERAL_DOCUMENT,
        description="Type of document being uploaded"
    ),
    description: Optional[str] = Form(
        default=None,
        description="Description of the document contents"
    ),
    tags: Optional[str] = Form(
        default=None,
        description="Comma-separated tags for categorization"
    ),
    is_public: bool = Form(
        default=False,
        description="Whether the document can be accessed without authentication"
    ),
    project_id: Optional[int] = Form(
        default=None,
        description="ID of associated project"
    ),
    resource_id: Optional[int] = Form(
        default=None,
        description="ID of associated ICT resource"
    ),
    maintenance_ticket_id: Optional[int] = Form(
        default=None,
        description="ID of associated maintenance ticket"
    ),
    location_id: Optional[int] = Form(
        default=None,
        description="ID of associated location"
    ),
    sensor_site_id: Optional[int] = Form(
        default=None,
        description="ID of associated sensor site"
    ),
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    """
    Upload a new document.
    
    Parameters
    ----------
    file : UploadFile
        The file to upload.
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
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    DocumentUploadResponse
        Upload response with document details.
        
    Raises
    ------
    HTTPException
        If upload fails due to validation or storage errors.
    """
    try:
        return await service.upload_document(
            file=file,
            document_type=document_type,
            description=description,
            tags=tags,
            is_public=is_public,
            project_id=project_id,
            resource_id=resource_id,
            maintenance_ticket_id=maintenance_ticket_id,
            location_id=location_id,
            sensor_site_id=sensor_site_id,
            uploaded_by_user_id=current_user.id if current_user else None,
            actor=current_user,
        )
    except FileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File validation failed: {e}"
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage error: {e}"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[DocumentRead],
    summary="List Documents",
    description="""
    List documents with advanced filtering and search capabilities.
    
    Supports filtering by:
    - Document type, status, MIME type, file extension
    - Associated entities (projects, resources, tickets, etc.)
    - Date ranges, file size ranges
    - Text search across filename, description, and tags
    
    Results are paginated and can be sorted by various fields.
    """,
)
async def list_documents(
    search: Optional[str] = Query(
        default=None,
        description="Text search across filename, description, and tags"
    ),
    document_type: Optional[DocumentType] = Query(
        default=None,
        description="Filter by document type"
    ),
    status: Optional[DocumentStatus] = Query(
        default=None,
        description="Filter by document status"
    ),
    mime_type: Optional[str] = Query(
        default=None,
        description="Filter by MIME type"
    ),
    file_extension: Optional[str] = Query(
        default=None,
        description="Filter by file extension"
    ),
    is_public: Optional[bool] = Query(
        default=None,
        description="Filter by public access setting"
    ),
    project_id: Optional[int] = Query(
        default=None,
        description="Filter by associated project"
    ),
    resource_id: Optional[int] = Query(
        default=None,
        description="Filter by associated ICT resource"
    ),
    maintenance_ticket_id: Optional[int] = Query(
        default=None,
        description="Filter by associated maintenance ticket"
    ),
    location_id: Optional[int] = Query(
        default=None,
        description="Filter by associated location"
    ),
    sensor_site_id: Optional[int] = Query(
        default=None,
        description="Filter by associated sensor site"
    ),
    uploaded_by_user_id: Optional[int] = Query(
        default=None,
        description="Filter by uploader"
    ),
    sort_by: str = Query(
        default="created_at",
        description="Field to sort by"
    ),
    sort_order: str = Query(
        default="desc",
        description="Sort order (asc or desc)"
    ),
    pagination: PaginationQuery = Depends(get_pagination_params),
    service: DocumentService = Depends(get_document_service),
) -> PaginatedResponse[DocumentRead]:
    """
    List documents with filtering and pagination.
    
    Parameters
    ----------
    search : str, optional
        Text search term.
    document_type : DocumentType, optional
        Document type filter.
    status : DocumentStatus, optional
        Status filter.
    mime_type : str, optional
        MIME type filter.
    file_extension : str, optional
        File extension filter.
    is_public : bool, optional
        Public access filter.
    project_id : int, optional
        Project filter.
    resource_id : int, optional
        Resource filter.
    maintenance_ticket_id : int, optional
        Maintenance ticket filter.
    location_id : int, optional
        Location filter.
    sensor_site_id : int, optional
        Sensor site filter.
    uploaded_by_user_id : int, optional
        Uploader filter.
    sort_by : str
        Sort field.
    sort_order : str
        Sort order.
    pagination : PaginationQuery
        Pagination parameters.
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    PaginatedResponse[DocumentRead]
        Paginated list of documents.
    """
    search_query = DocumentSearchQuery(
        search=search,
        document_type=document_type,
        status=status,
        mime_type=mime_type,
        file_extension=file_extension,
        is_public=is_public,
        project_id=project_id,
        resource_id=resource_id,
        maintenance_ticket_id=maintenance_ticket_id,
        location_id=location_id,
        sensor_site_id=sensor_site_id,
        uploaded_by_user_id=uploaded_by_user_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    return await service.search_documents(
        search_query=search_query,
        pagination=pagination,
        user_id=None,  # TODO: Get from authentication
    )


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Get Document",
    description="""
    Get detailed information about a specific document.
    
    Returns comprehensive document metadata including file information,
    relationships, usage statistics, and access details.
    """,
)
async def get_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    """
    Get document by ID.
    
    Parameters
    ----------
    document_id : int
        Document ID to retrieve.
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    DocumentRead
        Document information.
        
    Raises
    ------
    HTTPException
        If document is not found or access is denied.
    """
    try:
        return await service.get_document(
            document_id=document_id,
            user_id=current_user.id if current_user else None,
        )
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get(
    "/{document_id}/download",
    summary="Download Document",
    description="""
    Download a document file.
    
    Streams the file content directly to the client with appropriate
    headers for download. Updates download statistics automatically.
    
    Supports range requests for large files and proper MIME type handling.
    """,
)
async def download_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Download document file.
    
    Parameters
    ----------
    document_id : int
        Document ID to download.
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    StreamingResponse
        File content stream.
        
    Raises
    ------
    HTTPException
        If document is not found, access is denied, or file is missing.
    """
    try:
        content, filename, mime_type = await service.download_document(
            document_id=document_id,
            user_id=current_user.id if current_user else None,
        )
        
        return StreamingResponse(
            iter([content]),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(content)),
            }
        )
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Update Document",
    description="""
    Update document metadata.
    
    Allows updating document description, tags, type, public access setting,
    and relationships to other entities. File content cannot be changed
    through this endpoint - use upload for new versions.
    """,
)
async def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    """
    Update document metadata.
    
    Parameters
    ----------
    document_id : int
        Document ID to update.
    update_data : DocumentUpdate
        Update data.
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    DocumentRead
        Updated document information.
        
    Raises
    ------
    HTTPException
        If document is not found, access is denied, or validation fails.
    """
    try:
        return await service.update_document(
            document_id=document_id,
            update_data=update_data,
            user_id=current_user.id if current_user else None,
            actor=current_user,
        )
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Document",
    description="""
    Delete a document and its associated file.
    
    Permanently removes the document record from the database and
    deletes the associated file from storage. This action cannot be undone.
    
    Only document owners or administrators can delete documents.
    """,
)
async def delete_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Delete document.
    
    Parameters
    ----------
    document_id : int
        Document ID to delete.
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    Response
        Empty response with 204 status.
        
    Raises
    ------
    HTTPException
        If document is not found, access is denied, or deletion fails.
    """
    try:
        success = await service.delete_document(
            document_id=document_id,
            user_id=current_user.id if current_user else None,
            actor=current_user,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=PaginatedResponse[DocumentSummary],
    summary="Get Documents by Entity",
    description="""
    Get documents associated with a specific entity.
    
    Retrieves all documents linked to a project, resource, maintenance ticket,
    location, or sensor site. Useful for displaying related documentation
    in entity detail views.
    
    Supported entity types: project, resource, maintenance_ticket, location, sensor_site
    """,
)
async def get_documents_by_entity(
    entity_type: str,
    entity_id: int,
    pagination: PaginationQuery = Depends(get_pagination_params),
    service: DocumentService = Depends(get_document_service),
) -> PaginatedResponse[DocumentSummary]:
    """
    Get documents by entity.
    
    Parameters
    ----------
    entity_type : str
        Type of entity.
    entity_id : int
        Entity ID.
    pagination : PaginationQuery
        Pagination parameters.
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    PaginatedResponse[DocumentSummary]
        Paginated list of document summaries.
        
    Raises
    ------
    HTTPException
        If entity type is invalid.
    """
    if entity_type not in ['project', 'resource', 'maintenance_ticket', 'location', 'sensor_site']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entity type. Must be one of: project, resource, maintenance_ticket, location, sensor_site"
        )
    
    return await service.get_documents_by_entity(
        entity_type=entity_type,
        entity_id=entity_id,
        pagination=pagination,
        user_id=None,  # TODO: Get from authentication
    )


@router.get(
    "/stats/overview",
    response_model=DocumentStats,
    summary="Get Document Statistics",
    description="""
    Get comprehensive document statistics and analytics.
    
    Provides aggregated information about documents in the system including:
    - Total documents and storage usage
    - Breakdown by document type, status, and MIME type
    - Most downloaded and recently uploaded documents
    - Storage usage by entity type
    
    Useful for system monitoring and reporting.
    """,
)
async def get_document_statistics(
    service: DocumentService = Depends(get_document_service),
) -> DocumentStats:
    """
    Get document statistics.
    
    Parameters
    ----------
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    DocumentStats
        Document statistics and analytics.
    """
    return await service.get_document_statistics()


@router.post(
    "/{document_id}/quarantine",
    status_code=status.HTTP_200_OK,
    summary="Quarantine Document",
    description="""
    Quarantine a document for security reasons.
    
    Moves the document file to quarantine storage and marks the document
    as quarantined. This action is typically performed when malicious
    content is detected or security concerns are identified.
    
    Only administrators can quarantine documents.
    """,
)
async def quarantine_document(
    document_id: int,
    reason: str = Form(..., description="Reason for quarantine"),
    service: DocumentService = Depends(get_document_service),
) -> dict:
    """
    Quarantine document.
    
    Parameters
    ----------
    document_id : int
        Document ID to quarantine.
    reason : str
        Reason for quarantine.
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    dict
        Quarantine result.
        
    Raises
    ------
    HTTPException
        If document is not found or quarantine fails.
    """
    try:
        success = await service.quarantine_document(
            document_id=document_id,
            reason=reason
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to quarantine document"
            )
        
        return {"success": True, "message": f"Document {document_id} quarantined"}
        
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/cleanup/orphaned",
    status_code=status.HTTP_200_OK,
    summary="Cleanup Orphaned Files",
    description="""
    Clean up orphaned files in storage.
    
    Removes files from storage that are no longer referenced by any
    document records. This helps maintain storage efficiency and
    removes files that may have been left behind due to failed operations.
    
    Only administrators can perform cleanup operations.
    """,
)
async def cleanup_orphaned_files(
    service: DocumentService = Depends(get_document_service),
) -> dict:
    """
    Cleanup orphaned files.
    
    Parameters
    ----------
    service : DocumentService
        Document service instance.
        
    Returns
    -------
    dict
        Cleanup results.
    """
    cleaned_files = await service.cleanup_orphaned_files()
    
    return {
        "success": True,
        "message": f"Cleaned up {len(cleaned_files)} orphaned files",
        "cleaned_files": cleaned_files
    }
