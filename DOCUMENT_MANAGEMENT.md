# 📄 Document Management System

## Overview

The Document Management System provides comprehensive file upload, storage, and management capabilities for the LifeLine-ICT platform. This system allows users to upload, organize, and access documents associated with various entities in the system including projects, ICT resources, maintenance tickets, locations, and sensor sites.

## 🎯 Features

### Core Functionality
- **File Upload**: Secure file upload with validation and processing
- **Document Storage**: Organized file storage with metadata tracking
- **Access Control**: Public/private document access with user authentication
- **File Validation**: Comprehensive validation including file type, size, and security checks
- **Search & Filter**: Advanced search and filtering capabilities
- **Statistics**: Document usage statistics and analytics
- **Cleanup**: Automatic cleanup of orphaned files

### Security Features
- **File Type Validation**: Whitelist-based file type checking
- **Size Limits**: Configurable file size restrictions
- **Content Scanning**: Basic malicious content detection
- **Quarantine System**: Isolate suspicious files for review
- **Access Control**: Role-based access to documents

### Integration Points
- **Projects**: Attach project documentation, reports, presentations
- **ICT Resources**: Upload manuals, warranties, certificates, photos
- **Maintenance Tickets**: Attach photos, reports, receipts, work orders
- **Locations**: Store floor plans, photos, documentation
- **Sensor Sites**: Upload calibration data, installation photos

## 🏗️ Architecture

### Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Router    │    │  Document       │    │  File Storage   │
│                 │───▶│  Service        │───▶│  Service        │
│ /api/v1/docs    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pydantic      │    │  Document       │    │  Local File     │
│   Schemas       │    │  Repository     │    │  System         │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite)      │
                       │                 │
                       └─────────────────┘
```

### Data Flow

1. **Upload Request**: Client sends file with metadata to API
2. **Validation**: File validation (type, size, content security)
3. **Processing**: Generate unique filename and storage path
4. **Storage**: Save file to organized directory structure
5. **Database**: Create document record with metadata
6. **Response**: Return document information and download URL

## 📊 Database Schema

### Documents Table

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    description TEXT,
    tags VARCHAR(500),
    checksum VARCHAR(64),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    download_count INTEGER NOT NULL DEFAULT 0,
    last_accessed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Relationship fields
    project_id INTEGER REFERENCES projects(id),
    resource_id INTEGER REFERENCES ict_resources(id),
    maintenance_ticket_id INTEGER REFERENCES maintenance_tickets(id),
    location_id INTEGER REFERENCES locations(id),
    sensor_site_id INTEGER REFERENCES sensor_sites(id),
    uploaded_by_user_id INTEGER REFERENCES users(id)
);
```

### Document Types

```python
class DocumentType(str, Enum):
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
```

### Document Status

```python
class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    AVAILABLE = "available"
    VALIDATION_FAILED = "validation_failed"
    CORRUPTED = "corrupted"
    QUARANTINED = "quarantined"
    DELETED = "deleted"
```

## 🚀 API Endpoints

### Upload Document
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: [binary file data]
document_type: general_document
description: Document description
tags: tag1, tag2, tag3
is_public: false
project_id: 1
resource_id: 1
```

**Response:**
```json
{
  "success": true,
  "document_id": 1,
  "filename": "document.pdf",
  "file_size": 1024,
  "file_size_human": "1.0 KB",
  "document_type": "general_document",
  "status": "available",
  "message": "Document uploaded successfully",
  "download_url": "/api/v1/documents/1/download"
}
```

### List Documents
```http
GET /api/v1/documents/
```

**Query Parameters:**
- `search`: Text search across filename, description, and tags
- `document_type`: Filter by document type
- `status`: Filter by document status
- `mime_type`: Filter by MIME type
- `file_extension`: Filter by file extension
- `is_public`: Filter by public access setting
- `project_id`: Filter by associated project
- `resource_id`: Filter by associated ICT resource
- `maintenance_ticket_id`: Filter by associated maintenance ticket
- `location_id`: Filter by associated location
- `sensor_site_id`: Filter by associated sensor site
- `uploaded_by_user_id`: Filter by uploader
- `sort_by`: Field to sort by (created_at, updated_at, filename, file_size, download_count, document_type, status)
- `sort_order`: Sort order (asc or desc)
- `page`: Page number for pagination
- `limit`: Number of items per page

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "filename": "document.pdf",
      "document_type": "general_document",
      "file_size": 1024,
      "file_size_human": "1.0 KB",
      "mime_type": "application/pdf",
      "status": "available",
      "created_at": "2024-01-01T12:00:00Z",
      "download_count": 5
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

### Get Document
```http
GET /api/v1/documents/{document_id}
```

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "original_filename": "document_12345678.pdf",
  "file_path": "documents/2024/01/document_12345678.pdf",
  "file_size": 1024,
  "mime_type": "application/pdf",
  "file_extension": "pdf",
  "document_type": "general_document",
  "status": "available",
  "description": "Document description",
  "tags": "tag1, tag2",
  "checksum": "abc123def456",
  "is_public": false,
  "download_count": 5,
  "last_accessed_at": "2024-01-01T12:30:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "file_size_human": "1.0 KB",
  "is_image": false,
  "is_document": true,
  "project_name": "Test Project",
  "resource_name": "Test Resource",
  "uploaded_by_username": "testuser"
}
```

