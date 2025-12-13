-- Migration: Consolidate duplicate documents and categorize files
-- Date: 2025-12-11
-- Purpose: Fix documents created by batch upload that should be one document with multiple files

-- Step 1: Get file IDs for both documents
-- Document 7: Calcata_ASCC_Are1_1_01.jpg
-- Document 8: sample1.dng

-- Step 2: Update document 7 to be the main document with proper metadata
UPDATE documents
SET
    logical_id = 'Calcata_ASCC_Are1_1_01',
    title = 'Calcata ASCC Are1 1 01',
    updated_at = NOW()
WHERE id = 7;

-- Step 3: Move the file from document 8 to document 7
UPDATE document_files
SET
    document_id = 7,
    sequence_number = 2
WHERE document_id = 8;

-- Step 4: Delete the empty document 8
DELETE FROM documents WHERE id = 8;

-- Step 5: Auto-categorize files based on extension
-- DNG files = master
UPDATE document_files df
SET file_category = 'master'
FROM files f
WHERE df.file_id = f.id
AND (
    f.content_type = 'image/x-adobe-dng'
    OR f.original_filename ILIKE '%.dng'
    OR f.original_filename ILIKE '%.raw'
    OR f.original_filename ILIKE '%.cr2'
    OR f.original_filename ILIKE '%.nef'
);

-- JPEG files = export_high (default for JPEG)
UPDATE document_files df
SET file_category = 'export_high'
FROM files f
WHERE df.file_id = f.id
AND df.file_category IS NULL
AND (
    f.content_type LIKE 'image/jpeg%'
    OR f.original_filename ILIKE '%.jpg'
    OR f.original_filename ILIKE '%.jpeg'
);

-- TIFF files = normalized (default for TIFF)
UPDATE document_files df
SET file_category = 'normalized'
FROM files f
WHERE df.file_id = f.id
AND df.file_category IS NULL
AND (
    f.content_type LIKE 'image/tiff%'
    OR f.original_filename ILIKE '%.tif'
    OR f.original_filename ILIKE '%.tiff'
);

-- Set sequence numbers for files without them
UPDATE document_files df
SET sequence_number = subquery.row_num
FROM (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY created_at) as row_num
    FROM document_files
    WHERE sequence_number IS NULL
) AS subquery
WHERE df.id = subquery.id;

-- Verify results
SELECT
    d.id as doc_id,
    d.logical_id,
    d.title,
    f.original_filename,
    df.file_category,
    df.sequence_number
FROM documents d
JOIN document_files df ON d.id = df.document_id
JOIN files f ON df.file_id = f.id
ORDER BY d.id, df.sequence_number;
