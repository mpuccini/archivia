# Archivia

Sistema di gestione documentale per l'archiviazione e la catalogazione di documenti digitali secondo lo standard METS ECO-MiC 1.1.

## Caratteristiche

- **Standard METS ECO-MiC 1.1**: Supporto completo profilo ICCU
- **Architettura Dual-Database**: PostgreSQL + MongoDB
- **Ricerca Avanzata**: Full-text search con stemming italiano
- **Upload Massivo**: Batch import da Excel e ZIP
- **File Grandi**: Supporto DNG fino a 80GB
- **Import Automatico**: Estrazione metadati da XML/CSV

## Quick Start

```bash
# Avvia tutti i servizi
docker compose up -d

# Crea utente admin
docker compose exec backend python create_admin.py

# Accedi all'applicazione
open http://localhost:3000
```

## Accessi

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO**: http://localhost:9001 (archivia/archivia123)

## Documentazione

La documentazione completa è disponibile in `/docs`:

- [Panoramica Sistema](docs/index.md)
- [Architettura](docs/architecture/overview.md)
- [API](docs/api/overview.md)
- [Guide](docs/guides/user-guide.md)
- [Changelog](docs/CHANGELOG.md)

### Generazione Documentazione (MkDocs)

```bash
# Installa MkDocs
pip install mkdocs-material

# Serve localmente
mkdocs serve

# Build per deploy
mkdocs build
```

## Stack Tecnologico

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + MongoDB
- **Frontend**: Vue 3 + Vite + Ant Design Vue 4.2
- **Storage**: MinIO (S3-compatible)
- **Deployment**: Docker Compose

## Gestione Utenti

Archivia utilizza un sistema di autenticazione semplice. Per creare un utente:

```bash
# Creazione interattiva (consigliato)
docker compose exec backend python create_admin.py
```

Lo script ti chiederà:
1. **Username** (default: `admin`)
2. **Password** (minimo 8 caratteri, richiesta conferma)

Se l'utente esiste già, puoi scegliere di resettare la password.

### Reset Password

Per resettare la password di un utente esistente, esegui nuovamente lo script e conferma il reset quando richiesto.

### Primo Avvio

Dopo aver avviato i servizi con `docker compose up -d`, **devi creare almeno un utente** prima di poter accedere all'applicazione:

```bash
docker compose exec backend python create_admin.py
```

## Sviluppo

```bash
# Backend dev
docker compose logs -f backend

# Frontend dev
cd frontend && npm run dev

# Database access
docker compose exec db psql -U archivia -d archivia
```

## Licenza

Copyright © 2025 Ass. Arca sul Lago

Questo progetto è rilasciato sotto la **European Union Public Licence (EUPL) v. 1.2**.

Vedi il file [LICENSE](LICENSE) per il testo completo della licenza.

Per maggiori informazioni: https://interoperable-europe.ec.europa.eu/licence/european-union-public-licence-version-12-eupl

## Link Utili

- [METS Standard](http://www.loc.gov/standards/mets/)
- [ECO-MiC GitHub](https://github.com/icdp-digital-library/profilo-mets-ecomic)
- [ICCU](https://www.iccu.sbn.it/)
