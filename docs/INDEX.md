# Archivia Documentation Index

This directory contains all technical documentation for the Archivia digital archive management system.

## Directory Structure

```
docs/
├── INDEX.md (this file)
├── implementation/     - Feature implementation documentation
├── troubleshooting/    - Bug fixes and issue resolutions
└── archive/            - Obsolete or superseded documentation
```

## Implementation Documentation

Located in `docs/implementation/`

### METS & Validation
- **METS_VALIDATION_STRATEGY.md** - Analysis of METS validation approaches and strategy selection
- **VALIDATION_IMPLEMENTATION_COMPLETE.md** - Implementation details of validation strategy changes
- **METS_ECOMIC_FILE_CATEGORIZATION.md** - ECO-MiC file categorization system

### File Management
- **FILE_CATEGORIZATION_IMPLEMENTATION.md** - File categorization feature implementation
- **MINIO_STORAGE_STRATEGY.md** - MinIO object storage architecture and path strategy
- **PATH_GENERATION_FIX.md** - Standardization of MinIO path generation

### Implementation Capabilities
- **IMPLEMENTATION_CAPABILITIES.md** - Complete analysis of implemented features (multipart upload, folder upload, exports)
- **FOLDER_UPLOAD_UI.md** - Web dashboard UI for uploading ECO-MiC folder structures (ZIP and direct folder support)

## Troubleshooting Documentation

Located in `docs/troubleshooting/`

### Upload Issues
- **UPLOAD_FIX_COMPLETE.md** - Database schema fixes for SHA256 hash support
- **UPLOAD_ISSUE_RESOLVED.md** - Resolution of file upload failures (checksum_md5 column)
- **UPLOAD_FLOW_FIXES.md** - Complete upload workflow fixes

### System Status
- **CURRENT_STATUS.md** - Latest system status and known issues
- **ARCHITECTURE_FIX_2025-12-11.md** - Architecture improvements (Dec 11, 2025)
- **COMPLETE_FIX_SUMMARY.md** - Comprehensive summary of all fixes applied
- **FINAL_FIXES_SUMMARY.md** - Final status of bug fixes and improvements

## Archive

Located in `docs/archive/`

Contains obsolete or superseded documentation:
- **DESIGN_ISSUE_RESOLUTION.md** - Failed attempt at UI redesign (Dec 12, 2025)
- **MODERN_DESIGN_APPLIED.md** - Modern design system attempt (reverted)

## Root Documentation

Located in project root `/`

- **README.md** - Project overview and setup instructions
- **CLAUDE.md** - Instructions for Claude Code AI assistant

## Test Files

Located in `tests/`

- `test_batch_import.csv` - CSV test data for batch import
- `test_batch_import.xlsx` - Excel test data for batch import
- `test_export.csv` - Export functionality test data
- `test_metadata.csv` - Metadata import test data
- `test_metadata.xml` - XML metadata test data
- `test_metadata_simple.xml` - Simplified XML test data
- `test_mets_validation.py` - METS validation unit tests
- `test_ecomic_structure/` - Complete ECO-MiC folder structure for testing folder upload
  - `TEST_DOC_001.zip` - Sample ECO-MiC compliant document (11 files)
  - `README.md` - Folder structure documentation
  - `USAGE_INSTRUCTIONS.md` - Step-by-step upload and verification guide

## Key Topics Quick Reference

### Upload Issues
1. Start with `UPLOAD_ISSUE_RESOLVED.md` (most recent)
2. See `UPLOAD_FIX_COMPLETE.md` for database schema details
3. Check `CURRENT_STATUS.md` for current state

### METS ECO-MiC Implementation
1. Read `METS_VALIDATION_STRATEGY.md` for overall approach
2. See `VALIDATION_IMPLEMENTATION_COMPLETE.md` for implementation
3. Check `METS_ECOMIC_FILE_CATEGORIZATION.md` for file handling

### MinIO Storage
1. Read `MINIO_STORAGE_STRATEGY.md` for architecture
2. See `PATH_GENERATION_FIX.md` for path standardization
3. Check `FILE_CATEGORIZATION_IMPLEMENTATION.md` for categorization

### Recent Issues (December 2025)
- **Dec 13**: Folder upload UI feature - see `implementation/FOLDER_UPLOAD_UI.md`
- **Dec 13**: Implementation capabilities analysis - see `implementation/IMPLEMENTATION_CAPABILITIES.md`
- **Dec 12**: UI redesign attempt (failed, reverted) - see `archive/`
- **Dec 11**: Upload fixes (checksum_md5 column extension) - see `troubleshooting/`
- **Nov-Dec**: METS validation strategy changes - see `implementation/`

## Maintenance

When adding new documentation:

1. **Implementation docs** → `docs/implementation/`
   - New features
   - Architecture decisions
   - Design patterns

2. **Troubleshooting docs** → `docs/troubleshooting/`
   - Bug fixes
   - Issue resolutions
   - Status updates

3. **Archive docs** → `docs/archive/`
   - Obsolete documentation
   - Failed experiments
   - Superseded approaches

4. **Update this index** with the new document

## Document Naming Conventions

- Use UPPERCASE for major documentation files
- Use descriptive names (e.g., `METS_VALIDATION_STRATEGY.md`)
- Include dates for time-sensitive docs (e.g., `ARCHITECTURE_FIX_2025-12-11.md`)
- Prefix with topic for related docs (e.g., `UPLOAD_*`, `METS_*`)

## Testing Resources

### ECO-MiC Folder Upload Testing
1. Navigate to `tests/test_ecomic_structure/`
2. Use `TEST_DOC_001.zip` for testing folder upload feature
3. Follow `USAGE_INSTRUCTIONS.md` for complete testing workflow
4. Verify all 11 files are categorized correctly across 7 categories

---

Last updated: December 13, 2025
