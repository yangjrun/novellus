"""
跨域关系分析器 - 分析九域之间的文化交互、冲突和关联
"""

import re
import json
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import logging

from database.models.cultural_framework_models import (
    DomainType, CulturalDimension, EntityType, RelationType,
    CulturalEntityCreate, CulturalRelationCreate
)

logger = logging.getLogger(__name__)


class CrossDomainRelationType(str, Enum):
    """跨域关系类型"""
    TRADE = "贸易往来"
    CONFLICT = "冲突对立"
    ALLIANCE = "联盟合作"
    INFLUENCE = "文化影响"
    MIGRATION = "人口迁移"
    EXCHANGE = "知识交换"
    WORSHIP = "信仰传播"
    CONTROL = "统治关系"
    TRIBUTE = "朝贡关系"
    ISOLATION = "隔离状态"


@dataclass
class CrossDomainRelation:
    """跨域关系"""
    source_domain: DomainType
    target_domain: DomainType
    relation_type: CrossDomainRelationType
    strength: float
    description: str
    evidence: List[str] = field(default_factory=list)
    cultural_dimensions: List[CulturalDimension] = field(default_factory=list)
    entities_involved: List[str] = field(default_factory=list)
    historical_context: Optional[str] = None
    current_status: str = "活跃"


@dataclass
class DomainProfile:
    """域特征画像"""
    domain: DomainType
    core_values: List[str]
    power_structure: str
    economic_model: str
    cultural_traits: List[str]
    strengths: List[str]
    weaknesses: List[str]
    natural_allies: List[DomainType]
    natural_enemies: List[DomainType]


@dataclass
class ConflictPoint:
    """冲突点"""
    domains: Tuple[DomainType, DomainType]
    conflict_type: str
    intensity: float
    root_cause: str
    manifestations: List[str]
    resolution_difficulty: float


@dataclass
class CulturalExchange:
    """文化交流"""
    domains: Tuple[DomainType, DomainType]
    exchange_type: str
    direction: str  # "bidirectional", "source_to_target", "target_to_source"
    content: List[str]
    mechanisms: List[str]
    impact_level: float


