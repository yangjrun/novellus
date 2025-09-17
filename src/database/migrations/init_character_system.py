#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色管理系统数据库初始化脚本
初始化 PostgreSQL 表结构和 MongoDB 集合
"""

import os
import asyncio
import logging
from typing import Optional
from datetime import datetime

# 导入数据库连接模块
from ..connections.postgresql import postgres_db, sync_postgres_db
from ..connections.mongodb import mongodb, sync_mongodb

logger = logging.getLogger(__name__)

class CharacterSystemInitializer:
    """角色管理系统初始化器"""

    def __init__(self):
        self.pg_db = None
        self.mongo_db = None

    async def initialize(self, force_recreate: bool = False) -> bool:
        """
        初始化角色管理系统

        Args:
            force_recreate: 是否强制重新创建（会删除现有数据）

        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("开始初始化角色管理系统...")

            # 1. 初始化 PostgreSQL 结构
            await self._init_postgresql_schema(force_recreate)

            # 2. 初始化 MongoDB 集合
            await self._init_mongodb_collections(force_recreate)

            # 3. 验证初始化结果
            await self._verify_initialization()

            logger.info("角色管理系统初始化完成！")
            return True

        except Exception as e:
            logger.error(f"角色管理系统初始化失败: {e}")
            return False

    async def _init_postgresql_schema(self, force_recreate: bool = False):
        """初始化 PostgreSQL 表结构"""
        logger.info("初始化 PostgreSQL 角色管理表结构...")

        # 读取 SQL 脚本
        schema_file = os.path.join(
            os.path.dirname(__file__),
            "..", "schemas", "character_management_tables.sql"
        )

        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"找不到角色管理表结构文件: {schema_file}")

        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # 如果强制重新创建，先删除相关表
        if force_recreate:
            await self._drop_character_tables()

        # 执行 SQL 脚本
        try:
            await postgres_db.execute_script(sql_script)
            logger.info("✓ PostgreSQL 角色管理表结构创建成功")
        except Exception as e:
            logger.error(f"✗ PostgreSQL 表结构创建失败: {e}")
            raise

    async def _drop_character_tables(self):
        """删除角色相关表（用于强制重新创建）"""
        logger.warning("正在删除现有角色管理表...")

        drop_commands = [
            "DROP TRIGGER IF EXISTS trigger_character_version_change ON entities;",
            "DROP TRIGGER IF EXISTS trigger_character_version_consistency ON entities;",
            "DROP FUNCTION IF EXISTS record_character_version_change();",
            "DROP FUNCTION IF EXISTS ensure_character_version_consistency();",
            "DROP FUNCTION IF EXISTS validate_character_data();",
            "DROP VIEW IF EXISTS character_version_overview;",
            "DROP VIEW IF EXISTS character_domain_distribution;",
            "DROP TABLE IF EXISTS character_relationship_evolution;",
            "DROP TABLE IF EXISTS character_version_history;",

            # 删除添加的列（需要谨慎）
            """
            ALTER TABLE entities
            DROP COLUMN IF EXISTS domain_code,
            DROP COLUMN IF EXISTS character_version,
            DROP COLUMN IF EXISTS previous_version_id,
            DROP COLUMN IF EXISTS transition_notes,
            DROP COLUMN IF EXISTS is_current_version,
            DROP COLUMN IF EXISTS character_unique_id;
            """,

            """
            ALTER TABLE entity_relationships
            DROP COLUMN IF EXISTS domain_context,
            DROP COLUMN IF EXISTS relationship_version,
            DROP COLUMN IF EXISTS is_cross_domain;
            """
        ]

        for cmd in drop_commands:
            try:
                await postgres_db.execute(cmd.strip())
                logger.debug(f"执行删除命令: {cmd.strip()[:50]}...")
            except Exception as e:
                logger.warning(f"删除命令执行警告: {e}")

    async def _init_mongodb_collections(self, force_recreate: bool = False):
        """初始化 MongoDB 集合"""
        logger.info("初始化 MongoDB 角色管理集合...")

        try:
            # 获取数据库连接
            mongo_client = await mongodb.get_client()
            db = mongo_client.get_database()

            collection_names = [
                "character_profiles",
                "character_relationship_details",
                "character_development_tracks",
                "character_psychological_history"
            ]

            # 如果强制重新创建，先删除现有集合
            if force_recreate:
                for collection_name in collection_names:
                    if collection_name in await db.list_collection_names():
                        await db.drop_collection(collection_name)
                        logger.info(f"删除现有集合: {collection_name}")

            # 创建角色档案集合
            await self._create_character_profiles_collection(db)

            # 创建关系详情集合
            await self._create_relationship_details_collection(db)

            # 创建发展轨迹集合
            await self._create_development_tracks_collection(db)

            # 创建心理历史集合
            await self._create_psychological_history_collection(db)

            logger.info("✓ MongoDB 角色管理集合创建成功")

        except Exception as e:
            logger.error(f"✗ MongoDB 集合创建失败: {e}")
            raise

    async def _create_character_profiles_collection(self, db):
        """创建角色档案集合"""
        collection_name = "character_profiles"

        # 创建集合（带验证模式）
        await db.create_collection(
            collection_name,
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["character_unique_id", "character_name", "novel_id", "domain_code", "version"],
                    "properties": {
                        "character_unique_id": {"bsonType": "string"},
                        "character_name": {"bsonType": "string"},
                        "novel_id": {"bsonType": "int"},
                        "domain_code": {"bsonType": "string"},
                        "version": {"bsonType": "string", "pattern": "^[0-9]+\\.[0-9]+$"},
                        "is_current_version": {"bsonType": "bool"},
                        "is_archived": {"bsonType": "bool"}
                    }
                }
            }
        )

        # 创建索引
        collection = db[collection_name]

        await collection.create_index(
            [("character_unique_id", 1), ("domain_code", 1), ("version", 1)],
            unique=True,
            name="idx_character_domain_version"
        )

        await collection.create_index(
            [("novel_id", 1), ("character_unique_id", 1)],
            name="idx_novel_character"
        )

        await collection.create_index(
            [("character_unique_id", 1), ("is_current_version", 1)],
            name="idx_character_current"
        )

        await collection.create_index(
            [("domain_code", 1), ("is_current_version", 1)],
            name="idx_domain_current"
        )

        # 文本搜索索引
        await collection.create_index(
            [
                ("character_name", "text"),
                ("basic_info.occupation", "text"),
                ("background.birthplace", "text")
            ],
            name="idx_character_text_search"
        )

        logger.info(f"✓ 创建集合: {collection_name}")

    async def _create_relationship_details_collection(self, db):
        """创建角色关系详情集合"""
        collection_name = "character_relationship_details"

        await db.create_collection(
            collection_name,
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["novel_id", "source_character_id", "target_character_id", "relationship_type"],
                    "properties": {
                        "novel_id": {"bsonType": "int"},
                        "source_character_id": {"bsonType": "string"},
                        "target_character_id": {"bsonType": "string"},
                        "relationship_type": {"bsonType": "string"}
                    }
                }
            }
        )

        collection = db[collection_name]

        await collection.create_index(
            [("source_character_id", 1), ("target_character_id", 1)],
            name="idx_relationship_pair"
        )

        await collection.create_index(
            [("novel_id", 1), ("relationship_type", 1)],
            name="idx_novel_relationship_type"
        )

        logger.info(f"✓ 创建集合: {collection_name}")

    async def _create_development_tracks_collection(self, db):
        """创建角色发展轨迹集合"""
        collection_name = "character_development_tracks"

        await db.create_collection(
            collection_name,
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["character_unique_id", "novel_id", "track_type"],
                    "properties": {
                        "character_unique_id": {"bsonType": "string"},
                        "novel_id": {"bsonType": "int"},
                        "track_type": {
                            "bsonType": "string",
                            "enum": ["skill", "personality", "relationship", "goal", "milestone"]
                        }
                    }
                }
            }
        )

        collection = db[collection_name]

        await collection.create_index(
            [("character_unique_id", 1), ("track_type", 1)],
            name="idx_character_track_type"
        )

        await collection.create_index(
            [("novel_id", 1), ("track_type", 1)],
            name="idx_novel_track_type"
        )

        logger.info(f"✓ 创建集合: {collection_name}")

    async def _create_psychological_history_collection(self, db):
        """创建角色心理状态历史集合"""
        collection_name = "character_psychological_history"

        await db.create_collection(
            collection_name,
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["character_unique_id", "novel_id", "record_date"],
                    "properties": {
                        "character_unique_id": {"bsonType": "string"},
                        "novel_id": {"bsonType": "int"},
                        "record_date": {"bsonType": "date"}
                    }
                }
            }
        )

        collection = db[collection_name]

        await collection.create_index(
            [("character_unique_id", 1), ("record_date", -1)],
            name="idx_character_psych_timeline"
        )

        await collection.create_index(
            [("novel_id", 1), ("domain_code", 1)],
            name="idx_novel_domain_psych"
        )

        logger.info(f"✓ 创建集合: {collection_name}")

    async def _verify_initialization(self):
        """验证初始化结果"""
        logger.info("验证初始化结果...")

        # 验证 PostgreSQL 表结构
        pg_tables = await self._check_postgresql_tables()
        logger.info(f"PostgreSQL 表状态: {pg_tables}")

        # 验证 MongoDB 集合
        mongo_collections = await self._check_mongodb_collections()
        logger.info(f"MongoDB 集合状态: {mongo_collections}")

        # 运行数据完整性检查
        await self._run_data_integrity_check()

    async def _check_postgresql_tables(self) -> dict:
        """检查 PostgreSQL 表状态"""
        tables_to_check = [
            "entities",
            "character_version_history",
            "character_relationship_evolution"
        ]

        status = {}
        for table in tables_to_check:
            try:
                result = await postgres_db.fetch_one(
                    "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_name = $1",
                    table
                )
                status[table] = "存在" if result["count"] > 0 else "不存在"
            except Exception as e:
                status[table] = f"检查失败: {e}"

        return status

    async def _check_mongodb_collections(self) -> dict:
        """检查 MongoDB 集合状态"""
        collections_to_check = [
            "character_profiles",
            "character_relationship_details",
            "character_development_tracks",
            "character_psychological_history"
        ]

        status = {}
        try:
            mongo_client = await mongodb.get_client()
            db = mongo_client.get_database()
            existing_collections = await db.list_collection_names()

            for collection in collections_to_check:
                status[collection] = "存在" if collection in existing_collections else "不存在"

        except Exception as e:
            for collection in collections_to_check:
                status[collection] = f"检查失败: {e}"

        return status

    async def _run_data_integrity_check(self):
        """运行数据完整性检查"""
        logger.info("运行数据完整性检查...")

        try:
            # 执行 PostgreSQL 数据验证函数
            validation_results = await postgres_db.fetch_all(
                "SELECT * FROM validate_character_data()"
            )

            if validation_results:
                logger.warning(f"发现数据完整性问题: {len(validation_results)} 个")
                for issue in validation_results:
                    logger.warning(f"  - {issue['issue_type']}: {issue['description']}")
            else:
                logger.info("✓ 数据完整性检查通过")

        except Exception as e:
            logger.warning(f"数据完整性检查失败: {e}")


