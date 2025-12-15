# Documentazione Archivia

Documentazione tecnica completa del sistema Archivia.

## Struttura Documentazione

```
docs/
├── README.md                 # Questo file
├── index.md                  # Homepage documentazione (MkDocs)
├── CHANGELOG.md              # Storia completa modifiche
│
├── architecture/             # Architettura Software
│   ├── overview.md          # Panoramica generale
│   ├── database.md          # Schema PostgreSQL + MongoDB
│   ├── backend.md           # Struttura backend
│   ├── frontend.md          # Struttura frontend
│   └── deployment.md        # Deploy e scaling
│
├── api/                      # Documentazione API
│   ├── overview.md          # Introduzione API
│   ├── documents.md         # Documents API
│   ├── files.md             # Files API
│   └── authentication.md    # Auth API
│
├── guides/                   # Guide Pratiche
│   ├── user-guide.md        # Guida utente
│   ├── developer-guide.md   # Guida sviluppatore
│   ├── mets-ecomic.md       # Standard METS
│   └── production-deploy.md # Deploy produzione
│
└── history/                  # Storia Interventi
    ├── implementations.md   # Riepilogo implementazioni
    └── [file dettagliati]   # Documentazione tecnica originale
```

## Quick Links

### Per Utenti
- [Guida Utente](guides/user-guide.md)
- [Changelog](CHANGELOG.md)

### Per Sviluppatori
- [Panoramica Architettura](architecture/overview.md)
- [Guida Sviluppatore](guides/developer-guide.md)
- [API Documentation](api/overview.md)

### Per DevOps
- [Deployment](architecture/deployment.md)
- [Deploy Produzione](guides/production-deploy.md)

## Generazione Documentazione

Questo progetto utilizza [MkDocs](https://www.mkdocs.org/) con tema [Material](https://squidfunk.github.io/mkdocs-material/).

### Setup

```bash
pip install mkdocs-material
```

### Comandi

```bash
# Serve localmente (http://localhost:8000)
mkdocs serve

# Build statico
mkdocs build

# Deploy su GitHub Pages
mkdocs gh-deploy
```

### Configurazione

La configurazione MkDocs è in `/mkdocs.yml` nella root del progetto.

## Convenzioni

### Nomi File
- Usa kebab-case: `user-guide.md`
- Nomi descrittivi e chiari
- Prefissi per tipo: `api-`, `guide-`, etc.

### Struttura Markdown
- Titolo H1 per titolo pagina
- Sezioni H2 per capitoli principali
- Sezioni H3 per sottocapitoli
- Code blocks con linguaggio specificato

### Link Interni
Usa path relativi:
```markdown
[Architettura](architecture/overview.md)
[API Docs](../api/overview.md)
```

## Contribuire

1. Mantieni struttura cartelle esistente
2. Aggiungi nuove pagine al `nav` in `mkdocs.yml`
3. Usa convenzioni di naming
4. Include esempi pratici
5. Testa con `mkdocs serve` prima del commit

## Storia Documenti

I documenti storici degli interventi tecnici sono conservati in `history/`:

- Implementazioni feature
- Fix bug e issue
- Migrazioni
- Refactoring

Questi file forniscono contesto dettagliato per ogni intervento.

