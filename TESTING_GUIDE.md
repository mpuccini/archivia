# Testing Guide for New Batch Import and Image Upload Features

## Overview
This guide covers testing the newly implemented features:
1. **Excel Batch Import**: Import multiple documents from an Excel file
2. **Single Image Upload**: Upload one image to a specific document  
3. **Batch Image Upload**: Upload multiple images that auto-match to documents by filename

## Prerequisites
- Application running on http://localhost:3000
- Test files available in `/Users/marco/source/archivia/`:
  - `test_batch_import.xlsx` - Excel file with 5 sample documents
  - `test_images/` directory with sample images (DOC001.jpg through DOC005.jpg, plus alternatives)

## Test Scenarios

### 1. Excel Batch Import Test

**Objective**: Test importing multiple documents from Excel file

**Steps**:
1. Navigate to http://localhost:3000
2. Login if required
3. Click the new "Batch Import Excel" button (green button in header)
4. Upload `test_batch_import.xlsx`
5. Verify Excel file is parsed correctly showing 5 documents
6. Review the preview table with document metadata
7. Click "Create X Documents" to import
8. Verify success message and document count

**Expected Results**:
- Excel file uploads successfully
- 5 documents shown in preview: DOC001-DOC005
- All documents created with proper metadata
- Documents appear in main document list

### 2. Single Image Upload Test

**Objective**: Test uploading one image to a specific document

**Steps**:
1. From the document list, find a document (e.g., DOC001)
2. Click the dropdown menu (⋮) for that document
3. Select "Upload Image" from the menu
4. Upload `test_images/DOC001.jpg`
5. Verify upload success

**Expected Results**:
- Image upload modal opens for specific document
- File uploads successfully 
- Success message appears
- Document now shows it has files attached

### 3. Batch Image Upload Test

**Objective**: Test uploading multiple images that auto-match to documents

**Steps**:
1. Click the "Upload Images" button (purple button in header)
2. Select "Batch Upload" mode
3. Upload multiple files from `test_images/` directory
4. Verify matching status for each file:
   - DOC001.jpg → Matches DOC001
   - DOC002.jpg → Matches DOC002
   - DOC999.jpg → Will create new document
5. Click "Upload X Images"
6. Verify results

**Expected Results**:
- Files show correct matching status
- Existing documents get images attached
- New documents created for unmatched logical_ids
- Success/error summary displayed

### 4. Conflict Resolution Test

**Objective**: Test handling of conflicts during batch upload

**Steps**:
1. Upload multiple images with same logical_id (e.g., DOC001.jpg and DOC001_alt.jpg)
2. Verify conflict resolution options appear
3. Choose resolution strategy
4. Complete upload

**Expected Results**:
- Conflicts detected and presented to user
- User can choose resolution strategy
- Upload completes based on choice

## Test Data

### Excel File Contents (`test_batch_import.xlsx`):
- DOC001: Sample Document 1, Test Archive, manuscript
- DOC002: Sample Document 2, Test Archive, book  
- DOC003: Sample Document 3, Main Archive, letter
- DOC004: Sample Document 4, Main Archive, report
- DOC005: Sample Document 5, Digital Collection, photograph

### Test Images:
- DOC001.jpg through DOC005.jpg (match documents)
- DOC999.jpg (will create new document)
- DOC001_alt.jpg (for conflict testing)

## Error Scenarios to Test

1. **Invalid Excel File**: Upload non-Excel file
2. **Empty Excel File**: Upload Excel with no data
3. **Missing logical_id**: Excel with empty required fields
4. **Invalid Image Format**: Upload unsupported file type
5. **Large File**: Upload file exceeding size limit
6. **Duplicate logical_id**: Import document with existing logical_id
7. **Network Error**: Test with backend offline

## Success Criteria

✅ Excel files parse correctly and show preview
✅ Batch document creation works with proper error handling
✅ Single image upload associates with correct document
✅ Batch image upload matches files to documents by filename
✅ New documents created for unmatched image filenames
✅ Conflict resolution works for duplicate filenames
✅ Proper error messages for invalid inputs
✅ UI provides good feedback during operations
✅ All operations update the document list properly

## Notes

- The frontend uses XLSX.js for Excel parsing
- Image formats supported: JPG, PNG, TIFF, PDF
- File size limit: 50MB per image
- Filename matching is case-sensitive for logical_id
- Created documents without images can have images added later
