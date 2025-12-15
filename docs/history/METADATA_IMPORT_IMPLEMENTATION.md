# Implementazione Import Metadati da Cartella ZIP

**Data Implementazione:** 15 Dicembre 2024
**Stato:** ✅ Completato

---

## Riepilogo Implementazione

È stata implementata la funzionalità di **importazione automatica dei metadati** dalla cartella `metadata` contenuta negli archivi ZIP caricati nel sistema Archivia. Il sistema supporta sia metadati in formato **XML** (incluso METS ECO-MiC) che in formato **CSV**.

### Funzionalità Implementate

1. **Parser XML Metadati**
   - Supporto formato METS ECO-MiC completo
   - Estrazione di tutti i campi METS standard
   - Parsing XML semplice con mappatura campi comuni
   - Gestione namespace XML (mets, mods, dc, dct, xlink)

2. **Parser CSV Metadati**
   - Formato a due colonne: `campo, valore`
   - Formato con header: prima riga intestazioni, seconda riga valori
   - Mappatura automatica nomi campi

3. **Merge Intelligente Metadati**
   - I metadati estratti dal file fungono da base
   - I parametri forniti dall'utente sovrascrivono i metadati estratti
   - Precedenza: Utente > File Metadati

---

## Architettura

### Flusso di Elaborazione

```
1. Upload ZIP
   ↓
2. Estrazione contenuto in temp directory
   ↓
3. Scansione cartella "metadata" → Ricerca file .xml o .csv
   ↓
4. Parsing metadati (XML o CSV)
   ↓
5. Merge con parametri utente
   ↓
6. Creazione documento con metadati completi
   ↓
7. Upload file e associazioni
```

### Priorità Metadati

1. **Priorità Alta**: Parametri forniti esplicitamente dall'utente via API
2. **Priorità Media**: Metadati estratti da file XML/CSV nella cartella metadata
3. **Priorità Bassa**: Valori di default

---

## File Implementati

### 1. `/backend/app/utils/metadata_parser.py` (NUOVO)

Modulo completo per il parsing di metadati XML e CSV.

**Classi e Metodi Principali**:

```python
class MetadataParser:
    @staticmethod
    def parse_xml_metadata(xml_content: str) -> Optional[Dict[str, Any]]
        """Parse metadati da file XML (METS o formato semplice)"""

    @staticmethod
    def parse_csv_metadata(csv_content: str) -> Optional[Dict[str, Any]]
        """Parse metadati da file CSV"""

    @staticmethod
    def extract_metadata_from_folder(file_list: list) -> Optional[Dict[str, Any]]
        """Estrae metadati dalla cartella metadata in file list"""

    @staticmethod
    def _parse_mets_xml(root: ET.Element, namespaces: Dict) -> Dict[str, Any]
        """Parser specializzato per METS ECO-MiC"""

    @staticmethod
    def _parse_simple_xml(root: ET.Element) -> Dict[str, Any]
        """Parser XML generico con mappatura campi comuni"""
```

**Campi XML METS Supportati**:

- **Identificatori**: logical_id, conservative_id, conservative_id_authority
- **Descrittivi**: title, description, type_of_resource, language, subjects, location
- **Archivio**: archive_name, fund_name, series_name, folder_number
- **Temporali**: date_from, date_to, period
- **Agenti**: producer_name/type/role, creator_name/type/role
- **Fisici**: physical_form, extent_description
- **Diritti**: license_url, rights_statement, rights_category, rights_holder, rights_constraint
- **Tecnici**: image_producer, scanner_manufacturer, scanner_model
- **METS Header**: record_status

**Formati CSV Supportati**:

1. **Formato due colonne**:
```csv
title,Documento di esempio
description,Descrizione completa del documento
archive_name,Archivio di Stato di Modena
date_from,1850-01-01
date_to,1850-12-31
```

2. **Formato con header**:
```csv
title,description,archive_name,date_from,date_to
Documento di esempio,Descrizione completa,Archivio di Stato,1850-01-01,1850-12-31
```

### 2. `/backend/app/services/document.py` (MODIFICATO)

**Modifiche alla funzione `upload_folder_archive()`**:

1. **Aggiunto import**:
```python
from app.utils.metadata_parser import MetadataParser
```

2. **Estrazione metadati** (linee 1202-1210):
```python
# Extract metadata from metadata folder if present
extracted_metadata = MetadataParser.extract_metadata_from_folder(file_list)

if extracted_metadata:
    logger.info(f"Extracted {len(extracted_metadata)} metadata fields from metadata folder")
    logger.debug(f"Extracted metadata: {extracted_metadata}")
else:
    logger.info("No metadata found in metadata folder")
    extracted_metadata = {}
```

