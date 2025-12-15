"""
MongoDB service for METS ECO-MiC metadata storage
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from typing import Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDBService:
    """MongoDB service for METS ECO-MiC metadata storage"""

    def __init__(self):
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.async_db: Optional[AsyncIOMotorDatabase] = None

    async def connect_async(self):
        """Connect to MongoDB (async)"""
        try:
            self.async_client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.async_db = self.async_client.get_database()

            # Verify connection
            await self.async_client.admin.command('ping')
            logger.info("MongoDB async connection established")

            # Create indexes
            await self._create_indexes()

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close_async(self):
        """Close async connection"""
        if self.async_client:
            self.async_client.close()
            logger.info("MongoDB async connection closed")

    async def _create_indexes(self):
        """Create required indexes on mets_documents collection"""
        mets_collection = self.async_db.mets_documents

        # Unique index on logical_id
        await mets_collection.create_index("logical_id", unique=True)

        # Index on owner_id for user queries
        await mets_collection.create_index("owner_id")

        # Index on archive.name for filtering
        await mets_collection.create_index("archive.name")

        # Index on schema_version for version-specific queries
        await mets_collection.create_index("schema_version")

        # Index on created_at for sorting
        await mets_collection.create_index([("created_at", -1)])

        # Index on temporal date fields
        await mets_collection.create_index("temporal.date_from")
        await mets_collection.create_index("temporal.date_to")

        # Full-text search index with Italian language support
        # Weighted fields: title (highest), description, archive fields, subjects, agents
        await mets_collection.create_index(
            [
                ("title", "text"),
                ("description", "text"),
                ("conservative_id", "text"),
                ("archive.name", "text"),
                ("archive.fund_name", "text"),
                ("archive.series_name", "text"),
                ("subjects", "text"),
                ("location", "text"),
                ("agents.producer.name", "text"),
                ("agents.creator.name", "text")
            ],
            name="fulltext_search_idx",
            weights={
                "title": 10,
                "conservative_id": 8,
                "description": 5,
                "archive.name": 3,
                "archive.fund_name": 3,
                "subjects": 3,
                "agents.creator.name": 2,
                "agents.producer.name": 2,
                "location": 1,
                "archive.series_name": 1
            },
            default_language="italian"
        )

        logger.info("MongoDB indexes created successfully")

    async def create_mets_document(self, document_data: Dict[str, Any]) -> str:
        """
        Create METS document in MongoDB

        Args:
            document_data: Dictionary containing METS metadata

        Returns:
            String representation of MongoDB ObjectId
        """
        result = await self.async_db.mets_documents.insert_one(document_data)
        return str(result.inserted_id)

    async def get_mets_document(self, mets_id: str) -> Optional[Dict[str, Any]]:
        """
        Get METS document by MongoDB ObjectId

        Args:
            mets_id: String representation of MongoDB ObjectId

        Returns:
            METS document dictionary or None if not found
        """
        try:
            doc = await self.async_db.mets_documents.find_one(
                {"_id": ObjectId(mets_id)}
            )
            if doc:
                # Convert ObjectId to string for JSON serialization
                doc['_id'] = str(doc['_id'])
            return doc
        except Exception as e:
            logger.error(f"Error fetching METS document {mets_id}: {e}")
            return None

    async def get_mets_document_by_logical_id(self, logical_id: str) -> Optional[Dict[str, Any]]:
        """
        Get METS document by logical_id

        Args:
            logical_id: Logical identifier of the document

        Returns:
            METS document dictionary or None if not found
        """
        try:
            doc = await self.async_db.mets_documents.find_one(
                {"logical_id": logical_id}
            )
            if doc:
                doc['_id'] = str(doc['_id'])
            return doc
        except Exception as e:
            logger.error(f"Error fetching METS document by logical_id {logical_id}: {e}")
            return None

    async def update_mets_document(
        self, mets_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """
        Update METS document

        Args:
            mets_id: String representation of MongoDB ObjectId
            update_data: Dictionary of fields to update

        Returns:
            True if document was modified, False otherwise
        """
        try:
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.utcnow()

            result = await self.async_db.mets_documents.update_one(
                {"_id": ObjectId(mets_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating METS document {mets_id}: {e}")
            return False

    async def delete_mets_document(self, mets_id: str) -> bool:
        """
        Delete METS document

        Args:
            mets_id: String representation of MongoDB ObjectId

        Returns:
            True if document was deleted, False otherwise
        """
        try:
            result = await self.async_db.mets_documents.delete_one(
                {"_id": ObjectId(mets_id)}
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting METS document {mets_id}: {e}")
            return False

    async def list_mets_documents(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """
        List METS documents for a user

        Args:
            owner_id: User ID
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of METS documents
        """
        try:
            cursor = self.async_db.mets_documents.find(
                {"owner_id": owner_id}
            ).sort("created_at", -1).skip(skip).limit(limit)

            documents = await cursor.to_list(length=limit)

            # Convert ObjectIds to strings
            for doc in documents:
                doc['_id'] = str(doc['_id'])

            return documents
        except Exception as e:
            logger.error(f"Error listing METS documents for user {owner_id}: {e}")
            return []

    async def search_documents(
        self,
        owner_id: int,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search METS documents with full-text search and filters

        Args:
            owner_id: User ID
            query: Full-text search query
            filters: Dictionary of filters (logical_id, archive, date_from, date_to, schema_version)
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return

        Returns:
            Dictionary with 'items' (list of documents), 'total' (total count), and metadata
        """
        try:
            mets_collection = self.async_db.mets_documents
            filters = filters or {}

            # Build MongoDB filter
            match_filter = {"owner_id": owner_id}

            # Full-text search
            if query:
                match_filter["$text"] = {"$search": query}

            # Additional filters
            if filters.get('logical_id'):
                match_filter["logical_id"] = {
                    "$regex": filters['logical_id'],
                    "$options": "i"
                }

            if filters.get('archive'):
                match_filter["archive.name"] = {
                    "$regex": filters['archive'],
                    "$options": "i"
                }

            if filters.get('schema_version'):
                match_filter["schema_version"] = filters['schema_version']

            # Date range filters
            if filters.get('date_from') or filters.get('date_to'):
                temporal_filter = {}
                if filters.get('date_from'):
                    temporal_filter["$gte"] = filters['date_from']
                if filters.get('date_to'):
                    temporal_filter["$lte"] = filters['date_to']

                if temporal_filter:
                    match_filter["temporal.date_from"] = temporal_filter

            # Build aggregation pipeline
            pipeline = [
                {"$match": match_filter}
            ]

            # Add text score if full-text search
            if query:
                pipeline.append({
                    "$addFields": {
                        "search_score": {"$meta": "textScore"}
                    }
                })
                pipeline.append({"$sort": {"search_score": -1}})
            else:
                # Sort by created_at if no text search
                pipeline.append({"$sort": {"created_at": -1}})

            # Get total count
            count_pipeline = pipeline.copy()
            count_pipeline.append({"$count": "total"})
            count_result = await mets_collection.aggregate(count_pipeline).to_list(1)
            total = count_result[0]['total'] if count_result else 0

            # Add pagination
            pipeline.append({"$skip": skip})
            pipeline.append({"$limit": limit})

            # Execute search
            cursor = mets_collection.aggregate(pipeline)
            documents = await cursor.to_list(length=limit)

            # Convert ObjectIds to strings
            for doc in documents:
                doc['_id'] = str(doc['_id'])

            return {
                "items": documents,
                "total": total,
                "skip": skip,
                "limit": limit
            }

        except Exception as e:
            logger.error(f"Error searching METS documents: {e}")
            return {
                "items": [],
                "total": 0,
                "skip": skip,
                "limit": limit
            }


# Global instance
mongodb_service = MongoDBService()


async def get_mongodb() -> AsyncIOMotorDatabase:
    """
    Dependency for FastAPI endpoints

    Returns:
        MongoDB database instance
    """
    return mongodb_service.async_db
