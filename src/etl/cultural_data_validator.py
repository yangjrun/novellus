"""
文化数据验证器 - 专门针对九域文化数据的质量检查和清洗
"""

import re
import json
from typing import Dict, List, Tuple, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import logging
from datetime import datetime
from uuid import UUID
import asyncpg

from ..database.models.cultural_framework_models import (
    DomainType, CulturalDimension, EntityType, RelationType,
    CulturalFrameworkCreate, CulturalEntityCreate, CulturalRelationCreate,
    PlotHookCreate, ConceptDictionaryCreate, CulturalFrameworkBatch
)


logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """验证问题严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """验证问题"""
    severity: ValidationSeverity
    category: str
    message: str
    context: Optional[str] = None
    suggestion: Optional[str] = None
    affected_items: Optional[List[str]] = None


@dataclass
class ValidationResult:
    """验证结果"""
    passed: bool
    quality_score: float
    completeness_score: float
    issues: List[ValidationIssue]
    statistics: Dict[str, Any]
    suggestions: List[str]


class CulturalDataValidator:
    """文化数据验证器"""

    def __init__(self):
        # 质量标准配置
        self.quality_standards = {
            "min_framework_content_length": 50,
            "min_entity_description_length": 20,
            "max_entity_name_length": 100,
            "min_entities_per_domain": 3,
            "min_concepts_per_novel": 5,
            "max_duplicate_rate": 0.1,
            "min_relation_strength": 0.3,
            "required_dimensions": 6,
            "required_domains": 3
        }

        # 关键词验证模式
        self.domain_keywords = {
            DomainType.HUMAN_DOMAIN: ["人域", "天命王朝", "链籍", "人类"],
            DomainType.HEAVEN_DOMAIN: ["天域", "天界", "神", "仙"],
            DomainType.WILD_DOMAIN: ["荒域", "野外", "荒野", "原始"],
            DomainType.UNDERWORLD_DOMAIN: ["冥域", "冥界", "死亡", "亡灵"],
            DomainType.DEMON_DOMAIN: ["魔域", "魔界", "恶魔", "邪恶"],
            DomainType.VOID_DOMAIN: ["虚域", "虚空", "虚无", "空间"],
            DomainType.SEA_DOMAIN: ["海域", "海洋", "水", "海"],
            DomainType.SOURCE_DOMAIN: ["源域", "起源", "本源", "根源"]
        }

        self.dimension_keywords = {
            CulturalDimension.MYTHOLOGY_RELIGION: ["神话", "宗教", "信仰", "神", "祭祀", "神明"],
            CulturalDimension.POWER_LAW: ["权力", "法律", "政治", "统治", "法则", "制度"],
            CulturalDimension.ECONOMY_TECHNOLOGY: ["经济", "技术", "货币", "工艺", "贸易", "产业"],
            CulturalDimension.FAMILY_EDUCATION: ["家庭", "教育", "婚姻", "血缘", "传承", "学习"],
            CulturalDimension.RITUAL_DAILY: ["仪式", "日常", "习俗", "节日", "礼仪", "传统"],
            CulturalDimension.ART_ENTERTAINMENT: ["艺术", "娱乐", "美学", "竞技", "表演", "音乐"]
        }

    async def validate_batch_data(self, batch_data: CulturalFrameworkBatch,
                                novel_id: UUID) -> ValidationResult:
        """验证批量数据"""
        issues = []
        statistics = {}

        # 1. 基础数据验证
        basic_issues, basic_stats = self._validate_basic_structure(batch_data)
        issues.extend(basic_issues)
        statistics.update(basic_stats)

        # 2. 内容质量验证
        content_issues, content_stats = self._validate_content_quality(batch_data)
        issues.extend(content_issues)
        statistics.update(content_stats)

        # 3. 数据完整性验证
        completeness_issues, completeness_stats = self._validate_completeness(batch_data)
        issues.extend(completeness_issues)
        statistics.update(completeness_stats)

        # 4. 实体关系验证
        relation_issues, relation_stats = self._validate_relations(batch_data)
        issues.extend(relation_issues)
        statistics.update(relation_stats)

        # 5. 领域特定验证
        domain_issues, domain_stats = self._validate_domain_specific(batch_data)
        issues.extend(domain_issues)
        statistics.update(domain_stats)

        # 6. 一致性验证
        consistency_issues, consistency_stats = self._validate_consistency(batch_data)
        issues.extend(consistency_issues)
        statistics.update(consistency_stats)

        # 计算总体分数
        quality_score = self._calculate_quality_score(issues, statistics)
        completeness_score = self._calculate_completeness_score(batch_data, statistics)

        # 生成改进建议
        suggestions = self._generate_suggestions(issues, statistics)

        # 判断是否通过验证
        critical_errors = [issue for issue in issues if issue.severity == ValidationSeverity.CRITICAL]
        errors = [issue for issue in issues if issue.severity == ValidationSeverity.ERROR]
        passed = len(critical_errors) == 0 and len(errors) <= 3

        return ValidationResult(
            passed=passed,
            quality_score=quality_score,
            completeness_score=completeness_score,
            issues=issues,
            statistics=statistics,
            suggestions=suggestions
        )

    def _validate_basic_structure(self, batch_data: CulturalFrameworkBatch) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """验证基础数据结构"""
        issues = []
        stats = {
            "frameworks_count": len(batch_data.frameworks),
            "entities_count": len(batch_data.entities),
            "relations_count": len(batch_data.relations),
            "plot_hooks_count": len(batch_data.plot_hooks),
            "concepts_count": len(batch_data.concepts)
        }

        # 检查数据是否为空
        if not batch_data.frameworks:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="structure",
                message="没有文化框架数据",
                suggestion="确保文本包含可识别的文化维度内容"
            ))

        if not batch_data.entities:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="structure",
                message="没有提取到文化实体",
                suggestion="检查文本中是否包含组织、概念、物品等实体"
            ))

        if len(batch_data.entities) < self.quality_standards["min_entities_per_domain"]:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="structure",
                message=f"实体数量偏少，当前: {len(batch_data.entities)}",
                suggestion=f"建议每个域至少包含{self.quality_standards['min_entities_per_domain']}个实体"
            ))

        # 检查数据类型正确性
        for i, framework in enumerate(batch_data.frameworks):
            if not framework.title or len(framework.title.strip()) == 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="structure",
                    message=f"文化框架 {i+1} 标题为空",
                    context=f"域: {framework.domain_type.value}, 维度: {framework.dimension.value}"
                ))

            if len(framework.detailed_content) < self.quality_standards["min_framework_content_length"]:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="structure",
                    message=f"文化框架 {i+1} 内容过短",
                    context=f"当前长度: {len(framework.detailed_content)}",
                    suggestion=f"建议内容长度至少{self.quality_standards['min_framework_content_length']}字符"
                ))

        # 检查实体名称合理性
        for i, entity in enumerate(batch_data.entities):
            if len(entity.name) > self.quality_standards["max_entity_name_length"]:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="structure",
                    message=f"实体名称过长: {entity.name[:50]}...",
                    suggestion="实体名称应简洁明确"
                ))

            if len(entity.description) < self.quality_standards["min_entity_description_length"]:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="structure",
                    message=f"实体描述过短: {entity.name}",
                    context=f"当前长度: {len(entity.description)}",
                    suggestion=f"建议描述长度至少{self.quality_standards['min_entity_description_length']}字符"
                ))

        return issues, stats

    def _validate_content_quality(self, batch_data: CulturalFrameworkBatch) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """验证内容质量"""
        issues = []
        stats = {}

        # 检查重复内容
        framework_titles = [f.title for f in batch_data.frameworks]
        duplicate_titles = self._find_duplicates(framework_titles)
        if duplicate_titles:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="quality",
                message="发现重复的框架标题",
                affected_items=duplicate_titles,
                suggestion="确保每个文化框架都有独特的标题"
            ))

        entity_names = [e.name for e in batch_data.entities]
        duplicate_entities = self._find_duplicates(entity_names)
        if duplicate_entities:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="quality",
                message="发现重复的实体名称",
                affected_items=duplicate_entities,
                suggestion="确保实体名称唯一或添加域前缀区分"
            ))

        stats["duplicate_rate"] = (len(duplicate_titles) + len(duplicate_entities)) / max(len(framework_titles) + len(entity_names), 1)

        # 检查内容一致性
        domain_entity_map = {}
        for entity in batch_data.entities:
            if entity.domain_type:
                domain = entity.domain_type.value
                if domain not in domain_entity_map:
                    domain_entity_map[domain] = []
                domain_entity_map[domain].append(entity.name)

        stats["entities_per_domain"] = {domain: len(entities) for domain, entities in domain_entity_map.items()}

        # 检查关键词匹配
        for framework in batch_data.frameworks:
            domain_keywords = self.domain_keywords.get(framework.domain_type, [])
            dimension_keywords = self.dimension_keywords.get(framework.dimension, [])

            if not any(keyword in framework.detailed_content for keyword in domain_keywords):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="quality",
                    message=f"文化框架可能与域不匹配: {framework.domain_type.value}",
                    context=f"标题: {framework.title}",
                    suggestion=f"确保内容包含相关关键词: {', '.join(domain_keywords[:3])}"
                ))

            if not any(keyword in framework.detailed_content for keyword in dimension_keywords):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="quality",
                    message=f"文化框架可能与维度不匹配: {framework.dimension.value}",
                    context=f"标题: {framework.title}",
                    suggestion=f"确保内容包含相关关键词: {', '.join(dimension_keywords[:3])}"
                ))

        return issues, stats

    def _validate_completeness(self, batch_data: CulturalFrameworkBatch) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """验证数据完整性"""
        issues = []
        stats = {}

        # 检查域覆盖率
        covered_domains = set(f.domain_type for f in batch_data.frameworks)
        all_domains = set(DomainType)
        missing_domains = all_domains - covered_domains

        stats["domain_coverage"] = len(covered_domains) / len(all_domains)
        stats["covered_domains"] = [d.value for d in covered_domains]
        stats["missing_domains"] = [d.value for d in missing_domains]

        if len(missing_domains) > 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="completeness",
                message=f"缺少以下域的数据: {', '.join(d.value for d in missing_domains)}",
                suggestion="考虑添加缺失域的文化框架数据"
            ))

        # 检查维度覆盖率
        covered_dimensions = set(f.dimension for f in batch_data.frameworks)
        all_dimensions = set(CulturalDimension)
        missing_dimensions = all_dimensions - covered_dimensions

        stats["dimension_coverage"] = len(covered_dimensions) / len(all_dimensions)
        stats["covered_dimensions"] = [d.value for d in covered_dimensions]
        stats["missing_dimensions"] = [d.value for d in missing_dimensions]

        if len(missing_dimensions) > 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="completeness",
                message=f"缺少以下维度的数据: {', '.join(d.value for d in missing_dimensions)}",
                suggestion="确保六维文化框架数据完整"
            ))

        # 检查每个域的维度完整性
        domain_dimension_matrix = {}
        for framework in batch_data.frameworks:
            domain = framework.domain_type.value
            dimension = framework.dimension.value
            if domain not in domain_dimension_matrix:
                domain_dimension_matrix[domain] = set()
            domain_dimension_matrix[domain].add(dimension)

        for domain, dimensions in domain_dimension_matrix.items():
            missing_dims = all_dimensions - set(CulturalDimension(d) for d in dimensions)
            if missing_dims:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="completeness",
                    message=f"{domain}缺少维度: {', '.join(d.value for d in missing_dims)}",
                    suggestion=f"为{domain}补充完整的六维文化数据"
                ))

        stats["domain_dimension_matrix"] = {k: list(v) for k, v in domain_dimension_matrix.items()}

        # 检查概念词典完整性
        if len(batch_data.concepts) < self.quality_standards["min_concepts_per_novel"]:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="completeness",
                message=f"概念词典条目较少: {len(batch_data.concepts)}",
                suggestion=f"建议至少包含{self.quality_standards['min_concepts_per_novel']}个重要概念"
            ))

        return issues, stats

    def _validate_relations(self, batch_data: CulturalFrameworkBatch) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """验证实体关系"""
        issues = []
        stats = {}

        if not batch_data.relations:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="relations",
                message="没有发现实体关系",
                suggestion="分析实体间的关联关系有助于构建完整的文化网络"
            ))
            return issues, stats

        # 检查关系强度
        weak_relations = [r for r in batch_data.relations if r.strength < self.quality_standards["min_relation_strength"]]
        if weak_relations:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="relations",
                message=f"发现{len(weak_relations)}个弱关系",
                suggestion="考虑补充关系描述或提高关系强度"
            ))

        # 检查跨域关系
        cross_domain_relations = [r for r in batch_data.relations if r.is_cross_domain]
        stats["cross_domain_relations"] = len(cross_domain_relations)
        stats["total_relations"] = len(batch_data.relations)
        stats["cross_domain_ratio"] = len(cross_domain_relations) / len(batch_data.relations) if batch_data.relations else 0

        if stats["cross_domain_ratio"] > 0.5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="relations",
                message="跨域关系比例较高",
                context=f"跨域关系: {len(cross_domain_relations)}/{len(batch_data.relations)}",
                suggestion="这可能表明各域联系紧密，有助于故事发展"
            ))

        # 检查孤立实体
        entity_names = set(e.name for e in batch_data.entities)
        related_entities = set()
        for relation in batch_data.relations:
            # 注意：这里需要根据实际的实体ID匹配逻辑调整
            pass

        return issues, stats

    def _validate_domain_specific(self, batch_data: CulturalFrameworkBatch) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """验证领域特定规则"""
        issues = []
        stats = {}

        # 检查实体类型分布
        entity_type_counts = {}
        for entity in batch_data.entities:
            entity_type = entity.entity_type.value
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1

        stats["entity_type_distribution"] = entity_type_counts

        # 检查是否缺少重要实体类型
        required_types = ["组织机构", "重要概念", "文化物品"]
        missing_types = [t for t in required_types if t not in entity_type_counts]

        if missing_types:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="domain_specific",
                message=f"缺少重要实体类型: {', '.join(missing_types)}",
                suggestion="确保包含核心的文化实体类型"
            ))

        # 检查裂世九域特定概念
        key_concepts = ["法则链", "链籍", "断链术", "环印", "裂世夜"]
        found_concepts = [concept.term for concept in batch_data.concepts if concept.term in key_concepts]
        missing_concepts = [c for c in key_concepts if c not in found_concepts]

        if missing_concepts:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="domain_specific",
                message=f"缺少关键概念: {', '.join(missing_concepts)}",
                suggestion="考虑添加裂世九域的核心概念"
            ))

        stats["key_concepts_found"] = found_concepts
        stats["key_concepts_missing"] = missing_concepts

        return issues, stats

    def _validate_consistency(self, batch_data: CulturalFrameworkBatch) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """验证数据一致性"""
        issues = []
        stats = {}

        # 检查命名一致性
        entity_name_patterns = {}
        for entity in batch_data.entities:
            # 提取命名模式（如后缀）
            if "王朝" in entity.name:
                entity_name_patterns.setdefault("王朝", []).append(entity.name)
            elif "殿" in entity.name:
                entity_name_patterns.setdefault("殿", []).append(entity.name)
            elif "会" in entity.name:
                entity_name_patterns.setdefault("会", []).append(entity.name)

        stats["naming_patterns"] = entity_name_patterns

        # 检查域归属一致性
        domain_consistency_issues = []
        for entity in batch_data.entities:
            if entity.domain_type:
                expected_keywords = self.domain_keywords.get(entity.domain_type, [])
                if not any(keyword in entity.description for keyword in expected_keywords):
                    domain_consistency_issues.append(entity.name)

        if domain_consistency_issues:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="consistency",
                message=f"以下实体的域归属可能不准确: {', '.join(domain_consistency_issues[:5])}",
                suggestion="检查实体描述与所属域的匹配度"
            ))

        # 检查优先级分布合理性
        priority_distribution = {}
        for framework in batch_data.frameworks:
            priority = framework.priority
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1

        stats["priority_distribution"] = priority_distribution

        if all(p == 5 for p in priority_distribution.keys()):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="consistency",
                message="所有框架优先级相同",
                suggestion="考虑根据重要性调整不同框架的优先级"
            ))

        return issues, stats

    def _find_duplicates(self, items: List[str]) -> List[str]:
        """查找重复项"""
        seen = set()
        duplicates = set()
        for item in items:
            if item in seen:
                duplicates.add(item)
            seen.add(item)
        return list(duplicates)

    def _calculate_quality_score(self, issues: List[ValidationIssue], statistics: Dict[str, Any]) -> float:
        """计算质量分数"""
        base_score = 1.0

        # 根据问题严重程度扣分
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 0.3
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.15
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.05

        # 根据数据量调整
        entity_count = statistics.get("entities_count", 0)
        if entity_count >= 20:
            base_score += 0.1
        elif entity_count < 5:
            base_score -= 0.1

        # 根据重复率调整
        duplicate_rate = statistics.get("duplicate_rate", 0)
        if duplicate_rate > self.quality_standards["max_duplicate_rate"]:
            base_score -= duplicate_rate * 0.2

        return max(0.0, min(1.0, base_score))

    def _calculate_completeness_score(self, batch_data: CulturalFrameworkBatch, statistics: Dict[str, Any]) -> float:
        """计算完整性分数"""
        domain_coverage = statistics.get("domain_coverage", 0)
        dimension_coverage = statistics.get("dimension_coverage", 0)

        # 基础完整性分数
        base_score = (domain_coverage + dimension_coverage) / 2

        # 根据数据丰富度调整
        entity_bonus = min(0.2, len(batch_data.entities) / 50)
        concept_bonus = min(0.1, len(batch_data.concepts) / 20)
        relation_bonus = min(0.1, len(batch_data.relations) / 30)

        total_score = base_score + entity_bonus + concept_bonus + relation_bonus

        return min(1.0, total_score)

    def _generate_suggestions(self, issues: List[ValidationIssue], statistics: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 根据问题生成建议
        error_count = len([i for i in issues if i.severity == ValidationSeverity.ERROR])
        warning_count = len([i for i in issues if i.severity == ValidationSeverity.WARNING])

        if error_count > 0:
            suggestions.append("优先解决错误级别的问题，确保数据质量")

        if warning_count > 5:
            suggestions.append("存在较多警告，建议逐步完善数据内容")

        # 基于统计数据生成建议
        domain_coverage = statistics.get("domain_coverage", 0)
        if domain_coverage < 0.5:
            suggestions.append("当前域覆盖率较低，建议补充更多域的文化数据")

        entity_count = statistics.get("entities_count", 0)
        if entity_count < 10:
            suggestions.append("实体数量偏少，建议丰富文化实体内容")

        if statistics.get("concepts_count", 0) < 5:
            suggestions.append("概念词典条目较少，建议添加更多核心概念")

        # 特定改进建议
        if not suggestions:
            suggestions.append("数据质量良好，可考虑进一步丰富细节描述")

        return suggestions[:5]  # 限制建议数量


async def validate_database_cultural_data(novel_id: str, pg_pool: asyncpg.Pool, mongo_db) -> ValidationResult:
    """验证数据库中的文化数据"""
    validator = CulturalDataValidator()

    try:
        # 从数据库加载数据
        async with pg_pool.acquire() as conn:
            # 查询文化框架
            frameworks_rows = await conn.fetch("""
                SELECT domain_type, dimension, title, summary, key_elements,
                       detailed_content, tags, priority
                FROM cultural_frameworks
                WHERE novel_id = $1
            """, novel_id)

            # 查询文化实体
            entities_rows = await conn.fetch("""
                SELECT name, entity_type, domain_type, dimensions, description,
                       characteristics, functions, significance, aliases, tags
                FROM cultural_entities
                WHERE novel_id = $1
            """, novel_id)

            # 查询概念词典
            concepts_rows = await conn.fetch("""
                SELECT term, definition, category, domain_type, frequency, importance
                FROM concept_dictionary
                WHERE novel_id = $1
            """, novel_id)

        # 构建验证用的批量数据
        from ..database.models.cultural_framework_models import (
            CulturalFrameworkBatch, CulturalFrameworkCreate,
            CulturalEntityCreate, ConceptDictionaryCreate
        )

        batch_data = CulturalFrameworkBatch()

        # 转换框架数据
        for row in frameworks_rows:
            framework = CulturalFrameworkCreate(
                novel_id=UUID(novel_id),
                domain_type=DomainType(row['domain_type']),
                dimension=CulturalDimension(row['dimension']),
                title=row['title'],
                summary=row['summary'],
                key_elements=row['key_elements'] or [],
                detailed_content=row['detailed_content'],
                tags=row['tags'] or [],
                priority=row['priority']
            )
            batch_data.frameworks.append(framework)

        # 转换实体数据
        for row in entities_rows:
            entity = CulturalEntityCreate(
                novel_id=UUID(novel_id),
                name=row['name'],
                entity_type=EntityType(row['entity_type']),
                domain_type=DomainType(row['domain_type']) if row['domain_type'] else None,
                dimensions=[CulturalDimension(d) for d in (row['dimensions'] or [])],
                description=row['description'],
                characteristics=json.loads(row['characteristics']) if row['characteristics'] else {},
                functions=row['functions'] or [],
                significance=row['significance'],
                aliases=row['aliases'] or [],
                tags=row['tags'] or []
            )
            batch_data.entities.append(entity)

        # 转换概念数据
        for row in concepts_rows:
            concept = ConceptDictionaryCreate(
                novel_id=UUID(novel_id),
                term=row['term'],
                definition=row['definition'],
                category=row['category'],
                domain_type=DomainType(row['domain_type']) if row['domain_type'] else None,
                frequency=row['frequency'],
                importance=row['importance']
            )
            batch_data.concepts.append(concept)

        # 执行验证
        result = await validator.validate_batch_data(batch_data, UUID(novel_id))
        return result

    except Exception as e:
        logger.error(f"数据库验证失败: {e}")
        raise


# 命令行接口
if __name__ == "__main__":
    import argparse
    import asyncio
    from ..config import config

    async def main():
        parser = argparse.ArgumentParser(description="验证文化框架数据质量")
        parser.add_argument("--novel-id", required=True, help="小说ID")
        args = parser.parse_args()

        # 连接数据库
        pg_pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )

        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        mongo_db = mongo_client[config.mongodb_db]

        try:
            result = await validate_database_cultural_data(args.novel_id, pg_pool, mongo_db)

            print(f"验证结果: {'通过' if result.passed else '未通过'}")
            print(f"质量分数: {result.quality_score:.2f}")
            print(f"完整性分数: {result.completeness_score:.2f}")
            print(f"问题数量: {len(result.issues)}")

            print("\n问题详情:")
            for issue in result.issues:
                print(f"[{issue.severity.upper()}] {issue.category}: {issue.message}")
                if issue.suggestion:
                    print(f"  建议: {issue.suggestion}")

            print("\n改进建议:")
            for suggestion in result.suggestions:
                print(f"- {suggestion}")

        finally:
            await pg_pool.close()
            mongo_client.close()

    asyncio.run(main())