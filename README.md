# Archivia - Digital Document Archiving System

A modern digital document archiving system built with Vue.js frontend and FastAPI backend.

## Architecture

- **Frontend**: Vue.js 3 with Vite, Tailwind CSS, and Headless UI
- **Backend**: FastAPI with PostgreSQL database
- **Storage**: MinIO object storage
- **Deployment**: Docker Compose

## Prerequisites

- Docker and Docker Compose (modern CLI - `docker compose` command)
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## Getting Started

### Using Docker Compose (Recommended)

1. **Start all services**:
   ```bash
   docker compose up --build
   ```

2. **Access the application**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - MinIO Console: [http://localhost:9001](http://localhost:9001)

3. **Stop all services**:
   ```bash
   docker compose down
   ```

### Development Workflow

#### Frontend Development

To work on the frontend with hot reload:

1. **Stop the frontend container** (if running):
   ```bash
   docker compose stop frontend
   ```

2. **Install dependencies locally**:
   ```bash
   cd frontend
   npm install
   ```

3. **Start frontend in development mode**:
   ```bash
   npm run dev
   ```

4. **Keep backend services running**:
   ```bash
   docker compose up db backend minio
   ```

#### Backend Development

For backend development with auto-reload:

1. **The backend is already configured with `--reload`** in the Docker Compose configuration
2. **Edit files in `./backend`** - changes will be reflected automatically
3. **View logs**:
   ```bash
   docker compose logs -f backend
   ```

### Building and Updating Containers

#### Frontend Container Updates

When you make changes to the frontend and want to update the container:

1. **Rebuild the frontend service**:
   ```bash
   docker compose build frontend
   ```

2. **Restart the frontend service**:
   ```bash
   docker compose up -d frontend
   ```

3. **Or rebuild and restart in one command**:
   ```bash
   docker compose up --build -d frontend
   ```

#### Backend Container Updates

The backend container automatically reloads code changes due to the volume mount and `--reload` flag.

#### Full System Rebuild

To rebuild all containers:

```bash
docker compose down
docker compose build
docker compose up -d
```

### Useful Commands

#### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f frontend
docker compose logs -f backend
```

#### Service Management
```bash
# Start specific services
docker compose up -d db backend

# Stop specific services
docker compose stop frontend

# Restart a service
docker compose restart backend
```

#### Database Operations
```bash
# Access PostgreSQL
docker compose exec db psql -U archivia -d archivia

# View database logs
docker compose logs -f db
```

#### MinIO Operations
```bash
# Access MinIO console at http://localhost:9001
# Credentials: archivia / archivia123
```

### Troubleshooting

#### Frontend Not Updating After Rebuild

If the frontend container doesn't reflect your changes after rebuild:

1. **Clear Docker build cache**:
   ```bash
   docker compose build --no-cache frontend
   ```

2. **Remove the container and rebuild**:
   ```bash
   docker compose rm -f frontend
   docker compose build frontend
   docker compose up -d frontend
   ```

3. **Check if files are properly copied**:
   ```bash
   docker compose exec frontend ls -la /usr/share/nginx/html
   ```

#### Port Conflicts

If you get port conflict errors:

1. **Check what's using the ports**:
   ```bash
   lsof -i :3000  # Frontend
   lsof -i :8000  # Backend
   lsof -i :5432  # PostgreSQL
   ```

2. **Stop conflicting services or change ports in the Docker Compose configuration**

#### Container Health Issues

1. **Check container status**:
   ```bash
   docker compose ps
   ```

2. **View detailed container info**:
   ```bash
   docker compose exec frontend sh
   docker compose exec backend bash
   ```

### Environment Variables

The system uses the following environment variables:

- `VITE_API_URL`: Frontend API endpoint (default: http://localhost:8000)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key for authentication
- `MINIO_*`: MinIO configuration

## Features

### Document Management
- Upload and manage digital documents with rich metadata
- Multi-step document upload wizard with guided metadata entry
- Support for batch document import via Excel/CSV
- METS ECO-MiC 1.1 compliant XML generation and export
- Support for large files including DNG (Digital Negative) RAW files up to 80GB

### METS ECO-MiC 1.1 Standard
- Complete implementation of Italian METS ECO-MiC 1.1 archival standard
- Real-time validation against ECO-MiC 1.1 via Cineca API
- Integrated validation during document upload workflow
- Detailed error reporting with line numbers and tag references
- Per-file technical metadata (MIX standard)
- Rights metadata (METSRIGHTS schema)

### File Handling
- **Chunked uploads** for files up to 80GB (DNG camera RAW files)
- **Streaming downloads** for memory-efficient file delivery
- **Automatic thumbnail generation** for DNG/RAW files
- Multiple image formats: TIFF, JPEG, PNG, DNG
- File type validation via magic number verification
- MD5 checksums for data integrity

### Storage & Export
- MinIO object storage for scalable file management
- Multiple export formats (CSV, METS XML, ZIP archives)
- Batch operations for multiple documents
- Full document archives with metadata and files
- Memory-optimized ZIP creation (handles 100+ GB archives)

### User Management
- Secure JWT-based authentication
- User-specific document access control
- Admin user creation via CLI script

## Project Structure

```
archivia/
├── docker-compose.yml          # Service orchestration
├── README.md                   # This file
├── CLAUDE.md                   # Project instructions for Claude Code
├── docs/                       # Comprehensive documentation
│   ├── deployment/            # Deployment guides
│   ├── features/              # Feature documentation
│   ├── history/               # Historical records
│   ├── implementation/        # Implementation guides
│   ├── security/              # Security best practices
│   └── testing/               # Testing procedures
├── frontend/                   # Vue.js frontend
│   ├── Dockerfile             # Frontend container
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.js         # Vite configuration
│   └── src/                   # Source code
└── backend/                    # FastAPI backend
    ├── Dockerfile             # Backend container
    ├── requirements.txt       # Python dependencies
    ├── main.py               # Application entry point
    └── app/                  # Application modules
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### For Users
- **[docs/features/METADATA_IMPORT.md](docs/features/METADATA_IMPORT.md)** - Batch metadata import guide
- **[docs/testing/TESTING_GUIDE.md](docs/testing/TESTING_GUIDE.md)** - Testing procedures

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - Complete development guide and project overview
- **[docs/implementation/METS_ECOMIC_IMPLEMENTATION.md](docs/implementation/METS_ECOMIC_IMPLEMENTATION.md)** - METS ECO-MiC 1.1 implementation details
- **[docs/implementation/PERFORMANCE_OPTIMIZATIONS.md](docs/implementation/PERFORMANCE_OPTIMIZATIONS.md)** - Large file handling and performance tuning

### For DevOps
- **[docs/deployment/DOCKER_DEPLOYMENT.md](docs/deployment/DOCKER_DEPLOYMENT.md)** - Deployment guide and troubleshooting
- **[docs/security/SECURITY_RECOMMENDATIONS.md](docs/security/SECURITY_RECOMMENDATIONS.md)** - Security best practices

### Historical Reference
- **[docs/history/SECURITY_FIXES_HISTORY.md](docs/history/SECURITY_FIXES_HISTORY.md)** - Security fixes and improvements log

## Contributing

This project follows:
- **Security-first approach** - All code changes undergo security review
- **METS ECO-MiC 1.1 compliance** - Strict adherence to Italian archival standards
- **Performance optimization** - Designed to handle files up to 80GB efficiently

## License

[Add your license information here]

## Support

For issues or questions:
- Check the [documentation](docs/)
- Review [CLAUDE.md](CLAUDE.md) for development guidance
- Consult the [Testing Guide](docs/testing/TESTING_GUIDE.md) for validation procedures
