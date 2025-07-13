# Metadata Import Feature - Documentation

## Overview
The document upload wizard now supports importing METS metadata from CSV or XML files to automatically pre-fill form fields.

## Supported File Formats

### CSV Files
CSV files should have a header row with field names that map to the document form fields.

**Supported CSV Field Names:**
- `logical_id`, `logicalid`, `id`, `identifier` → Logical ID
- `conservative_id`, `conservativeid`, `archive_id` → Conservative ID  
- `title`, `name` → Title
- `description`, `summary` → Description
- `archive_name`, `archivename`, `archive`, `institution` → Archive Name
- `archive_contact`, `contact`, `email` → Archive Contact
- `fund_name`, `fundname`, `fund`, `collection` → Fund Name
- `series_name`, `seriesname`, `series` → Series Name
- `folder_number`, `foldernumber`, `folder`, `unit`, `busta` → Folder Number
- `document_type`, `documenttype`, `type` → Document Type
- `total_pages`, `totalpages`, `pages`, `page_count` → Total Pages
- `date_from`, `datefrom`, `start_date`, `date_start`, `date` → Date From
- `date_to`, `dateto`, `end_date`, `date_end` → Date To
- `period`, `era`, `epoch` → Period
- `location`, `place`, `geographic` → Location
- `language`, `lang` → Language
- `subjects`, `keywords`, `subject`, `tags` → Subjects
- `conservative_id_authority`, `authority`, `id_authority` → ID Authority

**Example CSV:**
```csv
logical_id,title,description,document_type,archive_name,fund_name,date_from,location,language
ARCH-DOC-001,"Historic Cathedral Photo","Photo of Modena Cathedral",photograph,"State Archive of Modena","Photo Collection",1905-01-01,"Modena, Italy",it
```

### XML/METS Files
XML files support both Dublin Core and MODS/METS elements.

**Supported XML Elements:**
- `<identifier>`, `<mods:identifier>` → Logical ID
- `<identifier type="conservative">` → Conservative ID
- `<title>`, `<mods:title>` → Title
- `<description>`, `<abstract>`, `<mods:abstract>` → Description
- `<type>`, `<typeOfResource>` → Document Type
- `<namePart>` (corporate) → Archive Name
- `<extent>` → Total Pages (extracts numbers)
- `<dateCreated point="start">` → Date From
- `<dateCreated point="end">` → Date To
- `<placeTerm>` → Location
- `<languageTerm>` → Language (converts codes like 'lat' → 'la')
- `<topic>`, `<subject>` → Subjects
- `<relatedItem type="host">` → Fund Name
- `<relatedItem type="series">` → Series Name

**Example XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<mets:mets xmlns:mets="http://www.loc.gov/METS/" xmlns:mods="http://www.loc.gov/mods/v3">
  <mets:dmdSec>
    <mets:mdWrap MDTYPE="MODS">
      <mets:xmlData>
        <mods:mods>
          <mods:identifier type="logical">ARCH-DOC-002</mods:identifier>
          <mods:titleInfo>
            <mods:title>15th Century Manuscript</mods:title>
          </mods:titleInfo>
          <mods:abstract>Illuminated 15th century manuscript with religious texts</mods:abstract>
          <!-- Additional fields... -->
        </mods:mods>
      </mets:xmlData>
    </mets:mdWrap>
  </mets:dmdSec>
</mets:mets>
```

## How to Use

1. **Start Upload Wizard**: Click "Upload New Document" button
2. **Import Metadata (Optional)**: 
   - In the first step, look for the blue "Import METS Metadata" section
   - Click "Choose Metadata File"
   - Select your CSV or XML file
   - Wait for processing confirmation
3. **Review Pre-filled Fields**: Continue through the wizard steps to see which fields were automatically filled
4. **Edit as Needed**: Modify any auto-filled values as necessary
5. **Upload Files**: Select your document images as usual
6. **Complete Upload**: Follow remaining wizard steps normally

## Data Type Conversions

The system automatically converts certain values:
- **Document Types**: 'text' → 'manuscript', 'still image' → 'photograph'
- **Languages**: 'lat' → 'la', 'ita' → 'it', 'eng' → 'en', etc.
- **Page Numbers**: Extracts numeric values from text like "45 pages" → 45

## Error Handling

- **Invalid File Format**: Only CSV and XML files are accepted
- **Parsing Errors**: Clear error messages indicate what went wrong
- **No Matching Fields**: Warning if no recognizable fields are found
- **Partial Import**: Success message shows how many fields were imported

## Benefits

- **Time Saving**: Bulk import metadata instead of manual entry
- **Accuracy**: Reduces typing errors
- **Consistency**: Standardized field mapping
- **Flexibility**: Works with existing CSV exports and standard METS files
