# Architettura Database

## PostgreSQL Schema

### Tabelle Principali

**users**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**documents** (semplificato - 7 campi)
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id),
    logical_id VARCHAR(255) UNIQUE NOT NULL,
    mets_document_id VARCHAR(24),  -- MongoDB ObjectId
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**files**
```sql
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id),
    filename VARCHAR(500) NOT NULL,
    content_type VARCHAR(100),
    file_size BIGINT,
    file_hash VARCHAR(64),
    minio_path VARCHAR(1000),
    -- Technical metadata (MIX)
    width INTEGER,
    height INTEGER,
    color_space VARCHAR(50),
    bits_per_sample INTEGER,
    samples_per_pixel INTEGER,
    x_sampling_frequency DECIMAL,
    y_sampling_frequency DECIMAL,
    sampling_frequency_unit VARCHAR(20),
    compression_scheme VARCHAR(100),
    format_name VARCHAR(100),
    byte_order VARCHAR(20),
    orientation INTEGER,
    icc_profile_name VARCHAR(200),
    date_time_created TIMESTAMP,
    scanner_manufacturer VARCHAR(200),
    scanner_model_name VARCHAR(200),
    scanning_software_name VARCHAR(200),
    scanning_software_version VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**document_files** (associazione many-to-many)
```sql
CREATE TABLE document_files (
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    file_id INTEGER REFERENCES files(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    file_use VARCHAR(50),  -- 'master', 'normalized', 'export_high', etc.
    file_label VARCHAR(500),
    PRIMARY KEY (document_id, file_id)
);
```

### Indici

```sql
CREATE INDEX idx_documents_logical_id ON documents(logical_id);
CREATE INDEX idx_documents_owner_id ON documents(owner_id);
CREATE INDEX idx_documents_mets_id ON documents(mets_document_id);
CREATE INDEX idx_files_owner_id ON files(owner_id);
CREATE INDEX idx_files_hash ON files(file_hash);
```

## MongoDB Schema

### Collection: mets_documents

Struttura documento METS ECO-MiC:

```javascript
{
  _id: ObjectId,
  schema_version: "1.1",  // "1.1" o "1.2"
  
  // Identificatori
  logical_id: "DOC001",
  conservative_id: "IT-MO0172-DOC001",
  conservative_id_authority: "IT-MO0172",
  
  // Descrittivi
  title: "Titolo documento",
  description: "Descrizione completa...",
  type_of_resource: "risorsa manoscritta",
  
  // Archivio (gerarchia)
  archive: {
    name: "Archivio di Stato di Modena",
    contact: "archivio@example.com",
    fund_name: "Fondo Estense",
    series_name: "Serie Amministrativa",
    folder_number: "Busta 45"
  },
  
  // Temporali
  temporal: {
    date_from: "1850-01-01",
    date_to: "1850-12-31",
    period: "Risorgimento"
  },
  
  // Contesto
  location: "Modena, Italy",
  language: "it",
  subjects: ["storia", "amministrazione"],
  
  // Agenti
  agents: {
    producer: { 
      name: "Casa d'Este", 
      type: "corporate", 
      role: "producer" 
    },
    creator: { 
      name: "Francesco IV d'Este", 
      type: "personal", 
      role: "creator" 
    }
  },
  
  // Diritti
  rights: {
    license_url: "https://...",
    rights_statement: "...",
    category: "COPYRIGHTED",
    holder: "Archivio di Stato",
    constraint: "NoC-OKLR"
  },
  
  // Tecnici (livello documento)
  technical: {
    image_producer: "EDS Gamma",
    scanner_manufacturer: "...",
    scanner_model: "..."
  },
  
  // Fisici
  physical: {
    document_type: "manuscript",
    total_pages: 14,
    physical_form: "documento testuale",
    extent_description: "c. 14 nel fascicolo"
  },
  
  // METS header
  mets_header: {
    record_status: "COMPLETE",
    profile: "http://www.iccu.sbn.it/metaAG1.pdf"
  },
  
  // Audit
  created_at: ISODate("2024-12-15T10:00:00Z"),
  updated_at: ISODate("2024-12-15T10:00:00Z"),
  
  // Cross-references
  platform_document_id: 123,  // PostgreSQL documents.id
  owner_id: 456
}
```

### Indici MongoDB

```javascript
// Unique constraint
db.mets_documents.createIndex({ logical_id: 1 }, { unique: true })

// Query optimization
db.mets_documents.createIndex({ owner_id: 1 })
db.mets_documents.createIndex({ "archive.name": 1 })
db.mets_documents.createIndex({ schema_version: 1 })
db.mets_documents.createIndex({ created_at: -1 })

// Date range queries
db.mets_documents.createIndex({ "temporal.date_from": 1 })
db.mets_documents.createIndex({ "temporal.date_to": 1 })

// Full-text search (weighted)
db.mets_documents.createIndex(
  {
    "title": "text",
    "description": "text",
    "conservative_id": "text",
    "archive.name": "text",
    "archive.fund_name": "text",
    "subjects": "text",
    "agents.producer.name": "text",
    "agents.creator.name": "text"
  },
  {
    name: "fulltext_search_idx",
    weights: {
      "title": 10,
      "conservative_id": 8,
      "description": 5,
      "archive.name": 3,
      "subjects": 3
    },
    default_language: "italian"
  }
)
```

## MinIO Storage Organization

### Struttura Bucket

```
archivia-files/
  ├── documents/
  │   ├── DOC001/
  │   │   ├── master/
  │   │   │   ├── DOC001_001.tif
  │   │   │   └── DOC001_002.tif
  │   │   ├── normalized/
  │   │   │   ├── DOC001_001.jpg
  │   │   │   └── DOC001_002.jpg
  │   │   ├── export_high/
  │   │   │   └── DOC001_001.jpg
  │   │   └── metadata/
  │   │       └── metadata.xml
  │   └── DOC002/
  │       └── master/
  │           └── DOC002_001.dng
  └── chunks/
      └── [temporary upload chunks]
```

