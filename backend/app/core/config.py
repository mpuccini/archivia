import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str
    MONGODB_URL: str = "mongodb://archivia:archivia123@mongodb:27017/archivia_mets?authSource=admin"

    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS - Accept both string and list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080"

    @field_validator('CORS_ORIGINS', mode='after')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str = "archivia-files"
    MINIO_SECURE: bool = False

    @field_validator('MINIO_SECURE', mode='before')
    @classmethod
    def parse_minio_secure(cls, v):
        """Parse MINIO_SECURE from string to boolean"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return v
    
    # File upload
    MAX_FILE_SIZE: int = 80 * 1024 * 1024 * 1024  # 80GB (for large DNG files)
    CHUNK_SIZE: int = 64 * 1024 * 1024  # 64MB chunks for multipart
    STREAMING_CHUNK_SIZE: int = 1 * 1024 * 1024  # 1MB chunks for streaming downloads
    HASH_CHUNK_SIZE: int = 8 * 1024  # 8KB chunks for hash calculation


settings = Settings()
