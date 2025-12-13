# How to Use the ECO-MiC Test Folder

## Quick Start

The test folder `TEST_DOC_001.zip` is ready to use for testing the folder upload feature.

### Using cURL (Command Line)

```bash
# 1. Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin" | jq -r '.access_token')

# 2. Upload the test folder
curl -X POST http://localhost:8000/api/documents/upload-folder \
  -H "Authorization: Bearer $TOKEN" \
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

### Expected Response

```json
{
  "success": true,
  "message": "Successfully uploaded 11 files",
  "document_id": 1,
  "categorized_files": {
    "master": [
      {
        "filename": "TEST_DOC_001_0001.tif",
        "category": "master",
        "confidence": 0.95,
        "file_use": "PRESERVATION MASTER",
        "folder": "TEST_DOC_001/TIF.Master"
      },
      {
        "filename": "TEST_DOC_001_0002.tif",
        "category": "master",
        "confidence": 0.95,
        "file_use": "PRESERVATION MASTER",
        "folder": "TEST_DOC_001/TIF.Master"
      }
    ],
    "normalized": [
      {
        "filename": "TEST_DOC_001_0001.tif",
        "category": "normalized",
        "confidence": 0.95,
        "file_use": "NORMALIZED MASTER",
        "folder": "TEST_DOC_001/TIF.Derived"
      },
      {
        "filename": "TEST_DOC_001_0002.tif",
        "category": "normalized",
        "confidence": 0.95,
        "file_use": "NORMALIZED MASTER",
        "folder": "TEST_DOC_001/TIF.Derived"
      }
    ],
    "export_high": [
      {
        "filename": "TEST_DOC_001_0001.jpg",
        "category": "export_high",
        "confidence": 0.95,
        "file_use": "SERVICE HIGH",
        "folder": "TEST_DOC_001/JPG300"
      },
      {
        "filename": "TEST_DOC_001_0002.jpg",
        "category": "export_high",
        "confidence": 0.95,
        "file_use": "SERVICE HIGH",
        "folder": "TEST_DOC_001/JPG300"
      }
    ],
    "export_low": [
      {
        "filename": "TEST_DOC_001_0001.jpg",
        "category": "export_low",
        "confidence": 0.95,
        "file_use": "SERVICE LOW",
        "folder": "TEST_DOC_001/JPG150"
      },
      {
        "filename": "TEST_DOC_001_0002.jpg",
        "category": "export_low",
        "confidence": 0.95,
        "file_use": "SERVICE LOW",
        "folder": "TEST_DOC_001/JPG150"
      }
    ],
    "metadata": [
      {
        "filename": "TEST_DOC_001_metadata.xml",
        "category": "metadata",
        "confidence": 0.95,
        "file_use": "METADATA",
        "folder": "TEST_DOC_001/Metadata"
      }
    ],
    "icc": [
      {
        "filename": "AdobeRGB1998.icc",
        "category": "icc",
        "confidence": 0.95,
        "file_use": "ICC PROFILE",
        "folder": "TEST_DOC_001/ICC"
      }
    ],
    "logs": [
      {
        "filename": "scan_log.txt",
        "category": "logs",
        "confidence": 0.95,
        "file_use": "LOG",
        "folder": "TEST_DOC_001/Logs"
      }
    ]
  },
  "total_files": 11
}
```

## Verification Steps

### 1. Check Database

```bash
docker compose exec db psql -U archivia -d archivia -c "
  SELECT d.logical_id, COUNT(df.id) as file_count
  FROM documents d
  LEFT JOIN document_files df ON d.id = df.document_id
  WHERE d.logical_id = 'TEST_DOC_001'
  GROUP BY d.logical_id;
"
```

Expected output:
```
 logical_id   | file_count
--------------+------------
 TEST_DOC_001 |         11
```

### 2. Check File Categories

```bash
docker compose exec db psql -U archivia -d archivia -c "
  SELECT file_category, COUNT(*) as count
  FROM document_files df
  JOIN documents d ON df.document_id = d.id
  WHERE d.logical_id = 'TEST_DOC_001'
  GROUP BY file_category
  ORDER BY file_category;
