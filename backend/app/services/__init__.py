from .auth import AuthService
from .minio import MinIOService
from .file import FileService

# Global service instances
auth_service = AuthService()
minio_service = MinIOService()
file_service = FileService()

__all__ = ["AuthService", "MinIOService", "FileService", "auth_service", "minio_service", "file_service"]