from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, HttpUrl
import re


class DocumentFileSchema(BaseModel):
    """Schema for document file association"""
    id: int
    file_id: int
    file_use: Optional[str] = None
    file_category: Optional[str] = None
    file_label: Optional[str] = None
    sequence_number: Optional[int] = None
    checksum_md5: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    bits_per_sample: Optional[str] = None
    samples_per_pixel: Optional[int] = None
    date_time_created: Optional[datetime] = None

    # Enhanced technical metadata (ECO-MiC / MIX)
    compression_scheme: Optional[str] = None
    color_space: Optional[str] = None
    sampling_frequency_unit: Optional[str] = None
    x_sampling_frequency: Optional[int] = None
    y_sampling_frequency: Optional[int] = None
    format_name: Optional[str] = None
    byte_order: Optional[str] = None
    orientation: Optional[str] = None
    icc_profile_name: Optional[str] = None

    # Camera/Scanner metadata
    scanner_manufacturer: Optional[str] = None
    scanner_model_name: Optional[str] = None
    scanning_software_name: Optional[str] = None
    scanning_software_version: Optional[str] = None

    # Complete DNG/EXIF metadata (all extracted tags)
    raw_metadata: Optional[Dict[str, Any]] = None

    # Include file information
    filename: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """Base schema for document"""
    logical_id: str = Field(
        ...,
        description="Logical identifier for the document",
        min_length=1,
        max_length=255,
        pattern=r'^[a-zA-Z0-9_\-\.]+$'
    )
    conservative_id: Optional[str] = Field(None, max_length=255)
    conservative_id_authority: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)

    # Archive information
    archive_name: Optional[str] = Field(None, max_length=255)
    archive_contact: Optional[str] = Field(None, max_length=500)
    fund_name: Optional[str] = Field(None, max_length=255)
    series_name: Optional[str] = Field(None, max_length=255)
    folder_number: Optional[str] = Field(None, max_length=100)

    # Temporal information
    date_from: Optional[str] = Field(None, max_length=50)
    date_to: Optional[str] = Field(None, max_length=50)
    period: Optional[str] = Field(None, max_length=255)

    # Geographic and contextual information
    location: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=100)
    subjects: Optional[str] = Field(None, max_length=1000)

    # ECO-MiC typeOfResource
    type_of_resource: Optional[str] = Field(None, max_length=100)  # e.g., "risorsa manoscritta"

    # Corporate and personal names (ECO-MiC)
    producer_name: Optional[str] = Field(None, max_length=255)
    producer_type: Optional[str] = Field(None, max_length=20)  # "corporate" or "personal"
    producer_role: Optional[str] = Field(None, max_length=100)
    creator_name: Optional[str] = Field(None, max_length=255)
    creator_type: Optional[str] = Field(None, max_length=20)  # "corporate" or "personal"
    creator_role: Optional[str] = Field(None, max_length=100)

    # Rights information (ECO-MiC)
    license_url: Optional[str] = Field(None, max_length=500)
    rights_statement: Optional[str] = Field(None, max_length=1000)
    rights_category: Optional[str] = Field(None, max_length=50)  # e.g., "COPYRIGHTED"
    rights_holder: Optional[str] = Field(None, max_length=255)
    rights_constraint: Optional[str] = Field(None, max_length=100)  # e.g., "NoC-OKLR"

    # Technical metadata
    image_producer: Optional[str] = Field(None, max_length=255)
    scanner_manufacturer: Optional[str] = Field(None, max_length=255)
    scanner_model: Optional[str] = Field(None, max_length=255)

    # Physical structure (ECO-MiC)
    document_type: Optional[str] = Field(None, max_length=100)
    total_pages: Optional[int] = Field(None, ge=1, le=10000)
    physical_form: Optional[str] = Field(None, max_length=100)  # e.g., "documento testuale"
    extent_description: Optional[str] = Field(None, max_length=255)  # e.g., "c. 14 nel fascicolo"

    # METS header
    record_status: Optional[str] = Field("COMPLETE", max_length=20)  # "COMPLETE", "MINIMUM", "REFERENCED"

    mets_xml: Optional[str] = None

    @field_validator('license_url')
    @classmethod
    def validate_license_url(cls, v):
        """Validate license URL format"""
        if v and v.strip():
            # Basic URL validation
            if not re.match(r'^https?://', v):
                raise ValueError('License URL must start with http:// or https://')
            if len(v) > 500:
                raise ValueError('License URL too long')
        return v

    @field_validator('total_pages')
    @classmethod
    def validate_total_pages(cls, v):
        """Validate total pages is positive"""
        if v is not None and v < 1:
            raise ValueError('Total pages must be at least 1')
        return v


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    logical_id: Optional[str] = None
    conservative_id: Optional[str] = None
    conservative_id_authority: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

    # Archive information
    archive_name: Optional[str] = None
    archive_contact: Optional[str] = None
    fund_name: Optional[str] = None
    series_name: Optional[str] = None
    folder_number: Optional[str] = None

    # Temporal information
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    period: Optional[str] = None

    # Geographic and contextual information
    location: Optional[str] = None
    language: Optional[str] = None
    subjects: Optional[str] = None

    # ECO-MiC typeOfResource
    type_of_resource: Optional[str] = None

    # Corporate and personal names (ECO-MiC)
    producer_name: Optional[str] = None
    producer_type: Optional[str] = None
    producer_role: Optional[str] = None
    creator_name: Optional[str] = None
    creator_type: Optional[str] = None
    creator_role: Optional[str] = None

    # Rights information (ECO-MiC)
    license_url: Optional[str] = None
    rights_statement: Optional[str] = None
    rights_category: Optional[str] = None
    rights_holder: Optional[str] = None
    rights_constraint: Optional[str] = None

    # Technical metadata
    image_producer: Optional[str] = None
    scanner_manufacturer: Optional[str] = None
    scanner_model: Optional[str] = None

    # Physical structure (ECO-MiC)
    document_type: Optional[str] = None
    total_pages: Optional[int] = None
    physical_form: Optional[str] = None
    extent_description: Optional[str] = None

    # METS header
    record_status: Optional[str] = None

    mets_xml: Optional[str] = None


