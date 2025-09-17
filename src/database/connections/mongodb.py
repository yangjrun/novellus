"""
MongoDB database connection and query utilities.
"""

import motor.motor_asyncio
import pymongo
from typing import List, Dict, Any, Optional
import logging

from config import config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class MongoDBConnection:
    """MongoDB connection manager using Motor (async)."""

    def __init__(self):
        self._client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self._database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

    async def initialize_client(self) -> None:
        """Initialize MongoDB client and database."""
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(config.mongodb_url)
            self._database = self._client[config.mongodb_db]

            # Test connection
            await self._client.admin.command('ping')
            logger.info("MongoDB connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            raise DatabaseError(f"Failed to connect to MongoDB: {e}")

    async def close_client(self) -> None:
        """Close MongoDB client."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")

    @property
    def database(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Get the MongoDB database instance."""
        if self._database is None:
            raise DatabaseError("MongoDB not initialized. Call initialize_client() first.")
        return self._database

    def get_collection(self, name: str) -> motor.motor_asyncio.AsyncIOMotorCollection:
        """Get a collection by name."""
        return self.database[name]

    async def find_one(self, collection_name: str, filter_dict: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find one document in a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.find_one(filter_dict or {})
            return result
        except Exception as e:
            logger.error(f"MongoDB find_one failed: {e}")
            raise DatabaseError(f"Find operation failed: {e}")

    async def find_many(self, collection_name: str, filter_dict: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection."""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter_dict or {})
            if limit:
                cursor = cursor.limit(limit)

            results = []
            async for document in cursor:
                results.append(document)
            return results
        except Exception as e:
            logger.error(f"MongoDB find_many failed: {e}")
            raise DatabaseError(f"Find operation failed: {e}")

    async def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert one document into a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"MongoDB insert_one failed: {e}")
            raise DatabaseError(f"Insert operation failed: {e}")

    async def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents into a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.insert_many(documents)
            return [str(obj_id) for obj_id in result.inserted_ids]
        except Exception as e:
            logger.error(f"MongoDB insert_many failed: {e}")
            raise DatabaseError(f"Insert operation failed: {e}")

    async def update_one(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        """Update one document in a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.update_one(filter_dict, {"$set": update_dict})
            return result.modified_count
        except Exception as e:
            logger.error(f"MongoDB update_one failed: {e}")
            raise DatabaseError(f"Update operation failed: {e}")

    async def update_many(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        """Update multiple documents in a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.update_many(filter_dict, {"$set": update_dict})
            return result.modified_count
        except Exception as e:
            logger.error(f"MongoDB update_many failed: {e}")
            raise DatabaseError(f"Update operation failed: {e}")

    async def delete_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> int:
        """Delete one document from a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.delete_one(filter_dict)
            return result.deleted_count
        except Exception as e:
            logger.error(f"MongoDB delete_one failed: {e}")
            raise DatabaseError(f"Delete operation failed: {e}")

    async def delete_many(self, collection_name: str, filter_dict: Dict[str, Any]) -> int:
        """Delete multiple documents from a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.delete_many(filter_dict)
            return result.deleted_count
        except Exception as e:
            logger.error(f"MongoDB delete_many failed: {e}")
            raise DatabaseError(f"Delete operation failed: {e}")

    async def aggregate(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline."""
        try:
            collection = self.get_collection(collection_name)
            results = []
            async for document in collection.aggregate(pipeline):
                results.append(document)
            return results
        except Exception as e:
            logger.error(f"MongoDB aggregate failed: {e}")
            raise DatabaseError(f"Aggregation failed: {e}")

    async def create_index(self, collection_name: str, index_spec: Dict[str, Any], **kwargs) -> str:
        """Create an index on a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.create_index([(key, direction) for key, direction in index_spec.items()], **kwargs)
            return result
        except Exception as e:
            logger.error(f"MongoDB create_index failed: {e}")
            raise DatabaseError(f"Index creation failed: {e}")


class SyncMongoDBConnection:
    """Synchronous MongoDB connection for simple operations."""

    def __init__(self):
        self._client: Optional[pymongo.MongoClient] = None
        self._database: Optional[pymongo.database.Database] = None

    def initialize_client(self) -> None:
        """Initialize MongoDB client and database."""
        try:
            self._client = pymongo.MongoClient(config.mongodb_url)
            self._database = self._client[config.mongodb_db]

            # Test connection
            self._client.admin.command('ping')
            logger.info("Sync MongoDB connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sync MongoDB client: {e}")
            raise DatabaseError(f"Failed to connect to MongoDB: {e}")

    def close_client(self) -> None:
        """Close MongoDB client."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("Sync MongoDB connection closed")

    @property
    def database(self) -> pymongo.database.Database:
        """Get the MongoDB database instance."""
        if self._database is None:
            raise DatabaseError("MongoDB not initialized. Call initialize_client() first.")
        return self._database

    def get_collection(self, name: str) -> pymongo.collection.Collection:
        """Get a collection by name."""
        return self.database[name]

    def find_one(self, collection_name: str, filter_dict: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find one document in a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one(filter_dict or {})
            return result
        except Exception as e:
            logger.error(f"Sync MongoDB find_one failed: {e}")
            raise DatabaseError(f"Find operation failed: {e}")

    def find_many(self, collection_name: str, filter_dict: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection."""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter_dict or {})
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Sync MongoDB find_many failed: {e}")
            raise DatabaseError(f"Find operation failed: {e}")

    def test_connection(self) -> bool:
        """Test MongoDB connection."""
        try:
            if not self._client:
                self.initialize_client()
            self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB connection test failed: {e}")
            return False


# Module-level instances
mongodb = MongoDBConnection()
sync_mongodb = SyncMongoDBConnection()