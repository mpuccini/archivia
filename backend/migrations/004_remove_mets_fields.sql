-- Migration 004: Remove METS ECO-MiC metadata fields from documents table
-- These fields are now stored in MongoDB for better flexibility and versioning

-- Remove core METS identifiers
ALTER TABLE documents DROP COLUMN IF EXISTS conservative_id;
ALTER TABLE documents DROP COLUMN IF EXISTS conservative_id_authority;
ALTER TABLE documents DROP COLUMN IF EXISTS title;
ALTER TABLE documents DROP COLUMN IF EXISTS description;
ALTER TABLE documents DROP COLUMN IF EXISTS type_of_resource;

-- Remove archive hierarchy fields
ALTER TABLE documents DROP COLUMN IF EXISTS archive_name;
ALTER TABLE documents DROP COLUMN IF EXISTS archive_contact;
ALTER TABLE documents DROP COLUMN IF EXISTS fund_name;
ALTER TABLE documents DROP COLUMN IF EXISTS series_name;
ALTER TABLE documents DROP COLUMN IF EXISTS folder_number;

-- Remove temporal fields
ALTER TABLE documents DROP COLUMN IF EXISTS date_from;
ALTER TABLE documents DROP COLUMN IF EXISTS date_to;
ALTER TABLE documents DROP COLUMN IF EXISTS period;

-- Remove geographic/contextual fields
ALTER TABLE documents DROP COLUMN IF EXISTS location;
ALTER TABLE documents DROP COLUMN IF EXISTS language;
ALTER TABLE documents DROP COLUMN IF EXISTS subjects;

-- Remove agent fields (producer/creator)
ALTER TABLE documents DROP COLUMN IF EXISTS producer_name;
ALTER TABLE documents DROP COLUMN IF EXISTS producer_type;
ALTER TABLE documents DROP COLUMN IF EXISTS producer_role;
ALTER TABLE documents DROP COLUMN IF EXISTS creator_name;
ALTER TABLE documents DROP COLUMN IF EXISTS creator_type;
ALTER TABLE documents DROP COLUMN IF EXISTS creator_role;

-- Remove rights fields
ALTER TABLE documents DROP COLUMN IF EXISTS license_url;
ALTER TABLE documents DROP COLUMN IF EXISTS rights_statement;
ALTER TABLE documents DROP COLUMN IF EXISTS rights_category;
ALTER TABLE documents DROP COLUMN IF EXISTS rights_holder;
ALTER TABLE documents DROP COLUMN IF EXISTS rights_constraint;

-- Remove technical fields (document-level)
ALTER TABLE documents DROP COLUMN IF EXISTS image_producer;
ALTER TABLE documents DROP COLUMN IF EXISTS scanner_manufacturer;
ALTER TABLE documents DROP COLUMN IF EXISTS scanner_model;

-- Remove physical structure fields
ALTER TABLE documents DROP COLUMN IF EXISTS document_type;
ALTER TABLE documents DROP COLUMN IF EXISTS total_pages;
ALTER TABLE documents DROP COLUMN IF EXISTS physical_form;
ALTER TABLE documents DROP COLUMN IF EXISTS extent_description;

-- Remove METS header fields
ALTER TABLE documents DROP COLUMN IF EXISTS record_status;
ALTER TABLE documents DROP COLUMN IF EXISTS mets_xml;

-- Total: 34 METS-specific fields removed from PostgreSQL
-- These are now managed in MongoDB for better schema flexibility
