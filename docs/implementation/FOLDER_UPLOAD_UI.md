# Folder Upload UI Feature

Implementation of web dashboard UI for uploading ECO-MiC folder structures.

**Date**: December 13, 2025
**Feature**: Folder Upload with ZIP and Direct Folder Support

---

## Overview

Added a complete UI component to the web dashboard that allows users to upload ECO-MiC compliant folder structures either as ZIP archives or by selecting folders directly from their file system.

## Implementation

### New Component

**File**: `/frontend/src/components/FolderUpload.vue`

A full-featured Vue component with:
- **Dual upload modes**: ZIP archive or direct folder selection
- **Drag-and-drop support**: Intuitive file upload interface
- **Folder structure detection**: Shows detected ECO-MiC folders before upload
- **Complete metadata form**: All required METS fields
- **Upload progress tracking**: Real-time progress with percentage and status
- **Categorization results**: Displays how files were categorized after upload
- **Error handling**: Clear error messages and validation

### Integration

**File**: `/frontend/src/components/DocumentsManager.vue`

Added folder upload option to the Batch Operations menu:
- New menu item: "Upload ECO-MiC Folder"
- Modal dialog integration
- Auto-refresh document list after successful upload

### Features

#### 1. Upload Type Selection

Users can choose between two methods:

**ZIP Archive**:
- Upload pre-compressed folder structure
- Faster for large datasets
- Compatible with archives created elsewhere

**Direct Folder**:
- Select folder directly from file system
- Automatically compressed in browser before upload
- Uses JSZip library loaded from CDN

#### 2. File Input Methods

- **Drag-and-drop**: Intuitive file/folder dragging
- **Click to browse**: Traditional file picker dialog
- **Visual feedback**: Highlight on drag-over

#### 3. Folder Structure Detection

When selecting a direct folder, the component:
- Analyzes the webkitRelativePath of all files
- Detects ECO-MiC folder names (TIF.Master, JPG300, etc.)
- Displays detected folders before upload
- Shows file count

#### 4. Metadata Form

Complete METS ECO-MiC metadata fields:
- **Logical ID** (required) - Unique document identifier
- **Title** (required) - Document title
- **Description** - Optional detailed description
- **Conservative ID** - Physical archive identifier (e.g., IT-MO0172)
- **Conservative ID Authority** - Authority system (e.g., ISIL)
- **Archive Name** - Institution name
- **Archive Contact** - Contact information
- **Document Type** - Dropdown with ECO-MiC standard types:
  - Risorsa manoscritta
  - Documento testuale
  - Risorsa a stampa
  - Risorsa cartografica
  - Risorsa grafica

#### 5. Upload Process

**For ZIP files**:
1. User selects/drops ZIP file
2. Fills in metadata form
3. Clicks "Upload Document"
4. File uploaded directly to backend
5. Progress bar shows upload percentage

**For direct folders**:
1. User selects folder from file system
2. Browser collects all files with paths
3. Shows detected folder structure
4. Fills in metadata form
5. Clicks "Upload Document"
6. JSZip compresses files (0-50% progress)
7. ZIP uploaded to backend (50-100% progress)
8. Progress bar shows combined progress

#### 6. Upload Results

After successful upload, displays:
- Success message with file count
- **File categorization breakdown**:
  - Shows each category (master, normalized, export_high, etc.)
  - File count per category
  - File use designation (PRESERVATION MASTER, SERVICE HIGH, etc.)
- Document ID for reference

Example categorization result:
```
Files categorized (11 total):
- Master Files: 2 file(s) - PRESERVATION MASTER
- Normalized: 2 file(s) - NORMALIZED MASTER
- High Quality Export: 2 file(s) - SERVICE HIGH
- Low Quality Export: 2 file(s) - SERVICE LOW
- Metadata: 1 file(s) - METADATA
- ICC Profiles: 1 file(s) - ICC PROFILE
- Logs: 1 file(s) - LOG
```

#### 7. Error Handling

Clear error messages for:
- Authentication failures
- File too large
- Invalid ZIP format
- Network errors
- Server-side validation errors

## Technical Details

### Browser API Usage

**Direct Folder Selection**:
Uses the `webkitdirectory` attribute:
```html
<input
  type="file"
  webkitdirectory
  directory
  multiple
  @change="handleFileSelect"
/>
```

This allows browsers to open a folder picker instead of file picker.

**File Path Preservation**:
Uses `file.webkitRelativePath` to maintain folder structure:
```javascript
selectedFiles.value.forEach(file => {
  zip.file(file.webkitRelativePath, file)
})
```

### JSZip Integration

Loaded from CDN (ESM module):
```javascript
const JSZip = (await import('https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm')).default
```

Creates ZIP on-the-fly with progress tracking:
```javascript
const zipBlob = await zip.generateAsync(
  { type: 'blob' },
  (metadata) => {
    uploadProgress.value = Math.round(metadata.percent / 2)
  }
)
```

### Upload Progress

Combined progress calculation:
- **ZIP mode**: 0-100% = direct upload progress
- **Folder mode**:
  - 0-50% = ZIP generation
  - 50-100% = upload progress

### API Integration

Sends FormData with:
- `zip_file`: ZIP blob or file
- `logical_id`, `title`, etc.: Metadata fields

Endpoint: `POST /api/documents/upload-folder`

## User Interface

