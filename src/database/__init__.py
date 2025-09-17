# -*- coding: utf-8 -*-
"""
网络小说世界观数据库包
提供多小说兼容的数据管理功能
"""

from typing import Dict, Any
import logging

# Import legacy components for backward compatibility
from .connections.postgresql import (
    PostgreSQLConnection,
    SyncPostgreSQLConnection,
    postgres_db,
    sync_postgres_db
)

from .connections.mongodb import (
    MongoDBConnection,
    SyncMongoDBConnection,
    mongodb,
    sync_mongodb
)

# Import new data access layer
from .data_access import (
    init_database,
    close_database,
    get_global_manager,
    get_novel_manager,
    DatabaseError,
    DatabaseManager,
    db_manager
)

# Import models
from .models import *

# Import cultural framework system
from .cultural_framework import (
    CrossDomainConflictManager,
    PlotHookManager,
    CulturalElementManager,
    ConflictAnalyzer,
    ConflictMatrixInitializer,
    ConflictMatrixManager,
    create_conflict_matrix_system,
    get_conflict_overview
)

from config import config

logger = logging.getLogger(__name__)

# Backward compatibility - maintain original names
db = postgres_db
sync_db = sync_postgres_db

# Export all components
__all__ = [
    # Legacy PostgreSQL
    'PostgreSQLConnection',
    'SyncPostgreSQLConnection',
    'postgres_db',
    'sync_postgres_db',
    'db',  # backward compatibility alias
    'sync_db',  # backward compatibility alias

    # Legacy MongoDB
    'MongoDBConnection',
    'SyncMongoDBConnection',
    'mongodb',
    'sync_mongodb',

    # New data access layer
    'init_database',
    'close_database',
    'get_global_manager',
    'get_novel_manager',
    'DatabaseManager',
    'db_manager',

    # Models
    'Novel',
    'Entity',
    'EntityRelationship',
    'Event',
    'Category',
    'CreateEntityRequest',
    'UpdateEntityRequest',
    'QueryRequest',
    'StandardResponse',
    'PaginatedResponse',

    # Cultural Framework System
    'CrossDomainConflictManager',
    'PlotHookManager',
    'CulturalElementManager',
    'ConflictAnalyzer',
    'ConflictMatrixInitializer',
    'ConflictMatrixManager',
    'create_conflict_matrix_system',
    'get_conflict_overview',

    # Exceptions
    'DatabaseError',

    # Legacy functions
    'get_database_info'
]


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