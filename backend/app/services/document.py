import csv
import hashlib
import io
import os
import tempfile
import zipfile
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.document import Document, DocumentFile
from app.models.file import File
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentListItem, DocumentDetail, DocumentUpload
from app.services.file import FileService
from app.services.minio import MinIOService


class DocumentService:
    """Service for document management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()
        self.minio_service = MinIOService()
    
    def create_document(self, document_data: DocumentCreate, user_id: int) -> Document:
        """Create a new document"""
        # Check if logical_id already exists
        existing = self.db.query(Document).filter(
            Document.logical_id == document_data.logical_id,
            Document.owner_id == user_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Document with logical_id '{document_data.logical_id}' already exists"
            )
        
        document = Document(
            **document_data.dict(),
            owner_id=user_id
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    async def create_document_with_file(
        self, 
        file: UploadFile, 
        document_data: DocumentUpload, 
        user_id: int
    ) -> Document:
        """Create a new document with associated file"""
        # First create the document
        doc_create = DocumentCreate(**document_data.dict())
        document = self.create_document(doc_create, user_id)
        
        try:
            # Create a temporary file to simulate the upload process
            # In a real scenario, we would handle the file upload differently
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(await file.read())
                tmp_file.flush()
                
                # Create file record manually
                from app.models.file import File
                minio_object_name = self.minio_service.generate_object_name(file.filename)
                uploaded_file = File(
                    filename=file.filename,
                    original_filename=file.filename,
                    file_size=file.size,
                    content_type=file.content_type,
                    owner_id=user_id,
                    file_hash=hashlib.md5(open(tmp_file.name, 'rb').read()).hexdigest(),
                    minio_object_name=minio_object_name,
                    bucket_name=settings.MINIO_BUCKET_NAME,
                    upload_completed=True
                )
                
                self.db.add(uploaded_file)
                self.db.commit()
                self.db.refresh(uploaded_file)
                
                # Upload to MinIO
                with open(tmp_file.name, 'rb') as f:
                    self.minio_service.client.put_object(
                        bucket_name=settings.MINIO_BUCKET_NAME,
                        object_name=uploaded_file.minio_object_name,
                        data=f,
                        length=file.size,
                        content_type=file.content_type
                    )
                
                # Clean up temp file
                os.unlink(tmp_file.name)
            
            # Create document-file association
            doc_file = DocumentFile(
                document_id=document.id,
                file_id=uploaded_file.id,
                file_use=document_data.file_use,
                file_label=document_data.file_label,
                sequence_number=document_data.sequence_number,
                checksum_md5=uploaded_file.file_hash
            )
            
            self.db.add(doc_file)
            self.db.commit()
            
            return document
            
        except Exception as e:
            # If file upload fails, delete the document
            self.db.delete(document)
            self.db.commit()
            raise e
    
    def get_documents(self, user_id: int, skip: int = 0, limit: int = 100) -> List[DocumentListItem]:
        """Get list of documents for a user"""
        query = self.db.query(
            Document.id,
            Document.logical_id,
            Document.title,
            Document.archive_name,
            Document.document_type,
            Document.total_pages,
            Document.created_at,
            func.count(DocumentFile.id).label('file_count')
        ).outerjoin(
            DocumentFile, Document.id == DocumentFile.document_id
        ).filter(
            Document.owner_id == user_id
        ).group_by(
            Document.id
        ).order_by(
            Document.created_at.desc()
        ).offset(skip).limit(limit)
        
        results = query.all()
        
        return [
            DocumentListItem(
                id=row.id,
                logical_id=row.logical_id,
                title=row.title,
                archive_name=row.archive_name,
                document_type=row.document_type,
                total_pages=row.total_pages,
                created_at=row.created_at,
                file_count=row.file_count
            )
            for row in results
        ]
    
    async def get_document(self, document_id: int, user_id: int) -> Optional[DocumentDetail]:
        """Get a specific document with files"""
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            return None
        
        # Convert to schema
        document_files = []
        for doc_file in document.document_files:
            file_data = {
                'id': doc_file.id,
                'file_id': doc_file.file_id,
                'file_use': doc_file.file_use,
                'file_label': doc_file.file_label,
                'sequence_number': doc_file.sequence_number,
                'checksum_md5': doc_file.checksum_md5,
                'image_width': doc_file.image_width,
                'image_height': doc_file.image_height,
                'bits_per_sample': doc_file.bits_per_sample,
                'samples_per_pixel': doc_file.samples_per_pixel,
                'date_time_created': doc_file.date_time_created,
                'filename': doc_file.file.filename,
                'file_size': doc_file.file.file_size,
                'content_type': doc_file.file.content_type
            }
            document_files.append(file_data)
        
        return DocumentDetail(
            id=document.id,
            logical_id=document.logical_id,
            conservative_id=document.conservative_id,
            conservative_id_authority=document.conservative_id_authority,
            title=document.title,
            description=document.description,
            archive_name=document.archive_name,
            archive_contact=document.archive_contact,
            license_url=document.license_url,
            rights_statement=document.rights_statement,
            image_producer=document.image_producer,
            scanner_manufacturer=document.scanner_manufacturer,
            scanner_model=document.scanner_model,
            document_type=document.document_type,
            total_pages=document.total_pages,
            mets_xml=document.mets_xml,
            owner_id=document.owner_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            document_files=document_files
        )
    
    def update_document(self, document_id: int, document_data: DocumentUpdate, user_id: int) -> Optional[Document]:
        """Update a document"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            return None
        
        # Update fields
        for field, value in document_data.dict(exclude_unset=True).items():
            setattr(document, field, value)
        
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete a document and its associated files"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            return False
        
        # Delete files from MinIO
        for doc_file in document.document_files:
            try:
                self.minio_service.delete_file(doc_file.file.minio_object_name)
            except Exception as e:
                print(f"Error deleting file from MinIO: {e}")
        
        # Delete document (cascade will handle document_files and files)
        self.db.delete(document)
        self.db.commit()
        return True
    
    def export_metadata_csv(self, document_ids: List[int], user_id: int) -> StreamingResponse:
        """Export metadata for multiple documents as CSV"""
        documents = self.db.query(Document).filter(
            Document.id.in_(document_ids),
            Document.owner_id == user_id
        ).all()
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'logical_id', 'title', 'description', 'archive_name', 'document_type',
            'total_pages', 'conservative_id', 'license_url', 'rights_statement',
            'image_producer', 'scanner_manufacturer', 'scanner_model', 'created_at'
        ])
        
        # Write data
        for doc in documents:
            writer.writerow([
                doc.logical_id, doc.title, doc.description, doc.archive_name,
                doc.document_type, doc.total_pages, doc.conservative_id,
                doc.license_url, doc.rights_statement, doc.image_producer,
                doc.scanner_manufacturer, doc.scanner_model, doc.created_at
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=documents_metadata.csv"}
        )
    
    def export_mets_xml(self, document_id: int, user_id: int) -> StreamingResponse:
        """Export METS XML for a single document"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.mets_xml:
            raise HTTPException(status_code=404, detail="METS XML not available for this document")
        
        return StreamingResponse(
            io.BytesIO(document.mets_xml.encode()),
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={document.logical_id}_mets.xml"}
        )
    
    def download_document_files(self, document_id: int, user_id: int) -> StreamingResponse:
        """Download all files for a document as ZIP"""
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.document_files:
            raise HTTPException(status_code=404, detail="No files found for this document")
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for doc_file in document.document_files:
                try:
                    # Get file from MinIO
                    file_data = self.minio_service.get_file(doc_file.file.minio_object_name)
                    
                    # Add to ZIP
                    zip_file.writestr(doc_file.file.filename, file_data.read())
                except Exception as e:
                    print(f"Error adding file to ZIP: {e}")
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={document.logical_id}_files.zip"}
        )
    
    def download_document_archive(self, document_id: int, user_id: int) -> StreamingResponse:
        """Download complete document archive (metadata + files)"""
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add metadata CSV
            metadata_csv = io.StringIO()
            writer = csv.writer(metadata_csv)
            writer.writerow(['field', 'value'])
            
            for field in ['logical_id', 'title', 'description', 'archive_name', 'document_type',
                         'total_pages', 'conservative_id', 'license_url', 'rights_statement',
                         'image_producer', 'scanner_manufacturer', 'scanner_model']:
                value = getattr(document, field)
                if value:
                    writer.writerow([field, value])
            
            zip_file.writestr('metadata.csv', metadata_csv.getvalue())
            
            # Add METS XML if available
            if document.mets_xml:
                zip_file.writestr('mets.xml', document.mets_xml)
            
            # Add files
            for doc_file in document.document_files:
                try:
                    file_data = self.minio_service.get_file(doc_file.file.minio_object_name)
                    zip_file.writestr(f"files/{doc_file.file.filename}", file_data.read())
                except Exception as e:
                    print(f"Error adding file to ZIP: {e}")
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={document.logical_id}_complete.zip"}
        )
    
    def batch_download_archives(self, document_ids: List[int], user_id: int) -> StreamingResponse:
        """Download multiple documents as separate archives in a single ZIP"""
        documents = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id.in_(document_ids),
            Document.owner_id == user_id
        ).all()
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Create main ZIP
        main_zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(main_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as main_zip:
            for document in documents:
                # Create individual document ZIP
                doc_zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(doc_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as doc_zip:
                    # Add metadata
                    metadata_csv = io.StringIO()
                    writer = csv.writer(metadata_csv)
                    writer.writerow(['field', 'value'])
                    
                    for field in ['logical_id', 'title', 'description', 'archive_name', 'document_type',
                                 'total_pages', 'conservative_id', 'license_url', 'rights_statement',
                                 'image_producer', 'scanner_manufacturer', 'scanner_model']:
                        value = getattr(document, field)
                        if value:
                            writer.writerow([field, value])
                    
                    doc_zip.writestr('metadata.csv', metadata_csv.getvalue())
                    
                    # Add METS XML if available
                    if document.mets_xml:
                        doc_zip.writestr('mets.xml', document.mets_xml)
                    
                    # Add files
                    for doc_file in document.document_files:
                        try:
                            file_data = self.minio_service.get_file(doc_file.file.minio_object_name)
                            doc_zip.writestr(f"files/{doc_file.file.filename}", file_data.read())
                        except Exception as e:
                            print(f"Error adding file to ZIP: {e}")
                
                # Add document ZIP to main ZIP
                main_zip.writestr(f"{document.logical_id}.zip", doc_zip_buffer.getvalue())
        
        main_zip_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(main_zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=documents_batch.zip"}
        )
