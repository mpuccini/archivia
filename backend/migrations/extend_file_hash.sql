-- Extend file_hash column to support SHA256 (64 chars) instead of MD5 (32 chars)

ALTER TABLE files ALTER COLUMN file_hash TYPE VARCHAR(64);
