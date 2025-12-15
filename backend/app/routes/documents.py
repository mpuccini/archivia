from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentDetail, DocumentListItem, DocumentUpload
)
from app.services.document import DocumentService
from app.services.mets_validation import METSValidationService
from app.services.mongodb import mongodb_service, get_mongodb
from app.utils.mets_generator_ecomic import METSEcoMicGenerator
from app.routes.auth import get_current_user

router = APIRouter()


class BatchDeleteRequest(BaseModel):
    document_ids: List[int]


class BatchCreateRequest(BaseModel):
    documents: List[DocumentCreate]


class BatchImportResult(BaseModel):
    success: List[dict]
    errors: List[dict]


class ImageUploadResult(BaseModel):
    success: bool
    message: str
    document_id: int = None


class BatchImageUploadResult(BaseModel):
    success: List[dict]
    errors: List[dict]
    created_documents: List[dict]


class FolderUploadResult(BaseModel):
    success: bool
    message: str
    document_id: int = None
    categorized_files: Dict[str, List[str]] = None
    total_files: int = 0


class METSValidationRequest(BaseModel):
    document_id: int


class METSValidationFromDataRequest(BaseModel):
    logical_id: str
    title: str = None
    description: str = None
    conservative_id: str = None
    conservative_id_authority: str = None
    archive_name: str = None
    archive_contact: str = None
    license_url: str = None
    rights_statement: str = None
    image_producer: str = None
    scanner_manufacturer: str = None
    scanner_model: str = None
    document_type: str = None
    total_pages: int = None
    # Additional METS fields
    date_from: str = None
    date_to: str = None
    period: str = None
    location: str = None
    language: str = None
    subjects: str = None
    fund_name: str = None
    series_name: str = None
    folder_number: str = None


class METSValidationResult(BaseModel):
    valid: bool
    response: dict
    errors: List[dict]
    summary: str


@router.post("/", response_model=DocumentDetail)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document"""
    service = DocumentService(db)
    return await service.create_document(document, current_user.id)


@router.post("/upload", response_model=DocumentDetail)
async def upload_document(
    file: UploadFile = File(...),
    logical_id: str = Form(...),
    title: str = Form(None),
    description: str = Form(None),
    conservative_id: str = Form(None),
    conservative_id_authority: str = Form(None),
    archive_name: str = Form(None),
    archive_contact: str = Form(None),
    license_url: str = Form(None),
    rights_statement: str = Form(None),
    image_producer: str = Form(None),
    scanner_manufacturer: str = Form(None),
    scanner_model: str = Form(None),
    document_type: str = Form(None),
    total_pages: int = Form(None),
    file_use: str = Form(None),
    file_label: str = Form(None),
    sequence_number: int = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document with file and metadata"""
    
    # Create document data
    document_data = DocumentUpload(
        logical_id=logical_id,
        title=title,
        description=description,
        conservative_id=conservative_id,
        conservative_id_authority=conservative_id_authority,
        archive_name=archive_name,
        archive_contact=archive_contact,
        license_url=license_url,
        rights_statement=rights_statement,
        image_producer=image_producer,
        scanner_manufacturer=scanner_manufacturer,
        scanner_model=scanner_model,
        document_type=document_type,
        total_pages=total_pages,
        file_use=file_use,
        file_label=file_label,
        sequence_number=sequence_number
    )
    
    service = DocumentService(db)
    document = await service.create_document_with_file(file, document_data, current_user.id)

    # Return detailed document
    return await service.get_document(document.id, current_user.id)


