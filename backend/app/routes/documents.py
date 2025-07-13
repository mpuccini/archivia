from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentDetail, DocumentListItem, DocumentUpload
)
from app.services.document import DocumentService
from app.routes.auth import get_current_user

router = APIRouter()


class BatchDeleteRequest(BaseModel):
    document_ids: List[int]


@router.post("/", response_model=DocumentDetail)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document"""
    service = DocumentService(db)
    return service.create_document(document, current_user.id)


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
    return service.get_document(document.id, current_user.id)


@router.get("/", response_model=List[DocumentListItem])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of documents"""
    service = DocumentService(db)
    return service.get_documents(current_user.id, skip, limit)


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document"""
    service = DocumentService(db)
    document = service.get_document(document_id, current_user.id)
    
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
    document = service.update_document(document_id, document_data, current_user.id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return service.get_document(document.id, current_user.id)


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
            success = service.delete_document(document_id, current_user.id)
            if success:
                deleted_count += 1
            else:
                errors.append(f"Document {document_id} not found")
        except Exception as e:
            errors.append(f"Error deleting document {document_id}: {str(e)}")
    
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
    success = service.delete_document(document_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}


@router.post("/export/csv")
async def export_metadata_csv(
    document_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export metadata for multiple documents as CSV"""
    service = DocumentService(db)
    return service.export_metadata_csv(document_ids, current_user.id)


@router.post("/export/mets")
async def export_multiple_mets_xml(
    document_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export METS XML for multiple documents as ZIP archive"""
    service = DocumentService(db)
    return service.export_multiple_mets_xml(document_ids, current_user.id)


@router.get("/{document_id}/export/mets")
async def export_mets_xml(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export METS XML for a document"""
    service = DocumentService(db)
    return service.export_mets_xml(document_id, current_user.id)


@router.get("/{document_id}/export/csv")
async def export_single_document_csv(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export CSV metadata for a single document"""
    service = DocumentService(db)
    return service.export_metadata_csv([document_id], current_user.id)


@router.get("/{document_id}/download/files")
async def download_document_files(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download all files for a document as ZIP"""
    service = DocumentService(db)
    return service.download_document_files(document_id, current_user.id)


@router.get("/{document_id}/download/archive")
async def download_document_archive(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download complete document archive (metadata + files)"""
    service = DocumentService(db)
    return service.download_document_archive(document_id, current_user.id)


@router.post("/download/batch")
async def batch_download_archives(
    document_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download multiple documents as archives in a single ZIP"""
    service = DocumentService(db)
    return service.batch_download_archives(document_ids, current_user.id)
