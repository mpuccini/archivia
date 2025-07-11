import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://archivia:archivia123@localhost:5432/archivia"
    )
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://frontend:80",
        "http://archivia-frontend:80",
        "*"  # Permetti tutti per sviluppo
    ]
    
    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "archivia")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "archivia123")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "archivia-files")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024 * 1024  # 10GB
    CHUNK_SIZE: int = 64 * 1024 * 1024  # 64MB chunks for multipart
    
    class Config:
        env_file = ".env"


settings = Settings()
