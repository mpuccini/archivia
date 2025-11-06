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
   - Backend API: [http://localhost:8000](http://localhost:3000)
   - MinIO Console: [http://localhost:9001](http://localhost:3000)

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

### Project Structure

```
archivia/
├── docker-compose.yml          # Service orchestration (modern syntax)
├── README.md                   # This file
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
