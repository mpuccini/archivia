-- Extend checksum_md5 column to support SHA256 (64 chars) instead of MD5 (32 chars)

ALTER TABLE document_files ALTER COLUMN checksum_md5 TYPE VARCHAR(64);
