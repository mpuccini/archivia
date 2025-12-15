# Implementazione Ricerca Documenti - MongoDB Full-Text Search

**Data Implementazione:** 15 Dicembre 2024
**Stato:** ✅ Backend Completato | ✅ Frontend Completato

---

## Riepilogo Implementazione

È stata implementata una funzionalità di **ricerca ibrida MongoDB + PostgreSQL** per i documenti archiviati nel sistema Archivia. La ricerca sfrutta il full-text search di MongoDB per cercare nei metadati METS ECO-MiC combinato con PostgreSQL per i dati della piattaforma.

### Architettura Scelta

**Strategia Ibrida:**
- **MongoDB**: Full-text search su metadati METS (titolo, descrizione, archivio, soggetti, agenti)
- **PostgreSQL**: Filtri esatti, paginazione, conteggio file, ownership
- **Coordinazione**: L'endpoint API combina risultati da entrambe le fonti

**Vantaggi:**
- ✅ Ricerca testuale veloce con stemming italiano
- ✅ Scoring automatico per rilevanza risultati
- ✅ Filtri avanzati su campi strutturati
- ✅ Isolamento utenti tramite `owner_id`
- ✅ Paginazione efficiente

---

## File Modificati

### Backend

#### 1. `/backend/app/services/mongodb.py`

**Modifiche agli Indici MongoDB:**

Aggiunto full-text search index con supporto italiano:

```python
# Full-text search index con pesi per rilevanza
await mets_collection.create_index(
    [
        ("title", "text"),
        ("description", "text"),
        ("conservative_id", "text"),
        ("archive.name", "text"),
        ("archive.fund_name", "text"),
        ("archive.series_name", "text"),
        ("subjects", "text"),
        ("location", "text"),
        ("agents.producer.name", "text"),
        ("agents.creator.name", "text")
    ],
    name="fulltext_search_idx",
    weights={
        "title": 10,                    # Priorità massima
        "conservative_id": 8,
        "description": 5,
        "archive.name": 3,
        "archive.fund_name": 3,
        "subjects": 3,
        "agents.creator.name": 2,
        "agents.producer.name": 2,
        "location": 1,
        "archive.series_name": 1
    },
    default_language="italian"        # Stemming italiano
)
```

**Indici aggiuntivi per filtri:**

```python
await mets_collection.create_index("temporal.date_from")
await mets_collection.create_index("temporal.date_to")
```

**Nuovo Metodo: `search_documents()`**

Metodo completo per ricerca con full-text, filtri e paginazione:

```python
async def search_documents(
    self,
    owner_id: int,
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    skip: int = 0,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search METS documents with full-text search and filters

    Parametri:
    - owner_id: ID utente (sicurezza)
    - query: Query full-text
    - filters: Dict con logical_id, archive, date_from, date_to, schema_version
    - skip, limit: Paginazione

    Ritorna:
    - items: Lista documenti trovati
    - total: Conteggio totale
    - skip, limit: Parametri paginazione
    """
```

**Funzionalità:**
- Full-text search con `$text` operator
- Scoring con `$meta: "textScore"`
- Filtri regex case-insensitive su logical_id e archive
- Filtri date range su campi temporali
- Aggregation pipeline con count e paginazione

---

#### 2. `/backend/app/routes/documents.py`

**Nuove Import:**

```python
from typing import Optional
from fastapi import Query
from datetime import date
from app.models.document import Document
from app.services.mongodb import mongodb_service
```

**Nuovo Endpoint: `GET /api/documents/search`**

