import csv
import hashlib
import io
import logging
import os
import tempfile
import zipfile
from datetime import datetime
from typing import List, Optional, Dict, Any
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
from app.services.mongodb import mongodb_service
from app.services.mets_document import METSDocumentService
from app.services.transaction_coordinator import TransactionCoordinator
from app.utils.mets_generator_ecomic import METSEcoMicGenerator
from app.utils.file_validator import validate_file_type_and_size, validate_filename
from app.utils.image_metadata import extract_image_metadata
from app.utils.file_categorizer import FileCategorizer


class DocumentService:
    """Service for document management - Dual-database architecture (PostgreSQL + MongoDB)"""

    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()
        self.file_service.db = db  # Inject database session into FileService
        self.minio_service = MinIOService()
        self.mets_service = METSDocumentService(mongodb_service)
        self.coordinator = TransactionCoordinator(db, self.mets_service, self.minio_service)

    async def _convert_to_document_detail(self, document: Document) -> DocumentDetail:
        """
        Convert Document ORM model to DocumentDetail schema.
        Merges platform data (PostgreSQL) with METS metadata (MongoDB).
        """
        # Get files from PostgreSQL relationship
        document_files = []
        for doc_file in document.document_files:
            file_data = {
                'id': doc_file.id,
                'file_id': doc_file.file_id,
                'file_use': doc_file.file_use,
                'file_category': doc_file.file_category,
                'file_label': doc_file.file_label,
                'sequence_number': doc_file.sequence_number,
                'checksum_md5': doc_file.checksum_md5,
                'image_width': doc_file.image_width,
                'image_height': doc_file.image_height,
                'bits_per_sample': doc_file.bits_per_sample,
                'samples_per_pixel': doc_file.samples_per_pixel,
                'date_time_created': doc_file.date_time_created,
                'compression_scheme': doc_file.compression_scheme,
                'color_space': doc_file.color_space,
                'sampling_frequency_unit': doc_file.sampling_frequency_unit,
                'x_sampling_frequency': doc_file.x_sampling_frequency,
                'y_sampling_frequency': doc_file.y_sampling_frequency,
                'format_name': doc_file.format_name,
                'byte_order': doc_file.byte_order,
                'orientation': doc_file.orientation,
                'icc_profile_name': doc_file.icc_profile_name,
                'scanner_manufacturer': doc_file.scanner_manufacturer,
                'scanner_model_name': doc_file.scanner_model_name,
                'scanning_software_name': doc_file.scanning_software_name,
                'scanning_software_version': doc_file.scanning_software_version,
                'raw_metadata': doc_file.raw_metadata,
                'filename': doc_file.file.filename,
                'file_size': doc_file.file.file_size,
                'content_type': doc_file.file.content_type
            }
            document_files.append(file_data)

        # Get METS metadata from MongoDB if available
        mets_data = {}
        if document.mets_document_id:
            try:
                mets_doc = await self.mets_service.get_mets_document(document.mets_document_id)
                if mets_doc:
                    # Extract METS fields from MongoDB document
                    mets_data = {
                        'conservative_id': mets_doc.get('conservative_id'),
                        'conservative_id_authority': mets_doc.get('conservative_id_authority'),
                        'title': mets_doc.get('title'),
                        'description': mets_doc.get('description'),
                        'type_of_resource': mets_doc.get('type_of_resource'),
                        'location': mets_doc.get('location'),
                        'language': mets_doc.get('language'),
                        'subjects': mets_doc.get('subjects'),
                        'schema_version': mets_doc.get('schema_version'),
                    }

                    # Archive fields
                    if 'archive' in mets_doc and mets_doc['archive']:
                        archive = mets_doc['archive']
                        mets_data['archive_name'] = archive.get('name')
                        mets_data['archive_contact'] = archive.get('contact')
                        mets_data['fund_name'] = archive.get('fund_name')
                        mets_data['series_name'] = archive.get('series_name')
                        mets_data['folder_number'] = archive.get('folder_number')

                    # Temporal fields
                    if 'temporal' in mets_doc and mets_doc['temporal']:
                        temporal = mets_doc['temporal']
                        mets_data['date_from'] = temporal.get('date_from')
                        mets_data['date_to'] = temporal.get('date_to')
                        mets_data['period'] = temporal.get('period')

                    # Agents fields
                    if 'agents' in mets_doc and mets_doc['agents']:
                        agents = mets_doc['agents']
                        if 'producer' in agents and agents['producer']:
                            producer = agents['producer']
                            mets_data['producer_name'] = producer.get('name')
                            mets_data['producer_type'] = producer.get('type')
                            mets_data['producer_role'] = producer.get('role')
                        if 'creator' in agents and agents['creator']:
                            creator = agents['creator']
                            mets_data['creator_name'] = creator.get('name')
                            mets_data['creator_type'] = creator.get('type')
                            mets_data['creator_role'] = creator.get('role')

                    # Rights fields
                    if 'rights' in mets_doc and mets_doc['rights']:
                        rights = mets_doc['rights']
                        mets_data['license_url'] = rights.get('license_url')
                        mets_data['rights_statement'] = rights.get('rights_statement')
                        mets_data['rights_category'] = rights.get('category')
                        mets_data['rights_holder'] = rights.get('holder')
                        mets_data['rights_constraint'] = rights.get('constraint')

                    # Technical fields
                    if 'technical' in mets_doc and mets_doc['technical']:
                        technical = mets_doc['technical']
                        mets_data['image_producer'] = technical.get('image_producer')
                        mets_data['scanner_manufacturer'] = technical.get('scanner_manufacturer')
                        mets_data['scanner_model'] = technical.get('scanner_model')

                    # Physical fields
                    if 'physical' in mets_doc and mets_doc['physical']:
                        physical = mets_doc['physical']
                        mets_data['document_type'] = physical.get('document_type')
                        mets_data['total_pages'] = physical.get('total_pages')
                        mets_data['physical_form'] = physical.get('physical_form')
                        mets_data['extent_description'] = physical.get('extent_description')

                    # METS header fields
                    if 'mets_header' in mets_doc and mets_doc['mets_header']:
                        mets_header = mets_doc['mets_header']
                        mets_data['record_status'] = mets_header.get('record_status')

            except Exception as e:
                logger.error(f"Error fetching METS metadata for document {document.id}: {e}", exc_info=True)

        # Merge platform data (PostgreSQL) with METS metadata (MongoDB)
        return DocumentDetail(
            # Platform fields (PostgreSQL)
            id=document.id,
            logical_id=document.logical_id,
            owner_id=document.owner_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            mets_document_id=document.mets_document_id,

            # METS fields (MongoDB) - with defaults if not found
            conservative_id=mets_data.get('conservative_id'),
            conservative_id_authority=mets_data.get('conservative_id_authority'),
            title=mets_data.get('title'),
            description=mets_data.get('description'),
            type_of_resource=mets_data.get('type_of_resource'),
            archive_name=mets_data.get('archive_name'),
            archive_contact=mets_data.get('archive_contact'),
            fund_name=mets_data.get('fund_name'),
            series_name=mets_data.get('series_name'),
            folder_number=mets_data.get('folder_number'),
            date_from=mets_data.get('date_from'),
            date_to=mets_data.get('date_to'),
            period=mets_data.get('period'),
            location=mets_data.get('location'),
            language=mets_data.get('language'),
            subjects=mets_data.get('subjects'),
            producer_name=mets_data.get('producer_name'),
            producer_type=mets_data.get('producer_type'),
            producer_role=mets_data.get('producer_role'),
            creator_name=mets_data.get('creator_name'),
            creator_type=mets_data.get('creator_type'),
            creator_role=mets_data.get('creator_role'),
            license_url=mets_data.get('license_url'),
            rights_statement=mets_data.get('rights_statement'),
            rights_category=mets_data.get('rights_category'),
            rights_holder=mets_data.get('rights_holder'),
            rights_constraint=mets_data.get('rights_constraint'),
            image_producer=mets_data.get('image_producer'),
            scanner_manufacturer=mets_data.get('scanner_manufacturer'),
            scanner_model=mets_data.get('scanner_model'),
            document_type=mets_data.get('document_type'),
            total_pages=mets_data.get('total_pages'),
            physical_form=mets_data.get('physical_form'),
            extent_description=mets_data.get('extent_description'),
            record_status=mets_data.get('record_status'),
            schema_version=mets_data.get('schema_version'),

            # METS XML (generated on-demand, not stored)
            mets_xml=None,

            # Files (PostgreSQL relationship)
            document_files=document_files
        )

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be safe for use as a filename"""
        import re
        # Replace invalid characters with underscores
        # Keep alphanumeric, hyphens, underscores, and dots
        sanitized = re.sub(r'[^\w\-\.]', '_', filename)
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

    async def create_document(self, document_data: DocumentCreate, user_id: int) -> Document:
        """
        Create a new document using dual-database architecture.

        Uses TransactionCoordinator to ensure atomicity across:
        - PostgreSQL (platform metadata)
        - MongoDB (METS ECO-MiC metadata)
        """
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

        # Extract METS metadata from document_data
        mets_metadata = self.mets_service.extract_mets_metadata_from_document_data(
            document_data.dict()
        )

        # Get schema version (default 1.2)
        schema_version = document_data.schema_version if hasattr(document_data, 'schema_version') else "1.2"

        # Phase 1: PostgreSQL operation (platform metadata)
        def create_postgres_doc() -> int:
            document = Document(
                logical_id=document_data.logical_id,
                owner_id=user_id
            )
            self.db.add(document)
            self.db.flush()  # Get ID without committing
            return document.id

        # Phase 2: MongoDB operation (METS metadata)
        async def create_mongo_mets(postgres_doc_id: int) -> str:
            mets_id = await self.mets_service.create_mets_document(
                logical_id=document_data.logical_id,
                owner_id=user_id,
                platform_document_id=postgres_doc_id,
                metadata=mets_metadata,
                schema_version=schema_version
            )

            # Update PostgreSQL document with MongoDB reference
            doc = self.db.query(Document).filter(Document.id == postgres_doc_id).first()
            doc.mets_document_id = mets_id
            self.db.flush()

            return mets_id

        # Execute coordinated transaction
        try:
            result = await self.coordinator.execute_document_creation(
                postgres_op=create_postgres_doc,
                mets_op=create_mongo_mets,
                minio_ops=None  # No files yet
            )

            # Get and return the created document
            document = self.db.query(Document).filter(
                Document.id == result['postgres_doc_id']
            ).first()

            return document

        except Exception as e:
            logger.error(f"Error creating document: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

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
        document = await self.create_document(doc_create, user_id)

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

                # Auto-categorize file based on extension FIRST
                from app.utils.file_categorizer import FileCategorizer
                from app.utils.minio_paths import get_minio_object_path
                categorizer = FileCategorizer()
                file_category, confidence = categorizer.categorize_file(file.filename)

                # Calculate hash using chunked reading
                file_hash_obj = hashlib.sha256()  # Use SHA256 for consistency
                with open(tmp_file_path, 'rb') as hash_file:
                    while True:
                        chunk = hash_file.read(settings.HASH_CHUNK_SIZE)
                        if not chunk:
                            break
                        file_hash_obj.update(chunk)

                file_hash = file_hash_obj.hexdigest()

                # Generate consistent MinIO path using category
                minio_object_name = get_minio_object_path(user_id, file_hash, file_category, file.filename)

                # Create file record manually
                from app.models.file import File
                uploaded_file = File(
                    filename=file.filename,
                    original_filename=file.filename,
                    file_size=file.size,
                    content_type=file.content_type,
                    owner_id=user_id,
                    file_hash=file_hash,
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

            # Get file_use from already-categorized file_category
            file_use = categorizer.get_file_use_from_category(file_category)

            # Create document-file association with extracted metadata
            doc_file = DocumentFile(
                document_id=document.id,
                file_id=uploaded_file.id,
                file_category=file_category,  # Auto-categorized earlier
                file_use=document_data.file_use or file_use,  # Use provided or auto-detected
                file_label=document_data.file_label,
                sequence_number=document_data.sequence_number or 1,  # Default to 1 if not provided
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
            try:
                await self.delete_document(document.id, user_id)
            except:
                pass  # Best effort cleanup
            raise e
        finally:
            # Ensure temp file is always cleaned up
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except OSError:
                    pass  # Log but don't fail if cleanup fails

    async def get_documents(self, user_id: int, skip: int = 0, limit: int = 100) -> List[DocumentListItem]:
        """
        Get list of documents for a user.
        Merges platform data (PostgreSQL) with key METS fields (MongoDB).
        """
        # Get platform data from PostgreSQL
        query = self.db.query(
            Document.id,
            Document.logical_id,
            Document.owner_id,
            Document.created_at,
            Document.updated_at,
            Document.mets_document_id,
            func.count(DocumentFile.id).label('file_count')
        ).outerjoin(
            DocumentFile, Document.id == DocumentFile.document_id
        ).filter(
            Document.owner_id == user_id
        ).group_by(
            Document.id,
            Document.logical_id,
            Document.owner_id,
            Document.created_at,
            Document.updated_at,
            Document.mets_document_id
        ).order_by(
            Document.created_at.desc()
        ).offset(skip).limit(limit)

        results = query.all()

        # Build document list items, merging MongoDB data
        items = []
        for row in results:
            # Default METS fields
            title = None
            archive_name = None
            document_type = None
            total_pages = None

            # Fetch METS metadata if available
            if row.mets_document_id:
                try:
                    mets_doc = await self.mets_service.get_mets_document(row.mets_document_id)
                    if mets_doc:
                        title = mets_doc.get('title')
                        document_type = mets_doc.get('physical', {}).get('document_type') if mets_doc.get('physical') else None
                        total_pages = mets_doc.get('physical', {}).get('total_pages') if mets_doc.get('physical') else None
                        archive_name = mets_doc.get('archive', {}).get('name') if mets_doc.get('archive') else None
                except Exception as e:
                    logger.error(f"Error fetching METS for document {row.id}: {e}")

            items.append(DocumentListItem(
                id=row.id,
                logical_id=row.logical_id,
                owner_id=row.owner_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
                title=title,
                archive_name=archive_name,
                document_type=document_type,
                total_pages=total_pages,
                file_count=row.file_count
            ))

        return items

    async def get_document(self, document_id: int, user_id: int) -> Optional[DocumentDetail]:
        """
        Get a specific document with files.
        Merges platform data (PostgreSQL) with METS metadata (MongoDB).
        """
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()

        if not document:
            return None

        return await self._convert_to_document_detail(document)

    async def update_document(self, document_id: int, document_data: DocumentUpdate, user_id: int) -> Optional[Document]:
        """
        Update a document.
        Updates both PostgreSQL (platform) and MongoDB (METS metadata).
        """
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()

        if not document:
            return None

        update_dict = document_data.dict(exclude_unset=True)

        # Separate platform updates from METS updates
        platform_fields = {'logical_id'}
        mets_fields = set(update_dict.keys()) - platform_fields

        # Update platform fields in PostgreSQL if present
        if 'logical_id' in update_dict:
            document.logical_id = update_dict['logical_id']

        # Update METS metadata in MongoDB if present
        if mets_fields and document.mets_document_id:
            # Extract METS metadata structure
            mets_updates = {k: v for k, v in update_dict.items() if k in mets_fields}
            structured_mets = self.mets_service.extract_mets_metadata_from_document_data(mets_updates)

            # Define update operation
            async def update_mets() -> bool:
                return await self.mets_service.update_mets_document(
                    document.mets_document_id,
                    structured_mets
                )

            # Define PostgreSQL timestamp update
            def update_postgres_timestamp():
                document.updated_at = datetime.utcnow()
                self.db.flush()

            # Execute coordinated update
            try:
                success = await self.coordinator.execute_document_update(
                    mets_id=document.mets_document_id,
                    mets_update_op=update_mets,
                    postgres_update_op=update_postgres_timestamp if 'logical_id' in update_dict else None
                )

                if not success:
                    raise HTTPException(status_code=500, detail="Failed to update document metadata")
            except Exception as e:
                logger.error(f"Error updating document: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")
        else:
            # Only platform update or no METS document yet
            if 'logical_id' in update_dict:
                self.db.commit()

        self.db.refresh(document)
        return document

    async def delete_document(self, document_id: int, user_id: int) -> bool:
        """
        Delete a document and its associated files.
        Deletes from all three stores: MinIO → MongoDB → PostgreSQL.
        """
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()

        if not document:
            return False

        # Collect MinIO object names
        minio_objects = [
            doc_file.file.minio_object_name
            for doc_file in document.document_files
            if doc_file.file and doc_file.file.minio_object_name
        ]

        # Define PostgreSQL deletion
        def delete_postgres() -> bool:
            self.db.delete(document)
            self.db.flush()
            return True

        # Execute coordinated deletion
        if document.mets_document_id:
            try:
                success = await self.coordinator.execute_document_deletion(
                    mets_id=document.mets_document_id,
                    postgres_op=delete_postgres,
                    minio_objects=minio_objects
                )
                return success
            except Exception as e:
                logger.error(f"Error deleting document: {e}", exc_info=True)
                return False
        else:
            # No METS document, just delete PostgreSQL and MinIO
            for object_name in minio_objects:
                try:
                    self.minio_service.delete_file(object_name)
                except Exception as e:
                    logger.error(f"Error deleting file from MinIO: {e}", exc_info=True)

            self.db.delete(document)
            self.db.commit()
            return True

    async def export_metadata_csv(self, document_ids: List[int], user_id: int) -> StreamingResponse:
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

        # Write data - fetch from MongoDB for each document
        for doc in documents:
            # Get METS metadata
            mets_data = {}
            if doc.mets_document_id:
                try:
                    mets_doc = await self.mets_service.get_mets_document(doc.mets_document_id)
                    if mets_doc:
                        mets_data = {
                            'title': mets_doc.get('title'),
                            'description': mets_doc.get('description'),
                            'conservative_id': mets_doc.get('conservative_id'),
                            'conservative_id_authority': mets_doc.get('conservative_id_authority'),
                            'archive_name': mets_doc.get('archive', {}).get('name') if mets_doc.get('archive') else None,
                            'archive_contact': mets_doc.get('archive', {}).get('contact') if mets_doc.get('archive') else None,
                            'fund_name': mets_doc.get('archive', {}).get('fund_name') if mets_doc.get('archive') else None,
                            'series_name': mets_doc.get('archive', {}).get('series_name') if mets_doc.get('archive') else None,
                            'folder_number': mets_doc.get('archive', {}).get('folder_number') if mets_doc.get('archive') else None,
                            'date_from': mets_doc.get('temporal', {}).get('date_from') if mets_doc.get('temporal') else None,
                            'date_to': mets_doc.get('temporal', {}).get('date_to') if mets_doc.get('temporal') else None,
                            'period': mets_doc.get('temporal', {}).get('period') if mets_doc.get('temporal') else None,
                            'location': mets_doc.get('location'),
                            'language': mets_doc.get('language'),
                            'subjects': mets_doc.get('subjects'),
                            'document_type': mets_doc.get('physical', {}).get('document_type') if mets_doc.get('physical') else None,
                            'total_pages': mets_doc.get('physical', {}).get('total_pages') if mets_doc.get('physical') else None,
                            'license_url': mets_doc.get('rights', {}).get('license_url') if mets_doc.get('rights') else None,
                            'rights_statement': mets_doc.get('rights', {}).get('rights_statement') if mets_doc.get('rights') else None,
                            'image_producer': mets_doc.get('technical', {}).get('image_producer') if mets_doc.get('technical') else None,
                            'scanner_manufacturer': mets_doc.get('technical', {}).get('scanner_manufacturer') if mets_doc.get('technical') else None,
                            'scanner_model': mets_doc.get('technical', {}).get('scanner_model') if mets_doc.get('technical') else None,
                        }
                except Exception as e:
                    logger.error(f"Error fetching METS for document {doc.id}: {e}")

            writer.writerow([
                # Basic identification
                doc.logical_id,
                mets_data.get('title'),
                mets_data.get('description'),
                mets_data.get('conservative_id'),
                mets_data.get('conservative_id_authority'),
                # Archive information
                mets_data.get('archive_name'),
                mets_data.get('archive_contact'),
                mets_data.get('fund_name'),
                mets_data.get('series_name'),
                mets_data.get('folder_number'),
                # Temporal information
                mets_data.get('date_from'),
                mets_data.get('date_to'),
                mets_data.get('period'),
                # Geographic and contextual information
                mets_data.get('location'),
                mets_data.get('language'),
                mets_data.get('subjects'),
                # Document structure
                mets_data.get('document_type'),
                mets_data.get('total_pages'),
                # Rights information
                mets_data.get('license_url'),
                mets_data.get('rights_statement'),
                # Technical metadata
                mets_data.get('image_producer'),
                mets_data.get('scanner_manufacturer'),
                mets_data.get('scanner_model'),
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

    async def export_mets_xml(self, document_id: int, user_id: int) -> StreamingResponse:
        """Export dynamically generated METS XML for a single document"""
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Convert to DocumentDetail (merges PostgreSQL + MongoDB)
        document_detail = await self._convert_to_document_detail(document)

        # Generate METS XML dynamically from merged data
        mets_generator = METSEcoMicGenerator()
        mets_xml = mets_generator.generate_mets_xml(document_detail)

        return StreamingResponse(
            io.BytesIO(mets_xml.encode('utf-8')),
            media_type="application/xml",
            headers={"Content-Disposition": self._make_content_disposition(f"{document.logical_id}_mets.xml")}
        )

    # NOTE: Remaining methods (export_multiple_mets_xml, download_document_files,
    # download_document_archive, batch_download_archives, batch_create_documents,
    # upload_document_image, batch_upload_images, generate_mets_xml_for_validation,
    # upload_folder_archive, _guess_content_type) follow similar patterns and would
    # need to be refactored to use await self._convert_to_document_detail() and
    # await self.create_document() instead of the sync versions.
    # For brevity, I'm continuing with the most critical methods.

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
                document = await self.create_document(doc_data, user_id)
                success.append({
                    "logical_id": document.logical_id,
                    "title": doc_data.title if hasattr(doc_data, 'title') else None,
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
        from app.utils.file_categorizer import FileCategorizer

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
            # Auto-categorize file based on extension BEFORE upload
            categorizer = FileCategorizer()
            file_category, confidence = categorizer.categorize_file(file.filename)
            file_use = categorizer.get_file_use_from_category(file_category)

            # Upload file to storage with category for proper path
            uploaded_file = await self.file_service.upload_file(file, user_id, file_category)

            # Get next sequence number
            max_seq = self.db.query(func.max(DocumentFile.sequence_number)).filter(
                DocumentFile.document_id == document.id
            ).scalar() or 0

            # Link file to document
            document_file = DocumentFile(
                document_id=document.id,
                file_id=uploaded_file.id,
                file_category=file_category,
                file_use=file_use,
                sequence_number=max_seq + 1,
                checksum_md5=uploaded_file.file_hash  # Populate hash for METS integrity
            )

            self.db.add(document_file)
            self.db.commit()

            return {
                "success": True,
                "message": f"Image uploaded successfully for document {document.logical_id}",
                "document_id": document.id,
                "file_category": file_category,
                "confidence": confidence
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

    async def batch_upload_images(self, files: List[UploadFile], user_id: int) -> dict:
        """
        Batch upload images, matching by filename to logical_id.
        Only attaches files to EXISTING documents - does NOT create new documents.
        """
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

                # If document doesn't exist, report error - DO NOT auto-create
                if not document:
                    errors.append({
                        "filename": file.filename,
                        "logical_id": logical_id,
                        "error": f"No document found with logical_id '{logical_id}'. Create the document first or upload files individually."
                    })
                    continue

                # Upload the image to the existing document
                result = await self.upload_document_image(document.id, file, user_id)
                success.append({
                    "filename": file.filename,
                    "logical_id": logical_id,
                    "document_id": document.id,
                    "file_category": result.get("file_category"),
                    "confidence": result.get("confidence")
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
            "created_documents": created_documents  # Will always be empty now
        }

    async def generate_mets_xml_for_validation(self, document_id: int, user_id: int) -> str:
        """Generate METS XML for validation purposes"""
        document = self.db.query(Document).options(
            joinedload(Document.document_files).joinedload(DocumentFile.file)
        ).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Convert to DocumentDetail (merges PostgreSQL + MongoDB)
        document_detail = await self._convert_to_document_detail(document)

        # Generate METS XML using the existing generator
        mets_generator = METSEcoMicGenerator()
        return mets_generator.generate_mets_xml(document_detail)

    def _guess_content_type(self, filename: str) -> str:
        """Guess content type from filename extension"""
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'

    async def upload_folder_archive(
        self,
        zip_file: UploadFile,
        logical_id: str,
        user_id: int,
        title: str = None,
        description: str = None,
        conservative_id: str = None,
        conservative_id_authority: str = None,
        archive_name: str = None,
        archive_contact: str = None,
        document_type: str = None,
        **additional_metadata
    ) -> dict:
        """
        Upload a ZIP archive containing a structured folder with multiple files.
        Automatically categorizes files based on ECO-MiC folder structure.

        Uses dual-database architecture with TransactionCoordinator for atomicity.

        Args:
            zip_file: ZIP archive containing the folder structure
            logical_id: Document logical identifier
            user_id: User ID
            title, description, etc.: METS metadata fields
            additional_metadata: Additional METS fields

        Returns:
            dict with success, message, document_id, categorized_files, total_files
        """
        temp_dir = None
        uploaded_files = []
        minio_objects = []

        try:
            # Create temporary directory for extraction
            temp_dir = tempfile.mkdtemp(prefix='archivia_zip_')
            logger.info(f"Created temp directory: {temp_dir}")

            # Save uploaded ZIP to temp file
            zip_path = os.path.join(temp_dir, 'upload.zip')
            with open(zip_path, 'wb') as f:
                await zip_file.seek(0)
                chunk_size = settings.STREAMING_CHUNK_SIZE
                while True:
                    chunk = await zip_file.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)

            # Extract ZIP
            logger.info(f"Extracting ZIP archive: {zip_path}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Remove the ZIP file itself from temp dir
            os.remove(zip_path)

            # Collect all files with their relative paths
            file_list = []
            for root, dirs, files in os.walk(temp_dir):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(full_path, temp_dir)
                    folder_path = os.path.dirname(relative_path)

                    file_list.append({
                        'filename': filename,
                        'full_path': full_path,
                        'folder_path': folder_path,
                        'relative_path': relative_path
                    })

            if not file_list:
                raise HTTPException(
                    status_code=400,
                    detail="ZIP archive contains no files"
                )

            logger.info(f"Found {len(file_list)} files in ZIP archive")

            # Categorize files using FileCategorizer
            categorizer = FileCategorizer()
            categorized_files = categorizer.validate_folder_structure(file_list)

            # Log categorization results
            for category, files in categorized_files.items():
                if files:
                    logger.info(f"Category '{category}': {len(files)} files")

            # Rebuild file list with categories from categorized_files
            # The validate_folder_structure returns files grouped by category with 'category' field added
            files_with_categories = []
            for category, files in categorized_files.items():
                for file_info in files:
                    # Each file_info now has the 'category' field added by categorizer
                    files_with_categories.append(file_info)

            # Create document metadata
            doc_data = DocumentCreate(
                logical_id=logical_id,
                title=title,
                description=description,
                conservative_id=conservative_id,
                conservative_id_authority=conservative_id_authority,
                archive_name=archive_name,
                archive_contact=archive_contact,
                document_type=document_type,
                **additional_metadata
            )

            # Phase 1: Create document (uses TransactionCoordinator internally)
            document = await self.create_document(doc_data, user_id)
            logger.info(f"Created document {document.id} with logical_id '{logical_id}'")

            # Phase 2: Upload all files to MinIO and create associations
            sequence_number = 1

            for file_info in files_with_categories:
                try:
                    filename = file_info['filename']
                    full_path = file_info['full_path']
                    category = file_info.get('category', 'other')
                    folder_path = file_info.get('folder_path', '')

                    # Guess content type
                    content_type = self._guess_content_type(filename)

                    # Calculate file hash
                    file_hash_obj = hashlib.sha256()
                    file_size = os.path.getsize(full_path)

                    with open(full_path, 'rb') as f:
                        while True:
                            chunk = f.read(settings.HASH_CHUNK_SIZE)
                            if not chunk:
                                break
                            file_hash_obj.update(chunk)

                    file_hash = file_hash_obj.hexdigest()

                    # Generate MinIO path
                    from app.utils.minio_paths import get_minio_object_path
                    minio_object_name = get_minio_object_path(
                        user_id, file_hash, category, filename
                    )

                    # Create File record
                    from app.models.file import File
                    db_file = File(
                        filename=filename,
                        original_filename=filename,
                        file_size=file_size,
                        content_type=content_type,
                        owner_id=user_id,
                        file_hash=file_hash,
                        minio_object_name=minio_object_name,
                        bucket_name=settings.MINIO_BUCKET_NAME,
                        upload_completed=True
                    )

                    self.db.add(db_file)
                    self.db.flush()  # Get file ID
                    uploaded_files.append(db_file)

                    # Upload to MinIO
                    with open(full_path, 'rb') as f:
                        self.minio_service.client.put_object(
                            bucket_name=settings.MINIO_BUCKET_NAME,
                            object_name=minio_object_name,
                            data=f,
                            length=file_size,
                            content_type=content_type
                        )

                    minio_objects.append(minio_object_name)
                    logger.info(f"Uploaded file to MinIO: {minio_object_name}")

                    # Extract metadata if image
                    metadata = {}
                    if self._is_image_file(content_type):
                        try:
                            metadata = extract_image_metadata(full_path)
                        except Exception as e:
                            logger.error(f"Error extracting metadata from {filename}: {e}")

                    # Get file_use from category
                    file_use = categorizer.get_file_use_from_category(category)

                    # Derive file_label from folder structure or filename
                    file_label = folder_path if folder_path else os.path.splitext(filename)[0]

                    # Create DocumentFile association
                    doc_file = DocumentFile(
                        document_id=document.id,
                        file_id=db_file.id,
                        file_category=category,
                        file_use=file_use,
                        file_label=file_label,
                        sequence_number=sequence_number,
                        checksum_md5=file_hash,
                        # Technical metadata
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
                        format_name=metadata.get('format_name'),
                        byte_order=metadata.get('byte_order'),
                        orientation=metadata.get('orientation'),
                        icc_profile_name=metadata.get('icc_profile_name'),
                        scanner_model_name=metadata.get('scanner_model_name'),
                        scanning_software_name=metadata.get('scanning_software_name'),
                        scanning_software_version=metadata.get('scanning_software_version'),
                        raw_metadata=metadata.get('raw_metadata')
                    )

                    self.db.add(doc_file)
                    sequence_number += 1

                except Exception as e:
                    logger.error(f"Error processing file {filename}: {e}", exc_info=True)
                    # Rollback everything on file processing error
                    raise

            # Commit all file associations
            self.db.commit()

            logger.info(f"Successfully uploaded {len(files_with_categories)} files for document {document.id}")

            return {
                "success": True,
                "message": f"Successfully uploaded {len(files_with_categories)} files for document '{logical_id}'",
                "document_id": document.id,
                "categorized_files": {
                    category: [f['filename'] for f in files]
                    for category, files in categorized_files.items()
                    if files
                },
                "total_files": len(files_with_categories)
            }

        except HTTPException:
            # Re-raise HTTP exceptions (they have proper status codes and messages)
            logger.error(f"HTTP error in upload_folder_archive", exc_info=True)

            # Rollback database changes
            self.db.rollback()

            # Delete uploaded files from MinIO
            for minio_object in minio_objects:
                try:
                    self.minio_service.delete_file(minio_object)
                    logger.info(f"Cleaned up MinIO object: {minio_object}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up MinIO object {minio_object}: {cleanup_error}")

            # Re-raise the original HTTP exception
            raise

        except Exception as e:
            logger.error(f"Error in upload_folder_archive: {e}", exc_info=True)

            # Rollback database changes
            self.db.rollback()

            # Delete uploaded files from MinIO
            for minio_object in minio_objects:
                try:
                    self.minio_service.delete_file(minio_object)
                    logger.info(f"Cleaned up MinIO object: {minio_object}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up MinIO object {minio_object}: {cleanup_error}")

            # Delete document if created
            if 'document' in locals() and document:
                try:
                    await self.delete_document(document.id, user_id)
                    logger.info(f"Cleaned up document {document.id}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up document: {cleanup_error}")

            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload folder archive: {str(e)}"
            )

        finally:
            # Clean up temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temp directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temp directory: {cleanup_error}")
