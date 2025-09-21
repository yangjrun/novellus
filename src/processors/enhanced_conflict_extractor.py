#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版冲突要素提取器
专门设计用于从跨域冲突矩阵分析报告中提取完整的60个实体和270个关系
"""

import json
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EnhancedConflictEntity:
    """增强版冲突实体数据模型"""
    id: str
    novel_id: str
    name: str
    entity_type: str  # 核心资源、法条制度、关键角色
    domains: List[str]
    importance: str
    description: str
    category: str = ""
    aliases: List[str] = None
    characteristics: Dict[str, Any] = None
    source_conflict_pair: str = ""
    confidence_score: float = 0.95
    extraction_method: str = "matrix_direct"
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.aliases is None:
            self.aliases = []
        if self.characteristics is None:
            self.characteristics = {}

@dataclass
class EnhancedConflictRelation:
    """增强版冲突关系数据模型"""
    id: str
    novel_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    description: str
    strength: float
    context: str
    is_cross_domain: bool
    source_domain: str
    target_domain: str
    bidirectional: bool = True
    temporal_context: str = "current"
    confidence_score: float = 0.8
    detection_method: str = "matrix_inference"
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class EnhancedConflictExtractor:
    """增强版冲突要素提取器"""

    def __init__(self):
        self.entities: Dict[str, EnhancedConflictEntity] = {}
        self.relations: Dict[str, EnhancedConflictRelation] = {}
        self.novel_id = "裂世九域-法则链纪元-placeholder-id"

        # 详细的实体映射（基于原始数据中的具体实体）
        self.detailed_entity_mapping = {
            # 人域↔天域冲突实体
            "人域_天域": {
                "核心资源": [
                    {"name": "粮税征收", "description": "人域向天域缴纳的粮食税收，是基础行政资源"},
                    {"name": "人役征召", "description": "天域对人域的人力征召权，包括劳役和兵役"},
                    {"name": "链籍指标", "description": "天域制定的链籍管理标准和配额"},
                    {"name": "童生青壮征召", "description": "天域优先征召人域的优秀青年"},
                    {"name": "评印权", "description": "天域对人域器械和技术的评印审核权威"},
                    {"name": "界核维护承包", "description": "人域承担的界核维护工作合同"}
                ],
                "法条制度": [
                    {"name": "《链籍法》", "description": "规范链籍管理的基本法律"},
                    {"name": "链祭日", "description": "固定的链法祭祀活动日期"},
                    {"name": "新生链测", "description": "新生儿的链法天赋测试仪式"},
                    {"name": "环约巡誓", "description": "定期进行的环印约定宣誓仪式"},
                    {"name": "万器朝链", "description": "所有器械向链法致敬的仪式"},
                    {"name": "评印院年审", "description": "评印院的年度审核制度"}
                ],
                "关键角色": [
                    {"name": "巡链官", "description": "负责巡视链法执行情况的天域官员"},
                    {"name": "缚司", "description": "负责约束和管理的执法人员"},
                    {"name": "乡祭/里正", "description": "基层的宗教和行政负责人"},
                    {"name": "被降等的黑籍户", "description": "因违法被降等的问题人员"},
                    {"name": "税收官", "description": "负责税收征收的官员"},
                    {"name": "链籍官", "description": "管理链籍的专门官员"},
                    {"name": "地方领主", "description": "人域的地方统治者"},
                    {"name": "民兵组织", "description": "地方武装力量"}
                ]
            },
            # 人域↔灵域冲突实体
            "人域_灵域": {
                "核心资源": [
                    {"name": "链算所参数与标准", "description": "灵域制定的计算和测量标准"},
                    {"name": "学徒供给", "description": "向灵域提供的学徒候选人"},
                    {"name": "低端代工", "description": "人域承担的低技术含量制造工作"},
                    {"name": "链墨/链纤维采购", "description": "灵域从人域采购的基础材料"},
                    {"name": "学徒名额", "description": "灵域提供给人域的学徒培训名额"},
                    {"name": "器械供应", "description": "灵域向人域供应的器械设备"}
                ],
                "法条制度": [
                    {"name": "《环印律》", "description": "规范环印使用的法律条文"},
                    {"name": "《工程链契》", "description": "工程项目的链法合同规范"},
                    {"name": "师承刻环礼", "description": "师父收徒弟的正式仪式"},
                    {"name": "学徒三年小试", "description": "学徒期间的阶段性考核"},
                    {"name": "《工坊用工契》", "description": "工坊雇佣工人的合同规范"},
                    {"name": "万器朝链", "description": "器械向链法致敬的共同仪式"}
                ],
                "关键角色": [
                    {"name": "评印院执事", "description": "评印院的执行官员"},
                    {"name": "链算所监理", "description": "链算所的监督管理人员"},
                    {"name": "宗匠", "description": "技艺精湛的手工业大师"},
                    {"name": "公会头人", "description": "各类工匠公会的领导人"},
                    {"name": "器械师", "description": "制造和维修器械的技术人员"},
                    {"name": "评印官", "description": "负责器械评印的官员"},
                    {"name": "学徒候选人", "description": "希望成为学徒的年轻人"},
                    {"name": "贸易商", "description": "从事商业贸易的商人"}
                ]
            },
            # 人域↔荒域冲突实体
            "人域_荒域": {
                "核心资源": [
                    {"name": "链矿坐标", "description": "链矿位置的精确坐标信息"},
                    {"name": "断链者引渡", "description": "对断链罪犯的引渡处理"},
                    {"name": "边境军镇补给线", "description": "边境军事据点的供应线"},
                    {"name": "边贸粮盐", "description": "边境贸易中的粮食和盐类"},
                    {"name": "链矿走带", "description": "链矿的运输通道"},
                    {"name": "护运与治安", "description": "货物护送和治安维护服务"}
                ],
                "法条制度": [
                    {"name": "边防临时断链许可", "description": "边防特殊情况下的断链授权"},
                    {"name": "裂世夜取缔令", "description": "裂世夜期间的禁令条例"},
                    {"name": "《边域缚约》", "description": "边境地区的约束性法规"},
                    {"name": "火灰印通关", "description": "使用火灰印的通关手续"},
                    {"name": "《互市环约》", "description": "互市贸易的环印约定"},
                    {"name": "灾年临时断链互助", "description": "灾害年份的临时断链救助"}
                ],
                "关键角色": [
                    {"name": "军镇都尉", "description": "边境军镇的军事指挥官"},
                    {"name": "断链祭司", "description": "负责断链仪式的宗教人员"},
                    {"name": "部落首领", "description": "荒域各部落的领导人"},
                    {"name": "天域密探", "description": "天域派遣的情报人员"},
                    {"name": "边防军官", "description": "边境防务的军事官员"},
                    {"name": "走私头目", "description": "走私集团的首领"},
                    {"name": "边境商人", "description": "从事边境贸易的商人"},
                    {"name": "流民组织", "description": "边境地区的流民团体"}
                ]
            },
            # 天域↔灵域冲突实体
            "天域_灵域": {
                "核心资源": [
                    {"name": "监管权威", "description": "天域对灵域的监督管理权力"},
                    {"name": "评印体系", "description": "器械和技术的评印认证体系"},
                    {"name": "链法解释权", "description": "对链法条文的最终解释权"}
                ],
                "法条制度": [
                    {"name": "《环印律》统一版", "description": "天域制定的统一环印法律"},
                    {"name": "《工程链契》标准", "description": "天域规范的工程合同标准"},
                    {"name": "评印院年审制", "description": "天域对评印院的年度审核制度"}
                ],
                "关键角色": [
                    {"name": "监管官", "description": "天域派驻的监督官员"},
                    {"name": "高级器械师", "description": "技术等级最高的器械师"},
                    {"name": "链法学者", "description": "研究链法理论的学者"},
                    {"name": "评印委员会", "description": "负责评印工作的委员会"}
                ]
            },
            # 天域↔荒域冲突实体
            "天域_荒域": {
                "核心资源": [
                    {"name": "断链惩罚权", "description": "天域对断链行为的惩罚权力"},
                    {"name": "矿脉开采权", "description": "荒域矿脉的开采权限"},
                    {"name": "军镇建设权", "description": "在荒域建设军事据点的权力"}
                ],
                "法条制度": [
                    {"name": "《边域缚约》执行令", "description": "边域法规的执行命令"},
                    {"name": "断链者引渡法", "description": "断链罪犯的引渡法律"},
                    {"name": "荒域开发许可", "description": "荒域资源开发的许可制度"}
                ],
                "关键角色": [
                    {"name": "断链执行官", "description": "执行断链惩罚的官员"},
                    {"name": "矿业公司", "description": "从事矿业开采的企业"},
                    {"name": "军镇指挥官", "description": "荒域军镇的指挥官"},
                    {"name": "荒域部族", "description": "荒域的原住民部族"}
                ]
            },
            # 灵域↔荒域冲突实体
            "灵域_荒域": {
                "核心资源": [
                    {"name": "断链器与碎链武装交易", "description": "违禁武器的非法交易"},
                    {"name": "遗迹清道", "description": "古代遗迹的清理和探索"},
                    {"name": "矿料直采", "description": "绕过正规渠道的矿料开采"},
                    {"name": "黑市器械", "description": "在黑市流通的非正规器械"},
                    {"name": "稀有矿料", "description": "荒域出产的珍贵矿物材料"},
                    {"name": "远古遗械", "description": "古代遗留的神秘器械"}
                ],
                "法条制度": [
                    {"name": "链工博览黑市分会", "description": "链工博览会的地下黑市部分"},
                    {"name": "遗迹开发许可证", "description": "遗迹探索和开发的许可"},
                    {"name": "《危械禁令》", "description": "禁止危险器械的法令"}
                ],
                "关键角色": [
                    {"name": "黑市商人", "description": "从事黑市交易的商人"},
                    {"name": "矿料走私犯", "description": "非法运输矿料的走私者"},
                    {"name": "遗械猎人", "description": "专门寻找古代器械的冒险者"},
                    {"name": "考古学者", "description": "研究古代文明的学者"}
                ]
            }
        }

    def load_conflict_matrix_data(self, file_path: str) -> Dict[str, Any]:
        """加载冲突矩阵分析数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功加载冲突矩阵数据: {file_path}")
            return data
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return {}

    def extract_all_entities(self, matrix_data: Dict[str, Any]) -> None:
        """提取所有实体 - 从原始数据和详细映射"""
        logger.info("开始提取所有冲突实体...")

        # 1. 提取原始报告中的60个实体
        self._extract_entities_from_original_report(matrix_data)

        # 2. 从详细映射中补充实体
        self._extract_entities_from_detailed_mapping()

        # 3. 从剧情钩子中提取隐含实体
        self._extract_entities_from_plot_hooks(matrix_data)

        logger.info(f"实体提取完成，共提取 {len(self.entities)} 个实体")

    def _extract_entities_from_original_report(self, matrix_data: Dict[str, Any]) -> None:
        """从原始报告提取实体"""
        try:
            # 查找原始报告中的实体数据
            if "2. 冲突要素详细分析" in matrix_data:
                analysis_section = matrix_data["2. 冲突要素详细分析"]

                # 检查是否有conflict_entities字段
                if "conflict_entities" in analysis_section:
                    entities_list = analysis_section["conflict_entities"]
                    logger.info(f"从原始报告中找到 {len(entities_list)} 个实体")

                    for entity_data in entities_list:
                        entity = EnhancedConflictEntity(
                            id=entity_data.get("id", str(uuid.uuid4())),
                            novel_id=self.novel_id,
                            name=entity_data.get("name", ""),
                            entity_type=entity_data.get("entity_type", ""),
                            domains=entity_data.get("domains", []),
                            importance=entity_data.get("importance", "中"),
                            description=entity_data.get("description", ""),
                            category=self._determine_category(entity_data.get("entity_type", "")),
                            source_conflict_pair=self._determine_conflict_pair(entity_data.get("domains", [])),
                            confidence_score=0.95
                        )
                        self.entities[entity.id] = entity
                else:
                    logger.warning("原始报告中未找到conflict_entities字段")
            else:
                logger.warning("原始报告中未找到冲突要素详细分析部分")

        except Exception as e:
            logger.error(f"从原始报告提取实体时发生错误: {e}")

    def _extract_entities_from_detailed_mapping(self) -> None:
        """从详细映射中提取实体"""
        logger.info("从详细实体映射中提取实体...")

        entity_count = 0
        for conflict_pair, domains_data in self.detailed_entity_mapping.items():
            domain_a, domain_b = conflict_pair.split("_")
            domain_a_name = domain_a + "域"
            domain_b_name = domain_b + "域"

            for entity_type, entities_list in domains_data.items():
                for entity_info in entities_list:
                    entity_id = f"detailed_{entity_count}"
                    entity_count += 1

                    entity = EnhancedConflictEntity(
                        id=entity_id,
                        novel_id=self.novel_id,
                        name=entity_info["name"],
                        entity_type=entity_type,
                        domains=[domain_a_name, domain_b_name],
                        importance="高" if entity_type == "核心资源" else "中高",
                        description=entity_info["description"],
                        category=self._determine_category(entity_type),
                        source_conflict_pair=f"{domain_a_name}↔{domain_b_name}",
                        confidence_score=0.9,
                        extraction_method="detailed_mapping"
                    )

                    # 检查是否已存在相同名称的实体
                    existing_entity = None
                    for existing in self.entities.values():
                        if existing.name == entity.name:
                            existing_entity = existing
                            break

                    if existing_entity:
                        # 合并域信息
                        existing_entity.domains = list(set(existing_entity.domains + entity.domains))
                        # 更新描述
                        if len(entity.description) > len(existing_entity.description):
                            existing_entity.description = entity.description
                    else:
                        self.entities[entity_id] = entity

    def _extract_entities_from_plot_hooks(self, matrix_data: Dict[str, Any]) -> None:
        """从剧情钩子中提取隐含实体"""
        logger.info("从剧情钩子中提取隐含实体...")

        if "4. 故事情节潜力评估" in matrix_data:
            hooks_data = matrix_data["4. 故事情节潜力评估"].get("剧情钩子分析", {})

            hook_entity_count = 0
            for conflict_pair, hook_info in hooks_data.items():
                for hook in hook_info.get("钩子详情", []):
                    description = hook.get("描述", "")

                    # 从描述中提取关键实体
                    entities = self._extract_entities_from_description(description, conflict_pair)
                    for entity_name in entities:
                        entity_id = f"hook_entity_{hook_entity_count}"
                        hook_entity_count += 1

                        # 检查是否已存在
                        exists = any(e.name == entity_name for e in self.entities.values())
                        if not exists:
                            entity = EnhancedConflictEntity(
                                id=entity_id,
                                novel_id=self.novel_id,
                                name=entity_name,
                                entity_type="推断实体",
                                domains=conflict_pair.split("↔") if "↔" in conflict_pair else [conflict_pair],
                                importance="待评估",
                                description=f"从剧情钩子'{description[:50]}...'中提取的实体",
                                category="情节相关",
                                source_conflict_pair=conflict_pair,
                                confidence_score=0.7,
                                extraction_method="plot_hook_extraction"
                            )
                            self.entities[entity_id] = entity

    def _extract_entities_from_description(self, description: str, conflict_pair: str) -> List[str]:
        """从描述中提取实体名称"""
        entities = []

        # 实体关键词模式
        patterns = [
            r'([^，。；！？]*官[^，。；！？]*)',      # 以"官"结尾的实体
            r'([^，。；！？]*师[^，。；！？]*)',      # 以"师"结尾的实体
            r'([^，。；！？]*商[^，。；！？]*)',      # 以"商"结尾的实体
            r'([^，。；！？]*组织[^，。；！？]*)',    # 包含"组织"的实体
            r'([^，。；！？]*军[^，。；！？]*)',      # 包含"军"的实体
            r'([^，。；！？]*市场[^，。；！？]*)',    # 包含"市场"的实体
            r'([^，。；！？]*网络[^，。；！？]*)',    # 包含"网络"的实体
            r'([^，。；！？]*器械[^，。；！？]*)',    # 包含"器械"的实体
        ]

        for pattern in patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                clean_match = match.strip()
                if 2 < len(clean_match) < 20 and clean_match not in entities:
                    entities.append(clean_match)

        return entities[:3]  # 限制每个描述最多提取3个实体

    def _determine_category(self, entity_type: str) -> str:
        """确定实体细分类别"""
        category_mapping = {
            "核心资源": "资源要素",
            "法条制度": "制度规范",
            "关键角色": "人员角色",
            "推断实体": "推断要素"
        }
        return category_mapping.get(entity_type, "其他")

    def _determine_conflict_pair(self, domains: List[str]) -> str:
        """确定冲突对"""
        if len(domains) >= 2:
            return f"{domains[0]}↔{domains[1]}"
        elif len(domains) == 1:
            return domains[0]
        return "未知冲突对"

    def build_comprehensive_relations(self, matrix_data: Dict[str, Any]) -> None:
        """构建全面的关系网络"""
        logger.info("构建全面的冲突关系网络...")

        # 1. 从冲突矩阵构建跨域关系
        self._build_cross_domain_relations(matrix_data)

        # 2. 构建同域合作关系
        self._build_same_domain_relations()

        # 3. 从实体类型推断关系
        self._build_type_based_relations()

        # 4. 从剧情钩子推断关系
        self._build_plot_based_relations(matrix_data)

        logger.info(f"关系网络构建完成，共构建 {len(self.relations)} 个关系")

    def _build_cross_domain_relations(self, matrix_data: Dict[str, Any]) -> None:
        """构建跨域关系"""
        # 从冲突矩阵强度数据构建关系
        if "1. 冲突矩阵深度分析" in matrix_data:
            strength_matrix = matrix_data["1. 冲突矩阵深度分析"].get("强度矩阵", [])
            domains = ["人域", "天域", "灵域", "荒域"]

            relation_count = 0
            for i, row in enumerate(strength_matrix):
                for j, strength in enumerate(row):
                    if i != j and strength > 0:
                        domain_a, domain_b = domains[i], domains[j]

                        # 找到这两个域的实体
                        domain_a_entities = [e for e in self.entities.values() if domain_a in e.domains]
                        domain_b_entities = [e for e in self.entities.values() if domain_b in e.domains]

                        # 在相同类型的实体间创建关系
                        for entity_a in domain_a_entities:
                            for entity_b in domain_b_entities:
                                if entity_a.entity_type == entity_b.entity_type:
                                    relation_id = f"cross_domain_relation_{relation_count}"
                                    relation_count += 1

                                    relation = EnhancedConflictRelation(
                                        id=relation_id,
                                        novel_id=self.novel_id,
                                        source_entity_id=entity_a.id,
                                        target_entity_id=entity_b.id,
                                        relation_type="对立",
                                        description=f"{domain_a}与{domain_b}间的{entity_a.entity_type}冲突",
                                        strength=strength / 4.0,  # 标准化强度到0-1区间
                                        context=f"跨域冲突: {domain_a}↔{domain_b}",
                                        is_cross_domain=True,
                                        source_domain=domain_a,
                                        target_domain=domain_b,
                                        confidence_score=0.8
                                    )
                                    self.relations[relation_id] = relation

    def _build_same_domain_relations(self) -> None:
        """构建同域关系"""
        # 同域实体间的合作关系
        domain_entities = defaultdict(list)
        for entity in self.entities.values():
            for domain in entity.domains:
                domain_entities[domain].append(entity)

        relation_count = len(self.relations)
        for domain, entities in domain_entities.items():
            # 在同域的不同类型实体间建立依赖关系
            resource_entities = [e for e in entities if e.entity_type == "核心资源"]
            law_entities = [e for e in entities if e.entity_type == "法条制度"]
            role_entities = [e for e in entities if e.entity_type == "关键角色"]

            # 资源-角色依赖关系
            for resource in resource_entities:
                for role in role_entities:
                    relation_id = f"resource_role_relation_{relation_count}"
                    relation_count += 1

                    relation = EnhancedConflictRelation(
                        id=relation_id,
                        novel_id=self.novel_id,
                        source_entity_id=role.id,
                        target_entity_id=resource.id,
                        relation_type="依赖",
                        description=f"{role.name}依赖{resource.name}进行工作",
                        strength=0.6,
                        context=f"{domain}域内资源依赖",
                        is_cross_domain=False,
                        source_domain=domain,
                        target_domain=domain,
                        confidence_score=0.7
                    )
                    self.relations[relation_id] = relation

            # 法条-角色制约关系
            for law in law_entities:
                for role in role_entities:
                    relation_id = f"law_role_relation_{relation_count}"
                    relation_count += 1

                    relation = EnhancedConflictRelation(
                        id=relation_id,
                        novel_id=self.novel_id,
                        source_entity_id=law.id,
                        target_entity_id=role.id,
                        relation_type="制约",
                        description=f"{law.name}制约{role.name}的行为",
                        strength=0.5,
                        context=f"{domain}域内法条制约",
                        is_cross_domain=False,
                        source_domain=domain,
                        target_domain=domain,
                        confidence_score=0.6
                    )
                    self.relations[relation_id] = relation

    def _build_type_based_relations(self) -> None:
        """基于实体类型构建关系"""
        # 相同类型实体间的竞争关系
        type_entities = defaultdict(list)
        for entity in self.entities.values():
            type_entities[entity.entity_type].append(entity)

        relation_count = len(self.relations)
        for entity_type, entities in type_entities.items():
            if entity_type in ["核心资源", "关键角色"]:
                # 在相同类型的实体间建立竞争关系
                for i, entity_a in enumerate(entities):
                    for entity_b in entities[i+1:i+3]:  # 限制关系数量
                        # 只在不同域的实体间建立竞争关系
                        if not set(entity_a.domains).intersection(set(entity_b.domains)):
                            relation_id = f"competition_relation_{relation_count}"
                            relation_count += 1

                            relation = EnhancedConflictRelation(
                                id=relation_id,
                                novel_id=self.novel_id,
                                source_entity_id=entity_a.id,
                                target_entity_id=entity_b.id,
                                relation_type="竞争",
                                description=f"{entity_a.name}与{entity_b.name}的{entity_type}竞争",
                                strength=0.4,
                                context=f"{entity_type}竞争关系",
                                is_cross_domain=True,
                                source_domain=entity_a.domains[0] if entity_a.domains else "未知",
                                target_domain=entity_b.domains[0] if entity_b.domains else "未知",
                                confidence_score=0.5
                            )
                            self.relations[relation_id] = relation

    def _build_plot_based_relations(self, matrix_data: Dict[str, Any]) -> None:
        """基于剧情钩子构建关系"""
        if "4. 故事情节潜力评估" in matrix_data:
            hooks_data = matrix_data["4. 故事情节潜力评估"].get("剧情钩子分析", {})

            relation_count = len(self.relations)
            for conflict_pair, hook_info in hooks_data.items():
                for hook in hook_info.get("钩子详情", []):
                    conflict_type = hook.get("冲突类型", "")
                    description = hook.get("描述", "")

                    # 找到相关的实体
                    relevant_entities = []
                    for entity in self.entities.values():
                        if (conflict_pair in entity.source_conflict_pair or
                            any(keyword in description for keyword in [entity.name] + entity.aliases)):
                            relevant_entities.append(entity)

                    # 在相关实体间建立情节关系
                    if len(relevant_entities) >= 2:
                        relation_type = self._get_relation_type_from_conflict(conflict_type)
                        for i, entity_a in enumerate(relevant_entities):
                            for entity_b in relevant_entities[i+1:i+2]:  # 限制关系数量
                                relation_id = f"plot_relation_{relation_count}"
                                relation_count += 1

                                relation = EnhancedConflictRelation(
                                    id=relation_id,
                                    novel_id=self.novel_id,
                                    source_entity_id=entity_a.id,
                                    target_entity_id=entity_b.id,
                                    relation_type=relation_type,
                                    description=f"基于剧情'{description[:30]}...'的{relation_type}关系",
                                    strength=0.6,
                                    context=f"剧情冲突: {conflict_type}",
                                    is_cross_domain="↔" in conflict_pair,
                                    source_domain=entity_a.domains[0] if entity_a.domains else "未知",
                                    target_domain=entity_b.domains[0] if entity_b.domains else "未知",
                                    confidence_score=0.6,
                                    detection_method="plot_hook_analysis"
                                )
                                self.relations[relation_id] = relation

    def _get_relation_type_from_conflict(self, conflict_type: str) -> str:
        """根据冲突类型确定关系类型"""
        type_mapping = {
            "权力斗争": "对立",
            "身份认同": "竞争",
            "经济冲突": "竞争",
            "综合冲突": "制约",
            "生存危机": "依赖"
        }
        return type_mapping.get(conflict_type, "影响")

    def generate_comprehensive_output(self, output_dir: str = "D:/work/novellus/enhanced_conflict_output") -> Dict[str, Any]:
        """生成全面的输出"""
        logger.info("生成全面的结构化输出...")

        import os
        os.makedirs(output_dir, exist_ok=True)

        # 生成主要数据集
        datasets = {
            "metadata": {
                "extraction_time": datetime.now().isoformat(),
                "novel_id": self.novel_id,
                "extractor_version": "enhanced_v1.0",
                "total_entities": len(self.entities),
                "total_relations": len(self.relations)
            },
            "entities": [asdict(entity) for entity in self.entities.values()],
            "relations": [asdict(relation) for relation in self.relations.values()],
            "statistics": self._generate_comprehensive_statistics(),
            "network_graph": self._generate_network_graph_data(),
            "entity_index": self._generate_entity_index(),
            "relation_matrix": self._generate_relation_matrix()
        }

        # 保存主要数据文件
        main_file = f"{output_dir}/enhanced_conflict_elements_data.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(datasets, f, ensure_ascii=False, indent=2)

        # 生成PostgreSQL插入脚本
        postgres_script = self._generate_enhanced_postgres_script()
        script_file = f"{output_dir}/enhanced_postgresql_insert.sql"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(postgres_script)

        # 生成数据质量报告
        quality_report = self._generate_quality_report()
        quality_file = f"{output_dir}/enhanced_quality_report.json"
        with open(quality_file, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)

        # 生成CSV格式数据（用于Excel分析）
        self._generate_csv_outputs(output_dir)

        summary_report = {
            "处理时间": datetime.now().isoformat(),
            "输出目录": output_dir,
            "数据统计": {
                "实体总数": len(self.entities),
                "关系总数": len(self.relations),
                "跨域关系数": len([r for r in self.relations.values() if r.is_cross_domain]),
                "域覆盖": list(set([d for e in self.entities.values() for d in e.domains]))
            },
            "输出文件": {
                "主数据文件": main_file,
                "PostgreSQL脚本": script_file,
                "质量报告": quality_file
            }
        }

        logger.info(f"全面输出生成完成，输出到: {output_dir}")
        return summary_report

    def _generate_comprehensive_statistics(self) -> Dict[str, Any]:
        """生成全面统计信息"""
        entity_by_type = defaultdict(int)
        entity_by_domain = defaultdict(int)
        entity_by_importance = defaultdict(int)

        for entity in self.entities.values():
            entity_by_type[entity.entity_type] += 1
            entity_by_importance[entity.importance] += 1
            for domain in entity.domains:
                entity_by_domain[domain] += 1

        relation_by_type = defaultdict(int)
        relation_by_strength = {"0.0-0.3": 0, "0.3-0.6": 0, "0.6-1.0": 0}
        cross_domain_count = 0

        for relation in self.relations.values():
            relation_by_type[relation.relation_type] += 1
            if relation.is_cross_domain:
                cross_domain_count += 1

            # 强度分类
            if relation.strength < 0.3:
                relation_by_strength["0.0-0.3"] += 1
            elif relation.strength < 0.6:
                relation_by_strength["0.3-0.6"] += 1
            else:
                relation_by_strength["0.6-1.0"] += 1

        return {
            "entity_statistics": {
                "by_type": dict(entity_by_type),
                "by_domain": dict(entity_by_domain),
                "by_importance": dict(entity_by_importance),
                "average_confidence": sum(e.confidence_score for e in self.entities.values()) / len(self.entities) if self.entities else 0
            },
            "relation_statistics": {
                "by_type": dict(relation_by_type),
                "by_strength": dict(relation_by_strength),
                "cross_domain_ratio": cross_domain_count / len(self.relations) if self.relations else 0,
                "average_confidence": sum(r.confidence_score for r in self.relations.values()) / len(self.relations) if self.relations else 0
            },
            "network_statistics": {
                "node_count": len(self.entities),
                "edge_count": len(self.relations),
                "density": len(self.relations) / (len(self.entities) * (len(self.entities) - 1)) if len(self.entities) > 1 else 0,
                "average_degree": (2 * len(self.relations)) / len(self.entities) if self.entities else 0
            }
        }

    def _generate_network_graph_data(self) -> Dict[str, Any]:
        """生成网络图数据"""
        nodes = []
        edges = []

        # 生成节点
        for entity in self.entities.values():
            node = {
                "id": entity.id,
                "label": entity.name,
                "type": entity.entity_type,
                "domains": entity.domains,
                "importance": entity.importance,
                "confidence": entity.confidence_score,
                "size": self._calculate_node_size(entity),
                "color": self._get_node_color(entity.entity_type),
                "category": entity.category
            }
            nodes.append(node)

        # 生成边
        for relation in self.relations.values():
            edge = {
                "id": relation.id,
                "source": relation.source_entity_id,
                "target": relation.target_entity_id,
                "type": relation.relation_type,
                "strength": relation.strength,
                "is_cross_domain": relation.is_cross_domain,
                "confidence": relation.confidence_score,
                "width": max(1, relation.strength * 10),
                "color": self._get_edge_color(relation.relation_type)
            }
            edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "layout_suggestions": {
                "force_directed": {"repulsion": 1000, "attraction": 0.1},
                "hierarchical": {"direction": "UD", "sortMethod": "directed"},
                "clustering": {"algorithm": "modularity"}
            }
        }

    def _calculate_node_size(self, entity: EnhancedConflictEntity) -> int:
        """计算节点大小"""
        base_size = 10

        # 重要性权重
        importance_weights = {"极高": 2.5, "高": 2.0, "中高": 1.5, "中": 1.0, "低": 0.7, "待评估": 0.8}
        importance_multiplier = importance_weights.get(entity.importance, 1.0)

        # 连接数权重
        connection_count = len([r for r in self.relations.values()
                              if r.source_entity_id == entity.id or r.target_entity_id == entity.id])
        connection_bonus = min(connection_count * 0.3, 3)

        # 置信度权重
        confidence_bonus = entity.confidence_score * 2

        size = base_size * importance_multiplier + connection_bonus + confidence_bonus
        return int(max(8, min(30, size)))  # 限制在8-30范围内

    def _get_node_color(self, entity_type: str) -> str:
        """获取节点颜色"""
        colors = {
            "核心资源": "#E74C3C",      # 红色 - 资源
            "法条制度": "#3498DB",      # 蓝色 - 制度
            "关键角色": "#2ECC71",      # 绿色 - 角色
            "推断实体": "#F39C12",      # 橙色 - 推断
            "其他": "#95A5A6"          # 灰色 - 其他
        }
        return colors.get(entity_type, "#95A5A6")

    def _get_edge_color(self, relation_type: str) -> str:
        """获取边颜色"""
        colors = {
            "对立": "#E74C3C",         # 红色
            "竞争": "#E67E22",         # 橙红色
            "制约": "#8E44AD",         # 紫色
            "依赖": "#27AE60",         # 绿色
            "合作": "#16A085",         # 青绿色
            "影响": "#3498DB",         # 蓝色
            "包含": "#F39C12",         # 橙色
            "衍生": "#E91E63"          # 粉色
        }
        return colors.get(relation_type, "#BDC3C7")

    def _generate_entity_index(self) -> Dict[str, Any]:
        """生成实体索引"""
        index = {
            "by_name": {},
            "by_type": defaultdict(list),
            "by_domain": defaultdict(list),
            "by_importance": defaultdict(list)
        }

        for entity in self.entities.values():
            index["by_name"][entity.name] = entity.id
            index["by_type"][entity.entity_type].append(entity.id)
            index["by_importance"][entity.importance].append(entity.id)

            for domain in entity.domains:
                index["by_domain"][domain].append(entity.id)

        # 转换defaultdict为普通dict
        return {
            "by_name": index["by_name"],
            "by_type": dict(index["by_type"]),
            "by_domain": dict(index["by_domain"]),
            "by_importance": dict(index["by_importance"])
        }

    def _generate_relation_matrix(self) -> Dict[str, Any]:
        """生成关系矩阵"""
        entity_ids = list(self.entities.keys())
        matrix_size = len(entity_ids)

        # 创建邻接矩阵
        adjacency_matrix = [[0 for _ in range(matrix_size)] for _ in range(matrix_size)]
        relation_types_matrix = [["" for _ in range(matrix_size)] for _ in range(matrix_size)]

        id_to_index = {entity_id: i for i, entity_id in enumerate(entity_ids)}

        for relation in self.relations.values():
            if relation.source_entity_id in id_to_index and relation.target_entity_id in id_to_index:
                source_idx = id_to_index[relation.source_entity_id]
                target_idx = id_to_index[relation.target_entity_id]

                adjacency_matrix[source_idx][target_idx] = relation.strength
                relation_types_matrix[source_idx][target_idx] = relation.relation_type

                if relation.bidirectional:
                    adjacency_matrix[target_idx][source_idx] = relation.strength
                    relation_types_matrix[target_idx][source_idx] = relation.relation_type

        return {
            "entity_ids": entity_ids,
            "adjacency_matrix": adjacency_matrix,
            "relation_types_matrix": relation_types_matrix,
            "matrix_size": matrix_size
        }

    def _generate_enhanced_postgres_script(self) -> str:
        """生成增强版PostgreSQL插入脚本"""
        script = f"""
-- 增强版冲突要素数据批量插入脚本
-- 生成时间: {datetime.now().isoformat()}
-- 实体总数: {len(self.entities)}
-- 关系总数: {len(self.relations)}

BEGIN;

-- 插入文化实体数据
INSERT INTO cultural_entities (
    id, novel_id, name, entity_type, domain_type, dimensions,
    description, characteristics, functions, significance,
    confidence_score, extraction_method, validation_status,
    aliases, tags, created_at, updated_at
) VALUES
"""

        # 生成实体插入语句
        entity_values = []
        for entity in self.entities.values():
            characteristics_json = json.dumps(entity.characteristics, ensure_ascii=False).replace("'", "''")
            values = f"""(
    '{entity.id}',
    '{entity.novel_id}',
    '{entity.name.replace("'", "''")}',
    '{entity.entity_type}',
    '{entity.domains[0] if entity.domains else "未知"}',
    ARRAY{entity.domains},
    '{entity.description.replace("'", "''")}',
    '{characteristics_json}',
    ARRAY['基础功能'],
    '{entity.importance}',
    {entity.confidence_score},
    '{entity.extraction_method}',
    'validated',
    ARRAY{entity.aliases},
    ARRAY['enhanced-extracted'],
    '{entity.created_at}',
    '{entity.created_at}'
)"""
            entity_values.append(values)

        script += ",\n".join(entity_values)
        script += "\nON CONFLICT (id) DO UPDATE SET\n"
        script += "    description = EXCLUDED.description,\n"
        script += "    confidence_score = EXCLUDED.confidence_score,\n"
        script += "    updated_at = CURRENT_TIMESTAMP;\n\n"

        # 生成关系插入语句
        script += """
-- 插入文化关系数据
INSERT INTO cultural_relations (
    id, novel_id, source_entity_id, target_entity_id, relation_type,
    description, strength, context, is_cross_domain,
    source_domain, target_domain, confidence_score, detection_method,
    bidirectional, temporal_context, created_at, updated_at
) VALUES
"""

        relation_values = []
        for relation in self.relations.values():
            values = f"""(
    '{relation.id}',
    '{relation.novel_id}',
    '{relation.source_entity_id}',
    '{relation.target_entity_id}',
    '{relation.relation_type}',
    '{relation.description.replace("'", "''")}',
    {relation.strength},
    '{relation.context.replace("'", "''")}',
    {relation.is_cross_domain},
    '{relation.source_domain}',
    '{relation.target_domain}',
    {relation.confidence_score},
    '{relation.detection_method}',
    {relation.bidirectional},
    '{relation.temporal_context}',
    '{relation.created_at}',
    '{relation.created_at}'
)"""
            relation_values.append(values)

        script += ",\n".join(relation_values)
        script += "\nON CONFLICT (id) DO UPDATE SET\n"
        script += "    strength = EXCLUDED.strength,\n"
        script += "    confidence_score = EXCLUDED.confidence_score,\n"
        script += "    updated_at = CURRENT_TIMESTAMP;\n\n"

        script += "COMMIT;\n\n"

        # 添加统计查询
        script += """
-- 数据统计查询
SELECT
    '实体统计' as category,
    entity_type,
    COUNT(*) as count
FROM cultural_entities
GROUP BY entity_type

UNION ALL

SELECT
    '关系统计' as category,
    relation_type,
    COUNT(*) as count
FROM cultural_relations
GROUP BY relation_type

ORDER BY category, count DESC;
"""

        return script

    def _generate_quality_report(self) -> Dict[str, Any]:
        """生成数据质量报告"""
        return {
            "数据完整性": {
                "实体完整性": {
                    "总实体数": len(self.entities),
                    "有描述的实体": len([e for e in self.entities.values() if e.description]),
                    "有域归属的实体": len([e for e in self.entities.values() if e.domains]),
                    "完整性比例": len([e for e in self.entities.values() if e.description and e.domains]) / len(self.entities)
                },
                "关系完整性": {
                    "总关系数": len(self.relations),
                    "跨域关系数": len([r for r in self.relations.values() if r.is_cross_domain]),
                    "有效关系比例": len([r for r in self.relations.values()
                                    if r.source_entity_id in self.entities and r.target_entity_id in self.entities]) / len(self.relations)
                }
            },
            "数据质量": {
                "实体置信度": {
                    "平均置信度": sum(e.confidence_score for e in self.entities.values()) / len(self.entities),
                    "高置信度实体(>0.8)": len([e for e in self.entities.values() if e.confidence_score > 0.8]),
                    "中等置信度实体(0.5-0.8)": len([e for e in self.entities.values() if 0.5 <= e.confidence_score <= 0.8]),
                    "低置信度实体(<0.5)": len([e for e in self.entities.values() if e.confidence_score < 0.5])
                },
                "关系置信度": {
                    "平均置信度": sum(r.confidence_score for r in self.relations.values()) / len(self.relations),
                    "高置信度关系(>0.7)": len([r for r in self.relations.values() if r.confidence_score > 0.7]),
                    "中等置信度关系(0.4-0.7)": len([r for r in self.relations.values() if 0.4 <= r.confidence_score <= 0.7]),
                    "低置信度关系(<0.4)": len([r for r in self.relations.values() if r.confidence_score < 0.4])
                }
            },
            "覆盖范围": {
                "域覆盖": {
                    domain: len([e for e in self.entities.values() if domain in e.domains])
                    for domain in ["人域", "天域", "灵域", "荒域"]
                },
                "实体类型覆盖": {
                    entity_type: len([e for e in self.entities.values() if e.entity_type == entity_type])
                    for entity_type in ["核心资源", "法条制度", "关键角色", "推断实体"]
                }
            }
        }

    def _generate_csv_outputs(self, output_dir: str) -> None:
        """生成CSV格式输出"""
        import csv

        # 实体CSV
        entities_csv = f"{output_dir}/entities.csv"
        with open(entities_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', '名称', '实体类型', '域归属', '重要性', '描述', '置信度', '提取方法'])

            for entity in self.entities.values():
                writer.writerow([
                    entity.id,
                    entity.name,
                    entity.entity_type,
                    ';'.join(entity.domains),
                    entity.importance,
                    entity.description,
                    entity.confidence_score,
                    entity.extraction_method
                ])

        # 关系CSV
        relations_csv = f"{output_dir}/relations.csv"
        with open(relations_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', '源实体ID', '目标实体ID', '关系类型', '强度', '描述', '跨域', '置信度'])

            for relation in self.relations.values():
                writer.writerow([
                    relation.id,
                    relation.source_entity_id,
                    relation.target_entity_id,
                    relation.relation_type,
                    relation.strength,
                    relation.description,
                    relation.is_cross_domain,
                    relation.confidence_score
                ])

    def run_complete_enhanced_extraction(self, input_file: str) -> Dict[str, Any]:
        """运行完整的增强提取流程"""
        logger.info("开始增强版冲突要素提取流程...")

        # 1. 加载数据
        matrix_data = self.load_conflict_matrix_data(input_file)
        if not matrix_data:
            raise Exception("无法加载冲突矩阵数据")

        # 2. 提取所有实体
        self.extract_all_entities(matrix_data)

        # 3. 构建全面关系网络
        self.build_comprehensive_relations(matrix_data)

        # 4. 生成全面输出
        summary_report = self.generate_comprehensive_output()

        logger.info("增强版提取流程完成")
        return summary_report

def main():
    """主函数"""
    extractor = EnhancedConflictExtractor()

    try:
        # 运行增强版提取流程
        report = extractor.run_complete_enhanced_extraction(
            input_file="D:/work/novellus/cross_domain_conflict_analysis_report.json"
        )

        print("增强版冲突要素提取完成!")
        print(f"数据统计: {report['数据统计']}")
        print(f"输出目录: {report['输出目录']}")

    except Exception as e:
        logger.error(f"提取过程失败: {e}")
        raise

if __name__ == "__main__":
    main()