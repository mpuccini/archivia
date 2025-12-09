import csv
import hashlib
import io
import logging
import os
import tempfile
import zipfile
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.models.document import Document, DocumentFile
from app.models.file import File
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentListItem, DocumentDetail, DocumentUpload
from app.services.file import FileService
from app.services.minio import MinIOService
from app.utils.mets_generator_ecomic import METSEcoMicGenerator
from app.utils.file_validator import validate_file_type_and_size, validate_filename
from app.utils.image_metadata import extract_image_metadata
from app.utils.file_categorizer import FileCategorizer


class DocumentService:
    """Service for document management"""

    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()
        self.minio_service = MinIOService()

    def _convert_to_document_detail(self, document: Document) -> DocumentDetail:
        """Convert Document ORM model to DocumentDetail schema"""
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
            fund_name=document.fund_name,
            series_name=document.series_name,
            folder_number=document.folder_number,
            date_from=document.date_from,
            date_to=document.date_to,
            period=document.period,
            location=document.location,
            language=document.language,
            subjects=document.subjects,
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

    def _add_document_to_zip(self, zip_file: zipfile.ZipFile, document: Document, include_metadata: bool = True) -> None:
        """Add document metadata, METS, and files to a ZIP archive"""
        # Add metadata CSV
        if include_metadata:
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
            mets_generator = METSEcoMicGenerator()
            document_detail = self._convert_to_document_detail(document)
            mets_xml = mets_generator.generate_mets_xml(document_detail)
            zip_file.writestr('mets.xml', mets_xml)
        except Exception as e:
            logger.error(f"Error generating METS XML for document {document.id}: {e}", exc_info=True)

        # Add files
        for doc_file in document.document_files:
            try:
                file_data = self.minio_service.get_file(doc_file.file.minio_object_name)
                zip_file.writestr(f"files/{doc_file.file.filename}", file_data.read())
            except Exception as e:
                logger.error(f"Error adding file to ZIP: {e}", exc_info=True)

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

    def _make_content_disposition(self, filename: str, disposition_type: str = "attachment") -> str:
        """
        Create a safe Content-Disposition header value.

        Args:
            filename: The filename to include in the header
            disposition_type: Either 'attachment' or 'inline'

        Returns:
            Properly formatted Content-Disposition header value
        """
        import re
        # Sanitize filename for safety
        safe_filename = self._sanitize_filename(filename)

        # Use RFC 5987 encoding for non-ASCII characters
        # Quote the filename to handle spaces and special chars
        return f'{disposition_type}; filename="{safe_filename}"'

    def _is_image_file(self, content_type: Optional[str]) -> bool:
        """Check if the file is an image based on content type"""
        if not content_type:
            return False
        image_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/tiff',
            'image/tif', 'image/x-adobe-dng', 'image/dng', 'image/bmp',
            'image/gif', 'image/webp'
        ]
        return content_type.lower() in image_types

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
        
        # Create temporary file with proper cleanup
        import tempfile
        tmp_file_path = None
        try:
            # Create a temporary file to simulate the upload process
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file_path = tmp_file.name

                # Write file in chunks to avoid loading entire file into memory
                await file.seek(0)
                chunk_size = settings.STREAMING_CHUNK_SIZE
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    tmp_file.write(chunk)
                tmp_file.flush()

                # Calculate hash using chunked reading
                file_hash_obj = hashlib.md5()
                with open(tmp_file_path, 'rb') as hash_file:
                    while True:
                        chunk = hash_file.read(settings.HASH_CHUNK_SIZE)
                        if not chunk:
                            break
                        file_hash_obj.update(chunk)

                # Create file record manually
                from app.models.file import File
                minio_object_name = self.minio_service.generate_object_name(file.filename)
                uploaded_file = File(
                    filename=file.filename,
                    original_filename=file.filename,
                    file_size=file.size,
                    content_type=file.content_type,
                    owner_id=user_id,
                    file_hash=file_hash_obj.hexdigest(),
                    minio_object_name=minio_object_name,
                    bucket_name=settings.MINIO_BUCKET_NAME,
                    upload_completed=True
                )

                self.db.add(uploaded_file)
                self.db.commit()
                self.db.refresh(uploaded_file)

                # Upload to MinIO
                with open(tmp_file_path, 'rb') as f:
                    self.minio_service.client.put_object(
                        bucket_name=settings.MINIO_BUCKET_NAME,
                        object_name=uploaded_file.minio_object_name,
                        data=f,
                        length=file.size,
                        content_type=file.content_type
                    )
            
            # Extract image metadata if it's an image file
            metadata = {}
            if self._is_image_file(file.content_type):
                try:
                    metadata = extract_image_metadata(tmp_file_path)
                    logger.info(f"Extracted metadata for {file.filename}: {metadata}")
                except Exception as e:
                    logger.error(f"Error extracting metadata from {file.filename}: {e}", exc_info=True)

            # Create document-file association with extracted metadata
            doc_file = DocumentFile(
                document_id=document.id,
                file_id=uploaded_file.id,
                file_use=document_data.file_use,
                file_label=document_data.file_label,
                sequence_number=document_data.sequence_number,
                checksum_md5=uploaded_file.file_hash,
                # Technical metadata from extraction - Standard MIX fields
                image_width=metadata.get('image_width'),
                image_height=metadata.get('image_height'),
                bits_per_sample=metadata.get('bits_per_sample'),
                samples_per_pixel=metadata.get('samples_per_pixel'),
                compression_scheme=metadata.get('compression_scheme'),
                color_space=metadata.get('color_space'),
                x_sampling_frequency=metadata.get('x_sampling_frequency'),
                y_sampling_frequency=metadata.get('y_sampling_frequency'),
                sampling_frequency_unit=metadata.get('sampling_frequency_unit'),
                date_time_created=metadata.get('date_time_created'),
                # Additional MIX metadata
                format_name=metadata.get('format_name'),
                byte_order=metadata.get('byte_order'),
                orientation=metadata.get('orientation'),
                icc_profile_name=metadata.get('icc_profile_name'),
                scanner_model_name=metadata.get('scanner_model_name'),
                scanning_software_name=metadata.get('scanning_software_name'),
                scanning_software_version=metadata.get('scanning_software_version'),
                # Comprehensive raw metadata (ALL EXIF/DNG tags)
                raw_metadata=metadata.get('raw_metadata')
            )

            self.db.add(doc_file)
            self.db.commit()

            return document

        except Exception as e:
            # If file upload fails, delete the document
            self.db.delete(document)
            self.db.commit()
            raise e
        finally:
            # Ensure temp file is always cleaned up
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except OSError:
                    pass  # Log but don't fail if cleanup fails
    
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

        return self._convert_to_document_detail(document)
    
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
                logger.error(f"Error deleting file from MinIO: {e}", exc_info=True)
        
        # Delete document (cascade will handle document_files and files)
        self.db.delete(document)
        self.db.commit()
        return True
    
    def export_metadata_csv(self, document_ids: List[int], user_id: int) -> StreamingResponse:
        """Export metadata for multiple documents as CSV"""
        # First verify all documents belong to user
        document_count = self.db.query(Document).filter(
            Document.id.in_(document_ids),
            Document.owner_id == user_id
        ).count()

        if document_count != len(document_ids):
            logger.warning(f"User {user_id} attempted to access documents they don't own")
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access some of the requested documents"
            )

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
            headers={"Content-Disposition": self._make_content_disposition(filename)}
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
        mets_generator = METSEcoMicGenerator()
        mets_xml = mets_generator.generate_mets_xml(document)
        
        return StreamingResponse(
            io.BytesIO(mets_xml.encode('utf-8')),
            media_type="application/xml",
            headers={"Content-Disposition": self._make_content_disposition(f"{document.logical_id}_mets.xml")}
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
        mets_generator = METSEcoMicGenerator()

        # Use temporary file for ZIP to avoid loading entire ZIP into memory
        import tempfile
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        tmp_zip_path = tmp_zip.name
        tmp_zip.close()

        try:
            with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for document in documents:
                    try:
                        mets_xml = mets_generator.generate_mets_xml(document)
                        filename = f"{document.logical_id}_mets.xml"
                        zip_file.writestr(filename, mets_xml.encode('utf-8'))
                    except Exception as e:
                        # Log error but continue with other documents
                        logger.error(f"Error generating METS for document {document.id}: {e}", exc_info=True)
                        continue

            # Stream the ZIP file
            def zip_stream_generator():
                try:
                    with open(tmp_zip_path, 'rb') as f:
                        chunk_size = settings.STREAMING_CHUNK_SIZE
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            yield chunk
                finally:
                    # Clean up temp file after streaming
                    import os
                    try:
                        os.unlink(tmp_zip_path)
                    except Exception:
                        pass

            return StreamingResponse(
                zip_stream_generator(),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=documents_mets.zip"}
            )
        except Exception as e:
            # Clean up on error
            import os
            try:
                os.unlink(tmp_zip_path)
            except Exception:
                pass
            raise
    
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

        # Use temporary file for ZIP to avoid loading entire ZIP into memory
        import tempfile
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        tmp_zip_path = tmp_zip.name
        tmp_zip.close()

        try:
            with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for doc_file in document.document_files:
                    try:
                        # Get file from MinIO
                        file_data = self.minio_service.get_file(doc_file.file.minio_object_name)

                        # Stream file data directly to ZIP in chunks to avoid loading entire file into memory
                        with zip_file.open(doc_file.file.filename, 'w') as zip_entry:
                            chunk_size = settings.STREAMING_CHUNK_SIZE
                            while True:
                                chunk = file_data.read(chunk_size)
                                if not chunk:
                                    break
                                zip_entry.write(chunk)
                    except Exception as e:
                        logger.error(f"Error adding file to ZIP: {e}", exc_info=True)

            # Stream the ZIP file
            def zip_stream_generator():
                try:
                    with open(tmp_zip_path, 'rb') as f:
                        chunk_size = settings.STREAMING_CHUNK_SIZE
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            yield chunk
                finally:
                    # Clean up temp file after streaming
                    import os
                    try:
                        os.unlink(tmp_zip_path)
                    except Exception:
                        pass

            return StreamingResponse(
                zip_stream_generator(),
                media_type="application/zip",
                headers={"Content-Disposition": self._make_content_disposition(f"{document.logical_id}_files.zip")}
            )
        except Exception as e:
            # Clean up on error
            import os
            try:
                os.unlink(tmp_zip_path)
            except Exception:
                pass
            raise
    
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

        # Use temporary file for ZIP to avoid loading entire ZIP into memory
        import tempfile
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        tmp_zip_path = tmp_zip.name
        tmp_zip.close()

        try:
            with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
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
                    mets_generator = METSEcoMicGenerator()
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
                    logger.error(f"Error generating METS XML: {e}", exc_info=True)
                    import traceback
                    traceback.print_exc()

                # Add files - stream to avoid loading into memory
                for doc_file in document.document_files:
                    try:
                        file_data = self.minio_service.get_file(doc_file.file.minio_object_name)

                        # Stream file data directly to ZIP in chunks
                        with zip_file.open(f"files/{doc_file.file.filename}", 'w') as zip_entry:
                            chunk_size = settings.STREAMING_CHUNK_SIZE
                            while True:
                                chunk = file_data.read(chunk_size)
                                if not chunk:
                                    break
                                zip_entry.write(chunk)
                    except Exception as e:
                        logger.error(f"Error adding file to ZIP: {e}", exc_info=True)

            # Stream the ZIP file
            def zip_stream_generator():
                try:
                    with open(tmp_zip_path, 'rb') as f:
                        chunk_size = settings.STREAMING_CHUNK_SIZE
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            yield chunk
                finally:
                    # Clean up temp file after streaming
                    import os
                    try:
                        os.unlink(tmp_zip_path)
                    except Exception:
                        pass

            return StreamingResponse(
                zip_stream_generator(),
                media_type="application/zip",
                headers={"Content-Disposition": self._make_content_disposition(f"{document.logical_id}_complete.zip")}
            )
        except Exception as e:
            # Clean up on error
            import os
            try:
                os.unlink(tmp_zip_path)
            except Exception:
                pass
            raise
    
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

        # Use temporary file for main ZIP to avoid loading entire ZIP into memory
        import tempfile
        main_tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        main_tmp_zip_path = main_tmp_zip.name
        main_tmp_zip.close()

        try:
            with zipfile.ZipFile(main_tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as main_zip:
                for document in documents:
                    # Create individual document ZIP in temp file
                    doc_tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
                    doc_tmp_zip_path = doc_tmp_zip.name
                    doc_tmp_zip.close()

                    try:
                        with zipfile.ZipFile(doc_tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as doc_zip:
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
                                mets_generator = METSEcoMicGenerator()
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
                                logger.error(f"Error generating METS XML: {e}", exc_info=True)
                                import traceback
                                traceback.print_exc()

                            # Add files - stream to avoid loading into memory
                            for doc_file in document.document_files:
                                try:
                                    file_data = self.minio_service.get_file(doc_file.file.minio_object_name)

                                    # Stream file data directly to ZIP in chunks
                                    with doc_zip.open(f"files/{doc_file.file.filename}", 'w') as zip_entry:
                                        chunk_size = settings.STREAMING_CHUNK_SIZE
                                        while True:
                                            chunk = file_data.read(chunk_size)
                                            if not chunk:
                                                break
                                            zip_entry.write(chunk)
                                except Exception as e:
                                    logger.error(f"Error adding file to ZIP: {e}", exc_info=True)

                        # Add document ZIP to main ZIP by reading from temp file
                        with open(doc_tmp_zip_path, 'rb') as doc_zip_file:
                            main_zip.writestr(f"{document.logical_id}.zip", doc_zip_file.read())
                    finally:
                        # Clean up document temp file
                        import os
                        try:
                            os.unlink(doc_tmp_zip_path)
                        except Exception:
                            pass

            # Stream the main ZIP file
            def zip_stream_generator():
                try:
                    with open(main_tmp_zip_path, 'rb') as f:
                        chunk_size = settings.STREAMING_CHUNK_SIZE
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            yield chunk
                finally:
                    # Clean up main temp file after streaming
                    import os
                    try:
                        os.unlink(main_tmp_zip_path)
                    except Exception:
                        pass

            return StreamingResponse(
                zip_stream_generator(),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=documents_batch.zip"}
            )
        except Exception as e:
            # Clean up on error
            import os
            try:
                os.unlink(main_tmp_zip_path)
            except Exception:
                pass
            raise
    
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

        # Validate file type and size using magic number verification
        detected_mime, is_valid = await validate_file_type_and_size(file)

        # Sanitize filename
        file.filename = validate_filename(file.filename)

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

        # Extract all logical_ids from filenames
        logical_ids = [os.path.splitext(file.filename)[0] for file in files]

        # Batch load all existing documents (prevents N+1 query problem)
        existing_documents = self.db.query(Document).filter(
            Document.logical_id.in_(logical_ids),
            Document.owner_id == user_id
        ).all()

        # Create a map for quick lookup
        doc_map = {doc.logical_id: doc for doc in existing_documents}

        for file in files:
            try:
                # Extract logical_id from filename (remove extension)
                logical_id = os.path.splitext(file.filename)[0]

                # Check if document exists in our pre-loaded map
                document = doc_map.get(logical_id)
                
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
    
    def generate_mets_xml_for_validation(self, document_id: int, user_id: int) -> str:
        """Generate METS XML for validation purposes"""
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate METS XML using the existing generator
        mets_generator = METSEcoMicGenerator()
        return mets_generator.generate_mets_xml(document)

    async def upload_folder_archive(
        self,
        zip_file: UploadFile,
        logical_id: str,
        title: str,
        description: str,
        conservative_id: str,
        conservative_id_authority: str,
        archive_name: str,
        archive_contact: str,
        document_type: str,
        user_id: int
    ) -> dict:
        """
        Upload a ZIP archive containing a structured folder with multiple files.
        Automatically categorizes files based on ECO-MiC folder structure.

        Args:
            zip_file: ZIP archive containing document files
            logical_id: Document logical identifier
            title: Document title
            description: Document description
            conservative_id: Conservative identifier
            conservative_id_authority: Authority for conservative ID
            archive_name: Archive name
            archive_contact: Archive contact
            document_type: Type of document
            user_id: User ID

        Returns:
            Dict with upload status, document_id, and categorized files info
        """

        try:
            # Validate ZIP file
            if not zip_file.filename.endswith('.zip'):
                raise HTTPException(status_code=400, detail="File must be a ZIP archive")

            # Create document first
            document_data = DocumentCreate(
                logical_id=logical_id,
                title=title,
                description=description,
                conservative_id=conservative_id,
                conservative_id_authority=conservative_id_authority,
                archive_name=archive_name,
                archive_contact=archive_contact,
                document_type=document_type
            )

            document = self.create_document(document_data, user_id)

            # Create temp directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save ZIP to temp file
                zip_path = os.path.join(temp_dir, "upload.zip")
                with open(zip_path, "wb") as f:
                    content = await zip_file.read()
                    f.write(content)

                # Extract ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Collect all files with their paths
                file_list = []
                for root, dirs, files in os.walk(temp_dir):
                    for filename in files:
                        if filename == "upload.zip":
                            continue  # Skip the ZIP itself

                        full_path = os.path.join(root, filename)
                        # Get relative folder path for categorization
                        rel_folder = os.path.relpath(root, temp_dir)

                        file_list.append({
                            'filename': filename,
                            'full_path': full_path,
                            'folder_path': rel_folder
                        })

                # Categorize files
                categorizer = FileCategorizer()
                categorized_files = {}
                total_uploaded = 0

                for file_info in file_list:
                    filename = file_info['filename']
                    full_path = file_info['full_path']
                    folder_path = file_info['folder_path']

                    # Categorize file
                    category, confidence = categorizer.categorize_file(filename, folder_path)
                    file_use = categorizer.get_file_use_from_category(category)

                    try:
                        # Upload file to MinIO
                        with open(full_path, 'rb') as file_handle:
                            # Create a file-like object with required attributes
                            class FileWrapper:
                                def __init__(self, file, filename):
                                    self.file = file
                                    self.filename = filename

                                def read(self, size=-1):
                                    return self.file.read(size)

                                def seek(self, offset, whence=0):
                                    return self.file.seek(offset, whence)

                            wrapped_file = FileWrapper(file_handle, filename)

                            # Get file size
                            file_size = os.path.getsize(full_path)

                            # Generate unique filename for MinIO
                            minio_filename = f"{logical_id}_{filename}"
                            object_name = await self.minio_service.upload_file(
                                wrapped_file,
                                minio_filename
                            )

                            # Create File record
                            file_record = File(
                                filename=filename,
                                content_type=self._guess_content_type(filename),
                                file_size=file_size,
                                minio_object_name=object_name,
                                uploaded_by_id=user_id
                            )
                            self.db.add(file_record)
                            self.db.flush()

                            # Create DocumentFile association
                            doc_file = DocumentFile(
                                document_id=document.id,
                                file_id=file_record.id,
                                file_use=file_use,
                                file_category=category,
                                sequence_number=total_uploaded + 1
                            )
                            self.db.add(doc_file)

                            # Track for response
                            if category not in categorized_files:
                                categorized_files[category] = []

                            categorized_files[category].append({
                                'filename': filename,
                                'category': category,
                                'confidence': confidence,
                                'file_use': file_use,
                                'folder': folder_path
                            })

                            total_uploaded += 1

                    except Exception as e:
                        logger.error(f"Error uploading file {filename}: {str(e)}", exc_info=True)
                        # Continue with other files

                self.db.commit()

                return {
                    "success": True,
                    "message": f"Successfully uploaded {total_uploaded} files",
                    "document_id": document.id,
                    "categorized_files": categorized_files,
                    "total_files": total_uploaded
                }

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error uploading folder archive: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to upload folder: {str(e)}")

    def _guess_content_type(self, filename: str) -> str:
        """Guess content type from filename extension"""
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
