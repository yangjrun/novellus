"""
数据库连接管理器
支持PostgreSQL和MongoDB的异步连接管理，包含连接池和错误处理
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo.errors
from ..config import config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """数据库操作异常"""
    pass


class PostgreSQLManager:
    """PostgreSQL连接管理器"""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._connected = False

    async def connect(self) -> None:
        """建立数据库连接池"""
        try:
            self._pool = await asyncpg.create_pool(
                host=config.postgres_host,
                port=config.postgres_port,
                database=config.postgres_db,
                user=config.postgres_user,
                password=config.postgres_password,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'jit': 'off',  # 禁用JIT以避免冷启动延迟
                    'application_name': 'novellus_mcp_server'
                }
            )
            self._connected = True
            logger.info("PostgreSQL连接池创建成功")

            # 测试连接
            async with self._pool.acquire() as conn:
                await conn.execute("SELECT 1")
                logger.info("PostgreSQL连接测试成功")

        except Exception as e:
            logger.error(f"PostgreSQL连接失败: {e}")
            self._connected = False
            raise DatabaseError(f"PostgreSQL连接失败: {e}")

    async def close(self) -> None:
        """关闭连接池"""
        if self._pool:
            await self._pool.close()
            self._connected = False
            logger.info("PostgreSQL连接池已关闭")

    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接的上下文管理器"""
        if not self._connected or not self._pool:
            raise DatabaseError("PostgreSQL未连接")

        async with self._pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"PostgreSQL操作错误: {e}")
                raise DatabaseError(f"数据库操作失败: {e}")

    @asynccontextmanager
    async def get_transaction(self):
        """获取事务连接的上下文管理器"""
        async with self.get_connection() as conn:
            async with conn.transaction():
                yield conn

    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected and self._pool is not None


class MongoDBManager:
    """MongoDB连接管理器"""

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._connected = False

    async def connect(self) -> None:
        """建立MongoDB连接"""
        try:
            # 构建连接URL
            if config.mongodb_user and config.mongodb_password:
                url = f"mongodb://{config.mongodb_user}:{config.mongodb_password}@{config.mongodb_host}:{config.mongodb_port}/{config.mongodb_db}"
            else:
                url = f"mongodb://{config.mongodb_host}:{config.mongodb_port}"

            self._client = AsyncIOMotorClient(
                url,
                maxPoolSize=20,
                minPoolSize=5,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
                appname='novellus_mcp_server'
            )

            self._database = self._client[config.mongodb_db]

            # 测试连接
            await self._client.admin.command('ping')
            self._connected = True
            logger.info("MongoDB连接建立成功")

        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            self._connected = False
            raise DatabaseError(f"MongoDB连接失败: {e}")

    async def close(self) -> None:
        """关闭MongoDB连接"""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("MongoDB连接已关闭")

    @property
    def database(self) -> AsyncIOMotorDatabase:
        """获取数据库实例"""
        if not self._connected or self._database is None:
            raise DatabaseError("MongoDB未连接")
        return self._database

    @property
    def client(self) -> AsyncIOMotorClient:
        """获取客户端实例"""
        if not self._connected or self._client is None:
            raise DatabaseError("MongoDB未连接")
        return self._client

    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected and self._client is not None


class DatabaseManager:
    """数据库管理器 - 统一管理PostgreSQL和MongoDB连接"""

    def __init__(self):
        self.postgres = PostgreSQLManager()
        self.mongodb = MongoDBManager()
        self._initialized = False

    async def initialize(self) -> None:
        """初始化数据库连接"""
        try:
            # 并行连接两个数据库
            await asyncio.gather(
                self.postgres.connect(),
                self.mongodb.connect()
            )
            self._initialized = True
            logger.info("数据库管理器初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            await self.close()
            raise DatabaseError(f"数据库初始化失败: {e}")

    async def close(self) -> None:
        """关闭所有数据库连接"""
        await asyncio.gather(
            self.postgres.close(),
            self.mongodb.close(),
            return_exceptions=True
        )
        self._initialized = False
        logger.info("数据库管理器已关闭")

    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return (self._initialized and
                self.postgres.is_connected and
                self.mongodb.is_connected)

    async def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        result = {
            "postgresql": {"connected": False, "error": None},
            "mongodb": {"connected": False, "error": None}
        }

        # 检查PostgreSQL
        try:
            if self.postgres.is_connected:
                async with self.postgres.get_connection() as conn:
                    await conn.execute("SELECT 1")
                result["postgresql"]["connected"] = True
        except Exception as e:
            result["postgresql"]["error"] = str(e)

        # 检查MongoDB
        try:
            if self.mongodb.is_connected:
                await self.mongodb.client.admin.command('ping')
                result["mongodb"]["connected"] = True
        except Exception as e:
            result["mongodb"]["error"] = str(e)

        return result


# 全局数据库管理器实例
_database_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global _database_manager

    if _database_manager is None:
        _database_manager = DatabaseManager()
        await _database_manager.initialize()

    if not _database_manager.is_initialized:
        await _database_manager.initialize()

    return _database_manager


async def close_database_manager() -> None:
    """关闭数据库管理器"""
    global _database_manager

    if _database_manager:
        await _database_manager.close()
        _database_manager = None