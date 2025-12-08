# Archivia - Docker Deployment Guide

## 🚀 Quick Start

### 1. Start the Application

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Check if all services are running
docker-compose ps
```

### 2. Create Admin User

**Option A: Using the script (Recommended)**

```bash
# Enter the backend container
docker-compose exec backend python create_admin.py
```

Follow the prompts to create your admin user.

**Option B: Using Docker Exec**

```bash
docker-compose exec backend python -c "
from app.core.database import SessionLocal, create_tables
from app.services.auth import AuthService
from app.schemas.user import UserCreate

create_tables()
db = SessionLocal()
auth_service = AuthService()

# Create admin user
user_data = UserCreate(username='admin', password='your-secure-password')
user = auth_service.create_user(db, user_data)
print(f'Admin user created: {user.username}')
db.close()
"
```

**Option C: Using the API directly**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-secure-password"}'
```

### 3. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001 (archivia / archivia123)

---

## 🔧 Configuration

### Environment Variables

The application uses environment variables defined in:
1. `.env` (project root) - Used by docker-compose
2. `backend/.env` - Used when running backend locally

**Docker Compose Variables** (`.env`):
```bash
SECRET_KEY=<your-generated-secret-key>
```

**Backend Variables** (`backend/.env`):
```bash
DATABASE_URL=postgresql://archivia:archivia123@db:5432/archivia
SECRET_KEY=<same-as-above>
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=archivia
MINIO_SECRET_KEY=archivia123
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Generate Secure SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then update both `.env` files with the generated key.

---

## 🐛 Troubleshooting

### Issue: "Register here" not working

**Possible Causes:**

1. **CORS Error** - Check browser console
   ```bash
   # Fix: Ensure CORS_ORIGINS includes your frontend URL
   # In docker-compose.yml, backend environment section
   ```

2. **Backend not ready** - Wait for services to be healthy
   ```bash
   docker-compose logs backend
   # Look for: "Archivia API v2.0.0 started successfully!"
   ```

3. **Frontend can't reach backend** - Check network
   ```bash
   # Test from your machine:
   curl http://localhost:8000/health

   # Should return: {"status":"healthy","version":"2.0.0"}
   ```

4. **Database connection failed**
   ```bash
   docker-compose logs backend | grep -i error
   docker-compose logs db
   ```

### Issue: SECRET_KEY error

```bash
# Error: "Field required" for SECRET_KEY
# Solution: Ensure .env file exists with SECRET_KEY
cat .env
# Should contain: SECRET_KEY=<your-key>

# Restart backend
docker-compose restart backend
```

### Issue: Database connection refused

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Try connecting manually
docker-compose exec db psql -U archivia -d archivia
```

### Issue: MinIO connection error

```bash
# Check MinIO is running
docker-compose ps minio

# Access MinIO console
open http://localhost:9001
# Login: archivia / archivia123

# Create bucket manually if needed:
# Go to Buckets > Create Bucket > Name: archivia-files
```

---

## 📋 Common Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs --tail=100 backend

# Rebuild and restart
docker-compose up -d --build backend
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec db psql -U archivia -d archivia

# Run SQL query
docker-compose exec db psql -U archivia -d archivia -c "SELECT * FROM users;"

# Backup database
docker-compose exec db pg_dump -U archivia archivia > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U archivia -d archivia
```

### Backend Shell Access

```bash
# Python shell in backend container
docker-compose exec backend python

# Bash shell in backend container
docker-compose exec backend bash

# Run migrations (if you add them)
docker-compose exec backend alembic upgrade head
```

### Cleanup

```bash
# Remove all containers and networks
docker-compose down

# Remove all containers, networks, and volumes (⚠️ DELETES DATA!)
docker-compose down -v

# Remove unused images
docker image prune -a
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Generate a strong SECRET_KEY (32+ characters)
- [ ] Change default database password
- [ ] Change default MinIO credentials
- [ ] Update CORS_ORIGINS to only include production domains
- [ ] Enable HTTPS (use reverse proxy like nginx)
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Monitor logs for security events

---

## 📊 Service Health Checks

### Check Backend Health

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"2.0.0"}
```

### Check Database Connection

```bash
docker-compose exec backend python -c "
from app.core.database import engine
try:
    with engine.connect() as conn:
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### Check MinIO Connection

```bash
docker-compose exec backend python -c "
from app.services.minio import MinIOService
try:
    minio = MinIOService()
    print('✅ MinIO connection successful')
    print(f'Bucket exists: {minio.client.bucket_exists(\"archivia-files\")}')
except Exception as e:
    print(f'❌ MinIO connection failed: {e}')
"
```

---

## 🔄 Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose up -d --build

# Check logs for errors
docker-compose logs -f
```

---

## 📞 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f backend`
2. Check service health: `docker-compose ps`
3. Try the troubleshooting section above
4. Check API docs: http://localhost:8000/docs

---

## 🎯 Testing the API

Once your admin user is created, test the API:

```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# Test authenticated endpoint
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Create a document
curl -X POST http://localhost:8000/api/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "logical_id": "test-doc-001",
    "title": "Test Document",
    "description": "My first document"
  }'
```

---

## 📝 Development Mode

For development with hot-reload:

```bash
# Backend with auto-reload (already configured in docker-compose)
docker-compose up -d

# Frontend with hot-reload
cd frontend
npm install
npm run dev
```

The backend is already configured to auto-reload when you change files (see `--reload` flag in docker-compose.yml).
