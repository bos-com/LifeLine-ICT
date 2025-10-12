"""
Tests for document API router functionality.

This test suite covers all API endpoints for document management including
upload, download, search, and CRUD operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient
from io import BytesIO

from app.main import create_app
from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import DocumentUploadResponse, DocumentRead, DocumentSummary
from app.services.exceptions import (
    DocumentNotFoundError,
    FileValidationError,
    StorageError,
    ValidationError,
)


class TestDocumentRouter:
    """Test cases for document API router."""

    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        app = create_app()
        return TestClient(app)

    @pytest.fixture
    def sample_file_content(self):
        """Sample file content for testing."""
        return b"Sample file content for testing purposes"

    @pytest.fixture
    def sample_document(self):
        """Sample document model."""
        return Document(
            id=1,
            filename="test_document.pdf",
            original_filename="test_document_12345678.pdf",
            file_path="documents/2024/01/test_document_12345678.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_extension="pdf",
            document_type=DocumentType.GENERAL_DOCUMENT,
            status=DocumentStatus.AVAILABLE,
            description="Test document",
            tags="test, sample",
            checksum="abc123def456",
            is_public=False,
            download_count=0,
            project_id=1,
            resource_id=1,
            maintenance_ticket_id=None,
            location_id=None,
            sensor_site_id=None,
            uploaded_by_user_id=1,
        )

    @pytest.fixture
    def sample_document_read(self, sample_document):
        """Sample document read schema."""
        return DocumentRead(
            id=1,
            filename="test_document.pdf",
            original_filename="test_document_12345678.pdf",
            file_path="documents/2024/01/test_document_12345678.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_extension="pdf",
            document_type=DocumentType.GENERAL_DOCUMENT,
            status=DocumentStatus.AVAILABLE,
            description="Test document",
            tags="test, sample",
            checksum="abc123def456",
            is_public=False,
            download_count=0,
            last_accessed_at=None,
            created_at=sample_document.created_at,
            updated_at=sample_document.updated_at,
            project_id=1,
            resource_id=1,
            maintenance_ticket_id=None,
            location_id=None,
            sensor_site_id=None,
            uploaded_by_user_id=1,
            file_size_human="1.0 KB",
            is_image=False,
            is_document=True,
            project_name="Test Project",
            resource_name="Test Resource",
            location_campus=None,
            uploaded_by_username="testuser",
        )

    @pytest.fixture
    def upload_response(self):
        """Sample upload response."""
        return DocumentUploadResponse(
            success=True,
            document_id=1,
            filename="test_document.pdf",
            file_size=1024,
            file_size_human="1.0 KB",
            document_type=DocumentType.GENERAL_DOCUMENT,
            status=DocumentStatus.AVAILABLE,
            message="Document uploaded successfully",
            download_url="/api/v1/documents/1/download",
        )

    @patch('app.api.document_router.get_document_service')
    def test_upload_document_success(
        self, mock_get_service, client, sample_file_content, upload_response
    ):
        """Test successful document upload."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.upload_document.return_value = upload_response
        mock_get_service.return_value = mock_service
        
        # Prepare file upload
        files = {"file": ("test_document.pdf", BytesIO(sample_file_content), "application/pdf")}
        data = {
            "document_type": "general_document",
            "description": "Test document",
            "tags": "test, sample",
            "is_public": "false",
            "project_id": "1",
            "resource_id": "1",
        }
        
        # Execute
        response = client.post("/api/v1/documents/upload", files=files, data=data)
        
        # Assertions
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["document_id"] == 1
        assert response_data["filename"] == "test_document.pdf"
        assert response_data["status"] == "available"
        
        # Verify service call
        mock_service.upload_document.assert_called_once()

    @patch('app.api.document_router.get_document_service')
    def test_upload_document_validation_failure(
        self, mock_get_service, client, sample_file_content
    ):
        """Test document upload with validation failure."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.upload_document.side_effect = FileValidationError("Invalid file type")
        mock_get_service.return_value = mock_service
        
        # Prepare file upload
        files = {"file": ("test_document.exe", BytesIO(sample_file_content), "application/octet-stream")}
        data = {"document_type": "general_document"}
        
        # Execute
        response = client.post("/api/v1/documents/upload", files=files, data=data)
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "File validation failed" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_upload_document_storage_failure(
        self, mock_get_service, client, sample_file_content
    ):
        """Test document upload with storage failure."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.upload_document.side_effect = StorageError("Storage failed")
        mock_get_service.return_value = mock_service
        
        # Prepare file upload
        files = {"file": ("test_document.pdf", BytesIO(sample_file_content), "application/pdf")}
        data = {"document_type": "general_document"}
        
        # Execute
        response = client.post("/api/v1/documents/upload", files=files, data=data)
        
        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert "Storage error" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_list_documents_success(
        self, mock_get_service, client, sample_document_read
    ):
        """Test successful document listing."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.search_documents.return_value = {
            "items": [sample_document_read],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "pages": 1,
        }
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total"] == 1
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["id"] == 1
        assert response_data["items"][0]["filename"] == "test_document.pdf"

    @patch('app.api.document_router.get_document_service')
    def test_list_documents_with_filters(
        self, mock_get_service, client, sample_document_read
    ):
        """Test document listing with filters."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.search_documents.return_value = {
            "items": [sample_document_read],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "pages": 1,
        }
        mock_get_service.return_value = mock_service
        
        # Execute with filters
        response = client.get(
            "/api/v1/documents/",
            params={
                "search": "test",
                "document_type": "general_document",
                "status": "available",
                "project_id": "1",
                "sort_by": "created_at",
                "sort_order": "desc",
            }
        )
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total"] == 1

    @patch('app.api.document_router.get_document_service')
    def test_get_document_success(
        self, mock_get_service, client, sample_document_read
    ):
        """Test successful document retrieval."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.get_document.return_value = sample_document_read
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/1")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["filename"] == "test_document.pdf"
        assert response_data["document_type"] == "general_document"

    @patch('app.api.document_router.get_document_service')
    def test_get_document_not_found(
        self, mock_get_service, client
    ):
        """Test document retrieval when document doesn't exist."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.get_document.side_effect = DocumentNotFoundError("Document not found")
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/999")
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "Document not found" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_get_document_access_denied(
        self, mock_get_service, client
    ):
        """Test document retrieval with access denied."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.get_document.side_effect = ValidationError("Access denied")
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/1")
        
        # Assertions
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        assert "Access denied" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_download_document_success(
        self, mock_get_service, client, sample_file_content
    ):
        """Test successful document download."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.download_document.return_value = (
            sample_file_content, "test_document.pdf", "application/pdf"
        )
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/1/download")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == "attachment; filename=test_document.pdf"
        assert response.content == sample_file_content

    @patch('app.api.document_router.get_document_service')
    def test_download_document_not_found(
        self, mock_get_service, client
    ):
        """Test document download when document doesn't exist."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.download_document.side_effect = DocumentNotFoundError("Document not found")
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/999/download")
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "Document not found" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_update_document_success(
        self, mock_get_service, client, sample_document_read
    ):
        """Test successful document update."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.update_document.return_value = sample_document_read
        mock_get_service.return_value = mock_service
        
        # Prepare update data
        update_data = {
            "description": "Updated description",
            "tags": "updated, tags",
            "is_public": True,
        }
        
        # Execute
        response = client.put("/api/v1/documents/1", json=update_data)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["filename"] == "test_document.pdf"

    @patch('app.api.document_router.get_document_service')
    def test_update_document_not_found(
        self, mock_get_service, client
    ):
        """Test document update when document doesn't exist."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.update_document.side_effect = DocumentNotFoundError("Document not found")
        mock_get_service.return_value = mock_service
        
        # Prepare update data
        update_data = {"description": "Updated description"}
        
        # Execute
        response = client.put("/api/v1/documents/999", json=update_data)
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "Document not found" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_delete_document_success(
        self, mock_get_service, client
    ):
        """Test successful document deletion."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.delete_document.return_value = True
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.delete("/api/v1/documents/1")
        
        # Assertions
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch('app.api.document_router.get_document_service')
    def test_delete_document_not_found(
        self, mock_get_service, client
    ):
        """Test document deletion when document doesn't exist."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.delete_document.side_effect = DocumentNotFoundError("Document not found")
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.delete("/api/v1/documents/999")
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "Document not found" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_get_documents_by_entity_success(
        self, mock_get_service, client
    ):
        """Test successful document retrieval by entity."""
        # Mock service
        mock_service = AsyncMock()
        sample_summary = DocumentSummary(
            id=1,
            filename="test_document.pdf",
            document_type=DocumentType.GENERAL_DOCUMENT,
            file_size=1024,
            file_size_human="1.0 KB",
            mime_type="application/pdf",
            status=DocumentStatus.AVAILABLE,
            created_at=sample_document.created_at,
            download_count=0,
        )
        mock_service.get_documents_by_entity.return_value = {
            "items": [sample_summary],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "pages": 1,
        }
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/entity/project/1")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total"] == 1
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["id"] == 1

    @patch('app.api.document_router.get_document_service')
    def test_get_documents_by_entity_invalid_type(
        self, mock_get_service, client
    ):
        """Test document retrieval with invalid entity type."""
        # Mock service (should not be called)
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/entity/invalid_type/1")
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "Invalid entity type" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_get_document_statistics(
        self, mock_get_service, client
    ):
        """Test document statistics retrieval."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.get_document_statistics.return_value = {
            "total_documents": 100,
            "total_size_bytes": 1024000,
            "total_size_human": "1.0 MB",
            "documents_by_type": {
                "general_document": 50,
                "project_photo": 30,
            },
            "documents_by_status": {
                "available": 80,
                "quarantined": 20,
            },
            "documents_by_mime_type": {
                "application/pdf": 40,
                "image/jpeg": 30,
            },
            "most_downloaded": [],
            "recent_uploads": [],
            "storage_usage_by_entity": {
                "project": {"count": 10, "total_size": 100000},
                "resource": {"count": 15, "total_size": 150000},
            },
        }
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.get("/api/v1/documents/stats/overview")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total_documents"] == 100
        assert response_data["total_size_bytes"] == 1024000
        assert response_data["total_size_human"] == "1.0 MB"

    @patch('app.api.document_router.get_document_service')
    def test_quarantine_document_success(
        self, mock_get_service, client
    ):
        """Test successful document quarantine."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.quarantine_document.return_value = True
        mock_get_service.return_value = mock_service
        
        # Prepare form data
        data = {"reason": "Suspicious content detected"}
        
        # Execute
        response = client.post("/api/v1/documents/1/quarantine", data=data)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert "quarantined" in response_data["message"]

    @patch('app.api.document_router.get_document_service')
    def test_quarantine_document_not_found(
        self, mock_get_service, client
    ):
        """Test document quarantine when document doesn't exist."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.quarantine_document.side_effect = DocumentNotFoundError("Document not found")
        mock_get_service.return_value = mock_service
        
        # Prepare form data
        data = {"reason": "Test quarantine"}
        
        # Execute
        response = client.post("/api/v1/documents/999/quarantine", data=data)
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "Document not found" in response_data["detail"]

    @patch('app.api.document_router.get_document_service')
    def test_cleanup_orphaned_files_success(
        self, mock_get_service, client
    ):
        """Test successful orphaned file cleanup."""
        # Mock service
        mock_service = AsyncMock()
        mock_service.cleanup_orphaned_files.return_value = [
            "/path/to/orphaned1.txt",
            "/path/to/orphaned2.txt"
        ]
        mock_get_service.return_value = mock_service
        
        # Execute
        response = client.post("/api/v1/documents/cleanup/orphaned")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["message"] == "Cleaned up 2 orphaned files"
        assert len(response_data["cleaned_files"]) == 2
