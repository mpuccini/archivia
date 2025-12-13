# MinIO Path Generation Fix - December 11, 2025

## Issue

The `create_document_with_file()` method was still using UUID-based path generation (`generate_object_name()`) instead of the new category-based consistent path strategy.

This caused:
1. Inconsistent storage paths between first file and subsequent files
2. Files stored with UUID names instead of hash-based names
3. No category organization in MinIO

## Root Cause

In `backend/app/services/document.py`, the `create_document_with_file()` method was:
1. Using `self.minio_service.generate_object_name(file.filename)` (UUID-based)
2. Categorizing files AFTER uploading to MinIO
3. Using MD5 hash instead of SHA256

## Fix Applied

Updated `create_document_with_file()` to:

1. **Categorize FIRST** (before generating path):
```python
# Auto-categorize file based on extension FIRST
from app.utils.file_categorizer import FileCategorizer
from app.utils.minio_paths import get_minio_object_path
categorizer = FileCategorizer()
file_category, confidence = categorizer.categorize_file(file.filename)
```

2. **Use SHA256** for consistency:
```python
file_hash_obj = hashlib.sha256()  # Changed from MD5
```

3. **Generate consistent path**:
```python
file_hash = file_hash_obj.hexdigest()
minio_object_name = get_minio_object_path(user_id, file_hash, file_category, file.filename)
```

4. **Remove duplicate categorization** later in the code

## Result

Both upload methods now use identical path generation:
- Format: `{user_id}/{category}/{sha256_hash}.{ext}`
- Example: `2/master/abc123...def.dng`
- Example: `2/export_high/xyz789...uvw.jpg`

## File Comparison

**Before:**
- First file (via `create_document_with_file`): `c02e69cc-2e0b-4c41-a185-f871c28ace41.dng`
- Second file (via `upload_document_image`): `files/2/54c7c33eb9e93b1ced372bdf84427fa43555f11c085f444433619c0d1fec6949`

**After:**
- First file: `2/master/3bf1e8efb5c0145f64708e0a7f83cf6b.dng`
- Second file: `2/export_high/54c7c33eb9e93b1ced372bdf84427fa43555f11c085f444433619c0d1fec6949.jpg`

## Files Modified

1. `backend/app/services/document.py`
   - Lines 230-248: Categorize first, then generate path
   - Line 237: Changed to SHA256
   - Line 248: Use `get_minio_object_path()`
   - Line 258: Use `file_hash` variable
   - Line 288: Removed duplicate categorization

## Status

✅ Both upload methods now use consistent category-based paths
✅ SHA256 hash used throughout
✅ Backend restarted successfully

## Testing

Try uploading a new document with 2 files to verify:
1. Both files should appear in correct MinIO paths
2. Paths should follow pattern: `{user_id}/{category}/{hash}.{ext}`
3. File categories should display correctly in frontend
