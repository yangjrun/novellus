#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
裂世九域·法则链纪元 - 冲突要素提取和数据结构化工具
专业数据工程版本

功能：
1. 从跨域冲突矩阵中提取所有冲突要素
2. 对实体进行分类和标准化
3. 构建关系网络数据模型
4. 生成冲突升级路径
5. 提取时空背景和场景数据
6. 数据质量验证和去重
7. 生成标准化数据集和ETL脚本
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
class ConflictEntity:
    """冲突实体数据模型"""
    id: str
    name: str
    entity_type: str  # 核心资源、法条制度、关键角色
    domains: List[str]
    category: str
    description: str
    importance_level: str
    characteristics: Dict[str, Any]
    aliases: List[str]
    source_conflict_pair: str
    confidence_score: float
    extraction_method: str = "conflict_matrix_analysis"
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ConflictRelation:
    """冲突关系数据模型"""
    id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str  # 对立、依赖、竞争、制约、影响
    description: str
    strength: float
    context: str
    is_cross_domain: bool
    source_domain: str
    target_domain: str
    bidirectional: bool
    temporal_context: str
    confidence_score: float
    detection_method: str = "matrix_inference"
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ConflictEscalationPath:
    """冲突升级路径模型"""
    id: str
    conflict_pair: str
    stage_name: str
    stage_level: int
    description: str
    trigger_conditions: List[str]
    escalation_factors: List[str]
    involved_entities: List[str]
    potential_outcomes: List[str]
    probability: float
    risk_level: str
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class PlotHook:
    """剧情钩子数据模型"""
    id: str
    title: str
    description: str
    conflict_pair: str
    complexity_level: int
    dramatic_value: int
    character_potential: int
    conflict_type: str
    trigger_conditions: List[str]
    involved_entities: List[str]
    potential_outcomes: List[str]
    temporal_context: str
    geographic_context: str
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ScenarioContext:
    """场景上下文数据模型"""
    id: str
    name: str
    conflict_pair: str
    geographic_location: str
    temporal_setting: str
    environmental_factors: List[str]
    participant_roles: List[str]
    resource_constraints: List[str]
    cultural_context: List[str]
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class ConflictElementsExtractor:
    """冲突要素提取器 - 专业数据工程实现"""

    def __init__(self):
        self.entities: Dict[str, ConflictEntity] = {}
        self.relations: Dict[str, ConflictRelation] = {}
        self.escalation_paths: Dict[str, ConflictEscalationPath] = {}
        self.plot_hooks: Dict[str, PlotHook] = {}
        self.scenario_contexts: Dict[str, ScenarioContext] = {}

        # 实体分类映射
        self.entity_type_mapping = {
            "核心资源": {
                "税役征收", "链籍管控", "征召权力", "学徒名额", "器械供应", "评印权威",
                "边境贸易", "走私路线", "治安控制", "监管权威", "评印体系", "链法解释",
                "断链惩罚", "矿脉开采", "军镇建设", "黑市器械", "稀有矿料", "远古遗械",
                "粮税", "人役", "链籍指标", "征召童生", "青壮", "评印权", "界核维护承包",
                "链算所参数", "链算所标准", "链矿坐标", "断链者引渡", "边境军镇补给线",
                "学徒供给", "低端代工", "链墨", "链纤维采购", "边贸粮盐", "链矿走带",
                "护运", "治安", "断链器", "碎链武装交易", "遗迹清道", "矿料直采"
            },
            "法条制度": {
                "《链籍法》", "《环印律》", "《边域缚约》", "《工程链契》", "《工坊用工契》",
                "《互市环约》", "《危械禁令》", "链祭日", "新生链测", "环约巡誓",
                "万器朝链", "评印院年审", "边防临时断链许可", "裂世夜取缔令",
                "师承刻环礼", "学徒三年小试", "火灰印通关", "灾年临时断链互助",
                "链工博览黑市分会", "遗迹开发许可证"
            },
            "关键角色": {
                "税收官", "链籍官", "地方领主", "民兵组织", "器械师", "评印官",
                "学徒候选人", "贸易商", "边防军官", "走私头目", "边境商人", "流民组织",
                "监管官", "高级器械师", "链法学者", "评印委员会", "断链执行官",
                "矿业公司", "军镇指挥官", "荒域部族", "黑市商人", "矿料走私犯",
                "遗械猎人", "考古学者", "巡链官", "缚司", "乡祭", "里正",
                "被降等的黑籍户", "评印院执事", "链算所监理", "宗匠", "公会头人",
                "军镇都尉", "断链祭司", "部落首领", "天域密探"
            }
        }

        # 关系类型定义
        self.relation_types = {
            "对立": "两个实体之间存在直接冲突或竞争关系",
            "依赖": "一个实体的存在或功能依赖于另一个实体",
            "竞争": "两个实体争夺相同的资源或地位",
            "制约": "一个实体限制或约束另一个实体的行为",
            "影响": "一个实体对另一个实体产生影响但不直接控制",
            "合作": "两个实体在某些方面存在合作关系",
            "替代": "两个实体在功能上可以相互替代",
            "包含": "一个实体包含或管辖另一个实体",
            "衍生": "一个实体从另一个实体演化或派生而来"
        }

        # 冲突升级阶段定义
        self.escalation_stages = {
            1: {"name": "潜在摩擦", "description": "存在利益分歧但未公开化"},
            2: {"name": "公开分歧", "description": "双方立场明确对立"},
            3: {"name": "局部冲突", "description": "在特定领域发生直接冲突"},
            4: {"name": "全面对抗", "description": "冲突扩大到多个领域"},
            5: {"name": "危机爆发", "description": "冲突达到不可调和的程度"}
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

    def extract_entities_from_matrix(self, matrix_data: Dict[str, Any]) -> None:
        """从冲突矩阵中提取所有实体"""
        logger.info("开始提取冲突实体...")

        # 提取已标识的实体数据
        if "2. 冲突要素详细分析" in matrix_data and "conflict_entities" in matrix_data["2. 冲突要素详细分析"]:
            entities_list = matrix_data["2. 冲突要素详细分析"]["conflict_entities"]

            for entity_data in entities_list:
                entity = ConflictEntity(
                    id=entity_data.get("id", str(uuid.uuid4())),
                    name=entity_data.get("name", ""),
                    entity_type=entity_data.get("entity_type", ""),
                    domains=entity_data.get("domains", []),
                    category=self._classify_entity_category(entity_data.get("name", "")),
                    description=entity_data.get("description", ""),
                    importance_level=entity_data.get("importance", "中"),
                    characteristics=self._extract_entity_characteristics(entity_data),
                    aliases=self._generate_aliases(entity_data.get("name", "")),
                    source_conflict_pair=self._determine_source_conflict_pair(entity_data.get("domains", [])),
                    confidence_score=0.95  # 已验证的实体
                )

                self.entities[entity.id] = entity

        # 从文本描述中提取更多隐含实体
        self._extract_implicit_entities(matrix_data)

        logger.info(f"实体提取完成，共提取 {len(self.entities)} 个实体")

    def _classify_entity_category(self, entity_name: str) -> str:
        """分类实体类别"""
        for category, names in self.entity_type_mapping.items():
            if entity_name in names:
                return category
            # 模糊匹配
            for name in names:
                if name in entity_name or entity_name in name:
                    return category
        return "其他"

    def _extract_entity_characteristics(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取实体特征"""
        characteristics = {}

        # 基础特征
        if "domains" in entity_data:
            characteristics["跨域范围"] = len(entity_data["domains"])
            characteristics["主要域"] = entity_data["domains"][0] if entity_data["domains"] else "未知"

        # 根据实体类型添加特定特征
        entity_type = entity_data.get("entity_type", "")
        if entity_type == "核心资源":
            characteristics["资源类型"] = self._infer_resource_type(entity_data.get("name", ""))
            characteristics["稀缺性"] = self._infer_scarcity(entity_data.get("name", ""))
        elif entity_type == "法条制度":
            characteristics["法条级别"] = self._infer_law_level(entity_data.get("name", ""))
            characteristics["适用范围"] = entity_data.get("domains", [])
        elif entity_type == "关键角色":
            characteristics["角色类型"] = self._infer_role_type(entity_data.get("name", ""))
            characteristics["权力等级"] = self._infer_power_level(entity_data.get("name", ""))

        return characteristics

    def _infer_resource_type(self, name: str) -> str:
        """推断资源类型"""
        if any(keyword in name for keyword in ["税", "征收", "人役"]):
            return "人力资源"
        elif any(keyword in name for keyword in ["链籍", "评印", "链算"]):
            return "信息资源"
        elif any(keyword in name for keyword in ["矿", "材料", "器械"]):
            return "物质资源"
        elif any(keyword in name for keyword in ["贸易", "走私", "市场"]):
            return "经济资源"
        else:
            return "综合资源"

    def _infer_scarcity(self, name: str) -> str:
        """推断稀缺性"""
        if any(keyword in name for keyword in ["稀有", "古", "禁忌", "秘密"]):
            return "极稀缺"
        elif any(keyword in name for keyword in ["高级", "特殊", "精英"]):
            return "稀缺"
        else:
            return "一般"

    def _infer_law_level(self, name: str) -> str:
        """推断法条级别"""
        if "《" in name and "》" in name:
            return "正式法典"
        elif any(keyword in name for keyword in ["礼", "仪", "节"]):
            return "仪式规范"
        elif any(keyword in name for keyword in ["许可", "证", "批准"]):
            return "行政规定"
        else:
            return "习俗约定"

    def _infer_role_type(self, name: str) -> str:
        """推断角色类型"""
        if any(keyword in name for keyword in ["官", "执事", "监理", "司"]):
            return "行政官员"
        elif any(keyword in name for keyword in ["师", "学者", "宗匠"]):
            return "技术专家"
        elif any(keyword in name for keyword in ["商", "贸易", "走私"]):
            return "商业人员"
        elif any(keyword in name for keyword in ["军", "防", "兵"]):
            return "军事人员"
        elif any(keyword in name for keyword in ["部族", "组织", "会"]):
            return "组织团体"
        else:
            return "其他角色"

    def _infer_power_level(self, name: str) -> str:
        """推断权力等级"""
        if any(keyword in name for keyword in ["都尉", "指挥官", "头人", "首领"]):
            return "高级"
        elif any(keyword in name for keyword in ["官", "师", "学者"]):
            return "中级"
        else:
            return "基层"

    def _generate_aliases(self, name: str) -> List[str]:
        """生成实体别名"""
        aliases = []

        # 去除修饰词的简化版本
        simplified = re.sub(r'[的之与和及]', '', name)
        if simplified != name and len(simplified) > 1:
            aliases.append(simplified)

        # 提取关键词
        if len(name) > 2:
            for i in range(len(name) - 1):
                substring = name[i:i+2]
                if len(substring) == 2 and substring not in aliases:
                    aliases.append(substring)

        return aliases[:3]  # 限制别名数量

    def _determine_source_conflict_pair(self, domains: List[str]) -> str:
        """确定源冲突对"""
        if len(domains) >= 2:
            return f"{domains[0]}↔{domains[1]}"
        return "单域实体"

    def _extract_implicit_entities(self, matrix_data: Dict[str, Any]) -> None:
        """从文本描述中提取隐含实体"""
        logger.info("提取隐含实体...")

        # 从剧情钩子中提取实体
        if "4. 故事情节潜力评估" in matrix_data:
            hooks_data = matrix_data["4. 故事情节潜力评估"].get("剧情钩子分析", {})

            for conflict_pair, hook_info in hooks_data.items():
                for hook in hook_info.get("钩子详情", []):
                    self._extract_entities_from_text(
                        hook.get("描述", ""),
                        conflict_pair,
                        source_type="plot_hook"
                    )

    def _extract_entities_from_text(self, text: str, conflict_pair: str, source_type: str) -> None:
        """从文本中提取实体"""
        # 简单的关键词提取（实际应用中可使用NLP技术）
        keywords = ["官", "师", "商", "法", "律", "器", "料", "矿", "域", "镇", "市", "路", "线"]

        for keyword in keywords:
            pattern = rf'([^，。；！？]*{keyword}[^，。；！？]*)'
            matches = re.findall(pattern, text)

            for match in matches:
                if len(match.strip()) > 1 and match.strip() not in [entity.name for entity in self.entities.values()]:
                    # 创建新的隐含实体
                    entity_id = f"implicit_{len(self.entities)}"
                    entity = ConflictEntity(
                        id=entity_id,
                        name=match.strip(),
                        entity_type="推断实体",
                        domains=conflict_pair.split("↔") if "↔" in conflict_pair else [conflict_pair],
                        category="隐含实体",
                        description=f"从{source_type}中提取的隐含实体",
                        importance_level="待评估",
                        characteristics={"extraction_source": source_type},
                        aliases=[],
                        source_conflict_pair=conflict_pair,
                        confidence_score=0.6  # 较低的置信度
                    )
                    self.entities[entity_id] = entity

    def build_relationship_network(self, matrix_data: Dict[str, Any]) -> None:
        """构建关系网络"""
        logger.info("构建冲突关系网络...")

        # 从实体的域归属推断关系
        self._infer_domain_relationships()

        # 从冲突矩阵数据推断关系
        self._infer_matrix_relationships(matrix_data)

        # 从剧情钩子推断关系
        self._infer_hook_relationships(matrix_data)

        logger.info(f"关系网络构建完成，共构建 {len(self.relations)} 个关系")

    def _infer_domain_relationships(self) -> None:
        """从域归属推断关系"""
        # 同域实体间的合作关系
        domain_entities = defaultdict(list)
        for entity in self.entities.values():
            for domain in entity.domains:
                domain_entities[domain].append(entity)

        for domain, entities in domain_entities.items():
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    relation_id = f"relation_{len(self.relations)}"
                    relation = ConflictRelation(
                        id=relation_id,
                        source_entity_id=entity1.id,
                        target_entity_id=entity2.id,
                        relation_type="合作",
                        description=f"同域({domain})实体间的潜在合作关系",
                        strength=0.3,
                        context=f"{domain}域内协作",
                        is_cross_domain=False,
                        source_domain=domain,
                        target_domain=domain,
                        bidirectional=True,
                        temporal_context="持续",
                        confidence_score=0.4,
                        detection_method="domain_inference"
                    )
                    self.relations[relation_id] = relation

    def _infer_matrix_relationships(self, matrix_data: Dict[str, Any]) -> None:
        """从冲突矩阵推断关系"""
        # 从冲突强度推断对立关系
        if "1. 冲突矩阵深度分析" in matrix_data:
            analysis = matrix_data["1. 冲突矩阵深度分析"]

            # 高风险冲突对
            high_risk_pairs = analysis.get("基础统计", {}).get("高风险冲突对", [])
            for pair in high_risk_pairs:
                if len(pair) >= 2:
                    self._create_domain_conflict_relations(pair[0], pair[1], strength=0.8)

    def _create_domain_conflict_relations(self, domain1: str, domain2: str, strength: float) -> None:
        """创建域间冲突关系"""
        domain1_entities = [e for e in self.entities.values() if domain1 in e.domains]
        domain2_entities = [e for e in self.entities.values() if domain2 in e.domains]

        for entity1 in domain1_entities:
            for entity2 in domain2_entities:
                # 只在相同类型的实体间创建直接冲突关系
                if entity1.entity_type == entity2.entity_type:
                    relation_id = f"conflict_relation_{len(self.relations)}"
                    relation = ConflictRelation(
                        id=relation_id,
                        source_entity_id=entity1.id,
                        target_entity_id=entity2.id,
                        relation_type="对立",
                        description=f"{domain1}与{domain2}间的{entity1.entity_type}冲突",
                        strength=strength,
                        context=f"跨域冲突: {domain1}↔{domain2}",
                        is_cross_domain=True,
                        source_domain=domain1,
                        target_domain=domain2,
                        bidirectional=True,
                        temporal_context="持续紧张",
                        confidence_score=0.7,
                        detection_method="conflict_matrix_inference"
                    )
                    self.relations[relation_id] = relation

    def _infer_hook_relationships(self, matrix_data: Dict[str, Any]) -> None:
        """从剧情钩子推断关系"""
        # 基于剧情描述推断实体间的复杂关系
        if "4. 故事情节潜力评估" in matrix_data:
            hooks_data = matrix_data["4. 故事情节潜力评估"].get("剧情钩子分析", {})

            for conflict_pair, hook_info in hooks_data.items():
                for hook in hook_info.get("钩子详情", []):
                    self._analyze_hook_for_relations(hook, conflict_pair)

    def _analyze_hook_for_relations(self, hook: Dict[str, Any], conflict_pair: str) -> None:
        """分析剧情钩子中的关系"""
        description = hook.get("描述", "")
        conflict_type = hook.get("冲突类型", "")

        # 根据冲突类型推断关系类型
        relation_mapping = {
            "权力斗争": "对立",
            "身份认同": "竞争",
            "经济冲突": "竞争",
            "综合冲突": "制约",
            "生存危机": "依赖"
        }

        relation_type = relation_mapping.get(conflict_type, "影响")

        # 查找相关实体并创建关系
        relevant_entities = [e for e in self.entities.values()
                           if any(keyword in description for keyword in [e.name] + e.aliases)]

        for i, entity1 in enumerate(relevant_entities):
            for entity2 in relevant_entities[i+1:]:
                relation_id = f"hook_relation_{len(self.relations)}"
                relation = ConflictRelation(
                    id=relation_id,
                    source_entity_id=entity1.id,
                    target_entity_id=entity2.id,
                    relation_type=relation_type,
                    description=f"基于剧情钩子'{description[:50]}...'推断的关系",
                    strength=0.6,
                    context=f"剧情情境: {conflict_type}",
                    is_cross_domain="↔" in conflict_pair,
                    source_domain=entity1.domains[0] if entity1.domains else "未知",
                    target_domain=entity2.domains[0] if entity2.domains else "未知",
                    bidirectional=relation_type in ["竞争", "对立"],
                    temporal_context="情节相关",
                    confidence_score=0.5,
                    detection_method="plot_hook_analysis"
                )
                self.relations[relation_id] = relation

    def build_escalation_paths(self, matrix_data: Dict[str, Any]) -> None:
        """构建冲突升级路径"""
        logger.info("构建冲突升级路径...")

        # 从冲突强度数据构建升级路径
        if "1. 冲突矩阵深度分析" in matrix_data:
            strength_matrix = matrix_data["1. 冲突矩阵深度分析"].get("强度矩阵", [])
            domains = ["人域", "天域", "灵域", "荒域"]  # 从数据中提取的域列表

            for i, row in enumerate(strength_matrix):
                for j, strength in enumerate(row):
                    if i != j and strength > 0:  # 排除自己与自己的关系
                        domain_a, domain_b = domains[i], domains[j]
                        conflict_pair = f"{domain_a}↔{domain_b}"

                        # 为每个冲突强度等级创建升级路径
                        for stage in range(1, strength + 1):
                            path_id = f"path_{conflict_pair}_{stage}"
                            escalation_path = ConflictEscalationPath(
                                id=path_id,
                                conflict_pair=conflict_pair,
                                stage_name=self.escalation_stages[stage]["name"],
                                stage_level=stage,
                                description=self.escalation_stages[stage]["description"],
                                trigger_conditions=self._generate_trigger_conditions(conflict_pair, stage),
                                escalation_factors=self._generate_escalation_factors(conflict_pair, stage),
                                involved_entities=self._get_conflict_entities(domain_a, domain_b),
                                potential_outcomes=self._generate_potential_outcomes(conflict_pair, stage),
                                probability=self._calculate_escalation_probability(strength, stage),
                                risk_level=self._determine_risk_level(strength, stage)
                            )
                            self.escalation_paths[path_id] = escalation_path

        logger.info(f"升级路径构建完成，共构建 {len(self.escalation_paths)} 个路径")

    def _generate_trigger_conditions(self, conflict_pair: str, stage: int) -> List[str]:
        """生成触发条件"""
        domains = conflict_pair.split("↔")
        base_conditions = {
            1: ["资源竞争加剧", "政策分歧显现", "利益分配不均"],
            2: ["公开声明立场", "媒体曝光争议", "官方表态对立"],
            3: ["小规模冲突事件", "经济制裁措施", "外交抗议"],
            4: ["全面经济封锁", "军事威胁", "联盟分化"],
            5: ["直接军事冲突", "全面断交", "体系性崩溃"]
        }

        return base_conditions.get(stage, ["未定义条件"])

    def _generate_escalation_factors(self, conflict_pair: str, stage: int) -> List[str]:
        """生成升级因素"""
        factors = {
            1: ["误解加深", "沟通不畅", "第三方挑拨"],
            2: ["舆论压力", "内部鹰派势力", "历史恩怨"],
            3: ["军备竞赛", "盟友介入", "经济压力"],
            4: ["国际制裁", "内政危机", "极端主义抬头"],
            5: ["生存威胁", "体系崩溃", "不可逆转的损失"]
        }

        return factors.get(stage, ["未知因素"])

    def _get_conflict_entities(self, domain_a: str, domain_b: str) -> List[str]:
        """获取冲突涉及的实体ID"""
        entities = []
        for entity in self.entities.values():
            if domain_a in entity.domains or domain_b in entity.domains:
                entities.append(entity.id)
        return entities

    def _generate_potential_outcomes(self, conflict_pair: str, stage: int) -> List[str]:
        """生成潜在结果"""
        outcomes = {
            1: ["协商解决", "暂时妥协", "问题搁置"],
            2: ["正式谈判", "第三方调解", "舆论战"],
            3: ["局部和解", "冲突扩大", "国际干预"],
            4: ["全面和谈", "武装冲突", "联盟重组"],
            5: ["完全胜利", "相互毁灭", "新秩序建立"]
        }

        return outcomes.get(stage, ["不确定结果"])

    def _calculate_escalation_probability(self, max_strength: int, current_stage: int) -> float:
        """计算升级概率"""
        if current_stage >= max_strength:
            return 0.9  # 已达到最高强度，维持概率
        else:
            # 升级概率随着接近最高强度而增加
            return 0.3 + (current_stage / max_strength) * 0.6

    def _determine_risk_level(self, max_strength: int, current_stage: int) -> str:
        """确定风险等级"""
        risk_score = (current_stage / 5.0) * (max_strength / 4.0)

        if risk_score < 0.3:
            return "低风险"
        elif risk_score < 0.6:
            return "中风险"
        elif risk_score < 0.8:
            return "高风险"
        else:
            return "极高风险"

    def extract_plot_hooks(self, matrix_data: Dict[str, Any]) -> None:
        """提取剧情钩子"""
        logger.info("提取剧情钩子数据...")

        if "4. 故事情节潜力评估" in matrix_data:
            hooks_data = matrix_data["4. 故事情节潜力评估"].get("剧情钩子分析", {})

            for conflict_pair, hook_info in hooks_data.items():
                for i, hook in enumerate(hook_info.get("钩子详情", [])):
                    hook_id = f"hook_{conflict_pair}_{i}"

                    plot_hook = PlotHook(
                        id=hook_id,
                        title=hook.get("描述", "")[:50] + "...",
                        description=hook.get("描述", ""),
                        conflict_pair=conflict_pair,
                        complexity_level=hook.get("复杂度", 5),
                        dramatic_value=hook.get("戏剧价值", 5),
                        character_potential=hook.get("角色潜力", 5),
                        conflict_type=hook.get("冲突类型", "综合冲突"),
                        trigger_conditions=self._extract_hook_triggers(hook.get("描述", "")),
                        involved_entities=self._find_hook_entities(hook.get("描述", "")),
                        potential_outcomes=self._generate_hook_outcomes(hook.get("冲突类型", "")),
                        temporal_context=self._infer_temporal_context(hook.get("描述", "")),
                        geographic_context=self._infer_geographic_context(hook.get("描述", ""), conflict_pair)
                    )

                    self.plot_hooks[hook_id] = plot_hook

        logger.info(f"剧情钩子提取完成，共提取 {len(self.plot_hooks)} 个钩子")

    def _extract_hook_triggers(self, description: str) -> List[str]:
        """从描述中提取触发条件"""
        triggers = []

        # 关键词匹配
        trigger_keywords = {
            "失踪": "关键人物失踪",
            "伪造": "伪造证件或身份",
            "神秘": "神秘事件发生",
            "围困": "军事围困",
            "腐败": "腐败丑闻曝光",
            "走私": "走私活动暴露",
            "危机": "突发危机事件"
        }

        for keyword, trigger in trigger_keywords.items():
            if keyword in description:
                triggers.append(trigger)

        return triggers if triggers else ["情节触发点"]

    def _find_hook_entities(self, description: str) -> List[str]:
        """查找钩子涉及的实体"""
        involved = []

        for entity in self.entities.values():
            if entity.name in description or any(alias in description for alias in entity.aliases):
                involved.append(entity.id)

        return involved

    def _generate_hook_outcomes(self, conflict_type: str) -> List[str]:
        """生成钩子潜在结果"""
        outcomes_map = {
            "权力斗争": ["权力重新分配", "政治联盟重组", "体制改革"],
            "身份认同": ["身份危机解决", "社会地位变化", "认同体系重构"],
            "经济冲突": ["经济秩序重建", "贸易关系调整", "资源重新分配"],
            "综合冲突": ["多领域变革", "社会结构调整", "新平衡建立"],
            "生存危机": ["生存威胁解除", "安全体系重建", "救援成功"]
        }

        return outcomes_map.get(conflict_type, ["情节解决", "冲突缓解", "新状态确立"])

    def _infer_temporal_context(self, description: str) -> str:
        """推断时间背景"""
        if any(keyword in description for keyword in ["古老", "传说", "远古"]):
            return "历史背景"
        elif any(keyword in description for keyword in ["现在", "当前", "目前"]):
            return "当前时期"
        elif any(keyword in description for keyword in ["未来", "将来", "预言"]):
            return "未来可能"
        else:
            return "时间不明"

    def _infer_geographic_context(self, description: str, conflict_pair: str) -> str:
        """推断地理背景"""
        domains = conflict_pair.split("↔")

        location_keywords = {
            "边境": f"{domains[0]}-{domains[1]}边境地区",
            "深处": f"{domains[-1]}深处",
            "中心": f"{domains[0]}中心区域",
            "矿": "矿脉区域",
            "市场": "贸易市场",
            "军镇": "军事重镇"
        }

        for keyword, location in location_keywords.items():
            if keyword in description:
                return location

        return f"{conflict_pair}交界区域"

    def extract_scenario_contexts(self, matrix_data: Dict[str, Any]) -> None:
        """提取场景上下文"""
        logger.info("提取场景上下文数据...")

        # 从剧情钩子中提取场景
        for hook in self.plot_hooks.values():
            scenario_id = f"scenario_{hook.conflict_pair}_{len(self.scenario_contexts)}"

            scenario = ScenarioContext(
                id=scenario_id,
                name=f"{hook.title}场景",
                conflict_pair=hook.conflict_pair,
                geographic_location=hook.geographic_context,
                temporal_setting=hook.temporal_context,
                environmental_factors=self._extract_environmental_factors(hook.description),
                participant_roles=self._extract_participant_roles(hook.description),
                resource_constraints=self._extract_resource_constraints(hook.description),
                cultural_context=self._extract_cultural_context(hook.description, hook.conflict_pair)
            )

            self.scenario_contexts[scenario_id] = scenario

        logger.info(f"场景上下文提取完成，共提取 {len(self.scenario_contexts)} 个场景")

    def _extract_environmental_factors(self, description: str) -> List[str]:
        """提取环境因素"""
        factors = []

        env_keywords = {
            "矿": "矿业环境",
            "边境": "边境地理",
            "市场": "商业环境",
            "军": "军事环境",
            "秘密": "隐秘环境",
            "危险": "危险环境"
        }

        for keyword, factor in env_keywords.items():
            if keyword in description:
                factors.append(factor)

        return factors if factors else ["一般环境"]

    def _extract_participant_roles(self, description: str) -> List[str]:
        """提取参与角色"""
        roles = []

        for entity in self.entities.values():
            if entity.entity_type == "关键角色" and (
                entity.name in description or
                any(alias in description for alias in entity.aliases)
            ):
                roles.append(entity.name)

        return roles

    def _extract_resource_constraints(self, description: str) -> List[str]:
        """提取资源约束"""
        constraints = []

        constraint_keywords = {
            "限制": "行动限制",
            "禁止": "法律禁止",
            "缺乏": "资源缺乏",
            "竞争": "竞争压力",
            "时间": "时间压力",
            "秘密": "保密需求"
        }

        for keyword, constraint in constraint_keywords.items():
            if keyword in description:
                constraints.append(constraint)

        return constraints if constraints else ["无明显约束"]

    def _extract_cultural_context(self, description: str, conflict_pair: str) -> List[str]:
        """提取文化背景"""
        contexts = []

        cultural_keywords = {
            "法": "法律文化",
            "链": "链文化",
            "传统": "传统文化",
            "仪式": "仪式文化",
            "禁忌": "禁忌文化",
            "信仰": "宗教信仰"
        }

        for keyword, context in cultural_keywords.items():
            if keyword in description:
                contexts.append(context)

        # 添加域特有文化
        domains = conflict_pair.split("↔")
        for domain in domains:
            contexts.append(f"{domain}域文化")

        return list(set(contexts))  # 去重

    def validate_data_quality(self) -> Dict[str, Any]:
        """数据质量验证"""
        logger.info("进行数据质量验证...")

        validation_report = {
            "实体质量": self._validate_entities(),
            "关系质量": self._validate_relations(),
            "完整性检查": self._check_completeness(),
            "一致性检查": self._check_consistency(),
            "去重结果": self._deduplicate_data()
        }

        logger.info("数据质量验证完成")
        return validation_report

    def _validate_entities(self) -> Dict[str, Any]:
        """验证实体数据质量"""
        issues = []
        stats = {
            "total_entities": len(self.entities),
            "by_type": {},
            "by_confidence": {},
            "issues": []
        }

        for entity in self.entities.values():
            # 统计分类
            stats["by_type"][entity.entity_type] = stats["by_type"].get(entity.entity_type, 0) + 1

            # 统计置信度
            conf_range = f"{int(entity.confidence_score * 10) * 10}%-{int(entity.confidence_score * 10) * 10 + 10}%"
            stats["by_confidence"][conf_range] = stats["by_confidence"].get(conf_range, 0) + 1

            # 检查数据完整性
            if not entity.name:
                issues.append(f"实体 {entity.id} 缺少名称")
            if not entity.description:
                issues.append(f"实体 {entity.id} 缺少描述")
            if not entity.domains:
                issues.append(f"实体 {entity.id} 缺少域归属")

        stats["issues"] = issues
        return stats

    def _validate_relations(self) -> Dict[str, Any]:
        """验证关系数据质量"""
        stats = {
            "total_relations": len(self.relations),
            "by_type": {},
            "cross_domain_ratio": 0,
            "bidirectional_ratio": 0,
            "orphaned_relations": []
        }

        cross_domain_count = 0
        bidirectional_count = 0

        for relation in self.relations.values():
            # 统计关系类型
            stats["by_type"][relation.relation_type] = stats["by_type"].get(relation.relation_type, 0) + 1

            # 统计跨域关系
            if relation.is_cross_domain:
                cross_domain_count += 1

            # 统计双向关系
            if relation.bidirectional:
                bidirectional_count += 1

            # 检查孤儿关系（指向不存在实体的关系）
            if relation.source_entity_id not in self.entities:
                stats["orphaned_relations"].append(f"关系 {relation.id} 的源实体不存在")
            if relation.target_entity_id not in self.entities:
                stats["orphaned_relations"].append(f"关系 {relation.id} 的目标实体不存在")

        if len(self.relations) > 0:
            stats["cross_domain_ratio"] = cross_domain_count / len(self.relations)
            stats["bidirectional_ratio"] = bidirectional_count / len(self.relations)

        return stats

    def _check_completeness(self) -> Dict[str, Any]:
        """检查数据完整性"""
        return {
            "实体覆盖率": {
                "核心资源覆盖": len([e for e in self.entities.values() if e.entity_type == "核心资源"]) / 18,
                "法条制度覆盖": len([e for e in self.entities.values() if e.entity_type == "法条制度"]) / 18,
                "关键角色覆盖": len([e for e in self.entities.values() if e.entity_type == "关键角色"]) / 24
            },
            "域覆盖率": {
                domain: len([e for e in self.entities.values() if domain in e.domains])
                for domain in ["人域", "天域", "灵域", "荒域"]
            },
            "关系完整性": {
                "实体关系覆盖率": len(set([r.source_entity_id for r in self.relations.values()] +
                                          [r.target_entity_id for r in self.relations.values()])) / len(self.entities)
            }
        }

    def _check_consistency(self) -> Dict[str, Any]:
        """检查数据一致性"""
        issues = []

        # 检查实体名称唯一性
        name_counts = Counter([entity.name for entity in self.entities.values()])
        duplicates = [name for name, count in name_counts.items() if count > 1]
        if duplicates:
            issues.append(f"重复的实体名称: {duplicates}")

        # 检查关系的逻辑一致性
        for relation in self.relations.values():
            if relation.bidirectional:
                # 检查是否存在反向关系
                reverse_exists = any(
                    r.source_entity_id == relation.target_entity_id and
                    r.target_entity_id == relation.source_entity_id and
                    r.relation_type == relation.relation_type
                    for r in self.relations.values()
                )
                if not reverse_exists:
                    issues.append(f"双向关系 {relation.id} 缺少反向关系")

        return {"consistency_issues": issues}

    def _deduplicate_data(self) -> Dict[str, Any]:
        """数据去重"""
        original_counts = {
            "entities": len(self.entities),
            "relations": len(self.relations)
        }

        # 实体去重（基于名称和类型）
        unique_entities = {}
        entity_mapping = {}  # 旧ID到新ID的映射

        for entity in self.entities.values():
            key = (entity.name, entity.entity_type)
            if key not in unique_entities:
                unique_entities[key] = entity
                entity_mapping[entity.id] = entity.id
            else:
                # 合并重复实体的信息
                existing = unique_entities[key]
                existing.domains = list(set(existing.domains + entity.domains))
                existing.aliases = list(set(existing.aliases + entity.aliases))
                # 保持较高的置信度
                existing.confidence_score = max(existing.confidence_score, entity.confidence_score)
                entity_mapping[entity.id] = existing.id

        # 更新实体字典
        self.entities = {entity.id: entity for entity in unique_entities.values()}

        # 关系去重并更新实体引用
        unique_relations = {}
        for relation in self.relations.values():
            # 更新实体引用
            relation.source_entity_id = entity_mapping.get(relation.source_entity_id, relation.source_entity_id)
            relation.target_entity_id = entity_mapping.get(relation.target_entity_id, relation.target_entity_id)

            # 生成关系唯一键
            key = (
                min(relation.source_entity_id, relation.target_entity_id),
                max(relation.source_entity_id, relation.target_entity_id),
                relation.relation_type
            )

            if key not in unique_relations:
                unique_relations[key] = relation
            else:
                # 保持较高强度的关系
                existing = unique_relations[key]
                existing.strength = max(existing.strength, relation.strength)
                existing.confidence_score = max(existing.confidence_score, relation.confidence_score)

        # 更新关系字典
        self.relations = {relation.id: relation for relation in unique_relations.values()}

        return {
            "removed_entities": original_counts["entities"] - len(self.entities),
            "removed_relations": original_counts["relations"] - len(self.relations),
            "final_counts": {
                "entities": len(self.entities),
                "relations": len(self.relations)
            }
        }

    def generate_structured_datasets(self) -> Dict[str, Any]:
        """生成结构化数据集"""
        logger.info("生成结构化数据集...")

        datasets = {
            "entities": [asdict(entity) for entity in self.entities.values()],
            "relations": [asdict(relation) for relation in self.relations.values()],
            "escalation_paths": [asdict(path) for path in self.escalation_paths.values()],
            "plot_hooks": [asdict(hook) for hook in self.plot_hooks.values()],
            "scenario_contexts": [asdict(scenario) for scenario in self.scenario_contexts.values()],
            "network_graph": self._generate_network_graph_data(),
            "statistics": self._generate_statistics()
        }

        logger.info("结构化数据集生成完成")
        return datasets

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
                "category": entity.category,
                "domains": entity.domains,
                "importance": entity.importance_level,
                "confidence": entity.confidence_score,
                "size": self._calculate_node_size(entity),
                "color": self._get_node_color(entity.entity_type)
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
                "bidirectional": relation.bidirectional,
                "width": relation.strength * 5,  # 视觉化权重
                "color": self._get_edge_color(relation.relation_type)
            }
            edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "cross_domain_edges": len([e for e in edges if e["is_cross_domain"]]),
                "node_types": list(set([n["type"] for n in nodes])),
                "edge_types": list(set([e["type"] for e in edges]))
            }
        }

    def _calculate_node_size(self, entity: ConflictEntity) -> int:
        """计算节点大小"""
        base_size = 10

        # 基于重要性调整
        importance_multiplier = {
            "极高": 2.0,
            "高": 1.5,
            "中高": 1.3,
            "中": 1.0,
            "低": 0.8
        }

        # 基于连接数调整
        connection_count = len([r for r in self.relations.values()
                               if r.source_entity_id == entity.id or r.target_entity_id == entity.id])
        connection_bonus = min(connection_count * 0.5, 5)

        size = base_size * importance_multiplier.get(entity.importance_level, 1.0) + connection_bonus
        return int(size)

    def _get_node_color(self, entity_type: str) -> str:
        """获取节点颜色"""
        colors = {
            "核心资源": "#FF6B6B",
            "法条制度": "#4ECDC4",
            "关键角色": "#45B7D1",
            "推断实体": "#96CEB4",
            "隐含实体": "#FFEAA7",
            "其他": "#DDA0DD"
        }
        return colors.get(entity_type, "#CCCCCC")

    def _get_edge_color(self, relation_type: str) -> str:
        """获取边颜色"""
        colors = {
            "对立": "#FF4757",
            "竞争": "#FF6348",
            "制约": "#FF7675",
            "依赖": "#00B894",
            "合作": "#00CECA",
            "影响": "#74B9FF",
            "包含": "#A29BFE",
            "衍生": "#FD79A8",
            "替代": "#FDCB6E"
        }
        return colors.get(relation_type, "#95A5A6")

    def _generate_statistics(self) -> Dict[str, Any]:
        """生成统计信息"""
        return {
            "summary": {
                "total_entities": len(self.entities),
                "total_relations": len(self.relations),
                "total_escalation_paths": len(self.escalation_paths),
                "total_plot_hooks": len(self.plot_hooks),
                "total_scenarios": len(self.scenario_contexts)
            },
            "entity_distribution": {
                entity_type: len([e for e in self.entities.values() if e.entity_type == entity_type])
                for entity_type in set([e.entity_type for e in self.entities.values()])
            },
            "relation_distribution": {
                relation_type: len([r for r in self.relations.values() if r.relation_type == relation_type])
                for relation_type in set([r.relation_type for r in self.relations.values()])
            },
            "domain_coverage": {
                domain: len([e for e in self.entities.values() if domain in e.domains])
                for domain in ["人域", "天域", "灵域", "荒域"]
            },
            "confidence_analysis": {
                "high_confidence_entities": len([e for e in self.entities.values() if e.confidence_score >= 0.8]),
                "medium_confidence_entities": len([e for e in self.entities.values() if 0.5 <= e.confidence_score < 0.8]),
                "low_confidence_entities": len([e for e in self.entities.values() if e.confidence_score < 0.5]),
                "avg_entity_confidence": sum([e.confidence_score for e in self.entities.values()]) / len(self.entities) if self.entities else 0,
                "avg_relation_confidence": sum([r.confidence_score for r in self.relations.values()]) / len(self.relations) if self.relations else 0
            }
        }

    def generate_data_dictionary(self) -> Dict[str, Any]:
        """生成数据字典"""
        logger.info("生成数据字典...")

        data_dictionary = {
            "数据模型定义": {
                "ConflictEntity": {
                    "description": "冲突实体数据模型，表示参与冲突的核心要素",
                    "fields": {
                        "id": {"type": "string", "description": "唯一标识符"},
                        "name": {"type": "string", "description": "实体名称"},
                        "entity_type": {"type": "string", "enum": ["核心资源", "法条制度", "关键角色", "推断实体", "隐含实体"], "description": "实体类型"},
                        "domains": {"type": "array", "items": "string", "description": "所属域列表"},
                        "category": {"type": "string", "description": "细分类别"},
                        "description": {"type": "string", "description": "详细描述"},
                        "importance_level": {"type": "string", "enum": ["极高", "高", "中高", "中", "低"], "description": "重要性等级"},
                        "characteristics": {"type": "object", "description": "实体特征属性"},
                        "aliases": {"type": "array", "items": "string", "description": "别名列表"},
                        "source_conflict_pair": {"type": "string", "description": "来源冲突对"},
                        "confidence_score": {"type": "float", "range": "0.0-1.0", "description": "置信度分数"},
                        "extraction_method": {"type": "string", "description": "提取方法"},
                        "created_at": {"type": "string", "format": "ISO 8601", "description": "创建时间"}
                    }
                },
                "ConflictRelation": {
                    "description": "冲突关系数据模型，表示实体间的各种关系",
                    "fields": {
                        "id": {"type": "string", "description": "唯一标识符"},
                        "source_entity_id": {"type": "string", "description": "源实体ID"},
                        "target_entity_id": {"type": "string", "description": "目标实体ID"},
                        "relation_type": {"type": "string", "enum": ["对立", "依赖", "竞争", "制约", "影响", "合作", "替代", "包含", "衍生"], "description": "关系类型"},
                        "description": {"type": "string", "description": "关系描述"},
                        "strength": {"type": "float", "range": "0.0-1.0", "description": "关系强度"},
                        "context": {"type": "string", "description": "关系上下文"},
                        "is_cross_domain": {"type": "boolean", "description": "是否为跨域关系"},
                        "source_domain": {"type": "string", "description": "源域"},
                        "target_domain": {"type": "string", "description": "目标域"},
                        "bidirectional": {"type": "boolean", "description": "是否为双向关系"},
                        "temporal_context": {"type": "string", "description": "时间上下文"},
                        "confidence_score": {"type": "float", "range": "0.0-1.0", "description": "置信度分数"},
                        "detection_method": {"type": "string", "description": "检测方法"},
                        "created_at": {"type": "string", "format": "ISO 8601", "description": "创建时间"}
                    }
                }
            },
            "编码规范": {
                "实体类型编码": {
                    "核心资源": "具体的物质或抽象资源，如税收、矿产、贸易权等",
                    "法条制度": "法律条文、制度规范、仪式规则等",
                    "关键角色": "在冲突中起重要作用的个人或组织",
                    "推断实体": "通过文本分析推断出的实体",
                    "隐含实体": "从描述中暗示的实体"
                },
                "关系类型编码": {
                    "对立": "直接冲突或敌对关系",
                    "依赖": "功能或存在上的依赖关系",
                    "竞争": "争夺相同资源的竞争关系",
                    "制约": "限制或约束关系",
                    "影响": "间接影响关系",
                    "合作": "协作或联盟关系",
                    "替代": "功能可替代关系",
                    "包含": "层级包含关系",
                    "衍生": "演化或派生关系"
                },
                "重要性等级编码": {
                    "极高": "对故事核心情节有决定性影响",
                    "高": "对主要冲突有重要影响",
                    "中高": "对局部冲突有重要影响",
                    "中": "有一定影响但非关键",
                    "低": "影响有限或背景性"
                }
            },
            "质量标准": {
                "置信度标准": {
                    "0.9-1.0": "经过人工验证的高质量数据",
                    "0.7-0.9": "自动分析高置信度结果",
                    "0.5-0.7": "自动分析中等置信度结果",
                    "0.3-0.5": "推断性数据，需要验证",
                    "0.0-0.3": "低置信度数据，可能存在错误"
                },
                "完整性要求": {
                    "必填字段": ["id", "name", "entity_type", "description", "created_at"],
                    "推荐字段": ["domains", "importance_level", "confidence_score"],
                    "可选字段": ["aliases", "characteristics", "source_conflict_pair"]
                }
            }
        }

        logger.info("数据字典生成完成")
        return data_dictionary

    def generate_etl_scripts(self) -> Dict[str, str]:
        """生成ETL处理脚本"""
        logger.info("生成ETL处理脚本...")

        scripts = {
            "postgresql_insert.sql": self._generate_postgresql_insert_script(),
            "data_validation.py": self._generate_validation_script(),
            "data_migration.py": self._generate_migration_script(),
            "batch_processor.py": self._generate_batch_processor_script()
        }

        logger.info("ETL脚本生成完成")
        return scripts

    def _generate_postgresql_insert_script(self) -> str:
        """生成PostgreSQL插入脚本"""
        script = """
-- 冲突要素数据批量插入脚本
-- 生成时间: {timestamp}

BEGIN;

-- 插入文化实体数据
INSERT INTO cultural_entities (
    id, novel_id, name, entity_type, domain_type, dimensions,
    description, characteristics, functions, significance,
    confidence_score, extraction_method, validation_status,
    aliases, tags, created_at, updated_at
) VALUES
""".format(timestamp=datetime.now().isoformat())

        # 生成实体插入语句
        entity_values = []
        for entity in self.entities.values():
            values = f"""(
    '{entity.id}',
    'novel-placeholder-id',
    '{entity.name.replace("'", "''")}',
    '{entity.entity_type}',
    '{entity.domains[0] if entity.domains else "未知"}',
    ARRAY{entity.domains},
    '{entity.description.replace("'", "''")}',
    '{json.dumps(entity.characteristics, ensure_ascii=False).replace("'", "''")}',
    ARRAY['基础功能'],
    '{entity.importance_level}',
    {entity.confidence_score},
    '{entity.extraction_method}',
    'pending',
    ARRAY{entity.aliases},
    ARRAY['auto-extracted'],
    '{entity.created_at}',
    '{entity.created_at}'
)"""
            entity_values.append(values)

        script += ",\n".join(entity_values)
        script += ";\n\n"

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
    'novel-placeholder-id',
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
        script += ";\n\nCOMMIT;\n"

        return script

    def _generate_validation_script(self) -> str:
        """生成数据验证脚本"""
        return '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本
验证冲突要素数据的完整性和一致性
"""

import json
import uuid
from typing import Dict, List, Any

def validate_entities(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """验证实体数据"""
    issues = []
    stats = {"total": len(entities), "by_type": {}}

    for entity in entities:
        # 检查必填字段
        required_fields = ["id", "name", "entity_type", "description"]
        for field in required_fields:
            if not entity.get(field):
                issues.append(f"实体 {entity.get('id', 'unknown')} 缺少必填字段: {field}")

        # 统计类型分布
        entity_type = entity.get("entity_type", "unknown")
        stats["by_type"][entity_type] = stats["by_type"].get(entity_type, 0) + 1

        # 验证ID格式
        try:
            uuid.UUID(entity.get("id", ""))
        except ValueError:
            issues.append(f"实体 {entity.get('id')} ID格式不正确")

    return {"stats": stats, "issues": issues}

def validate_relations(relations: List[Dict[str, Any]], entity_ids: set) -> Dict[str, Any]:
    """验证关系数据"""
    issues = []
    stats = {"total": len(relations), "by_type": {}}

    for relation in relations:
        # 检查实体引用
        source_id = relation.get("source_entity_id")
        target_id = relation.get("target_entity_id")

        if source_id not in entity_ids:
            issues.append(f"关系 {relation.get('id')} 引用不存在的源实体: {source_id}")
        if target_id not in entity_ids:
            issues.append(f"关系 {relation.get('id')} 引用不存在的目标实体: {target_id}")

        # 统计关系类型
        relation_type = relation.get("relation_type", "unknown")
        stats["by_type"][relation_type] = stats["by_type"].get(relation_type, 0) + 1

        # 验证强度范围
        strength = relation.get("strength", 0)
        if not (0 <= strength <= 1):
            issues.append(f"关系 {relation.get('id')} 强度值超出范围[0,1]: {strength}")

    return {"stats": stats, "issues": issues}

def main():
    """主验证函数"""
    print("开始数据验证...")

    # 这里应该加载实际的数据文件
    # 示例代码省略具体加载逻辑

    print("数据验证完成")

if __name__ == "__main__":
    main()
'''

    def _generate_migration_script(self) -> str:
        """生成数据迁移脚本"""
        return '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本
将冲突要素数据迁移到目标数据库
"""

import json
import psycopg2
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConflictDataMigrator:
    """冲突数据迁移器"""

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None

    def connect(self):
        """连接数据库"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def migrate_entities(self, entities: List[Dict[str, Any]]) -> int:
        """迁移实体数据"""
        if not self.connection:
            raise Exception("数据库未连接")

        cursor = self.connection.cursor()
        success_count = 0

        for entity in entities:
            try:
                cursor.execute("""
                    INSERT INTO cultural_entities (
                        id, novel_id, name, entity_type, domain_type,
                        description, confidence_score, extraction_method,
                        validation_status, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    entity["id"],
                    "novel-placeholder-id",  # 需要替换为实际的novel_id
                    entity["name"],
                    entity["entity_type"],
                    entity["domains"][0] if entity["domains"] else None,
                    entity["description"],
                    entity["confidence_score"],
                    entity["extraction_method"],
                    "pending",
                    entity["created_at"],
                    entity["created_at"]
                ))
                success_count += 1

            except Exception as e:
                logger.error(f"插入实体失败 {entity['id']}: {e}")

        self.connection.commit()
        cursor.close()
        logger.info(f"成功迁移 {success_count} 个实体")
        return success_count

    def migrate_relations(self, relations: List[Dict[str, Any]]) -> int:
        """迁移关系数据"""
        if not self.connection:
            raise Exception("数据库未连接")

        cursor = self.connection.cursor()
        success_count = 0

        for relation in relations:
            try:
                cursor.execute("""
                    INSERT INTO cultural_relations (
                        id, novel_id, source_entity_id, target_entity_id,
                        relation_type, description, strength, context,
                        is_cross_domain, confidence_score, detection_method,
                        bidirectional, temporal_context, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO UPDATE SET
                        description = EXCLUDED.description,
                        strength = EXCLUDED.strength,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    relation["id"],
                    "novel-placeholder-id",
                    relation["source_entity_id"],
                    relation["target_entity_id"],
                    relation["relation_type"],
                    relation["description"],
                    relation["strength"],
                    relation["context"],
                    relation["is_cross_domain"],
                    relation["confidence_score"],
                    relation["detection_method"],
                    relation["bidirectional"],
                    relation["temporal_context"],
                    relation["created_at"],
                    relation["created_at"]
                ))
                success_count += 1

            except Exception as e:
                logger.error(f"插入关系失败 {relation['id']}: {e}")

        self.connection.commit()
        cursor.close()
        logger.info(f"成功迁移 {success_count} 个关系")
        return success_count

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")

def main():
    """主迁移函数"""
    # 数据库配置
    db_config = {
        "host": "localhost",
        "database": "novellus",
        "user": "your_username",
        "password": "your_password",
        "port": "5432"
    }

    # 创建迁移器
    migrator = ConflictDataMigrator(db_config)

    try:
        migrator.connect()

        # 加载数据文件
        with open("conflict_elements_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # 执行迁移
        migrator.migrate_entities(data["entities"])
        migrator.migrate_relations(data["relations"])

        logger.info("数据迁移完成")

    except Exception as e:
        logger.error(f"迁移失败: {e}")
    finally:
        migrator.close()

if __name__ == "__main__":
    main()
'''

    def _generate_batch_processor_script(self) -> str:
        """生成批处理脚本"""
        return '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批处理脚本
用于大规模处理冲突要素数据
"""

import json
import asyncio
import aiofiles
from typing import Dict, List, Any
import logging
from concurrent.futures import ThreadPoolExecutor
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConflictDataBatchProcessor:
    """冲突数据批处理器"""

    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_entities_batch(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批处理实体数据"""
        logger.info(f"开始处理 {len(entities)} 个实体的批次")
        start_time = time.time()

        # 并行处理
        tasks = []
        for i in range(0, len(entities), self.batch_size):
            batch = entities[i:i + self.batch_size]
            task = asyncio.create_task(self._process_entity_batch(batch))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # 汇总结果
        total_processed = sum(result["processed"] for result in results)
        total_errors = sum(len(result["errors"]) for result in results)

        processing_time = time.time() - start_time

        logger.info(f"批处理完成: 处理 {total_processed} 个实体，{total_errors} 个错误，耗时 {processing_time:.2f}s")

        return {
            "total_processed": total_processed,
            "total_errors": total_errors,
            "processing_time": processing_time,
            "batches": len(tasks)
        }

    async def _process_entity_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理单个实体批次"""
        processed = 0
        errors = []

        for entity in batch:
            try:
                # 这里添加具体的处理逻辑
                # 例如：数据清洗、验证、转换等
                await self._validate_entity(entity)
                processed += 1

            except Exception as e:
                errors.append(f"实体 {entity.get('id', 'unknown')} 处理失败: {e}")

        return {"processed": processed, "errors": errors}

    async def _validate_entity(self, entity: Dict[str, Any]) -> None:
        """验证单个实体"""
        # 模拟异步验证过程
        await asyncio.sleep(0.01)  # 模拟I/O操作

        # 基本验证
        required_fields = ["id", "name", "entity_type"]
        for field in required_fields:
            if not entity.get(field):
                raise ValueError(f"缺少必填字段: {field}")

    async def export_to_file(self, data: Dict[str, Any], filename: str) -> None:
        """异步导出数据到文件"""
        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(f"数据已导出到: {filename}")

    def close(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)

async def main():
    """主处理函数"""
    processor = ConflictDataBatchProcessor(batch_size=50, max_workers=4)

    try:
        # 加载数据
        with open("conflict_elements_raw.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # 批处理实体
        entity_results = await processor.process_entities_batch(raw_data.get("entities", []))

        # 导出处理结果
        await processor.export_to_file(entity_results, "processing_results.json")

        logger.info("批处理完成")

    except Exception as e:
        logger.error(f"批处理失败: {e}")
    finally:
        processor.close()

if __name__ == "__main__":
    asyncio.run(main())
'''

    def run_complete_extraction(self, input_file: str, output_dir: str = "D:/work/novellus/conflict_extraction_output") -> Dict[str, Any]:
        """运行完整的提取流程"""
        logger.info("开始完整的冲突要素提取流程...")

        # 创建输出目录
        import os
        os.makedirs(output_dir, exist_ok=True)

        # 1. 加载数据
        matrix_data = self.load_conflict_matrix_data(input_file)
        if not matrix_data:
            raise Exception("无法加载冲突矩阵数据")

        # 2. 提取实体
        self.extract_entities_from_matrix(matrix_data)

        # 3. 构建关系网络
        self.build_relationship_network(matrix_data)

        # 4. 构建升级路径
        self.build_escalation_paths(matrix_data)

        # 5. 提取剧情钩子
        self.extract_plot_hooks(matrix_data)

        # 6. 提取场景上下文
        self.extract_scenario_contexts(matrix_data)

        # 7. 数据质量验证
        quality_report = self.validate_data_quality()

        # 8. 生成结构化数据集
        datasets = self.generate_structured_datasets()

        # 9. 生成数据字典
        data_dictionary = self.generate_data_dictionary()

        # 10. 生成ETL脚本
        etl_scripts = self.generate_etl_scripts()

        # 保存所有输出
        output_files = {}

        # 保存主要数据集
        main_output_file = f"{output_dir}/conflict_elements_structured_data.json"
        with open(main_output_file, 'w', encoding='utf-8') as f:
            json.dump(datasets, f, ensure_ascii=False, indent=2)
        output_files["structured_data"] = main_output_file

        # 保存数据字典
        dict_output_file = f"{output_dir}/data_dictionary.json"
        with open(dict_output_file, 'w', encoding='utf-8') as f:
            json.dump(data_dictionary, f, ensure_ascii=False, indent=2)
        output_files["data_dictionary"] = dict_output_file

        # 保存质量报告
        quality_output_file = f"{output_dir}/data_quality_report.json"
        with open(quality_output_file, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)
        output_files["quality_report"] = quality_output_file

        # 保存ETL脚本
        for script_name, script_content in etl_scripts.items():
            script_file = f"{output_dir}/{script_name}"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            output_files[f"etl_{script_name}"] = script_file

        # 生成处理报告
        processing_report = {
            "处理时间": datetime.now().isoformat(),
            "输入文件": input_file,
            "输出目录": output_dir,
            "提取统计": {
                "实体总数": len(self.entities),
                "关系总数": len(self.relations),
                "升级路径总数": len(self.escalation_paths),
                "剧情钩子总数": len(self.plot_hooks),
                "场景总数": len(self.scenario_contexts)
            },
            "数据质量": quality_report,
            "输出文件": output_files
        }

        # 保存处理报告
        report_file = f"{output_dir}/extraction_processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(processing_report, f, ensure_ascii=False, indent=2)
        output_files["processing_report"] = report_file

        logger.info(f"完整提取流程完成，输出保存到: {output_dir}")
        return processing_report

def main():
    """主函数 - 使用示例"""
    extractor = ConflictElementsExtractor()

    try:
        # 运行完整提取流程
        report = extractor.run_complete_extraction(
            input_file="D:/work/novellus/cross_domain_conflict_analysis_report.json"
        )

        print("冲突要素提取完成!")
        print(f"提取统计: {report['提取统计']}")
        print(f"输出目录: {report['输出目录']}")

    except Exception as e:
        logger.error(f"提取过程失败: {e}")
        raise

if __name__ == "__main__":
    main()