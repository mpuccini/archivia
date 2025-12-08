# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Archivia is a digital document archiving system for managing archival metadata and files according to the METS (Metadata Encoding and Transmission Standard) specification. The system enables archivists to upload documents with rich metadata, manage files, and export METS-compliant XML for preservation.

**Tech Stack:**
- Frontend: Vue.js 3 + Vite + Tailwind CSS + Pinia (state management)
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Storage: MinIO object storage
- Deployment: Docker Compose

## Development Commands

### Docker Compose (Primary Development)

```bash
# Start all services (builds if needed)
docker compose up --build

# View logs for specific service
docker compose logs -f backend
docker compose logs -f frontend

# Restart specific service
docker compose restart backend

# Stop all services
docker compose down

# Rebuild specific service
docker compose build backend
docker compose up -d backend
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Development server with hot reload (uses backend via Docker)
npm run dev

# Build for production
npm run build

# Preview production build
npm preview
```

The frontend runs on port 3000 and expects the backend API at `http://localhost:8000`.

### Backend Development

The backend container auto-reloads on code changes (volume mounted at `./backend:/app`).

```bash
# Access backend container
docker compose exec backend bash

# Create admin user (from host or container)
python backend/create_admin.py

# Test configuration
python backend/test_config.py
```

### Database Operations

```bash
# Access PostgreSQL directly
docker compose exec db psql -U archivia -d archivia

# View database logs
docker compose logs -f db
```

## Architecture & Code Organization

### Backend Structure (`backend/app/`)

The backend follows a layered architecture pattern:

```
app/
├── core/           # Core configuration and database setup
│   ├── config.py   # Pydantic settings (env vars, file upload limits)
│   └── database.py # SQLAlchemy engine and session management
├── models/         # SQLAlchemy ORM models
│   ├── user.py
│   ├── file.py     # File and FileChunk models for multipart uploads
│   └── document.py # Document and DocumentFile association
├── schemas/        # Pydantic schemas for request/response validation
├── routes/         # FastAPI route handlers (thin layer)
│   ├── auth.py
│   ├── files.py
│   └── documents.py
├── services/       # Business logic layer
│   ├── auth.py          # Authentication and user management
│   ├── minio.py         # Object storage client wrapper
│   ├── file.py          # File upload/download with chunking
│   ├── document.py      # Document CRUD and metadata operations
│   └── mets_validation.py  # External METS ECO-MiC validation API
└── utils/
    ├── mets_generator.py   # Generate METS XML from Document models
    ├── file_validator.py   # File type and security validation
    ├── file_utils.py       # File hashing and utilities
    └── logging.py          # Structured logging setup
```

**Key Backend Patterns:**

1. **Service Layer Pattern**: Routes are thin controllers that delegate to service classes. All business logic lives in `services/`.

2. **Multipart Upload Flow**: Large files (especially DNG camera files up to 80GB) use chunked uploads:
   - Frontend splits file into chunks (64MB)
   - Backend stores chunks as `FileChunk` records
   - Final assembly creates `File` record and uploads to MinIO
   - See `backend/app/services/file.py` for implementation

3. **Document-File Association**: Documents and Files have a many-to-many relationship via `DocumentFile` which stores per-file metadata (sequence, checksum, dimensions, file_use, file_label).

4. **METS Generation**: `METSGenerator` in `utils/mets_generator.py` converts Document models to METS XML with proper namespaces (mets, mods, mix, dct, xlink).

5. **METS Validation**: External validation against ECO-MiC 1.1 standard via Cineca API (`validavmetsecomic.prod.os01.ocp.cineca.it`). See `services/mets_validation.py`.

### Frontend Structure (`frontend/src/`)

```
src/
├── main.js              # App entry, router, pinia setup
├── App.vue              # Root component
├── components/
│   ├── Login.vue
│   ├── Dashboard.vue    # Main document management interface
│   ├── DocumentsManager.vue       # Document list and operations
│   ├── DocumentUploadForm.vue     # Multi-step document creation wizard
│   ├── DocumentDetailModal.vue    # View/edit document details
│   ├── ImageUpload.vue            # Single image upload to document
│   ├── BatchImageUpload.vue       # Batch image upload with auto-matching
│   ├── ExcelBatchImport.vue       # Bulk document import from Excel
│   ├── FileList.vue               # Display files for documents
│   ├── ImageViewer.vue            # Image preview modal
│   └── Guide.vue                  # User guide
└── assets/css/tailwind.css
```