```python
@router.get("/search")
async def search_documents(
    q: Optional[str] = Query(None, description="Full-text search query"),
    logical_id: Optional[str] = Query(None, description="Filter by logical ID"),
    archive: Optional[str] = Query(None, description="Filter by archive name"),
    date_from: Optional[date] = Query(None, description="Filter by start date"),
    date_to: Optional[date] = Query(None, description="Filter by end date"),
    schema_version: Optional[str] = Query(None, description="Filter by METS version"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

**Risposta JSON:**

```json
{
  "documents": [
    {
      "id": 1,
      "logical_id": "DOC001",
      "title": "Documento di esempio",
      "description": "Descrizione completa...",
      "conservative_id": "IT-MO0172-DOC001",
      "archive_name": "Archivio di Stato di Modena",
      "fund_name": "Fondo Estense",
      "schema_version": "1.1",
      "created_at": "2024-12-15T10:30:00",
      "updated_at": "2024-12-15T10:30:00",
      "file_count": 5,
      "search_score": 0.95    // Solo se query full-text
    }
  ],
  "total": 42,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

**Logica dell'Endpoint:**

1. **Raccolta Filtri**: Costruisce dizionario filtri da query parameters
2. **Ricerca MongoDB**: Esegue full-text search con filtri
3. **Fetch PostgreSQL**: Recupera dati piattaforma per documenti trovati
4. **Merge Risultati**: Combina metadati MongoDB con dati PostgreSQL
5. **Paginazione**: Calcola pagine totali e ritorna risultati

---

### Frontend

#### 3. `/frontend/src/components/DocumentDetailModal.vue`

**Metadati Tecnici Completi:**

Espansi i metadati visualizzati da 6 a 14 campi totali:

**Metadati Tecnici (MIX)** - 10 campi:
- ✅ Formato (`format_name`)
- ✅ Spazio Colore (`color_space`)
- ✅ Bit per Campione (`bits_per_sample`)
- ✅ Campioni per Pixel (`samples_per_pixel`)
- ✅ Compressione (`compression_scheme`)
- ✅ DPI con unità (`x_sampling_frequency` + `y_sampling_frequency` + `sampling_frequency_unit`)
- ✅ Byte Order (`byte_order`)
- ✅ Orientamento (`orientation`)
- ✅ Profilo ICC (`icc_profile_name`)
- ✅ Data Creazione (`date_time_created`)

**Info Scanner** - 4 campi (nomi corretti):
- ✅ Produttore (`scanner_manufacturer`) - corretto da `camera_manufacturer`
- ✅ Modello (`scanner_model_name`) - corretto da `camera_model`
- ✅ Software (`scanning_software_name`) - corretto da `scanner_software`
- ✅ Versione Software (`scanning_software_version`) - NUOVO

**Fix Preview File Testuali:**

Modificata funzione `isImageFile()` per escludere file testuali:

```javascript
const isImageFile = (file) => {
  // Escludi file testuali anche se hanno content_type image/*
  const textExtensions = ['.xml', '.csv', '.txt', '.log', '.json', '.html', '.css', '.js']
  const hasTextExtension = textExtensions.some(ext => file.filename?.toLowerCase().endsWith(ext))

  if (hasTextExtension) {
    return false
  }

  return file.content_type?.startsWith('image/')
}
```

**File Esclusi da Preview:**
- `.xml` - Metadati METS
- `.csv` - Export dati
- `.txt`, `.log` - File di testo
- `.json`, `.html`, `.css`, `.js` - File web

#### 4. `/frontend/src/components/DocumentsManager.vue`

**Implementazione UI di Ricerca:**

Aggiunta interfaccia completa di ricerca documenti con i seguenti componenti:

**1. Barra di Ricerca Principale**
```vue
<a-input-search
  v-model:value="searchQuery"
  placeholder="Cerca documenti per titolo, descrizione, archivio, soggetti..."
  size="large"
  :loading="searching"
  @search="handleSearch"
>
  <template #prefix>
    <SearchOutlined />
  </template>
</a-input-search>
```

**2. Pannello Filtri Avanzati**
- Collapse panel espandibile/collassabile
- 5 campi filtro:
  - **ID Logico**: Input text per ricerca parziale
  - **Archivio**: Input text per nome archivio
  - **Versione METS**: Select con opzioni 1.1, 1.2
  - **Data Da**: DatePicker per data inizio range
  - **Data A**: DatePicker per data fine range
- Pulsanti "Cerca" e "Cancella Filtri"

**3. Visualizzazione Risultati**
- Badge con conteggio: "X risultati trovati"
- Pulsante "Cancella Ricerca" per tornare alla lista completa
- Integrazione con lista documenti esistente
- Paginazione automatica

**4. State Management**
```javascript
// Search state
const searchQuery = ref('')
const searching = ref(false)
const showFilters = ref(false)
const isSearchActive = ref(false)
const filters = reactive({
  logical_id: '',
  archive: '',
  date_from: null,
  date_to: null,
  schema_version: ''
})
```

**5. Funzioni Principali**
- `handleSearch()`: Esegue chiamata API con query e filtri
- `clearSearch()`: Reset ricerca e ricarica documenti
- `clearFilters()`: Pulisce tutti i filtri
- `onSearchChange()`: Auto-clear quando input vuoto
- `hasActiveFilters`: Computed per verificare filtri attivi

**6. Integrazione API**
```javascript
const response = await axios.get(
  `${import.meta.env.VITE_API_URL}/api/documents/search`,
  {
    params: {
      page, size, q, logical_id, archive,
      date_from, date_to, schema_version
    },
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  }
)
```

---

## Configurazione MongoDB

### Docker Compose

MongoDB già configurato in `docker-compose.yml`:

```yaml
mongodb:
  image: mongo:7.0
  container_name: archivia-mongodb
  environment:
    MONGO_INITDB_ROOT_USERNAME: archivia
    MONGO_INITDB_ROOT_PASSWORD: archivia123
    MONGO_INITDB_DATABASE: archivia_mets
  volumes:
    - mongodb_data:/data/db
    - mongodb_config:/data/configdb
  ports:
    - "27017:27017"
  healthcheck:
    test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
```

### Backend Config

URL MongoDB in `/backend/app/core/config.py`:

```python
MONGODB_URL: str = "mongodb://archivia:archivia123@mongodb:27017/archivia_mets?authSource=admin"
```

### Inizializzazione

MongoDB inizializzato in `/backend/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    # ...
    await mongodb_service.connect_async()
    logger.info("MongoDB connection established successfully")

@app.on_event("shutdown")
async def shutdown_event():
    await mongodb_service.close_async()
```

**Log di Startup Verificato:**

```
INFO: MongoDB async connection established
INFO: MongoDB indexes created successfully
INFO: MongoDB connection established successfully
INFO: Application startup complete
```

---

## Esempi di Utilizzo API

### Ricerca Full-Text

```bash
GET /api/documents/search?q=archivio+modena&page=1&size=20
Authorization: Bearer <token>
```

Cerca "archivio modena" in tutti i campi testuali indicizzati.

### Ricerca con Filtri

```bash
GET /api/documents/search?archive=Modena&date_from=1850-01-01&date_to=1900-12-31&schema_version=1.1
Authorization: Bearer <token>
```

Filtra per archivio, range di date e versione METS.

### Ricerca Combinata

```bash
GET /api/documents/search?q=estense&archive=Stato&page=2&size=10
Authorization: Bearer <token>
```

Full-text "estense" + filtro archivio "Stato", pagina 2, 10 risultati.

### Solo Filtri (senza full-text)

```bash
GET /api/documents/search?logical_id=DOC&schema_version=1.2
Authorization: Bearer <token>
```

Trova documenti con logical_id contenente "DOC" e versione 1.2.

---

## Stato Implementazione

### ✅ Completato (Backend)

1. **MongoDB Full-Text Index**
   - Indice con 10 campi testuali
   - Pesi per rilevanza
   - Supporto lingua italiana
   - Indici per filtri date

2. **Servizio MongoDB**
   - Metodo `search_documents()` completo
   - Aggregation pipeline con scoring
   - Gestione filtri multipli
   - Paginazione efficiente

3. **Endpoint API**
   - `GET /api/documents/search`
   - 7 parametri query
   - Documentazione OpenAPI completa
   - Merge MongoDB + PostgreSQL
   - Response paginato

4. **Fix Metadati Frontend**
   - 14 campi metadati tecnici visualizzati
   - Nomi campi corretti
   - Preview file testuali disabilitata

5. **Infrastruttura**
   - MongoDB configurato e attivo
   - Indici creati automaticamente
   - Health check funzionante

### ✅ Completato (Frontend)

1. **Barra di Ricerca**
   - ✅ Input search in DocumentsManager header con icona SearchOutlined
   - ✅ Clear button integrato
   - ✅ Enter per avviare la ricerca

2. **Filtri Avanzati**
   - ✅ Collapse panel con form filtri (Ant Design Collapse)
   - ✅ Date picker per range temporale (date_from, date_to)
   - ✅ Select per versione METS (1.1, 1.2)
   - ✅ Input per archivio e logical_id

3. **Visualizzazione Risultati**
   - ✅ Lista risultati con contatore
   - ✅ Badge informativi "X risultati trovati"
   - ✅ Integrazione con lista documenti esistente
   - ✅ Search score incluso in response

4. **UX Enhancements**
   - ✅ Loading spinner durante ricerca
   - ✅ Pulsante "Cancella Ricerca" per tornare alla lista completa
   - ✅ Paginazione integrata (riutilizza componente esistente)
   - ✅ Sorting automatico per rilevanza (quando query full-text) o data

---

## Testing

### Test Manuale Consigliato

**Frontend URL**: http://localhost:3000

**Procedura di Test**:

1. **Prerequisiti**
   - Login nell'applicazione
   - Avere almeno alcuni documenti caricati nel sistema
   - Frontend e backend attivi

2. **Test Ricerca Semplice**
   - Inserire un termine nella barra di ricerca (es. "archivio", "modena")
   - Premere Enter o cliccare sul pulsante "Cerca"
   - Verificare che appaia il badge "X risultati trovati"
   - Verificare che i risultati siano ordinati per rilevanza

3. **Test Filtri Avanzati**
   - Cliccare sull'icona filtro per espandere il pannello
   - Inserire filtri:
     - ID Logico (es. "DOC")
     - Archivio (es. "Modena")
     - Selezionare versione METS (1.1 o 1.2)
     - Impostare range di date
   - Cliccare "Cerca"
   - Verificare che i risultati rispettino i filtri

4. **Test Ricerca Combinata**
   - Inserire query full-text + filtri
   - Verificare risultati corretti

5. **Test Cancella Ricerca**
   - Dopo una ricerca, cliccare "Cancella Ricerca"
   - Verificare che torni alla lista completa dei documenti

6. **Test Paginazione**
   - Con molti risultati, verificare che la paginazione funzioni
   - Cambiare pagina e verificare aggiornamento risultati

7. **Test API via Swagger UI** (opzionale)
   - Aprire http://localhost:8000/docs
   - Login per ottenere token
   - Testare endpoint `/api/documents/search`
   - Verificare response JSON con campi: documents, total, page, size, pages

---

## Note Tecniche

### Lingua Italiana

MongoDB full-text search usa stemming italiano:
- "archivio" trova anche "archivi", "archivistica"
- "documento" trova "documenti", "documentazione"
- Stop words italiane rimosse ("il", "la", "di", "da", ...)

### Scoring

Score calcolato da MongoDB basato su:
- Peso del campo (title=10 > description=5 > location=1)
- Frequenza termine nel documento
- Rarità termine nel corpus

### Sicurezza

- Filtro automatico `owner_id` impedisce accesso cross-user
- Token JWT obbligatorio
- Validazione Pydantic su tutti i parametri

### Scalabilità

- MongoDB index supporta milioni di documenti
- Aggregation pipeline ottimizzata
- Paginazione limita risultati (max 100/page)

---

## Prossimi Passi

### Possibili Miglioramenti Futuri

1. **Ottimizzazioni** (Priorità Media)
   - Cache risultati ricerche frequenti (Redis)
   - Suggerimenti autocomplete basati su query precedenti
   - Faceted search (aggregazioni per archivio, anno, tipo documento)
   - Highlighting dei termini cercati nei risultati
   - Export risultati ricerca in CSV/Excel

2. **Analytics** (Priorità Bassa)
   - Log query ricerche per analisi
   - Statistiche termini più cercati
   - Dashboard utilizzo ricerca
   - Report periodici sull'utilizzo

3. **UX Enhancements**
   - Ricerca vocale (Web Speech API)
   - Salvataggio ricerche preferite
   - Condivisione link ricerca con filtri
   - Ricerca avanzata con operatori booleani (AND, OR, NOT)

---

## Risorse

- **Documentazione MongoDB Text Search**: https://docs.mongodb.com/manual/text-search/
- **FastAPI Query Parameters**: https://fastapi.tiangolo.com/tutorial/query-params/
- **METS ECO-MiC 1.1**: https://github.com/icdp-digital-library/profilo-mets-ecomic
- **Ant Design Vue Components**: https://antdv.com/components/overview

---

## Conclusione

**Implementazione completata con successo!** ✅

La funzionalità di ricerca ibrida MongoDB + PostgreSQL è stata implementata completamente sia nel **backend** che nel **frontend**. Il sistema è ora in grado di:

- Eseguire ricerche full-text su metadati METS con stemming italiano
- Filtrare documenti per ID logico, archivio, versione METS e range di date
- Ordinare risultati per rilevanza o data di creazione
- Gestire paginazione efficiente
- Garantire isolamento utenti tramite `owner_id`

**Sistema pronto per il testing!**

Accedi a http://localhost:3000 per testare la funzionalità di ricerca.