# 同步版本的初始化器（用于同步调用）
class SyncCharacterSystemInitializer:
    """同步版本的角色管理系统初始化器"""

    def __init__(self):
        pass

    def initialize(self, force_recreate: bool = False) -> bool:
        """同步初始化角色管理系统"""
        try:
            logger.info("开始同步初始化角色管理系统...")

            # 1. 初始化 PostgreSQL 结构
            self._init_postgresql_schema_sync(force_recreate)

            # 2. 初始化 MongoDB 集合
            self._init_mongodb_collections_sync(force_recreate)

            logger.info("同步角色管理系统初始化完成！")
            return True

        except Exception as e:
            logger.error(f"同步角色管理系统初始化失败: {e}")
            return False

    def _init_postgresql_schema_sync(self, force_recreate: bool = False):
        """同步初始化 PostgreSQL 表结构"""
        logger.info("同步初始化 PostgreSQL 角色管理表结构...")

        schema_file = os.path.join(
            os.path.dirname(__file__),
            "..", "schemas", "character_management_tables.sql"
        )

        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"找不到角色管理表结构文件: {schema_file}")

        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        try:
            sync_postgres_db.execute_script(sql_script)
            logger.info("✓ PostgreSQL 角色管理表结构创建成功")
        except Exception as e:
            logger.error(f"✗ PostgreSQL 表结构创建失败: {e}")
            raise

    def _init_mongodb_collections_sync(self, force_recreate: bool = False):
        """同步初始化 MongoDB 集合"""
        logger.info("同步初始化 MongoDB 角色管理集合...")

        try:
            # 这里可能需要使用同步的 MongoDB 操作
            # 或者调用异步版本
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def init_mongo():
                initializer = CharacterSystemInitializer()
                await initializer._init_mongodb_collections(force_recreate)

            loop.run_until_complete(init_mongo())
            loop.close()

            logger.info("✓ MongoDB 角色管理集合创建成功")

        except Exception as e:
            logger.error(f"✗ MongoDB 集合创建失败: {e}")
            raise


# 便捷的初始化函数
async def init_character_system(force_recreate: bool = False) -> bool:
    """
    初始化角色管理系统（异步版本）

    Args:
        force_recreate: 是否强制重新创建

    Returns:
        bool: 初始化是否成功
    """
    initializer = CharacterSystemInitializer()
    return await initializer.initialize(force_recreate)


def init_character_system_sync(force_recreate: bool = False) -> bool:
    """
    初始化角色管理系统（同步版本）

    Args:
        force_recreate: 是否强制重新创建

    Returns:
        bool: 初始化是否成功
    """
    initializer = SyncCharacterSystemInitializer()
    return initializer.initialize(force_recreate)


# 命令行执行
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="初始化角色管理系统")
    parser.add_argument("--force", action="store_true", help="强制重新创建")
    parser.add_argument("--async", action="store_true", help="使用异步模式")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.async:
        # 异步执行
        success = asyncio.run(init_character_system(args.force))
    else:
        # 同步执行
        success = init_character_system_sync(args.force)

    if success:
        print("角色管理系统初始化成功！")
        sys.exit(0)
    else:
        print("角色管理系统初始化失败！")
        sys.exit(1)