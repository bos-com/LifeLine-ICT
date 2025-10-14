"""
File storage service for document management.

This service handles secure file storage operations including upload validation,
file organization, security checks, and storage management. It provides a
unified interface for file operations while maintaining security and integrity
of uploaded documents in the LifeLine-ICT system.

The service supports local filesystem storage with organized directory structures,
file validation, quarantine capabilities, and cleanup operations for orphaned files.
"""

from __future__ import annotations

import hashlib
import mimetypes
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple

from fastapi import UploadFile

from ..core.config import settings
from ..models.document import Document, DocumentStatus, DocumentType
from .exceptions import (
    FileValidationError,
    StorageError,
    FileNotFoundError,
    QuarantineError,
)


class FileStorageService:
    """
    Service for managing file storage operations.
    
    Provides secure file upload, validation, organization, and management
    capabilities for the LifeLine-ICT document system. Handles file validation,
    storage organization, security checks, and cleanup operations.
    
    Attributes
    ----------
    storage_path : Path
        Base directory for document storage.
    quarantine_path : Path
        Directory for quarantined files.
    allowed_extensions : set
        Set of allowed file extensions.
    max_file_size : int
        Maximum allowed file size in bytes.
    """
    
    def __init__(self):
        """Initialize the file storage service with configuration."""
        self.storage_path = Path(settings.upload_storage_path)
        self.quarantine_path = Path(settings.upload_quarantine_path)
        self.allowed_extensions = set(
            ext.strip().lower() 
            for ext in settings.upload_allowed_extensions.split(',')
        )
        self.max_file_size = settings.upload_max_size
        
        # Ensure storage directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """
        Ensure that storage and quarantine directories exist.
        
        Creates the necessary directory structure for file storage
        and quarantine operations.
        """
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self.quarantine_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for organization
            for subdir in ['documents', 'images', 'archives', 'temp']:
                (self.storage_path / subdir).mkdir(exist_ok=True)
                
        except Exception as e:
            raise StorageError(f"Failed to create storage directories: {e}")
    
    def validate_file(
        self, 
        file: UploadFile, 
        document_type: DocumentType
    ) -> Tuple[str, str, str, int]:
        """
        Validate uploaded file for security and compatibility.
        
        Parameters
        ----------
        file : UploadFile
            The uploaded file to validate.
        document_type : DocumentType
            The expected document type for additional validation.
            
        Returns
        -------
        Tuple[str, str, str, int]
            Tuple containing (filename, mime_type, file_extension, file_size).
            
        Raises
        ------
        FileValidationError
            If file validation fails.
        StorageError
            If file reading fails.
        """
        try:
            # Read file content for validation
            content = file.file.read()
            file_size = len(content)
            
            # Reset file pointer for later use
            file.file.seek(0)
            
            # Validate file size
            if file_size > self.max_file_size:
                raise FileValidationError(
                    f"File size {file_size} exceeds maximum allowed size "
                    f"{self.max_file_size} bytes"
                )
            
            if file_size == 0:
                raise FileValidationError("Empty files are not allowed")
            
            # Extract and validate file extension
            original_filename = file.filename or "unnamed"
            file_extension = self._extract_extension(original_filename)
            
            if file_extension not in self.allowed_extensions:
                raise FileValidationError(
                    f"File extension '{file_extension}' is not allowed. "
                    f"Allowed extensions: {', '.join(self.allowed_extensions)}"
                )
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(original_filename)
            if not mime_type:
                # Try to detect from content
                mime_type = self._detect_mime_type_from_content(content[:1024])
            
            if not mime_type:
                raise FileValidationError("Could not determine file type")
            
            # Validate MIME type against extension
            expected_mime_types = self._get_expected_mime_types(file_extension)
            if mime_type not in expected_mime_types:
                raise FileValidationError(
                    f"MIME type '{mime_type}' does not match file extension "
                    f"'{file_extension}'"
                )
            
            # Additional validation based on document type
            self._validate_by_document_type(
                file_extension, mime_type, document_type, content
            )
            
            return original_filename, mime_type, file_extension, file_size
            
        except FileValidationError:
            raise
        except Exception as e:
            raise StorageError(f"File validation failed: {e}")
    
    def _extract_extension(self, filename: str) -> str:
        """
        Extract file extension from filename.
        
        Parameters
        ----------
        filename : str
            Original filename.
            
        Returns
        -------
        str
            File extension in lowercase.
        """
        return Path(filename).suffix.lstrip('.').lower()
    
    def _detect_mime_type_from_content(self, content: bytes) -> Optional[str]:
        """
        Detect MIME type from file content.
        
        Parameters
        ----------
        content : bytes
            First 1024 bytes of file content.
            
        Returns
        -------
        str, optional
            Detected MIME type or None.
        """
        # Simple magic number detection
        magic_numbers = {
            b'\x89PNG\r\n\x1a\n': 'image/png',
            b'\xff\xd8\xff': 'image/jpeg',
            b'GIF87a': 'image/gif',
            b'GIF89a': 'image/gif',
            b'%PDF': 'application/pdf',
            b'PK\x03\x04': 'application/zip',
            b'\x50\x4b\x03\x04': 'application/zip',
        }
        
        for magic, mime_type in magic_numbers.items():
            if content.startswith(magic):
                return mime_type
        
        return None
    
    def _get_expected_mime_types(self, extension: str) -> List[str]:
        """
        Get expected MIME types for a file extension.
        
        Parameters
        ----------
        extension : str
            File extension.
            
        Returns
        -------
        List[str]
            List of expected MIME types.
        """
        mime_type_map = {
            'pdf': ['application/pdf'],
            'doc': ['application/msword'],
            'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            'txt': ['text/plain'],
            'jpg': ['image/jpeg'],
            'jpeg': ['image/jpeg'],
            'png': ['image/png'],
            'gif': ['image/gif'],
            'bmp': ['image/bmp'],
            'tiff': ['image/tiff'],
            'zip': ['application/zip'],
            'rar': ['application/vnd.rar'],
            '7z': ['application/x-7z-compressed'],
        }
        
        return mime_type_map.get(extension, [])
    
    def _validate_by_document_type(
        self,
        extension: str,
        mime_type: str,
        document_type: DocumentType,
        content: bytes
    ) -> None:
        """
        Validate file based on document type requirements.
        
        Parameters
        ----------
        extension : str
            File extension.
        mime_type : str
            MIME type.
        document_type : DocumentType
            Expected document type.
        content : bytes
            File content.
            
        Raises
        ------
        FileValidationError
            If validation fails.
        """
        # Image documents should be images
        image_types = {
            DocumentType.PROJECT_PHOTO,
            DocumentType.RESOURCE_PHOTO,
            DocumentType.MAINTENANCE_PHOTO,
            DocumentType.LOCATION_PHOTO,
            DocumentType.INSTALLATION_PHOTO,
            DocumentType.IMAGE,
        }
        
        if document_type in image_types and not mime_type.startswith('image/'):
            raise FileValidationError(
                f"Document type '{document_type}' requires an image file"
            )
        
        # Document types should be text-based
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
        
        if document_type in document_types:
            # Check for suspicious content in documents
            if self._contains_suspicious_content(content):
                raise FileValidationError(
                    "File contains potentially malicious content"
                )
    
    def _contains_suspicious_content(self, content: bytes) -> bool:
        """
        Check if file content contains suspicious patterns.
        
        Parameters
        ----------
        content : bytes
            File content to check.
            
        Returns
        -------
        bool
            True if suspicious content is detected.
        """
        # Simple heuristics for suspicious content
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'<iframe',
            b'<object',
            b'<embed',
            b'eval(',
            b'exec(',
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in suspicious_patterns)
    
    def generate_storage_path(
        self,
        filename: str,
        document_type: DocumentType
    ) -> Tuple[str, str]:
        """
        Generate storage path and sanitized filename for a document.
        
        Parameters
        ----------
        filename : str
            Original filename.
        document_type : DocumentType
            Document type for organization.
            
        Returns
        -------
        Tuple[str, str]
            Tuple containing (relative_path, sanitized_filename).
        """
        # Sanitize filename
        sanitized_filename = self._sanitize_filename(filename)
        
        # Generate unique filename to prevent conflicts
        unique_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(sanitized_filename)
        unique_filename = f"{name}_{unique_id}{ext}"
        
        # Determine storage subdirectory based on document type
        subdir = self._get_storage_subdir(document_type)
        
        # Create date-based organization
        date_path = datetime.now().strftime("%Y/%m")
        
        # Generate relative path
        relative_path = f"{subdir}/{date_path}/{unique_filename}"
        
        return relative_path, unique_filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage.
        
        Parameters
        ----------
        filename : str
            Original filename.
            
        Returns
        -------
        str
            Sanitized filename.
        """
        # Remove or replace dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Limit length
        if len(sanitized) > 200:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:200-len(ext)] + ext
        
        return sanitized
    
    def _get_storage_subdir(self, document_type: DocumentType) -> str:
        """
        Get storage subdirectory based on document type.
        
        Parameters
        ----------
        document_type : DocumentType
            Document type.
            
        Returns
        -------
        str
            Subdirectory name.
        """
        # Map document types to storage directories
        type_mapping = {
            # Images
            DocumentType.PROJECT_PHOTO: 'images',
            DocumentType.RESOURCE_PHOTO: 'images',
            DocumentType.MAINTENANCE_PHOTO: 'images',
            DocumentType.LOCATION_PHOTO: 'images',
            DocumentType.INSTALLATION_PHOTO: 'images',
            DocumentType.IMAGE: 'images',
            
            # Archives
            DocumentType.ARCHIVE: 'archives',
            
            # Default to documents
        }
        
        return type_mapping.get(document_type, 'documents')
    
    def save_file(
        self,
        file: UploadFile,
        storage_path: str,
        content: bytes
    ) -> None:
        """
        Save file content to storage.
        
        Parameters
        ----------
        file : UploadFile
            The uploaded file.
        storage_path : str
            Relative path where file should be stored.
        content : bytes
            File content to save.
            
        Raises
        ------
        StorageError
            If file saving fails.
        """
        try:
            full_path = self.storage_path / storage_path
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file content
            with open(full_path, 'wb') as f:
                f.write(content)
            
            # Set appropriate permissions
            os.chmod(full_path, 0o644)
            
        except Exception as e:
            raise StorageError(f"Failed to save file: {e}")
    
    def calculate_checksum(self, content: bytes) -> str:
        """
        Calculate SHA-256 checksum of file content.
        
        Parameters
        ----------
        content : bytes
            File content.
            
        Returns
        -------
        str
            SHA-256 checksum as hexadecimal string.
        """
        return hashlib.sha256(content).hexdigest()
    
    def get_file_path(self, document: Document) -> Path:
        """
        Get full file path for a document.
        
        Parameters
        ----------
        document : Document
            Document model instance.
            
        Returns
        -------
        Path
            Full file path.
        """
        return self.storage_path / document.file_path
    
    def file_exists(self, document: Document) -> bool:
        """
        Check if file exists in storage.
        
        Parameters
        ----------
        document : Document
            Document model instance.
            
        Returns
        -------
        bool
            True if file exists.
        """
        return self.get_file_path(document).exists()
    
    def get_file_content(self, document: Document) -> bytes:
        """
        Read file content from storage.
        
        Parameters
        ----------
        document : Document
            Document model instance.
            
        Returns
        -------
        bytes
            File content.
            
        Raises
        ------
        FileNotFoundError
            If file does not exist.
        StorageError
            If file reading fails.
        """
        file_path = self.get_file_path(document)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise StorageError(f"Failed to read file: {e}")
    
    def delete_file(self, document: Document) -> None:
        """
        Delete file from storage.
        
        Parameters
        ----------
        document : Document
            Document model instance.
            
        Raises
        ------
        StorageError
            If file deletion fails.
        """
        try:
            file_path = self.get_file_path(document)
            
            if file_path.exists():
                file_path.unlink()
                
                # Remove empty directories
                self._cleanup_empty_directories(file_path.parent)
                
        except Exception as e:
            raise StorageError(f"Failed to delete file: {e}")
    
    def _cleanup_empty_directories(self, directory: Path) -> None:
        """
        Remove empty directories up to storage root.
        
        Parameters
        ----------
        directory : Path
            Directory to start cleanup from.
        """
        try:
            # Don't remove storage root or quarantine directories
            if directory == self.storage_path or directory == self.quarantine_path:
                return
            
            # Remove if empty and not storage root
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
                # Recursively clean up parent directories
                self._cleanup_empty_directories(directory.parent)
                
        except OSError:
            # Directory not empty or permission error
            pass
    
    def quarantine_file(self, document: Document, reason: str) -> None:
        """
        Move file to quarantine directory.
        
        Parameters
        ----------
        document : Document
            Document to quarantine.
        reason : str
            Reason for quarantine.
            
        Raises
        ------
        QuarantineError
            If quarantine operation fails.
        """
        try:
            source_path = self.get_file_path(document)
            quarantine_filename = f"{document.id}_{document.original_filename}"
            quarantine_path = self.quarantine_path / quarantine_filename
            
            if source_path.exists():
                shutil.move(str(source_path), str(quarantine_path))
                
                # Log quarantine action
                quarantine_log = self.quarantine_path / f"{document.id}.log"
                with open(quarantine_log, 'w') as f:
                    f.write(f"Quarantined: {datetime.now().isoformat()}\n")
                    f.write(f"Reason: {reason}\n")
                    f.write(f"Document ID: {document.id}\n")
                    f.write(f"Original Path: {document.file_path}\n")
                    
        except Exception as e:
            raise QuarantineError(f"Failed to quarantine file: {e}")
    
    def cleanup_orphaned_files(self) -> List[str]:
        """
        Clean up orphaned files in storage.
        
        Returns
        -------
        List[str]
            List of cleaned up file paths.
        """
        cleaned_files = []
        
        try:
            # Walk through storage directory
            for root, dirs, files in os.walk(self.storage_path):
                for filename in files:
                    file_path = Path(root) / filename
                    
                    # Skip quarantine directory
                    if self.quarantine_path in file_path.parents:
                        continue
                    
                    # Check if file is older than cleanup interval
                    file_age = datetime.now().timestamp() - file_path.stat().st_mtime
                    cleanup_interval_seconds = settings.upload_cleanup_interval_hours * 3600
                    
                    if file_age > cleanup_interval_seconds:
                        # Check if file is referenced in database
                        # This would require database access - implement in service layer
                        # For now, just log the file
                        cleaned_files.append(str(file_path))
                        
        except Exception as e:
            raise StorageError(f"Failed to cleanup orphaned files: {e}")
        
        return cleaned_files
    
    def get_storage_stats(self) -> Dict[str, any]:
        """
        Get storage statistics.
        
        Returns
        -------
        Dict[str, any]
            Storage statistics including total size, file count, etc.
        """
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'files_by_type': {},
            'oldest_file': None,
            'newest_file': None,
        }
        
        try:
            for root, dirs, files in os.walk(self.storage_path):
                for filename in files:
                    file_path = Path(root) / filename
                    
                    # Skip quarantine directory
                    if self.quarantine_path in file_path.parents:
                        continue
                    
                    try:
                        stat = file_path.stat()
                        stats['total_files'] += 1
                        stats['total_size_bytes'] += stat.st_size
                        
                        # Track file types
                        ext = file_path.suffix.lower()
                        stats['files_by_type'][ext] = stats['files_by_type'].get(ext, 0) + 1
                        
                        # Track oldest/newest files
                        mtime = stat.st_mtime
                        if stats['oldest_file'] is None or mtime < stats['oldest_file']:
                            stats['oldest_file'] = mtime
                        if stats['newest_file'] is None or mtime > stats['newest_file']:
                            stats['newest_file'] = mtime
                            
                    except OSError:
                        # Skip files that can't be accessed
                        continue
                        
        except Exception as e:
            raise StorageError(f"Failed to get storage stats: {e}")
        
        return stats
