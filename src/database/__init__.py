"""
Unified database package providing access to PostgreSQL and MongoDB connections.
"""

from typing import Dict, Any
import logging

# Import PostgreSQL components
from .postgresql import (
    PostgreSQLConnection,
    SyncPostgreSQLConnection,
    postgres_db,
    sync_postgres_db
)

# Import MongoDB components
from .mongodb import (
    MongoDBConnection,
    SyncMongoDBConnection,
    mongodb,
    sync_mongodb
)

# Import shared exceptions
from .postgresql import DatabaseError

from config import config

logger = logging.getLogger(__name__)

# Backward compatibility - maintain original names
db = postgres_db
sync_db = sync_postgres_db

# Export all components
__all__ = [
    # PostgreSQL
    'PostgreSQLConnection',
    'SyncPostgreSQLConnection',
    'postgres_db',
    'sync_postgres_db',
    'db',  # backward compatibility alias
    'sync_db',  # backward compatibility alias

    # MongoDB
    'MongoDBConnection',
    'SyncMongoDBConnection',
    'mongodb',
    'sync_mongodb',

    # Exceptions
    'DatabaseError',

    # Functions
    'init_database',
    'close_database',
    'get_database_info'
]


async def init_database():
    """Initialize all database connections."""
    logger.info("Initializing database connections...")

    try:
        # Initialize PostgreSQL
        await postgres_db.initialize_pool()
        logger.info("PostgreSQL connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL: {e}")
        raise

    try:
        # Initialize MongoDB
        await mongodb.initialize_client()
        logger.info("MongoDB connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise

    logger.info("All database connections initialized successfully")


async def close_database():
    """Close all database connections."""
    logger.info("Closing database connections...")

    try:
        await postgres_db.close_pool()
        logger.info("PostgreSQL connection closed")
    except Exception as e:
        logger.error(f"Error closing PostgreSQL: {e}")

    try:
        await mongodb.close_client()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB: {e}")

    logger.info("All database connections closed")


def get_database_info() -> Dict[str, Any]:
    """Get comprehensive database connection information."""
    return {
        "databases": {
            "postgresql": {
                "host": config.postgres_host,
                "port": config.postgres_port,
                "database": config.postgres_db,
                "user": config.postgres_user,
                "connected": sync_postgres_db.test_connection(),
                "type": "relational"
            },
            "mongodb": {
                "host": config.mongodb_host,
                "port": config.mongodb_port,
                "database": config.mongodb_db,
                "user": config.mongodb_user,
                "connected": sync_mongodb.test_connection(),
                "type": "document"
            }
        },
        "summary": {
            "total_databases": 2,
            "connected_count": sum([
                sync_postgres_db.test_connection(),
                sync_mongodb.test_connection()
            ])
        }
    }