**Key Frontend Patterns:**

1. **State Management**: Pinia store for authentication (token stored in localStorage).

2. **API Communication**: Axios for HTTP requests. Auth token attached via interceptor.

3. **Batch Operations**:
   - Excel import uses `XLSX` library to parse spreadsheets
   - Batch image upload matches filenames to document `logical_id`
   - Creates new documents for unmatched images

4. **Multi-step Forms**: `DocumentUploadForm` uses `vue3-form-wizard` for guided metadata entry.

5. **File Uploads**: Uses `FormData` with multipart encoding. Large files handled via chunking on frontend.

## Important Domain Concepts

### METS ECO-MiC 1.2 Standard

Documents follow the **METS ECO-MiC 1.2** standard for Italian archival description (ICCU profile):

**Core Identifiers:**
- **logical_id**: Unique document identifier (required)
- **conservative_id**: Physical archive identifier with ISIL authority (e.g., "IT-MO0172")

**ECO-MiC Specific Fields:**
- **type_of_resource**: Document type (e.g., "risorsa manoscritta", "documento testuale")
- **producer_name/creator_name**: Corporate or personal names with roles
- **record_status**: METS completion level ("COMPLETE", "MINIMUM", "REFERENCED")

**Archival Hierarchy:**
- Archive → Fund → Series → Folder structure using MODS relatedItem
- Physical description with form and extent
- Temporal metadata: date ranges with ISO 8601 format

**Rights Metadata (metsrights):**
- **rights_category**: COPYRIGHTED, PUBLIC DOMAIN, CONTRACTUAL
- **rights_holder**: Organization or person holding rights
- **rights_constraint**: Rights statement codes (e.g., "NoC-OKLR", "InC")

**Technical Metadata (MIX per file):**
- Image dimensions, DPI/sampling frequency
- Color space, compression scheme
- Scanner information
- MD5 checksums for integrity

**METS Structure:**
- **PROFILE**: http://www.iccu.sbn.it/metaAG1.pdf (ECO-MiC)
- **structMap TYPE**: "PHYSICAL" (archival requirement)
- **techMD**: Per-file in amdSec (not per-document)
- **rightsMD**: Complete METSRIGHTS structure

### File Types and Validation

The system handles archival image formats:
- **DNG (Adobe Digital Negative)** - large RAW files up to 80GB with automatic thumbnail generation
  - Backend automatically extracts embedded JPEG preview or generates thumbnail from RAW data
  - Frontend displays thumbnails with "DNG RAW" badge indicator
  - Thumbnails generated on-the-fly via `ThumbnailGenerator` utility (`backend/app/utils/thumbnail_generator.py`)
  - Uses `rawpy` library for RAW processing and `Pillow` for image manipulation
- TIFF, JPEG, PNG - standard image formats
- PDF - document scans

File validation in `backend/app/utils/file_validator.py` checks:
- MIME type validation with magic number verification
- Extension verification
- Maximum file size (80GB for DNG, varies by type)

**DNG Preview System:**
- When streaming DNG files via `/api/files/{file_id}/stream`, backend automatically generates and returns a JPEG thumbnail
- Thumbnail size: 1200x1200px max, 85% JPEG quality
- Extraction priority: 1) Embedded JPEG preview (fast), 2) Processed RAW data (slower)
- Frontend displays DNG indicator badge and informational note about preview quality

### Authentication Flow

- JWT token-based authentication
- Tokens expire after 30 minutes (configurable in `config.py`)
- User model is simple (id, username, hashed_password)
- Use `backend/create_admin.py` to create initial user

## Environment Variables

Key environment variables (defined in `docker-compose.yml` and `backend/app/core/config.py`):

