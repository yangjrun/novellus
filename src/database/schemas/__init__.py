"""
数据库模式定义模块
包含PostgreSQL表结构和MongoDB集合定义
"""

# SQL文件路径常量
POSTGRESQL_SCHEMA = "init_postgresql.sql"
CULTURAL_FRAMEWORK_SCHEMA = "cultural_framework_tables.sql"

__all__ = [
    "POSTGRESQL_SCHEMA",
    "CULTURAL_FRAMEWORK_SCHEMA"
]