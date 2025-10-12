"""
Tests for document service functionality.

This test suite covers all document management operations including upload,
validation, storage, retrieval, and business logic enforcement.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile
from io import BytesIO

from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import DocumentUploadResponse, DocumentRead
from app.services.document_service import DocumentService
from app.services.exceptions import (
    DocumentNotFoundError,
    FileValidationError,
    StorageError,
    ValidationError,
)


class TestDocumentService:
    """Test cases for DocumentService."""

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_repository(self):
        """Mock document repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_storage_service(self):
        """Mock file storage service."""
        return MagicMock()

    @pytest.fixture
    def document_service(self, mock_session, mock_repository, mock_storage_service):
        """Document service with mocked dependencies."""
        service = DocumentService(mock_session)
        service.repository = mock_repository
        service.storage_service = mock_storage_service
        return service

    @pytest.fixture
    def sample_file(self):
        """Sample file for testing."""
        content = b"Sample file content for testing"
        file_obj = BytesIO(content)
        upload_file = UploadFile(
            filename="test_document.pdf",
            file=file_obj,
            size=len(content)
        )
        return upload_file

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
            project_id=None,
            resource_id=None,
            maintenance_ticket_id=None,
            location_id=None,
            sensor_site_id=None,
            uploaded_by_user_id=None,
        )

    @pytest.mark.asyncio
    async def test_upload_document_success(
        self, document_service, sample_file, sample_document
    ):
        """Test successful document upload."""
        # Mock validation
        document_service.storage_service.validate_file.return_value = (
            "test_document.pdf", "application/pdf", "pdf", 1024
        )
        
        # Mock file content reading
        sample_file.file.read = MagicMock(return_value=b"Sample file content")
        sample_file.file.seek = MagicMock()
        
        # Mock storage operations
        document_service.storage_service.generate_storage_path.return_value = (
            "documents/2024/01/test_document_12345678.pdf",
            "test_document_12345678.pdf"
        )
        document_service.storage_service.calculate_checksum.return_value = "abc123def456"
        
        # Mock repository operations
        document_service.repository.create_document.return_value = sample_document
        
        # Mock validation
        document_service._validate_relationships = AsyncMock()
        
        # Execute
        result = await document_service.upload_document(
            file=sample_file,
            document_type=DocumentType.GENERAL_DOCUMENT,
            description="Test document",
            tags="test, sample"
        )
        
        # Assertions
        assert isinstance(result, DocumentUploadResponse)
        assert result.success is True
        assert result.document_id == 1
        assert result.filename == "test_document.pdf"
        assert result.status == DocumentStatus.AVAILABLE
        
        # Verify method calls
        document_service.storage_service.validate_file.assert_called_once()
        document_service.storage_service.generate_storage_path.assert_called_once()
        document_service.storage_service.save_file.assert_called_once()
        document_service.repository.create_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_document_validation_failure(
        self, document_service, sample_file
    ):
        """Test document upload with validation failure."""
        # Mock validation failure
        document_service.storage_service.validate_file.side_effect = FileValidationError(
            "Invalid file type"
        )
        
        # Execute and assert
        with pytest.raises(FileValidationError):
            await document_service.upload_document(file=sample_file)

    @pytest.mark.asyncio
    async def test_upload_document_storage_failure(
        self, document_service, sample_file
    ):
        """Test document upload with storage failure."""
        # Mock validation success
        document_service.storage_service.validate_file.return_value = (
            "test_document.pdf", "application/pdf", "pdf", 1024
        )
        
        # Mock file content reading
        sample_file.file.read = MagicMock(return_value=b"Sample file content")
        sample_file.file.seek = MagicMock()
        
        # Mock storage operations
        document_service.storage_service.generate_storage_path.return_value = (
            "documents/2024/01/test_document_12345678.pdf",
            "test_document_12345678.pdf"
        )
        document_service.storage_service.calculate_checksum.return_value = "abc123def456"
        document_service.storage_service.save_file.side_effect = StorageError(
            "Storage failed"
        )
        
        # Mock validation
        document_service._validate_relationships = AsyncMock()
        
        # Execute and assert
        with pytest.raises(StorageError):
            await document_service.upload_document(file=sample_file)

    @pytest.mark.asyncio
    async def test_get_document_success(
        self, document_service, sample_document
    ):
        """Test successful document retrieval."""
        # Mock repository response
        document_service.repository.get_document_with_relationships.return_value = sample_document
        
        # Execute
        result = await document_service.get_document(document_id=1, user_id=1)
        
        # Assertions
        assert isinstance(result, DocumentRead)
        assert result.id == 1
        assert result.filename == "test_document.pdf"
        
        # Verify method call
        document_service.repository.get_document_with_relationships.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_document_not_found(
        self, document_service
    ):
        """Test document retrieval when document doesn't exist."""
        # Mock repository response
        document_service.repository.get_document_with_relationships.return_value = None
        
        # Execute and assert
        with pytest.raises(DocumentNotFoundError):
            await document_service.get_document(document_id=999, user_id=1)

    @pytest.mark.asyncio
    async def test_get_document_access_denied(
        self, document_service, sample_document
    ):
        """Test document retrieval with access denied."""
        # Mock private document
        sample_document.is_public = False
        
        # Mock repository response
        document_service.repository.get_document_with_relationships.return_value = sample_document
        
        # Execute and assert
        with pytest.raises(ValidationError):
            await document_service.get_document(document_id=1, user_id=None)

    @pytest.mark.asyncio
    async def test_download_document_success(
        self, document_service, sample_document
    ):
        """Test successful document download."""
        # Mock repository response
        document_service.repository.get_by_id.return_value = sample_document
        
        # Mock storage operations
        document_service.storage_service.file_exists.return_value = True
        document_service.storage_service.get_file_content.return_value = b"File content"
        document_service.repository.increment_download_count.return_value = sample_document
        
        # Execute
        content, filename, mime_type = await document_service.download_document(
            document_id=1, user_id=1
        )
        
        # Assertions
        assert content == b"File content"
        assert filename == "test_document.pdf"
        assert mime_type == "application/pdf"
        
        # Verify method calls
        document_service.repository.get_by_id.assert_called_once_with(1)
        document_service.storage_service.file_exists.assert_called_once_with(sample_document)
        document_service.storage_service.get_file_content.assert_called_once_with(sample_document)
        document_service.repository.increment_download_count.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_download_document_file_not_found(
        self, document_service, sample_document
    ):
        """Test document download when file doesn't exist in storage."""
        # Mock repository response
        document_service.repository.get_by_id.return_value = sample_document
        
        # Mock storage operations
        document_service.storage_service.file_exists.return_value = False
        
        # Execute and assert
        with pytest.raises(StorageError):
            await document_service.download_document(document_id=1, user_id=1)

    @pytest.mark.asyncio
    async def test_delete_document_success(
        self, document_service, sample_document
    ):
        """Test successful document deletion."""
        # Mock repository response
        document_service.repository.get_by_id.return_value = sample_document
        
        # Mock storage operations
        document_service.storage_service.file_exists.return_value = True
        document_service.repository.delete = AsyncMock()
        
        # Execute
        result = await document_service.delete_document(document_id=1, user_id=1)
        
        # Assertions
        assert result is True
        
        # Verify method calls
        document_service.storage_service.delete_file.assert_called_once_with(sample_document)
        document_service.repository.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_document_not_found(
        self, document_service
    ):
        """Test document deletion when document doesn't exist."""
        # Mock repository response
        document_service.repository.get_by_id.return_value = None
        
        # Execute and assert
        with pytest.raises(DocumentNotFoundError):
            await document_service.delete_document(document_id=999, user_id=1)

    @pytest.mark.asyncio
    async def test_quarantine_document_success(
        self, document_service, sample_document
    ):
        """Test successful document quarantine."""
        # Mock repository response
        document_service.repository.get_by_id.return_value = sample_document
        document_service.repository.update_document_status = AsyncMock()
        
        # Execute
        result = await document_service.quarantine_document(
            document_id=1, reason="Suspicious content"
        )
        
        # Assertions
        assert result is True
        
        # Verify method calls
        document_service.storage_service.quarantine_file.assert_called_once_with(
            sample_document, "Suspicious content"
        )
        document_service.repository.update_document_status.assert_called_once_with(
            1, DocumentStatus.QUARANTINED
        )

    @pytest.mark.asyncio
    async def test_quarantine_document_not_found(
        self, document_service
    ):
        """Test document quarantine when document doesn't exist."""
        # Mock repository response
        document_service.repository.get_by_id.return_value = None
        
        # Execute and assert
        with pytest.raises(DocumentNotFoundError):
            await document_service.quarantine_document(
                document_id=999, reason="Test"
            )

    @pytest.mark.asyncio
    async def test_cleanup_orphaned_files(
        self, document_service
    ):
        """Test orphaned file cleanup."""
        # Mock storage service response
        document_service.storage_service.cleanup_orphaned_files.return_value = [
            "/path/to/orphaned1.txt",
            "/path/to/orphaned2.txt"
        ]
        
        # Execute
        result = await document_service.cleanup_orphaned_files()
        
        # Assertions
        assert len(result) == 2
        assert "/path/to/orphaned1.txt" in result
        assert "/path/to/orphaned2.txt" in result
        
        # Verify method call
        document_service.storage_service.cleanup_orphaned_files.assert_called_once()

    def test_bytes_to_human_readable(self, document_service):
        """Test bytes to human readable conversion."""
        # Test cases
        test_cases = [
            (1024, "1.0 KB"),
            (1048576, "1.0 MB"),
            (1073741824, "1.0 GB"),
            (512, "512.0 B"),
        ]
        
        for bytes_value, expected in test_cases:
            result = document_service._bytes_to_human_readable(bytes_value)
            assert result == expected

    def test_document_to_read_schema(self, document_service, sample_document):
        """Test document to read schema conversion."""
        # Execute
        result = document_service._document_to_read_schema(sample_document)
        
        # Assertions
        assert isinstance(result, DocumentRead)
        assert result.id == sample_document.id
        assert result.filename == sample_document.filename
        assert result.file_size_human == sample_document.file_size_human
        assert result.is_image == sample_document.is_image
        assert result.is_document == sample_document.is_document

    def test_document_to_summary_schema(self, document_service, sample_document):
        """Test document to summary schema conversion."""
        # Execute
        result = document_service._document_to_summary_schema(sample_document)
        
        # Assertions
        from app.schemas.document import DocumentSummary
        assert isinstance(result, DocumentSummary)
        assert result.id == sample_document.id
        assert result.filename == sample_document.filename
        assert result.document_type == sample_document.document_type
        assert result.status == sample_document.status