```bash
# Database
DATABASE_URL=postgresql://archivia:archivia123@db:5432/archivia

# Auth
SECRET_KEY=your-secret-key-here

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=archivia
MINIO_SECRET_KEY=archivia123
MINIO_BUCKET_NAME=archivia-files
MINIO_SECURE=false

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# File upload limits (in config.py)
MAX_FILE_SIZE=80 * 1024 * 1024 * 1024  # 80GB
CHUNK_SIZE=64 * 1024 * 1024            # 64MB
```

## Common Development Scenarios

### Adding a New Document Field

1. Add column to `backend/app/models/document.py` (Document model)
2. Add field to `backend/app/schemas/document.py` (DocumentCreate/DocumentUpdate schemas)
3. Update `backend/app/utils/mets_generator.py` to include field in METS XML generation
4. Update `frontend/src/components/DocumentUploadForm.vue` to capture field in UI
5. Database migration happens automatically via SQLAlchemy (tables created on startup)

### Adding a New API Endpoint

1. Define Pydantic schema in `backend/app/schemas/`
2. Add business logic to appropriate service in `backend/app/services/`
3. Create route handler in `backend/app/routes/`
4. Include router in `backend/main.py`
5. Frontend: Add API call in appropriate Vue component

### Debugging File Upload Issues

- Check MinIO console at `http://localhost:9001` (credentials: archivia/archivia123)
- Backend logs show upload progress: `docker compose logs -f backend`
- For large files, verify chunk assembly in `FileService.assemble_chunks()`
- Check `FileChunk` records in database for incomplete uploads

### Working with METS ECO-MiC XML

**Generation:**
- Generator: `METSEcoMicGenerator` in `utils/mets_generator_ecomic.py`
- Full ECO-MiC 1.2 compliance with all required sections
- Automatic per-file techMD generation
- Rights metadata (metsrights) support

**Validation:**
- `METSValidationService.validate_mets_xml()` in `services/mets_validation.py`
- External validation via Cineca API: `validavmetsecomic.prod.os01.ocp.cineca.it`
- Validates against ECO-MiC 1.1 standard (API endpoint)
- Network access required for validation

**Storage:**
- Generated METS XML stored in `Document.mets_xml` field
- Regenerated on-demand for exports
- Export includes both METS XML and associated files in ZIP format

**ECO-MiC Implementation:**
- Reference: [ECO-MiC GitHub Repository](https://github.com/icdp-digital-library/profilo-mets-ecomic)
- Examples: `ICDP_Profilo_METS_ECO-MiC_v.1.2/ESEMPI METS ECO-MiC 1.2/`
- See `docs/implementation/METS_ECOMIC_IMPLEMENTATION.md` for full implementation details

## Testing

Currently no automated test suite. Manual testing procedures in `docs/testing/TESTING_GUIDE.md` cover:
- Excel batch import
- Single and batch image upload
- Document creation and editing
- File matching by logical_id

Test data files referenced:
- `test_batch_import.xlsx`
- `test_images/` directory with DOC001.jpg - DOC005.jpg

## Access Points

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (archivia/archivia123)
- PostgreSQL: localhost:5432 (archivia/archivia123)

## Related Documentation

Comprehensive documentation is organized in the `docs/` directory:

### Implementation Guides
- **`docs/implementation/METS_ECOMIC_IMPLEMENTATION.md`** - Complete METS ECO-MiC 1.1 implementation guide including XML generation and Cineca API validation
- **`docs/implementation/PERFORMANCE_OPTIMIZATIONS.md`** - Large file handling (DNG up to 80GB), streaming, chunking, and memory optimizations

### Deployment & Operations
- **`docs/deployment/DOCKER_DEPLOYMENT.md`** - Docker Compose deployment guide with troubleshooting

### Features
- **`docs/features/METADATA_IMPORT.md`** - CSV/Excel metadata batch import guide

### Security
- **`docs/security/SECURITY_RECOMMENDATIONS.md`** - Security best practices and future enhancements

### Testing
- **`docs/testing/TESTING_GUIDE.md`** - Manual testing procedures for batch operations and file handling

### History
- **`docs/history/SECURITY_FIXES_HISTORY.md`** - Chronological record of all security fixes and code quality improvements applied to the project
