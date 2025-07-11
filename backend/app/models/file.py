from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class File(Base):
    """File model"""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA256 hash
    minio_object_name = Column(String(500), nullable=False)  # Path in MinIO
    bucket_name = Column(String(100), nullable=False)
    is_multipart = Column(Boolean, default=False)
    upload_id = Column(String(255), nullable=True)  # For multipart uploads
    upload_completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    owner = relationship("User", back_populates="files")


class FileChunk(Base):
    """File chunk model for multipart uploads"""
    __tablename__ = "file_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    chunk_number = Column(Integer, nullable=False)
    chunk_size = Column(BigInteger, nullable=False)
    etag = Column(String(255), nullable=True)
    uploaded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    file = relationship("File")