### Download Document
```http
GET /api/v1/documents/{document_id}/download
```

**Response:** Binary file content with appropriate headers

### Update Document
```http
PUT /api/v1/documents/{document_id}
Content-Type: application/json

{
  "description": "Updated description",
  "tags": "updated, tags",
  "is_public": true,
  "project_id": 2
}
```

### Delete Document
```http
DELETE /api/v1/documents/{document_id}
```

### Get Documents by Entity
```http
GET /api/v1/documents/entity/{entity_type}/{entity_id}
```

**Entity Types:** `project`, `resource`, `maintenance_ticket`, `location`, `sensor_site`

### Get Document Statistics
```http
GET /api/v1/documents/stats/overview
```

**Response:**
```json
{
  "total_documents": 100,
  "total_size_bytes": 1024000,
  "total_size_human": "1.0 MB",
  "documents_by_type": {
    "general_document": 50,
    "project_photo": 30,
    "manual": 20
  },
  "documents_by_status": {
    "available": 80,
    "quarantined": 20
  },
  "documents_by_mime_type": {
    "application/pdf": 40,
    "image/jpeg": 30,
    "image/png": 20
  },
  "most_downloaded": [...],
  "recent_uploads": [...],
  "storage_usage_by_entity": {
    "project": {"count": 10, "total_size": 100000},
    "resource": {"count": 15, "total_size": 150000}
  }
}
```

### Quarantine Document
```http
POST /api/v1/documents/{document_id}/quarantine
Content-Type: application/x-www-form-urlencoded

reason=Suspicious content detected
```

### Cleanup Orphaned Files
```http
POST /api/v1/documents/cleanup/orphaned
```

## ⚙️ Configuration

### Environment Variables

```bash
# File Upload Configuration
LIFELINE_UPLOAD_STORAGE_PATH=./uploads
LIFELINE_UPLOAD_MAX_SIZE=10485760  # 10MB in bytes
LIFELINE_UPLOAD_ALLOWED_EXTENSIONS=pdf,doc,docx,txt,jpg,jpeg,png,gif,bmp,tiff,zip,rar,7z
LIFELINE_UPLOAD_QUARANTINE_PATH=./quarantine
LIFELINE_UPLOAD_CLEANUP_INTERVAL_HOURS=24
```

### Storage Structure

```
uploads/
├── documents/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── document1_12345678.pdf
│   │   │   └── document2_87654321.docx
│   │   └── 02/
│   └── 2023/
├── images/
│   ├── 2024/
│   │   └── 01/
│   │       ├── image1_12345678.jpg
│   │       └── image2_87654321.png
└── archives/
    └── 2024/
        └── 01/
            └── archive1_12345678.zip

quarantine/
├── 1_document.pdf
├── 1.log
├── 2_image.jpg
└── 2.log
```

## 🔒 Security

### File Validation

1. **File Type Validation**: Whitelist-based extension checking
2. **MIME Type Verification**: Content-based MIME type detection
3. **File Size Limits**: Configurable maximum file size
4. **Content Scanning**: Basic malicious content detection
5. **Filename Sanitization**: Remove dangerous characters

