"""
PostgreSQL database connection and query utilities.
"""

import asyncpg
import psycopg2
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager, contextmanager
import logging

from ...config import config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class PostgreSQLConnection:
    """PostgreSQL connection manager."""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def initialize_pool(self) -> None:
        """Initialize the connection pool."""
        try:
            self._pool = await asyncpg.create_pool(
                host=config.postgres_host,
                port=config.postgres_port,
                database=config.postgres_db,
                user=config.postgres_user,
                password=config.postgres_password,
                min_size=1,
                max_size=10,
                command_timeout=30
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise DatabaseError(f"Failed to connect to PostgreSQL: {e}")

    async def close_pool(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("PostgreSQL connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool."""
        if not self._pool:
            await self.initialize_pool()

        async with self._pool.acquire() as connection:
            yield connection

    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        try:
            async with self.get_connection() as conn:
                if params:
                    rows = await conn.fetch(query, *params)
                else:
                    rows = await conn.fetch(query)

                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Query failed: {e}")

    async def execute_command(self, command: str, params: Optional[tuple] = None) -> str:
        """Execute an INSERT/UPDATE/DELETE command."""
        try:
            async with self.get_connection() as conn:
                if params:
                    result = await conn.execute(command, *params)
                else:
                    result = await conn.execute(command)

                return result
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise DatabaseError(f"Command failed: {e}")


class SyncPostgreSQLConnection:
    """Synchronous PostgreSQL connection for simple operations."""

    @contextmanager
    def get_connection(self):
        """Get a synchronous connection."""
        conn = None
        try:
            conn = psycopg2.connect(
                host=config.postgres_host,
                port=config.postgres_port,
                database=config.postgres_db,
                user=config.postgres_user,
                password=config.postgres_password
            )
            yield conn
        except Exception as e:
            logger.error(f"Sync connection failed: {e}")
            raise DatabaseError(f"Connection failed: {e}")
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query synchronously."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Sync query execution failed: {e}")
            raise DatabaseError(f"Query failed: {e}")

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Module-level instances
postgres_db = PostgreSQLConnection()
sync_postgres_db = SyncPostgreSQLConnection()