@router.get("/search")
async def search_documents(
    q: Optional[str] = Query(None, description="Full-text search query"),
    logical_id: Optional[str] = Query(None, description="Filter by logical ID (partial match)"),
    archive: Optional[str] = Query(None, description="Filter by archive name (partial match)"),
    date_from: Optional[date] = Query(None, description="Filter by start date"),
    date_to: Optional[date] = Query(None, description="Filter by end date"),
    schema_version: Optional[str] = Query(None, description="Filter by METS schema version (1.1 or 1.2)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search documents with full-text search and filters

    - **q**: Full-text search across title, description, archive, subjects, agents
    - **logical_id**: Filter by logical ID (case-insensitive partial match)
    - **archive**: Filter by archive name (case-insensitive partial match)
    - **date_from**: Filter documents from this date
    - **date_to**: Filter documents up to this date
    - **schema_version**: Filter by METS ECO-MiC version (1.1 or 1.2)
    - **page**: Page number (1-indexed)
    - **size**: Number of results per page (max 100)

    Returns paginated results with relevance scoring for text searches.
    """

    # Build filters dictionary
    filters = {}
    if logical_id:
        filters['logical_id'] = logical_id
    if archive:
        filters['archive'] = archive
    if date_from:
        filters['date_from'] = date_from.isoformat()
    if date_to:
        filters['date_to'] = date_to.isoformat()
    if schema_version:
        filters['schema_version'] = schema_version

    # Calculate skip for pagination
    skip = (page - 1) * size

    # Perform MongoDB search
    mongo_result = await mongodb_service.search_documents(
        owner_id=current_user.id,
        query=q,
        filters=filters,
        skip=skip,
        limit=size
    )

    mets_docs = mongo_result['items']
    total = mongo_result['total']

    if not mets_docs:
        return {
            "documents": [],
            "total": 0,
            "page": page,
            "size": size,
            "pages": 0
        }

    # Fetch PostgreSQL data for matched documents
    logical_ids = [doc['logical_id'] for doc in mets_docs]
    pg_docs = db.query(Document).filter(
        Document.logical_id.in_(logical_ids),
        Document.owner_id == current_user.id
    ).all()

    # Create lookup map
    pg_docs_map = {doc.logical_id: doc for doc in pg_docs}

    # Merge MongoDB metadata with PostgreSQL platform data
    results = []
    for mets_doc in mets_docs:
        pg_doc = pg_docs_map.get(mets_doc['logical_id'])
        if pg_doc:
            # Count files
            file_count = len(pg_doc.document_files) if hasattr(pg_doc, 'document_files') else 0

            results.append({
                "id": pg_doc.id,
                "logical_id": mets_doc['logical_id'],
                "title": mets_doc.get('title', ''),
                "description": mets_doc.get('description', ''),
                "conservative_id": mets_doc.get('conservative_id', ''),
                "archive_name": mets_doc.get('archive', {}).get('name', ''),
                "fund_name": mets_doc.get('archive', {}).get('fund_name', ''),
                "schema_version": mets_doc.get('schema_version', ''),
                "created_at": pg_doc.created_at,
                "updated_at": pg_doc.updated_at,
                "file_count": file_count,
                "search_score": mets_doc.get('search_score', 0) if q else None
            })

    # Calculate total pages
    total_pages = (total + size - 1) // size if total > 0 else 0

    return {
        "documents": results,
        "total": total,
        "page": page,
        "size": size,
        "pages": total_pages
    }


@router.get("/", response_model=List[DocumentListItem])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of documents"""
    service = DocumentService(db)
    return await service.get_documents(current_user.id, skip, limit)


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document"""
    service = DocumentService(db)
    document = await service.get_document(document_id, current_user.id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.put("/{document_id}", response_model=DocumentDetail)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a document"""
    service = DocumentService(db)
    document = await service.update_document(document_id, document_data, current_user.id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return await service.get_document(document.id, current_user.id)


@router.delete("/batch")
async def delete_documents_batch(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete multiple documents"""
    service = DocumentService(db)

    deleted_count = 0
    errors = []

    for document_id in request.document_ids:
        try:
            success = await service.delete_document(document_id, current_user.id)
            if success:
                deleted_count += 1
            else:
                errors.append(f"Document {document_id} not found")
        except HTTPException:
            raise  # Re-raise HTTP exceptions (404, 403, etc.)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting document {document_id}: {str(e)}", exc_info=True)
            errors.append(f"Error deleting document {document_id}")

    return {
        "message": f"Successfully deleted {deleted_count} documents",
        "deleted_count": deleted_count,
        "errors": errors if errors else None
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document"""
    service = DocumentService(db)
    success = await service.delete_document(document_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}


@router.post("/export/csv")
async def export_metadata_csv(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export metadata for multiple documents as CSV"""
    service = DocumentService(db)
    return await service.export_metadata_csv(request.document_ids, current_user.id)


# TEMPORARILY DISABLED - Needs refactoring for dual-database architecture
# @router.post("/export/mets")
# async def export_multiple_mets_xml(
#     request: BatchDeleteRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Export METS XML for multiple documents as ZIP archive"""
#     service = DocumentService(db)
#     return service.export_multiple_mets_xml(request.document_ids, current_user.id)


@router.get("/{document_id}/export/mets")
async def export_mets_xml(
    document_id: int,
    validate: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export METS XML for a document.

    Args:
        document_id: Document ID to export
        validate: Whether to validate METS against ECO-MiC 1.1 before export (default: True)

    Returns:
        METS XML file download
    """
    service = DocumentService(db)
    return await service.export_mets_xml(document_id, current_user.id, validate=validate)


@router.get("/{document_id}/export/csv")
async def export_single_document_csv(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export CSV metadata for a single document"""
    service = DocumentService(db)
    return await service.export_metadata_csv([document_id], current_user.id)


# TEMPORARILY DISABLED - Needs refactoring for dual-database architecture
# @router.get("/{document_id}/download/files")
# async def download_document_files(
#     document_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Download all files for a document as ZIP"""
#     service = DocumentService(db)
#     return service.download_document_files(document_id, current_user.id)


# TEMPORARILY DISABLED - Needs refactoring for dual-database architecture
# @router.get("/{document_id}/download/archive")
# async def download_document_archive(
#     document_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Download complete document archive (metadata + files)"""
#     service = DocumentService(db)
#     return service.download_document_archive(document_id, current_user.id)


# TEMPORARILY DISABLED - Needs refactoring for dual-database architecture
# @router.post("/download/archives")
# async def batch_download_archives(
#     request: BatchDeleteRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Download multiple documents as archives in a single ZIP"""
#     service = DocumentService(db)
#     return service.batch_download_archives(request.document_ids, current_user.id)


@router.post("/batch", response_model=BatchImportResult)
async def batch_create_documents(
    request: BatchCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple documents from batch import"""
    service = DocumentService(db)
    return await service.batch_create_documents(request.documents, current_user.id)


@router.post("/{document_id}/images", response_model=ImageUploadResult)
async def upload_document_image(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload an image for a specific document"""
    service = DocumentService(db)
    return await service.upload_document_image(document_id, file, current_user.id)


@router.post("/images/batch", response_model=BatchImageUploadResult)
async def batch_upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batch upload images, matching by filename to logical_id"""
    service = DocumentService(db)
    return await service.batch_upload_images(files, current_user.id)


@router.post("/upload-folder", response_model=FolderUploadResult)
async def upload_folder_archive(
    zip_file: UploadFile = File(...),
    logical_id: str = Form(...),
    title: str = Form(None),
    description: str = Form(None),
    conservative_id: str = Form(None),
    conservative_id_authority: str = Form(None),
    archive_name: str = Form(None),
    archive_contact: str = Form(None),
    document_type: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a ZIP archive containing a structured folder with multiple files.
    Automatically categorizes files based on ECO-MiC folder structure.
    """
    service = DocumentService(db)
    return await service.upload_folder_archive(
        zip_file=zip_file,
        logical_id=logical_id,
        title=title,
        description=description,
        conservative_id=conservative_id,
        conservative_id_authority=conservative_id_authority,
        archive_name=archive_name,
        archive_contact=archive_contact,
        document_type=document_type,
        user_id=current_user.id
    )


@router.post("/validate-mets", response_model=METSValidationResult)
async def validate_mets_xml(
    request: METSValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate METS XML for a document against ECO-MiC 1.1 standard"""
    document_service = DocumentService(db)
    validation_service = METSValidationService()

    # Get document to ensure user owns it
    document = await document_service.get_document(request.document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Generate METS XML for the document
    mets_xml = await document_service.generate_mets_xml_for_validation(request.document_id, current_user.id)

    # Validate the METS XML
    validation_result = await validation_service.validate_mets_xml(
        mets_xml,
        f"{document.logical_id}_mets.xml"
    )

    return validation_result


# DISABLED: Form validation is too expensive and provides poor UX
# See METS_VALIDATION_STRATEGY.md for rationale
# Validation now happens only on-demand (button) and on export
#
# @router.post("/validate-mets-from-data", response_model=METSValidationResult)
# async def validate_mets_xml_from_data(
#     request: METSValidationFromDataRequest,
#     current_user: User = Depends(get_current_user)
# ):
#     """Validate METS XML generated from form data against ECO-MiC 1.1 standard"""
#     from app.models.document import Document
#     from datetime import datetime
#
#     validation_service = METSValidationService()
#     mets_generator = METSEcoMicGenerator()
#
#     # Create a temporary Document object from form data for METS generation
#     now = datetime.now()
#     temp_doc = Document(
#         id=0,
#         logical_id=request.logical_id,
#         title=request.title,
#         description=request.description,
#         conservative_id=request.conservative_id,
#         conservative_id_authority=request.conservative_id_authority,
#         archive_name=request.archive_name,
#         archive_contact=request.archive_contact,
#         license_url=request.license_url,
#         rights_statement=request.rights_statement,
#         image_producer=request.image_producer,
#         scanner_manufacturer=request.scanner_manufacturer,
#         scanner_model=request.scanner_model,
#         document_type=request.document_type,
#         total_pages=request.total_pages,
#         date_from=request.date_from,
#         date_to=request.date_to,
#         period=request.period,
#         location=request.location,
#         language=request.language,
#         owner_id=current_user.id,
#         created_at=now,
#         updated_at=now,
#         document_files=[]  # No files for validation-only
#     )
#
#     # Generate METS XML using ECO-MiC 1.1 generator
#     mets_xml = mets_generator.generate_mets_xml(temp_doc)
#
#     # DEBUG: Save generated XML to temp file for inspection
#     import logging
#     logger = logging.getLogger(__name__)
#     logger.info(f"Generated METS XML (first 1000 chars): {mets_xml[:1000]}")
#
#     # Validate the METS XML
#     validation_result = await validation_service.validate_mets_xml(
#         mets_xml,
#         f"{request.logical_id}_mets.xml"
#     )
#
#     return validation_result