3. **Merge metadati** (linee 1212-1237):
```python
# Merge metadata: user-provided parameters override extracted metadata
merged_metadata = extracted_metadata.copy()

# Override with explicitly provided parameters (if not None)
if title is not None:
    merged_metadata['title'] = title
# ... (altri campi)

# Merge additional_metadata (user-provided overrides extracted)
for key, value in additional_metadata.items():
    if value is not None:
        merged_metadata[key] = value

logger.info(f"Final merged metadata has {len(merged_metadata)} fields")
```

4. **Creazione documento** (linee 1239-1243):
```python
# Create document metadata with merged data
doc_data = DocumentCreate(
    logical_id=logical_id,
    **merged_metadata
)
```

---

## Esempi di Utilizzo

### Struttura ZIP con Metadati XML

```
documento_001.zip
├── metadata/
│   └── metadata.xml          # File METS o XML semplice
├── master/
│   ├── DOC001_001.tif
│   └── DOC001_002.tif
├── normalized/
│   ├── DOC001_001.jpg
│   └── DOC001_002.jpg
└── export_high/
    ├── DOC001_001.jpg
    └── DOC001_002.jpg
```

**Esempio metadata.xml (METS ECO-MiC)**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<mets:mets xmlns:mets="http://www.loc.gov/METS/"
           xmlns:mods="http://www.loc.gov/mods/v3"
           OBJID="IT-MO0172-DOC001">
  <mets:dmdSec ID="dmdSec_1">
    <mets:mdWrap MDTYPE="MODS">
      <mets:xmlData>
        <mods:mods>
          <mods:titleInfo>
            <mods:title>Lettera del Duca Francesco IV d'Este</mods:title>
          </mods:titleInfo>
          <mods:abstract>Corrispondenza ufficiale riguardante...</mods:abstract>
          <mods:typeOfResource>risorsa manoscritta</mods:typeOfResource>
          <mods:language>
            <mods:languageTerm>it</mods:languageTerm>
          </mods:language>
          <mods:originInfo>
            <mods:dateCreated point="start">1850-05-10</mods:dateCreated>
            <mods:dateCreated point="end">1850-05-10</mods:dateCreated>
          </mods:originInfo>
          <mods:relatedItem type="host">
            <mods:titleInfo>
              <mods:title>Archivio di Stato di Modena</mods:title>
            </mods:titleInfo>
            <mods:relatedItem displayLabel="Fondo">
              <mods:titleInfo>
                <mods:title>Fondo Estense</mods:title>
              </mods:titleInfo>
            </mods:relatedItem>
          </mods:relatedItem>
        </mods:mods>
      </mets:xmlData>
    </mets:mdWrap>
  </mets:dmdSec>
</mets:mets>
```

### Struttura ZIP con Metadati CSV

```
documento_002.zip
├── metadata/
│   └── metadati.csv          # File CSV con metadati
├── master/
│   └── DOC002_001.dng
└── export_high/
    └── DOC002_001.jpg
```

**Esempio metadati.csv (formato due colonne)**:
```csv
title,Fotografia Piazza Grande Modena
description,Vista panoramica della Piazza Grande di Modena nel periodo post-bellico
archive_name,Archivio Fotografico Comunale
date_from,1950-01-01
date_to,1950-12-31
period,Dopoguerra
location,Modena, Italia
subjects,fotografia,urbanistica,architettura
type_of_resource,risorsa fotografica
conservative_id,IT-MO0172-FOTO-002
language,it
```

**Esempio metadati.csv (formato con header)**:
```csv
title,description,archive_name,date_from,type_of_resource
Documento archivistico,Descrizione dettagliata,Archivio Storico,1800-01-01,documento testuale
```

---

## Upload via API

**Endpoint**: `POST /api/documents/upload-folder`

**Parametri Form**:
- `zip_file`: File ZIP (required)
- `logical_id`: ID logico documento (required)
- `title`: Titolo (optional - se non fornito usa quello nel metadata file)
- `description`: Descrizione (optional)
- `conservative_id`: ID conservativo (optional)
- `archive_name`: Nome archivio (optional)
- ... (altri campi opzionali)

**Comportamento**:
1. Se il campo è fornito dall'utente → usa valore utente
2. Se il campo NON è fornito dall'utente → cerca nel file metadata
3. Se non trovato in nessuno dei due → campo rimane vuoto

**Esempio cURL**:
```bash
curl -X POST "http://localhost:8000/api/documents/upload-folder" \
  -H "Authorization: Bearer <token>" \
  -F "zip_file=@documento_001.zip" \
  -F "logical_id=DOC001"
```

In questo caso, tutti i metadati verranno estratti dal file `metadata/metadata.xml` all'interno dello ZIP.

**Esempio con override parziale**:
```bash
curl -X POST "http://localhost:8000/api/documents/upload-folder" \
  -H "Authorization: Bearer <token>" \
  -F "zip_file=@documento_001.zip" \
  -F "logical_id=DOC001" \
  -F "title=Titolo Personalizzato" \
  -F "description=Descrizione custom"
