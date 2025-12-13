# Complete Fix Summary - December 11, 2025

## Issues Identified

### 1. Database Schema Missing Column
**Problem:** The `file_category` column didn't exist in the `document_files` table
**Error:** `column document_files_1.file_category does not exist`
**Impact:** 500 error when viewing any document

### 2. Multiple Document Rows for Single Archival Item
**Problem:** Two images (DNG + JPEG) appeared as 2 separate documents instead of 1 document with 2 files
**Root Cause:** Batch upload feature was auto-creating new documents for unmatched filenames
**Impact:** Incorrect data model - violates archival principles

### 3. File Categorization Not Working
**Problem:** DNG files and JPEG files were both categorized as "Other"
**Root Cause:**
- `file_category` was never set during upload
- Only `file_use` was hardcoded to "master"
**Impact:** Cannot distinguish between master files, exports, and derivatives

## Solutions Applied

### 1. Database Migration ✅
**File:** `backend/migrations/add_file_category.sql`

```sql
-- Add file_category column
ALTER TABLE document_files
ADD COLUMN IF NOT EXISTS file_category VARCHAR(50);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_document_files_category
ON document_files(file_category);
```

**Status:** Applied successfully

### 2. Data Consolidation ✅
**File:** `backend/migrations/fix_duplicate_documents.sql`

Actions performed:
- Merged documents 7 and 8 into single document (ID: 7)
- Moved both files to document 7
- Auto-categorized existing files:
  - `sample1.dng` → `master` (preservation master)
  - `Calcata_ASCC_Are1_1_01.jpg` → `export_high` (derivative)
- Set proper sequence numbers

**Result:**
```
doc_id |       logical_id       |     original_filename      | file_category | sequence_number
-------+------------------------+----------------------------+---------------+-----------------
     7 | Calcata_ASCC_Are1_1_01 | Calcata_ASCC_Are1_1_01.jpg | export_high   |               1
     7 | Calcata_ASCC_Are1_1_01 | sample1.dng                | master        |               2
```

### 3. Fixed upload_document_image() ✅
**File:** `backend/app/services/document.py` (lines 990-1045)

**Changes:**
1. Import FileCategorizer
2. Auto-detect file category based on extension:
   ```python
   categorizer = FileCategorizer()
   file_category, confidence = categorizer.categorize_file(file.filename)
   file_use = categorizer.get_file_use_from_category(file_category)
   ```
3. Calculate next sequence number automatically
4. Set both `file_category` and `file_use` on DocumentFile

**Classification Logic:**
- `.dng`, `.raw`, `.cr2`, `.nef` → `master` (preservation master)
- `.tif`, `.tiff` → `normalized` (derived TIFF)
- `.jpg`, `.jpeg` → `export_high` (compressed derivative)
- `.xml`, `.mets` → `metadata`
- `.icc`, `.icm` → `icc` (color profiles)
- `.log`, `.txt` → `logs`

### 4. Fixed batch_upload_images() ✅
**File:** `backend/app/services/document.py` (lines 1047-1106)

**Old Behavior (WRONG):**
```python
if not document:
    # Create new document automatically
    doc_data = DocumentCreate(logical_id=logical_id, ...)
    document = self.create_document(doc_data, user_id)
```

**New Behavior (CORRECT):**
```python
if not document:
    # Report error - do NOT create
    errors.append({
        "filename": file.filename,
        "logical_id": logical_id,
        "error": f"No document found with logical_id '{logical_id}'. Create the document first."
    })
    continue
```

**Impact:** Batch upload now ONLY attaches files to existing documents

## ECO-MiC 5.3/5.4 Compliance

The file categorization now follows ECO-MiC digitization guidelines:

### Master Files (Preservation)
- **Purpose:** Long-term preservation
- **Formats:** DNG, RAW, uncompressed TIFF
- **Category:** `master`
- **METS USE:** `MASTER`

### Normalized Files (Access Copy)
- **Purpose:** Standardized access format
- **Formats:** TIFF (Adobe RGB, 2400px)
- **Category:** `normalized`
- **METS USE:** `REFERENCE`