### Visual Design

- **Modern card-based layout**: Clean, professional appearance
- **Color-coded elements**:
  - Blue: Primary actions and progress
  - Green: Success states
  - Red: Errors and warnings
  - Indigo: Folder-specific elements
- **Responsive grid layouts**: 2-column forms adapt to screen size
- **Clear visual hierarchy**: Step-by-step flow
- **Icons**: Intuitive SVG icons for all actions

### User Flow

1. **Dashboard** → Click "Batch Operations"
2. **Menu** → Select "Upload ECO-MiC Folder"
3. **Modal opens** → Choose upload method (ZIP or Folder)
4. **Select files** → Drag-drop or click to browse
5. **Review selection** → See detected structure
6. **Fill metadata** → Complete required fields
7. **Upload** → Click "Upload Document" button
8. **Monitor progress** → Watch upload percentage
9. **View results** → See categorization breakdown
10. **Auto-close** → Modal closes after 2 seconds, document list refreshes

## Browser Compatibility

### Folder Selection Support

The `webkitdirectory` attribute is supported in:
- ✅ Chrome/Edge (all versions)
- ✅ Firefox 50+
- ✅ Safari 11.1+
- ❌ Internet Explorer (not supported)

For unsupported browsers, users can fall back to ZIP upload method.

### File API Support

Requires modern File API support:
- `FileReader`
- `FormData`
- `Blob`

All modern browsers (last 5 years) supported.

## Testing

### Test Case 1: ZIP Archive Upload

1. Navigate to `/tests/test_ecomic_structure/`
2. Open dashboard → Batch Operations → Upload ECO-MiC Folder
3. Select "ZIP Archive" mode
4. Drag `TEST_DOC_001.zip` or click to browse
5. Fill in metadata:
   - Logical ID: `TEST_DOC_001`
   - Title: `Sample Archival Document`
6. Click "Upload Document"
7. Verify: 11 files categorized across 7 categories

### Test Case 2: Direct Folder Upload

1. Open dashboard → Batch Operations → Upload ECO-MiC Folder
2. Select "Direct Folder" mode
3. Click upload area (folder picker opens)
4. Navigate to `tests/test_ecomic_structure/TEST_DOC_001/`
5. Select the folder
6. Verify detected folders shown:
   - ICC
   - JPG150
   - JPG300
   - Logs
   - Metadata
   - TIF.Derived
   - TIF.Master
7. Fill in metadata
8. Click "Upload Document"
9. Watch progress: 0-50% (compressing), 50-100% (uploading)
10. Verify: Same categorization as ZIP method

### Test Case 3: Error Handling

**Invalid file type**:
- Drop a .pdf file in ZIP mode
- Verify: Clear error message

**Missing required fields**:
- Select folder but leave Logical ID empty
- Verify: Upload button disabled

**Network error**:
- Disconnect network during upload
- Verify: Clear error message with details

## Performance Considerations

### Large Folders

For folders with many files (100+ files):
- ZIP generation happens in browser (may take 30-60 seconds)
- Progress bar shows real-time compression progress
- No server timeout as compression is client-side

### File Size Limits

- **Individual files**: 80GB max (DNG support)
- **Total ZIP size**: 5GB recommended (browser memory limit)
- **Chunk upload**: Automatic for files > 64MB

### Memory Usage

Direct folder upload:
- Browser loads all files into memory
- JSZip compresses in-memory
- For very large folders (> 5GB), recommend:
  - Pre-compress to ZIP externally
  - Use ZIP upload mode

## Future Enhancements

### Potential Improvements

1. **Validation preview**: Show categorization before upload
2. **Edit categorization**: Allow manual category override
3. **Resume support**: Pause/resume large uploads
4. **Batch folder upload**: Multiple folders in one operation
5. **Template support**: Save metadata as template for reuse
6. **Drag folder directly**: Support folder drag-drop (Chrome only)

### Technical Debt

- JSZip loaded from CDN (consider bundling in production)
- No retry logic for failed uploads
- No browser storage for draft uploads

## Documentation

For end users:
- Add to user guide with screenshots
- Create video tutorial for folder selection
- Document ECO-MiC folder structure requirements

For developers:
- Component API documentation
- Integration guide for other upload types
- Browser compatibility matrix

## Related Files

**Frontend**:
- `/frontend/src/components/FolderUpload.vue` - Main component
- `/frontend/src/components/DocumentsManager.vue` - Integration point

**Backend**:
- `/backend/app/routes/documents.py:361-391` - API endpoint
- `/backend/app/services/document.py:1141-1319` - Upload service
- `/backend/app/utils/file_categorizer.py` - Categorization logic

**Documentation**:
- `/docs/implementation/IMPLEMENTATION_CAPABILITIES.md` - Backend capabilities
- `/tests/test_ecomic_structure/README.md` - Test folder structure
- `/tests/test_ecomic_structure/USAGE_INSTRUCTIONS.md` - Usage guide

---

## Summary

The folder upload UI feature provides a complete, user-friendly interface for uploading ECO-MiC compliant folder structures directly from the web dashboard. It supports both ZIP archives and direct folder selection, with automatic compression, real-time progress tracking, and detailed categorization results.

Users can now upload complete document archives with minimal technical knowledge, following the same ECO-MiC standards used by professional digitization workflows.

---

Last updated: December 13, 2025
