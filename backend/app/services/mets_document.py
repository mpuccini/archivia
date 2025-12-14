"""
METS Document Service - Business logic for METS ECO-MiC metadata operations
"""
from typing import Optional, Dict, Any
from datetime import datetime
from app.services.mongodb import MongoDBService
import logging

logger = logging.getLogger(__name__)


class METSDocumentService:
    """Service for METS ECO-MiC document operations"""

    def __init__(self, mongodb_service: MongoDBService):
        self.mongodb = mongodb_service

    async def create_mets_document(
        self,
        logical_id: str,
        owner_id: int,
        platform_document_id: int,
        metadata: Dict[str, Any],
        schema_version: str = "1.2"
    ) -> str:
        """
        Create METS document in MongoDB

        Args:
            logical_id: Unique logical identifier
            owner_id: User ID who owns this document
            platform_document_id: PostgreSQL document.id reference
            metadata: METS metadata dictionary
            schema_version: ECO-MiC version ("1.1" or "1.2")

        Returns:
            MongoDB ObjectId as string
        """
        now = datetime.utcnow()

        # Build complete METS document
        document = {
            "schema_version": schema_version,
            "logical_id": logical_id,
            "platform_document_id": platform_document_id,
            "owner_id": owner_id,
            "created_at": now,
            "updated_at": now,
            **metadata
        }

        mets_id = await self.mongodb.create_mets_document(document)
        logger.info(f"Created METS document {mets_id} for logical_id {logical_id} (schema v{schema_version})")
        return mets_id

    async def get_mets_document(self, mets_id: str) -> Optional[Dict[str, Any]]:
        """
        Get METS document by MongoDB ID

        Args:
            mets_id: MongoDB ObjectId as string

        Returns:
            METS document dictionary or None
        """
        return await self.mongodb.get_mets_document(mets_id)

    async def get_mets_document_by_logical_id(self, logical_id: str) -> Optional[Dict[str, Any]]:
        """
        Get METS document by logical_id

        Args:
            logical_id: Logical identifier

        Returns:
            METS document dictionary or None
        """
        return await self.mongodb.get_mets_document_by_logical_id(logical_id)

    async def update_mets_document(
        self, mets_id: str, metadata_updates: Dict[str, Any]
    ) -> bool:
        """
        Update METS metadata

        Args:
            mets_id: MongoDB ObjectId as string
            metadata_updates: Dictionary of fields to update

        Returns:
            True if updated successfully
        """
        success = await self.mongodb.update_mets_document(mets_id, metadata_updates)
        if success:
            logger.info(f"Updated METS document {mets_id}")
        return success

    async def delete_mets_document(self, mets_id: str) -> bool:
        """
        Delete METS document

        Args:
            mets_id: MongoDB ObjectId as string

        Returns:
            True if deleted successfully
        """
        success = await self.mongodb.delete_mets_document(mets_id)
        if success:
            logger.info(f"Deleted METS document {mets_id}")
        return success

    async def list_mets_documents(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list:
        """
        List METS documents for a user

        Args:
            owner_id: User ID
            skip: Number to skip for pagination
            limit: Maximum number to return

        Returns:
            List of METS documents
        """
        return await self.mongodb.list_mets_documents(owner_id, skip, limit)

    def extract_mets_metadata_from_document_data(
        self, document_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract METS-specific metadata from document creation data

        Args:
            document_data: Complete document data including platform and METS fields

        Returns:
            Dictionary containing only METS metadata fields
        """
        # Define which fields belong in MongoDB (METS metadata)
        mets_fields = {
            # Core identifiers
            'conservative_id',
            'conservative_id_authority',
            'title',
            'description',
            'type_of_resource',

            # Archive hierarchy
            'archive_name',
            'archive_contact',
            'fund_name',
            'series_name',
            'folder_number',

            # Temporal
            'date_from',
            'date_to',
            'period',

            # Geographic/Contextual
            'location',
            'language',
            'subjects',

            # Agents
            'producer_name',
            'producer_type',
            'producer_role',
            'creator_name',
            'creator_type',
            'creator_role',

            # Rights
            'license_url',
            'rights_statement',
            'rights_category',
            'rights_holder',
            'rights_constraint',

            # Technical (document-level)
            'image_producer',
            'scanner_manufacturer',
            'scanner_model',

            # Physical
            'document_type',
            'total_pages',
            'physical_form',
            'extent_description',

            # METS header
            'record_status',
        }

        # Extract and structure metadata
        metadata = {}

        # Direct fields
        for field in mets_fields:
            if field in document_data and document_data[field] is not None:
                metadata[field] = document_data[field]

        # Structure nested fields for better MongoDB organization
        if any(k in document_data for k in ['archive_name', 'archive_contact', 'fund_name', 'series_name', 'folder_number']):
            metadata['archive'] = {
                'name': document_data.get('archive_name'),
                'contact': document_data.get('archive_contact'),
                'fund_name': document_data.get('fund_name'),
                'series_name': document_data.get('series_name'),
                'folder_number': document_data.get('folder_number'),
            }
            # Remove from top level
            for k in ['archive_name', 'archive_contact', 'fund_name', 'series_name', 'folder_number']:
                metadata.pop(k, None)

        if any(k in document_data for k in ['date_from', 'date_to', 'period']):
            metadata['temporal'] = {
                'date_from': document_data.get('date_from'),
                'date_to': document_data.get('date_to'),
                'period': document_data.get('period'),
            }
            for k in ['date_from', 'date_to', 'period']:
                metadata.pop(k, None)

        if any(k in document_data for k in ['producer_name', 'producer_type', 'producer_role', 'creator_name', 'creator_type', 'creator_role']):
            metadata['agents'] = {}
            if document_data.get('producer_name'):
                metadata['agents']['producer'] = {
                    'name': document_data.get('producer_name'),
                    'type': document_data.get('producer_type'),
                    'role': document_data.get('producer_role'),
                }
            if document_data.get('creator_name'):
                metadata['agents']['creator'] = {
                    'name': document_data.get('creator_name'),
                    'type': document_data.get('creator_type'),
                    'role': document_data.get('creator_role'),
                }
            for k in ['producer_name', 'producer_type', 'producer_role', 'creator_name', 'creator_type', 'creator_role']:
                metadata.pop(k, None)

        if any(k in document_data for k in ['license_url', 'rights_statement', 'rights_category', 'rights_holder', 'rights_constraint']):
            metadata['rights'] = {
                'license_url': document_data.get('license_url'),
                'rights_statement': document_data.get('rights_statement'),
                'category': document_data.get('rights_category'),
                'holder': document_data.get('rights_holder'),
                'constraint': document_data.get('rights_constraint'),
            }
            for k in ['license_url', 'rights_statement', 'rights_category', 'rights_holder', 'rights_constraint']:
                metadata.pop(k, None)

        if any(k in document_data for k in ['image_producer', 'scanner_manufacturer', 'scanner_model']):
            metadata['technical'] = {
                'image_producer': document_data.get('image_producer'),
                'scanner_manufacturer': document_data.get('scanner_manufacturer'),
                'scanner_model': document_data.get('scanner_model'),
            }
            for k in ['image_producer', 'scanner_manufacturer', 'scanner_model']:
                metadata.pop(k, None)

        if any(k in document_data for k in ['document_type', 'total_pages', 'physical_form', 'extent_description']):
            metadata['physical'] = {
                'document_type': document_data.get('document_type'),
                'total_pages': document_data.get('total_pages'),
                'physical_form': document_data.get('physical_form'),
                'extent_description': document_data.get('extent_description'),
            }
            for k in ['document_type', 'total_pages', 'physical_form', 'extent_description']:
                metadata.pop(k, None)

        if 'record_status' in document_data:
            metadata['mets_header'] = {
                'record_status': document_data.get('record_status', 'COMPLETE'),
                'profile': 'http://www.iccu.sbn.it/metaAG1.pdf'
            }
            metadata.pop('record_status', None)

        return metadata
