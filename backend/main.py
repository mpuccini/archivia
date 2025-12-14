from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables, get_db
from app.services.auth import AuthService
from app.services.mongodb import mongodb_service
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

    # Connect to MongoDB
    try:
        await mongodb_service.connect_async()
        logger.info("MongoDB connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

    logger.info("Archivia API v2.0.0 started successfully!")
    logger.info("To create an admin user, use the /api/auth/register endpoint or run the user creation script")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Archivia API...")

    # Close MongoDB connection
    await mongodb_service.close_async()

    logger.info("Archivia API shut down successfully")


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