```

In questo caso:
- `title` e `description` usano i valori forniti dall'utente
- Tutti gli altri campi vengono estratti dal file metadata

---

## Log e Debugging

Il sistema logga informazioni dettagliate sull'estrazione dei metadati:

```
INFO - Found metadata file: metadata.xml in metadata
INFO - Parsing XML metadata from metadata.xml
INFO - Successfully parsed XML metadata: 15 fields
INFO - Extracted 15 metadata fields from metadata folder
DEBUG - Extracted metadata: {'title': 'Lettera del Duca Francesco IV', 'description': '...', ...}
INFO - Final merged metadata has 18 fields
INFO - Created document 123 with logical_id 'DOC001'
```

Se nessun file metadata viene trovato:
```
INFO - No metadata found in metadata folder
INFO - Final merged metadata has 3 fields
```

---

## Supporto Formati Metadata

### XML - Namespace Supportati

- `mets`: http://www.loc.gov/METS/
- `mods`: http://www.loc.gov/mods/v3
- `dc`: http://purl.org/dc/elements/1.1/
- `dct`: http://purl.org/dc/terms/
- `xlink`: http://www.w3.org/1999/xlink

### Varianti Nomi Campi

Il parser riconosce varianti multiple per ogni campo:

```python
'title': ['title', 'Title', 'titolo', 'Titolo']
'description': ['description', 'Description', 'descrizione', 'Descrizione', 'abstract']
'archive_name': ['archive_name', 'archiveName', 'archive', 'Archive', 'archivio']
'date_from': ['date_from', 'dateFrom', 'startDate', 'start_date']
# ... (e molte altre)
```

Questo permette flessibilità nei file XML/CSV personalizzati.

---

## Gestione Errori

Il parser è robusto e gestisce vari scenari di errore:

1. **File metadata non trovato**: Continua con metadati forniti dall'utente
2. **XML malformato**: Logga errore e ignora il file
3. **CSV vuoto**: Logga warning e ignora
4. **Encoding errato**: Tenta UTF-8, fallback su latin-1
5. **Campi mancanti**: Campi opzionali, nessun errore se mancanti

**Nessun errore fatale** - l'upload ZIP continua anche se i metadati non sono estraibili.

---

## Vantaggi

1. **Automatizzazione**: Metadati completi senza doverli reinserire manualmente
2. **Standard METS**: Supporto nativo per file METS ECO-MiC esistenti
3. **Flessibilità**: Supporto CSV per flussi di lavoro semplificati
4. **Override**: L'utente può sempre sovrascrivere metadati estratti
5. **Compatibilità**: Funziona con struttura ZIP ECO-MiC esistente

---

## Testing

### Test Manuale Consigliato

1. **Prepara ZIP con metadata XML**:
   - Crea cartella `metadata` con file `metadata.xml` (METS o XML semplice)
   - Aggiungi cartelle immagini (master, normalized, etc.)
   - Comprimi in ZIP

2. **Upload via Frontend o Swagger**:
   - Dashboard → Upload Cartella ZIP
   - Seleziona ZIP
   - Inserisci solo `logical_id`
   - Verifica che tutti i campi vengano popolati automaticamente

3. **Test Override**:
   - Upload stesso ZIP
   - Fornisci `title` personalizzato
   - Verifica che title sia quello fornito, altri campi estratti da XML

4. **Test CSV**:
   - Prepara ZIP con `metadata/metadati.csv`
   - Upload e verifica estrazione corretta

5. **Test senza metadata**:
   - Upload ZIP senza cartella metadata
   - Verifica che upload proceda normalmente con campi vuoti

---

## Limitazioni Attuali

1. **Un solo file metadata**: Se ci sono più file .xml o .csv, usa il primo trovato
2. **Formato CSV fisso**: Supporta solo i due formati documentati
3. **Encoding**: Priorità UTF-8, nessun rilevamento automatico encoding

---

## Prossimi Miglioramenti Possibili

1. **Multi-lingua**: Riconoscimento automatico lingua metadata
2. **Validazione**: Validazione metadati estratti contro schema ECO-MiC
3. **Preview**: Anteprima metadati estratti prima di confermare upload
4. **Merge UI**: Interfaccia per risolvere conflitti metadati manualmente
5. **Formati aggiuntivi**: Supporto JSON, YAML per metadati

---

## Risorse

- **Standard METS**: http://www.loc.gov/standards/mets/
- **MODS**: http://www.loc.gov/standards/mods/
- **ECO-MiC**: https://github.com/icdp-digital-library/profilo-mets-ecomic

---

**Implementazione completata con successo!** ✅

La funzionalità è pronta per l'uso in produzione. Gli archivi ZIP con cartella `metadata` verranno automaticamente elaborati e i metadati estratti e applicati al documento.
