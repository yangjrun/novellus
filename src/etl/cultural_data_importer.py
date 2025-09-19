"""
文化框架数据导入器 - 负责批量导入解析后的文化数据
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID, uuid4
import traceback

import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError

from ..config import config
from ..database.models.cultural_framework_models import (
    CulturalFrameworkBatch, CulturalFrameworkCreate, CulturalEntityCreate,
    CulturalRelationCreate, PlotHookCreate, ConceptDictionaryCreate,
    DomainType, CulturalDimension, EntityType
)
from .cultural_text_parser import CulturalTextParser


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """数据库连接管理器"""

    def __init__(self):
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.mongo_db = None

    async def connect(self):
        """建立数据库连接"""
        try:
            # PostgreSQL连接
            self.pg_pool = await asyncpg.create_pool(
                host=config.postgres_host,
                port=config.postgres_port,
                database=config.postgres_db,
                user=config.postgres_user,
                password=config.postgres_password,
                min_size=5,
                max_size=20
            )
            logger.info("PostgreSQL连接池创建成功")

            # MongoDB连接
            self.mongo_client = AsyncIOMotorClient(config.mongodb_url)
            self.mongo_db = self.mongo_client[config.mongodb_db]
            logger.info("MongoDB连接创建成功")

        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    async def close(self):
        """关闭数据库连接"""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.mongo_client:
            self.mongo_client.close()


class CulturalDataImporter:
    """文化数据导入器"""

    def __init__(self, db_manager: DatabaseConnectionManager):
        self.db_manager = db_manager
        self.parser = CulturalTextParser()

    async def import_cultural_text(self, text: str, novel_id: UUID, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """导入文化框架文本"""
        start_time = datetime.utcnow()
        log_id = str(uuid4())

        # 记录开始处理
        await self._log_processing_start(log_id, novel_id, "text_parsing", {
            "input_size": len(text),
            "source_info": source_info or {}
        })

        try:
            # 1. 解析文本
            logger.info(f"开始解析文化框架文本，长度: {len(text)}")
            batch_data = self.parser.parse_cultural_text(text, novel_id)

            # 2. 验证数据
            validation_result = await self._validate_batch_data(batch_data)
            if not validation_result["valid"]:
                raise ValueError(f"数据验证失败: {validation_result['errors']}")

            # 3. 导入PostgreSQL
            pg_result = await self._import_to_postgresql(batch_data)

            # 4. 导入MongoDB
            mongo_result = await self._import_to_mongodb(batch_data, text, source_info)

            # 5. 记录处理成功
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._log_processing_success(log_id, novel_id, {
                "processing_time": processing_time,
                "frameworks_imported": len(batch_data.frameworks),
                "entities_imported": len(batch_data.entities),
                "relations_imported": len(batch_data.relations),
                "plot_hooks_imported": len(batch_data.plot_hooks),
                "concepts_imported": len(batch_data.concepts)
            })

            return {
                "success": True,
                "log_id": log_id,
                "processing_time": processing_time,
                "postgresql_result": pg_result,
                "mongodb_result": mongo_result,
                "statistics": {
                    "frameworks": len(batch_data.frameworks),
                    "entities": len(batch_data.entities),
                    "relations": len(batch_data.relations),
                    "plot_hooks": len(batch_data.plot_hooks),
                    "concepts": len(batch_data.concepts)
                }
            }

        except Exception as e:
            error_info = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
            await self._log_processing_error(log_id, novel_id, error_info)
            logger.error(f"文化数据导入失败: {e}")
            raise

    async def _validate_batch_data(self, batch_data: CulturalFrameworkBatch) -> Dict[str, Any]:
        """验证批量数据"""
        errors = []
        warnings = []

        # 验证数据完整性
        if not batch_data.frameworks:
            warnings.append("没有解析到文化框架数据")

        if not batch_data.entities:
            warnings.append("没有解析到文化实体")

        # 验证实体名称唯一性
        entity_names = set()
        for entity in batch_data.entities:
            if entity.name in entity_names:
                errors.append(f"实体名称重复: {entity.name}")
            entity_names.add(entity.name)

        # 验证关系的实体引用
        entity_ids = {entity.name: str(uuid4()) for entity in batch_data.entities}
        for relation in batch_data.relations:
            # 这里需要根据实际的ID匹配逻辑进行验证
            pass

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    async def _import_to_postgresql(self, batch_data: CulturalFrameworkBatch) -> Dict[str, Any]:
        """导入数据到PostgreSQL"""
        async with self.db_manager.pg_pool.acquire() as conn:
            async with conn.transaction():
                result = {
                    "frameworks": 0,
                    "entities": 0,
                    "relations": 0,
                    "plot_hooks": 0,
                    "concepts": 0
                }

                # 1. 导入文化框架
                if batch_data.frameworks:
                    frameworks_data = []
                    for framework in batch_data.frameworks:
                        frameworks_data.append((
                            str(uuid4()),
                            str(framework.novel_id),
                            framework.domain_type.value,
                            framework.dimension.value,
                            framework.title,
                            framework.summary,
                            framework.key_elements,
                            framework.detailed_content,
                            framework.tags,
                            framework.priority,
                            1.0,  # completion_status
                            datetime.utcnow(),
                            datetime.utcnow()
                        ))

                    await conn.executemany("""
                        INSERT INTO cultural_frameworks
                        (id, novel_id, domain_type, dimension, title, summary, key_elements,
                         detailed_content, tags, priority, completion_status, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        ON CONFLICT (novel_id, domain_type, dimension)
                        DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            key_elements = EXCLUDED.key_elements,
                            detailed_content = EXCLUDED.detailed_content,
                            tags = EXCLUDED.tags,
                            priority = EXCLUDED.priority,
                            updated_at = EXCLUDED.updated_at
                    """, frameworks_data)
                    result["frameworks"] = len(frameworks_data)

                # 2. 导入文化实体
                if batch_data.entities:
                    entities_data = []
                    entity_id_map = {}  # 保存实体名称到ID的映射

                    for entity in batch_data.entities:
                        entity_id = str(uuid4())
                        entity_id_map[entity.name] = entity_id

                        entities_data.append((
                            entity_id,
                            str(entity.novel_id),
                            None,  # framework_id 待关联
                            entity.name,
                            entity.entity_type.value,
                            entity.domain_type.value if entity.domain_type else None,
                            [d.value for d in entity.dimensions],
                            entity.description,
                            json.dumps(entity.characteristics),
                            entity.functions,
                            entity.significance,
                            entity.origin_story,
                            entity.historical_context,
                            entity.current_status,
                            entity.aliases,
                            entity.tags,
                            entity.references,
                            datetime.utcnow(),
                            datetime.utcnow()
                        ))

                    await conn.executemany("""
                        INSERT INTO cultural_entities
                        (id, novel_id, framework_id, name, entity_type, domain_type, dimensions,
                         description, characteristics, functions, significance, origin_story,
                         historical_context, current_status, aliases, tags, references, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                        ON CONFLICT (novel_id, name, entity_type)
                        DO UPDATE SET
                            description = EXCLUDED.description,
                            characteristics = EXCLUDED.characteristics,
                            functions = EXCLUDED.functions,
                            significance = EXCLUDED.significance,
                            updated_at = EXCLUDED.updated_at
                    """, entities_data)
                    result["entities"] = len(entities_data)

                # 3. 导入文化关系
                if batch_data.relations and entity_id_map:
                    relations_data = []
                    for relation in batch_data.relations:
                        # 需要通过实体名称找到对应的ID
                        # 这里简化处理，实际应该根据实体匹配逻辑
                        relations_data.append((
                            str(uuid4()),
                            str(relation.novel_id),
                            str(relation.source_entity_id),  # 需要映射为实际ID
                            str(relation.target_entity_id),  # 需要映射为实际ID
                            relation.relation_type.value,
                            relation.description,
                            relation.strength,
                            relation.context,
                            relation.is_cross_domain,
                            relation.source_domain.value if relation.source_domain else None,
                            relation.target_domain.value if relation.target_domain else None,
                            datetime.utcnow(),
                            datetime.utcnow()
                        ))

                    if relations_data:
                        await conn.executemany("""
                            INSERT INTO cultural_relations
                            (id, novel_id, source_entity_id, target_entity_id, relation_type,
                             description, strength, context, is_cross_domain, source_domain,
                             target_domain, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                            ON CONFLICT (source_entity_id, target_entity_id, relation_type)
                            DO UPDATE SET
                                description = EXCLUDED.description,
                                strength = EXCLUDED.strength,
                                context = EXCLUDED.context,
                                updated_at = EXCLUDED.updated_at
                        """, relations_data)
                        result["relations"] = len(relations_data)

                # 4. 导入剧情钩子
                if batch_data.plot_hooks:
                    hooks_data = []
                    for hook in batch_data.plot_hooks:
                        hooks_data.append((
                            str(uuid4()),
                            str(hook.novel_id),
                            hook.domain_type.value,
                            hook.title,
                            hook.description,
                            hook.trigger_conditions,
                            hook.potential_outcomes,
                            [str(entity_id) for entity_id in hook.related_entities],
                            [d.value for d in hook.cultural_dimensions],
                            hook.complexity_level,
                            hook.story_impact,
                            hook.tags,
                            datetime.utcnow(),
                            datetime.utcnow()
                        ))

                    await conn.executemany("""
                        INSERT INTO plot_hooks
                        (id, novel_id, domain_type, title, description, trigger_conditions,
                         potential_outcomes, related_entities, cultural_dimensions,
                         complexity_level, story_impact, tags, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    """, hooks_data)
                    result["plot_hooks"] = len(hooks_data)

                # 5. 导入概念词典
                if batch_data.concepts:
                    concepts_data = []
                    for concept in batch_data.concepts:
                        concepts_data.append((
                            str(uuid4()),
                            str(concept.novel_id),
                            concept.term,
                            concept.definition,
                            concept.category,
                            concept.domain_type.value if concept.domain_type else None,
                            concept.etymology,
                            concept.usage_examples,
                            concept.related_terms,
                            concept.frequency,
                            concept.importance,
                            datetime.utcnow(),
                            datetime.utcnow()
                        ))

                    await conn.executemany("""
                        INSERT INTO concept_dictionary
                        (id, novel_id, term, definition, category, domain_type, etymology,
                         usage_examples, related_terms, frequency, importance, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        ON CONFLICT (novel_id, term)
                        DO UPDATE SET
                            definition = EXCLUDED.definition,
                            category = EXCLUDED.category,
                            etymology = EXCLUDED.etymology,
                            usage_examples = EXCLUDED.usage_examples,
                            related_terms = EXCLUDED.related_terms,
                            frequency = EXCLUDED.frequency,
                            importance = EXCLUDED.importance,
                            updated_at = EXCLUDED.updated_at
                    """, concepts_data)
                    result["concepts"] = len(concepts_data)

                return result

    async def _import_to_mongodb(self, batch_data: CulturalFrameworkBatch, original_text: str, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """导入数据到MongoDB"""
        result = {"collections_updated": 0, "documents_inserted": 0}

        # 1. 保存原始文本和解析结果
        cultural_details_doc = {
            "novelId": str(batch_data.frameworks[0].novel_id) if batch_data.frameworks else "",
            "domainType": "多域" if len(set(f.domain_type for f in batch_data.frameworks)) > 1 else (
                batch_data.frameworks[0].domain_type.value if batch_data.frameworks else "未知"),
            "rawContent": original_text,
            "processedContent": {
                "frameworks": [self._framework_to_dict(f) for f in batch_data.frameworks],
                "entities": [self._entity_to_dict(e) for e in batch_data.entities],
                "relations": [self._relation_to_dict(r) for r in batch_data.relations],
                "plot_hooks": [self._plot_hook_to_dict(h) for h in batch_data.plot_hooks],
                "concepts": [self._concept_to_dict(c) for c in batch_data.concepts]
            },
            "parsedSections": self._create_parsed_sections(batch_data),
            "processingMetadata": {
                "version": "1.0.0",
                "processingDate": datetime.utcnow(),
                "parserVersion": "1.0.0",
                "qualityScore": self._calculate_quality_score(batch_data),
                "completeness": self._calculate_completeness(batch_data),
                "sourceInfo": source_info or {}
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        await self.db_manager.mongo_db.cultural_details.insert_one(cultural_details_doc)
        result["documents_inserted"] += 1
        result["collections_updated"] += 1

        # 2. 保存详细的剧情钩子
        if batch_data.plot_hooks:
            hook_docs = []
            for hook in batch_data.plot_hooks:
                hook_doc = {
                    "novelId": str(hook.novel_id),
                    "domainType": hook.domain_type.value,
                    "hookContent": {
                        "title": hook.title,
                        "description": hook.description,
                        "fullText": hook.description,
                        "structuredData": {
                            "trigger_conditions": hook.trigger_conditions,
                            "potential_outcomes": hook.potential_outcomes,
                            "complexity_level": hook.complexity_level,
                            "story_impact": hook.story_impact
                        }
                    },
                    "analysis": {
                        "themes": hook.tags,
                        "cultural_dimensions": [d.value for d in hook.cultural_dimensions]
                    },
                    "connections": {
                        "related_entities": [str(entity_id) for entity_id in hook.related_entities],
                        "cross_domain_links": [],
                        "cultural_references": []
                    },
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                hook_docs.append(hook_doc)

            if hook_docs:
                await self.db_manager.mongo_db.plot_hooks_detailed.insert_many(hook_docs)
                result["documents_inserted"] += len(hook_docs)

        # 3. 保存详细的概念词典
        if batch_data.concepts:
            concept_docs = []
            for concept in batch_data.concepts:
                concept_doc = {
                    "novelId": str(concept.novel_id),
                    "term": concept.term,
                    "definition": concept.definition,
                    "category": concept.category,
                    "domainType": concept.domain_type.value if concept.domain_type else None,
                    "detailedInfo": {
                        "etymology": concept.etymology,
                        "culturalContext": "",
                        "historicalBackground": "",
                        "variations": []
                    },
                    "usage": {
                        "frequency": concept.frequency,
                        "contexts": [],
                        "examples": concept.usage_examples,
                        "relatedTerms": concept.related_terms
                    },
                    "analysis": {
                        "importance": concept.importance,
                        "complexity": 5,
                        "storyRelevance": 0.8,
                        "culturalSignificance": 0.7
                    },
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                concept_docs.append(concept_doc)

            if concept_docs:
                # 使用upsert操作避免重复
                for doc in concept_docs:
                    await self.db_manager.mongo_db.concepts_dictionary.replace_one(
                        {"novelId": doc["novelId"], "term": doc["term"]},
                        doc,
                        upsert=True
                    )
                result["documents_inserted"] += len(concept_docs)

        return result

    # 辅助方法
    def _framework_to_dict(self, framework: CulturalFrameworkCreate) -> Dict[str, Any]:
        """转换文化框架为字典"""
        return {
            "domain_type": framework.domain_type.value,
            "dimension": framework.dimension.value,
            "title": framework.title,
            "summary": framework.summary,
            "key_elements": framework.key_elements,
            "detailed_content": framework.detailed_content,
            "tags": framework.tags,
            "priority": framework.priority
        }

    def _entity_to_dict(self, entity: CulturalEntityCreate) -> Dict[str, Any]:
        """转换文化实体为字典"""
        return {
            "name": entity.name,
            "entity_type": entity.entity_type.value,
            "domain_type": entity.domain_type.value if entity.domain_type else None,
            "dimensions": [d.value for d in entity.dimensions],
            "description": entity.description,
            "characteristics": entity.characteristics,
            "functions": entity.functions,
            "aliases": entity.aliases,
            "tags": entity.tags
        }

    def _relation_to_dict(self, relation: CulturalRelationCreate) -> Dict[str, Any]:
        """转换文化关系为字典"""
        return {
            "source_entity_id": str(relation.source_entity_id),
            "target_entity_id": str(relation.target_entity_id),
            "relation_type": relation.relation_type.value,
            "description": relation.description,
            "strength": relation.strength,
            "is_cross_domain": relation.is_cross_domain
        }

    def _plot_hook_to_dict(self, hook: PlotHookCreate) -> Dict[str, Any]:
        """转换剧情钩子为字典"""
        return {
            "title": hook.title,
            "description": hook.description,
            "domain_type": hook.domain_type.value,
            "trigger_conditions": hook.trigger_conditions,
            "potential_outcomes": hook.potential_outcomes,
            "complexity_level": hook.complexity_level,
            "story_impact": hook.story_impact,
            "tags": hook.tags
        }

    def _concept_to_dict(self, concept: ConceptDictionaryCreate) -> Dict[str, Any]:
        """转换概念为字典"""
        return {
            "term": concept.term,
            "definition": concept.definition,
            "category": concept.category,
            "domain_type": concept.domain_type.value if concept.domain_type else None,
            "frequency": concept.frequency,
            "importance": concept.importance
        }

    def _create_parsed_sections(self, batch_data: CulturalFrameworkBatch) -> List[Dict[str, Any]]:
        """创建解析段落数据"""
        sections = []
        for framework in batch_data.frameworks:
            sections.append({
                "dimension": framework.dimension.value,
                "title": framework.title,
                "content": framework.detailed_content,
                "keyElements": framework.key_elements,
                "extractedEntities": [entity.name for entity in batch_data.entities
                                    if framework.domain_type in [entity.domain_type] or
                                    framework.dimension in entity.dimensions],
                "tags": framework.tags
            })
        return sections

    def _calculate_quality_score(self, batch_data: CulturalFrameworkBatch) -> float:
        """计算质量分数"""
        score = 0.0

        # 基于数据完整性
        if batch_data.frameworks:
            score += 0.3
        if batch_data.entities:
            score += 0.3
        if batch_data.relations:
            score += 0.2
        if batch_data.plot_hooks:
            score += 0.1
        if batch_data.concepts:
            score += 0.1

        return min(score, 1.0)

    def _calculate_completeness(self, batch_data: CulturalFrameworkBatch) -> float:
        """计算完整度"""
        total_domains = len(DomainType)
        total_dimensions = len(CulturalDimension)

        covered_domains = len(set(f.domain_type for f in batch_data.frameworks))
        covered_dimensions = len(set(f.dimension for f in batch_data.frameworks))

        domain_completeness = covered_domains / total_domains
        dimension_completeness = covered_dimensions / total_dimensions

        return (domain_completeness + dimension_completeness) / 2

    async def _log_processing_start(self, log_id: str, novel_id: UUID, process_type: str, details: Dict[str, Any]):
        """记录处理开始"""
        log_doc = {
            "_id": log_id,
            "novelId": str(novel_id),
            "processType": process_type,
            "status": "started",
            "processDetails": details,
            "statistics": {},
            "issues": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        await self.db_manager.mongo_db.processing_logs.insert_one(log_doc)

    async def _log_processing_success(self, log_id: str, novel_id: UUID, result: Dict[str, Any]):
        """记录处理成功"""
        await self.db_manager.mongo_db.processing_logs.update_one(
            {"_id": log_id},
            {
                "$set": {
                    "status": "completed",
                    "processDetails.processingTime": result["processing_time"],
                    "statistics": {
                        "entitiesExtracted": result.get("entities_imported", 0),
                        "relationsFound": result.get("relations_imported", 0),
                        "conceptsIdentified": result.get("concepts_imported", 0),
                        "qualityScore": 0.85
                    },
                    "updatedAt": datetime.utcnow()
                }
            }
        )

    async def _log_processing_error(self, log_id: str, novel_id: UUID, error_info: Dict[str, Any]):
        """记录处理错误"""
        await self.db_manager.mongo_db.processing_logs.update_one(
            {"_id": log_id},
            {
                "$set": {
                    "status": "failed",
                    "processDetails.processingTime": error_info["processing_time"],
                    "issues": [{
                        "type": "error",
                        "severity": "high",
                        "message": error_info["error"],
                        "context": error_info.get("traceback", "")
                    }],
                    "updatedAt": datetime.utcnow()
                }
            }
        )


# 主要的导入函数
async def import_cultural_framework_text(text: str, novel_id: str, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """导入文化框架文本的主函数"""
    db_manager = DatabaseConnectionManager()

    try:
        await db_manager.connect()
        importer = CulturalDataImporter(db_manager)

        novel_uuid = UUID(novel_id)
        result = await importer.import_cultural_text(text, novel_uuid, source_info)

        return result

    finally:
        await db_manager.close()


# 命令行接口
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="导入文化框架文本数据")
    parser.add_argument("--file", required=True, help="文本文件路径")
    parser.add_argument("--novel-id", required=True, help="小说ID")
    parser.add_argument("--encoding", default="utf-8", help="文件编码")

    args = parser.parse_args()

    try:
        with open(args.file, 'r', encoding=args.encoding) as f:
            text = f.read()

        result = asyncio.run(import_cultural_framework_text(
            text,
            args.novel_id,
            {"source_file": args.file, "encoding": args.encoding}
        ))

        print(f"导入成功!")
        print(f"处理时间: {result['processing_time']:.2f}秒")
        print(f"导入统计: {result['statistics']}")

    except Exception as e:
        print(f"导入失败: {e}")
        sys.exit(1)