# Panoramica Architettura

## Architettura Generale

Archivia utilizza un'architettura **dual-database** con separazione delle responsabilità:

- **PostgreSQL**: Metadati piattaforma, relazioni, file tracking
- **MongoDB**: Metadati METS ECO-MiC, documenti archivistici
- **MinIO**: Storage oggetti (file immagini, DNG, PDF)

### Vantaggi Architettura Dual-Database

1. **Flessibilità Schema**: MongoDB gestisce metadati METS variabili per versione
2. **Performance**: PostgreSQL per query relazionali, MongoDB per full-text search
3. **Scalabilità**: Scaling indipendente dei due database
4. **Evoluzione Standard**: Nuove versioni METS senza migration SQL

## Stack Tecnologico

### Backend
- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0
- **Async DB Driver**: Motor (MongoDB), asyncpg
- **Validation**: Pydantic v2
- **Auth**: JWT (python-jose)

### Frontend
- **Framework**: Vue 3.3+ (Composition API)
- **Build**: Vite 4
- **UI**: Ant Design Vue 4.2
- **State**: Pinia
- **HTTP**: Axios

### Infrastructure
- **DB Relazionale**: PostgreSQL 15
- **DB Documenti**: MongoDB 7.0
- **Object Storage**: MinIO (S3-compatible)
- **Web Server**: Nginx Alpine
- **Orchestration**: Docker Compose

## Pattern Architetturali

### Service Layer Pattern

```
Routes (FastAPI) 
  ↓
Services (Business Logic)
  ↓
Models (SQLAlchemy ORM) / MongoDB Service
  ↓
Database / Storage
```

### Transaction Coordinator Pattern

Per operazioni dual-database, utilizziamo 3-phase commit:

1. **Phase 1**: PostgreSQL transaction
2. **Phase 2**: MongoDB document creation
3. **Phase 3**: MinIO file upload

In caso di fallimento, rollback automatico in ordine inverso.

## Sicurezza

- JWT token-based authentication
- Password hashing (bcrypt)
- Input validation (Pydantic)
- File type validation (magic numbers)
- CORS configurabile
- User isolation (owner_id)

