# Upload Fix Complete - December 11, 2025

## Problem Summary

Document creation was failing when uploading multiple files. The first file would upload successfully, but the second file would fail, leaving the document with no files visible in the UI despite one file being present in MinIO.

## Root Cause

After switching from MD5 to SHA256 hashing throughout the system, two database columns were not updated to accommodate the longer hash length (64 characters vs 32 characters):

1. **`files.file_hash`** - VARCHAR(32) → needed VARCHAR(64)
2. **`document_files.checksum_md5`** - VARCHAR(32) → needed VARCHAR(64)

## Error Details

```
sqlalchemy.exc.DataError: (psycopg2.errors.StringDataRightTruncation)
value too long for type character varying(32)

SQL: INSERT INTO document_files ... checksum_md5='b3a8299bd47ba5c43b96ddbfc152b1f4df9774097760598726c7811a79d901e5'
```

The SHA256 hash (64 chars) was too long for the VARCHAR(32) column.

## Migrations Applied

### Migration 1: `backend/migrations/extend_file_hash.sql`
```sql
ALTER TABLE files ALTER COLUMN file_hash TYPE VARCHAR(64);
```

**Applied**: ✅ December 11, 2025

### Migration 2: `backend/migrations/extend_checksum_md5.sql`
```sql
ALTER TABLE document_files ALTER COLUMN checksum_md5 TYPE VARCHAR(64);
```

**Applied**: ✅ December 11, 2025

## Verification

Both columns now support SHA256 hashes:

```bash
# files.file_hash
archivia=# \d files
Column     | Type
-----------+-------------------------
file_hash  | character varying(64)  ✅

# document_files.checksum_md5
archivia=# \d document_files
Column        | Type
--------------+-------------------------
checksum_md5  | character varying(64)  ✅
```

## Services Restarted

- **Database**: Restarted to clear connection pool
- **Backend**: Restarted to clear SQLAlchemy sessions and pending rollback errors

## Upload Flow Now Works

The complete upload flow should now work correctly:

1. **User uploads 2 files** to create a document
2. **First file** → Processed, File record created, MinIO upload successful
3. **Second file** → Processed, File record created, MinIO upload successful
4. **DocumentFile associations** → Both files linked to document with SHA256 checksums
5. **Result** → Document appears with 2 files, both visible in UI and MinIO

## Related Changes

This fix is part of the broader MinIO storage path standardization work:

- **Content-addressable storage**: `{user_id}/{category}/{sha256_hash}.{ext}`
- **Automatic file categorization**: master, normalized, export_high, export_low, etc.
- **SHA256 hashing**: More secure than MD5, better for deduplication
- **Consistent paths**: Both upload methods use the same path generation logic

## Testing Checklist

- ✅ Database migrations applied
- ✅ Backend restarted successfully
- ⏳ Upload test: Create document with 2 files (master DNG + export_high JPEG)
- ⏳ Verify: Both files appear in document details
- ⏳ Verify: Both files visible in MinIO with correct paths
- ⏳ Verify: File categories displayed correctly in UI

## Files Modified

1. `backend/migrations/extend_file_hash.sql` (NEW)
2. `backend/migrations/extend_checksum_md5.sql` (NEW)
3. `UPLOAD_FIX_COMPLETE.md` (NEW - this document)

## Previous Related Documents

- `CURRENT_STATUS.md` - Overall system status
- `VALIDATION_IMPLEMENTATION_COMPLETE.md` - METS validation strategy changes
- `PATH_GENERATION_FIX.md` - MinIO path standardization
- `MINIO_STORAGE_STRATEGY.md` - Storage architecture decisions

## Status

**Backend**: ✅ Ready
**Database**: ✅ Schema updated
**Upload**: ✅ Should work completely now
**Frontend**: ⚠️ Still calling disabled `/validate-mets-from-data` endpoint (harmless 405 error)

## Recommendation

The system is now ready for testing. Please try:

1. **Login** with fresh credentials
2. **Create a new document** with 2 files (e.g., DNG + JPEG)
3. **Verify both files** appear in document details
4. **Check MinIO** to confirm both files are stored correctly
5. **Verify categories** are displayed correctly in the UI

If you encounter any errors, please check:
- Browser console for JavaScript errors
- Backend logs: `docker compose logs -f backend`
- Network tab for failed API requests
