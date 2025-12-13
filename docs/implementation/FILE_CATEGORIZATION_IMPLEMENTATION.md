# File Categorization Implementation

## Overview

This document describes the implementation of file categorization for archival digitization workflows, following the ECO-MiC 5.3 and 5.4 guidelines.

## Problem Statement

Archival documents are digitized into multiple file formats for different purposes:
- **Master files**: Preservation-quality RAW/DNG files
- **Normalized files**: Standardized TIFF exports
- **Export files**: Compressed JPEG files for web delivery
- **Metadata files**: XML, METS, and other descriptive files
- **Support files**: ICC profiles, logs, etc.

These files are organized in structured folders (e.g., `TIF.Master`, `JPG300`, `Metadata`), and the system needs to:
1. Automatically detect file categories based on folder structure and file extensions
2. Preserve this logical structure in the database
3. Display files grouped by category in the UI
4. Generate METS XML that properly represents this structure

## Implementation

### 1. Database Changes

**Added to `DocumentFile` model:**
```python
file_category = Column(String(50), nullable=True)
# Values: "master", "normalized", "export_high", "export_low", "metadata", "icc", "logs", "other"
```

**Schema updated:**
- `DocumentFileSchema` now includes `file_category` field
- Compatible with existing `file_use` field (METS fileGrp USE attribute)

### 2. File Categorization Service

**Location:** `backend/app/utils/file_categorizer.py`

**Key Features:**
- `categorize_file(filename, folder_path)`: Auto-detect category with confidence score
- `get_file_use_from_category(category)`: Map category to METS USE attribute
- `validate_folder_structure(file_list)`: Analyze and group files by category

**Detection Logic:**
1. **High confidence (0.95)**: Folder-based detection
   - `TIF.Master/`, `Master/`, `RAW/` → master
   - `TIF.Derived/`, `Normalized/` → normalized
   - `JPG300/`, `Export300/` → export_high
   - `JPG150/`, `Export150/` → export_low

2. **Medium confidence (0.75)**: Extension-based detection
   - `.dng`, `.raw`, `.cr2`, `.nef` → master
   - `.tif`, `.tiff` with "master" in name → master
   - `.tif`, `.tiff` with "derived" in name → normalized
   - `.jpg`, `.jpeg` with "300" or "high" → export_high
   - `.jpg`, `.jpeg` with "150" or "low" → export_low
   - `.xml`, `.mets` → metadata
   - `.icc`, `.icm` → icc
   - `.log`, `.txt` → logs

3. **Low confidence (0.3)**: Fallback to "other"

### 3. Planned Features

#### Folder Upload
- Accept ZIP archives containing structured folders
- Extract files while preserving folder paths
- Auto-categorize all files
- Present categorization results to user for confirmation

#### UI Enhancements
- Group files by category in DocumentDetailModal
- Visual indicators for each category (icons, colors)
- Category edit/override capability
- Bulk re-categorization

#### METS Export
- Proper `<mets:fileGrp USE="MASTER">` sections per category
- Maintain file relationships in structural map
- Include category metadata in techMD sections

## ECO-MiC Compliance

Follows ECO-MiC Profile 1.2 Section 5.3 and 5.4:
- ✅ Distinguishes preservation master from derived files
- ✅ Supports multiple derived formats (TIFF, JPEG at different qualities)
- ✅ Recognizes standard folder naming conventions
- ✅ Preserves metadata and support files

## File Naming Convention Support

Supports ECO-MiC 5.4 naming patterns:
- Library Code - Significant Name - Progressive Number
- Fund Acronym - Series - File - Progressive Number
- Recto/Verso notation: `-r`, `-v` suffixes
- Color scale notation: `-c` suffix

## Migration Path

**For existing documents:**
- `file_category` is nullable - existing records unaffected
- Can be populated via:
  1. Manual categorization in UI
  2. Batch re-categorization script
  3. Re-upload with folder structure

**For new uploads:**
- Auto-categorization on upload
- User confirmation step before final save
- Default to existing behavior if no categorization detected

## Next Steps

1. ✅ Database schema updated
2. ✅ Categorization service implemented
3. ⏳ Folder upload endpoint
4. ⏳ Frontend UI for grouped display
5. ⏳ User confirmation workflow
6. ⏳ METS generator updates

---

**Status:** In Progress
**Last Updated:** 2025-12-09
**Version:** 1.0
