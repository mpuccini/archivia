from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
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
    conservative_id_authority = Column(String(100), nullable=True)  # ISIL (e.g., "IT-MO0172")
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    # MODS typeOfResource (ECO-MiC required)
    type_of_resource = Column(String(100), nullable=True)  # e.g., "risorsa manoscritta", "documento testuale"
    
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

    # Corporate and personal names (ECO-MiC)
    producer_name = Column(String(255), nullable=True)  # Corporate/personal name who produced the document
    producer_type = Column(String(20), nullable=True)  # "corporate" or "personal"
    producer_role = Column(String(100), nullable=True)  # e.g., "producer", "author"
    creator_name = Column(String(255), nullable=True)  # Creator/contributor name
    creator_type = Column(String(20), nullable=True)  # "corporate" or "personal"
    creator_role = Column(String(100), nullable=True)  # e.g., "creator", "contributor"
    
    # Rights information (ECO-MiC metsrights)
    license_url = Column(String(500), nullable=True)  # DCT license URL
    rights_statement = Column(String(500), nullable=True)  # DCT rights statement
    rights_category = Column(String(50), nullable=True)  # e.g., "COPYRIGHTED", "PUBLIC DOMAIN", "CONTRACTUAL"
    rights_holder = Column(String(255), nullable=True)  # Rights holder name
    rights_constraint = Column(String(100), nullable=True)  # e.g., "NoC-OKLR", "InC"
    
    # Technical metadata (from MIX)
    image_producer = Column(String(255), nullable=True)  # e.g., "EDS Gamma"
    scanner_manufacturer = Column(String(255), nullable=True)  # e.g., "Metis Systems srl"
    scanner_model = Column(String(500), nullable=True)  # Scanner model details
    
    # Physical structure
    document_type = Column(String(100), nullable=True)  # e.g., "book", "manuscript", "folder"
    total_pages = Column(Integer, nullable=True)
    physical_form = Column(String(100), nullable=True)  # e.g., "documento testuale", "documento cartografico"
    extent_description = Column(String(255), nullable=True)  # e.g., "c. 14 nel fascicolo", "1 volume"
    
    # Full METS XML storage
    mets_xml = Column(Text, nullable=True)  # Store complete METS XML

    # METS header information (ECO-MiC)
    record_status = Column(String(20), nullable=True, default="COMPLETE")  # "COMPLETE", "MINIMUM", "REFERENCED"

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
    file_category = Column(String(50), nullable=True)  # e.g., "master", "normalized", "export_high", "export_low", "metadata", "icc", "logs"
    file_label = Column(String(255), nullable=True)  # e.g., "Dorso", "Piatto anteriore"
    sequence_number = Column(Integer, nullable=True)  # ORDER attribute
    checksum_md5 = Column(String(32), nullable=True)
    
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