"
```

Expected output:
```
 file_category | count
---------------+-------
 export_high   |     2
 export_low    |     2
 icc           |     1
 logs          |     1
 master        |     2
 metadata      |     1
 normalized    |     2
```

### 3. Check MinIO Storage

```bash
# Access MinIO console
open http://localhost:9001

# Login: archivia / archivia123
# Navigate to bucket: archivia-files
# Verify all 11 files are uploaded
```

### 4. Export Document and Verify METS

```bash
# Get document ID from upload response (e.g., document_id: 1)
DOCUMENT_ID=1

# Export METS XML
curl -X GET "http://localhost:8000/api/documents/$DOCUMENT_ID/export/mets" \
  -H "Authorization: Bearer $TOKEN" \
  -o TEST_DOC_001_mets.xml

# View METS XML
cat TEST_DOC_001_mets.xml
```

The METS XML should contain:
- All 11 files in `<fileSec>`
- Proper file categorization in `USE` attributes
- Technical metadata (techMD) for each file
- Structural map with file references

## Testing Different Scenarios

### Scenario 1: Minimal Structure (Master + Metadata Only)

Create a minimal folder:
```bash
mkdir -p TEST_MIN/TIF.Master
mkdir -p TEST_MIN/Metadata
echo "Master file" > TEST_MIN/TIF.Master/TEST_MIN_0001.tif
echo "<metadata/>" > TEST_MIN/Metadata/metadata.xml
zip -r TEST_MIN.zip TEST_MIN/
```

Upload and verify only 2 files are categorized.

### Scenario 2: Alternative Folder Names

Test case-insensitive and alternative naming:
```bash
mkdir -p TEST_ALT/Master
mkdir -p TEST_ALT/Normalized
mkdir -p TEST_ALT/High
mkdir -p TEST_ALT/Low
# Add files...
```

System should recognize:
- `Master` → master category
- `Normalized` → normalized category
- `High` → export_high category
- `Low` → export_low category

### Scenario 3: Large Files (Multipart Upload)

For testing chunked uploads, create a large test file:
```bash
# Create a 100MB test file
dd if=/dev/zero of=TEST_LARGE/TIF.Master/large_scan.tif bs=1m count=100

# System will automatically use multipart upload for files > 64MB
```

## Troubleshooting

### Problem: Files Not Categorized Correctly

Check the confidence scores in the response. Low confidence (< 0.75) may indicate:
- Folder name doesn't match ECO-MiC patterns
- File extension doesn't match expected category
- Typo in folder name

### Problem: Upload Fails

Check backend logs:
```bash
docker compose logs -f backend
```

Common issues:
- ZIP file corrupted
- Invalid file extensions
- Database connection error

### Problem: METS Validation Fails

Use the validation endpoint:
```bash
curl -X POST http://localhost:8000/api/documents/validate-mets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\": $DOCUMENT_ID}"
```

Check validation errors and update metadata accordingly.

## Cleanup

Delete the test document:
```bash
curl -X DELETE "http://localhost:8000/api/documents/$DOCUMENT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## Additional Test Cases

### Test Case 1: RAW Files (DNG)

```bash
# Add DNG master files to test RAW support
mkdir -p TEST_RAW/RAW
# Add .dng files...
```

### Test Case 2: Mixed Extensions

```bash
# Test with various image formats
TIF.Master/scan_001.tif
TIF.Master/scan_002.dng
TIF.Master/scan_003.cr2
```

All should be categorized as "master" with high confidence.

### Test Case 3: Unicode Filenames

```bash
# Test with special characters and Unicode
mkdir -p "TEST_UNICODE/TIF.Master"
echo "test" > "TEST_UNICODE/TIF.Master/documento_àéìòù.tif"
```

System should handle Unicode filenames correctly.

---

Last updated: December 13, 2025