### Export Files (Derivatives)
- **High Quality:** JPEG 300 DPI (~2400px) → `export_high` → `HIGH`
- **Low Quality:** JPEG 150 DPI (~1200px) → `export_low` → `THUMBNAIL`

### Support Files
- **Metadata:** XML, METS → `metadata` → `METADATA`
- **ICC Profiles:** .icc, .icm → `icc` → `METADATA`
- **Logs:** .log, .txt → `logs` → `METADATA`

## Correct Architecture Now Implemented

### Document (Metadata Entity)
- ONE document = ONE archival item
- Contains descriptive metadata
- Has unique `logical_id`

### Files (Digital Objects)
- MULTIPLE files can belong to ONE document
- Each file has `file_category` indicating its purpose
- Proper sequence ordering

### Example:
```
Document: "Calcata_ASCC_Are1_1_01"
├── File 1: sample1.dng (master, seq=2)
└── File 2: Calcata_ASCC_Are1_1_01.jpg (export_high, seq=1)
```

## User Experience Changes

### Before (BROKEN):
1. Upload 2 images for document "DOC001"
2. System creates 3 documents:
   - "DOC001" (original)
   - "DOC001_1" (first image)
   - "DOC001_2" (second image)
3. Files categorized as "Other"
4. User sees 3 rows in document list ❌

### After (FIXED):
1. Upload 2 images to document "DOC001"
2. System attaches both to existing "DOC001"
3. Files auto-categorized:
   - DNG → `master`
   - JPEG → `export_high`
4. User sees 1 row in document list ✅
5. Click on document → sees both files grouped by category ✅

## Frontend Display (Already Implemented)

DocumentDetailModal now shows:

```
📸 Preservation Master (1)
   └─ sample1.dng (85MB, 6000x4000px, RAW)

🖼️ High-Quality Export (1)
   └─ Calcata_ASCC_Are1_1_01.jpg (12MB, 2400x1600px, JPEG)
```

## Testing the Fix

### 1. View Existing Document
- Navigate to http://localhost:3000
- Login with admin/archivia123
- Click on "Calcata ASCC Are1 1 01"
- Should see:
  - ✅ Document metadata
  - ✅ 2 files grouped by category
  - ✅ DNG labeled as "Preservation Master"
  - ✅ JPEG labeled as "High-Quality Export"

### 2. Upload New File to Existing Document
- Click "Upload Image" on an existing document
- Upload a .jpg file
- Should auto-categorize as `export_high`
- Should appear in correct category group

### 3. Batch Upload (New Behavior)
- Upload multiple files via batch upload
- Files WITHOUT matching `logical_id` will show error:
  - "No document found with logical_id 'xyz'. Create the document first."
- Files WITH matching `logical_id` will attach correctly

## Files Modified

1. `backend/migrations/add_file_category.sql` (NEW)
2. `backend/migrations/fix_duplicate_documents.sql` (NEW)
3. `backend/app/services/document.py`:
   - `upload_document_image()` - Added auto-categorization
   - `batch_upload_images()` - Removed auto-creation logic
4. `backend/app/models/document.py` - Added `file_category` field (already done)
5. `backend/app/utils/file_categorizer.py` - File categorization service (already done)
6. `frontend/src/components/DocumentDetailModal.vue` - Grouped file display (already done)

## Migration Commands for Future Deployments

```bash
# Add file_category column
docker compose exec -T db psql -U archivia -d archivia < backend/migrations/add_file_category.sql

# Fix existing duplicate documents (run only once)
docker compose exec -T db psql -U archivia -d archivia < backend/migrations/fix_duplicate_documents.sql

# Restart backend to apply code changes
docker compose restart backend
```

## Next Steps (Pending)

1. ⏳ **Folder Upload UI** - Frontend component for ZIP upload
2. ⏳ **METS Generator Update** - Use file categories in `<mets:fileSec>`
3. ⏳ **User Documentation** - Guide for archivists on file categorization

## Status: ✅ COMPLETE

All critical issues have been fixed:
- ✅ Database schema updated
- ✅ Duplicate documents consolidated
- ✅ File categorization working
- ✅ Batch upload no longer creates unwanted documents
- ✅ Frontend displays files grouped by category

The application now correctly implements the ECO-MiC archival digitization model.