### Access Control

1. **Public/Private Documents**: Configurable access levels
2. **User Authentication**: Required for private documents
3. **Role-Based Access**: Future implementation for admin functions
4. **Quarantine System**: Isolate suspicious files

### Security Headers

- Content-Disposition: attachment for downloads
- Content-Type: Proper MIME type handling
- Content-Length: File size information

## 📈 Usage Examples

### Upload a Project Document

```python
import requests

# Upload project report
files = {'file': open('project_report.pdf', 'rb')}
data = {
    'document_type': 'project_report',
    'description': 'Q4 2024 Project Report',
    'tags': 'report, quarterly, 2024',
    'is_public': 'false',
    'project_id': '1'
}

response = requests.post(
    'http://localhost:8000/api/v1/documents/upload',
    files=files,
    data=data
)

if response.status_code == 201:
    document = response.json()
    print(f"Document uploaded: {document['document_id']}")
    print(f"Download URL: {document['download_url']}")
```

### Search Documents

```python
# Search for PDF documents in a specific project
params = {
    'search': 'report',
    'document_type': 'project_report',
    'project_id': '1',
    'file_extension': 'pdf',
    'sort_by': 'created_at',
    'sort_order': 'desc',
    'limit': '10'
}

response = requests.get(
    'http://localhost:8000/api/v1/documents/',
    params=params
)

documents = response.json()
for doc in documents['items']:
    print(f"- {doc['filename']} ({doc['file_size_human']})")
```

### Download Document

```python
# Download a document
response = requests.get(
    'http://localhost:8000/api/v1/documents/1/download'
)

if response.status_code == 200:
    with open('downloaded_document.pdf', 'wb') as f:
        f.write(response.content)
    print("Document downloaded successfully")
```

### Get Entity Documents

```python
# Get all documents for a project
response = requests.get(
    'http://localhost:8000/api/v1/documents/entity/project/1'
)

project_docs = response.json()
print(f"Project has {project_docs['total']} documents")
```

## 🧪 Testing

### Running Tests

```bash
# Run all document-related tests
pytest tests/services/test_document_service.py -v
pytest tests/services/test_file_storage.py -v
pytest tests/repositories/test_document_repository.py -v
pytest tests/api/test_document_router.py -v

# Run with coverage
pytest --cov=app.services.document_service --cov=app.services.file_storage tests/
```

### Test Coverage

The test suite covers:
- ✅ File upload and validation
- ✅ Document CRUD operations
- ✅ File storage operations
- ✅ Search and filtering
- ✅ Access control
- ✅ Error handling
- ✅ API endpoints
- ✅ Security features

## 🔧 Maintenance

### Cleanup Operations

```bash
# Clean up orphaned files
curl -X POST http://localhost:8000/api/v1/documents/cleanup/orphaned

# Quarantine suspicious document
curl -X POST http://localhost:8000/api/v1/documents/1/quarantine \
  -d "reason=Suspicious content detected"
```

### Monitoring

Monitor the following metrics:
- Total storage usage
- Number of documents by type
- Upload/download rates
- Quarantined files count
- Failed validations

### Backup

Ensure regular backups of:
- Document files in storage directory
- Database records
- Quarantine logs

## 🚀 Future Enhancements

### Planned Features
- **Cloud Storage**: Integration with AWS S3, Google Cloud Storage
- **Virus Scanning**: Integration with antivirus engines
- **Version Control**: Document versioning and history
- **Advanced Search**: Full-text search with Elasticsearch
- **Workflow Integration**: Document approval workflows
- **Audit Logging**: Comprehensive audit trail
- **API Rate Limiting**: Protect against abuse
- **CDN Integration**: Global document delivery

### Performance Optimizations
- **File Streaming**: Large file streaming support
- **Compression**: Automatic file compression
- **Caching**: Document metadata caching
- **Batch Operations**: Bulk document operations

## 📞 Support

For issues or questions regarding the Document Management System:

1. Check the API documentation at `/docs`
2. Review the test cases for usage examples
3. Check server logs for error details
4. Contact the development team

---

**Note**: This document management system is designed to be secure, scalable, and maintainable. Regular updates and security patches should be applied to ensure optimal performance and security.
