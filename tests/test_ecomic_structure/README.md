# METS ECO-MiC Test Folder Structure

This folder contains a sample ECO-MiC compliant document structure for testing the folder upload feature.

## Document Information

- **Logical ID**: TEST_DOC_001
- **Title**: Sample Archival Document for Testing
- **Description**: Test document demonstrating ECO-MiC folder structure
- **Conservative ID**: IT-TEST-0001
- **Document Type**: risorsa manoscritta

## Folder Structure

```
TEST_DOC_001/
├── TIF.Master/          # Preservation master files (uncompressed TIFF)
│   ├── TEST_DOC_001_0001.tif
│   └── TEST_DOC_001_0002.tif
├── TIF.Derived/         # Normalized TIFF files (Adobe RGB, 2400px)
│   ├── TEST_DOC_001_0001.tif
│   └── TEST_DOC_001_0002.tif
├── JPG300/              # High-quality export (300 DPI)
│   ├── TEST_DOC_001_0001.jpg
│   └── TEST_DOC_001_0002.jpg
├── JPG150/              # Low-quality export (150 DPI, web)
│   ├── TEST_DOC_001_0001.jpg
│   └── TEST_DOC_001_0002.jpg
├── Metadata/            # Metadata files
│   └── TEST_DOC_001_metadata.xml
├── ICC/                 # ICC color profiles
│   └── AdobeRGB1998.icc
└── Logs/                # Processing logs
    └── scan_log.txt
```

## File Categories According to ECO-MiC 5.4

| Folder | Category | File Use | Description |
|--------|----------|----------|-------------|
| TIF.Master | master | PRESERVATION MASTER | Preservation master files (uncompressed TIFF or DNG) |
| TIF.Derived | normalized | NORMALIZED MASTER | Normalized TIFF (Adobe RGB profile, 2400px) |
| JPG300 | export_high | SERVICE HIGH | High-quality JPEG (300 DPI, ~2400px) |
| JPG150 | export_low | SERVICE LOW | Web-quality JPEG (150 DPI, ~1200-1500px) |
| Metadata | metadata | METADATA | XML metadata files |
| ICC | icc | ICC PROFILE | ICC color profiles |
| Logs | logs | LOG | Processing logs |

## How to Use

### 1. Upload via API

```bash
# Create ZIP archive
cd tests/test_ecomic_structure
zip -r TEST_DOC_001.zip TEST_DOC_001/

# Upload to Archivia
curl -X POST http://localhost:8000/api/documents/upload-folder \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "zip_file=@TEST_DOC_001.zip" \
  -F "logical_id=TEST_DOC_001" \
  -F "title=Sample Archival Document for Testing" \
  -F "description=Test document demonstrating ECO-MiC folder structure" \
  -F "conservative_id=IT-TEST-0001" \
  -F "conservative_id_authority=ISIL" \
  -F "archive_name=Test Archive" \
  -F "archive_contact=test@example.com" \
  -F "document_type=risorsa manoscritta"
```

### 2. Expected Result

The system will:
1. Create a new document with logical_id "TEST_DOC_001"
2. Extract all files from the ZIP
3. Categorize files based on folder structure:
   - 2 files in "master" category (TIF.Master)
   - 2 files in "normalized" category (TIF.Derived)
   - 2 files in "export_high" category (JPG300)
   - 2 files in "export_low" category (JPG150)
   - 1 file in "metadata" category (Metadata)
   - 1 file in "icc" category (ICC)
   - 1 file in "logs" category (Logs)
4. Upload all files to MinIO storage
5. Generate METS XML with proper file categorization

### 3. Verify Upload

Check the API response for:
```json
{
  "success": true,
  "message": "Successfully uploaded 11 files",
  "document_id": 123,
  "categorized_files": {
    "master": [
      {"filename": "TEST_DOC_001_0001.tif", "category": "master", "confidence": 0.95, ...},
      {"filename": "TEST_DOC_001_0002.tif", "category": "master", "confidence": 0.95, ...}
    ],
    "normalized": [...],
    "export_high": [...],
    "export_low": [...],
    "metadata": [...],
    "icc": [...],
    "logs": [...]
  },
  "total_files": 11
}
```

## File Format Details

### Master TIFF Files
- Format: Uncompressed TIFF
- Color space: Adobe RGB (1998)
- Bit depth: 16-bit per channel (recommended) or 8-bit
- Resolution: Original scan resolution (typically 300-600 DPI)

### Normalized TIFF Files
- Format: TIFF with LZW compression (optional)
- Color space: Adobe RGB (1998) with embedded ICC profile
- Dimensions: Maximum 2400px on longest side
- Resolution: 300 DPI

### High-Quality JPEG (JPG300)
- Format: JPEG
- Quality: 85-95%
- Resolution: 300 DPI
- Dimensions: ~2400px on longest side

### Low-Quality JPEG (JPG150)
- Format: JPEG
- Quality: 70-85%
- Resolution: 150 DPI
- Dimensions: ~1200-1500px on longest side

## Alternative Folder Names

The system recognizes these alternative folder naming conventions:

### Master Files
- `TIF.Master`, `TIFF.Master`, `Master`, `RAW`

### Normalized Files
- `TIF.Derived`, `TIFF.Derived`, `Derived`, `Normalized`

### High-Quality Export
- `JPG300`, `JPEG300`, `Export300`, `High`

### Low-Quality Export
- `JPG150`, `JPEG150`, `Export150`, `Low`

### Metadata
- `Metadata`, `XML`, `METS`

### ICC Profiles
- `ICC`, `ColorProfiles`, `Profiles`

### Logs
- `Logs`, `Log`

## Testing Scenarios

1. **Complete structure**: All folders present (as shown above)
2. **Minimal structure**: Only Master + Metadata folders
3. **Master only**: Only preservation files (for raw digitization)
4. **Mixed case**: Test case-insensitive folder matching
5. **Alternative names**: Use different folder naming conventions

## References

- **ECO-MiC Profile**: http://www.iccu.sbn.it/metaAG1.pdf
- **METS Standard**: http://www.loc.gov/standards/mets/
- **GitHub Repository**: https://github.com/icdp-digital-library/profilo-mets-ecomic

---

Last updated: December 13, 2025
