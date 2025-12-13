# Upload Flow Fixes - December 11, 2025

## Summary

Fixed multiple critical bugs in the document upload flow that were preventing users from uploading multiple files to a single document.

## Issues Found and Fixed

### 1. File Categorization Not Working ✅
**File**: `backend/app/services/document.py`
**Method**: `create_document_with_file()` (lines 275-289)

**Problem**: The method wasn't setting `file_category` when creating documents with files.

**Fix**: Added auto-categorization logic using FileCategorizer:
```python
# Auto-categorize file based on extension
from app.utils.file_categorizer import FileCategorizer
categorizer = FileCategorizer()
file_category, confidence = categorizer.categorize_file(file.filename)
file_use = categorizer.get_file_use_from_category(file_category)

doc_file = DocumentFile(
    file_category=file_category,  # Auto-categorized
    file_use=document_data.file_use or file_use,
    # ...
)
```

### 2. UploadFile.seek() Invalid Arguments ✅
**Files**:
- `backend/app/utils/file_validator.py` (line 71)
- `backend/app/services/file.py` (line 428)

**Problem**: Code was calling `file.seek(0, 2)` but FastAPI's UploadFile.seek() only accepts 1 argument.

**Fix**: Changed to use `file.size` attribute:
```python
# Before (WRONG):
await file.seek(0, 2)  # Seek to end
file_size = file.tell()

# After (CORRECT):
file_size = file.size
```

### 3. FileService Missing Database Session ✅
**File**: `backend/app/services/document.py` (line 36)

**Problem**: FileService was instantiated without a database session, but `upload_file()` method needs `self.db`.

**Fix**: Injected database session after instantiation:
```python
def __init__(self, db: Session):
    self.db = db
    self.file_service = FileService()
    self.file_service.db = db  # Inject database session
    self.minio_service = MinIOService()
```

### 4. File Model Attribute Name Mismatch ✅
**File**: `backend/app/services/file.py` (lines 423, 443-453)

**Problem**: Code was using wrong attribute names that don't exist in the File model:
- `File.checksum` → should be `File.file_hash`
- `mime_type` → should be `content_type`
- `file_path` → should be `minio_object_name`

**Fix**: Updated to use correct attribute names:
```python
# Check if file already exists
existing_file = self.db.query(File).filter(File.file_hash == file_hash).first()

# Create file record with correct attributes
db_file = File(
    filename=file.filename,
    original_filename=file.filename,
    minio_object_name=object_name,
    bucket_name=settings.MINIO_BUCKET_NAME,
    file_size=file_size,
    content_type=mime_type,
    file_hash=file_hash,
    owner_id=user_id,
    upload_completed=True
)
```

### 5. MinIO Method Name Mismatch ✅
**File**: `backend/app/services/file.py` (line 436)

**Problem**: Code was calling `self.minio_service.upload_object()` but the method is named `upload_file()`.

**Fix**: Changed to correct method name and signature:
```python
# Before (WRONG):
self.minio_service.upload_object(
    file.file,
    object_name,
    content_type=mime_type,
    length=file_size
)

# After (CORRECT):
await self.minio_service.upload_file(
    file.file,
    object_name,
    mime_type
)
```

## Testing Checklist

Before marking this as complete, verify:

1. ✅ Backend starts without errors
2. ⏳ Upload a document with 2 files (DNG + JPEG)
3. ⏳ Verify ONE document is created (not two)
4. ⏳ Verify both files are attached to the same document
5. ⏳ Verify file categorization works:
   - DNG → `master` (Preservation Master)
   - JPEG → `export_high` (High-Quality Export)
6. ⏳ Check document detail modal shows files grouped by category

## Files Modified

1. `backend/app/services/document.py`
   - Added file categorization to `create_document_with_file()`
   - Injected database session into FileService

2. `backend/app/services/file.py`
   - Fixed UploadFile.seek() calls
   - Fixed File model attribute names
   - Fixed MinIO method call

3. `backend/app/utils/file_validator.py`
   - Fixed UploadFile.seek() call

## Related Documentation

- `METS_ECOMIC_FILE_CATEGORIZATION.md` - File categorization system
- `COMPLETE_FIX_SUMMARY.md` - Previous database and frontend fixes
