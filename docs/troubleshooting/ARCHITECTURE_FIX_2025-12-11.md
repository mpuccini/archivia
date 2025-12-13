# Architecture Fix - December 11, 2025

## Problem Summary

The application was broken after implementing file categorization features:
1. **500 Error on Document Detail:** Clicking on any document resulted in a database error
2. **Multiple Document Entities:** Two images uploaded for one document appeared as separate document entries in the list
3. **Missing Database Column:** The `file_category` column didn't exist in the database

## Root Causes

### 1. Database Schema Not Updated
- Added `file_category` field to the DocumentFile **model** (`backend/app/models/document.py`)
- But the actual **database table** was never altered to add this column
- SQLAlchemy tried to query a non-existent column → 500 error

### 2. Misunderstanding of Document vs File Relationship
The batch image upload feature was creating new documents instead of attaching files to existing documents.

## Solution Applied

### Database Migration
Created and ran migration to add the missing column:

```sql
ALTER TABLE document_files
ADD COLUMN IF NOT EXISTS file_category VARCHAR(50);

CREATE INDEX IF NOT EXISTS idx_document_files_category
ON document_files(file_category);
```

**Result:** Column added successfully, application now loads without errors.

### Data Cleanup
Removed orphaned empty documents (IDs 5 and 6) that were created incorrectly by batch upload.

## Correct Architecture

### Document-File Relationship

```
┌─────────────────────────────────────────────────────────┐
│                       DOCUMENT                          │
│  (Metadata Entity - Archival Description)               │
│                                                          │
│  - logical_id: "sample1"                                │
│  - title: "Test document"                               │
│  - description, dates, location, etc.                   │
│  - archive info, rights, etc.                           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ 1:N relationship
                   │
      ┌────────────┴────────────┬────────────────┐
      │                         │                │
      ▼                         ▼                ▼
┌───────────────┐    ┌────────────────┐   ┌──────────────┐
│  FILE (Master)│    │ FILE (Export)  │   │ FILE (Logs)  │
│               │    │                │   │              │
│ sample1.dng   │    │ sample1.jpg    │   │ sample1.log  │
│ Category:     │    │ Category:      │   │ Category:    │
│ "master"      │    │ "export_high"  │   │ "logs"       │
└───────────────┘    └────────────────┘   └──────────────┘
```

### Key Concepts

1. **Document = Metadata Entity**
   - One document represents ONE archival item
   - Contains descriptive metadata (title, dates, location, rights, etc.)
   - Has a unique `logical_id`

2. **File = Digital Object**
   - Multiple files can belong to ONE document
   - Each file has a `file_category` that indicates its purpose:
     - `master`: Preservation master (RAW/DNG/uncompressed TIFF)
     - `normalized`: Normalized TIFF exports
     - `export_high`: High-quality JPEG (300 DPI)
     - `export_low`: Low-quality JPEG/thumbnails
     - `metadata`: XML, METS, etc.
     - `icc`: ICC color profiles
     - `logs`: Log files
     - `other`: Uncategorized

3. **DocumentFile = Association Table**
   - Links documents to files (many-to-many)
   - Stores per-file metadata:
     - `file_category`: Type of file
     - `file_use`: METS fileGrp USE attribute
     - `sequence_number`: Order in document
     - Technical metadata (dimensions, DPI, color space, etc.)

## Database Schema

```sql
-- Documents table (metadata entities)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    logical_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    -- ... many metadata fields ...
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Files table (digital objects)
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    content_type VARCHAR(255),
    file_size BIGINT,
    minio_object_name TEXT,
    -- ... storage metadata ...
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP
);

-- Association table with file categorization
CREATE TABLE document_files (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    file_id INTEGER REFERENCES files(id) ON DELETE CASCADE,

    -- File categorization (NEW)
    file_category VARCHAR(50),  -- master, normalized, export_high, etc.
    file_use VARCHAR(50),        -- METS USE attribute

    -- File metadata
    sequence_number INTEGER,
    image_width INTEGER,
    image_height INTEGER,
    x_sampling_frequency NUMERIC,
    scanner_manufacturer TEXT,
    scanner_model_name TEXT,
    -- ... technical metadata ...

    created_at TIMESTAMP
);
```

## Frontend Behavior

### Document List View
- Shows **documents** (metadata entities)
- Each row = one archival item
- Displays: logical_id, title, file count, creation date

### Document Detail View
- Shows document metadata (title, description, dates, etc.)
- Shows **all associated files** grouped by category:

  ```
  📸 Preservation Master (1)
     └─ sample1.dng (85MB, 6000x4000px)

  🖼️ High-Quality Export (1)
     └─ sample1_high.jpg (12MB, 2400x1600px)

  🏞️ Low-Quality Export (1)
     └─ sample1_thumb.jpg (800KB, 800x533px)

  📝 Logs (1)
     └─ scan_log.txt (2KB)
  ```

## File Upload Workflows

### 1. Single Image Upload to Document
- User clicks "Upload Image" on existing document
- Image is attached to that document
- `file_category` auto-detected or user-selected

### 2. Batch Image Upload (TO BE FIXED)
- User uploads multiple images
- System tries to match filenames to existing `logical_id`
- **CURRENT BUG:** Creates new documents for unmatched files
- **CORRECT BEHAVIOR:** Should either:
  - Attach to matching document by `logical_id`
  - OR ask user to select target document
  - OR fail with clear error message

### 3. Folder Upload (ZIP Archive) - NEW FEATURE
- User uploads ZIP containing structured folders:
  ```
  document1/
    ├── Master/
    │   └── IMG_001.dng
    ├── Derived/
    │   └── IMG_001.tif
    ├── JPG300/
    │   └── IMG_001.jpg
    └── Metadata/
        └── metadata.xml
  ```
- System creates ONE document
- Attaches all files with auto-detected categories based on folder structure

## Next Steps

1. ✅ Database migration applied
2. ✅ Empty documents cleaned up
3. ⏳ Test document detail view
4. ⏳ Fix batch image upload logic to NOT create new documents
5. ⏳ Implement folder upload UI
6. ⏳ Update METS generator to use file categories

## Migration Notes

For future deployments, use this migration:
```bash
docker compose exec -T db psql -U archivia -d archivia < backend/migrations/add_file_category.sql
```

Or integrate with Alembic for proper version control:
```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add file_category to document_files"

# Apply
alembic upgrade head
```
