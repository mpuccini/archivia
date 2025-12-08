-- Migration: Add ECO-MiC 1.2 fields to documents and document_files tables
-- Date: 2025-12-05
-- Description: Adds new fields required for METS ECO-MiC 1.2 compliance

-- Add new fields to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS type_of_resource VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS producer_name VARCHAR(255);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS producer_type VARCHAR(20);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS producer_role VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS creator_name VARCHAR(255);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS creator_type VARCHAR(20);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS creator_role VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS rights_category VARCHAR(50);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS rights_holder VARCHAR(255);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS rights_constraint VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS physical_form VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS extent_description VARCHAR(255);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS record_status VARCHAR(20) DEFAULT 'COMPLETE';

-- Add new fields to document_files table
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS compression_scheme VARCHAR(50);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS color_space VARCHAR(50);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS sampling_frequency_unit VARCHAR(20);
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS x_sampling_frequency INTEGER;
ALTER TABLE document_files ADD COLUMN IF NOT EXISTS y_sampling_frequency INTEGER;

-- Set default value for record_status on existing records
UPDATE documents SET record_status = 'COMPLETE' WHERE record_status IS NULL;
