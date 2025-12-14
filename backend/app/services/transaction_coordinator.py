"""
Transaction Coordinator - Coordinate operations across PostgreSQL, MongoDB, and MinIO
"""
from typing import Optional, Dict, Any, Callable, Awaitable, List
from sqlalchemy.orm import Session
from app.services.mets_document import METSDocumentService
from app.services.minio import MinIOService
import logging

logger = logging.getLogger(__name__)


class TransactionCoordinator:
    """
    Coordinate transactions across PostgreSQL, MongoDB, and MinIO

    Implements 3-phase commit pattern with rollback capability to ensure
    consistency across all three storage systems.
    """

    def __init__(
        self,
        postgres_session: Session,
        mets_service: METSDocumentService,
        minio_service: MinIOService
    ):
        self.postgres = postgres_session
        self.mets = mets_service
        self.minio = minio_service

    async def execute_document_creation(
        self,
        postgres_op: Callable[[], int],  # Returns document_id
        mets_op: Callable[[int], Awaitable[str]],  # Takes doc_id, returns mets_id
        minio_ops: Optional[List[Callable[[], Awaitable[str]]]] = None  # List of file upload operations
    ) -> Dict[str, Any]:
        """
        Execute document creation with 3-phase commit and rollback capability.

        Phase 1: PostgreSQL (create platform document record)
        Phase 2: MongoDB (create METS metadata)
        Phase 3: MinIO (upload files if any)

        If any phase fails, all previous phases are rolled back in reverse order.

        Args:
            postgres_op: Function that creates PostgreSQL document, returns document.id
            mets_op: Async function that creates MongoDB METS document, takes postgres doc_id, returns mets_id
            minio_ops: Optional list of async functions that upload files to MinIO, each returns object_name

        Returns:
            Dictionary with success status and IDs:
            {
                "success": True,
                "postgres_doc_id": int,
                "mets_id": str,
                "minio_objects": List[str]
            }

        Raises:
            Exception: If transaction fails and rollback cannot recover
        """
        postgres_doc_id = None
        mets_id = None
        minio_objects = []

        try:
            # Phase 1: PostgreSQL (platform record)
            logger.info("Phase 1: Creating PostgreSQL document record")
            postgres_doc_id = postgres_op()
            self.postgres.commit()
            logger.info(f"Phase 1 complete: PostgreSQL document {postgres_doc_id} created")

            # Phase 2: MongoDB (METS metadata)
            logger.info(f"Phase 2: Creating MongoDB METS document for doc {postgres_doc_id}")
            mets_id = await mets_op(postgres_doc_id)
            logger.info(f"Phase 2 complete: MongoDB METS document {mets_id} created")

            # Phase 3: MinIO (files if any)
            if minio_ops:
                logger.info(f"Phase 3: Uploading {len(minio_ops)} files to MinIO")
                for idx, minio_op in enumerate(minio_ops, 1):
                    object_name = await minio_op()
                    minio_objects.append(object_name)
                    logger.debug(f"Phase 3: Uploaded file {idx}/{len(minio_ops)}: {object_name}")
                logger.info(f"Phase 3 complete: {len(minio_objects)} files uploaded to MinIO")

            logger.info(f"Transaction complete: doc_id={postgres_doc_id}, mets_id={mets_id}, files={len(minio_objects)}")

            return {
                "success": True,
                "postgres_doc_id": postgres_doc_id,
                "mets_id": mets_id,
                "minio_objects": minio_objects
            }

        except Exception as e:
            logger.error(f"Transaction failed: {e}", exc_info=True)
            logger.info("Rolling back transaction in reverse order...")

            # Rollback in REVERSE order (MinIO → MongoDB → PostgreSQL)

            # Rollback MinIO (Phase 3)
            for object_name in minio_objects:
                try:
                    logger.debug(f"Rolling back MinIO object: {object_name}")
                    self.minio.delete_file(object_name)
                except Exception as me:
                    logger.error(f"MinIO rollback failed for {object_name}: {me}")

            # Rollback MongoDB (Phase 2)
            if mets_id:
                try:
                    logger.debug(f"Rolling back MongoDB METS document: {mets_id}")
                    await self.mets.delete_mets_document(mets_id)
                except Exception as me:
                    logger.error(f"MongoDB rollback failed for {mets_id}: {me}")

            # Rollback PostgreSQL (Phase 1)
            if postgres_doc_id:
                try:
                    logger.debug(f"Rolling back PostgreSQL document: {postgres_doc_id}")
                    self.postgres.rollback()
                except Exception as pe:
                    logger.error(f"PostgreSQL rollback failed: {pe}")

            logger.error("Transaction rolled back due to error")
            raise

    async def execute_document_update(
        self,
        mets_id: str,
        mets_update_op: Callable[[], Awaitable[bool]],
        postgres_update_op: Optional[Callable[[], None]] = None
    ) -> bool:
        """
        Execute document update (primarily METS metadata updates)

        Args:
            mets_id: MongoDB METS document ID
            mets_update_op: Async function that updates MongoDB METS document
            postgres_update_op: Optional function that updates PostgreSQL (e.g., timestamp)

        Returns:
            True if successful
        """
        try:
            # Update MongoDB
            logger.info(f"Updating MongoDB METS document: {mets_id}")
            success = await mets_update_op()

            if not success:
                logger.warning(f"MongoDB update returned False for {mets_id}")
                return False

            # Update PostgreSQL if provided (e.g., updated_at timestamp)
            if postgres_update_op:
                logger.debug("Updating PostgreSQL document")
                postgres_update_op()
                self.postgres.commit()

            logger.info(f"Document update complete: mets_id={mets_id}")
            return True

        except Exception as e:
            logger.error(f"Document update failed: {e}", exc_info=True)
            if postgres_update_op:
                self.postgres.rollback()
            return False

    async def execute_document_deletion(
        self,
        mets_id: str,
        postgres_op: Callable[[], bool],
        minio_objects: List[str]
    ) -> bool:
        """
        Delete document from all three stores

        Deletion order: MinIO → MongoDB → PostgreSQL
        (Delete external resources first, then metadata, then platform record)

        Args:
            mets_id: MongoDB METS document ID
            postgres_op: Function that deletes PostgreSQL document
            minio_objects: List of MinIO object names to delete

        Returns:
            True if successful
        """
        try:
            # Delete MinIO objects first
            logger.info(f"Deleting {len(minio_objects)} files from MinIO")
            for object_name in minio_objects:
                try:
                    self.minio.delete_file(object_name)
                    logger.debug(f"Deleted MinIO object: {object_name}")
                except Exception as e:
                    logger.error(f"Failed to delete MinIO object {object_name}: {e}")
                    # Continue with other deletions even if one fails

            # Delete MongoDB document
            logger.info(f"Deleting MongoDB METS document: {mets_id}")
            await self.mets.delete_mets_document(mets_id)

            # Delete PostgreSQL record
            logger.info("Deleting PostgreSQL document")
            postgres_op()
            self.postgres.commit()

            logger.info(f"Document deletion complete: mets_id={mets_id}, files={len(minio_objects)}")
            return True

        except Exception as e:
            logger.error(f"Document deletion failed: {e}", exc_info=True)
            self.postgres.rollback()
            return False

    async def execute_file_addition(
        self,
        postgres_file_op: Callable[[], int],  # Returns file_id
        minio_upload_op: Callable[[], Awaitable[str]]  # Returns object_name
    ) -> Dict[str, Any]:
        """
        Add file to existing document (PostgreSQL + MinIO only)

        Args:
            postgres_file_op: Function that creates PostgreSQL file record, returns file_id
            minio_upload_op: Async function that uploads file to MinIO, returns object_name

        Returns:
            Dictionary with file_id and object_name
        """
        file_id = None
        object_name = None

        try:
            # Upload to MinIO first
            logger.info("Uploading file to MinIO")
            object_name = await minio_upload_op()
            logger.info(f"File uploaded to MinIO: {object_name}")

            # Create PostgreSQL record
            logger.info("Creating PostgreSQL file record")
            file_id = postgres_file_op()
            self.postgres.commit()
            logger.info(f"File record created: file_id={file_id}")

            return {
                "success": True,
                "file_id": file_id,
                "object_name": object_name
            }

        except Exception as e:
            logger.error(f"File addition failed: {e}", exc_info=True)

            # Rollback
            if object_name:
                try:
                    logger.debug(f"Rolling back MinIO object: {object_name}")
                    self.minio.delete_file(object_name)
                except Exception as me:
                    logger.error(f"MinIO rollback failed: {me}")

            if file_id:
                try:
                    logger.debug("Rolling back PostgreSQL file record")
                    self.postgres.rollback()
                except Exception as pe:
                    logger.error(f"PostgreSQL rollback failed: {pe}")

            raise
