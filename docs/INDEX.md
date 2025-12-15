# Archivia - Documentazione

Sistema di gestione documentale per l'archiviazione e la catalogazione di documenti digitali secondo lo standard METS ECO-MiC.

---

## Panoramica

Archivia è una piattaforma completa per la gestione di archivi digitali che implementa lo standard italiano **METS ECO-MiC 1.1** (ICCU - Istituto Centrale per il Catalogo Unico) per la digitalizzazione e conservazione di documenti archivistici.

### Caratteristiche Principali

- **Metadati Archivistici Completi**: Supporto completo standard METS ECO-MiC 1.1
- **Architettura Dual-Database**: PostgreSQL + MongoDB per flessibilità e performance
- **Ricerca Avanzata**: Full-text search con MongoDB e stemming italiano
- **Upload Massivo**: Import batch da Excel e ZIP con struttura ECO-MiC
- **File di Grandi Dimensioni**: Supporto DNG fino a 80GB con chunked upload
- **Import Metadati Automatico**: Estrazione automatica da XML/CSV in cartella metadata
- **Export Standard**: Generazione METS XML conforme con validazione

---

## Documentazione

### [Architettura](architecture/overview.md)

- [Panoramica Sistema](architecture/overview.md)
- [Database](architecture/database.md)
- [Backend](architecture/backend.md)
- [Frontend](architecture/frontend.md)
- [Deployment](architecture/deployment.md)

### [API](api/overview.md)

- [Panoramica API](api/overview.md)
- [Documents API](api/documents.md)
- [Files API](api/files.md)
- [Authentication API](api/authentication.md)

### [Guide](guides/user-guide.md)

- [Guida Utente](guides/user-guide.md)
- [Guida Sviluppatore](guides/developer-guide.md)
- [METS ECO-MiC](guides/mets-ecomic.md)
- [Deploy in Produzione](guides/production-deploy.md)

### [Changelog](CHANGELOG.md)

Storia completa delle modifiche e degli interventi.

---

## Quick Start

```bash
# Avvia tutti i servizi
docker compose up -d

# Crea utente admin
docker compose exec backend python create_admin.py

# Accedi
open http://localhost:3000
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **MinIO**: http://localhost:9001

---

## Stack Tecnologico

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + MongoDB
- **Frontend**: Vue 3 + Vite + Ant Design Vue 4
- **Storage**: MinIO (S3-compatible)
- **Deployment**: Docker Compose

