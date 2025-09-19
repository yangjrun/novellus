# -*- coding: utf-8 -*-
"""
裂世九域·法则链纪元 文化框架分析工具
支持六维文化分析和实体关系网络构建
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import asyncio
from pathlib import Path


class DomainType(Enum):
    """九域类型枚举"""
    HUMAN = "人域"
    HEAVEN = "天域"
    WILD = "荒域"
    UNDERWORLD = "冥域"
    DEMON = "魔域"
    VOID = "虚域"
    SEA = "海域"
    SOURCE = "源域"
    UNKNOWN = "未知域"


class CulturalDimension(Enum):
    """六维文化框架"""
    MYTHOLOGY_RELIGION = "A"  # 神话与宗教
    POWER_LAW = "B"          # 权力与法律
    ECONOMY_TECH = "C"       # 经济与技术
    FAMILY_EDUCATION = "D"   # 家庭与教育
    RITUAL_DAILY = "E"       # 仪式与日常
    ART_ENTERTAINMENT = "F"  # 艺术与娱乐


class EntityType(Enum):
    """实体类型"""
    ORGANIZATION = "组织机构"
    CONCEPT = "重要概念"
    CULTURAL_ITEM = "文化物品"
    RITUAL = "仪式活动"
    LOCATION = "地理位置"
    CHARACTER = "角色人物"
    POWER_SYSTEM = "权力体系"
    TRADE_ITEM = "贸易物品"


@dataclass
class CulturalEntity:
    """文化实体"""
    name: str
    entity_type: EntityType
    domain: DomainType
    dimension: CulturalDimension
    description: str
    importance_level: int  # 1-10
    related_entities: List[str]
    attributes: Dict[str, Any]
    source_text: str


@dataclass
class DomainRelation:
    """域间关系"""
    from_domain: DomainType
    to_domain: DomainType
    relation_type: str  # 政治、经济、文化、军事等
    strength: int  # 1-10
    nature: str     # 友好、敌对、中立、复杂等
    description: str
    key_factors: List[str]


@dataclass
class CulturalDimension6D:
    """六维文化数据"""
    mythology_religion: Dict[str, Any]    # A. 神话与宗教
    power_law: Dict[str, Any]            # B. 权力与法律
    economy_tech: Dict[str, Any]         # C. 经济与技术
    family_education: Dict[str, Any]     # D. 家庭与教育
    ritual_daily: Dict[str, Any]         # E. 仪式与日常
    art_entertainment: Dict[str, Any]    # F. 艺术与娱乐


@dataclass
class DomainCulture:
    """单个域的完整文化信息"""
    domain_name: str
    domain_type: DomainType
    description: str
    cultural_dimensions: CulturalDimension6D
    entities: List[CulturalEntity]
    internal_structure: Dict[str, Any]
    external_relations: List[DomainRelation]
    plot_hooks: List[str]
    potential_conflicts: List[str]


class CulturalFrameworkAnalyzer:
    """文化框架分析器"""

    def __init__(self):
        self.domains: Dict[DomainType, DomainCulture] = {}
        self.entities: List[CulturalEntity] = []
        self.relations: List[DomainRelation] = []
        self.concept_dictionary: Dict[str, Dict[str, Any]] = {}

        # 实体识别模式
        self.entity_patterns = {
            EntityType.ORGANIZATION: [
                r'([^\s]*王朝|[^\s]*议会|[^\s]*宗门|[^\s]*司|[^\s]*殿|[^\s]*院|[^\s]*府|[^\s]*团|[^\s]*会)',
                r'(天命王朝|祭司议会|冥司殿|裂世反叛军)'
            ],
            EntityType.CONCEPT: [
                r'(链籍|法则链|断链术|[^\s]*链[^\s]*)',
                r'([^\s]*法则[^\s]*|[^\s]*律[^\s]*|[^\s]*道[^\s]*)'
            ],
            EntityType.CULTURAL_ITEM: [
                r'(链票|环印|镇魂器|[^\s]*器|[^\s]*印|[^\s]*符)',
                r'([^\s]*宝|[^\s]*珠|[^\s]*石|[^\s]*玉)'
            ],
            EntityType.RITUAL: [
                r'(裂世夜|归环礼|狂环月|[^\s]*节|[^\s]*礼|[^\s]*祭)',
                r'([^\s]*典|[^\s]*仪|[^\s]*会)'
            ],
            EntityType.LOCATION: [
                r'(帝都|[^\s]*港|[^\s]*城|[^\s]*阙|[^\s]*山|[^\s]*海)',
                r'([^\s]*宫|[^\s]*院|[^\s]*台|[^\s]*楼|[^\s]*阁)'
            ]
        }

        # 链相关概念词典
        self.chain_concepts = {
            '链籍': {'type': '法则记录', 'domains': ['天域'], 'function': '记录法则'},
            '法则链': {'type': '核心概念', 'domains': ['所有域'], 'function': '修炼基础'},
            '断链术': {'type': '禁忌法术', 'domains': ['虚域', '魔域'], 'function': '破坏法则'},
            '链票': {'type': '货币工具', 'domains': ['人域', '天域'], 'function': '经济交易'},
            '环印': {'type': '身份标识', 'domains': ['天域'], 'function': '权力象征'},
            '镇魂器': {'type': '法器', 'domains': ['冥域'], 'function': '灵魂控制'}
        }

    def parse_domain_text(self, domain_text: str, domain_type: DomainType) -> DomainCulture:
        """解析单个域的文本内容"""

        # 提取六维文化内容
        cultural_dimensions = self._extract_cultural_dimensions(domain_text)

        # 识别实体
        entities = self._extract_entities(domain_text, domain_type)

        # 提取情节钩子
        plot_hooks = self._extract_plot_hooks(domain_text)

        # 识别潜在冲突
        conflicts = self._identify_conflicts(domain_text, entities)

        domain_culture = DomainCulture(
            domain_name=domain_type.value,
            domain_type=domain_type,
            description=self._extract_domain_description(domain_text),
            cultural_dimensions=cultural_dimensions,
            entities=entities,
            internal_structure=self._analyze_internal_structure(domain_text),
            external_relations=[],  # 将在分析完所有域后填充
            plot_hooks=plot_hooks,
            potential_conflicts=conflicts
        )

        self.domains[domain_type] = domain_culture
        self.entities.extend(entities)

        return domain_culture

    def _extract_cultural_dimensions(self, text: str) -> CulturalDimension6D:
        """提取六维文化信息"""

        # 查找各维度的内容标记
        dimensions = {
            'A': {},  # 神话与宗教
            'B': {},  # 权力与法律
            'C': {},  # 经济与技术
            'D': {},  # 家庭与教育
            'E': {},  # 仪式与日常
            'F': {}   # 艺术与娱乐
        }

        # 使用正则表达式查找维度标记
        for dim_code in dimensions.keys():
            pattern = rf'{dim_code}\.([^\n]*(?:\n(?!(?:[A-F]\.|\n))[^\n]*)*)'
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

            if matches:
                content = matches[0].strip()
                dimensions[dim_code] = self._parse_dimension_content(content, dim_code)

        return CulturalDimension6D(
            mythology_religion=dimensions['A'],
            power_law=dimensions['B'],
            economy_tech=dimensions['C'],
            family_education=dimensions['D'],
            ritual_daily=dimensions['E'],
            art_entertainment=dimensions['F']
        )

    def _parse_dimension_content(self, content: str, dimension_code: str) -> Dict[str, Any]:
        """解析维度内容"""
        result = {
            'title': '',
            'key_elements': [],
            'organizations': [],
            'concepts': [],
            'items': [],
            'practices': [],
            'raw_content': content
        }

        # 提取标题
        lines = content.split('\n')
        if lines:
            result['title'] = lines[0].strip()

        # 提取关键要素
        for line in lines[1:]:
            line = line.strip()
            if line and not line.startswith('-'):
                # 识别不同类型的要素
                if any(keyword in line for keyword in ['王朝', '议会', '宗门', '司', '殿']):
                    result['organizations'].append(line)
                elif any(keyword in line for keyword in ['链', '法则', '术', '道']):
                    result['concepts'].append(line)
                elif any(keyword in line for keyword in ['器', '印', '符', '票']):
                    result['items'].append(line)
                else:
                    result['practices'].append(line)

                result['key_elements'].append(line)

        return result

    def _extract_entities(self, text: str, domain: DomainType) -> List[CulturalEntity]:
        """提取文本中的实体"""
        entities = []

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity_name = match.group(1) if match.groups() else match.group(0)

                    # 确定维度
                    dimension = self._determine_entity_dimension(entity_name, text)

                    entity = CulturalEntity(
                        name=entity_name,
                        entity_type=entity_type,
                        domain=domain,
                        dimension=dimension,
                        description=self._extract_entity_description(entity_name, text),
                        importance_level=self._assess_importance(entity_name, text),
                        related_entities=self._find_related_entities(entity_name, text),
                        attributes=self._extract_entity_attributes(entity_name, text),
                        source_text=self._extract_source_context(entity_name, text)
                    )
                    entities.append(entity)

        return entities

    def _determine_entity_dimension(self, entity_name: str, text: str) -> CulturalDimension:
        """确定实体所属的文化维度"""
        # 在文本中查找实体周围的维度标记
        pattern = rf'([A-F]\..*?{re.escape(entity_name)}.*?)(?=[A-F]\.|$)'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            section = match.group(1)
            if section.startswith('A.'):
                return CulturalDimension.MYTHOLOGY_RELIGION
            elif section.startswith('B.'):
                return CulturalDimension.POWER_LAW
            elif section.startswith('C.'):
                return CulturalDimension.ECONOMY_TECH
            elif section.startswith('D.'):
                return CulturalDimension.FAMILY_EDUCATION
            elif section.startswith('E.'):
                return CulturalDimension.RITUAL_DAILY
            elif section.startswith('F.'):
                return CulturalDimension.ART_ENTERTAINMENT

        # 默认根据实体类型推断
        type_to_dimension = {
            EntityType.ORGANIZATION: CulturalDimension.POWER_LAW,
            EntityType.CONCEPT: CulturalDimension.MYTHOLOGY_RELIGION,
            EntityType.CULTURAL_ITEM: CulturalDimension.ECONOMY_TECH,
            EntityType.RITUAL: CulturalDimension.RITUAL_DAILY,
            EntityType.LOCATION: CulturalDimension.POWER_LAW
        }

        return type_to_dimension.get(entity_name, CulturalDimension.MYTHOLOGY_RELIGION)

    def _extract_entity_description(self, entity_name: str, text: str) -> str:
        """提取实体描述"""
        # 查找实体周围的描述性文本
        pattern = rf'[^\n]*{re.escape(entity_name)}[^\n]*'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _assess_importance(self, entity_name: str, text: str) -> int:
        """评估实体重要性 (1-10)"""
        # 基于出现频率和上下文关键词
        frequency = len(re.findall(re.escape(entity_name), text))

        # 关键词权重
        keywords_weight = 0
        important_keywords = ['核心', '重要', '关键', '主要', '统治', '控制', '法则']
        context_pattern = rf'.{{0,50}}{re.escape(entity_name)}.{{0,50}}'
        context_matches = re.findall(context_pattern, text)

        for context in context_matches:
            for keyword in important_keywords:
                if keyword in context:
                    keywords_weight += 1

        # 计算重要性分数 (1-10)
        score = min(10, max(1, frequency * 2 + keywords_weight))
        return score

    def _find_related_entities(self, entity_name: str, text: str) -> List[str]:
        """查找相关实体"""
        related = []

        # 在同一段落中查找其他实体
        paragraphs = text.split('\n\n')
        target_paragraph = None

        for paragraph in paragraphs:
            if entity_name in paragraph:
                target_paragraph = paragraph
                break

        if target_paragraph:
            for entity_type, patterns in self.entity_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, target_paragraph)
                    for match in matches:
                        if match != entity_name and match not in related:
                            related.append(match)

        return related[:5]  # 限制数量

    def _extract_entity_attributes(self, entity_name: str, text: str) -> Dict[str, Any]:
        """提取实体属性"""
        attributes = {}

        # 如果是链相关概念，使用预定义信息
        if entity_name in self.chain_concepts:
            attributes.update(self.chain_concepts[entity_name])

        # 提取数值属性
        context_pattern = rf'.{{0,100}}{re.escape(entity_name)}.{{0,100}}'
        context = re.search(context_pattern, text)

        if context:
            context_text = context.group(0)

            # 查找等级、级别等数值
            level_patterns = [
                r'([一二三四五六七八九十]+)级',
                r'([一二三四五六七八九十]+)层',
                r'([一二三四五六七八九十]+)阶',
                r'第([一二三四五六七八九十]+)'
            ]

            for pattern in level_patterns:
                match = re.search(pattern, context_text)
                if match:
                    attributes['level'] = match.group(1)
                    break

        return attributes

    def _extract_source_context(self, entity_name: str, text: str) -> str:
        """提取实体的源文本上下文"""
        pattern = rf'.{{0,200}}{re.escape(entity_name)}.{{0,200}}'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _extract_plot_hooks(self, text: str) -> List[str]:
        """提取情节钩子"""
        hooks = []

        # 查找明确的情节钩子部分
        hook_patterns = [
            r'情节钩子[：:](.*?)(?=\n\n|\n[A-Z]|$)',
            r'剧情事件[：:](.*?)(?=\n\n|\n[A-Z]|$)',
            r'故事线索[：:](.*?)(?=\n\n|\n[A-Z]|$)'
        ]

        for pattern in hook_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                # 分割为单独的钩子
                individual_hooks = [hook.strip() for hook in match.split('\n') if hook.strip()]
                hooks.extend(individual_hooks)

        # 如果没有明确标记，查找冲突性描述
        if not hooks:
            conflict_indicators = [
                '冲突', '矛盾', '争夺', '对立', '敌对', '竞争',
                '危机', '威胁', '阴谋', '秘密', '禁忌'
            ]

            for indicator in conflict_indicators:
                pattern = rf'[^\n]*{indicator}[^\n]*'
                matches = re.findall(pattern, text)
                hooks.extend(matches[:3])  # 限制数量

        return hooks

    def _identify_conflicts(self, text: str, entities: List[CulturalEntity]) -> List[str]:
        """识别潜在冲突"""
        conflicts = []

        # 基于实体类型识别冲突
        organizations = [e for e in entities if e.entity_type == EntityType.ORGANIZATION]

        if len(organizations) > 1:
            conflicts.append(f"多个组织势力并存可能产生权力冲突")

        # 查找明确的冲突描述
        conflict_keywords = ['冲突', '对立', '争夺', '矛盾', '敌对']
        for keyword in conflict_keywords:
            pattern = rf'[^\n]*{keyword}[^\n]*'
            matches = re.findall(pattern, text)
            conflicts.extend(matches)

        return conflicts[:5]  # 限制数量

    def _extract_domain_description(self, text: str) -> str:
        """提取域的总体描述"""
        # 查找文本开头的描述段落
        lines = text.split('\n')
        description_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith(('A.', 'B.', 'C.', 'D.', 'E.', 'F.')):
                description_lines.append(line)
            elif line.startswith(('A.', 'B.', 'C.', 'D.', 'E.', 'F.')):
                break

        return ' '.join(description_lines)

    def _analyze_internal_structure(self, text: str) -> Dict[str, Any]:
        """分析域内部结构"""
        structure = {
            'hierarchy_levels': [],
            'power_distribution': {},
            'key_institutions': [],
            'social_classes': []
        }

        # 查找等级制度相关信息
        hierarchy_keywords = ['等级', '阶层', '级别', '层次', '品级']
        for keyword in hierarchy_keywords:
            pattern = rf'[^\n]*{keyword}[^\n]*'
            matches = re.findall(pattern, text)
            structure['hierarchy_levels'].extend(matches)

        # 识别关键机构
        institution_keywords = ['宗门', '议会', '王朝', '殿', '院', '府']
        for keyword in institution_keywords:
            pattern = rf'[^\s]*{keyword}[^\s]*'
            matches = re.findall(pattern, text)
            structure['key_institutions'].extend(matches)

        return structure

    def analyze_cross_domain_relations(self) -> List[DomainRelation]:
        """分析跨域关系"""
        relations = []

        # 分析每对域之间的关系
        domain_list = list(self.domains.keys())

        for i, domain1 in enumerate(domain_list):
            for domain2 in domain_list[i+1:]:
                relation = self._analyze_domain_pair_relation(domain1, domain2)
                if relation:
                    relations.append(relation)

        self.relations = relations
        return relations

    def _analyze_domain_pair_relation(self, domain1: DomainType, domain2: DomainType) -> Optional[DomainRelation]:
        """分析两个域之间的关系"""

        # 预定义的域间关系
        known_relations = {
            (DomainType.HEAVEN, DomainType.HUMAN): {
                'type': '政治统治',
                'strength': 9,
                'nature': '上下级',
                'description': '天域对人域的统治关系'
            },
            (DomainType.DEMON, DomainType.HUMAN): {
                'type': '敌对冲突',
                'strength': 7,
                'nature': '敌对',
                'description': '魔域与人域的对立关系'
            },
            (DomainType.SEA, DomainType.HUMAN): {
                'type': '贸易往来',
                'strength': 6,
                'nature': '互利',
                'description': '海域与人域的贸易关系'
            }
        }

        # 检查预定义关系
        pair_key = (domain1, domain2)
        reverse_key = (domain2, domain1)

        if pair_key in known_relations:
            rel_info = known_relations[pair_key]
            return DomainRelation(
                from_domain=domain1,
                to_domain=domain2,
                relation_type=rel_info['type'],
                strength=rel_info['strength'],
                nature=rel_info['nature'],
                description=rel_info['description'],
                key_factors=[]
            )
        elif reverse_key in known_relations:
            rel_info = known_relations[reverse_key]
            return DomainRelation(
                from_domain=domain2,
                to_domain=domain1,
                relation_type=rel_info['type'],
                strength=rel_info['strength'],
                nature=rel_info['nature'],
                description=rel_info['description'],
                key_factors=[]
            )

        # 基于实体分析推断关系
        domain1_entities = [e for e in self.entities if e.domain == domain1]
        domain2_entities = [e for e in self.entities if e.domain == domain2]

        # 查找共同实体或相关实体
        common_entities = []
        for e1 in domain1_entities:
            for e2 in domain2_entities:
                if e1.name in e2.related_entities or e2.name in e1.related_entities:
                    common_entities.append((e1.name, e2.name))

        if common_entities:
            return DomainRelation(
                from_domain=domain1,
                to_domain=domain2,
                relation_type='实体关联',
                strength=len(common_entities),
                nature='复杂',
                description=f'通过共同实体产生关联: {", ".join([f"{c[0]}-{c[1]}" for c in common_entities[:3]])}',
                key_factors=[c[0] for c in common_entities]
            )

        return None

    def build_concept_dictionary(self) -> Dict[str, Dict[str, Any]]:
        """构建核心概念词典"""

        # 基础链概念
        self.concept_dictionary.update(self.chain_concepts)

        # 从实体中提取概念
        concept_entities = [e for e in self.entities if e.entity_type == EntityType.CONCEPT]

        for entity in concept_entities:
            if entity.name not in self.concept_dictionary:
                self.concept_dictionary[entity.name] = {
                    'type': '提取概念',
                    'domain': entity.domain.value,
                    'dimension': entity.dimension.value,
                    'description': entity.description,
                    'importance': entity.importance_level,
                    'attributes': entity.attributes
                }

        return self.concept_dictionary

    def generate_structured_output(self) -> Dict[str, Any]:
        """生成结构化JSON输出"""

        # 构建跨域关系网络
        self.analyze_cross_domain_relations()

        # 构建概念词典
        self.build_concept_dictionary()

        output = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_domains': len(self.domains),
                'total_entities': len(self.entities),
                'total_relations': len(self.relations),
                'analysis_version': '1.0'
            },

            'domain_cultures': {
                domain_type.value: {
                    'basic_info': {
                        'name': culture.domain_name,
                        'type': culture.domain_type.value,
                        'description': culture.description
                    },
                    'cultural_dimensions': {
                        'mythology_religion': culture.cultural_dimensions.mythology_religion,
                        'power_law': culture.cultural_dimensions.power_law,
                        'economy_tech': culture.cultural_dimensions.economy_tech,
                        'family_education': culture.cultural_dimensions.family_education,
                        'ritual_daily': culture.cultural_dimensions.ritual_daily,
                        'art_entertainment': culture.cultural_dimensions.art_entertainment
                    },
                    'entities': [
                        {
                            'name': entity.name,
                            'type': entity.entity_type.value,
                            'dimension': entity.dimension.value,
                            'importance': entity.importance_level,
                            'description': entity.description,
                            'attributes': entity.attributes,
                            'related_entities': entity.related_entities
                        }
                        for entity in culture.entities
                    ],
                    'internal_structure': culture.internal_structure,
                    'plot_hooks': culture.plot_hooks,
                    'potential_conflicts': culture.potential_conflicts
                }
                for domain_type, culture in self.domains.items()
            },

            'cross_domain_relations': [
                {
                    'from_domain': relation.from_domain.value,
                    'to_domain': relation.to_domain.value,
                    'relation_type': relation.relation_type,
                    'strength': relation.strength,
                    'nature': relation.nature,
                    'description': relation.description,
                    'key_factors': relation.key_factors
                }
                for relation in self.relations
            ],

            'concept_dictionary': self.concept_dictionary,

            'entity_summary': {
                'by_type': {
                    entity_type.value: len([e for e in self.entities if e.entity_type == entity_type])
                    for entity_type in EntityType
                },
                'by_domain': {
                    domain_type.value: len([e for e in self.entities if e.domain == domain_type])
                    for domain_type in self.domains.keys()
                },
                'high_importance': [
                    {
                        'name': entity.name,
                        'domain': entity.domain.value,
                        'importance': entity.importance_level,
                        'type': entity.entity_type.value
                    }
                    for entity in sorted(self.entities, key=lambda x: x.importance_level, reverse=True)[:10]
                ]
            },

            'analysis_insights': {
                'dominant_themes': self._identify_dominant_themes(),
                'power_structure_analysis': self._analyze_power_structures(),
                'cultural_conflicts': self._identify_cultural_conflicts(),
                'world_consistency': self._check_world_consistency()
            }
        }

        return output

    def _identify_dominant_themes(self) -> List[str]:
        """识别主导主题"""
        themes = []

        # 基于高频概念识别主题
        concept_frequency = {}
        for entity in self.entities:
            if entity.entity_type == EntityType.CONCEPT:
                concept_frequency[entity.name] = concept_frequency.get(entity.name, 0) + entity.importance_level

        # 排序并取前5个
        top_concepts = sorted(concept_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        themes.extend([f"核心概念: {concept}" for concept, _ in top_concepts])

        # 基于维度分布识别主题
        dimension_count = {}
        for entity in self.entities:
            dim = entity.dimension.value
            dimension_count[dim] = dimension_count.get(dim, 0) + 1

        max_dimension = max(dimension_count.items(), key=lambda x: x[1])
        themes.append(f"文化重点: {max_dimension[0]}维度占主导")

        return themes

    def _analyze_power_structures(self) -> Dict[str, Any]:
        """分析权力结构"""
        organizations = [e for e in self.entities if e.entity_type == EntityType.ORGANIZATION]

        analysis = {
            'total_organizations': len(organizations),
            'by_domain': {},
            'hierarchy_indicators': [],
            'power_concentration': 'unknown'
        }

        for org in organizations:
            domain = org.domain.value
            if domain not in analysis['by_domain']:
                analysis['by_domain'][domain] = []
            analysis['by_domain'][domain].append({
                'name': org.name,
                'importance': org.importance_level
            })

        # 分析权力集中度
        if len(organizations) <= 2:
            analysis['power_concentration'] = 'high'
        elif len(organizations) <= 5:
            analysis['power_concentration'] = 'medium'
        else:
            analysis['power_concentration'] = 'distributed'

        return analysis

    def _identify_cultural_conflicts(self) -> List[Dict[str, Any]]:
        """识别文化冲突"""
        conflicts = []

        # 基于域间关系识别冲突
        for relation in self.relations:
            if relation.nature in ['敌对', '冲突']:
                conflicts.append({
                    'type': '域间冲突',
                    'description': relation.description,
                    'intensity': relation.strength,
                    'participants': [relation.from_domain.value, relation.to_domain.value]
                })

        # 基于实体冲突识别
        for domain_type, culture in self.domains.items():
            for conflict_desc in culture.potential_conflicts:
                conflicts.append({
                    'type': '域内冲突',
                    'description': conflict_desc,
                    'domain': domain_type.value,
                    'intensity': 5  # 默认中等强度
                })

        return conflicts

    def _check_world_consistency(self) -> Dict[str, Any]:
        """检查世界观一致性"""
        consistency = {
            'chain_concept_consistency': True,
            'power_hierarchy_consistency': True,
            'cultural_logic_consistency': True,
            'issues': []
        }

        # 检查链概念的一致性
        chain_entities = [e for e in self.entities if '链' in e.name]
        if len(chain_entities) > 0:
            # 检查不同域对链的理解是否一致
            chain_descriptions = {e.domain.value: e.description for e in chain_entities}
            if len(set(chain_descriptions.values())) > len(chain_descriptions) * 0.7:
                consistency['chain_concept_consistency'] = False
                consistency['issues'].append("不同域对'链'概念的理解存在较大差异")

        # 检查权力等级的逻辑性
        organizations = [e for e in self.entities if e.entity_type == EntityType.ORGANIZATION]
        if len(organizations) > 1:
            importance_levels = [org.importance_level for org in organizations]
            if max(importance_levels) - min(importance_levels) > 8:
                consistency['power_hierarchy_consistency'] = False
                consistency['issues'].append("组织间权力差距过大，可能存在逻辑问题")

        # 检查文化元素的逻辑性
        for domain_type, culture in self.domains.items():
            dimensions = culture.cultural_dimensions
            # 简单检查：是否所有维度都有内容
            dim_count = sum(1 for dim in [
                dimensions.mythology_religion,
                dimensions.power_law,
                dimensions.economy_tech,
                dimensions.family_education,
                dimensions.ritual_daily,
                dimensions.art_entertainment
            ] if dim)

            if dim_count < 4:  # 少于4个维度有内容
                consistency['cultural_logic_consistency'] = False
                consistency['issues'].append(f"{domain_type.value}的文化维度不够完整")

        return consistency

    async def analyze_full_text(self, text_content: str) -> Dict[str, Any]:
        """分析完整的九域文化文本"""

        # 分割九个域的内容
        domain_sections = self._split_domain_sections(text_content)

        # 分析每个域
        for domain_type, section_text in domain_sections.items():
            if section_text.strip():
                self.parse_domain_text(section_text, domain_type)

        # 生成完整的结构化输出
        return self.generate_structured_output()

    def _split_domain_sections(self, text: str) -> Dict[DomainType, str]:
        """分割九域文本内容"""
        sections = {}

        # 域名模式
        domain_patterns = {
            DomainType.HUMAN: [r'人域', r'人间域', r'凡人域'],
            DomainType.HEAVEN: [r'天域', r'天界域', r'天命域'],
            DomainType.WILD: [r'荒域', r'蛮荒域', r'野域'],
            DomainType.UNDERWORLD: [r'冥域', r'幽冥域', r'阴间域'],
            DomainType.DEMON: [r'魔域', r'魔界域', r'邪魔域'],
            DomainType.VOID: [r'虚域', r'虚空域', r'虚无域'],
            DomainType.SEA: [r'海域', r'海洋域', r'水域'],
            DomainType.SOURCE: [r'源域', r'本源域', r'起源域']
        }

        # 为每个域查找对应的文本段落
        for domain_type, patterns in domain_patterns.items():
            for pattern in patterns:
                # 查找域标题到下一个域标题之间的内容
                domain_pattern = rf'{pattern}.*?(?=(?:人域|天域|荒域|冥域|魔域|虚域|海域|源域)|$)'
                match = re.search(domain_pattern, text, re.DOTALL)

                if match:
                    sections[domain_type] = match.group(0)
                    break

            # 如果没有找到，设置为空
            if domain_type not in sections:
                sections[domain_type] = ""

        return sections

    def save_analysis_result(self, result: Dict[str, Any], output_path: str):
        """保存分析结果"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    def load_analysis_result(self, input_path: str) -> Dict[str, Any]:
        """加载分析结果"""
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)


