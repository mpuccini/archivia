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
from app.utils.mets_generator import METSGenerator


class DocumentService:
    """Service for document management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()
        self.minio_service = MinIOService()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be safe for use as a filename"""
        import re
        # Replace invalid characters with underscores
        # Keep alphanumeric, hyphens, underscores, and dots
        sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
        # Remove any leading/trailing dots or spaces
        sanitized = sanitized.strip('. ')
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized if sanitized else 'document'
    
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
        # Auto-generate logical_id from filename if not provided
        if not document_data.logical_id or document_data.logical_id.strip() == "":
            # Use filename without extension as logical_id
            filename_without_ext = os.path.splitext(file.filename)[0]
            document_data.logical_id = filename_without_ext
        
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
    
    def get_document(self, document_id: int, user_id: int) -> Optional[DocumentDetail]:
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
            # Basic identification
            'logical_id', 'title', 'description', 'conservative_id', 'conservative_id_authority',
            # Archive information
            'archive_name', 'archive_contact', 'fund_name', 'series_name', 'folder_number',
            # Temporal information
            'date_from', 'date_to', 'period',
            # Geographic and contextual information
            'location', 'language', 'subjects',
            # Document structure
            'document_type', 'total_pages',
            # Rights information
            'license_url', 'rights_statement',
            # Technical metadata
            'image_producer', 'scanner_manufacturer', 'scanner_model',
            # System fields
            'created_at'
        ])
        
        # Write data
        for doc in documents:
            writer.writerow([
                # Basic identification
                doc.logical_id, doc.title, doc.description, doc.conservative_id, doc.conservative_id_authority,
                # Archive information
                doc.archive_name, doc.archive_contact, doc.fund_name, doc.series_name, doc.folder_number,
                # Temporal information
                doc.date_from, doc.date_to, doc.period,
                # Geographic and contextual information
                doc.location, doc.language, doc.subjects,
                # Document structure
                doc.document_type, doc.total_pages,
                # Rights information
                doc.license_url, doc.rights_statement,
                # Technical metadata
                doc.image_producer, doc.scanner_manufacturer, doc.scanner_model,
                # System fields
                doc.created_at
            ])
        
        # Generate filename using logical IDs
        if len(documents) == 1:
            # Sanitize logical_id for filename (remove/replace invalid characters)
            safe_logical_id = self._sanitize_filename(documents[0].logical_id)
            filename = f"{safe_logical_id}_metadata.csv"
        else:
            # For multiple documents, use a generic name or first logical_id + count
            filename = f"documents_metadata_{len(documents)}_items.csv"
        
        # Create proper BytesIO stream
        csv_content = output.getvalue()
        csv_bytes = io.BytesIO(csv_content.encode('utf-8'))
        
        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    def export_mets_xml(self, document_id: int, user_id: int) -> StreamingResponse:
        """Export dynamically generated METS XML for a single document"""
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate METS XML dynamically from database data
        mets_generator = METSGenerator()
        mets_xml = mets_generator.generate_mets_xml(document)
        
        return StreamingResponse(
            io.BytesIO(mets_xml.encode('utf-8')),
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={document.logical_id}_mets.xml"}
        )
    
    def export_multiple_mets_xml(self, document_ids: List[int], user_id: int) -> StreamingResponse:
        """Export dynamically generated METS XML for multiple documents as ZIP archive"""
        documents = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id.in_(document_ids),
            Document.owner_id == user_id
        ).all()
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Generate METS XML for all documents
        mets_generator = METSGenerator()
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for document in documents:
                try:
                    mets_xml = mets_generator.generate_mets_xml(document)
                    filename = f"{document.logical_id}_mets.xml"
                    zip_file.writestr(filename, mets_xml.encode('utf-8'))
                except Exception as e:
                    # Log error but continue with other documents
                    print(f"Error generating METS for document {document.id}: {e}")
                    continue
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=documents_mets.zip"}
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
            
            # Generate and add METS XML
            try:
                mets_generator = METSGenerator()
                # Convert database document to DocumentDetail format for METS generator
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

                document_detail = DocumentDetail(
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
                
                mets_xml = mets_generator.generate_mets_xml(document_detail)
                zip_file.writestr('mets.xml', mets_xml)
            except Exception as e:
                print(f"Error generating METS XML: {e}")
                import traceback
                traceback.print_exc()
            
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
                    
                    # Generate and add METS XML
                    try:
                        mets_generator = METSGenerator()
                        # Convert database document to DocumentDetail format for METS generator
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

                        document_detail = DocumentDetail(
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
                        
                        mets_xml = mets_generator.generate_mets_xml(document_detail)
                        doc_zip.writestr('mets.xml', mets_xml)
                    except Exception as e:
                        print(f"Error generating METS XML: {e}")
                        import traceback
                        traceback.print_exc()
                    
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
    
    async def batch_create_documents(self, documents_data: List[DocumentCreate], user_id: int) -> dict:
        """Create multiple documents from batch import"""
        success = []
        errors = []
        
        for doc_data in documents_data:
            try:
                # Check if logical_id already exists
                existing = self.db.query(Document).filter(
                    Document.logical_id == doc_data.logical_id,
                    Document.owner_id == user_id
                ).first()
                
                if existing:
                    errors.append({
                        "logical_id": doc_data.logical_id,
                        "error": f"Document with logical_id '{doc_data.logical_id}' already exists"
                    })
                    continue
                
                # Create the document
                document = self.create_document(doc_data, user_id)
                success.append({
                    "logical_id": document.logical_id,
                    "title": document.title,
                    "id": document.id
                })
                
            except Exception as e:
                errors.append({
                    "logical_id": doc_data.logical_id if hasattr(doc_data, 'logical_id') else 'unknown',
                    "error": str(e)
                })
        
        return {
            "success": success,
            "errors": errors
        }
    
    async def upload_document_image(self, document_id: int, file: UploadFile, user_id: int) -> dict:
        """Upload an image for a specific document"""
        # Check if document exists and belongs to user
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Validate file type
        valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'application/pdf']
        valid_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.pdf']
        
        if (file.content_type not in valid_types and 
            not any(file.filename.lower().endswith(ext) for ext in valid_extensions)):
            raise HTTPException(status_code=400, detail="Invalid file type. Supported: JPG, PNG, TIFF, PDF")
        
        try:
            # Upload file to storage
            uploaded_file = await self.file_service.upload_file(file, user_id)
            
            # Link file to document
            document_file = DocumentFile(
                document_id=document.id,
                file_id=uploaded_file.id,
                file_use="master",  # Assuming images are master files
                sequence_number=1
            )
            
            self.db.add(document_file)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Image uploaded successfully for document {document.logical_id}",
                "document_id": document.id
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
    
    async def batch_upload_images(self, files: List[UploadFile], user_id: int) -> dict:
        """Batch upload images, matching by filename to logical_id"""
        success = []
        errors = []
        created_documents = []
        
        for file in files:
            try:
                # Extract logical_id from filename (remove extension)
                logical_id = os.path.splitext(file.filename)[0]
                
                # Check if document with this logical_id exists
                document = self.db.query(Document).filter(
                    Document.logical_id == logical_id,
                    Document.owner_id == user_id
                ).first()
                
                # If document doesn't exist, create a minimal one
                if not document:
                    try:
                        doc_data = DocumentCreate(
                            logical_id=logical_id,
                            title=f"Document {logical_id}",
                            description=f"Auto-created document for image {file.filename}"
                        )
                        document = self.create_document(doc_data, user_id)
                        created_documents.append({
                            "logical_id": logical_id,
                            "id": document.id
                        })
                    except Exception as e:
                        errors.append({
                            "filename": file.filename,
                            "logical_id": logical_id,
                            "error": f"Failed to create document: {str(e)}"
                        })
                        continue
                
                # Upload the image
                result = await self.upload_document_image(document.id, file, user_id)
                success.append({
                    "filename": file.filename,
                    "logical_id": logical_id,
                    "document_id": document.id
                })
                
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "logical_id": logical_id if 'logical_id' in locals() else 'unknown',
                    "error": str(e)
                })
        
        return {
            "success": success,
            "errors": errors,
            "created_documents": created_documents
        }
