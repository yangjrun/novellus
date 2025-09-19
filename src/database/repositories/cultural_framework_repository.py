"""
文化框架数据仓库 - 支持PostgreSQL和MongoDB的混合数据模型
处理文化实体、关系网络和复杂查询操作
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID, uuid4

import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from ..models.cultural_framework_models import (
    CulturalFramework, CulturalEntity, CulturalRelation,
    PlotHook, ConceptDictionary, CrossDomainAnalysis,
    CulturalFrameworkCreate, CulturalEntityCreate, CulturalRelationCreate,
    DomainType, EntityType, RelationType, CulturalDimension
)
from ..connection_manager import DatabaseManager

logger = logging.getLogger(__name__)


class CulturalFrameworkRepository:
    """文化框架数据仓库 - 混合数据库操作"""

    def __init__(self, connection_manager: DatabaseManager):
        self.connection_manager = connection_manager
        self._pg_pool: Optional[asyncpg.Pool] = None
        self._mongo_client: Optional[AsyncIOMotorClient] = None
        self._mongo_db: Optional[AsyncIOMotorDatabase] = None
        self._collections: Dict[str, AsyncIOMotorCollection] = {}

    async def initialize(self):
        """初始化数据库连接"""
        try:
            # 使用新的连接管理器接口
            self._pg_pool = self.connection_manager.postgres._pool
            self._mongo_client = self.connection_manager.mongodb.client
            self._mongo_db = self.connection_manager.mongodb.database

            # 缓存MongoDB集合引用
            self._collections = {
                'cultural_details': self._mongo_db['cultural_details'],
                'cultural_entities_detailed': self._mongo_db['cultural_entities_detailed'],
                'cultural_embeddings': self._mongo_db['cultural_embeddings'],
                'knowledge_graph': self._mongo_db['knowledge_graph'],
                'semantic_relations': self._mongo_db['semantic_relations'],
                'processing_logs': self._mongo_db['processing_logs'],
                'import_tasks': self._mongo_db['import_tasks']
            }

            logger.info("文化框架数据仓库初始化完成")

        except Exception as e:
            logger.error(f"文化框架数据仓库初始化失败: {e}")
            raise

    # ====================================================================
    # 文化框架主表操作 (PostgreSQL)
    # ====================================================================

    async def create_cultural_framework(self, framework: CulturalFrameworkCreate) -> UUID:
        """创建文化框架"""
        framework_id = uuid4()

        async with self._pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO cultural_frameworks (
                    id, novel_id, domain_type, dimension, title, summary,
                    key_elements, detailed_content, tags, priority,
                    processing_status, confidence_score
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                framework_id, framework.novel_id, framework.domain_type.value,
                framework.dimension.value, framework.title, framework.summary,
                framework.key_elements, framework.detailed_content,
                framework.tags, framework.priority, 'draft', 0.5
            )

        logger.info(f"创建文化框架: {framework_id}")
        return framework_id

    async def get_cultural_framework(self, framework_id: UUID) -> Optional[CulturalFramework]:
        """获取文化框架详情"""
        async with self._pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM cultural_frameworks WHERE id = $1",
                framework_id
            )

            if row:
                return CulturalFramework(
                    id=row['id'],
                    novel_id=row['novel_id'],
                    domain_type=DomainType(row['domain_type']),
                    dimension=CulturalDimension(row['dimension']),
                    title=row['title'],
                    summary=row['summary'],
                    key_elements=row['key_elements'] or [],
                    detailed_content=row['detailed_content'],
                    tags=row['tags'] or [],
                    priority=row['priority'],
                    completion_status=float(row['completion_status']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        return None

    async def get_frameworks_by_novel(self, novel_id: UUID, domain_type: Optional[DomainType] = None) -> List[CulturalFramework]:
        """获取小说的所有文化框架"""
        query = "SELECT * FROM cultural_frameworks WHERE novel_id = $1"
        params = [novel_id]

        if domain_type:
            query += " AND domain_type = $2"
            params.append(domain_type.value)

        query += " ORDER BY domain_type, dimension"

        async with self._pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

            return [
                CulturalFramework(
                    id=row['id'],
                    novel_id=row['novel_id'],
                    domain_type=DomainType(row['domain_type']),
                    dimension=CulturalDimension(row['dimension']),
                    title=row['title'],
                    summary=row['summary'],
                    key_elements=row['key_elements'] or [],
                    detailed_content=row['detailed_content'],
                    tags=row['tags'] or [],
                    priority=row['priority'],
                    completion_status=float(row['completion_status']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]

    # ====================================================================
    # 文化实体操作 (PostgreSQL + MongoDB)
    # ====================================================================

    async def create_cultural_entity(self, entity: CulturalEntityCreate) -> UUID:
        """创建文化实体 (PostgreSQL主表 + MongoDB详细信息)"""
        entity_id = uuid4()

        # 在PostgreSQL中创建主记录
        async with self._pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO cultural_entities (
                    id, novel_id, framework_id, name, entity_type, domain_type,
                    dimensions, description, characteristics, functions, significance,
                    origin_story, historical_context, current_status,
                    aliases, tags, text_references, confidence_score, extraction_method
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                """,
                entity_id, entity.novel_id, entity.framework_id, entity.name,
                entity.entity_type.value, entity.domain_type.value if entity.domain_type else None,
                [d.value for d in entity.dimensions], entity.description,
                json.dumps(entity.characteristics, ensure_ascii=False), entity.functions,
                entity.significance, entity.origin_story, entity.historical_context,
                entity.current_status, entity.aliases, entity.tags, entity.text_references,
                0.8, 'manual'
            )

        # 在MongoDB中创建详细记录
        await self._collections['cultural_entities_detailed'].insert_one({
            "novelId": str(entity.novel_id),
            "entityId": str(entity_id),
            "entityName": entity.name,
            "entityType": entity.entity_type.value,
            "detailedDescription": {
                "fullDescription": entity.description,
                "culturalSignificance": entity.significance or "",
                "functionalDescription": "\n".join(entity.functions),
                "physicalDescription": entity.characteristics.get("physical", "")
            },
            "history": {
                "origin": entity.origin_story or "",
                "currentState": entity.current_status or "",
                "keyEvents": [],
                "evolution": []
            },
            "relationships": {
                "directConnections": [],
                "indirectInfluences": [],
                "conflictingEntities": [],
                "supportingEntities": []
            },
            "analysis": {
                "importanceScore": 0.5,
                "influenceRadius": 0.5,
                "storyPotential": 0.5,
                "conflictPotential": 0.3
            },
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        })

        logger.info(f"创建文化实体: {entity.name} ({entity_id})")
        return entity_id

    async def get_cultural_entity(self, entity_id: UUID) -> Optional[CulturalEntity]:
        """获取文化实体详情"""
        async with self._pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM cultural_entities WHERE id = $1",
                entity_id
            )

            if row:
                return CulturalEntity(
                    id=row['id'],
                    novel_id=row['novel_id'],
                    framework_id=row['framework_id'],
                    name=row['name'],
                    entity_type=EntityType(row['entity_type']),
                    domain_type=DomainType(row['domain_type']) if row['domain_type'] else None,
                    dimensions=[CulturalDimension(d) for d in (row['dimensions'] or [])],
                    description=row['description'],
                    characteristics=json.loads(row['characteristics']) if row['characteristics'] else {},
                    functions=row['functions'] or [],
                    significance=row['significance'],
                    origin_story=row['origin_story'],
                    historical_context=row['historical_context'],
                    current_status=row['current_status'],
                    aliases=row['aliases'] or [],
                    tags=row['tags'] or [],
                    text_references=row['text_references'] or [],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        return None

    async def get_entities_by_type(self, novel_id: UUID, entity_type: EntityType,
                                 domain_type: Optional[DomainType] = None) -> List[CulturalEntity]:
        """按类型获取文化实体"""
        query = "SELECT * FROM cultural_entities WHERE novel_id = $1 AND entity_type = $2"
        params = [novel_id, entity_type.value]

        if domain_type:
            query += " AND domain_type = $3"
            params.append(domain_type.value)

        query += " ORDER BY name"

        async with self._pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

            return [
                CulturalEntity(
                    id=row['id'],
                    novel_id=row['novel_id'],
                    framework_id=row['framework_id'],
                    name=row['name'],
                    entity_type=EntityType(row['entity_type']),
                    domain_type=DomainType(row['domain_type']) if row['domain_type'] else None,
                    dimensions=[CulturalDimension(d) for d in (row['dimensions'] or [])],
                    description=row['description'],
                    characteristics=json.loads(row['characteristics']) if row['characteristics'] else {},
                    functions=row['functions'] or [],
                    significance=row['significance'],
                    origin_story=row['origin_story'],
                    historical_context=row['historical_context'],
                    current_status=row['current_status'],
                    aliases=row['aliases'] or [],
                    tags=row['tags'] or [],
                    text_references=row['text_references'] or [],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]

    # ====================================================================
    # 文化关系操作 (PostgreSQL + MongoDB)
    # ====================================================================

    async def create_cultural_relation(self, relation: CulturalRelationCreate) -> UUID:
        """创建文化关系"""
        relation_id = uuid4()

        # 检查源实体和目标实体的域信息
        source_domain, target_domain = await self._get_entity_domains(
            relation.source_entity_id, relation.target_entity_id
        )

        is_cross_domain = source_domain != target_domain if source_domain and target_domain else False

        # 在PostgreSQL中创建关系记录
        async with self._pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO cultural_relations (
                    id, novel_id, source_entity_id, target_entity_id, relation_type,
                    description, strength, context, is_cross_domain, source_domain,
                    target_domain, confidence_score, detection_method, bidirectional
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """,
                relation_id, relation.novel_id, relation.source_entity_id,
                relation.target_entity_id, relation.relation_type.value,
                relation.description, relation.strength, relation.context,
                is_cross_domain, source_domain, target_domain,
                0.8, 'manual', False
            )

        # 在MongoDB中创建语义关系记录
        source_entity = await self.get_cultural_entity(relation.source_entity_id)
        target_entity = await self.get_cultural_entity(relation.target_entity_id)

        if source_entity and target_entity:
            await self._collections['semantic_relations'].insert_one({
                "novelId": str(relation.novel_id),
                "relation_data": {
                    "source_entity": {
                        "id": str(source_entity.id),
                        "name": source_entity.name,
                        "type": source_entity.entity_type.value,
                        "domain": source_entity.domain_type.value if source_entity.domain_type else None
                    },
                    "target_entity": {
                        "id": str(target_entity.id),
                        "name": target_entity.name,
                        "type": target_entity.entity_type.value,
                        "domain": target_entity.domain_type.value if target_entity.domain_type else None
                    },
                    "relation_type": relation.relation_type.value,
                    "semantic_weight": relation.strength
                },
                "inference_path": [],
                "contextual_factors": {
                    "temporal_context": "current",
                    "cultural_context": relation.context or "",
                    "narrative_context": ""
                },
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            })

        logger.info(f"创建文化关系: {relation.relation_type.value} ({relation_id})")
        return relation_id

    async def get_entity_relations(self, entity_id: UUID) -> List[Dict[str, Any]]:
        """获取实体的所有关系"""
        async with self._pg_pool.acquire() as conn:
            # 获取作为源实体的关系
            source_relations = await conn.fetch(
                """
                SELECT r.*,
                       te.name as target_name, te.entity_type as target_type, te.domain_type as target_domain
                FROM cultural_relations r
                JOIN cultural_entities te ON r.target_entity_id = te.id
                WHERE r.source_entity_id = $1
                """,
                entity_id
            )

            # 获取作为目标实体的关系
            target_relations = await conn.fetch(
                """
                SELECT r.*,
                       se.name as source_name, se.entity_type as source_type, se.domain_type as source_domain
                FROM cultural_relations r
                JOIN cultural_entities se ON r.source_entity_id = se.id
                WHERE r.target_entity_id = $1
                """,
                entity_id
            )

            relations = []

            # 处理源关系
            for row in source_relations:
                relations.append({
                    "id": str(row['id']),
                    "direction": "outgoing",
                    "relation_type": row['relation_type'],
                    "other_entity": {
                        "id": str(row['target_entity_id']),
                        "name": row['target_name'],
                        "type": row['target_type'],
                        "domain": row['target_domain']
                    },
                    "strength": float(row['strength']),
                    "description": row['description'],
                    "is_cross_domain": row['is_cross_domain']
                })

            # 处理目标关系
            for row in target_relations:
                relations.append({
                    "id": str(row['id']),
                    "direction": "incoming",
                    "relation_type": row['relation_type'],
                    "other_entity": {
                        "id": str(row['source_entity_id']),
                        "name": row['source_name'],
                        "type": row['source_type'],
                        "domain": row['source_domain']
                    },
                    "strength": float(row['strength']),
                    "description": row['description'],
                    "is_cross_domain": row['is_cross_domain']
                })

            return relations

    # ====================================================================
    # 跨域分析操作
    # ====================================================================

    async def get_cross_domain_relations(self, novel_id: UUID) -> List[Dict[str, Any]]:
        """获取跨域关系分析"""
        async with self._pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT r.*,
                       se.name as source_name, se.entity_type as source_type,
                       te.name as target_name, te.entity_type as target_type
                FROM cultural_relations r
                JOIN cultural_entities se ON r.source_entity_id = se.id
                JOIN cultural_entities te ON r.target_entity_id = te.id
                WHERE r.novel_id = $1 AND r.is_cross_domain = TRUE
                ORDER BY r.strength DESC
                """,
                novel_id
            )

            return [
                {
                    "id": str(row['id']),
                    "source_domain": row['source_domain'],
                    "target_domain": row['target_domain'],
                    "relation_type": row['relation_type'],
                    "strength": float(row['strength']),
                    "source_entity": {
                        "name": row['source_name'],
                        "type": row['source_type']
                    },
                    "target_entity": {
                        "name": row['target_name'],
                        "type": row['target_type']
                    },
                    "description": row['description'],
                    "context": row['context']
                }
                for row in rows
            ]

    # ====================================================================
    # 批量数据导入操作 (MongoDB)
    # ====================================================================

    async def create_import_task(self, novel_id: UUID, task_name: str,
                               task_type: str, configuration: Dict[str, Any]) -> str:
        """创建批量导入任务"""
        task_data = {
            "novelId": str(novel_id),
            "taskName": task_name,
            "taskType": task_type,
            "status": "pending",
            "progress": {
                "totalRecords": 0,
                "processedRecords": 0,
                "successfulRecords": 0,
                "failedRecords": 0,
                "progressPercentage": 0.0
            },
            "configuration": configuration,
            "results": {
                "summary": "",
                "errors": [],
                "warnings": [],
                "statisticsSummary": {}
            },
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }

        result = await self._collections['import_tasks'].insert_one(task_data)
        task_id = str(result.inserted_id)

        logger.info(f"创建导入任务: {task_name} ({task_id})")
        return task_id

    async def update_import_task_progress(self, task_id: str, progress: Dict[str, Any]):
        """更新导入任务进度"""
        update_data = {
            "progress": progress,
            "updatedAt": datetime.now(timezone.utc)
        }

        await self._collections['import_tasks'].update_one(
            {"_id": task_id},
            {"$set": update_data}
        )

    # ====================================================================
    # 辅助方法
    # ====================================================================

    async def _get_entity_domains(self, source_id: UUID, target_id: UUID) -> Tuple[Optional[str], Optional[str]]:
        """获取实体的域信息"""
        async with self._pg_pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT
                    (SELECT domain_type FROM cultural_entities WHERE id = $1) as source_domain,
                    (SELECT domain_type FROM cultural_entities WHERE id = $2) as target_domain
                """,
                source_id, target_id
            )

            return result['source_domain'], result['target_domain'] if result else (None, None)

    async def get_novel_statistics(self, novel_id: UUID) -> Dict[str, Any]:
        """获取小说的文化数据统计"""
        async with self._pg_pool.acquire() as conn:
            # 获取PostgreSQL统计
            pg_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(DISTINCT cf.id) as framework_count,
                    COUNT(DISTINCT ce.id) as entity_count,
                    COUNT(DISTINCT cr.id) as relation_count,
                    COUNT(DISTINCT CASE WHEN cr.is_cross_domain THEN cr.id END) as cross_domain_relations,
                    AVG(cf.confidence_score) as avg_framework_confidence,
                    AVG(ce.confidence_score) as avg_entity_confidence
                FROM cultural_frameworks cf
                FULL OUTER JOIN cultural_entities ce ON cf.novel_id = ce.novel_id
                FULL OUTER JOIN cultural_relations cr ON cf.novel_id = cr.novel_id
                WHERE cf.novel_id = $1 OR ce.novel_id = $1 OR cr.novel_id = $1
                """,
                novel_id
            )

        # 获取MongoDB统计
        mongo_stats = await self._collections['cultural_details'].aggregate([
            {"$match": {"novelId": str(novel_id)}},
            {"$group": {
                "_id": None,
                "total_content": {"$sum": 1},
                "avg_quality": {"$avg": "$processingMetadata.qualityScore"},
                "avg_completeness": {"$avg": "$processingMetadata.completeness"}
            }}
        ]).to_list(length=1)

        mongo_data = mongo_stats[0] if mongo_stats else {}

        return {
            "postgresql_stats": {
                "framework_count": pg_stats['framework_count'] or 0,
                "entity_count": pg_stats['entity_count'] or 0,
                "relation_count": pg_stats['relation_count'] or 0,
                "cross_domain_relations": pg_stats['cross_domain_relations'] or 0,
                "avg_framework_confidence": float(pg_stats['avg_framework_confidence'] or 0),
                "avg_entity_confidence": float(pg_stats['avg_entity_confidence'] or 0)
            },
            "mongodb_stats": {
                "total_content": mongo_data.get('total_content', 0),
                "avg_quality": mongo_data.get('avg_quality', 0),
                "avg_completeness": mongo_data.get('avg_completeness', 0)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def search_entities(self, novel_id: UUID, search_query: str,
                            entity_types: Optional[List[EntityType]] = None,
                            domains: Optional[List[DomainType]] = None) -> List[Dict[str, Any]]:
        """全文搜索文化实体"""
        # PostgreSQL全文搜索
        query = """
        SELECT id, name, entity_type, domain_type, description, tags,
               ts_rank_cd(to_tsvector('simple', name || ' ' || description), plainto_tsquery('simple', $2)) as rank
        FROM cultural_entities
        WHERE novel_id = $1
        AND (to_tsvector('simple', name || ' ' || description) @@ plainto_tsquery('simple', $2))
        """
        params = [novel_id, search_query]

        if entity_types:
            query += f" AND entity_type = ANY($3)"
            params.append([et.value for et in entity_types])

        if domains:
            param_num = len(params) + 1
            query += f" AND domain_type = ANY(${param_num})"
            params.append([d.value for d in domains])

        query += " ORDER BY rank DESC LIMIT 50"

        async with self._pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

            return [
                {
                    "id": str(row['id']),
                    "name": row['name'],
                    "entity_type": row['entity_type'],
                    "domain_type": row['domain_type'],
                    "description": row['description'][:200] + "..." if len(row['description']) > 200 else row['description'],
                    "tags": row['tags'] or [],
                    "relevance_score": float(row['rank'])
                }
                for row in rows
            ]

    async def close(self):
        """关闭数据库连接"""
        if self._mongo_client:
            self._mongo_client.close()

        # PostgreSQL连接池由connection_manager管理，不需要手动关闭
        logger.info("文化框架数据仓库连接已关闭")