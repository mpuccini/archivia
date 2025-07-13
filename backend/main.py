from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables, get_db
from app.services.auth import AuthService
from app.routes import auth_router, files_router
from app.routes.documents import router as documents_router
from app.schemas.user import UserCreate
from app.utils import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Archivia API", 
    description="Modular file archiving system with authentication and multipart upload",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(files_router, prefix="/api")
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Archivia API v2.0.0...")
    
    # Create database tables
    create_tables()
    
    # Create admin user if it doesn't exist
    auth_service = AuthService()
    db = next(get_db())
    try:
        admin_user = auth_service.get_user_by_username(db, "admin")
        if not admin_user:
            admin_data = UserCreate(username="admin", password="admin123")
            auth_service.create_user(db, admin_data)
            logger.info("Admin user created: admin/admin123")
        else:
            logger.info("Admin user already exists")
    finally:
        db.close()
    
    logger.info("Archivia API v2.0.0 started successfully!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Archivia API", 
        "version": "2.0.0",
        "features": ["authentication", "file_upload", "multipart_upload", "document_management", "modular_architecture"],
        "architecture": {
            "routes": ["auth", "files", "documents"],
            "services": ["auth", "minio", "file", "document"],
            "models": ["user", "file", "file_chunk", "document", "document_file"],
            "utils": ["file_utils", "logging"]
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}
