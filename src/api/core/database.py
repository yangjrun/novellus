"""
Database Integration for FastAPI
Handles database connections and provides database dependencies
"""

import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging

from database.connection_manager import DatabaseConnectionManager
from database.data_access import (
    init_database as init_db,
    close_database as close_db,
    get_global_manager,
    get_novel_manager,
    get_database_health as get_db_health,
    DatabaseError
)
from database.repositories.cultural_framework_repository import CulturalFrameworkRepository
from database.law_chain_manager import LawChainManager
from database.batch_manager import get_batch_manager

logger = logging.getLogger(__name__)

# Global instances
_connection_manager: Optional[DatabaseConnectionManager] = None
_cultural_repository: Optional[CulturalFrameworkRepository] = None
_law_chain_manager: Optional[LawChainManager] = None


async def init_database():
    """Initialize database connections and repositories"""
    global _connection_manager, _cultural_repository, _law_chain_manager

    try:
        # Initialize main database
        await init_db()
        logger.info("Main database initialized")

        # Initialize connection manager for repositories
        _connection_manager = DatabaseConnectionManager()
        await _connection_manager.initialize()
        logger.info("Connection manager initialized")

        # Initialize cultural framework repository
        _cultural_repository = CulturalFrameworkRepository(_connection_manager)
        await _cultural_repository.initialize()
        logger.info("Cultural framework repository initialized")

        # Initialize law chain manager
        _law_chain_manager = LawChainManager(_connection_manager)
        logger.info("Law chain manager initialized")

        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_database():
    """Close database connections"""
    global _connection_manager, _cultural_repository, _law_chain_manager

    try:
        # Close main database
        await close_db()

        # Close connection manager
        if _connection_manager:
            await _connection_manager.close()
            _connection_manager = None

        # Clear repository references
        _cultural_repository = None
        _law_chain_manager = None

        logger.info("Database connections closed")

    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise


async def get_database_health() -> Dict[str, bool]:
    """Get health status of all database connections"""
    try:
        health = await get_db_health()
        return health
    except Exception as e:
        logger.error(f"Error checking database health: {e}")
        return {
            "postgresql": False,
            "mongodb": False
        }


# Dependency functions for FastAPI

async def get_db_connection():
    """Get database connection dependency"""
    if not _connection_manager:
        raise DatabaseError("Database not initialized")
    return _connection_manager


async def get_global_data_manager():
    """Get global data manager dependency"""
    return get_global_manager()


async def get_novel_data_manager(novel_id: str):
    """Get novel-specific data manager dependency"""
    return get_novel_manager(novel_id)


async def get_batch_data_manager(novel_id: str):
    """Get batch manager dependency"""
    return await get_batch_manager(novel_id)


async def get_cultural_repo():
    """Get cultural framework repository dependency"""
    if not _cultural_repository:
        raise DatabaseError("Cultural repository not initialized")
    return _cultural_repository


async def get_law_chain_mgr():
    """Get law chain manager dependency"""
    if not _law_chain_manager:
        raise DatabaseError("Law chain manager not initialized")
    return _law_chain_manager


# Transaction context manager
@asynccontextmanager
async def database_transaction():
    """Database transaction context manager"""
    if not _connection_manager:
        raise DatabaseError("Database not initialized")

    conn = None
    try:
        # Get connection from pool
        conn = await _connection_manager.get_connection()

        # Start transaction
        await conn.execute("BEGIN")

        yield conn

        # Commit transaction
        await conn.execute("COMMIT")

    except Exception as e:
        # Rollback on error
        if conn:
            await conn.execute("ROLLBACK")
        raise

    finally:
        # Return connection to pool
        if conn:
            await _connection_manager.release_connection(conn)


# Utility functions

async def execute_query(query: str, *args):
    """Execute a database query"""
    if not _connection_manager:
        raise DatabaseError("Database not initialized")

    async with database_transaction() as conn:
        result = await conn.fetch(query, *args)
        return result


async def execute_command(command: str, *args):
    """Execute a database command"""
    if not _connection_manager:
        raise DatabaseError("Database not initialized")

    async with database_transaction() as conn:
        await conn.execute(command, *args)


async def test_database_connection() -> bool:
    """Test database connectivity"""
    try:
        health = await get_database_health()
        return all(health.values())
    except Exception:
        return False