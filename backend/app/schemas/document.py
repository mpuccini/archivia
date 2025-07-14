from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentFileSchema(BaseModel):
    """Schema for document file association"""
    id: int
    file_id: int
    file_use: Optional[str] = None
    file_label: Optional[str] = None
    sequence_number: Optional[int] = None
    checksum_md5: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    bits_per_sample: Optional[str] = None
    samples_per_pixel: Optional[int] = None
    date_time_created: Optional[datetime] = None
    
    # Include file information
    filename: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """Base schema for document"""
    logical_id: str = Field(..., description="Logical identifier for the document")
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
    mets_xml: Optional[str] = None


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


class DocumentDetail(DocumentBase):
    """Schema for detailed document view"""
    id: int
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
