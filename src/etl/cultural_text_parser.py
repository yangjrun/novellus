"""
文化框架文本解析器 - 解析六维文化数据和实体提取
"""

import re
import json
from typing import Dict, List, Optional, Set, Tuple, Any
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum

from ..database.models.cultural_framework_models import (
    DomainType, CulturalDimension, EntityType, RelationType,
    CulturalFrameworkCreate, CulturalEntityCreate, CulturalRelationCreate,
    PlotHookCreate, ConceptDictionaryCreate, CulturalFrameworkBatch
)


class ParsedSection:
    """解析的文本段落"""
    def __init__(self, title: str, content: str, dimension: Optional[CulturalDimension] = None):
        self.title = title.strip()
        self.content = content.strip()
        self.dimension = dimension
        self.entities: List[str] = []
        self.key_elements: List[str] = []


@dataclass
class EntityCandidate:
    """实体候选"""
    name: str
    entity_type: EntityType
    context: str
    confidence: float
    characteristics: Dict[str, Any]
    domain: Optional[DomainType] = None


class CulturalTextParser:
    """文化框架文本解析器"""

    def __init__(self):
        self.domain_markers = {
            "人域": DomainType.HUMAN_DOMAIN,
            "天域": DomainType.HEAVEN_DOMAIN,
            "荒域": DomainType.WILD_DOMAIN,
            "冥域": DomainType.UNDERWORLD_DOMAIN,
            "魔域": DomainType.DEMON_DOMAIN,
            "虚域": DomainType.VOID_DOMAIN,
            "海域": DomainType.SEA_DOMAIN,
            "源域": DomainType.SOURCE_DOMAIN,
        }

        self.dimension_markers = {
            "A": CulturalDimension.MYTHOLOGY_RELIGION,
            "B": CulturalDimension.POWER_LAW,
            "C": CulturalDimension.ECONOMY_TECHNOLOGY,
            "D": CulturalDimension.FAMILY_EDUCATION,
            "E": CulturalDimension.RITUAL_DAILY,
            "F": CulturalDimension.ART_ENTERTAINMENT,
        }

        # 预定义实体模式
        self.entity_patterns = {
            EntityType.ORGANIZATION: [
                r'([^，。！？\s]{2,8}(?:王朝|议会|殿|会|宗|门|派|府|司|院|堂|社|团|联盟|组织))',
                r'(天命王朝|祭司议会|冥司殿|守源会|法则宗门)',
            ],
            EntityType.CONCEPT: [
                r'([^，。！？\s]{2,8}(?:法则|链|术|功|诀|道|理|法|式|制))',
                r'(链籍|法则链|断链术|环印|三等制|师承制|血契制)',
            ],
            EntityType.ITEM: [
                r'([^，。！？\s]{2,8}(?:票|器|盘|珠|石|符|印|镜|册|书|卷))',
                r'(链票|镇魂器|稳乱器|回响盘|环印|链籍)',
            ],
            EntityType.RITUAL: [
                r'([^，。！？\s]{2,8}(?:礼|节|夜|月|典|仪|祭|庆|会))',
                r'(裂世夜|归环礼|狂环月|拾链礼|链诞节|断链仪)',
            ],
            EntityType.CURRENCY: [
                r'([^，。！？\s]{2,8}(?:币|钱|金|银|铜|晶|石|珠))',
                r'(环币|链金|法则晶|灵石)',
            ],
            EntityType.TECHNOLOGY: [
                r'([^，。！？\s]{2,8}(?:技|工艺|法|术|学|道))',
                r'(锻链术|环铸法|法则工艺|链接技术)',
            ],
        }

        # 关系识别模式
        self.relation_patterns = {
            RelationType.CONTROLS: [r'(\w+)(?:控制|统治|管理|掌管)(\w+)', r'(\w+)(?:的|之)(?:统治者|管理者|控制者)(?:是|为)(\w+)'],
            RelationType.CONTAINS: [r'(\w+)(?:包含|含有|拥有)(\w+)', r'(\w+)(?:属于|隶属于)(\w+)'],
            RelationType.CONFLICTS_WITH: [r'(\w+)(?:与|和)(\w+)(?:冲突|对立|敌对)', r'(\w+)(?:反对|抵制)(\w+)'],
            RelationType.DERIVED_FROM: [r'(\w+)(?:来源于|源自|衍生自)(\w+)', r'(\w+)(?:的|之)(?:起源|来源)(?:是|为)(\w+)'],
            RelationType.INFLUENCED_BY: [r'(\w+)(?:受到|受)(\w+)(?:影响|感化)', r'(\w+)(?:影响|感化)(?:了)?(\w+)'],
            RelationType.RELATED_TO: [r'(\w+)(?:与|和)(\w+)(?:相关|关联|联系)', r'(\w+)(?:关联|联系|相关)(\w+)'],
        }

    def parse_cultural_text(self, text: str, novel_id: UUID) -> CulturalFrameworkBatch:
        """解析文化框架文本"""
        # 1. 按域分割文本
        domain_sections = self._split_by_domains(text)

        batch = CulturalFrameworkBatch()

        for domain_name, domain_text in domain_sections.items():
            domain_type = self.domain_markers.get(domain_name)
            if not domain_type:
                continue

            # 2. 按维度分割每个域的内容
            dimension_sections = self._split_by_dimensions(domain_text)

            # 3. 解析每个维度的内容
            for dimension_key, section_text in dimension_sections.items():
                dimension = self.dimension_markers.get(dimension_key)
                if not dimension:
                    continue

                # 创建文化框架条目
                framework = self._parse_framework_section(
                    section_text, novel_id, domain_type, dimension
                )
                batch.frameworks.append(framework)

                # 提取实体
                entities = self._extract_entities(section_text, novel_id, domain_type, [dimension])
                batch.entities.extend(entities)

            # 4. 提取剧情钩子
            plot_hooks = self._extract_plot_hooks(domain_text, novel_id, domain_type)
            batch.plot_hooks.extend(plot_hooks)

        # 5. 提取概念词典
        concepts = self._extract_concepts(text, novel_id)
        batch.concepts.extend(concepts)

        # 6. 分析实体关系
        relations = self._extract_relations(batch.entities, novel_id)
        batch.relations.extend(relations)

        return batch

    def _split_by_domains(self, text: str) -> Dict[str, str]:
        """按域分割文本"""
        domain_sections = {}
        current_domain = None
        current_content = []

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是域标题
            domain_match = None
            for domain_name in self.domain_markers.keys():
                if domain_name in line and ('域' in line or '##' in line or line.startswith(domain_name)):
                    domain_match = domain_name
                    break

            if domain_match:
                # 保存上一个域的内容
                if current_domain and current_content:
                    domain_sections[current_domain] = '\n'.join(current_content)

                # 开始新域
                current_domain = domain_match
                current_content = []
            elif current_domain:
                current_content.append(line)

        # 保存最后一个域
        if current_domain and current_content:
            domain_sections[current_domain] = '\n'.join(current_content)

        return domain_sections

    def _split_by_dimensions(self, domain_text: str) -> Dict[str, str]:
        """按维度分割域文本"""
        dimension_sections = {}
        current_dimension = None
        current_content = []

        lines = domain_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查维度标识
            dimension_match = re.search(r'^([A-F])[\.、\s]*(.+)', line)
            if dimension_match:
                # 保存上一个维度的内容
                if current_dimension and current_content:
                    dimension_sections[current_dimension] = '\n'.join(current_content)

                # 开始新维度
                current_dimension = dimension_match.group(1)
                current_content = [dimension_match.group(2)]
            elif current_dimension:
                current_content.append(line)

        # 保存最后一个维度
        if current_dimension and current_content:
            dimension_sections[current_dimension] = '\n'.join(current_content)

        return dimension_sections

    def _parse_framework_section(self, text: str, novel_id: UUID, domain_type: DomainType, dimension: CulturalDimension) -> CulturalFrameworkCreate:
        """解析文化框架段落"""
        lines = text.split('\n')
        title = lines[0] if lines else f"{domain_type.value} - {dimension.value}"

        # 提取关键要素
        key_elements = []
        for line in lines[1:]:
            if '：' in line or '。' in line:
                # 提取冒号前的关键词
                parts = re.split(r'[：。]', line)
                if parts[0].strip():
                    key_elements.append(parts[0].strip())

        # 生成摘要
        summary = self._generate_summary(text, max_length=200)

        # 提取标签
        tags = self._extract_tags(text)

        return CulturalFrameworkCreate(
            novel_id=novel_id,
            domain_type=domain_type,
            dimension=dimension,
            title=title,
            summary=summary,
            key_elements=key_elements[:10],  # 限制数量
            detailed_content=text,
            tags=tags,
            priority=self._calculate_priority(text)
        )

    def _extract_entities(self, text: str, novel_id: UUID, domain_type: DomainType, dimensions: List[CulturalDimension]) -> List[CulturalEntityCreate]:
        """提取文化实体"""
        entities = []
        found_entities = set()  # 避免重复

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)

                for match in matches:
                    entity_name = match if isinstance(match, str) else match[0]
                    entity_name = entity_name.strip()

                    if len(entity_name) < 2 or entity_name in found_entities:
                        continue

                    found_entities.add(entity_name)

                    # 提取上下文
                    context = self._extract_context(text, entity_name)

                    # 提取特征
                    characteristics = self._extract_characteristics(context, entity_type)

                    # 提取功能
                    functions = self._extract_functions(context, entity_type)

                    # 提取别名
                    aliases = self._extract_aliases(context, entity_name)

                    entity = CulturalEntityCreate(
                        novel_id=novel_id,
                        name=entity_name,
                        entity_type=entity_type,
                        domain_type=domain_type,
                        dimensions=dimensions,
                        description=context,
                        characteristics=characteristics,
                        functions=functions,
                        aliases=aliases,
                        tags=[domain_type.value, entity_type.value],
                        references=[self._extract_reference_snippet(text, entity_name)]
                    )
                    entities.append(entity)

        return entities

    def _extract_plot_hooks(self, text: str, novel_id: UUID, domain_type: DomainType) -> List[PlotHookCreate]:
        """提取剧情钩子"""
        hooks = []

        # 寻找剧情钩子标识
        hook_patterns = [
            r'【剧情钩子】(.+?)(?=【|$)',
            r'剧情事件：(.+?)(?=\n\n|\n[A-Z]|$)',
            r'事件钩子：(.+?)(?=\n\n|\n[A-Z]|$)',
        ]

        for pattern in hook_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

            for match in matches:
                hook_text = match.strip()
                if len(hook_text) < 10:
                    continue

                # 解析钩子内容
                lines = hook_text.split('\n')
                title = lines[0][:100] if lines else "未命名剧情钩子"

                # 提取触发条件
                trigger_conditions = self._extract_trigger_conditions(hook_text)

                # 提取可能结果
                potential_outcomes = self._extract_potential_outcomes(hook_text)

                # 识别相关文化维度
                cultural_dimensions = self._identify_dimensions_in_text(hook_text)

                hook = PlotHookCreate(
                    novel_id=novel_id,
                    domain_type=domain_type,
                    title=title,
                    description=hook_text,
                    trigger_conditions=trigger_conditions,
                    potential_outcomes=potential_outcomes,
                    cultural_dimensions=cultural_dimensions,
                    complexity_level=self._calculate_complexity(hook_text),
                    story_impact=self._calculate_story_impact(hook_text),
                    tags=[domain_type.value, "剧情钩子"]
                )
                hooks.append(hook)

        return hooks

    def _extract_concepts(self, text: str, novel_id: UUID) -> List[ConceptDictionaryCreate]:
        """提取概念词典"""
        concepts = []

        # 预定义重要概念
        important_concepts = {
            "链籍": "identity_system",
            "法则链": "power_system",
            "断链术": "technology",
            "环印": "item",
            "链票": "currency",
            "镇魂器": "item",
            "稳乱器": "item",
            "回响盘": "item",
            "裂世夜": "ritual",
            "归环礼": "ritual",
            "狂环月": "ritual",
            "拾链礼": "ritual",
            "三等制": "social_system",
            "师承制": "education_system",
            "血契制": "social_system",
        }

        for term, category in important_concepts.items():
            if term in text:
                # 提取定义
                definition = self._extract_definition(text, term)

                # 提取使用示例
                usage_examples = self._extract_usage_examples(text, term)

                # 确定所属域
                domain_type = self._identify_term_domain(text, term)

                concept = ConceptDictionaryCreate(
                    novel_id=novel_id,
                    term=term,
                    definition=definition,
                    category=category,
                    domain_type=domain_type,
                    usage_examples=usage_examples,
                    frequency=text.count(term),
                    importance=self._calculate_term_importance(text, term)
                )
                concepts.append(concept)

        return concepts

    def _extract_relations(self, entities: List[CulturalEntityCreate], novel_id: UUID) -> List[CulturalRelationCreate]:
        """提取实体关系"""
        relations = []

        # 建立实体名称到ID的映射
        entity_map = {entity.name: uuid4() for entity in entities}

        for i, source_entity in enumerate(entities):
            for j, target_entity in enumerate(entities):
                if i >= j:  # 避免重复和自关联
                    continue

                # 在描述中寻找关系
                relation_type, strength = self._find_relation_in_text(
                    source_entity.description + " " + target_entity.description,
                    source_entity.name,
                    target_entity.name
                )

                if relation_type:
                    # 检查是否为跨域关系
                    is_cross_domain = (source_entity.domain_type != target_entity.domain_type
                                     and source_entity.domain_type and target_entity.domain_type)

                    relation = CulturalRelationCreate(
                        novel_id=novel_id,
                        source_entity_id=entity_map[source_entity.name],
                        target_entity_id=entity_map[target_entity.name],
                        relation_type=relation_type,
                        strength=strength,
                        is_cross_domain=is_cross_domain,
                        source_domain=source_entity.domain_type,
                        target_domain=target_entity.domain_type
                    )
                    relations.append(relation)

        return relations

    # 辅助方法
    def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成摘要"""
        sentences = re.split(r'[。！？]', text)
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        return summary.strip()

    def _extract_tags(self, text: str) -> List[str]:
        """提取标签"""
        tags = []

        # 基于关键词提取标签
        keyword_tags = {
            "政治": ["政治", "权力", "统治", "管理"],
            "经济": ["经济", "货币", "贸易", "商业"],
            "宗教": ["信仰", "神", "祭祀", "宗教"],
            "技术": ["技术", "工艺", "法术", "技能"],
            "社会": ["社会", "制度", "阶层", "身份"],
            "文化": ["文化", "传统", "习俗", "艺术"],
        }

        for tag, keywords in keyword_tags.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags

    def _calculate_priority(self, text: str) -> int:
        """计算优先级"""
        priority = 5  # 默认值

        # 基于长度调整
        if len(text) > 1000:
            priority += 1
        if len(text) > 2000:
            priority += 1

        # 基于关键词调整
        important_keywords = ["重要", "核心", "关键", "主要", "根本"]
        for keyword in important_keywords:
            if keyword in text:
                priority += 1
                break

        return min(priority, 10)

    def _extract_context(self, text: str, entity_name: str, window: int = 100) -> str:
        """提取实体上下文"""
        index = text.find(entity_name)
        if index == -1:
            return ""

        start = max(0, index - window)
        end = min(len(text), index + len(entity_name) + window)

        return text[start:end].strip()

    def _extract_characteristics(self, context: str, entity_type: EntityType) -> Dict[str, Any]:
        """提取实体特征"""
        characteristics = {}

        # 基于实体类型提取不同特征
        if entity_type == EntityType.ORGANIZATION:
            characteristics["type"] = "组织"
            if "王朝" in context:
                characteristics["governance_type"] = "王朝制"
            if "议会" in context:
                characteristics["governance_type"] = "议会制"

        elif entity_type == EntityType.ITEM:
            characteristics["type"] = "物品"
            if "器" in context:
                characteristics["item_category"] = "器具"
            if "票" in context:
                characteristics["item_category"] = "票据"

        return characteristics

    def _extract_functions(self, context: str, entity_type: EntityType) -> List[str]:
        """提取实体功能"""
        functions = []

        # 寻找功能描述模式
        function_patterns = [
            r'(?:用于|用来|可以|能够|负责)([^，。！？\n]+)',
            r'(?:作用是|功能是|目的是)([^，。！？\n]+)',
        ]

        for pattern in function_patterns:
            matches = re.findall(pattern, context)
            functions.extend([match.strip() for match in matches])

        return functions[:5]  # 限制数量

    def _extract_aliases(self, context: str, entity_name: str) -> List[str]:
        """提取别名"""
        aliases = []

        # 寻找别名模式
        alias_patterns = [
            fr'{entity_name}(?:又称|也称|别名|简称)([^，。！？\n]+)',
            fr'([^，。！？\n]+)(?:又称|也称|即|也就是){entity_name}',
        ]

        for pattern in alias_patterns:
            matches = re.findall(pattern, context)
            aliases.extend([match.strip() for match in matches])

        return aliases

    def _extract_reference_snippet(self, text: str, entity_name: str, length: int = 50) -> str:
        """提取引用片段"""
        context = self._extract_context(text, entity_name, length)
        return context[:length] + "..." if len(context) > length else context

    def _extract_trigger_conditions(self, text: str) -> List[str]:
        """提取触发条件"""
        conditions = []

        condition_patterns = [
            r'(?:当|如果|若|假如)([^，。！？\n]+)',
            r'触发条件[：:]([^，。！？\n]+)',
            r'条件[：:]([^，。！？\n]+)',
        ]

        for pattern in condition_patterns:
            matches = re.findall(pattern, text)
            conditions.extend([match.strip() for match in matches])

        return conditions

    def _extract_potential_outcomes(self, text: str) -> List[str]:
        """提取可能结果"""
        outcomes = []

        outcome_patterns = [
            r'(?:将会|可能|或许|结果)([^，。！？\n]+)',
            r'可能结果[：:]([^，。！？\n]+)',
            r'结果[：:]([^，。！？\n]+)',
        ]

        for pattern in outcome_patterns:
            matches = re.findall(pattern, text)
            outcomes.extend([match.strip() for match in matches])

        return outcomes

    def _identify_dimensions_in_text(self, text: str) -> List[CulturalDimension]:
        """识别文本中的文化维度"""
        dimensions = []

        dimension_keywords = {
            CulturalDimension.MYTHOLOGY_RELIGION: ["神", "信仰", "宗教", "祭祀", "神话"],
            CulturalDimension.POWER_LAW: ["权力", "法律", "政治", "统治", "法则"],
            CulturalDimension.ECONOMY_TECHNOLOGY: ["经济", "技术", "货币", "工艺", "贸易"],
            CulturalDimension.FAMILY_EDUCATION: ["家庭", "教育", "婚姻", "血缘", "传承"],
            CulturalDimension.RITUAL_DAILY: ["仪式", "日常", "习俗", "节日", "礼仪"],
            CulturalDimension.ART_ENTERTAINMENT: ["艺术", "娱乐", "美学", "竞技", "表演"],
        }

        for dimension, keywords in dimension_keywords.items():
            if any(keyword in text for keyword in keywords):
                dimensions.append(dimension)

        return dimensions

    def _calculate_complexity(self, text: str) -> int:
        """计算复杂度"""
        complexity = 5

        # 基于长度
        if len(text) > 500:
            complexity += 1
        if len(text) > 1000:
            complexity += 1

        # 基于实体数量
        entity_count = len(re.findall(r'[，。]', text))
        if entity_count > 10:
            complexity += 1

        return min(complexity, 10)

    def _calculate_story_impact(self, text: str) -> int:
        """计算故事影响力"""
        impact = 5

        impact_keywords = ["重大", "关键", "决定性", "影响", "改变"]
        for keyword in impact_keywords:
            if keyword in text:
                impact += 1

        return min(impact, 10)

    def _extract_definition(self, text: str, term: str) -> str:
        """提取术语定义"""
        # 寻找定义模式
        definition_patterns = [
            fr'{term}[：:]([^，。！？\n]+)',
            fr'{term}(?:是|指|表示)([^，。！？\n]+)',
            fr'所谓{term}[，：]([^，。！？\n]+)',
        ]

        for pattern in definition_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # 如果没有找到明确定义，返回上下文
        context = self._extract_context(text, term, 50)
        return context

    def _extract_usage_examples(self, text: str, term: str) -> List[str]:
        """提取使用示例"""
        examples = []

        # 寻找包含术语的句子作为示例
        sentences = re.split(r'[。！？]', text)
        for sentence in sentences:
            if term in sentence and len(sentence.strip()) > 10:
                examples.append(sentence.strip())
                if len(examples) >= 3:  # 限制示例数量
                    break

        return examples

    def _identify_term_domain(self, text: str, term: str) -> Optional[DomainType]:
        """识别术语所属域"""
        context = self._extract_context(text, term, 200)

        for domain_name, domain_type in self.domain_markers.items():
            if domain_name in context:
                return domain_type

        return None

    def _calculate_term_importance(self, text: str, term: str) -> int:
        """计算术语重要性"""
        frequency = text.count(term)

        if frequency >= 10:
            return 10
        elif frequency >= 5:
            return 8
        elif frequency >= 3:
            return 6
        else:
            return 5

    def _find_relation_in_text(self, text: str, entity1: str, entity2: str) -> Tuple[Optional[RelationType], float]:
        """在文本中寻找实体关系"""
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                match = re.search(pattern.format(entity1, entity2), text, re.IGNORECASE)
                if match:
                    return relation_type, 0.8

                # 反向匹配
                match = re.search(pattern.format(entity2, entity1), text, re.IGNORECASE)
                if match:
                    return relation_type, 0.8

        # 如果在同一段落中出现，认为有弱关联
        if entity1 in text and entity2 in text:
            return RelationType.RELATED_TO, 0.3

        return None, 0.0