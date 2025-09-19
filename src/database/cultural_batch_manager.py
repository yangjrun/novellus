"""
文化数据批量管理器 - 支持大规模文化框架数据的导入、处理和验证
基于data-engineer处理的文化框架分析结果进行批量导入
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID, uuid4

from .repositories.cultural_framework_repository import CulturalFrameworkRepository
from .models.cultural_framework_models import (
    CulturalFrameworkCreate, CulturalEntityCreate, CulturalRelationCreate,
    DomainType, EntityType, RelationType, CulturalDimension
)

logger = logging.getLogger(__name__)


class CulturalDataBatchManager:
    """文化数据批量管理器"""

    def __init__(self, repository: CulturalFrameworkRepository):
        self.repository = repository
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'warnings': []
        }

    async def import_cultural_framework_analysis(self,
                                               novel_id: UUID,
                                               analysis_data: Dict[str, Any],
                                               task_name: str = "文化框架分析导入") -> str:
        """
        导入文化框架分析结果
        基于data-engineer的分析输出格式
        """

        # 创建导入任务
        task_id = await self.repository.create_import_task(
            novel_id=novel_id,
            task_name=task_name,
            task_type="full_import",
            configuration={
                "source_type": "cultural_analysis",
                "analysis_metadata": analysis_data.get("analysis_metadata", {}),
                "enable_validation": True,
                "create_relations": True
            }
        )

        try:
            # 重置统计
            self.processing_stats = {
                'total_processed': 0,
                'successful': 0,
                'failed': 0,
                'warnings': [],
                'entities_by_type': {},
                'relations_created': 0,
                'frameworks_created': 0
            }

            logger.info(f"开始导入文化框架分析数据 - 任务ID: {task_id}")

            # 第一阶段：导入域文化框架
            await self._import_domain_cultures(novel_id, analysis_data.get("domain_cultures", {}))

            # 第二阶段：导入文化实体
            await self._import_cultural_entities(novel_id, analysis_data)

            # 第三阶段：导入跨域关系
            await self._import_cross_domain_relations(novel_id, analysis_data.get("cross_domain_relations", []))

            # 第四阶段：导入概念词典
            await self._import_concept_dictionary(novel_id, analysis_data.get("concept_dictionary", []))

            # 更新任务完成状态
            await self.repository.update_import_task_progress(task_id, {
                "totalRecords": self.processing_stats['total_processed'],
                "processedRecords": self.processing_stats['total_processed'],
                "successfulRecords": self.processing_stats['successful'],
                "failedRecords": self.processing_stats['failed'],
                "progressPercentage": 100.0
            })

            logger.info(f"文化框架数据导入完成 - 任务ID: {task_id}")
            logger.info(f"处理统计: {self.processing_stats}")

            return task_id

        except Exception as e:
            logger.error(f"导入文化框架数据失败: {e}")
            logger.error(traceback.format_exc())

            # 更新任务失败状态
            await self.repository.update_import_task_progress(task_id, {
                "totalRecords": self.processing_stats['total_processed'],
                "processedRecords": self.processing_stats['total_processed'],
                "successfulRecords": self.processing_stats['successful'],
                "failedRecords": self.processing_stats['failed'],
                "progressPercentage": 0.0
            })

            raise

    async def _import_domain_cultures(self, novel_id: UUID, domain_cultures: Dict[str, Any]):
        """导入域文化框架数据"""
        logger.info("开始导入域文化框架...")

        for domain_name, domain_data in domain_cultures.items():
            try:
                # 转换域名称
                domain_type = self._normalize_domain_name(domain_name)
                if not domain_type:
                    self.processing_stats['warnings'].append(f"未知域类型: {domain_name}")
                    continue

                # 导入六个文化维度的框架
                for dimension_key, dimension_data in domain_data.items():
                    if dimension_key in ['analysis_summary', 'total_entities', 'entity_distribution']:
                        continue  # 跳过元数据

                    dimension = self._normalize_dimension_name(dimension_key)
                    if not dimension:
                        self.processing_stats['warnings'].append(f"未知文化维度: {dimension_key}")
                        continue

                    # 创建文化框架记录
                    framework = CulturalFrameworkCreate(
                        novel_id=novel_id,
                        domain_type=domain_type,
                        dimension=dimension,
                        title=f"{domain_name}{dimension.value}",
                        summary=dimension_data.get('summary', ''),
                        key_elements=dimension_data.get('key_elements', []),
                        detailed_content=dimension_data.get('content', ''),
                        tags=dimension_data.get('tags', []),
                        priority=8  # 高优先级
                    )

                    framework_id = await self.repository.create_cultural_framework(framework)
                    self.processing_stats['frameworks_created'] += 1
                    self.processing_stats['successful'] += 1

                logger.info(f"域 {domain_name} 文化框架导入完成")

            except Exception as e:
                logger.error(f"导入域 {domain_name} 文化框架失败: {e}")
                self.processing_stats['failed'] += 1

    async def _import_cultural_entities(self, novel_id: UUID, analysis_data: Dict[str, Any]):
        """导入文化实体数据"""
        logger.info("开始导入文化实体...")

        # 从domain_cultures中提取实体
        domain_cultures = analysis_data.get("domain_cultures", {})
        entity_id_mapping = {}  # 保存实体名称到ID的映射，用于后续关系创建

        for domain_name, domain_data in domain_cultures.items():
            domain_type = self._normalize_domain_name(domain_name)
            if not domain_type:
                continue

            for dimension_key, dimension_data in domain_data.items():
                if dimension_key in ['analysis_summary', 'total_entities', 'entity_distribution']:
                    continue

                dimension = self._normalize_dimension_name(dimension_key)
                if not dimension:
                    continue

                # 处理该维度下的实体
                entities = dimension_data.get('entities', [])
                for entity_data in entities:
                    try:
                        entity_type = self._normalize_entity_type(entity_data.get('type', ''))
                        if not entity_type:
                            self.processing_stats['warnings'].append(
                                f"未知实体类型: {entity_data.get('type', '')}"
                            )
                            continue

                        # 创建文化实体
                        entity = CulturalEntityCreate(
                            novel_id=novel_id,
                            name=entity_data['name'],
                            entity_type=entity_type,
                            domain_type=domain_type,
                            dimensions=[dimension],
                            description=entity_data.get('description', ''),
                            characteristics=entity_data.get('characteristics', {}),
                            functions=entity_data.get('functions', []),
                            significance=entity_data.get('significance', ''),
                            tags=entity_data.get('tags', [])
                        )

                        entity_id = await self.repository.create_cultural_entity(entity)
                        entity_id_mapping[entity_data['name']] = entity_id

                        # 统计
                        entity_type_key = entity_type.value
                        if entity_type_key not in self.processing_stats['entities_by_type']:
                            self.processing_stats['entities_by_type'][entity_type_key] = 0
                        self.processing_stats['entities_by_type'][entity_type_key] += 1

                        self.processing_stats['successful'] += 1
                        self.processing_stats['total_processed'] += 1

                    except Exception as e:
                        logger.error(f"创建实体 {entity_data.get('name', 'Unknown')} 失败: {e}")
                        self.processing_stats['failed'] += 1

        # 保存实体映射供后续使用
        self._entity_id_mapping = entity_id_mapping
        logger.info(f"文化实体导入完成，共创建 {len(entity_id_mapping)} 个实体")

    async def _import_cross_domain_relations(self, novel_id: UUID, cross_domain_relations: List[Dict[str, Any]]):
        """导入跨域关系数据"""
        logger.info("开始导入跨域关系...")

        for relation_data in cross_domain_relations:
            try:
                source_name = relation_data.get('source_entity', '')
                target_name = relation_data.get('target_entity', '')

                # 查找实体ID
                source_id = self._entity_id_mapping.get(source_name)
                target_id = self._entity_id_mapping.get(target_name)

                if not source_id or not target_id:
                    self.processing_stats['warnings'].append(
                        f"无法找到关系实体: {source_name} -> {target_name}"
                    )
                    continue

                # 规范化关系类型
                relation_type = self._normalize_relation_type(relation_data.get('relationship_type', ''))
                if not relation_type:
                    self.processing_stats['warnings'].append(
                        f"未知关系类型: {relation_data.get('relationship_type', '')}"
                    )
                    continue

                # 创建关系
                relation = CulturalRelationCreate(
                    novel_id=novel_id,
                    source_entity_id=source_id,
                    target_entity_id=target_id,
                    relation_type=relation_type,
                    description=relation_data.get('description', ''),
                    strength=relation_data.get('strength', 0.8),
                    context=relation_data.get('context', ''),
                    is_cross_domain=True
                )

                relation_id = await self.repository.create_cultural_relation(relation)
                self.processing_stats['relations_created'] += 1
                self.processing_stats['successful'] += 1

            except Exception as e:
                logger.error(f"创建跨域关系失败: {e}")
                self.processing_stats['failed'] += 1

        logger.info(f"跨域关系导入完成，共创建 {self.processing_stats['relations_created']} 个关系")

    async def _import_concept_dictionary(self, novel_id: UUID, concept_dictionary: List[Dict[str, Any]]):
        """导入概念词典数据"""
        logger.info("开始导入概念词典...")

        for concept_data in concept_dictionary:
            try:
                # 这里需要实现概念词典的导入逻辑
                # 暂时跳过，因为需要先实现ConceptDictionary的仓库方法
                pass

            except Exception as e:
                logger.error(f"导入概念 {concept_data.get('term', 'Unknown')} 失败: {e}")
                self.processing_stats['failed'] += 1

    # ====================================================================
    # 数据规范化方法
    # ====================================================================

    def _normalize_domain_name(self, domain_name: str) -> Optional[DomainType]:
        """规范化域名称"""
        domain_mapping = {
            '人域': DomainType.HUMAN_DOMAIN,
            '天域': DomainType.HEAVEN_DOMAIN,
            '荒域': DomainType.WILD_DOMAIN,
            '冥域': DomainType.UNDERWORLD_DOMAIN,
            '魔域': DomainType.DEMON_DOMAIN,
            '虚域': DomainType.VOID_DOMAIN,
            '海域': DomainType.SEA_DOMAIN,
            '源域': DomainType.SOURCE_DOMAIN
        }
        return domain_mapping.get(domain_name)

    def _normalize_dimension_name(self, dimension_name: str) -> Optional[CulturalDimension]:
        """规范化文化维度名称"""
        # 移除字母前缀 (A, B, C, D, E, F)
        clean_name = dimension_name.strip()
        if len(clean_name) > 2 and clean_name[0].isalpha() and clean_name[1] in ['.', ' ']:
            clean_name = clean_name[2:].strip()

        dimension_mapping = {
            '神话与宗教': CulturalDimension.MYTHOLOGY_RELIGION,
            '权力与法律': CulturalDimension.POWER_LAW,
            '经济与技术': CulturalDimension.ECONOMY_TECHNOLOGY,
            '家庭与教育': CulturalDimension.FAMILY_EDUCATION,
            '仪式与日常': CulturalDimension.RITUAL_DAILY,
            '艺术与娱乐': CulturalDimension.ART_ENTERTAINMENT
        }
        return dimension_mapping.get(clean_name)

    def _normalize_entity_type(self, entity_type: str) -> Optional[EntityType]:
        """规范化实体类型"""
        type_mapping = {
            '组织机构': EntityType.ORGANIZATION,
            '组织': EntityType.ORGANIZATION,
            '机构': EntityType.ORGANIZATION,
            '重要概念': EntityType.CONCEPT,
            '概念': EntityType.CONCEPT,
            '文化物品': EntityType.ITEM,
            '物品': EntityType.ITEM,
            '器物': EntityType.ITEM,
            '仪式活动': EntityType.RITUAL,
            '仪式': EntityType.RITUAL,
            '活动': EntityType.RITUAL,
            '身份制度': EntityType.SYSTEM,
            '制度': EntityType.SYSTEM,
            '货币体系': EntityType.CURRENCY,
            '货币': EntityType.CURRENCY,
            '技术工艺': EntityType.TECHNOLOGY,
            '技术': EntityType.TECHNOLOGY,
            '工艺': EntityType.TECHNOLOGY,
            '信仰体系': EntityType.BELIEF,
            '信仰': EntityType.BELIEF,
            '习俗传统': EntityType.CUSTOM,
            '习俗': EntityType.CUSTOM,
            '传统': EntityType.CUSTOM
        }
        return type_mapping.get(entity_type)

    def _normalize_relation_type(self, relation_type: str) -> Optional[RelationType]:
        """规范化关系类型"""
        type_mapping = {
            '包含': RelationType.CONTAINS,
            '关联': RelationType.RELATED_TO,
            '冲突': RelationType.CONFLICTS_WITH,
            '衍生自': RelationType.DERIVED_FROM,
            '控制': RelationType.CONTROLS,
            '受影响于': RelationType.INFLUENCED_BY,
            '相似于': RelationType.SIMILAR_TO,
            '影响': RelationType.CONTROLS,  # 映射到控制
            '依赖': RelationType.RELATED_TO,  # 映射到关联
            '对立': RelationType.CONFLICTS_WITH,  # 映射到冲突
            '统治': RelationType.CONTROLS  # 映射到控制
        }
        return type_mapping.get(relation_type)

    # ====================================================================
    # 数据验证和质量检查
    # ====================================================================

    async def validate_imported_data(self, novel_id: UUID) -> Dict[str, Any]:
        """验证导入的数据质量"""
        logger.info("开始验证导入数据质量...")

        validation_results = {
            "overall_status": "success",
            "statistics": {},
            "issues": [],
            "recommendations": []
        }

        try:
            # 获取统计信息
            stats = await self.repository.get_novel_statistics(novel_id)
            validation_results["statistics"] = stats

            # 检查数据完整性
            pg_stats = stats["postgresql_stats"]

            # 检查1：是否有孤立实体（没有关系的实体）
            if pg_stats["entity_count"] > 0 and pg_stats["relation_count"] == 0:
                validation_results["issues"].append({
                    "type": "warning",
                    "message": "存在实体但没有关系数据，可能影响关系分析"
                })

            # 检查2：跨域关系比例
            if pg_stats["relation_count"] > 0:
                cross_domain_ratio = pg_stats["cross_domain_relations"] / pg_stats["relation_count"]
                if cross_domain_ratio < 0.1:
                    validation_results["issues"].append({
                        "type": "info",
                        "message": f"跨域关系比例较低 ({cross_domain_ratio:.2%})，可能需要加强域间关系分析"
                    })

            # 检查3：置信度评估
            if pg_stats["avg_entity_confidence"] < 0.7:
                validation_results["issues"].append({
                    "type": "warning",
                    "message": f"实体平均置信度较低 ({pg_stats['avg_entity_confidence']:.2f})，建议人工验证"
                })

            # 生成推荐
            if pg_stats["entity_count"] > 50:
                validation_results["recommendations"].append("数据规模较大，建议启用知识图谱可视化分析")

            if pg_stats["cross_domain_relations"] > 10:
                validation_results["recommendations"].append("跨域关系丰富，建议进行深度的跨域分析")

            logger.info("数据质量验证完成")

        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            validation_results["overall_status"] = "error"
            validation_results["issues"].append({
                "type": "error",
                "message": f"验证过程出错: {str(e)}"
            })

        return validation_results

    async def export_cultural_data(self, novel_id: UUID, export_format: str = "json") -> Dict[str, Any]:
        """导出文化数据"""
        logger.info(f"开始导出文化数据 (格式: {export_format})...")

        try:
            # 获取所有文化框架
            frameworks = await self.repository.get_frameworks_by_novel(novel_id)

            # 获取所有文化实体
            all_entities = []
            for entity_type in EntityType:
                entities = await self.repository.get_entities_by_type(novel_id, entity_type)
                all_entities.extend(entities)

            # 获取跨域关系
            cross_domain_relations = await self.repository.get_cross_domain_relations(novel_id)

            # 获取统计信息
            statistics = await self.repository.get_novel_statistics(novel_id)

            export_data = {
                "export_metadata": {
                    "novel_id": str(novel_id),
                    "export_time": datetime.now(timezone.utc).isoformat(),
                    "export_format": export_format,
                    "total_frameworks": len(frameworks),
                    "total_entities": len(all_entities),
                    "total_cross_domain_relations": len(cross_domain_relations)
                },
                "cultural_frameworks": [
                    {
                        "id": str(fw.id),
                        "domain_type": fw.domain_type.value,
                        "dimension": fw.dimension.value,
                        "title": fw.title,
                        "summary": fw.summary,
                        "key_elements": fw.key_elements,
                        "detailed_content": fw.detailed_content,
                        "tags": fw.tags,
                        "priority": fw.priority
                    }
                    for fw in frameworks
                ],
                "cultural_entities": [
                    {
                        "id": str(entity.id),
                        "name": entity.name,
                        "entity_type": entity.entity_type.value,
                        "domain_type": entity.domain_type.value if entity.domain_type else None,
                        "dimensions": [d.value for d in entity.dimensions],
                        "description": entity.description,
                        "characteristics": entity.characteristics,
                        "functions": entity.functions,
                        "significance": entity.significance,
                        "tags": entity.tags
                    }
                    for entity in all_entities
                ],
                "cross_domain_relations": cross_domain_relations,
                "statistics": statistics
            }

            logger.info("文化数据导出完成")
            return export_data

        except Exception as e:
            logger.error(f"导出文化数据失败: {e}")
            raise

    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return self.processing_stats.copy()


# 使用示例函数
async def example_import_cultural_data():
    """示例：导入文化框架分析数据"""

    # 模拟data-engineer处理后的分析数据结构
    sample_analysis_data = {
        "analysis_metadata": {
            "timestamp": "2025-01-19T10:00:00Z",
            "total_domains": 9,
            "total_entities": 109,
            "total_relations": 28,
            "average_confidence": 0.91
        },
        "domain_cultures": {
            "人域": {
                "A. 神话与宗教": {
                    "summary": "以法则链信仰为核心的宗教体系",
                    "content": "人域居民信仰法则链的力量...",
                    "key_elements": ["法则链信仰", "祭司议会", "宗教仪式"],
                    "entities": [
                        {
                            "name": "祭司议会",
                            "type": "组织机构",
                            "description": "人域的宗教管理机构",
                            "characteristics": {"成员数量": "约200人", "权力范围": "宗教事务"},
                            "functions": ["法则解释", "宗教仪式主持", "信仰指导"]
                        }
                    ]
                },
                "B. 权力与法律": {
                    "summary": "天命王朝统治下的政治体系",
                    "content": "人域由天命王朝统治...",
                    "key_elements": ["天命王朝", "链籍三等制", "法则法庭"],
                    "entities": [
                        {
                            "name": "天命王朝",
                            "type": "组织机构",
                            "description": "人域的政治统治机构",
                            "characteristics": {"建立时间": "数千年前", "统治范围": "整个人域"},
                            "functions": ["政治统治", "法律制定", "军事管理"]
                        }
                    ]
                }
            }
        },
        "cross_domain_relations": [
            {
                "source_entity": "天命王朝",
                "target_entity": "祭司议会",
                "relationship_type": "控制",
                "strength": 0.9,
                "description": "天命王朝对祭司议会有政治控制权",
                "context": "政治宗教关系"
            }
        ],
        "concept_dictionary": [
            {
                "term": "法则链",
                "definition": "连接世界本源的神圣纽带",
                "category": "核心概念",
                "domain": "通用",
                "importance": 10
            }
        ]
    }

    # 这里只是示例，实际使用时需要正确的repository实例
    # batch_manager = CulturalDataBatchManager(repository)
    # novel_id = UUID("e1fd1aa4-bde2-4c76-8cee-334e54fa47d1")
    # task_id = await batch_manager.import_cultural_framework_analysis(novel_id, sample_analysis_data)
    # print(f"导入任务ID: {task_id}")

    logger.info("示例导入函数定义完成")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_import_cultural_data())