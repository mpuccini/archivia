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
        
        # Create chunk record
        chunk = FileChunk(
            file_id=file_id,
            chunk_number=chunk_number,
            chunk_size=len(await chunk_data.read())
        )
        
        # Reset file pointer
        await chunk_data.seek(0)
        
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
            # Calculate file hash first
            await file_data.seek(0)
            file_hash = hashlib.sha256()
            file_content = await file_data.read()
            file_hash.update(file_content)
            
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