class CrossDomainAnalyzer:
    """跨域关系分析器"""

    def __init__(self):
        self.initialize_domain_profiles()
        self.initialize_relationship_patterns()
        self.initialize_conflict_analysis()
        self.initialize_exchange_mechanisms()

    def initialize_domain_profiles(self):
        """初始化域特征画像"""

        self.domain_profiles = {
            DomainType.HUMAN_DOMAIN: DomainProfile(
                domain=DomainType.HUMAN_DOMAIN,
                core_values=["秩序", "传承", "等级", "稳定"],
                power_structure="等级制度",
                economic_model="农业+手工业",
                cultural_traits=["重视血缘", "尊重祖先", "注重规矩"],
                strengths=["组织性强", "稳定性好", "人口众多"],
                weaknesses=["保守固化", "创新不足", "内部分化"],
                natural_allies=[DomainType.HEAVEN_DOMAIN],
                natural_enemies=[DomainType.DEMON_DOMAIN]
            ),

            DomainType.HEAVEN_DOMAIN: DomainProfile(
                domain=DomainType.HEAVEN_DOMAIN,
                core_values=["权威", "天命", "统一", "秩序"],
                power_structure="中央集权",
                economic_model="朝贡体系",
                cultural_traits=["崇尚权威", "重视礼仪", "追求统一"],
                strengths=["政治影响力", "军事实力", "文化辐射"],
                weaknesses=["高高在上", "脱离民众", "官僚腐败"],
                natural_allies=[DomainType.HUMAN_DOMAIN, DomainType.SOURCE_DOMAIN],
                natural_enemies=[DomainType.DEMON_DOMAIN, DomainType.WILD_DOMAIN]
            ),

            DomainType.WILD_DOMAIN: DomainProfile(
                domain=DomainType.WILD_DOMAIN,
                core_values=["自由", "自然", "力量", "野性"],
                power_structure="部落联盟",
                economic_model="狩猎采集",
                cultural_traits=["崇拜自然", "重视力量", "部族忠诚"],
                strengths=["适应性强", "战斗力强", "生存能力"],
                weaknesses=["组织松散", "技术落后", "内部冲突"],
                natural_allies=[DomainType.SEA_DOMAIN],
                natural_enemies=[DomainType.HEAVEN_DOMAIN, DomainType.VOID_DOMAIN]
            ),

            DomainType.UNDERWORLD_DOMAIN: DomainProfile(
                domain=DomainType.UNDERWORLD_DOMAIN,
                core_values=["死亡", "轮回", "审判", "超度"],
                power_structure="冥府体系",
                economic_model="灵魂服务",
                cultural_traits=["敬畏死亡", "相信轮回", "重视仪式"],
                strengths=["神秘力量", "独特地位", "跨域影响"],
                weaknesses=["封闭保守", "缺乏活力", "依赖他域"],
                natural_allies=[DomainType.VOID_DOMAIN, DomainType.SOURCE_DOMAIN],
                natural_enemies=[DomainType.DEMON_DOMAIN]
            ),

            DomainType.DEMON_DOMAIN: DomainProfile(
                domain=DomainType.DEMON_DOMAIN,
                core_values=["力量", "欲望", "征服", "变化"],
                power_structure="强者统治",
                economic_model="掠夺榨取",
                cultural_traits=["崇拜力量", "追求欲望", "无视道德"],
                strengths=["破坏力强", "变化迅速", "个体强大"],
                weaknesses=["内部混乱", "不可持续", "众叛亲离"],
                natural_allies=[],  # 魔域很难有真正的盟友
                natural_enemies=[DomainType.HUMAN_DOMAIN, DomainType.HEAVEN_DOMAIN, DomainType.UNDERWORLD_DOMAIN, DomainType.VOID_DOMAIN]
            ),

            DomainType.VOID_DOMAIN: DomainProfile(
                domain=DomainType.VOID_DOMAIN,
                core_values=["超脱", "虚无", "智慧", "平静"],
                power_structure="贤者治理",
                economic_model="最简需求",
                cultural_traits=["追求超脱", "重视智慧", "淡泊名利"],
                strengths=["精神境界", "智慧深邃", "不易腐败"],
                weaknesses=["脱离现实", "影响力小", "缺乏行动力"],
                natural_allies=[DomainType.UNDERWORLD_DOMAIN, DomainType.SOURCE_DOMAIN],
                natural_enemies=[DomainType.DEMON_DOMAIN, DomainType.WILD_DOMAIN]
            ),

            DomainType.SEA_DOMAIN: DomainProfile(
                domain=DomainType.SEA_DOMAIN,
                core_values=["自由", "冒险", "财富", "交流"],
                power_structure="商会联盟",
                economic_model="海上贸易",
                cultural_traits=["重视财富", "善于交易", "包容开放"],
                strengths=["财富积累", "交通便利", "信息流通"],
                weaknesses=["缺乏深度", "利益至上", "稳定性差"],
                natural_allies=[DomainType.WILD_DOMAIN, DomainType.HUMAN_DOMAIN],
                natural_enemies=[]  # 海域较少与他域产生根本冲突
            ),

            DomainType.SOURCE_DOMAIN: DomainProfile(
                domain=DomainType.SOURCE_DOMAIN,
                core_values=["知识", "传承", "秘密", "起源"],
                power_structure="学者议会",
                economic_model="知识服务",
                cultural_traits=["崇尚知识", "保守秘密", "重视传承"],
                strengths=["知识宝库", "技术先进", "历史悠久"],
                weaknesses=["过于保守", "排外倾向", "实用性差"],
                natural_allies=[DomainType.HEAVEN_DOMAIN, DomainType.VOID_DOMAIN, DomainType.UNDERWORLD_DOMAIN],
                natural_enemies=[]  # 源域通常保持中立
            )
        }

    def initialize_relationship_patterns(self):
        """初始化关系模式"""

        # 关系识别模式
        self.relationship_patterns = {
            CrossDomainRelationType.TRADE: [
                r'(?:贸易|交易|商业|买卖|货物|商品)',
                r'(?:市场|商会|港口|货币|价格)',
                r'(?:出口|进口|运输|航运)'
            ],

            CrossDomainRelationType.CONFLICT: [
                r'(?:冲突|战争|对立|敌对|争斗)',
                r'(?:攻击|侵略|征服|占领|掠夺)',
                r'(?:仇恨|敌视|对抗|反对)'
            ],

            CrossDomainRelationType.ALLIANCE: [
                r'(?:联盟|合作|结盟|协作|同盟)',
                r'(?:友好|友谊|互助|支援|帮助)',
                r'(?:条约|协议|盟约|合约)'
            ],

            CrossDomainRelationType.INFLUENCE: [
                r'(?:影响|感化|传播|扩散|渗透)',
                r'(?:文化|思想|理念|价值观|风俗)',
                r'(?:学习|模仿|采纳|接受)'
            ],

            CrossDomainRelationType.MIGRATION: [
                r'(?:迁移|移民|流动|定居|迁徙)',
                r'(?:人口|族群|民众|百姓|居民)',
                r'(?:避难|逃亡|寻求|前往)'
            ],

            CrossDomainRelationType.EXCHANGE: [
                r'(?:交流|交换|分享|传授|学习)',
                r'(?:知识|技术|经验|秘密|信息)',
                r'(?:研究|探讨|合作|研习)'
            ],

            CrossDomainRelationType.WORSHIP: [
                r'(?:信仰|崇拜|信奉|皈依|祭祀)',
                r'(?:神明|神祇|教义|宗教|教派)',
                r'(?:传教|布道|传播|扩展)'
            ],

            CrossDomainRelationType.CONTROL: [
                r'(?:统治|控制|管辖|治理|支配)',
                r'(?:征服|占领|吞并|统一|收复)',
                r'(?:属国|附庸|从属|臣服)'
            ],

            CrossDomainRelationType.TRIBUTE: [
                r'(?:朝贡|进贡|贡品|朝觐|朝拜)',
                r'(?:册封|封赏|赏赐|恩典)',
                r'(?:宗主|附属|从属|臣属)'
            ],

            CrossDomainRelationType.ISOLATION: [
                r'(?:隔离|孤立|封闭|闭关|断绝)',
                r'(?:禁止|限制|阻止|防范)',
                r'(?:边界|壁垒|屏障|阻隔)'
            ]
        }

    def initialize_conflict_analysis(self):
        """初始化冲突分析"""

        # 已知的冲突模式
        self.known_conflicts = {
            (DomainType.HUMAN_DOMAIN, DomainType.DEMON_DOMAIN): {
                "type": "价值观冲突",
                "intensity": 0.9,
                "root_cause": "秩序与混乱的根本对立",
                "manifestations": ["魔化事件", "血契传播", "传统破坏"],
                "resolution_difficulty": 0.95
            },

            (DomainType.HEAVEN_DOMAIN, DomainType.WILD_DOMAIN): {
                "type": "政治冲突",
                "intensity": 0.7,
                "root_cause": "中央集权与部落自治的矛盾",
                "manifestations": ["征服战争", "反抗起义", "文化压制"],
                "resolution_difficulty": 0.8
            },

            (DomainType.VOID_DOMAIN, DomainType.DEMON_DOMAIN): {
                "type": "哲学冲突",
                "intensity": 0.8,
                "root_cause": "超脱与欲望的对立",
                "manifestations": ["教义辩论", "信徒争夺", "理念对抗"],
                "resolution_difficulty": 0.9
            },

            (DomainType.SOURCE_DOMAIN, DomainType.SEA_DOMAIN): {
                "type": "利益冲突",
                "intensity": 0.4,
                "root_cause": "知识保护与信息流通的矛盾",
                "manifestations": ["知识封锁", "信息泄露", "技术争夺"],
                "resolution_difficulty": 0.5
            }
        }

    def initialize_exchange_mechanisms(self):
        """初始化交流机制"""

        self.exchange_mechanisms = {
            "贸易往来": ["商队", "港口", "市场", "货币", "商会"],
            "人员流动": ["移民", "使节", "学者", "工匠", "商人"],
            "文化传播": ["书籍", "艺术", "语言", "习俗", "节庆"],
            "技术交流": ["工艺", "法术", "秘技", "设备", "知识"],
            "宗教传播": ["传教士", "教义", "仪式", "圣物", "神庙"],
            "政治互动": ["联盟", "条约", "朝贡", "外交", "战争"]
        }

    def analyze_cross_domain_relationships(self, text: str, entities: List[CulturalEntityCreate]) -> Dict[str, Any]:
        """分析跨域关系"""
        logger.info("开始跨域关系分析")

        # 1. 识别域提及
        domain_mentions = self._identify_domain_mentions(text)

        # 2. 提取跨域关系
        cross_relations = self._extract_cross_domain_relations(text, domain_mentions)

        # 3. 分析冲突点
        conflicts = self._analyze_conflicts(text, cross_relations)

        # 4. 分析文化交流
        exchanges = self._analyze_cultural_exchanges(text, cross_relations)

        # 5. 构建关系网络
        relationship_network = self._build_relationship_network(cross_relations)

        # 6. 生成影响分析
        impact_analysis = self._analyze_cross_domain_impacts(cross_relations, entities)

        # 7. 预测潜在关系
        potential_relations = self._predict_potential_relationships(cross_relations, conflicts, exchanges)

        result = {
            "domain_mentions": domain_mentions,
            "cross_domain_relations": cross_relations,
            "conflict_points": conflicts,
            "cultural_exchanges": exchanges,
            "relationship_network": relationship_network,
            "impact_analysis": impact_analysis,
            "potential_relations": potential_relations,
            "analysis_summary": self._generate_analysis_summary(cross_relations, conflicts, exchanges)
        }

        logger.info(f"跨域关系分析完成，发现 {len(cross_relations)} 个关系")
        return result

    def _identify_domain_mentions(self, text: str) -> Dict[DomainType, List[Tuple[int, int, str]]]:
        """识别域提及"""
        mentions = defaultdict(list)

        for domain in DomainType:
            domain_name = domain.value

            # 直接域名提及
            pattern = rf'{domain_name}(?:[的之]|(?=\s))'
            matches = re.finditer(pattern, text)

            for match in matches:
                context = text[max(0, match.start()-50):match.end()+50]
                mentions[domain].append((match.start(), match.end(), context))

            # 域特征实体提及
            if domain in self.domain_profiles:
                profile = self.domain_profiles[domain]
                signature_entities = [
                    "天命王朝", "祭司议会", "冥司殿", "守源会", "血契", "虚空", "港市", "源流"
                ]

                for entity in signature_entities:
                    if entity in text:
                        entity_matches = re.finditer(re.escape(entity), text)
                        for match in entity_matches:
                            context = text[max(0, match.start()-50):match.end()+50]
                            mentions[domain].append((match.start(), match.end(), context))

        return dict(mentions)

    def _extract_cross_domain_relations(self, text: str, domain_mentions: Dict[DomainType, List[Tuple[int, int, str]]]) -> List[CrossDomainRelation]:
        """提取跨域关系"""
        relations = []

        # 寻找域对共现
        domain_pairs = []
        domains = list(domain_mentions.keys())

        for i, domain1 in enumerate(domains):
            for domain2 in domains[i+1:]:
                # 检查两个域是否在相近位置被提及
                for pos1, end1, context1 in domain_mentions[domain1]:
                    for pos2, end2, context2 in domain_mentions[domain2]:
                        distance = abs(pos1 - pos2)
                        if distance < 200:  # 距离阈值
                            domain_pairs.append((domain1, domain2, pos1, pos2, min(pos1, pos2), max(end1, end2)))

        # 分析每个域对的关系
        for domain1, domain2, pos1, pos2, start, end in domain_pairs:
            context = text[max(0, start-100):min(len(text), end+100)]

            # 识别关系类型
            relation_types = self._identify_relation_types(context)

            for relation_type, confidence in relation_types:
                # 提取证据
                evidence = self._extract_relation_evidence(context, relation_type)

                # 识别涉及的文化维度
                dimensions = self._identify_cultural_dimensions_in_relation(context)

                # 提取相关实体
                entities_involved = self._extract_entities_in_context(context)

                relation = CrossDomainRelation(
                    source_domain=domain1,
                    target_domain=domain2,
                    relation_type=relation_type,
                    strength=confidence,
                    description=self._generate_relation_description(domain1, domain2, relation_type),
                    evidence=evidence,
                    cultural_dimensions=dimensions,
                    entities_involved=entities_involved,
                    historical_context=self._extract_historical_context(context),
                    current_status=self._determine_relation_status(context)
                )

                relations.append(relation)

        return relations

    def _identify_relation_types(self, context: str) -> List[Tuple[CrossDomainRelationType, float]]:
        """识别关系类型"""
        relation_scores = {}

        for relation_type, patterns in self.relationship_patterns.items():
            score = 0
            for pattern_list in patterns:
                if isinstance(pattern_list, list):
                    for pattern in pattern_list:
                        if re.search(pattern, context, re.IGNORECASE):
                            score += 1
                else:
                    if re.search(pattern_list, context, re.IGNORECASE):
                        score += 1

            if score > 0:
                confidence = min(score / len(patterns), 1.0)
                relation_scores[relation_type] = confidence

        # 返回得分最高的关系类型
        if relation_scores:
            sorted_relations = sorted(relation_scores.items(), key=lambda x: x[1], reverse=True)
            return sorted_relations[:2]  # 返回前两个最可能的关系

        return [(CrossDomainRelationType.INFLUENCE, 0.3)]  # 默认关系

    def _extract_relation_evidence(self, context: str, relation_type: CrossDomainRelationType) -> List[str]:
        """提取关系证据"""
        evidence = []

        # 提取关键句子作为证据
        sentences = re.split(r'[。！？]', context)
        patterns = self.relationship_patterns.get(relation_type, [])

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            for pattern_list in patterns:
                if isinstance(pattern_list, list):
                    for pattern in pattern_list:
                        if re.search(pattern, sentence, re.IGNORECASE):
                            evidence.append(sentence)
                            break
                else:
                    if re.search(pattern_list, sentence, re.IGNORECASE):
                        evidence.append(sentence)

        return evidence[:3]  # 限制证据数量

    def _identify_cultural_dimensions_in_relation(self, context: str) -> List[CulturalDimension]:
        """识别关系中的文化维度"""
        dimensions = []

        dimension_keywords = {
            CulturalDimension.MYTHOLOGY_RELIGION: ["信仰", "神", "祭祀", "宗教", "神话", "仪式"],
            CulturalDimension.POWER_LAW: ["权力", "法律", "政治", "统治", "法则", "制度"],
            CulturalDimension.ECONOMY_TECHNOLOGY: ["经济", "技术", "货币", "工艺", "贸易", "商业"],
            CulturalDimension.FAMILY_EDUCATION: ["家庭", "教育", "婚姻", "血缘", "传承", "学习"],
            CulturalDimension.RITUAL_DAILY: ["仪式", "日常", "习俗", "节日", "礼仪", "生活"],
            CulturalDimension.ART_ENTERTAINMENT: ["艺术", "娱乐", "美学", "竞技", "表演", "文艺"]
        }

        for dimension, keywords in dimension_keywords.items():
            if any(keyword in context for keyword in keywords):
                dimensions.append(dimension)

        return dimensions

    def _extract_entities_in_context(self, context: str) -> List[str]:
        """提取上下文中的实体"""
        entities = []

        # 简化的实体提取
        entity_patterns = [
            r'([^，。！？\s]{2,8}(?:王朝|议会|殿|会|宗|门|派|府|司))',
            r'([^，。！？\s]{2,8}(?:票|器|盘|珠|石|符|印|镜))',
            r'([^，。！？\s]{2,8}(?:礼|节|夜|月|典|仪|祭|庆))',
        ]

        for pattern in entity_patterns:
            matches = re.findall(pattern, context)
            entities.extend(matches)

        return list(set(entities))[:5]  # 去重并限制数量

    def _extract_historical_context(self, context: str) -> Optional[str]:
        """提取历史背景"""
        historical_indicators = ["历史上", "古代", "过去", "传统", "历来", "自古"]

        for indicator in historical_indicators:
            if indicator in context:
                # 提取包含历史指示词的句子
                sentences = re.split(r'[。！？]', context)
                for sentence in sentences:
                    if indicator in sentence and len(sentence.strip()) > 10:
                        return sentence.strip()

        return None

    def _determine_relation_status(self, context: str) -> str:
        """确定关系状态"""
        status_indicators = {
            "活跃": ["目前", "现在", "当前", "正在", "持续"],
            "衰落": ["曾经", "过去", "已经", "不再", "衰落"],
            "潜在": ["可能", "或许", "有望", "潜在", "未来"],
            "中断": ["中断", "停止", "终止", "断绝", "破裂"]
        }

        for status, indicators in status_indicators.items():
            if any(indicator in context for indicator in indicators):
                return status

        return "未知"

    def _generate_relation_description(self, domain1: DomainType, domain2: DomainType, relation_type: CrossDomainRelationType) -> str:
        """生成关系描述"""
        templates = {
            CrossDomainRelationType.TRADE: f"{domain1.value}与{domain2.value}之间存在贸易往来关系",
            CrossDomainRelationType.CONFLICT: f"{domain1.value}与{domain2.value}之间存在冲突对立关系",
            CrossDomainRelationType.ALLIANCE: f"{domain1.value}与{domain2.value}之间建立了联盟合作关系",
            CrossDomainRelationType.INFLUENCE: f"{domain1.value}对{domain2.value}产生了文化影响",
            CrossDomainRelationType.MIGRATION: f"存在从{domain1.value}到{domain2.value}的人口迁移",
            CrossDomainRelationType.EXCHANGE: f"{domain1.value}与{domain2.value}进行知识技术交流",
            CrossDomainRelationType.WORSHIP: f"{domain2.value}的信仰在{domain1.value}中传播",
            CrossDomainRelationType.CONTROL: f"{domain1.value}对{domain2.value}实施统治控制",
            CrossDomainRelationType.TRIBUTE: f"{domain2.value}向{domain1.value}进行朝贡",
            CrossDomainRelationType.ISOLATION: f"{domain1.value}与{domain2.value}之间保持隔离状态"
        }

        return templates.get(relation_type, f"{domain1.value}与{domain2.value}存在某种关联")

    def _analyze_conflicts(self, text: str, relations: List[CrossDomainRelation]) -> List[ConflictPoint]:
        """分析冲突点"""
        conflicts = []

        # 基于已知冲突模式
        for (domain1, domain2), conflict_info in self.known_conflicts.items():
            conflict = ConflictPoint(
                domains=(domain1, domain2),
                conflict_type=conflict_info["type"],
                intensity=conflict_info["intensity"],
                root_cause=conflict_info["root_cause"],
                manifestations=conflict_info["manifestations"],
                resolution_difficulty=conflict_info["resolution_difficulty"]
            )
            conflicts.append(conflict)

        # 从关系中识别新的冲突
        conflict_relations = [r for r in relations if r.relation_type == CrossDomainRelationType.CONFLICT]

        for relation in conflict_relations:
            # 检查是否已存在
            existing = any(
                set([relation.source_domain, relation.target_domain]) == set(conflict.domains)
                for conflict in conflicts
            )

            if not existing:
                conflict = ConflictPoint(
                    domains=(relation.source_domain, relation.target_domain),
                    conflict_type="新发现冲突",
                    intensity=relation.strength,
                    root_cause="需要进一步分析",
                    manifestations=relation.evidence,
                    resolution_difficulty=0.6
                )
                conflicts.append(conflict)

        return conflicts

    def _analyze_cultural_exchanges(self, text: str, relations: List[CrossDomainRelation]) -> List[CulturalExchange]:
        """分析文化交流"""
        exchanges = []

        exchange_relations = [
            r for r in relations
            if r.relation_type in [CrossDomainRelationType.EXCHANGE, CrossDomainRelationType.INFLUENCE,
                                 CrossDomainRelationType.TRADE, CrossDomainRelationType.WORSHIP]
        ]

        for relation in exchange_relations:
            # 确定交流方向
            direction = "bidirectional"
            if relation.relation_type == CrossDomainRelationType.INFLUENCE:
                direction = "source_to_target"
            elif relation.relation_type == CrossDomainRelationType.WORSHIP:
                direction = "target_to_source"

            # 确定交流内容
            content = self._determine_exchange_content(relation)

            # 确定交流机制
            mechanisms = self._determine_exchange_mechanisms(relation)

            exchange = CulturalExchange(
                domains=(relation.source_domain, relation.target_domain),
                exchange_type=relation.relation_type.value,
                direction=direction,
                content=content,
                mechanisms=mechanisms,
                impact_level=relation.strength
            )

            exchanges.append(exchange)

        return exchanges

    def _determine_exchange_content(self, relation: CrossDomainRelation) -> List[str]:
        """确定交流内容"""
        content_map = {
            CrossDomainRelationType.TRADE: ["商品", "货币", "贸易技术"],
            CrossDomainRelationType.EXCHANGE: ["知识", "技术", "经验"],
            CrossDomainRelationType.INFLUENCE: ["价值观", "制度", "文化习俗"],
            CrossDomainRelationType.WORSHIP: ["宗教教义", "仪式", "信仰体系"]
        }

        base_content = content_map.get(relation.relation_type, ["文化元素"])

        # 基于文化维度添加内容
        dimension_content = {
            CulturalDimension.MYTHOLOGY_RELIGION: ["神话传说", "宗教仪式"],
            CulturalDimension.POWER_LAW: ["政治制度", "法律体系"],
            CulturalDimension.ECONOMY_TECHNOLOGY: ["经济模式", "技术工艺"],
            CulturalDimension.FAMILY_EDUCATION: ["教育方式", "家庭观念"],
            CulturalDimension.RITUAL_DAILY: ["生活习俗", "日常仪式"],
            CulturalDimension.ART_ENTERTAINMENT: ["艺术形式", "娱乐活动"]
        }

        for dimension in relation.cultural_dimensions:
            if dimension in dimension_content:
                base_content.extend(dimension_content[dimension])

        return list(set(base_content))

    def _determine_exchange_mechanisms(self, relation: CrossDomainRelation) -> List[str]:
        """确定交流机制"""
        mechanism_map = {
            CrossDomainRelationType.TRADE: ["商队", "市场", "港口"],
            CrossDomainRelationType.EXCHANGE: ["学者访问", "技术传授", "书籍传播"],
            CrossDomainRelationType.INFLUENCE: ["文化渗透", "制度模仿", "人员流动"],
            CrossDomainRelationType.WORSHIP: ["传教活动", "宗教节庆", "圣地朝拜"]
        }

        return mechanism_map.get(relation.relation_type, ["未知机制"])

    def _build_relationship_network(self, relations: List[CrossDomainRelation]) -> Dict[str, Any]:
        """构建关系网络"""
        network = {
            "nodes": [],
            "edges": [],
            "clusters": [],
            "central_domains": []
        }

        # 节点（域）
        domains = set()
        for relation in relations:
            domains.add(relation.source_domain)
            domains.add(relation.target_domain)

        for domain in domains:
            profile = self.domain_profiles.get(domain)
            node = {
                "id": domain.value,
                "domain": domain,
                "type": "domain",
                "size": len([r for r in relations if domain in [r.source_domain, r.target_domain]]),
                "attributes": {
                    "core_values": profile.core_values if profile else [],
                    "power_structure": profile.power_structure if profile else "未知"
                }
            }
            network["nodes"].append(node)

        # 边（关系）
        for i, relation in enumerate(relations):
            edge = {
                "id": f"relation_{i}",
                "source": relation.source_domain.value,
                "target": relation.target_domain.value,
                "type": relation.relation_type.value,
                "weight": relation.strength,
                "attributes": {
                    "description": relation.description,
                    "evidence_count": len(relation.evidence),
                    "status": relation.current_status
                }
            }
            network["edges"].append(edge)

        # 计算中心域
        domain_degrees = Counter()
        for relation in relations:
            domain_degrees[relation.source_domain] += 1
            domain_degrees[relation.target_domain] += 1

        network["central_domains"] = [
            domain.value for domain, degree in domain_degrees.most_common(3)
        ]

        return network

    def _analyze_cross_domain_impacts(self, relations: List[CrossDomainRelation], entities: List[CulturalEntityCreate]) -> Dict[str, Any]:
        """分析跨域影响"""
        impacts = {
            "domain_influences": {},
            "entity_impacts": {},
            "cultural_diffusion": {},
            "power_shifts": {}
        }

        # 分析域影响力
        for domain in DomainType:
            influence_score = 0
            influenced_score = 0

            for relation in relations:
                if relation.source_domain == domain:
                    influence_score += relation.strength
                if relation.target_domain == domain:
                    influenced_score += relation.strength

            impacts["domain_influences"][domain.value] = {
                "influence_out": influence_score,
                "influence_in": influenced_score,
                "net_influence": influence_score - influenced_score
            }

        # 分析实体影响
        domain_entities = defaultdict(list)
        for entity in entities:
            if entity.domain_type:
                domain_entities[entity.domain_type].append(entity)

        for domain, domain_entity_list in domain_entities.items():
            cross_domain_count = sum(
                1 for relation in relations
                if domain in [relation.source_domain, relation.target_domain]
            )

            impacts["entity_impacts"][domain.value] = {
                "entity_count": len(domain_entity_list),
                "cross_relations": cross_domain_count,
                "exposure_ratio": cross_domain_count / len(domain_entity_list) if domain_entity_list else 0
            }

        return impacts

    def _predict_potential_relationships(self, relations: List[CrossDomainRelation], conflicts: List[ConflictPoint], exchanges: List[CulturalExchange]) -> List[Dict[str, Any]]:
        """预测潜在关系"""
        potential = []

        existing_pairs = set()
        for relation in relations:
            existing_pairs.add((relation.source_domain, relation.target_domain))
            existing_pairs.add((relation.target_domain, relation.source_domain))

        # 基于域特征预测
        for domain1 in DomainType:
            for domain2 in DomainType:
                if domain1 == domain2 or (domain1, domain2) in existing_pairs:
                    continue

                profile1 = self.domain_profiles.get(domain1)
                profile2 = self.domain_profiles.get(domain2)

                if not profile1 or not profile2:
                    continue

                # 预测联盟可能性
                if domain2 in profile1.natural_allies or domain1 in profile2.natural_allies:
                    potential.append({
                        "domains": (domain1.value, domain2.value),
                        "predicted_type": "联盟合作",
                        "probability": 0.7,
                        "reasoning": "域特征匹配，价值观相近"
                    })

                # 预测冲突可能性
                if domain2 in profile1.natural_enemies or domain1 in profile2.natural_enemies:
                    potential.append({
                        "domains": (domain1.value, domain2.value),
                        "predicted_type": "潜在冲突",
                        "probability": 0.6,
                        "reasoning": "域特征对立，价值观冲突"
                    })

        return potential[:10]  # 返回前10个预测

    def _generate_analysis_summary(self, relations: List[CrossDomainRelation], conflicts: List[ConflictPoint], exchanges: List[CulturalExchange]) -> str:
        """生成分析摘要"""
        total_relations = len(relations)
        conflict_count = len(conflicts)
        exchange_count = len(exchanges)

        # 统计关系类型
        relation_types = Counter(r.relation_type.value for r in relations)
        most_common_type = relation_types.most_common(1)[0] if relation_types else ("无", 0)

        # 最活跃的域
        domain_activity = Counter()
        for relation in relations:
            domain_activity[relation.source_domain.value] += 1
            domain_activity[relation.target_domain.value] += 1

        most_active_domain = domain_activity.most_common(1)[0] if domain_activity else ("无", 0)

        summary = f"""
九域跨域关系分析摘要：

总体情况：
- 发现跨域关系 {total_relations} 个
- 识别冲突点 {conflict_count} 个
- 发现文化交流 {exchange_count} 个

关系特征：
- 最常见关系类型：{most_common_type[0]} ({most_common_type[1]} 个)
- 最活跃域：{most_active_domain[0]} (参与 {most_active_domain[1]} 个关系)

主要发现：
- {"存在多个高强度冲突，需要重点关注" if any(c.intensity > 0.8 for c in conflicts) else "整体关系相对稳定"}
- {"文化交流活跃，促进域间融合" if exchange_count > 3 else "文化交流有限，域间相对独立"}
- {"关系网络复杂，影响深远" if total_relations > 5 else "关系网络简单，影响局限"}
        """.strip()

        return summary