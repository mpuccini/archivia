-- Migration 003: Add mets_document_id column to documents table
-- This column will store the MongoDB ObjectId reference

-- Add mets_document_id column
ALTER TABLE documents
ADD COLUMN mets_document_id VARCHAR(24);

-- Add index for faster lookups
CREATE INDEX idx_documents_mets_document_id ON documents(mets_document_id);

-- Add comment explaining the column
COMMENT ON COLUMN documents.mets_document_id IS 'MongoDB ObjectId reference to METS ECO-MiC metadata document';
