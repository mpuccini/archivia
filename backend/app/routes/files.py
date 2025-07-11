from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.services.file import FileService
from app.models.user import User
from app.models.file import File
from app.schemas.file import (
    FileUploadResponse, FileResponse, ChunkUploadRequest, 
    ChunkUploadResponse, CompleteUploadRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])
file_service = FileService()


@router.post("/upload/initiate", response_model=FileUploadResponse)
async def initiate_upload(
    filename: str = Form(...),
    file_size: int = Form(...),
    content_type: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a file upload (multipart for large files)"""
    try:
        result = await file_service.initiate_file_upload(
            db, current_user, filename, file_size, content_type
        )
        return FileUploadResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating upload: {e}")
        raise HTTPException(status_code=500, detail="Error initiating upload")


@router.post("/upload/chunk/{file_id}")
async def upload_chunk(
    file_id: int,
    chunk_number: int = Form(...),
    chunk: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a single chunk for multipart upload"""
    try:
        result = await file_service.upload_chunk(db, file_id, chunk_number, chunk)
        return ChunkUploadResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading chunk: {e}")
        raise HTTPException(status_code=500, detail="Error uploading chunk")


@router.post("/upload/complete/{file_id}")
async def complete_upload(
    file_id: int,
    request: CompleteUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a multipart upload"""
    try:
        result = await file_service.complete_multipart_upload(db, file_id, request.parts)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing upload: {e}")
        raise HTTPException(status_code=500, detail="Error completing upload")


@router.post("/upload/single/{file_id}")
async def upload_single_file(
    file_id: int,
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a single file (for small files)"""
    try:
        result = await file_service.upload_single_file(db, file_id, file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Error uploading file")


@router.get("/", response_model=List[FileResponse])
async def list_files(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user files"""
    try:
        files = file_service.get_user_files(db, current_user.id, skip, limit)
        return [FileResponse.model_validate(file) for file in files]
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail="Error listing files")


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get download URL for a file"""
    try:
        download_url = await file_service.get_file_download_url(db, file_id, current_user.id)
        return {"download_url": download_url}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating download URL")


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file information"""
    try:
        file = db.query(File).filter(
            File.id == file_id,
            File.owner_id == current_user.id
        ).first()
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse.model_validate(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file: {e}")
        raise HTTPException(status_code=500, detail="Error getting file")


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file"""
    try:
        result = await file_service.delete_file(db, file_id, current_user.id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Error deleting file")
