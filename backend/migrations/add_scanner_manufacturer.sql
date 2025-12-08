-- Migration: Add scanner_manufacturer and fix raw_metadata type
-- Run this to add the missing scanner_manufacturer field and convert raw_metadata to jsonb

BEGIN;

-- Add scanner_manufacturer column if not exists
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS scanner_manufacturer VARCHAR(255);

-- Add comment for documentation
COMMENT ON COLUMN document_files.scanner_manufacturer IS 'Scanner or camera manufacturer (e.g., Nikon, Canon)';

-- Convert raw_metadata from json to jsonb if needed
-- First, check if the column type needs conversion
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'document_files'
        AND column_name = 'raw_metadata'
        AND data_type = 'json'
    ) THEN
        -- Drop existing index if it exists
        DROP INDEX IF EXISTS idx_document_files_raw_metadata;

        -- Convert column type from json to jsonb
        ALTER TABLE document_files
        ALTER COLUMN raw_metadata TYPE JSONB USING raw_metadata::jsonb;

        -- Recreate GIN index on jsonb column
        CREATE INDEX idx_document_files_raw_metadata ON document_files USING gin (raw_metadata);
    END IF;
END $$;

COMMIT;

-- Verify the changes
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'document_files'
  AND column_name IN ('scanner_manufacturer', 'scanner_model_name', 'raw_metadata')
ORDER BY column_name;
