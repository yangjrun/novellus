"""
九域特定实体提取器 - 专门针对"裂世九域·法则链纪元"的实体识别和提取
"""

import re
import json
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..database.models.cultural_framework_models import DomainType, EntityType

logger = logging.getLogger(__name__)


@dataclass
class ExtractionRule:
    """提取规则"""
    name: str
    patterns: List[str]
    entity_type: EntityType
    domain_specific: Optional[DomainType] = None
    confidence_boost: float = 0.0
    context_requirements: List[str] = field(default_factory=list)
    exclusion_patterns: List[str] = field(default_factory=list)


@dataclass
class ExtractedEntity:
    """提取的实体"""
    text: str
    entity_type: EntityType
    domain: Optional[DomainType]
    confidence: float
    position: Tuple[int, int]
    context: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    extraction_rule: str = ""


class NineDomainsEntityExtractor:
    """九域实体提取器"""

    def __init__(self):
        self.initialize_domain_rules()
        self.initialize_entity_rules()
        self.initialize_validation_rules()

    def initialize_domain_rules(self):
        """初始化域特定规则"""

        self.domain_specific_rules = {
            DomainType.HUMAN_DOMAIN: {
                "signature_entities": ["链籍", "环祖", "乡祭", "缚司", "县府", "宗门驻坊"],
                "hierarchy_markers": ["黄籍", "灰籍", "黑籍", "良籍", "苦役", "罪籍"],
                "institutions": ["县府", "宗门", "缚司", "巡链司"],
                "cultural_items": ["链票", "环印", "家谱"],
                "rituals": ["归环礼", "拾链礼", "祖灵续籍祭"],
                "forbidden_terms": ["魔祭", "血池", "虚空", "噬魂"]
            },

            DomainType.HEAVEN_DOMAIN: {
                "signature_entities": ["天命王朝", "龙阙", "司天监", "御史台"],
                "hierarchy_markers": ["王侯", "世家", "官品", "天命"],
                "institutions": ["王朝", "朝廷", "官府", "御史台"],
                "cultural_items": ["龙印", "天符", "诏书"],
                "rituals": ["登基大典", "天祭", "朝会"],
                "forbidden_terms": ["血契", "魔化", "野性"]
            },

            DomainType.WILD_DOMAIN: {
                "signature_entities": ["野人", "萨满", "图腾", "部落", "长老"],
                "hierarchy_markers": ["族长", "萨满", "猎手", "勇士"],
                "institutions": ["部落", "萨满会", "长老院"],
                "cultural_items": ["图腾", "骨器", "兽皮"],
                "rituals": ["成人礼", "狩猎祭", "图腾祭"],
                "forbidden_terms": ["链籍", "官府", "文书"]
            },

            DomainType.UNDERWORLD_DOMAIN: {
                "signature_entities": ["冥司殿", "渡链僧", "镇魂器", "冥籍", "阴兵"],
                "hierarchy_markers": ["冥官", "渡僧", "守魂", "引路"],
                "institutions": ["冥司殿", "冥府", "渡魂院"],
                "cultural_items": ["镇魂器", "冥籍", "渡魂珠", "归环文"],
                "rituals": ["超度仪", "引魂礼", "冥祭"],
                "forbidden_terms": ["血契", "魔化", "活人"]
            },

            DomainType.DEMON_DOMAIN: {
                "signature_entities": ["血契", "魔祭", "噬魂", "血池", "魔典"],
                "hierarchy_markers": ["魔主", "血仆", "祭品", "堕落者"],
                "institutions": ["血殿", "魔教", "噬魂会"],
                "cultural_items": ["血契", "魔典", "噬魂器", "血符"],
                "rituals": ["血祭", "魔化仪", "献祭典"],
                "forbidden_terms": ["环祖", "归环", "净化"]
            },

            DomainType.VOID_DOMAIN: {
                "signature_entities": ["虚空", "无为", "空明", "超脱", "道境"],
                "hierarchy_markers": ["悟者", "空修", "虚行", "道人"],
                "institutions": ["虚观", "空门", "道院"],
                "cultural_items": ["空明珠", "虚道经", "无为印"],
                "rituals": ["悟道会", "虚空祭", "超脱仪"],
                "forbidden_terms": ["血肉", "欲望", "执着"]
            },

            DomainType.SEA_DOMAIN: {
                "signature_entities": ["港市", "商会", "航海", "岛屿", "潮汐"],
                "hierarchy_markers": ["船长", "商主", "水手", "岛主"],
                "institutions": ["商会", "港务", "船帮"],
                "cultural_items": ["航海图", "潮汐表", "海图"],
                "rituals": ["下水礼", "祭海神", "丰收节"],
                "forbidden_terms": ["内陆", "山民", "旱地"]
            },

            DomainType.SOURCE_DOMAIN: {
                "signature_entities": ["守源会", "源流", "古籍", "秘典", "源力"],
                "hierarchy_markers": ["源师", "典守", "研习者", "守秘"],
                "institutions": ["守源会", "典藏阁", "源学院"],
                "cultural_items": ["古籍", "秘典", "源石", "源符"],
                "rituals": ["传承礼", "启源仪", "守秘誓"],
                "forbidden_terms": ["破坏", "亵渎", "泄露"]
            }
        }

    def initialize_entity_rules(self):
        """初始化实体提取规则"""

        self.extraction_rules = [
            # 组织机构规则
            ExtractionRule(
                name="standard_organizations",
                patterns=[
                    r'([^，。！？\s]{2,8}(?:王朝|议会|殿|会|宗|门|派|府|司|院|堂|社|团|联盟|组织))',
                    r'([^，。！？\s]{2,6}(?:坊|寺|观|庙|祠|阁|楼|台))',
                ],
                entity_type=EntityType.ORGANIZATION,
                confidence_boost=0.2
            ),

            ExtractionRule(
                name="named_organizations",
                patterns=[
                    r'(天命王朝|祭司议会|冥司殿|守源会|巡链司|缚司|县府)',
                    r'(司天监|御史台|血殿|魔教|虚观|空门|商会|港务)',
                ],
                entity_type=EntityType.ORGANIZATION,
                confidence_boost=0.4
            ),

            # 重要概念规则
            ExtractionRule(
                name="core_concepts",
                patterns=[
                    r'(法则链|链籍|断链术|环印|裂世|九域)',
                    r'([^，。！？\s]{2,8}(?:法则|链|术|功|诀|道|理|法|式|制))',
                ],
                entity_type=EntityType.CONCEPT,
                confidence_boost=0.3
            ),

            ExtractionRule(
                name="hierarchy_systems",
                patterns=[
                    r'(三等制|师承制|血契制)',
                    r'(黄籍|灰籍|黑籍|良籍|苦役|罪籍)',
                    r'([^，。！？\s]{2,6}(?:籍|等|级|品|阶))',
                ],
                entity_type=EntityType.SYSTEM,
                confidence_boost=0.3
            ),

            # 文化物品规则
            ExtractionRule(
                name="cultural_items",
                patterns=[
                    r'(链票|镇魂器|稳乱器|回响盘|环印|链籍)',
                    r'([^，。！？\s]{2,8}(?:票|器|盘|珠|石|符|印|镜|册|书|卷|典))',
                    r'([^，。！？\s]{2,6}(?:剑|刀|锤|杖|袍|冠|玉|宝))',
                ],
                entity_type=EntityType.ITEM,
                confidence_boost=0.2
            ),

            # 仪式活动规则
            ExtractionRule(
                name="rituals_ceremonies",
                patterns=[
                    r'(裂世夜|归环礼|狂环月|拾链礼|链诞节|断链仪)',
                    r'([^，。！？\s]{2,8}(?:礼|节|夜|月|典|仪|祭|庆|会))',
                    r'([^，。！？\s]{2,6}(?:祭|祀|拜|诵|奠|葬))',
                ],
                entity_type=EntityType.RITUAL,
                confidence_boost=0.2
            ),

            # 货币体系规则
            ExtractionRule(
                name="currency_systems",
                patterns=[
                    r'(环币|链金|法则晶|灵石)',
                    r'([^，。！？\s]{2,8}(?:币|钱|金|银|铜|晶|石|珠))',
                ],
                entity_type=EntityType.CURRENCY,
                confidence_boost=0.2
            ),

            # 技术工艺规则
            ExtractionRule(
                name="technologies",
                patterns=[
                    r'(锻链术|环铸法|法则工艺|链接技术)',
                    r'([^，。！？\s]{2,8}(?:技|工艺|法|术|学|道|艺))',
                ],
                entity_type=EntityType.TECHNOLOGY,
                confidence_boost=0.2
            ),

            # 信仰体系规则
            ExtractionRule(
                name="belief_systems",
                patterns=[
                    r'([^，。！？\s]{2,8}(?:信仰|信条|教义|神话|传说))',
                    r'(环祖信仰|天命观|虚无道|血契誓)',
                ],
                entity_type=EntityType.BELIEF,
                confidence_boost=0.2
            ),

            # 习俗传统规则
            ExtractionRule(
                name="customs_traditions",
                patterns=[
                    r'([^，。！？\s]{2,8}(?:习俗|传统|风俗|惯例|规矩))',
                    r'(祖灵续籍|家谱传承|血脉认定)',
                ],
                entity_type=EntityType.CUSTOM,
                confidence_boost=0.2
            ),
        ]

        # 域特定规则
        for domain, domain_info in self.domain_specific_rules.items():
            # 为每个域创建特定的提取规则
            signature_pattern = '|'.join(re.escape(entity) for entity in domain_info["signature_entities"])
            if signature_pattern:
                rule = ExtractionRule(
                    name=f"{domain.value}_signature_entities",
                    patterns=[f'({signature_pattern})'],
                    entity_type=EntityType.ORGANIZATION,
                    domain_specific=domain,
                    confidence_boost=0.5
                )
                self.extraction_rules.append(rule)

    def initialize_validation_rules(self):
        """初始化验证规则"""

        self.validation_rules = {
            "min_length": 2,
            "max_length": 20,
            "forbidden_chars": ['/', '\\', '|', '<', '>', '*', '?'],
            "required_context_window": 20,
        }

        # 排除模式
        self.exclusion_patterns = [
            r'^[0-9]+$',  # 纯数字
            r'^[a-zA-Z]+$',  # 纯英文
            r'^[一二三四五六七八九十]+$',  # 纯中文数字
            r'^[的了在是我有和就不人都一上也很到说要去你会着没有看好自己这]+$',  # 常见停用词
        ]

    def extract_entities(self, text: str, target_domain: Optional[DomainType] = None) -> List[ExtractedEntity]:
        """提取实体"""
        entities = []
        text_length = len(text)

        # 预处理文本
        cleaned_text = self._preprocess_text(text)

        # 应用提取规则
        for rule in self.extraction_rules:
            # 如果指定了目标域，跳过不匹配的域特定规则
            if target_domain and rule.domain_specific and rule.domain_specific != target_domain:
                continue

            rule_entities = self._apply_extraction_rule(cleaned_text, rule, target_domain)
            entities.extend(rule_entities)

        # 去重和验证
        entities = self._deduplicate_entities(entities)
        entities = self._validate_entities(entities, cleaned_text)

        # 后处理
        entities = self._post_process_entities(entities, cleaned_text, target_domain)

        logger.info(f"提取到 {len(entities)} 个实体")
        return entities

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)

        # 修复常见的OCR错误（如果需要）
        replacements = {
            '链铬': '链籍',
            '环祀': '环祖',
            '冥司股': '冥司殿',
        }

        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)

        return text

    def _apply_extraction_rule(self, text: str, rule: ExtractionRule, target_domain: Optional[DomainType]) -> List[ExtractedEntity]:
        """应用提取规则"""
        entities = []

        for pattern in rule.patterns:
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    entity_text = match.group(1).strip()

                    # 基础验证
                    if not self._is_valid_entity_text(entity_text):
                        continue

                    # 提取位置和上下文
                    start_pos = match.start(1)
                    end_pos = match.end(1)
                    context = self._extract_context(text, start_pos, end_pos)

                    # 识别实体所属域
                    entity_domain = self._identify_entity_domain(entity_text, context, target_domain)

                    # 计算置信度
                    confidence = self._calculate_confidence(entity_text, rule, context, entity_domain)

                    # 提取属性
                    attributes = self._extract_entity_attributes(entity_text, context, rule.entity_type, entity_domain)

                    entity = ExtractedEntity(
                        text=entity_text,
                        entity_type=rule.entity_type,
                        domain=entity_domain,
                        confidence=confidence,
                        position=(start_pos, end_pos),
                        context=context,
                        attributes=attributes,
                        extraction_rule=rule.name
                    )

                    entities.append(entity)

            except re.error as e:
                logger.warning(f"正则表达式错误 in rule {rule.name}: {e}")
                continue

        return entities

    def _is_valid_entity_text(self, text: str) -> bool:
        """验证实体文本"""
        # 长度检查
        if len(text) < self.validation_rules["min_length"] or len(text) > self.validation_rules["max_length"]:
            return False

        # 禁用字符检查
        if any(char in text for char in self.validation_rules["forbidden_chars"]):
            return False

        # 排除模式检查
        for pattern in self.exclusion_patterns:
            if re.match(pattern, text):
                return False

        return True

    def _extract_context(self, text: str, start_pos: int, end_pos: int, window: int = 80) -> str:
        """提取上下文"""
        context_start = max(0, start_pos - window)
        context_end = min(len(text), end_pos + window)

        context = text[context_start:context_end]

        # 确保上下文的完整性
        if context_start > 0:
            # 找到前一个句号或段落开始
            prev_boundary = text.rfind('。', 0, start_pos)
            if prev_boundary != -1 and start_pos - prev_boundary < window * 2:
                context_start = prev_boundary + 1
                context = text[context_start:context_end]

        return context.strip()

    def _identify_entity_domain(self, entity_text: str, context: str, target_domain: Optional[DomainType]) -> Optional[DomainType]:
        """识别实体所属域"""
        if target_domain:
            # 如果指定了目标域，优先使用
            return target_domain

        domain_scores = {}

        for domain, domain_info in self.domain_specific_rules.items():
            score = 0

            # 检查签名实体
            if entity_text in domain_info["signature_entities"]:
                score += 10

            # 检查层级标记
            if entity_text in domain_info["hierarchy_markers"]:
                score += 8

            # 检查机构类型
            if entity_text in domain_info["institutions"]:
                score += 6

            # 检查文化物品
            if entity_text in domain_info["cultural_items"]:
                score += 6

            # 检查仪式活动
            if entity_text in domain_info["rituals"]:
                score += 6

            # 检查上下文中的域特征词
            for signature in domain_info["signature_entities"]:
                if signature in context:
                    score += 2

            # 检查禁用词汇（负分）
            for forbidden in domain_info["forbidden_terms"]:
                if forbidden in context:
                    score -= 5

            if score > 0:
                domain_scores[domain] = score

        # 返回得分最高的域
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)

        return None

    def _calculate_confidence(self, entity_text: str, rule: ExtractionRule, context: str, domain: Optional[DomainType]) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度

        # 规则置信度加成
        confidence += rule.confidence_boost

        # 长度因子
        if len(entity_text) >= 3:
            confidence += 0.1
        if len(entity_text) >= 5:
            confidence += 0.1

        # 域匹配加成
        if domain and rule.domain_specific == domain:
            confidence += 0.2

        # 上下文支持
        if rule.context_requirements:
            context_support = sum(1 for req in rule.context_requirements if req in context)
            confidence += context_support * 0.05

        # 域特征支持
        if domain and domain in self.domain_specific_rules:
            domain_info = self.domain_specific_rules[domain]
            signature_support = sum(1 for sig in domain_info["signature_entities"] if sig in context)
            confidence += signature_support * 0.03

        # 专有名词加成
        if entity_text in [entity for domain_info in self.domain_specific_rules.values()
                          for entity in domain_info["signature_entities"]]:
            confidence += 0.2

        return min(confidence, 1.0)

    def _extract_entity_attributes(self, entity_text: str, context: str, entity_type: EntityType, domain: Optional[DomainType]) -> Dict[str, Any]:
        """提取实体属性"""
        attributes = {
            "entity_type": entity_type.value,
            "domain": domain.value if domain else None,
            "length": len(entity_text)
        }

        # 规模属性
        scale_keywords = {
            "大型": ["庞大", "巨大", "宏大", "巨型", "超大"],
            "中型": ["中等", "适中", "一般", "标准"],
            "小型": ["小型", "微型", "精小", "袖珍", "迷你"]
        }

        for scale, keywords in scale_keywords.items():
            if any(keyword in context for keyword in keywords):
                attributes["scale"] = scale
                break

        # 时间属性
        time_keywords = {
            "古代": ["古代", "古时", "远古", "上古", "古老"],
            "现代": ["现代", "当前", "如今", "现在", "当今"],
            "传统": ["传统", "悠久", "历史", "世代"]
        }

        for time_period, keywords in time_keywords.items():
            if any(keyword in context for keyword in keywords):
                attributes["temporal"] = time_period
                break

        # 重要性属性
        importance_keywords = {
            "核心": ["核心", "根本", "基础", "关键"],
            "重要": ["重要", "主要", "重大", "显著"],
            "次要": ["次要", "辅助", "附属", "补充"]
        }

        for importance, keywords in importance_keywords.items():
            if any(keyword in context for keyword in keywords):
                attributes["importance"] = importance
                break

        # 状态属性
        status_keywords = {
            "活跃": ["活跃", "运行", "使用", "流行"],
            "衰落": ["衰落", "废弃", "过时", "消失"],
            "禁忌": ["禁忌", "禁止", "严禁", "不允许"]
        }

        for status, keywords in status_keywords.items():
            if any(keyword in context for keyword in keywords):
                attributes["status"] = status
                break

        # 特定于实体类型的属性
        if entity_type == EntityType.ORGANIZATION:
            # 组织规模
            org_scale_patterns = [
                (r'(?:共|总共|拥有).*?(\d+).*?(?:人|员|众)', "member_count"),
                (r'(?:设有|下辖|管辖).*?(\d+).*?(?:个|处|部)', "sub_units")
            ]

            for pattern, attr_name in org_scale_patterns:
                match = re.search(pattern, context)
                if match:
                    attributes[attr_name] = match.group(1)

        elif entity_type == EntityType.SYSTEM:
            # 等级数量
            level_pattern = r'(?:分为|共有|设有).*?(\d+).*?(?:等|级|层)'
            match = re.search(level_pattern, context)
            if match:
                attributes["level_count"] = match.group(1)

        elif entity_type == EntityType.CURRENCY:
            # 汇率信息
            rate_pattern = r'(\d+).*?(?:等于|换|兑).*?(\d+)'
            match = re.search(rate_pattern, context)
            if match:
                attributes["exchange_rate"] = f"{match.group(1)}:{match.group(2)}"

        return attributes

    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """去重实体"""
        seen = set()
        unique_entities = []

        for entity in entities:
            # 创建唯一键
            key = (entity.text, entity.entity_type, entity.domain)

            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
            else:
                # 如果有重复，保留置信度更高的
                for i, existing in enumerate(unique_entities):
                    if (existing.text, existing.entity_type, existing.domain) == key:
                        if entity.confidence > existing.confidence:
                            unique_entities[i] = entity
                        break

        return unique_entities

    def _validate_entities(self, entities: List[ExtractedEntity], text: str) -> List[ExtractedEntity]:
        """验证实体"""
        valid_entities = []

        for entity in entities:
            # 上下文长度检查
            if len(entity.context) < self.validation_rules["required_context_window"]:
                continue

            # 域一致性检查
            if entity.domain and not self._validate_domain_consistency(entity, text):
                # 降低置信度而不是完全排除
                entity.confidence *= 0.7

            # 实体类型一致性检查
            if not self._validate_entity_type_consistency(entity):
                entity.confidence *= 0.8

            # 保留置信度大于阈值的实体
            if entity.confidence >= 0.3:
                valid_entities.append(entity)

        return valid_entities

    def _validate_domain_consistency(self, entity: ExtractedEntity, text: str) -> bool:
        """验证域一致性"""
        if not entity.domain:
            return True

        domain_info = self.domain_specific_rules.get(entity.domain)
        if not domain_info:
            return True

        # 检查是否存在禁用词汇
        for forbidden in domain_info["forbidden_terms"]:
            if forbidden in entity.context:
                return False

        return True

    def _validate_entity_type_consistency(self, entity: ExtractedEntity) -> bool:
        """验证实体类型一致性"""
        # 简化的类型一致性检查
        type_patterns = {
            EntityType.ORGANIZATION: [r'(?:管理|控制|负责|设立)', r'(?:府|司|院|会|殿)'],
            EntityType.CONCEPT: [r'(?:理论|概念|原理|规则)', r'(?:制|法|道|术)'],
            EntityType.ITEM: [r'(?:使用|制作|持有)', r'(?:器|票|印|珠)'],
            EntityType.RITUAL: [r'(?:举行|参与|庆祝)', r'(?:礼|祭|节|仪)']
        }

        patterns = type_patterns.get(entity.entity_type, [])
        return any(re.search(pattern, entity.context) for pattern in patterns)

    def _post_process_entities(self, entities: List[ExtractedEntity], text: str, target_domain: Optional[DomainType]) -> List[ExtractedEntity]:
        """后处理实体"""
        # 按置信度排序
        entities.sort(key=lambda x: x.confidence, reverse=True)

        # 如果指定了目标域，优先保留该域的实体
        if target_domain:
            domain_entities = [e for e in entities if e.domain == target_domain]
            other_entities = [e for e in entities if e.domain != target_domain]
            entities = domain_entities + other_entities

        # 限制每种类型的实体数量，避免过多
        type_limits = {
            EntityType.ORGANIZATION: 20,
            EntityType.CONCEPT: 30,
            EntityType.ITEM: 25,
            EntityType.RITUAL: 15,
            EntityType.SYSTEM: 10,
            EntityType.CURRENCY: 8,
            EntityType.TECHNOLOGY: 15,
            EntityType.BELIEF: 12,
            EntityType.CUSTOM: 15
        }

        type_counts = {}
        filtered_entities = []

        for entity in entities:
            current_count = type_counts.get(entity.entity_type, 0)
            limit = type_limits.get(entity.entity_type, 20)

            if current_count < limit:
                filtered_entities.append(entity)
                type_counts[entity.entity_type] = current_count + 1

        return filtered_entities

    def extract_domain_entities(self, text: str, domain: DomainType) -> List[ExtractedEntity]:
        """提取特定域的实体"""
        return self.extract_entities(text, target_domain=domain)

    def get_extraction_statistics(self, entities: List[ExtractedEntity]) -> Dict[str, Any]:
        """获取提取统计信息"""
        stats = {
            "total_entities": len(entities),
            "by_type": {},
            "by_domain": {},
            "by_confidence": {"high": 0, "medium": 0, "low": 0},
            "average_confidence": 0.0
        }

        for entity in entities:
            # 按类型统计
            entity_type = entity.entity_type.value
            stats["by_type"][entity_type] = stats["by_type"].get(entity_type, 0) + 1

            # 按域统计
            domain = entity.domain.value if entity.domain else "未知域"
            stats["by_domain"][domain] = stats["by_domain"].get(domain, 0) + 1

            # 按置信度统计
            if entity.confidence >= 0.8:
                stats["by_confidence"]["high"] += 1
            elif entity.confidence >= 0.5:
                stats["by_confidence"]["medium"] += 1
            else:
                stats["by_confidence"]["low"] += 1

        # 计算平均置信度
        if entities:
            stats["average_confidence"] = sum(e.confidence for e in entities) / len(entities)

        return stats