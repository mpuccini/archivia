# Storia Implementazioni

Documentazione dettagliata di tutte le implementazioni e interventi tecnici.

---

## Dicembre 2024

### Ricerca Documenti - MongoDB Full-Text Search

**Data**: 15 Dicembre 2024  
**File Tecnico**: `DOCUMENT_SEARCH_IMPLEMENTATION.md`

#### Implementazione
- Sistema ricerca ibrido MongoDB + PostgreSQL
- Full-text search con stemming italiano
- Indici MongoDB con pesi per rilevanza (title:10, description:5, etc.)
- Endpoint API `GET /api/documents/search` con 7 parametri
- UI ricerca frontend con barra principale e filtri avanzati

#### File Modificati
- `backend/app/services/mongodb.py` - Indici e metodo search_documents()
- `backend/app/routes/documents.py` - Endpoint ricerca
- `frontend/src/components/DocumentsManager.vue` - UI ricerca

### Import Metadati da ZIP

**Data**: 15 Dicembre 2024  
**File Tecnico**: `METADATA_IMPORT_IMPLEMENTATION.md`

#### Implementazione
- Parser automatico metadati da cartella `metadata` in ZIP
- Supporto XML (METS ECO-MiC) e CSV
- Merge intelligente metadati estratti + parametri utente
- 40+ campi metadati supportati

#### File Creati
- `backend/app/utils/metadata_parser.py` - Parser XML/CSV

#### File Modificati
- `backend/app/services/document.py` - Integrazione estrazione metadati

### Migrazione Ant Design Vue

**Data**: Novembre-Dicembre 2024  
**File Tecnici**: `ANT_DESIGN_MIGRATION_*.md`

#### Implementazione
- Migrazione completa da Ant Design 3.x a 4.2.0
- Aggiornamento sintassi Vue 3 Composition API
- Nuovi componenti: DocumentsManager, DocumentDetailModal, DocumentUploadForm
- Sistema icone completo @ant-design/icons-vue

#### Componenti Migrati
- DocumentsManager
- DocumentDetailModal  
- DocumentUploadForm
- ImageUpload
- FileList
- Dashboard

---

## Novembre 2024

### Architettura Dual-Database

#### Implementazione
- Separazione PostgreSQL (piattaforma) + MongoDB (METS)
- Transaction Coordinator Pattern con 3-phase commit
- Motor (async MongoDB driver)
- Denormalizzazione logical_id per performance

#### Vantaggi
- Flessibilità schema METS
- Performance ottimizzate
- Supporto multi-versione standard

---

## Ottobre 2024

### METS ECO-MiC 1.1

#### Implementazione
- Generazione METS XML completa
- Supporto tutti namespace (mets, mods, mix, metsrights)
- Metadati archivistici, temporali, agenti, diritti
- Export con validazione

### Upload Cartelle ZIP

#### Implementazione
- Estrazione e categorizzazione automatica
- Supporto struttura ECO-MiC (master, normalized, etc.)
- FileCategorizer per riconoscimento cartelle
- Associazione file con metadati per-file

### Batch Operations

#### Implementazione
- Import batch da Excel
- Upload batch immagini con auto-matching
- Export CSV multipli documenti
- Eliminazione multipla

---

## Riferimenti

Per dettagli tecnici completi, consultare i file originali in `/docs/history/`:

- `DOCUMENT_SEARCH_IMPLEMENTATION.md`
- `METADATA_IMPORT_IMPLEMENTATION.md`
- `ANT_DESIGN_MIGRATION_COMPLETE.md`
- `ANT_DESIGN_MIGRATION_PLAN.md`
- `ANT_DESIGN_MIGRATION_STATUS.md`
- `DOCUMENTSMANAGER_MIGRATION_COMPLETE.md`
