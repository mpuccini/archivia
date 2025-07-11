from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileBase(BaseModel):
    """Base file schema"""
    filename: str
    original_filename: str
    content_type: Optional[str] = None
    file_size: int


class FileCreate(FileBase):
    """File creation schema"""
    minio_object_name: str
    bucket_name: str
    file_hash: Optional[str] = None
    is_multipart: bool = False


class FileUpdate(BaseModel):
    """File update schema"""
    filename: Optional[str] = None
    upload_completed: Optional[bool] = None
    file_hash: Optional[str] = None


class FileResponse(FileBase):
    """File response schema"""
    id: int
    file_hash: Optional[str]
    minio_object_name: str
    bucket_name: str
    is_multipart: bool
    upload_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """File upload response schema"""
    message: str
    file_id: int
    upload_id: Optional[str] = None
    chunk_size: Optional[int] = None
    total_chunks: Optional[int] = None


class ChunkUploadRequest(BaseModel):
    """Chunk upload request schema"""
    chunk_number: int
    total_chunks: int


class ChunkUploadResponse(BaseModel):
    """Chunk upload response schema"""
    message: str
    chunk_number: int
    etag: str
    upload_url: str


class CompleteUploadRequest(BaseModel):
    """Complete multipart upload request schema"""
    parts: list[dict]  # [{"PartNumber": 1, "ETag": "..."}, ...]
