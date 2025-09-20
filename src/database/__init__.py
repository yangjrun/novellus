# -*- coding: utf-8 -*-
"""
裂世九域·法则链纪元 数据库模块
支持PostgreSQL + MongoDB双数据库架构的小说世界观管理系统
"""

from .connection_manager import DatabaseManager, DatabaseConnectionManager, get_database_manager
from .data_access import (
    init_database,
    close_database,
    get_global_manager,
    get_novel_manager,
    DatabaseError,
)
from .models import *

__all__ = [
    'DatabaseManager',
    'get_database_manager',
    'init_database',
    'close_database',
    'get_global_manager',
    'get_novel_manager',
    'DatabaseError',
]