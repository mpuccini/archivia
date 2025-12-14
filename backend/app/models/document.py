from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Document(Base):
    """
    Document model - Platform metadata only

    Stores core platform data for document management.
    METS ECO-MiC archival metadata is stored separately in MongoDB.
    """
    __tablename__ = "documents"

    # Platform fields
    id = Column(Integer, primary_key=True, index=True)
    logical_id = Column(String(255), nullable=False, unique=True)  # Denormalized for queries
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # MongoDB reference
    mets_document_id = Column(String(24), nullable=True)  # MongoDB ObjectId as string

    # Relationships
    owner = relationship("User", back_populates="documents")
    document_files = relationship("DocumentFile", back_populates="document", cascade="all, delete-orphan")


class DocumentFile(Base):
    """Association table between documents and files with additional metadata"""
    __tablename__ = "document_files"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    
    # File-specific metadata from METS
    file_use = Column(String(50), nullable=True)  # e.g., "ARCHIVE", "HIGH"
    file_category = Column(String(50), nullable=True)  # e.g., "master", "normalized", "export_high", "export_low", "metadata", "icc", "logs"
    file_label = Column(String(255), nullable=True)  # e.g., "Dorso", "Piatto anteriore"
    sequence_number = Column(Integer, nullable=True)  # ORDER attribute
    checksum_md5 = Column(String(64), nullable=True)  # Supports both MD5 (32) and SHA256 (64)
    
    # Technical metadata specific to this file (MIX)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    bits_per_sample = Column(String(50), nullable=True)  # e.g., "8,8,8"
    samples_per_pixel = Column(Integer, nullable=True)
    date_time_created = Column(DateTime, nullable=True)

    # Enhanced technical metadata (ECO-MiC)
    compression_scheme = Column(String(50), nullable=True)  # e.g., "uncompressed", "JPEG"
    color_space = Column(String(50), nullable=True)  # e.g., "sRGB", "RGB"
    sampling_frequency_unit = Column(String(20), nullable=True)  # e.g., "in.", "cm"
    x_sampling_frequency = Column(Integer, nullable=True)  # e.g., 300 for 300 DPI
    y_sampling_frequency = Column(Integer, nullable=True)  # e.g., 300 for 300 DPI

    # Additional MIX metadata fields
    format_name = Column(String(100), nullable=True)  # e.g., "image/tiff", "image/dng"
    byte_order = Column(String(20), nullable=True)  # e.g., "little endian", "big endian"
    orientation = Column(String(50), nullable=True)  # e.g., "normal*", "rotate 90"
    icc_profile_name = Column(String(255), nullable=True)  # e.g., "sRGB IEC61966-2.1"

    # Scanner/Capture metadata
    scanner_manufacturer = Column(String(255), nullable=True)  # e.g., "Nikon", "Canon"
    scanner_model_name = Column(String(255), nullable=True)  # e.g., "Nikon D850"
    scanning_software_name = Column(String(255), nullable=True)  # e.g., "Adobe Lightroom"
    scanning_software_version = Column(String(100), nullable=True)

    # Comprehensive metadata storage (JSONB) - stores ALL extracted metadata
    # This includes DNG-specific tags, EXIF data, and any other metadata
    raw_metadata = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="document_files")
    file = relationship("File")
