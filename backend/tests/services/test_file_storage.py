"""
Tests for file storage service functionality.

This test suite covers file validation, storage operations, security checks,
and cleanup functionality.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import tempfile
import os

from app.models.document import Document, DocumentType, DocumentStatus
from app.services.file_storage import FileStorageService
from app.services.exceptions import (
    FileValidationError,
    StorageError,
    FileNotFoundError,
    QuarantineError,
)


class TestFileStorageService:
    """Test cases for FileStorageService."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def storage_service(self, temp_storage_dir):
        """File storage service with temporary storage."""
        with patch('app.services.file_storage.settings') as mock_settings:
            mock_settings.upload_storage_path = temp_storage_dir
            mock_settings.upload_quarantine_path = os.path.join(temp_storage_dir, 'quarantine')
            mock_settings.upload_allowed_extensions = "pdf,doc,docx,txt,jpg,jpeg,png,gif,bmp,tiff,zip,rar,7z"
            mock_settings.upload_max_size = 10 * 1024 * 1024  # 10MB
            mock_settings.upload_cleanup_interval_hours = 24
            
            service = FileStorageService()
            return service

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
        )

    def test_validate_file_success(self, storage_service, sample_file_content):
        """Test successful file validation."""
        # Create mock upload file
        mock_file = MagicMock()
        mock_file.filename = "test_document.pdf"
        mock_file.file.read.return_value = sample_file_content
        mock_file.file.seek = MagicMock()
        
        # Execute
        filename, mime_type, file_extension, file_size = storage_service.validate_file(
            mock_file, DocumentType.GENERAL_DOCUMENT
        )
        
        # Assertions
        assert filename == "test_document.pdf"
        assert mime_type == "application/pdf"
        assert file_extension == "pdf"
        assert file_size == len(sample_file_content)

    def test_validate_file_size_exceeded(self, storage_service):
        """Test file validation with size exceeded."""
        # Create mock upload file with large size
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        mock_file = MagicMock()
        mock_file.filename = "large_file.pdf"
        mock_file.file.read.return_value = large_content
        mock_file.file.seek = MagicMock()
        
        # Execute and assert
        with pytest.raises(FileValidationError, match="File size.*exceeds maximum"):
            storage_service.validate_file(mock_file, DocumentType.GENERAL_DOCUMENT)

    def test_validate_file_empty(self, storage_service):
        """Test file validation with empty file."""
        # Create mock upload file with empty content
        mock_file = MagicMock()
        mock_file.filename = "empty_file.pdf"
        mock_file.file.read.return_value = b""
        mock_file.file.seek = MagicMock()
        
        # Execute and assert
        with pytest.raises(FileValidationError, match="Empty files are not allowed"):
            storage_service.validate_file(mock_file, DocumentType.GENERAL_DOCUMENT)

    def test_validate_file_invalid_extension(self, storage_service, sample_file_content):
        """Test file validation with invalid extension."""
        # Create mock upload file with invalid extension
        mock_file = MagicMock()
        mock_file.filename = "test_document.exe"
        mock_file.file.read.return_value = sample_file_content
        mock_file.file.seek = MagicMock()
        
        # Execute and assert
        with pytest.raises(FileValidationError, match="File extension.*is not allowed"):
            storage_service.validate_file(mock_file, DocumentType.GENERAL_DOCUMENT)

    def test_validate_file_image_type_mismatch(self, storage_service, sample_file_content):
        """Test file validation with image document type but non-image file."""
        # Create mock upload file
        mock_file = MagicMock()
        mock_file.filename = "test_document.pdf"
        mock_file.file.read.return_value = sample_file_content
        mock_file.file.seek = MagicMock()
        
        # Execute and assert
        with pytest.raises(FileValidationError, match="Document type.*requires an image file"):
            storage_service.validate_file(mock_file, DocumentType.PROJECT_PHOTO)

    def test_extract_extension(self, storage_service):
        """Test file extension extraction."""
        test_cases = [
            ("document.pdf", "pdf"),
            ("image.jpg", "jpg"),
            ("archive.tar.gz", "gz"),
            ("file", ""),
            (".hidden", ""),
        ]
        
        for filename, expected in test_cases:
            result = storage_service._extract_extension(filename)
            assert result == expected

    def test_detect_mime_type_from_content(self, storage_service):
        """Test MIME type detection from content."""
        test_cases = [
            (b'\x89PNG\r\n\x1a\n', 'image/png'),
            (b'\xff\xd8\xff', 'image/jpeg'),
            (b'%PDF', 'application/pdf'),
            (b'PK\x03\x04', 'application/zip'),
            (b'unknown content', None),
        ]
        
        for content, expected in test_cases:
            result = storage_service._detect_mime_type_from_content(content[:1024])
            assert result == expected

    def test_sanitize_filename(self, storage_service):
        """Test filename sanitization."""
        test_cases = [
            ("normal_file.pdf", "normal_file.pdf"),
            ("file<with>bad:chars", "file_with_bad_chars"),
            ("file/with\\slashes", "file_with_slashes"),
            ("file|with?wildcards*", "file_with_wildcards_"),
            ("very_long_filename_that_exceeds_the_maximum_length_limit_and_should_be_truncated.pdf", 
             "very_long_filename_that_exceeds_the_maximum_length_limit_and_should_be_truncated.pdf"),
        ]
        
        for input_filename, expected in test_cases:
            result = storage_service._sanitize_filename(input_filename)
            assert result == expected
            # Ensure no dangerous characters remain
            dangerous_chars = '<>:"/\\|?*'
            for char in dangerous_chars:
                assert char not in result

    def test_get_storage_subdir(self, storage_service):
        """Test storage subdirectory mapping."""
        test_cases = [
            (DocumentType.PROJECT_PHOTO, "images"),
            (DocumentType.RESOURCE_PHOTO, "images"),
            (DocumentType.MAINTENANCE_PHOTO, "images"),
            (DocumentType.IMAGE, "images"),
            (DocumentType.ARCHIVE, "archives"),
            (DocumentType.GENERAL_DOCUMENT, "documents"),
            (DocumentType.MANUAL, "documents"),
        ]
        
        for document_type, expected in test_cases:
            result = storage_service._get_storage_subdir(document_type)
            assert result == expected

    def test_generate_storage_path(self, storage_service):
        """Test storage path generation."""
        # Execute
        relative_path, sanitized_filename = storage_service.generate_storage_path(
            "test document.pdf", DocumentType.GENERAL_DOCUMENT
        )
        
        # Assertions
        assert relative_path.startswith("documents/")
        assert relative_path.endswith(".pdf")
        assert sanitized_filename != "test document.pdf"  # Should be sanitized
        assert "_" in sanitized_filename  # Should contain unique ID

    def test_save_file(self, storage_service, temp_storage_dir, sample_file_content):
        """Test file saving."""
        # Setup
        storage_path = "documents/2024/01/test_file.pdf"
        
        # Execute
        storage_service.save_file(
            MagicMock(), storage_path, sample_file_content
        )
        
        # Assertions
        full_path = Path(temp_storage_dir) / storage_path
        assert full_path.exists()
        assert full_path.read_bytes() == sample_file_content

    def test_calculate_checksum(self, storage_service, sample_file_content):
        """Test checksum calculation."""
        # Execute
        checksum = storage_service.calculate_checksum(sample_file_content)
        
        # Assertions
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 hex length
        
        # Should be deterministic
        checksum2 = storage_service.calculate_checksum(sample_file_content)
        assert checksum == checksum2

    def test_get_file_path(self, storage_service, sample_document):
        """Test file path retrieval."""
        # Execute
        file_path = storage_service.get_file_path(sample_document)
        
        # Assertions
        expected_path = Path(storage_service.storage_path) / sample_document.file_path
        assert file_path == expected_path

    def test_file_exists(self, storage_service, temp_storage_dir, sample_document):
        """Test file existence check."""
        # Setup - create a file
        file_path = Path(temp_storage_dir) / sample_document.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"test content")
        
        # Execute
        exists = storage_service.file_exists(sample_document)
        
        # Assertions
        assert exists is True
        
        # Test non-existent file
        sample_document.file_path = "non/existent/path.pdf"
        exists = storage_service.file_exists(sample_document)
        assert exists is False

    def test_get_file_content(self, storage_service, temp_storage_dir, sample_document, sample_file_content):
        """Test file content retrieval."""
        # Setup - create a file
        file_path = Path(temp_storage_dir) / sample_document.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(sample_file_content)
        
        # Execute
        content = storage_service.get_file_content(sample_document)
        
        # Assertions
        assert content == sample_file_content

    def test_get_file_content_not_found(self, storage_service, sample_document):
        """Test file content retrieval when file doesn't exist."""
        # Execute and assert
        with pytest.raises(FileNotFoundError):
            storage_service.get_file_content(sample_document)

    def test_delete_file(self, storage_service, temp_storage_dir, sample_document, sample_file_content):
        """Test file deletion."""
        # Setup - create a file
        file_path = Path(temp_storage_dir) / sample_document.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(sample_file_content)
        
        # Execute
        storage_service.delete_file(sample_document)
        
        # Assertions
        assert not file_path.exists()

    def test_quarantine_file(self, storage_service, temp_storage_dir, sample_document, sample_file_content):
        """Test file quarantine."""
        # Setup - create a file
        file_path = Path(temp_storage_dir) / sample_document.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(sample_file_content)
        
        # Execute
        storage_service.quarantine_file(sample_document, "Test quarantine")
        
        # Assertions
        assert not file_path.exists()
        
        # Check quarantine file exists
        quarantine_file = Path(temp_storage_dir) / "quarantine" / f"{sample_document.id}_{sample_document.original_filename}"
        assert quarantine_file.exists()
        
        # Check quarantine log exists
        quarantine_log = Path(temp_storage_dir) / "quarantine" / f"{sample_document.id}.log"
        assert quarantine_log.exists()

    def test_quarantine_file_not_found(self, storage_service, sample_document):
        """Test file quarantine when file doesn't exist."""
        # Execute - should not raise exception
        storage_service.quarantine_file(sample_document, "Test quarantine")

    def test_cleanup_empty_directories(self, storage_service, temp_storage_dir):
        """Test empty directory cleanup."""
        # Setup - create nested empty directories
        empty_dir = Path(temp_storage_dir) / "documents" / "2024" / "01"
        empty_dir.mkdir(parents=True, exist_ok=True)
        
        # Execute
        storage_service._cleanup_empty_directories(empty_dir)
        
        # Assertions
        assert not empty_dir.exists()
        assert not empty_dir.parent.exists()
        # Storage root should still exist
        assert Path(temp_storage_dir).exists()

    def test_get_storage_stats(self, storage_service, temp_storage_dir, sample_file_content):
        """Test storage statistics."""
        # Setup - create some files
        files_to_create = [
            "documents/file1.pdf",
            "images/image1.jpg",
            "images/image2.png",
            "archives/archive1.zip",
        ]
        
        for file_path in files_to_create:
            full_path = Path(temp_storage_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(sample_file_content)
        
        # Execute
        stats = storage_service.get_storage_stats()
        
        # Assertions
        assert stats['total_files'] == len(files_to_create)
        assert stats['total_size_bytes'] == len(sample_file_content) * len(files_to_create)
        assert '.pdf' in stats['files_by_type']
        assert '.jpg' in stats['files_by_type']
        assert '.png' in stats['files_by_type']
        assert '.zip' in stats['files_by_type']

    def test_contains_suspicious_content(self, storage_service):
        """Test suspicious content detection."""
        # Test cases
        test_cases = [
            (b"<script>alert('xss')</script>", True),
            (b"javascript:void(0)", True),
            (b"<iframe src='evil.com'></iframe>", True),
            (b"eval(malicious_code)", True),
            (b"normal document content", False),
            (b"<p>Safe HTML content</p>", False),
        ]
        
        for content, expected in test_cases:
            result = storage_service._contains_suspicious_content(content)
            assert result == expected

    def test_get_expected_mime_types(self, storage_service):
        """Test expected MIME types for extensions."""
        test_cases = [
            ('pdf', ['application/pdf']),
            ('jpg', ['image/jpeg']),
            ('png', ['image/png']),
            ('docx', ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']),
            ('unknown', []),
        ]
        
        for extension, expected in test_cases:
            result = storage_service._get_expected_mime_types(extension)
            assert result == expected
