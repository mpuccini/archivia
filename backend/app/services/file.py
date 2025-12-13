import asyncio
import hashlib
import os
import tempfile
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.models.file import File, FileChunk
from app.models.user import User
from app.services.minio import MinIOService
from app.schemas.file import FileCreate, FileUpdate
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class FileService:
    """File management service"""
    
    def __init__(self):
        self.minio_service = MinIOService()
        self.active_uploads: Dict[str, Dict] = {}
    
    async def initiate_file_upload(
        self, 
        db: Session, 
        user: User, 
        filename: str, 
        file_size: int, 
        content_type: Optional[str] = None
    ) -> Dict:
        """Initiate a file upload (multipart for large files)"""
        
        # Validate file size
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Generate unique object name for MinIO
        object_name = self.minio_service.generate_object_name(filename)
        
        # Determine if multipart upload is needed
        is_multipart = file_size > settings.CHUNK_SIZE
        
        # Create file record in database
        file_data = FileCreate(
            filename=filename,
            original_filename=filename,
            file_size=file_size,
            content_type=content_type or "application/octet-stream",
            minio_object_name=object_name,
            bucket_name=settings.MINIO_BUCKET_NAME,
            is_multipart=is_multipart
        )
        
        db_file = File(
            **file_data.dict(),
            owner_id=user.id
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        if is_multipart:
            # Initiate multipart upload
            upload_id = await self.minio_service.initiate_multipart_upload(
                object_name, content_type or "application/octet-stream"
            )
            
            # Update file record with upload_id
            db_file.upload_id = upload_id
            db.commit()
            
            # Calculate total chunks
            total_chunks = (file_size + settings.CHUNK_SIZE - 1) // settings.CHUNK_SIZE
            
            # Store upload session info
            self.active_uploads[str(db_file.id)] = {
                "upload_id": upload_id,
                "object_name": object_name,
                "total_chunks": total_chunks,
                "completed_parts": []
            }
            
            return {
                "message": "Multipart upload initiated",
                "file_id": db_file.id,
                "upload_id": upload_id,
                "chunk_size": settings.CHUNK_SIZE,
                "total_chunks": total_chunks,
                "is_multipart": True
            }
        else:
            return {
                "message": "Ready for single upload",
                "file_id": db_file.id,
                "is_multipart": False
            }
    
    async def upload_chunk(
        self,
        db: Session,
        file_id: int,
        chunk_number: int,
        chunk_data: UploadFile
    ) -> Dict:
        """Upload a file chunk"""
        
        # Get file record
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if not db_file.is_multipart:
            raise HTTPException(status_code=400, detail="File is not multipart")
        
        upload_session = self.active_uploads.get(str(file_id))
        if not upload_session:
            raise HTTPException(status_code=400, detail="Upload session not found")
        
        # Get presigned URL for this chunk
        upload_url = await self.minio_service.get_presigned_upload_url(
            upload_session["object_name"],
            upload_session["upload_id"],
            chunk_number
        )

        # Get chunk size without reading entire chunk into memory
        await chunk_data.seek(0, 2)  # Seek to end
        chunk_size = chunk_data.tell()
        await chunk_data.seek(0)  # Reset to beginning

        # Create chunk record
        chunk = FileChunk(
            file_id=file_id,
            chunk_number=chunk_number,
            chunk_size=chunk_size
        )
        
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        
        return {
            "message": "Chunk upload URL generated",
            "chunk_number": chunk_number,
            "upload_url": upload_url,
            "chunk_id": chunk.id
        }
    
    async def complete_multipart_upload(
        self,
        db: Session,
        file_id: int,
        parts: List[Dict]
    ) -> Dict:
        """Complete a multipart upload"""
        
        # Get file record
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        upload_session = self.active_uploads.get(str(file_id))
        if not upload_session:
            raise HTTPException(status_code=400, detail="Upload session not found")
        
        try:
            # Complete the multipart upload in MinIO
            etag = await self.minio_service.complete_multipart_upload(
                upload_session["object_name"],
                upload_session["upload_id"],
                parts
            )
            
            # Update file record
            db_file.upload_completed = True
            db_file.file_hash = etag
            db.commit()
            
            # Clean up upload session
            del self.active_uploads[str(file_id)]
            
            return {
                "message": "File upload completed successfully",
                "file_id": file_id,
                "etag": etag
            }
            
        except Exception as e:
            # Abort the upload if completion fails
            await self.minio_service.abort_multipart_upload(
                upload_session["object_name"],
                upload_session["upload_id"]
            )
            
            # Clean up upload session
            del self.active_uploads[str(file_id)]
            
            raise HTTPException(status_code=500, detail=f"Upload completion failed: {str(e)}")
    
    async def upload_single_file(
        self,
        db: Session,
        file_id: int,
        file_data: UploadFile
    ) -> Dict:
        """Upload a single file (for small files)"""
        
        # Get file record
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if db_file.is_multipart:
            raise HTTPException(status_code=400, detail="Use multipart upload for this file")
        
        try:
            # Calculate file hash using chunked reading to avoid loading entire file into memory
            await file_data.seek(0)
            file_hash = hashlib.sha256()

            # Read and hash in chunks (8KB at a time for memory efficiency)
            chunk_size = settings.HASH_CHUNK_SIZE
            while True:
                chunk = await file_data.read(chunk_size)
                if not chunk:
                    break
                file_hash.update(chunk)

            # Reset file position and upload to MinIO
            await file_data.seek(0)
            etag = await self.minio_service.upload_file(
                file_data.file,
                db_file.minio_object_name,
                db_file.content_type or "application/octet-stream"
            )
            
            # Update file record
            db_file.upload_completed = True
            db_file.file_hash = file_hash.hexdigest()
            db.commit()
            
            return {
                "message": "File uploaded successfully",
                "file_id": file_id,
                "etag": etag
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def get_file_download_url(self, db: Session, file_id: int, user_id: int) -> str:
        """Get a download URL for a file"""
        
        # Get file record
        db_file = db.query(File).filter(
            File.id == file_id,
            File.owner_id == user_id,
            File.upload_completed == True
        ).first()
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found or not accessible")
        
        # Generate download URL
        download_url = await self.minio_service.get_file_url(db_file.minio_object_name)
        return download_url
    
    async def stream_file(self, db: Session, file_id: int, user_id: int, thumbnail: bool = False):
        """Stream file content directly using chunked streaming

        Args:
            db: Database session
            file_id: File ID to stream
            user_id: User ID for access control
            thumbnail: If True, generate and return thumbnail for DNG files
        """
        from fastapi.responses import StreamingResponse, Response
        from app.utils.thumbnail_generator import get_thumbnail_generator
        import re

        # Get file record
        db_file = db.query(File).filter(
            File.id == file_id,
            File.owner_id == user_id
        ).first()

        if not db_file:
            raise HTTPException(status_code=404, detail="File not found or not accessible")

        # Check if this is a DNG file that needs thumbnail generation
        is_dng = self._is_dng_file(db_file.content_type, db_file.filename)

        # Get file content from MinIO
        try:
            file_data = self.minio_service.get_file(db_file.minio_object_name)

            # Generate thumbnail for DNG files (always for preview purposes)
            if is_dng:
                try:
                    thumbnail_gen = get_thumbnail_generator()
                    result = thumbnail_gen.generate_thumbnail(
                        file_data,
                        db_file.content_type,
                        db_file.filename
                    )

                    if result:
                        thumbnail_bytes, mime_type = result
                        logger.info(f"Generated thumbnail for DNG file {file_id}")

                        # Return thumbnail as response
                        return Response(
                            content=thumbnail_bytes,
                            media_type=mime_type,
                            headers={
                                "Content-Disposition": f'inline; filename="thumb_{db_file.filename}.jpg"',
                                "X-Original-Content-Type": db_file.content_type,
                                "X-Thumbnail-Generated": "true"
                            }
                        )
                    else:
                        logger.warning(f"Failed to generate thumbnail for DNG file {file_id}, serving original")
                        # Fall through to serve original file
                        file_data = self.minio_service.get_file(db_file.minio_object_name)

                except Exception as thumb_error:
                    logger.error(f"Error generating DNG thumbnail: {thumb_error}", exc_info=True)
                    # Fall through to serve original file
                    file_data = self.minio_service.get_file(db_file.minio_object_name)

            # Generator function to stream file in chunks (for non-DNG or if thumbnail failed)
            def file_stream_generator():
                chunk_size = settings.STREAMING_CHUNK_SIZE
                while True:
                    chunk = file_data.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

            # Sanitize filename for safety
            safe_filename = re.sub(r'[^\w\-_\.]', '_', db_file.filename).strip('. ')

            return StreamingResponse(
                file_stream_generator(),
                media_type=db_file.content_type or 'application/octet-stream',
                headers={
                    "Content-Disposition": f'inline; filename="{safe_filename}"',
                    "Content-Length": str(db_file.file_size)
                }
            )
        except Exception as e:
            logger.error(f"Error streaming file {file_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error accessing file")

    def _is_dng_file(self, content_type: str, filename: str) -> bool:
        """Check if file is a DNG file"""
        dng_mime_types = ['image/x-adobe-dng', 'image/dng', 'image/x-dng']
        if content_type and content_type in dng_mime_types:
            return True
        if filename and filename.lower().endswith('.dng'):
            return True
        return False
    
    def get_user_files(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[File]:
        """Get files for a user"""
        return db.query(File).filter(
            File.owner_id == user_id,
            File.upload_completed == True
        ).offset(skip).limit(limit).all()
    
    async def delete_file(self, db: Session, file_id: int, user_id: int) -> Dict:
        """Delete a file"""
        
        # Get file record
        db_file = db.query(File).filter(
            File.id == file_id,
            File.owner_id == user_id
        ).first()
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            # Delete from MinIO
            await self.minio_service.delete_file(db_file.minio_object_name)
            
            # Delete chunks if any
            db.query(FileChunk).filter(FileChunk.file_id == file_id).delete()
            
            # Delete file record
            db.delete(db_file)
            db.commit()
            
            return {"message": "File deleted successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
    
    async def upload_file(self, file: UploadFile, user_id: int, file_category: str = None) -> File:
        """
        Simple upload method for image files - handles the complete workflow

        Args:
            file: Uploaded file
            user_id: Owner user ID
            file_category: File category (master, export_high, etc.) - optional, defaults to 'other'
        """
        # Calculate file hash using chunked reading
        await file.seek(0)
        file_hash_obj = hashlib.sha256()
        chunk_size = settings.HASH_CHUNK_SIZE

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_hash_obj.update(chunk)

        file_hash = file_hash_obj.hexdigest()
        await file.seek(0)  # Reset for later use

        # Check if file already exists
        existing_file = self.db.query(File).filter(File.file_hash == file_hash).first()
        if existing_file:
            return existing_file

        # Get file size - use file.size attribute
        # Note: UploadFile.seek() only takes 1 argument, not 2
        file_size = file.size
        await file.seek(0)  # Reset to beginning

        mime_type = file.content_type or "application/octet-stream"

        # Generate consistent path using category-based structure
        from app.utils.minio_paths import get_minio_object_path
        category = file_category or 'other'
        object_name = get_minio_object_path(user_id, file_hash, category, file.filename)

        # Upload to MinIO using file object directly (streaming)
        await self.minio_service.upload_file(
            file.file,  # Pass file object for streaming
            object_name,
            mime_type
        )

        # Create file record
        db_file = File(
            filename=file.filename,
            original_filename=file.filename,
            minio_object_name=object_name,  # Use correct attribute name
            bucket_name=settings.MINIO_BUCKET_NAME,
            file_size=file_size,
            content_type=mime_type,  # Use correct attribute name
            file_hash=file_hash,  # Use correct attribute name
            owner_id=user_id,
            upload_completed=True
        )
        
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        
        return db_file

    # ...existing code...
