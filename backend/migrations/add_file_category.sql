-- Migration: Add file_category column to document_files table
-- Date: 2025-12-11

-- Add file_category column
ALTER TABLE document_files
ADD COLUMN IF NOT EXISTS file_category VARCHAR(50);

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_document_files_category
ON document_files(file_category);

-- Verify the column was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'document_files'
AND column_name = 'file_category';
