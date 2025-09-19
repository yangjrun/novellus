"""
九域文化框架完整处理管道 - 集成所有处理组件的主流程
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from pathlib import Path

from .nine_domains_cultural_processor import NineDomainsCulturalProcessor
from .advanced_chinese_text_analyzer import ChineseTextAnalyzer
from .nine_domains_entity_extractor import NineDomainsEntityExtractor
from .cross_domain_analyzer import CrossDomainAnalyzer
from .cultural_data_validator import CulturalDataValidator
from .cultural_data_importer import CulturalDataImporter, DatabaseConnectionManager

from ..database.models.cultural_framework_models import (
    CulturalFrameworkBatch, DomainType, CulturalDimension
)

logger = logging.getLogger(__name__)


class NineDomainsPipeline:
    """九域文化框架处理管道"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.initialize_components()
        self.initialize_settings()

    def initialize_components(self):
        """初始化处理组件"""
        self.cultural_processor = NineDomainsCulturalProcessor()
        self.text_analyzer = ChineseTextAnalyzer()
        self.entity_extractor = NineDomainsEntityExtractor()
        self.cross_domain_analyzer = CrossDomainAnalyzer()
        self.data_validator = CulturalDataValidator()
        self.db_manager = DatabaseConnectionManager()
        self.data_importer = None  # 延迟初始化

        logger.info("处理组件初始化完成")

    def initialize_settings(self):
        """初始化设置"""
        self.settings = {
            "enable_text_cleaning": True,
            "enable_validation": True,
            "enable_cross_domain_analysis": True,
            "enable_database_import": True,
            "validation_level": "NORMAL",
            "max_concurrent_processing": 3,
            "chunk_size": 5000,  # 文本分块大小
            "enable_auto_fix": True,
            "save_intermediate_results": True,
            "output_detailed_logs": True
        }

        # 更新配置
        if self.config:
            self.settings.update(self.config)

        logger.info(f"处理设置: {self.settings}")

    async def process_cultural_text(self, text: str, novel_id: UUID,
                                  source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理文化框架文本的主入口"""
        process_id = str(uuid4())
        start_time = datetime.utcnow()

        logger.info(f"开始处理文化文本 [{process_id}]，长度: {len(text)} 字符")

        try:
            # 1. 预处理阶段
            preprocessing_result = await self._preprocess_text(text, process_id)
            cleaned_text = preprocessing_result["cleaned_text"]
            preprocessing_stats = preprocessing_result["stats"]

            # 2. 核心处理阶段
            processing_result = await self._core_processing(cleaned_text, novel_id, process_id)

            # 3. 后处理阶段
            postprocessing_result = await self._postprocess_data(
                processing_result["batch_data"], novel_id, process_id
            )

            # 4. 数据库导入阶段
            import_result = None
            if self.settings["enable_database_import"]:
                import_result = await self._import_to_database(
                    postprocessing_result["final_batch"], novel_id, source_info, process_id
                )

            # 5. 生成最终结果
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            final_result = {
                "success": True,
                "process_id": process_id,
                "processing_time": processing_time,
                "preprocessing": preprocessing_result,
                "core_processing": processing_result,
                "postprocessing": postprocessing_result,
                "database_import": import_result,
                "summary": self._generate_processing_summary(
                    postprocessing_result["final_batch"], processing_time
                )
            }

            logger.info(f"文化文本处理完成 [{process_id}]，耗时: {processing_time:.2f}秒")
            return final_result

        except Exception as e:
            error_info = {
                "success": False,
                "process_id": process_id,
                "error": str(e),
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
            logger.error(f"文化文本处理失败 [{process_id}]: {e}")
            return error_info

    async def _preprocess_text(self, text: str, process_id: str) -> Dict[str, Any]:
        """预处理文本"""
        logger.info(f"开始文本预处理 [{process_id}]")

        # 1. 基础清洗
        cleaned_text = text
        if self.settings["enable_text_cleaning"]:
            # 简单的文本清洗
            cleaned_text = self._basic_text_cleaning(text)

        # 2. 文本分析
        text_analysis = None
        if hasattr(self.text_analyzer, 'analyze_text_structure'):
            text_segments = self.text_analyzer.analyze_text_structure(cleaned_text)
            named_entities = self.text_analyzer.extract_named_entities(cleaned_text)
            semantic_relations = self.text_analyzer.extract_semantic_relations(cleaned_text, named_entities)
            cultural_themes = self.text_analyzer.analyze_cultural_themes(cleaned_text)
            key_concepts = self.text_analyzer.extract_key_concepts(cleaned_text)

            text_analysis = {
                "segments_count": len(text_segments),
                "entities_count": len(named_entities),
                "relations_count": len(semantic_relations),
                "themes": cultural_themes,
                "key_concepts": key_concepts[:10]  # 前10个关键概念
            }

        # 3. 文本分块（如果需要）
        chunks = []
        if len(cleaned_text) > self.settings["chunk_size"]:
            chunks = self._split_text_into_chunks(cleaned_text)
        else:
            chunks = [cleaned_text]

        stats = {
            "original_length": len(text),
            "cleaned_length": len(cleaned_text),
            "chunks_count": len(chunks),
            "text_analysis": text_analysis
        }

        logger.info(f"文本预处理完成 [{process_id}]，分块数: {len(chunks)}")

        return {
            "cleaned_text": cleaned_text,
            "chunks": chunks,
            "stats": stats
        }

    async def _core_processing(self, text: str, novel_id: UUID, process_id: str) -> Dict[str, Any]:
        """核心处理流程"""
        logger.info(f"开始核心处理 [{process_id}]")

        # 1. 九域文化处理
        batch_data = await self.cultural_processor.process_nine_domains_text(text, novel_id)

        # 2. 增强实体提取
        enhanced_entities = self.entity_extractor.extract_entities(text)

        # 将增强的实体合并到批次数据中
        for extracted_entity in enhanced_entities:
            # 转换为CulturalEntityCreate格式
            enhanced_entity = self._convert_extracted_entity(extracted_entity, novel_id)
            if enhanced_entity:
                batch_data.entities.append(enhanced_entity)

        # 3. 跨域关系分析
        cross_domain_result = None
        if self.settings["enable_cross_domain_analysis"]:
            cross_domain_result = self.cross_domain_analyzer.analyze_cross_domain_relationships(
                text, batch_data.entities
            )

            # 将跨域关系添加到批次数据
            if cross_domain_result.get("cross_domain_relations"):
                for cross_relation in cross_domain_result["cross_domain_relations"]:
                    cultural_relation = self._convert_cross_domain_relation(cross_relation, novel_id)
                    if cultural_relation:
                        batch_data.relations.append(cultural_relation)

        stats = {
            "frameworks_extracted": len(batch_data.frameworks),
            "entities_extracted": len(batch_data.entities),
            "relations_extracted": len(batch_data.relations),
            "plot_hooks_extracted": len(batch_data.plot_hooks),
            "concepts_extracted": len(batch_data.concepts),
            "cross_domain_analysis": cross_domain_result is not None
        }

        logger.info(f"核心处理完成 [{process_id}]，提取实体: {len(batch_data.entities)}")

        return {
            "batch_data": batch_data,
            "cross_domain_result": cross_domain_result,
            "stats": stats
        }

    async def _postprocess_data(self, batch_data: CulturalFrameworkBatch, novel_id: UUID,
                               process_id: str) -> Dict[str, Any]:
        """后处理数据"""
        logger.info(f"开始数据后处理 [{process_id}]")

        # 1. 数据验证
        validation_result = None
        if self.settings["enable_validation"]:
            validation_result = self.data_validator.validate_cultural_batch(batch_data)

        # 2. 数据清洗
        cleaned_batch = batch_data
        cleaning_operations = []

        if self.settings["enable_auto_fix"] and validation_result:
            cleaned_batch, cleaning_operations = self.data_validator.clean_cultural_batch(batch_data)

        # 3. 数据增强
        enhanced_batch = await self._enhance_batch_data(cleaned_batch, novel_id)

        # 4. 最终优化
        final_batch = self._optimize_batch_data(enhanced_batch)

        stats = {
            "validation_passed": validation_result.is_valid if validation_result else None,
            "quality_score": validation_result.quality_score if validation_result else None,
            "cleaning_operations": len(cleaning_operations),
            "final_entities": len(final_batch.entities),
            "final_relations": len(final_batch.relations),
            "final_concepts": len(final_batch.concepts)
        }

        logger.info(f"数据后处理完成 [{process_id}]，质量分数: {stats.get('quality_score', 'N/A')}")

        return {
            "validation_result": validation_result,
            "cleaning_operations": cleaning_operations,
            "enhanced_batch": enhanced_batch,
            "final_batch": final_batch,
            "stats": stats
        }

    async def _import_to_database(self, batch_data: CulturalFrameworkBatch, novel_id: UUID,
                                 source_info: Dict[str, Any], process_id: str) -> Dict[str, Any]:
        """导入数据到数据库"""
        logger.info(f"开始数据库导入 [{process_id}]")

        try:
            if not self.data_importer:
                await self.db_manager.connect()
                self.data_importer = CulturalDataImporter(self.db_manager)

            # 执行导入
            import_result = await self.data_importer.import_cultural_text(
                "", # 原始文本已在之前步骤处理
                novel_id,
                source_info
            )

            logger.info(f"数据库导入完成 [{process_id}]")
            return import_result

        except Exception as e:
            logger.error(f"数据库导入失败 [{process_id}]: {e}")
            return {"success": False, "error": str(e)}

    def _basic_text_cleaning(self, text: str) -> str:
        """基础文本清洗"""
        # 移除多余空白
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)

        # 标准化标点符号
        cleaned = cleaned.replace('：', '：')
        cleaned = cleaned.replace('，', '，')
        cleaned = cleaned.replace('。', '。')

        return cleaned.strip()

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """将文本分割成块"""
        chunks = []
        chunk_size = self.settings["chunk_size"]

        # 按段落分割
        paragraphs = text.split('\n\n')
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _convert_extracted_entity(self, extracted_entity, novel_id: UUID):
        """转换提取的实体格式"""
        try:
            from ..database.models.cultural_framework_models import CulturalEntityCreate

            return CulturalEntityCreate(
                novel_id=novel_id,
                name=extracted_entity.text,
                entity_type=extracted_entity.entity_type,
                domain_type=extracted_entity.domain,
                dimensions=[],
                description=extracted_entity.context,
                characteristics=extracted_entity.attributes,
                functions=[],
                aliases=[],
                tags=[extracted_entity.entity_type.value],
                references=[extracted_entity.context[:100]]
            )
        except Exception as e:
            logger.warning(f"实体转换失败: {e}")
            return None

    def _convert_cross_domain_relation(self, cross_relation, novel_id: UUID):
        """转换跨域关系格式"""
        try:
            from ..database.models.cultural_framework_models import CulturalRelationCreate, RelationType

            # 映射关系类型
            relation_type_map = {
                "贸易往来": RelationType.RELATED_TO,
                "冲突对立": RelationType.CONFLICTS_WITH,
                "联盟合作": RelationType.RELATED_TO,
                "文化影响": RelationType.INFLUENCED_BY,
                "统治关系": RelationType.CONTROLS
            }

            relation_type = relation_type_map.get(
                cross_relation.relation_type.value,
                RelationType.RELATED_TO
            )

            return CulturalRelationCreate(
                novel_id=novel_id,
                source_entity_id=uuid4(),  # 临时ID
                target_entity_id=uuid4(),  # 临时ID
                relation_type=relation_type,
                description=cross_relation.description,
                strength=cross_relation.strength,
                is_cross_domain=True,
                source_domain=cross_relation.source_domain,
                target_domain=cross_relation.target_domain
            )
        except Exception as e:
            logger.warning(f"跨域关系转换失败: {e}")
            return None

    async def _enhance_batch_data(self, batch_data: CulturalFrameworkBatch, novel_id: UUID) -> CulturalFrameworkBatch:
        """增强批次数据"""
        # 1. 实体描述增强
        for entity in batch_data.entities:
            if len(entity.description) < 50:
                entity.description = self._enhance_entity_description(entity)

        # 2. 关系强度计算
        for relation in batch_data.relations:
            if relation.strength < 0.5:
                relation.strength = self._calculate_enhanced_relation_strength(relation)

        # 3. 概念重要性评估
        for concept in batch_data.concepts:
            concept.importance = self._calculate_concept_importance(concept, batch_data)

        return batch_data

    def _enhance_entity_description(self, entity) -> str:
        """增强实体描述"""
        base_description = entity.description

        # 根据实体类型添加标准描述
        type_descriptions = {
            "ORGANIZATION": "是一个重要的组织机构",
            "CONCEPT": "是九域世界中的核心概念",
            "ITEM": "是具有特殊意义的文化物品",
            "RITUAL": "是传统的仪式活动",
            "SYSTEM": "是重要的制度体系"
        }

        type_desc = type_descriptions.get(entity.entity_type.value, "是文化体系中的重要元素")

        if len(base_description) < 20:
            return f"{entity.name}{type_desc}。{base_description}"

        return base_description

    def _calculate_enhanced_relation_strength(self, relation) -> float:
        """计算增强的关系强度"""
        base_strength = relation.strength

        # 根据关系类型调整
        type_strengths = {
            "包含": 0.8,
            "控制": 0.9,
            "冲突": 0.7,
            "相关": 0.5
        }

        type_strength = type_strengths.get(relation.relation_type.value, 0.5)

        # 结合原始强度和类型强度
        enhanced_strength = (base_strength + type_strength) / 2

        return min(enhanced_strength, 1.0)

    def _calculate_concept_importance(self, concept, batch_data: CulturalFrameworkBatch) -> int:
        """计算概念重要性"""
        base_importance = concept.importance

        # 根据频率调整
        if concept.frequency >= 5:
            base_importance += 2
        elif concept.frequency >= 3:
            base_importance += 1

        # 根据类别调整
        important_categories = ["power_system", "identity_system", "world_structure"]
        if concept.category in important_categories:
            base_importance += 2

        return min(base_importance, 10)

    def _optimize_batch_data(self, batch_data: CulturalFrameworkBatch) -> CulturalFrameworkBatch:
        """优化批次数据"""
        # 1. 去除低质量数据
        filtered_entities = []
        for entity in batch_data.entities:
            if len(entity.name) >= 2 and len(entity.description) >= 10:
                filtered_entities.append(entity)

        batch_data.entities = filtered_entities

        # 2. 优化关系数据
        filtered_relations = []
        for relation in batch_data.relations:
            if relation.strength >= 0.3:
                filtered_relations.append(relation)

        batch_data.relations = filtered_relations

        # 3. 按重要性排序
        batch_data.entities.sort(key=lambda x: len(x.description), reverse=True)
        batch_data.concepts.sort(key=lambda x: x.importance, reverse=True)

        return batch_data

    def _generate_processing_summary(self, batch_data: CulturalFrameworkBatch, processing_time: float) -> Dict[str, Any]:
        """生成处理摘要"""
        # 统计信息
        domain_distribution = {}
        for framework in batch_data.frameworks:
            domain = framework.domain_type.value
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1

        dimension_distribution = {}
        for framework in batch_data.frameworks:
            dimension = framework.dimension.value
            dimension_distribution[dimension] = dimension_distribution.get(dimension, 0) + 1

        entity_type_distribution = {}
        for entity in batch_data.entities:
            entity_type = entity.entity_type.value
            entity_type_distribution[entity_type] = entity_type_distribution.get(entity_type, 0) + 1

        # 质量指标
        avg_entity_description_length = sum(len(e.description) for e in batch_data.entities) / max(len(batch_data.entities), 1)
        cross_domain_relations = sum(1 for r in batch_data.relations if r.is_cross_domain)

        return {
            "processing_time_seconds": processing_time,
            "total_data_count": {
                "frameworks": len(batch_data.frameworks),
                "entities": len(batch_data.entities),
                "relations": len(batch_data.relations),
                "plot_hooks": len(batch_data.plot_hooks),
                "concepts": len(batch_data.concepts)
            },
            "domain_distribution": domain_distribution,
            "dimension_distribution": dimension_distribution,
            "entity_type_distribution": entity_type_distribution,
            "quality_metrics": {
                "domains_covered": len(domain_distribution),
                "dimensions_covered": len(dimension_distribution),
                "avg_entity_description_length": avg_entity_description_length,
                "cross_domain_relations": cross_domain_relations,
                "cross_domain_ratio": cross_domain_relations / max(len(batch_data.relations), 1)
            },
            "recommendations": self._generate_recommendations(batch_data)
        }

    def _generate_recommendations(self, batch_data: CulturalFrameworkBatch) -> List[str]:
        """生成处理建议"""
        recommendations = []

        # 基于数据量的建议
        if len(batch_data.entities) < 10:
            recommendations.append("实体数量较少，建议丰富文本内容以提取更多文化实体")

        if len(batch_data.relations) < 5:
            recommendations.append("关系数据较少，建议在文本中明确描述实体间的关联")

        if len(batch_data.concepts) < 5:
            recommendations.append("概念词典条目较少，建议补充更多专业术语")

        # 基于覆盖率的建议
        domain_count = len(set(f.domain_type for f in batch_data.frameworks))
        if domain_count < 5:
            recommendations.append("域覆盖率较低，建议补充更多域的文化设定")

        dimension_count = len(set(f.dimension for f in batch_data.frameworks))
        if dimension_count < 6:
            recommendations.append("文化维度不完整，建议补充六维文化框架数据")

        # 基于质量的建议
        short_descriptions = sum(1 for e in batch_data.entities if len(e.description) < 30)
        if short_descriptions > len(batch_data.entities) * 0.3:
            recommendations.append("部分实体描述过短，建议丰富实体详细信息")

        if not recommendations:
            recommendations.append("数据质量良好，可考虑进一步细化文化设定细节")

        return recommendations

    async def close(self):
        """关闭资源"""
        if self.db_manager:
            await self.db_manager.close()
        logger.info("处理管道资源已关闭")


async def process_nine_domains_file(file_path: str, novel_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """处理九域文化文件的便捷函数"""
    pipeline = NineDomainsPipeline(config)

    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # 处理文本
        result = await pipeline.process_cultural_text(
            text,
            UUID(novel_id),
            {"source_file": file_path}
        )

        return result

    finally:
        await pipeline.close()


# 命令行接口
if __name__ == "__main__":
    import argparse
    import sys
    import json

    async def main():
        parser = argparse.ArgumentParser(description="处理九域文化框架文本")
        parser.add_argument("--file", required=True, help="文本文件路径")
        parser.add_argument("--novel-id", required=True, help="小说ID")
        parser.add_argument("--config", help="配置文件路径")
        parser.add_argument("--output", help="输出结果文件路径")

        args = parser.parse_args()

        # 加载配置
        config = {}
        if args.config:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)

        try:
            result = await process_nine_domains_file(args.file, args.novel_id, config)

            # 输出结果
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2, default=str)
                print(f"处理结果已保存到: {args.output}")
            else:
                # 打印摘要
                if result.get("success"):
                    summary = result.get("summary", {})
                    print(f"处理成功!")
                    print(f"处理时间: {summary.get('processing_time_seconds', 0):.2f}秒")
                    print(f"提取数据: {summary.get('total_data_count', {})}")
                    print(f"质量指标: {summary.get('quality_metrics', {})}")

                    recommendations = summary.get('recommendations', [])
                    if recommendations:
                        print("\n建议:")
                        for rec in recommendations:
                            print(f"- {rec}")
                else:
                    print(f"处理失败: {result.get('error')}")

        except Exception as e:
            print(f"处理失败: {e}")
            sys.exit(1)

    asyncio.run(main())