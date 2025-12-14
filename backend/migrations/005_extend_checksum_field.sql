-- Migration 005: Extend checksum_md5 field to support SHA256 hashes
-- SHA256 produces 64-character hex strings, MD5 produces 32 characters
-- The field name is misleading but we're keeping it for backward compatibility

-- Extend the checksum_md5 column to VARCHAR(64) to support SHA256
ALTER TABLE document_files ALTER COLUMN checksum_md5 TYPE VARCHAR(64);

-- Add comment explaining the field supports both MD5 and SHA256
COMMENT ON COLUMN document_files.checksum_md5 IS 'File checksum (MD5 32 chars or SHA256 64 chars)';
