import asyncio
import uuid
from datetime import timedelta
from typing import Dict, List, Optional, AsyncGenerator, BinaryIO
from minio import Minio
from minio.error import S3Error
import aiofiles
import magic
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MinIOService:
    """MinIO service for file storage and multipart uploads"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.client.make_bucket(settings.MINIO_BUCKET_NAME)
                logger.info(f"Created bucket: {settings.MINIO_BUCKET_NAME}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    def generate_object_name(self, original_filename: str) -> str:
        """Generate a unique object name for MinIO storage"""
        file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
        unique_id = str(uuid.uuid4())
        return f"{unique_id}.{file_extension}" if file_extension else unique_id
    
    async def initiate_multipart_upload(self, object_name: str, content_type: str) -> str:
        """Initiate a multipart upload and return upload_id"""
        try:
            loop = asyncio.get_event_loop()
            upload_result = await loop.run_in_executor(
                None,
                self.client._create_multipart_upload,
                settings.MINIO_BUCKET_NAME,
                object_name,
                {"Content-Type": content_type}
            )
            return upload_result.upload_id
        except S3Error as e:
            logger.error(f"Error initiating multipart upload: {e}")
            raise
    
    async def get_presigned_upload_url(
        self, 
        object_name: str, 
        upload_id: str, 
        part_number: int,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Get a presigned URL for uploading a part"""
        try:
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None,
                self.client.presigned_put_object,
                settings.MINIO_BUCKET_NAME,
                object_name,
                expires,
                {"uploadId": upload_id, "partNumber": str(part_number)}
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    async def complete_multipart_upload(
        self, 
        object_name: str, 
        upload_id: str, 
        parts: List[Dict]
    ) -> str:
        """Complete a multipart upload"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.client._complete_multipart_upload,
                settings.MINIO_BUCKET_NAME,
                object_name,
                upload_id,
                parts
            )
            return result.etag
        except S3Error as e:
            logger.error(f"Error completing multipart upload: {e}")
            raise
    
    async def abort_multipart_upload(self, object_name: str, upload_id: str):
        """Abort a multipart upload"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.client._abort_multipart_upload,
                settings.MINIO_BUCKET_NAME,
                object_name,
                upload_id
            )
        except S3Error as e:
            logger.error(f"Error aborting multipart upload: {e}")
            raise
    
    async def upload_file(self, file_data: BinaryIO, object_name: str, content_type: str) -> str:
        """Upload a file directly (for small files)"""
        try:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.client.put_object,
                settings.MINIO_BUCKET_NAME,
                object_name,
                file_data,
                file_size,
                content_type
            )
            return object_name
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    async def get_file_url(self, object_name: str, expires: timedelta = timedelta(hours=1)) -> str:
        """Get a presigned URL for downloading a file"""
        try:
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None,
                self.client.presigned_get_object,
                settings.MINIO_BUCKET_NAME,
                object_name,
                expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating download URL: {e}")
            raise
    
    def delete_file(self, object_name: str):
        """Delete a file from MinIO"""
        try:
            self.client.remove_object(
                settings.MINIO_BUCKET_NAME,
                object_name
            )
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise
    
    def detect_content_type(self, file_path: str) -> str:
        """Detect file content type using python-magic"""
        try:
            return magic.from_file(file_path, mime=True)
        except Exception:
            return "application/octet-stream"
    
    def get_file(self, object_name: str):
        """Get file data from MinIO"""
        try:
            response = self.client.get_object(
                settings.MINIO_BUCKET_NAME,
                object_name
            )
            return response
        except S3Error as e:
            logger.error(f"Error getting file: {e}")
            raise
