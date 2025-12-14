"""
Pydantic schemas for METS ECO-MiC metadata (MongoDB documents)
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ArchiveInfo(BaseModel):
    """Archive hierarchy information"""
    name: Optional[str] = None
    contact: Optional[str] = None
    fund_name: Optional[str] = None
    series_name: Optional[str] = None
    folder_number: Optional[str] = None


class TemporalInfo(BaseModel):
    """Temporal metadata"""
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    period: Optional[str] = None


class AgentInfo(BaseModel):
    """Agent (producer/creator) information"""
    name: Optional[str] = None
    type: Optional[str] = None  # "corporate" or "personal"
    role: Optional[str] = None


class AgentsInfo(BaseModel):
    """Agents container"""
    producer: Optional[AgentInfo] = None
    creator: Optional[AgentInfo] = None


class RightsInfo(BaseModel):
    """Rights metadata"""
    license_url: Optional[str] = None
    rights_statement: Optional[str] = None
    category: Optional[str] = None  # "COPYRIGHTED", "PUBLIC DOMAIN", "CONTRACTUAL"
    holder: Optional[str] = None
    constraint: Optional[str] = None  # e.g., "NoC-OKLR", "InC"


class TechnicalInfo(BaseModel):
    """Document-level technical metadata"""
    image_producer: Optional[str] = None
    scanner_manufacturer: Optional[str] = None
    scanner_model: Optional[str] = None


class PhysicalInfo(BaseModel):
    """Physical structure metadata"""
    document_type: Optional[str] = None
    total_pages: Optional[int] = None
    physical_form: Optional[str] = None
    extent_description: Optional[str] = None


class METSHeader(BaseModel):
    """METS header information"""
    record_status: str = "COMPLETE"  # "COMPLETE", "MINIMUM", "REFERENCED"
    profile: str = "http://www.iccu.sbn.it/metaAG1.pdf"


class METSDocumentBase(BaseModel):
    """Base METS document schema"""
    # Schema version
    schema_version: str = Field(default="1.1", description="ECO-MiC version: 1.1 or 1.2")

    # Core identifiers
    logical_id: str = Field(..., description="Unique logical identifier")
    conservative_id: Optional[str] = Field(None, description="Physical archive identifier")
    conservative_id_authority: Optional[str] = Field(None, description="ISIL authority code")

    # Descriptive metadata
    title: Optional[str] = None
    description: Optional[str] = None
    type_of_resource: Optional[str] = Field(None, description="ECO-MiC resource type")

    # Structured metadata
    archive: Optional[ArchiveInfo] = None
    temporal: Optional[TemporalInfo] = None
    agents: Optional[AgentsInfo] = None
    rights: Optional[RightsInfo] = None
    technical: Optional[TechnicalInfo] = None
    physical: Optional[PhysicalInfo] = None
    mets_header: Optional[METSHeader] = None

    # Geographic and contextual
    location: Optional[str] = None
    language: Optional[str] = None
    subjects: Optional[List[str]] = Field(default_factory=list)


class METSDocumentCreate(METSDocumentBase):
    """Schema for creating METS document"""
    pass


class METSDocumentUpdate(BaseModel):
    """Schema for updating METS document (all fields optional)"""
    # Core identifiers
    conservative_id: Optional[str] = None
    conservative_id_authority: Optional[str] = None

    # Descriptive metadata
    title: Optional[str] = None
    description: Optional[str] = None
    type_of_resource: Optional[str] = None

    # Structured metadata
    archive: Optional[ArchiveInfo] = None
    temporal: Optional[TemporalInfo] = None
    agents: Optional[AgentsInfo] = None
    rights: Optional[RightsInfo] = None
    technical: Optional[TechnicalInfo] = None
    physical: Optional[PhysicalInfo] = None
    mets_header: Optional[METSHeader] = None

    # Geographic and contextual
    location: Optional[str] = None
    language: Optional[str] = None
    subjects: Optional[List[str]] = None


class METSDocumentResponse(METSDocumentBase):
    """Schema for METS document response"""
    # MongoDB fields
    id: str = Field(..., alias="_id", description="MongoDB ObjectId")

    # Platform references
    platform_document_id: int = Field(..., description="PostgreSQL document.id")
    owner_id: int = Field(..., description="User ID")

    # Audit fields
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class METSMetadataExtract(BaseModel):
    """
    Helper schema for extracting METS metadata from legacy document data

    Used during migration/refactoring when receiving old-style flat document data
    """
    # All METS fields as optional for flexible extraction
    conservative_id: Optional[str] = None
    conservative_id_authority: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    type_of_resource: Optional[str] = None

    # Archive (flat structure for input)
    archive_name: Optional[str] = None
    archive_contact: Optional[str] = None
    fund_name: Optional[str] = None
    series_name: Optional[str] = None
    folder_number: Optional[str] = None

    # Temporal (flat)
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    period: Optional[str] = None

    # Location/Context
    location: Optional[str] = None
    language: Optional[str] = None
    subjects: Optional[str] = None  # Will be split into list

    # Agents (flat)
    producer_name: Optional[str] = None
    producer_type: Optional[str] = None
    producer_role: Optional[str] = None
    creator_name: Optional[str] = None
    creator_type: Optional[str] = None
    creator_role: Optional[str] = None

    # Rights (flat)
    license_url: Optional[str] = None
    rights_statement: Optional[str] = None
    rights_category: Optional[str] = None
    rights_holder: Optional[str] = None
    rights_constraint: Optional[str] = None

    # Technical (flat)
    image_producer: Optional[str] = None
    scanner_manufacturer: Optional[str] = None
    scanner_model: Optional[str] = None

    # Physical (flat)
    document_type: Optional[str] = None
    total_pages: Optional[int] = None
    physical_form: Optional[str] = None
    extent_description: Optional[str] = None

    # METS header
    record_status: Optional[str] = "COMPLETE"
