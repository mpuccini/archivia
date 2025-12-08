# METS ECO-MiC Implementation Guide

This document describes the implementation of METS ECO-MiC 1.1 standard in Archivia, including XML generation and validation integration with the Cineca API.

---

## Overview

Archivia implements the **METS ECO-MiC 1.1** standard for Italian archival description (ICCU profile). This includes:

- METS XML generation from document metadata
- Validation against ECO-MiC 1.1 standard via Cineca API
- Complete metadata schema supporting all ECO-MiC fields
- Per-file technical metadata (MIX)
- Rights metadata (METSRIGHTS)

**Reference:** [ECO-MiC GitHub Repository](https://github.com/icdp-digital-library/profilo-mets-ecomic)

---

## Database Schema

### Document Model Extensions

Added ECO-MiC specific fields to `backend/app/models/document.py`:

```python
# ECO-MiC typeOfResource
type_of_resource = Column(String(100))  # e.g., "risorsa manoscritta"

# Corporate and personal names
producer_name = Column(String(255))
producer_type = Column(String(20))  # "corporate" or "personal"
producer_role = Column(String(100))
creator_name = Column(String(255))
creator_type = Column(String(20))
creator_role = Column(String(100))

# Rights information (METSRIGHTS)
license_url = Column(String(500))
rights_statement = Column(String(1000))
rights_category = Column(String(50))  # "COPYRIGHTED", "PUBLIC DOMAIN", etc.
rights_holder = Column(String(255))
rights_constraint = Column(String(100))  # e.g., "NoC-OKLR"

# Physical structure
physical_form = Column(String(100))  # e.g., "documento testuale"
extent_description = Column(String(255))  # e.g., "c. 14 nel fascicolo"

# METS header
record_status = Column(String(20), default="COMPLETE")  # "COMPLETE", "MINIMUM", "REFERENCED"
```

### DocumentFile Enhanced Metadata

Per-file technical metadata in `backend/app/models/document.py`:

```python
# MIX technical metadata
compression_scheme = Column(String(100))
color_space = Column(String(50))
sampling_frequency_unit = Column(String(20))
x_sampling_frequency = Column(Integer)
y_sampling_frequency = Column(Integer)
format_name = Column(String(100))
byte_order = Column(String(20))
orientation = Column(String(50))
icc_profile_name = Column(String(255))

# Scanner metadata
scanner_manufacturer = Column(String(255))
scanner_model_name = Column(String(255))
scanning_software_name = Column(String(255))
scanning_software_version = Column(String(255))
```

---

## METS XML Generation

### Generator Implementation

Located in `backend/app/utils/mets_generator_ecomic.py`:

```python
class METSEcoMicGenerator:
    """Generate METS XML compliant with ECO-MiC 1.1 standard"""
    
    def generate_mets_xml(self, document: Document) -> str:
        """Generate complete ECO-MiC 1.1 compliant METS XML"""
```

### METS Structure

Generated XML follows this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mets:mets xmlns:mets="http://www.loc.gov/METS/"
           xmlns:mods="http://www.loc.gov/mods/v3"
           xmlns:mix="http://www.loc.gov/mix/v20"
           xmlns:dct="http://purl.org/dc/terms/"
           xmlns:metsrights="http://cosimo.stanford.edu/sdr/metsrights/"
           xmlns:xlink="http://www.w3.org/1999/xlink"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="...">
  
  <!-- METS Header -->
  <mets:metsHdr CREATEDATE="..." LASTMODDATE="..." RECORDSTATUS="COMPLETE">
    <mets:agent ROLE="CREATOR" TYPE="ORGANIZATION">
      <mets:name>Archive Name</mets:name>
    </mets:agent>
  </mets:metsHdr>
  
  <!-- Descriptive Metadata (MODS) -->
  <mets:dmdSec ID="dmd01" STATUS="referenced">
    <mets:mdWrap MDTYPE="MODS">
      <mets:xmlData>
        <mods:mods>
          <!-- Identifiers, titles, descriptions, etc. -->
        </mods:mods>
      </mets:xmlData>
    </mets:mdWrap>
  </mets:dmdSec>
  
  <!-- Administrative Metadata (per file) -->
  <mets:amdSec>
    <!-- Technical MD (MIX) for each file -->
    <mets:techMD ID="techMD_001">...</mets:techMD>
    <!-- Rights MD (METSRIGHTS) -->
    <mets:rightsMD ID="rightsMD_001">...</mets:rightsMD>
  </mets:amdSec>
  
  <!-- File Section -->
  <mets:fileSec>
    <mets:fileGrp USE="MASTER">
      <mets:file ID="FILE_001" MIMETYPE="image/tiff" SIZE="..." CHECKSUM="..." CHECKSUMTYPE="MD5">
        <mets:FLocat LOCTYPE="URL" xlink:href="..."/>
      </mets:file>
    </mets:fileGrp>
  </mets:fileSec>
  
  <!-- Structural Map -->
  <mets:structMap TYPE="PHYSICAL">
    <mets:div TYPE="document" LABEL="...">
      <mets:fptr FILEID="FILE_001"/>
    </mets:div>
  </mets:structMap>
</mets:mets>
```

### Key ECO-MiC 1.1 Features

1. **No PROFILE attribute** - Unlike other METS profiles
2. **dmdSec with STATUS="referenced"** - ECO-MiC requirement
3. **Separate identifiers** for logical, conservative, and authority
4. **relationId** identifier with value "representation"
5. **structMap TYPE="PHYSICAL"** - Archival requirement
6. **Per-file techMD** in amdSec (not per-document)

---

## Validation Integration

### Cineca Validation API

**Endpoint:** `https://validavmetsecomic.prod.os01.ocp.cineca.it/api/v1/checkmetsecomic/files`

**Method:** POST (multipart/form-data)

**Field:** `files` (one or more XML files)

### Validation Service

Located in `backend/app/services/mets_validation.py`:

```python
class METSValidationService:
    def __init__(self):
        self.validation_api_url = "https://validavmetsecomic.prod.os01.ocp.cineca.it/api/v1/checkmetsecomic/files"
        self.timeout = 30.0
    
    async def validate_mets_xml(self, xml_content: str, filename: str) -> Dict[str, Any]:
        """Validate METS XML against ECO-MiC 1.1 standard"""
```

### Response Handling

**Success (HTTP 200):**
```json
{
  "esito": true,
  "response": {...}
}
```

**Validation Errors (HTTP 412 or 400):**
```json
{
  "esito": false,
  "filesResponse": [{
    "esito": false,
    "fileName": "document.xml",
    "listaMessaggi": [{
      "idErrore": 1,
      "tipologiaErrore": "ERROR",
      "descrizioneErrore": "Error description",
      "tagCoinvolto": "<mets:element>",
      "fileLocationDetail": "Line 6"
    }]
  }]
}
```

### API Routes

**Validate from form data:**
```
POST /api/documents/validate-mets-from-data
```

**Validate existing document:**
```
POST /api/documents/{document_id}/validate-mets
```

---

## Frontend Integration

### Validation in Upload Workflow

Location: `frontend/src/components/DocumentUploadForm.vue`

Validation triggered at Step 3 (Metadata Review) before final document creation:

```javascript
const validateMetadata = async () => {
  try {
    const response = await axios.post(
      `${API_URL}/api/documents/validate-mets-from-data`,
      formData
    );
    
    if (response.data.valid) {
      showSuccess("METS metadata is valid!");
    } else {
      showErrors(response.data.errors);
    }
  } catch (error) {
    handleValidationError(error);
  }
};
```

### Error Display

Validation errors displayed in user-friendly format:

- Error ID
- Error type
- Description (Italian from Cineca API)
- XML tag involved
- Line number in generated XML

---

## Testing

### Manual Testing with curl

Test Cineca API directly:

```bash
curl -X POST \
  -F "files=@document_mets.xml" \
  https://validavmetsecomic.prod.os01.ocp.cineca.it/api/v1/checkmetsecomic/files
```

### Example METS Files

Reference examples in: `/Users/marco/source/icdp-digital-library/profilo-mets-ecomic/ICDP_Profilo_METS_ECO-MiC_v.1.1_Apr2025/`

### Common Validation Errors

1. **Missing PROFILE attribute** - Some validators require it despite spec
2. **Duplicate namespace declarations** - ElementTree auto-adds namespaces
3. **Invalid identifier types** - Must use "logicalId", "conservativeId", "conservativeIdAuthority"
4. **Missing STATUS attribute** - dmdSec requires STATUS="referenced"

---

## Known Issues & Workarounds

### Issue: Cineca API Profile Requirement

**Problem:** Reference examples don't include PROFILE, but Cineca validator requires it

**Current Status:** Testing without PROFILE attribute (as per spec)

**Workaround if needed:** Add `PROFILE="http://www.iccu.sbn.it/metaAG1.pdf"` to root element

### Issue: Namespace Declaration Duplication

**Problem:** ElementTree auto-adds namespaces when using qualified names

**Solution:** Only use qualified attribute names for xsi:schemaLocation, let ElementTree handle xmlns declarations

---

## Security Considerations

### XML Generation Safety

- All user input sanitized via `html.escape()` before XML insertion
- Uses standard `xml.etree.ElementTree` for generation (safe for creating XML)
- No parsing of user-provided XML files (no XXE risk)

### Input Validation

All fields validated via Pydantic schemas before METS generation:

- String length constraints
- Pattern validation (e.g., alphanumeric identifiers)
- URL format validation
- Range validation for numeric fields

---

## References

- [ECO-MiC GitHub Repository](https://github.com/icdp-digital-library/profilo-mets-ecomic)
- [METS Standard](http://www.loc.gov/standards/mets/)
- [MODS Standard](http://www.loc.gov/standards/mods/)
- [MIX Standard](http://www.loc.gov/standards/mix/)
- [METSRIGHTS Schema](https://www.loc.gov/standards/rights/METSRights.xsd)

---

**Implementation Date:** 2025-12-05
**ECO-MiC Version:** 1.1
**Status:** Active
