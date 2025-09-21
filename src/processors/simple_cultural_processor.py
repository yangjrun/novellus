#!/usr/bin/env python3
"""
简化的文化框架数据处理脚本
避免复杂的依赖导入，直接执行核心功能
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from uuid import UUID, uuid4

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.config import config
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 项目常量
PROJECT_ID = "29c170c5-4a3e-4829-a242-74c1acb96453"
NOVEL_ID = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"


async def init_postgresql_schema():
    """初始化PostgreSQL数据库架构"""
    logger.info("正在初始化PostgreSQL数据库架构...")

    try:
        pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )

        # 读取SQL脚本
        sql_file = PROJECT_ROOT / "src" / "database" / "schemas" / "cultural_framework_tables.sql"
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        async with pool.acquire() as conn:
            # 分段执行SQL脚本
            statements = sql_script.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        await conn.execute(statement)
                    except Exception as e:
                        if "already exists" not in str(e):
                            logger.warning(f"SQL执行警告: {e}")

        await pool.close()
        logger.info("PostgreSQL架构初始化完成")
        return True

    except Exception as e:
        logger.error(f"PostgreSQL初始化失败: {e}")
        return False


async def init_mongodb_collections():
    """初始化MongoDB集合"""
    logger.info("正在初始化MongoDB集合...")

    try:
        client = AsyncIOMotorClient(config.mongodb_url)
        db = client[config.mongodb_db]

        # 创建集合
        collections = [
            "cultural_details",
            "plot_hooks_detailed",
            "concepts_dictionary",
            "cross_domain_analysis",
            "processing_logs",
            "cultural_entities_detailed"
        ]

        for collection_name in collections:
            try:
                await db.create_collection(collection_name)
                logger.info(f"创建集合: {collection_name}")
            except Exception as e:
                if "already exists" not in str(e):
                    logger.warning(f"集合创建警告: {e}")

        # 创建基本索引
        await db.cultural_details.create_index([("novelId", 1), ("domainType", 1)])
        await db.concepts_dictionary.create_index([("novelId", 1), ("term", 1)], unique=True)
        await db.processing_logs.create_index([("novelId", 1), ("processType", 1)])

        client.close()
        logger.info("MongoDB集合初始化完成")
        return True

    except Exception as e:
        logger.error(f"MongoDB初始化失败: {e}")
        return False


async def insert_sample_cultural_data():
    """插入示例文化数据"""
    logger.info("正在插入示例文化数据...")

    try:
        pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )

        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        mongo_db = mongo_client[config.mongodb_db]

        # 示例文化框架数据
        sample_frameworks = [
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "domain_type": "人域",
                "dimension": "权力与法律",
                "title": "天命王朝政治体系",
                "summary": "以天命王朝为核心的政治结构，实行链籍三等制",
                "key_elements": ["天命王朝", "链籍三等制", "祭司议会", "断链律"],
                "detailed_content": "人域实行天命王朝统治，建立了严格的链籍三等制社会体系。天命王朝作为统治整个人域的政治实体，通过链籍三等制根据法则链强度划分社会等级。祭司议会负责宗教事务和法则链认证，而断链律则规范法则链的使用。",
                "tags": ["政治", "制度", "权力"],
                "priority": 9
            },
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "domain_type": "人域",
                "dimension": "神话与宗教",
                "title": "法则链信仰体系",
                "summary": "以法则链为核心的宗教信仰，包含链神崇拜和环印仪式",
                "key_elements": ["链神崇拜", "环印仪式", "断链禁忌"],
                "detailed_content": "人域的宗教体系以法则链信仰为核心。居民相信法则链是连接世界本源的神圣纽带，能够赋予修炼者强大的力量。主要信仰包括链神崇拜、环印仪式和断链禁忌。",
                "tags": ["宗教", "信仰", "仪式"],
                "priority": 8
            },
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "domain_type": "天域",
                "dimension": "神话与宗教",
                "title": "源链信仰体系",
                "summary": "天域古老神秘的宗教体系，相信源链连接所有法则链",
                "key_elements": ["源链信仰", "天链守护者", "净化仪式", "天启预言"],
                "detailed_content": "天域的宗教体系更加古老和神秘，以源链信仰为核心。天链守护者保护天域法则链不被污染，通过净化仪式清除法则链腐化，天启预言记录着关于法则链未来命运的古老预言。",
                "tags": ["古老", "神秘", "净化"],
                "priority": 9
            }
        ]

        # 示例文化实体数据
        sample_entities = [
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "name": "天命王朝",
                "entity_type": "组织机构",
                "domain_type": "人域",
                "dimensions": ["权力与法律"],
                "description": "统治整个人域的政治实体，建立了链籍三等制社会体系",
                "characteristics": json.dumps({"governance_type": "王朝制", "scope": "全域"}),
                "functions": ["政治统治", "社会管理", "法则链监管"],
                "significance": "人域最高政治权力机构"
            },
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "name": "链籍三等制",
                "entity_type": "身份制度",
                "domain_type": "人域",
                "dimensions": ["权力与法律", "家庭与教育"],
                "description": "根据法则链强度划分社会等级的制度体系",
                "characteristics": json.dumps({"levels": 3, "basis": "法则链强度"}),
                "functions": ["社会分层", "等级管理", "权利分配"],
                "significance": "人域核心社会制度"
            },
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "name": "法则链",
                "entity_type": "重要概念",
                "domain_type": None,
                "dimensions": ["神话与宗教", "权力与法律", "经济与技术"],
                "description": "连接世界本源的神圣纽带，修炼者力量的源泉",
                "characteristics": json.dumps({"type": "能量纽带", "sacred": True}),
                "functions": ["赋予力量", "连接本源", "修炼媒介"],
                "significance": "整个世界观的核心概念"
            }
        ]

        # 示例概念词典数据
        sample_concepts = [
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "term": "法则链",
                "definition": "连接世界本源的神圣纽带，能够赋予修炼者强大的力量",
                "category": "power_system",
                "domain_type": None,
                "frequency": 150,
                "importance": 10
            },
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "term": "链籍",
                "definition": "记录个人法则链信息和社会等级的重要证明",
                "category": "identity_system",
                "domain_type": "人域",
                "frequency": 45,
                "importance": 8
            },
            {
                "id": str(uuid4()),
                "novel_id": NOVEL_ID,
                "term": "环印",
                "definition": "法则链修炼者的身份标识，通过特殊仪式获得",
                "category": "item",
                "domain_type": "人域",
                "frequency": 32,
                "importance": 7
            }
        ]

        # 插入PostgreSQL数据
        async with pool.acquire() as conn:
            # 插入文化框架
            for fw in sample_frameworks:
                await conn.execute("""
                    INSERT INTO cultural_frameworks
                    (id, novel_id, domain_type, dimension, title, summary, key_elements,
                     detailed_content, tags, priority, completion_status, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    ON CONFLICT (novel_id, domain_type, dimension) DO NOTHING
                """, fw["id"], fw["novel_id"], fw["domain_type"], fw["dimension"],
                fw["title"], fw["summary"], fw["key_elements"], fw["detailed_content"],
                fw["tags"], fw["priority"], 1.0, datetime.utcnow(), datetime.utcnow())

            # 插入文化实体
            for entity in sample_entities:
                await conn.execute("""
                    INSERT INTO cultural_entities
                    (id, novel_id, framework_id, name, entity_type, domain_type, dimensions,
                     description, characteristics, functions, significance, aliases, tags,
                     references, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (novel_id, name, entity_type) DO NOTHING
                """, entity["id"], entity["novel_id"], None, entity["name"],
                entity["entity_type"], entity["domain_type"], entity["dimensions"],
                entity["description"], entity["characteristics"], entity["functions"],
                entity["significance"], [], [], [], datetime.utcnow(), datetime.utcnow())

            # 插入概念词典
            for concept in sample_concepts:
                await conn.execute("""
                    INSERT INTO concept_dictionary
                    (id, novel_id, term, definition, category, domain_type, etymology,
                     usage_examples, related_terms, frequency, importance, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    ON CONFLICT (novel_id, term) DO NOTHING
                """, concept["id"], concept["novel_id"], concept["term"], concept["definition"],
                concept["category"], concept["domain_type"], None, [], [],
                concept["frequency"], concept["importance"], datetime.utcnow(), datetime.utcnow())

        # 插入MongoDB数据
        cultural_detail_doc = {
            "novelId": NOVEL_ID,
            "domainType": "多域",
            "rawContent": "示例文化框架数据",
            "processedContent": {
                "frameworks": sample_frameworks,
                "entities": sample_entities,
                "concepts": sample_concepts
            },
            "processingMetadata": {
                "version": "1.0.0",
                "processingDate": datetime.utcnow(),
                "parserVersion": "1.0.0",
                "qualityScore": 0.85,
                "completeness": 0.9
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        await mongo_db.cultural_details.insert_one(cultural_detail_doc)

        # 插入处理日志
        log_doc = {
            "novelId": NOVEL_ID,
            "processType": "data_import",
            "status": "completed",
            "processDetails": {
                "inputSize": 3,
                "outputSize": 3,
                "processingTime": 1.5,
                "errorCount": 0,
                "warningCount": 0
            },
            "statistics": {
                "entitiesExtracted": len(sample_entities),
                "relationsFound": 0,
                "conceptsIdentified": len(sample_concepts),
                "qualityScore": 0.85
            },
            "issues": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        await mongo_db.processing_logs.insert_one(log_doc)

        await pool.close()
        mongo_client.close()

        logger.info("示例文化数据插入完成")
        return True

    except Exception as e:
        logger.error(f"数据插入失败: {e}")
        return False


async def query_and_validate_data():
    """查询并验证数据"""
    logger.info("正在查询和验证数据...")

    try:
        pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )

        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        mongo_db = mongo_client[config.mongodb_db]

        # 查询PostgreSQL统计信息
        async with pool.acquire() as conn:
            frameworks_count = await conn.fetchval(
                "SELECT COUNT(*) FROM cultural_frameworks WHERE novel_id = $1", NOVEL_ID
            )
            entities_count = await conn.fetchval(
                "SELECT COUNT(*) FROM cultural_entities WHERE novel_id = $1", NOVEL_ID
            )
            concepts_count = await conn.fetchval(
                "SELECT COUNT(*) FROM concept_dictionary WHERE novel_id = $1", NOVEL_ID
            )

            # 查询域分布
            domain_stats = await conn.fetch("""
                SELECT domain_type, COUNT(*) as count
                FROM cultural_frameworks
                WHERE novel_id = $1
                GROUP BY domain_type
            """, NOVEL_ID)

            # 查询维度分布
            dimension_stats = await conn.fetch("""
                SELECT dimension, COUNT(*) as count
                FROM cultural_frameworks
                WHERE novel_id = $1
                GROUP BY dimension
            """, NOVEL_ID)

        # 查询MongoDB统计信息
        mongo_details_count = await mongo_db.cultural_details.count_documents({"novelId": NOVEL_ID})
        mongo_logs_count = await mongo_db.processing_logs.count_documents({"novelId": NOVEL_ID})

        await pool.close()
        mongo_client.close()

        # 生成报告
        report = {
            "novel_id": NOVEL_ID,
            "postgresql_data": {
                "frameworks": frameworks_count,
                "entities": entities_count,
                "concepts": concepts_count
            },
            "mongodb_data": {
                "details": mongo_details_count,
                "logs": mongo_logs_count
            },
            "domain_distribution": {row['domain_type']: row['count'] for row in domain_stats},
            "dimension_distribution": {row['dimension']: row['count'] for row in dimension_stats}
        }

        logger.info("数据验证报告:")
        logger.info(f"  PostgreSQL - 框架: {frameworks_count}, 实体: {entities_count}, 概念: {concepts_count}")
        logger.info(f"  MongoDB - 详情: {mongo_details_count}, 日志: {mongo_logs_count}")
        logger.info(f"  域分布: {report['domain_distribution']}")
        logger.info(f"  维度分布: {report['dimension_distribution']}")

        return report

    except Exception as e:
        logger.error(f"数据验证失败: {e}")
        return None


async def main():
    """主函数"""
    logger.info("开始执行文化框架数据处理...")

    try:
        # 1. 初始化数据库
        logger.info("=== 步骤1: 初始化数据库 ===")
        pg_success = await init_postgresql_schema()
        mongo_success = await init_mongodb_collections()

        if not (pg_success and mongo_success):
            logger.error("数据库初始化失败")
            return False

        # 2. 插入示例数据
        logger.info("=== 步骤2: 插入示例数据 ===")
        data_success = await insert_sample_cultural_data()

        if not data_success:
            logger.error("数据插入失败")
            return False

        # 3. 验证数据
        logger.info("=== 步骤3: 验证数据 ===")
        report = await query_and_validate_data()

        if report is None:
            logger.error("数据验证失败")
            return False

        logger.info("=== 处理完成 ===")
        logger.info("✅ 文化框架数据处理成功完成!")

        return True

    except Exception as e:
        logger.error(f"处理失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)