class DocumentListItem(BaseModel):
    """Schema for document list view"""
    id: int
    logical_id: str
    title: Optional[str] = None
    archive_name: Optional[str] = None
    document_type: Optional[str] = None
    total_pages: Optional[int] = None
    created_at: datetime
    file_count: int = 0
    
    class Config:
        from_attributes = True


class DocumentDetail(BaseModel):
    """Schema for detailed document view"""
    id: int
    logical_id: str
    conservative_id: Optional[str] = None
    conservative_id_authority: Optional[str] = None
    title: Optional[str] = None  # Allow empty/None for existing documents
    description: Optional[str] = None

    # Archive information
    archive_name: Optional[str] = None
    archive_contact: Optional[str] = None
    fund_name: Optional[str] = None
    series_name: Optional[str] = None
    folder_number: Optional[str] = None

    # Temporal information
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    period: Optional[str] = None

    # Geographic and contextual information
    location: Optional[str] = None
    language: Optional[str] = None
    subjects: Optional[str] = None

    # ECO-MiC typeOfResource
    type_of_resource: Optional[str] = None

    # Corporate and personal names (ECO-MiC)
    producer_name: Optional[str] = None
    producer_type: Optional[str] = None
    producer_role: Optional[str] = None
    creator_name: Optional[str] = None
    creator_type: Optional[str] = None
    creator_role: Optional[str] = None

    # Rights information (ECO-MiC)
    license_url: Optional[str] = None
    rights_statement: Optional[str] = None
    rights_category: Optional[str] = None
    rights_holder: Optional[str] = None
    rights_constraint: Optional[str] = None

    # Technical metadata
    image_producer: Optional[str] = None
    scanner_manufacturer: Optional[str] = None
    scanner_model: Optional[str] = None

    # Physical structure (ECO-MiC)
    document_type: Optional[str] = None
    total_pages: Optional[int] = None
    physical_form: Optional[str] = None
    extent_description: Optional[str] = None

    # METS header
    record_status: Optional[str] = None

    mets_xml: Optional[str] = None

    owner_id: int
    created_at: datetime
    updated_at: datetime
    document_files: List[DocumentFileSchema] = []

    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    """Schema for document upload with metadata"""
    # Basic required fields
    logical_id: Optional[str] = Field(None, description="Logical identifier for the document (auto-filled from filename if not provided)")
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Optional metadata fields
    conservative_id: Optional[str] = None
    conservative_id_authority: Optional[str] = None
    
    # Archive information
    archive_name: Optional[str] = None
    archive_contact: Optional[str] = None
    fund_name: Optional[str] = None
    series_name: Optional[str] = None
    folder_number: Optional[str] = None
    
    # Temporal information
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    period: Optional[str] = None
    
    # Geographic and contextual information
    location: Optional[str] = None
    language: Optional[str] = None
    subjects: Optional[str] = None
    
    # Rights information
    license_url: Optional[str] = None
    rights_statement: Optional[str] = None
    
    # Technical metadata
    image_producer: Optional[str] = None
    scanner_manufacturer: Optional[str] = None
    scanner_model: Optional[str] = None
    
    # Physical structure
    document_type: Optional[str] = None
    total_pages: Optional[int] = None
    
    # File metadata
    file_use: Optional[str] = None
    file_label: Optional[str] = None
    sequence_number: Optional[int] = None
