from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Document(Base):
    """Document model for METS metadata"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic identification
    logical_id = Column(String(255), nullable=False, unique=True)  # MODS identifier logicalId
    conservative_id = Column(String(255), nullable=True)  # MODS identifier conservativeId  
    conservative_id_authority = Column(String(100), nullable=True)  # ISIL
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Archive information
    archive_name = Column(String(255), nullable=True)  # e.g., "Archivio di stato di Modena"
    archive_contact = Column(String(255), nullable=True)  # Contact email
    fund_name = Column(String(255), nullable=True)  # Fund/Collection name
    series_name = Column(String(255), nullable=True)  # Series name
    folder_number = Column(String(100), nullable=True)  # Folder/Unit number (e.g., "Busta 45")
    
    # Temporal information
    date_from = Column(String(50), nullable=True)  # Start date
    date_to = Column(String(50), nullable=True)  # End date
    period = Column(String(255), nullable=True)  # Historical period
    
    # Geographic and contextual information
    location = Column(String(255), nullable=True)  # Place/Location
    language = Column(String(10), nullable=True)  # Language code (e.g., "it", "en")
    subjects = Column(Text, nullable=True)  # Subjects/Keywords (comma-separated)
    
    # Rights information
    license_url = Column(String(500), nullable=True)  # DCT license
    rights_statement = Column(String(500), nullable=True)  # DCT rights
    
    # Technical metadata (from MIX)
    image_producer = Column(String(255), nullable=True)  # e.g., "EDS Gamma"
    scanner_manufacturer = Column(String(255), nullable=True)  # e.g., "Metis Systems srl"
    scanner_model = Column(String(500), nullable=True)  # Scanner model details
    
    # Physical structure
    document_type = Column(String(100), nullable=True)  # e.g., "book", "manuscript"
    total_pages = Column(Integer, nullable=True)
    
    # Full METS XML storage
    mets_xml = Column(Text, nullable=True)  # Store complete METS XML
    
    # System fields
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
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
    file_label = Column(String(255), nullable=True)  # e.g., "Dorso", "Piatto anteriore"
    sequence_number = Column(Integer, nullable=True)  # ORDER attribute
    checksum_md5 = Column(String(32), nullable=True)
    
    # Technical metadata specific to this file
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    bits_per_sample = Column(String(50), nullable=True)  # e.g., "8,8,8"
    samples_per_pixel = Column(Integer, nullable=True)
    date_time_created = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="document_files")
    file = relationship("File")
