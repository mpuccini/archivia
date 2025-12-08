"""
Alembic migration: Add comprehensive metadata fields to document_files table

To run this migration:
1. Make sure you're in the backend directory
2. Run: alembic upgrade head

Or manually run the SQL statements below in your PostgreSQL database
"""

# Manual migration SQL (if not using Alembic):
SQL_UPGRADE = """
-- Add new metadata fields to document_files table
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS format_name VARCHAR(100);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS byte_order VARCHAR(20);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS orientation VARCHAR(50);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS icc_profile_name VARCHAR(255);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanner_model_name VARCHAR(255);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanning_software_name VARCHAR(255);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanning_software_version VARCHAR(100);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS raw_metadata JSONB;

-- Add comments for documentation
COMMENT ON COLUMN document_files.format_name IS 'MIME type of the image file (e.g., image/tiff, image/dng)';
COMMENT ON COLUMN document_files.byte_order IS 'Byte order of the file (e.g., little endian, big endian)';
COMMENT ON COLUMN document_files.orientation IS 'Image orientation (e.g., normal*, rotate 90)';
COMMENT ON COLUMN document_files.icc_profile_name IS 'ICC color profile name';
COMMENT ON COLUMN document_files.scanner_model_name IS 'Scanner or camera model name';
COMMENT ON COLUMN document_files.scanning_software_name IS 'Software used for scanning/capture';
COMMENT ON COLUMN document_files.scanning_software_version IS 'Version of scanning software';
COMMENT ON COLUMN document_files.raw_metadata IS 'Complete JSON object containing ALL extracted EXIF/DNG metadata tags';

-- Create index on raw_metadata for faster queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_document_files_raw_metadata ON document_files USING gin (raw_metadata);
"""

SQL_DOWNGRADE = """
-- Remove added metadata fields
ALTER TABLE document_files DROP COLUMN IF EXISTS format_name;
ALTER TABLE document_files DROP COLUMN IF EXISTS byte_order;
ALTER TABLE document_files DROP COLUMN IF EXISTS orientation;
ALTER TABLE document_files DROP COLUMN IF EXISTS icc_profile_name;
ALTER TABLE document_files DROP COLUMN IF EXISTS scanner_model_name;
ALTER TABLE document_files DROP COLUMN IF EXISTS scanning_software_name;
ALTER TABLE document_files DROP COLUMN IF EXISTS scanning_software_version;
ALTER TABLE document_files DROP COLUMN IF EXISTS raw_metadata;

-- Drop index
DROP INDEX IF EXISTS idx_document_files_raw_metadata;
"""

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE MIGRATION: Add Comprehensive Metadata Fields")
    print("=" * 80)
    print("\nTo apply this migration, run the following SQL in your PostgreSQL database:\n")
    print(SQL_UPGRADE)
    print("\n" + "=" * 80)
    print("\nTo rollback this migration, run:\n")
    print(SQL_DOWNGRADE)
    print("\n" + "=" * 80)
