"""
数据库初始化脚本
负责创建表结构、集合、索引和初始数据
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

from .connection_manager import get_database_manager, DatabaseError
from .repositories.mongodb_repository import MongoDBRepository

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """数据库初始化器"""

    def __init__(self):
        self.db_manager = None
        self.base_dir = Path(__file__).parent
        self.schemas_dir = self.base_dir / "schemas"

    async def initialize_all(self) -> Dict[str, Any]:
        """初始化所有数据库"""
        result = {
            "postgresql": {"success": False, "message": "", "error": None},
            "mongodb": {"success": False, "message": "", "error": None},
            "overall_success": False
        }

        try:
            # 获取数据库管理器
            self.db_manager = await get_database_manager()
            logger.info("数据库管理器初始化成功")

            # 初始化PostgreSQL
            pg_result = await self.initialize_postgresql()
            result["postgresql"] = pg_result

            # 初始化MongoDB
            mongo_result = await self.initialize_mongodb()
            result["mongodb"] = mongo_result

            # 检查总体结果
            result["overall_success"] = (
                result["postgresql"]["success"] and
                result["mongodb"]["success"]
            )

            if result["overall_success"]:
                logger.info("数据库初始化完成")
            else:
                logger.error("数据库初始化部分失败")

            return result

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            result["error"] = str(e)
            return result

    async def initialize_postgresql(self) -> Dict[str, Any]:
        """初始化PostgreSQL数据库"""
        result = {"success": False, "message": "", "error": None}

        try:
            logger.info("开始初始化PostgreSQL数据库...")

            # 读取SQL初始化脚本
            sql_file = self.schemas_dir / "init_postgresql.sql"
            if not sql_file.exists():
                raise DatabaseError(f"PostgreSQL初始化脚本不存在: {sql_file}")

            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 执行SQL脚本
            async with self.db_manager.postgres.get_transaction() as conn:
                await conn.execute(sql_content)

            # 验证表是否创建成功
            await self._verify_postgresql_tables()

            result["success"] = True
            result["message"] = "PostgreSQL数据库初始化成功"
            logger.info("PostgreSQL数据库初始化完成")

        except Exception as e:
            error_msg = f"PostgreSQL初始化失败: {e}"
            logger.error(error_msg)
            result["error"] = error_msg
            result["message"] = error_msg

        return result

    async def initialize_mongodb(self) -> Dict[str, Any]:
        """初始化MongoDB数据库"""
        result = {"success": False, "message": "", "error": None}

        try:
            logger.info("开始初始化MongoDB数据库...")

            # 执行MongoDB初始化脚本
            js_file = self.schemas_dir / "init_mongodb.js"
            if not js_file.exists():
                raise DatabaseError(f"MongoDB初始化脚本不存在: {js_file}")

            # 通过mongo shell执行JavaScript脚本
            await self._execute_mongodb_script(js_file)

            # 创建索引
            mongo_repo = MongoDBRepository(self.db_manager.mongodb)
            await mongo_repo.ensure_indexes()

            # 验证集合是否创建成功
            await self._verify_mongodb_collections()

            result["success"] = True
            result["message"] = "MongoDB数据库初始化成功"
            logger.info("MongoDB数据库初始化完成")

        except Exception as e:
            error_msg = f"MongoDB初始化失败: {e}"
            logger.error(error_msg)
            result["error"] = error_msg
            result["message"] = error_msg

        return result

    async def _execute_mongodb_script(self, script_path: Path) -> None:
        """执行MongoDB脚本"""
        try:
            from src.config import config

            # 构建mongo命令
            mongo_cmd = [
                "mongo",
                f"{config.mongodb_host}:{config.mongodb_port}/{config.mongodb_db}",
                str(script_path)
            ]

            # 如果有认证信息，添加认证参数
            if config.mongodb_user and config.mongodb_password:
                mongo_cmd.extend([
                    "--username", config.mongodb_user,
                    "--password", config.mongodb_password
                ])

            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *mongo_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_output = stderr.decode('utf-8')
                # 如果没有mongo命令，尝试直接使用Python执行
                if "command not found" in error_output or "not recognized" in error_output:
                    await self._execute_mongodb_script_python(script_path)
                else:
                    raise DatabaseError(f"MongoDB脚本执行失败: {error_output}")
            else:
                logger.info("MongoDB脚本执行成功")

        except FileNotFoundError:
            # mongo命令不存在，使用Python直接执行
            await self._execute_mongodb_script_python(script_path)

    async def _execute_mongodb_script_python(self, script_path: Path) -> None:
        """使用Python直接执行MongoDB初始化"""
        try:
            db = self.db_manager.mongodb.database

            # 创建集合和验证器
            collections_config = {
                "characters": {
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["novel_id", "name", "character_type"],
                            "properties": {
                                "novel_id": {"bsonType": "string"},
                                "name": {"bsonType": "string"},
                                "character_type": {
                                    "enum": ["protagonist", "antagonist", "supporting", "background", "mentor", "love_interest"]
                                }
                            }
                        }
                    }
                },
                "locations": {
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["novel_id", "name", "location_type"],
                            "properties": {
                                "novel_id": {"bsonType": "string"},
                                "name": {"bsonType": "string"},
                                "location_type": {
                                    "enum": ["domain", "city", "sect", "palace", "mountain", "forest", "ruin", "battlefield", "cultivation_ground", "secret_realm"]
                                }
                            }
                        }
                    }
                },
                "items": {
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["novel_id", "name", "item_type"],
                            "properties": {
                                "novel_id": {"bsonType": "string"},
                                "name": {"bsonType": "string"},
                                "item_type": {
                                    "enum": ["weapon", "armor", "pill", "cultivation_manual", "treasure", "artifact", "material", "consumable"]
                                }
                            }
                        }
                    }
                },
                "events": {
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["novel_id", "name", "event_type"],
                            "properties": {
                                "novel_id": {"bsonType": "string"},
                                "name": {"bsonType": "string"},
                                "event_type": {
                                    "enum": ["battle", "cultivation_breakthrough", "political_intrigue", "discovery", "betrayal", "alliance", "romance", "tragedy", "mystery"]
                                }
                            }
                        }
                    }
                },
                "knowledge_base": {
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["novel_id", "title", "category"],
                            "properties": {
                                "novel_id": {"bsonType": "string"},
                                "title": {"bsonType": "string"},
                                "category": {
                                    "enum": ["world_history", "cultivation_theory", "politics", "geography", "culture", "language", "mythology", "technology", "economics"]
                                }
                            }
                        }
                    }
                }
            }

            # 创建集合
            for collection_name, config_data in collections_config.items():
                try:
                    await db.create_collection(collection_name, **config_data)
                    logger.info(f"创建集合: {collection_name}")
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.warning(f"创建集合 {collection_name} 失败: {e}")

            # 插入初始数据
            await self._insert_initial_data()

            logger.info("MongoDB集合创建完成")

        except Exception as e:
            logger.error(f"Python执行MongoDB初始化失败: {e}")
            raise DatabaseError(f"MongoDB初始化失败: {e}")

    async def _insert_initial_data(self) -> None:
        """插入初始数据"""
        try:
            db = self.db_manager.mongodb.database
            from datetime import datetime

            # 初始知识库数据
            initial_knowledge = [
                {
                    "novel_id": "default",
                    "title": "九域修炼体系总览",
                    "category": "cultivation_theory",
                    "content": {
                        "summary": "裂世九域的修炼体系以法则链为核心，分为七个主要阶段",
                        "detailed_info": "修炼阶段：凡身 → 开脉 → 归源 → 封侯 → 破界 → 帝境 → 裂世者。每个阶段都有其独特的力量特征和突破要求。",
                        "examples": [
                            "凡身期：淬炼肉身，为开脉做准备",
                            "开脉期：打通经脉，感知法则链",
                            "归源期：深度理解法则本质",
                            "封侯期：掌控区域法则",
                            "破界期：突破域界限制",
                            "帝境期：建立自身法则领域",
                            "裂世者：能够撕裂现实规则"
                        ]
                    },
                    "related_entities": [],
                    "sources": ["世界观设定文档"],
                    "reliability": 10,
                    "tags": ["修炼", "法则链", "体系"],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "novel_id": "default",
                    "title": "九大域基本情况",
                    "category": "geography",
                    "content": {
                        "summary": "裂世九域包含九个不同特色的域界，每个域都有独特的法则特性",
                        "detailed_info": "人域、天域、灵域、魔域、仙域、神域、虚域、混沌域、永恒域，每个域都有其独特的生态系统、修炼环境和统治结构。"
                    },
                    "related_entities": [],
                    "sources": ["世界观设定文档"],
                    "reliability": 10,
                    "tags": ["九域", "地理", "世界观"],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "novel_id": "default",
                    "title": "四大权力组织",
                    "category": "politics",
                    "content": {
                        "summary": "天命王朝、法则宗门、祭司议会、裂世反叛军四大势力主导政治格局",
                        "detailed_info": "每个组织都有其独特的理念、组织架构和势力范围，形成复杂的政治关系网。"
                    },
                    "related_entities": [],
                    "sources": ["世界观设定文档"],
                    "reliability": 10,
                    "tags": ["政治", "组织", "权力"],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            ]

            # 检查是否已存在数据，如果不存在则插入
            existing_count = await db.knowledge_base.count_documents({"novel_id": "default"})
            if existing_count == 0:
                await db.knowledge_base.insert_many(initial_knowledge)
                logger.info("插入初始知识库数据")

        except Exception as e:
            logger.warning(f"插入初始数据失败: {e}")

    async def _verify_postgresql_tables(self) -> None:
        """验证PostgreSQL表是否创建成功"""
        required_tables = [
            'projects', 'novels', 'content_batches', 'content_segments',
            'domains', 'cultivation_systems', 'cultivation_stages',
            'power_organizations', 'law_chains', 'chain_marks'
        ]

        async with self.db_manager.postgres.get_connection() as conn:
            for table in required_tables:
                result = await conn.fetchval(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = $1)",
                    table
                )
                if not result:
                    raise DatabaseError(f"表 {table} 创建失败")

        logger.info("PostgreSQL表验证成功")

    async def _verify_mongodb_collections(self) -> None:
        """验证MongoDB集合是否创建成功"""
        required_collections = [
            'characters', 'locations', 'items', 'events', 'knowledge_base'
        ]

        db = self.db_manager.mongodb.database
        existing_collections = await db.list_collection_names()

        for collection in required_collections:
            if collection not in existing_collections:
                logger.warning(f"集合 {collection} 不存在，尝试创建...")
                await db.create_collection(collection)

        logger.info("MongoDB集合验证成功")

    async def reset_database(self) -> Dict[str, Any]:
        """重置数据库（删除所有数据）"""
        result = {
            "postgresql": {"success": False, "message": ""},
            "mongodb": {"success": False, "message": ""},
            "overall_success": False
        }

        try:
            logger.warning("开始重置数据库...")

            if not self.db_manager:
                self.db_manager = await get_database_manager()

            # 重置PostgreSQL
            try:
                async with self.db_manager.postgres.get_transaction() as conn:
                    # 删除所有表的数据
                    tables = [
                        'content_segments', 'content_batches', 'novels', 'projects',
                        'chain_marks', 'law_chains', 'power_organizations',
                        'cultivation_stages', 'cultivation_systems', 'domains'
                    ]

                    for table in tables:
                        await conn.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")

                result["postgresql"]["success"] = True
                result["postgresql"]["message"] = "PostgreSQL数据重置成功"
                logger.info("PostgreSQL数据重置完成")

            except Exception as e:
                result["postgresql"]["message"] = f"PostgreSQL重置失败: {e}"
                logger.error(result["postgresql"]["message"])

            # 重置MongoDB
            try:
                db = self.db_manager.mongodb.database
                collections = ['characters', 'locations', 'items', 'events', 'knowledge_base']

                for collection in collections:
                    await db[collection].delete_many({})

                result["mongodb"]["success"] = True
                result["mongodb"]["message"] = "MongoDB数据重置成功"
                logger.info("MongoDB数据重置完成")

            except Exception as e:
                result["mongodb"]["message"] = f"MongoDB重置失败: {e}"
                logger.error(result["mongodb"]["message"])

            result["overall_success"] = (
                result["postgresql"]["success"] and
                result["mongodb"]["success"]
            )

            return result

        except Exception as e:
            logger.error(f"数据库重置失败: {e}")
            return {
                "postgresql": {"success": False, "message": str(e)},
                "mongodb": {"success": False, "message": str(e)},
                "overall_success": False
            }


# 便捷函数
async def initialize_database() -> Dict[str, Any]:
    """初始化数据库"""
    initializer = DatabaseInitializer()
    return await initializer.initialize_all()


async def reset_database() -> Dict[str, Any]:
    """重置数据库"""
    initializer = DatabaseInitializer()
    return await initializer.reset_database()


# 命令行工具
async def main():
    """命令行主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='数据库初始化工具')
    parser.add_argument('action', choices=['init', 'reset'], help='操作类型')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if args.action == 'init':
        result = await initialize_database()
        if result["overall_success"]:
            print("数据库初始化成功！")
            sys.exit(0)
        else:
            print("数据库初始化失败！")
            print(f"PostgreSQL: {result['postgresql']['message']}")
            print(f"MongoDB: {result['mongodb']['message']}")
            sys.exit(1)

    elif args.action == 'reset':
        confirmation = input("确定要重置数据库吗？这将删除所有数据！(yes/no): ")
        if confirmation.lower() == 'yes':
            result = await reset_database()
            if result["overall_success"]:
                print("数据库重置成功！")
                sys.exit(0)
            else:
                print("数据库重置失败！")
                print(f"PostgreSQL: {result['postgresql']['message']}")
                print(f"MongoDB: {result['mongodb']['message']}")
                sys.exit(1)
        else:
            print("操作已取消")


if __name__ == "__main__":
    asyncio.run(main())