# 示例使用
async def main():
    """示例主函数"""
    analyzer = CulturalFrameworkAnalyzer()

    # 示例文本（实际使用时替换为真实的九域文本）
    sample_text = """
    人域
    A. 神话与宗教
    天命信仰主导，认为链籍记录着天意，法则链是天赋的力量体系。

    B. 权力与法律
    天命王朝统治，采用链籍等级制度，以环印标识身份地位。

    C. 经济与技术
    链票作为主要货币，贸易发达，技术水平中等。

    D. 家庭与教育
    重视血脉传承，法则链能力世代相传。

    E. 仪式与日常
    裂世夜祭祀，归环礼成年仪式。

    F. 艺术与娱乐
    链纹艺术，环音乐器演奏。

    情节钩子：
    - 平民发现异常法则链能力
    - 天命王朝内部权力斗争
    - 与其他域的贸易冲突
    """

    # 分析文本
    result = await analyzer.analyze_full_text(sample_text)

    # 保存结果
    output_path = "cultural_analysis_result.json"
    analyzer.save_analysis_result(result, output_path)

    print(f"分析完成，结果已保存到: {output_path}")
    print(f"发现 {result['analysis_metadata']['total_domains']} 个域")
    print(f"识别 {result['analysis_metadata']['total_entities']} 个实体")
    print(f"分析 {result['analysis_metadata']['total_relations']} 个跨域关系")


if __name__ == "__main__":
    asyncio.run(main())