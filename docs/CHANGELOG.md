# Changelog

Cronologia completa degli interventi e delle modifiche apportate al progetto Archivia.

---

## [2.0.0] - 2025-12-15

### Aggiunte

#### Ricerca Documenti (MongoDB Full-Text Search)
- Implementato sistema di ricerca ibrido MongoDB + PostgreSQL
- Full-text search con stemming italiano su metadati METS
- Indici MongoDB ottimizzati con pesi per rilevanza
- Endpoint API `GET /api/documents/search` con 7 parametri query
- UI di ricerca nel frontend con barra principale e filtri avanzati
- Filtri: ID logico, archivio, versione METS, range date
- Risultati ordinati per rilevanza o data
- Paginazione integrata

#### Import Metadati da ZIP
- Parser automatico metadati da cartella `metadata` in archivi ZIP
- Supporto formato XML (METS ECO-MiC completo)
- Supporto formato CSV (due varianti)
- Merge intelligente: metadati estratti + parametri utente
- Gestione automatica namespace XML (mets, mods, dc, dct, xlink)
- Supporto 40+ campi metadati standard
- Log dettagliato estrazione metadati

#### Migrazione Ant Design Vue
- Migrazione completa componenti frontend da Ant Design 3.x a 4.2.0
- Aggiornamento sintassi Vue 3 Composition API
- Nuovi componenti: DocumentsManager, DocumentDetailModal, DocumentUploadForm
- Wizard multi-step per creazione documenti
- Modal dettaglio documento con visualizzazione file e metadati
- Sistema icone completo con @ant-design/icons-vue
- Gestione stato reattivo con ref/reactive
- Fix deprecation warnings e compatibility issues

### Migliorate

#### Metadati Tecnici
- Espansi metadati tecnici file da 6 a 14 campi
- Correzione nomi campi scanner (scanner_* invece di camera_*)
- Aggiunto campo `scanning_software_version`
- Fix preview file testuali (XML, CSV, TXT, LOG esclusi da preview immagini)

#### Upload DNG
- Generazione automatica thumbnail per file DNG RAW
- Badge indicatore "DNG RAW" nell'interfaccia
- Estrazione JPEG preview embedded o processing RAW data
- Dimensione thumbnail: 1200x1200px max, 85% quality

#### UI/UX
- Icone aggiunte a wizard steps, tabs, pulsanti, batch operations
- Spinner di caricamento per operazioni asincrone
- Result components per success/error states
- Blur sfondo per modali
- Auto-refresh liste dopo operazioni
- Guide utente aggiornata con sezione ricerca

### Fix

- Risolto problema versione METS (corretto da 1.2 a 1.1 ovunque)
- Rimosso pulsante validazione METS (feature disabilitata)
- Fix metadati tecnici non visualizzati correttamente
- Fix preview file testuali mostrati come immagini
- Fix folder upload list refresh
- Correzione Tailwind CSS warnings durante build

---

## [1.2.0] - 2025-11 (Data Approssimativa)

### Aggiunte

#### Architettura Dual-Database
- Implementata architettura ibrida PostgreSQL + MongoDB
- PostgreSQL: metadati piattaforma (users, files, associations)
- MongoDB: metadati METS ECO-MiC (flessibili, versionati)
- Transaction Coordinator Pattern con 3-phase commit
- Rollback automatico in caso di fallimento
- Motor (async MongoDB driver) per performance ottimali
- Denormalizzazione `logical_id` per query veloci

#### METS ECO-MiC 1.1
- Generazione completa METS XML conforme ECO-MiC 1.1
- Supporto tutti i namespace METS standard
- Metadati archivistici completi (archive, fund, series, folder)
- Metadati temporali con range date ISO 8601
- Metadati agenti (producer, creator) con ruoli
- Metadati diritti (metsrights con categorie e vincoli)
- Metadati tecnici MIX per-file
- Export METS con validazione

#### Upload Cartelle ZIP
- Upload archivi ZIP con struttura ECO-MiC
- Estrazione automatica e categorizzazione file
- Supporto cartelle: master, normalized, export_high, etc.
- FileCategorizer per riconoscimento automatico struttura
- Associazione file a documento con metadati per-file

#### Batch Operations
- Import batch documenti da Excel
- Upload batch immagini con matching automatico per logical_id
- Creazione automatica documenti per immagini non matchate
- Export metadati CSV multipli documenti
- Eliminazione multipla documenti selezionati

### Migliorate

#### File Management
- Supporto file DNG (Adobe Digital Negative) fino a 80GB
- Upload chunked per file di grandi dimensioni (chunk 64MB)
- Calcolo MD5 checksum per integrità file
- Estrazione metadati tecnici immagini (MIX)
- Storage MinIO con organizzazione per documento
- Streaming ottimizzato per download file

#### Security
- Validazione file type con magic number verification
- Sanitizzazione nomi file e percorsi
- Isolamento utenti con owner_id
- JWT token-based authentication
- CORS configuration
- Input validation con Pydantic

---

## [1.1.0] - 2025-10 (Data Approssimativa)

### Aggiunte

#### Sistema Base
- Backend FastAPI con SQLAlchemy ORM
- Frontend Vue 3 + Vite + Tailwind CSS
- PostgreSQL database
- MinIO object storage
- Docker Compose deployment

#### CRUD Documenti
- Creazione documenti con metadati completi
- Modifica metadati documento
- Eliminazione documenti
- Visualizzazione lista documenti
- Dettaglio documento con file associati

#### File Management
- Upload singolo file immagine
- Download file
- Associazione file-documento (many-to-many)
- Metadati per-file (sequence, checksum, dimensions)

#### Authentication
- Registrazione utenti
- Login con JWT token
- User sessions
- Protected routes

---

## [1.0.0] - 2025-09 (Data Approssimativa)

### Versione Iniziale

#### Setup Progetto
- Inizializzazione repository
- Configurazione ambiente sviluppo
- Docker containerization
- Database schema design
- API structure definition

---

## Categorie di Cambiamenti

Le versioni seguono [Semantic Versioning](https://semver.org/):

- **MAJOR**: Cambiamenti incompatibili con versioni precedenti
- **MINOR**: Nuove funzionalità backward-compatible
- **PATCH**: Bug fixes backward-compatible

### Tag Usati

- **Aggiunte**: Nuove funzionalità
- **Migliorate**: Miglioramenti a funzionalità esistenti
- **Fix**: Bug fixes
- **Deprecate**: Funzionalità deprecate (da rimuovere in futuro)
- **Rimosse**: Funzionalità rimosse
- **Sicurezza**: Vulnerabilità risolte
- **Performance**: Ottimizzazioni performance

---

## Date Importanti

- **15 Dicembre 2025**: Ricerca MongoDB, Import Metadati, Migrazione Ant Design
- **Novembre 2025**: Architettura dual-database, METS ECO-MiC 1.1
- **Ottobre 2025**: Sistema base, CRUD, File management
- **Settembre 2025**: Inizializzazione progetto

---

*Per dettagli tecnici specifici, consultare la documentazione in `/docs/architecture/` e `/docs/api/`.*
