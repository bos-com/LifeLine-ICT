"""
Tests for document repository functionality.

This test suite covers database operations, querying, and relationship management
for document entities.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus, DocumentType
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentSearchQuery


class TestDocumentRepository:
    """Test cases for DocumentRepository."""

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Document repository with mocked session."""
        return DocumentRepository(mock_session)

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

    @pytest.mark.asyncio
    async def test_create_document(self, repository, mock_session, sample_document):
        """Test document creation."""
        # Mock session operations
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Execute
        result = await repository.create_document(
            filename="test_document.pdf",
            original_filename="test_document_12345678.pdf",
            file_path="documents/2024/01/test_document_12345678.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_extension="pdf",
            document_type=DocumentType.GENERAL_DOCUMENT,
            description="Test document",
            tags="test, sample",
            checksum="abc123def456",
            is_public=False,
            project_id=1,
            resource_id=1,
            uploaded_by_user_id=1,
        )
        
        # Assertions
        assert isinstance(result, Document)
        assert result.filename == "test_document.pdf"
        assert result.document_type == DocumentType.GENERAL_DOCUMENT
        assert result.status == DocumentStatus.AVAILABLE
        
        # Verify session operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document_with_relationships(self, repository, mock_session, sample_document):
        """Test document retrieval with relationships."""
        # Mock session execute
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_document
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await repository.get_document_with_relationships(document_id=1)
        
        # Assertions
        assert result == sample_document
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document_with_relationships_not_found(self, repository, mock_session):
        """Test document retrieval when document doesn't exist."""
        # Mock session execute
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await repository.get_document_with_relationships(document_id=999)
        
        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_search_documents(self, repository, mock_session):
        """Test document search functionality."""
        # Create search query
        search_query = DocumentSearchQuery(
            search="test",
            document_type=DocumentType.GENERAL_DOCUMENT,
            status=DocumentStatus.AVAILABLE,
            sort_by="created_at",
            sort_order="desc"
        )
        
        # Mock documents
        sample_docs = [
            Document(id=1, filename="test1.pdf"),
            Document(id=2, filename="test2.pdf"),
        ]
        
        # Mock count query result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2
        
        # Mock main query result
        mock_main_result = MagicMock()
        mock_main_result.scalars.return_value.all.return_value = sample_docs
        
        # Mock session execute
        def mock_execute(query):
            # Return count result for count queries
            if "count" in str(query).lower():
                return mock_count_result
            # Return main result for main queries
            return mock_main_result
        
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        
        # Execute
        documents, total_count = await repository.search_documents(
            search_query, limit=10, offset=0
        )
        
        # Assertions
        assert len(documents) == 2
        assert total_count == 2
        assert documents[0].id == 1
        assert documents[1].id == 2

    @pytest.mark.asyncio
    async def test_search_documents_with_filters(self, repository, mock_session):
        """Test document search with various filters."""
        # Create search query with multiple filters
        search_query = DocumentSearchQuery(
            search="report",
            document_type=DocumentType.PROJECT_REPORT,
            status=DocumentStatus.AVAILABLE,
            mime_type="application/pdf",
            file_extension="pdf",
            is_public=False,
            project_id=1,
            resource_id=1,
            uploaded_by_user_id=1,
            min_file_size=1000,
            max_file_size=10000,
        )
        
        # Mock empty results
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        
        mock_main_result = MagicMock()
        mock_main_result.scalars.return_value.all.return_value = []
        
        # Mock session execute
        def mock_execute(query):
            if "count" in str(query).lower():
                return mock_count_result
            return mock_main_result
        
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        
        # Execute
        documents, total_count = await repository.search_documents(
            search_query, limit=10, offset=0
        )
        
        # Assertions
        assert len(documents) == 0
        assert total_count == 0

    @pytest.mark.asyncio
    async def test_get_documents_by_entity(self, repository, mock_session):
        """Test document retrieval by entity."""
        # Mock documents
        sample_docs = [
            Document(id=1, filename="doc1.pdf", project_id=1),
            Document(id=2, filename="doc2.pdf", project_id=1),
        ]
        
        # Mock count query result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2
        
        # Mock main query result
        mock_main_result = MagicMock()
        mock_main_result.scalars.return_value.all.return_value = sample_docs
        
        # Mock session execute
        def mock_execute(query):
            if "count" in str(query).lower():
                return mock_count_result
            return mock_main_result
        
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        
        # Execute
        documents, total_count = await repository.get_documents_by_entity(
            "project", entity_id=1, limit=10, offset=0
        )
        
        # Assertions
        assert len(documents) == 2
        assert total_count == 2
        assert all(doc.project_id == 1 for doc in documents)

    @pytest.mark.asyncio
    async def test_get_documents_by_entity_invalid_type(self, repository):
        """Test document retrieval with invalid entity type."""
        # Execute and assert
        with pytest.raises(ValueError, match="Invalid entity type"):
            await repository.get_documents_by_entity(
                "invalid_type", entity_id=1, limit=10, offset=0
            )

    @pytest.mark.asyncio
    async def test_get_documents_by_type(self, repository, mock_session):
        """Test document retrieval by type."""
        # Mock documents
        sample_docs = [
            Document(id=1, filename="image1.jpg", document_type=DocumentType.PROJECT_PHOTO),
            Document(id=2, filename="image2.png", document_type=DocumentType.PROJECT_PHOTO),
        ]
        
        # Mock count query result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2
        
        # Mock main query result
        mock_main_result = MagicMock()
        mock_main_result.scalars.return_value.all.return_value = sample_docs
        
        # Mock session execute
        def mock_execute(query):
            if "count" in str(query).lower():
                return mock_count_result
            return mock_main_result
        
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        
        # Execute
        documents, total_count = await repository.get_documents_by_type(
            DocumentType.PROJECT_PHOTO, limit=10, offset=0
        )
        
        # Assertions
        assert len(documents) == 2
        assert total_count == 2
        assert all(doc.document_type == DocumentType.PROJECT_PHOTO for doc in documents)

    @pytest.mark.asyncio
    async def test_get_documents_by_status(self, repository, mock_session):
        """Test document retrieval by status."""
        # Mock documents
        sample_docs = [
            Document(id=1, filename="doc1.pdf", status=DocumentStatus.QUARANTINED),
        ]
        
        # Mock count query result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        
        # Mock main query result
        mock_main_result = MagicMock()
        mock_main_result.scalars.return_value.all.return_value = sample_docs
        
        # Mock session execute
        def mock_execute(query):
            if "count" in str(query).lower():
                return mock_count_result
            return mock_main_result
        
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        
        # Execute
        documents, total_count = await repository.get_documents_by_status(
            DocumentStatus.QUARANTINED, limit=10, offset=0
        )
        
        # Assertions
        assert len(documents) == 1
        assert total_count == 1
        assert documents[0].status == DocumentStatus.QUARANTINED

    @pytest.mark.asyncio
    async def test_get_most_downloaded_documents(self, repository, mock_session):
        """Test retrieval of most downloaded documents."""
        # Mock documents
        sample_docs = [
            Document(id=1, filename="popular1.pdf", download_count=100),
            Document(id=2, filename="popular2.pdf", download_count=50),
        ]
        
        # Mock session execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_docs
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        documents = await repository.get_most_downloaded_documents(limit=10)
        
        # Assertions
        assert len(documents) == 2
        assert documents[0].download_count >= documents[1].download_count

    @pytest.mark.asyncio
    async def test_get_recent_documents(self, repository, mock_session):
        """Test retrieval of recent documents."""
        # Mock documents
        sample_docs = [
            Document(id=1, filename="recent1.pdf"),
            Document(id=2, filename="recent2.pdf"),
        ]
        
        # Mock session execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_docs
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        documents = await repository.get_recent_documents(limit=10)
        
        # Assertions
        assert len(documents) == 2

    @pytest.mark.asyncio
    async def test_increment_download_count(self, repository, mock_session, sample_document):
        """Test download count increment."""
        # Mock repository get_by_id
        repository.get_by_id = AsyncMock(return_value=sample_document)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Execute
        result = await repository.increment_download_count(document_id=1)
        
        # Assertions
        assert result == sample_document
        assert result.download_count == 1  # Should be incremented
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_increment_download_count_not_found(self, repository, mock_session):
        """Test download count increment when document doesn't exist."""
        # Mock repository get_by_id
        repository.get_by_id = AsyncMock(return_value=None)
        
        # Execute
        result = await repository.increment_download_count(document_id=999)
        
        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_update_document_status(self, repository, mock_session, sample_document):
        """Test document status update."""
        # Mock repository get_by_id
        repository.get_by_id = AsyncMock(return_value=sample_document)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Execute
        result = await repository.update_document_status(
            document_id=1, status=DocumentStatus.QUARANTINED
        )
        
        # Assertions
        assert result == sample_document
        assert result.status == DocumentStatus.QUARANTINED
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document_statistics(self, repository, mock_session):
        """Test document statistics retrieval."""
        # Mock statistics results
        mock_results = [
            # Total documents
            MagicMock(scalar=MagicMock(return_value=100)),
            # Total size
            MagicMock(scalar=MagicMock(return_value=1024000)),
            # Documents by type
            [
                MagicMock(document_type=DocumentType.GENERAL_DOCUMENT, count=50),
                MagicMock(document_type=DocumentType.PROJECT_PHOTO, count=30),
            ],
            # Documents by status
            [
                MagicMock(status=DocumentStatus.AVAILABLE, count=80),
                MagicMock(status=DocumentStatus.QUARANTINED, count=20),
            ],
            # Documents by MIME type
            [
                MagicMock(mime_type="application/pdf", count=40),
                MagicMock(mime_type="image/jpeg", count=30),
            ],
            # Entity usage
            [
                MagicMock(project_id=1, count=10, total_size=100000),
                MagicMock(project_id=2, count=15, total_size=150000),
            ],
        ]
        
        # Mock session execute
        def mock_execute(query):
            query_str = str(query).lower()
            if "count(documents.id)" in query_str and "sum" not in query_str:
                return mock_results[0]  # Total documents
            elif "sum(documents.file_size)" in query_str:
                return mock_results[1]  # Total size
            elif "document_type" in query_str:
                mock_result = MagicMock()
                mock_result.__iter__ = lambda self: iter(mock_results[2])
                return mock_result
            elif "status" in query_str and "documents" in query_str:
                mock_result = MagicMock()
                mock_result.__iter__ = lambda self: iter(mock_results[3])
                return mock_result
            elif "mime_type" in query_str:
                mock_result = MagicMock()
                mock_result.__iter__ = lambda self: iter(mock_results[4])
                return mock_result
            else:
                # Entity usage queries
                mock_result = MagicMock()
                mock_result.__iter__ = lambda self: iter(mock_results[5])
                return mock_result
        
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        
        # Execute
        stats = await repository.get_document_statistics()
        
        # Assertions
        assert stats['total_documents'] == 100
        assert stats['total_size_bytes'] == 1024000
        assert stats['documents_by_type'][DocumentType.GENERAL_DOCUMENT] == 50
        assert stats['documents_by_type'][DocumentType.PROJECT_PHOTO] == 30
        assert stats['documents_by_status'][DocumentStatus.AVAILABLE] == 80
        assert stats['documents_by_status'][DocumentStatus.QUARANTINED] == 20
        assert stats['documents_by_mime_type']["application/pdf"] == 40
        assert stats['documents_by_mime_type']["image/jpeg"] == 30

    @pytest.mark.asyncio
    async def test_get_orphaned_documents(self, repository, mock_session):
        """Test retrieval of orphaned documents."""
        # Mock documents
        sample_docs = [
            Document(id=1, filename="orphaned1.pdf", status=DocumentStatus.VALIDATION_FAILED),
        ]
        
        # Mock session execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_docs
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        documents = await repository.get_orphaned_documents()
        
        # Assertions
        assert len(documents) == 1
        assert documents[0].status == DocumentStatus.VALIDATION_FAILED

    @pytest.mark.asyncio
    async def test_delete_documents_by_status(self, repository, mock_session):
        """Test deletion of documents by status."""
        # Mock documents
        sample_docs = [
            Document(id=1, filename="doc1.pdf", status=DocumentStatus.QUARANTINED),
            Document(id=2, filename="doc2.pdf", status=DocumentStatus.QUARANTINED),
        ]
        
        # Mock session execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_docs
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock delete method
        repository.delete = AsyncMock()
        
        # Execute
        count = await repository.delete_documents_by_status(DocumentStatus.QUARANTINED)
        
        # Assertions
        assert count == 2
        assert repository.delete.call_count == 2
