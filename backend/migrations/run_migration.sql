-- Migration: Add comprehensive metadata fields to document_files table
-- Run this to fix the 500 error

BEGIN;

-- Add new metadata fields to document_files table
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS format_name VARCHAR(100);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS byte_order VARCHAR(20);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS orientation VARCHAR(50);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS icc_profile_name VARCHAR(255);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanner_manufacturer VARCHAR(255);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanner_model_name VARCHAR(255);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanning_software_name VARCHAR(255);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanning_software_version VARCHAR(100);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS raw_metadata JSONB;

-- Add comments for documentation
COMMENT ON COLUMN document_files.format_name IS 'MIME type of the image file (e.g., image/tiff, image/dng)';
COMMENT ON COLUMN document_files.byte_order IS 'Byte order of the file (e.g., little endian, big endian)';
COMMENT ON COLUMN document_files.orientation IS 'Image orientation (e.g., normal*, rotate 90)';
COMMENT ON COLUMN document_files.icc_profile_name IS 'ICC color profile name';
COMMENT ON COLUMN document_files.scanner_manufacturer IS 'Scanner or camera manufacturer (e.g., Nikon, Canon)';
COMMENT ON COLUMN document_files.scanner_model_name IS 'Scanner or camera model name (e.g., Nikon D850)';
COMMENT ON COLUMN document_files.scanning_software_name IS 'Software used for scanning/capture';
COMMENT ON COLUMN document_files.scanning_software_version IS 'Version of scanning software';
COMMENT ON COLUMN document_files.raw_metadata IS 'Complete JSON object containing ALL extracted EXIF/DNG metadata tags';

-- Create index on raw_metadata for faster queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_document_files_raw_metadata ON document_files USING gin (raw_metadata);

COMMIT;

-- Verify the changes
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'document_files'
ORDER BY ordinal_position;
