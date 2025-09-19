"""
高级中文文本分析器 - 专门处理复杂的中文文化设定文档
支持语义分析、实体链接、上下文理解等高级功能
"""

import re
import jieba
import jieba.posseg as pseg
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import logging

# 添加自定义词典
jieba.load_userdict('src/etl/custom_dict.txt')  # 需要创建这个文件

logger = logging.getLogger(__name__)


@dataclass
class TextSegment:
    """文本段落"""
    content: str
    start_pos: int
    end_pos: int
    segment_type: str  # header, content, list_item, etc.
    level: int = 0  # 层级，0为最高级
    tags: List[str] = field(default_factory=list)


@dataclass
class NamedEntity:
    """命名实体"""
    text: str
    entity_type: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticRelation:
    """语义关系"""
    subject: str
    predicate: str
    object: str
    confidence: float
    context: str


class ChineseTextAnalyzer:
    """中文文本分析器"""

    def __init__(self):
        self.initialize_dictionaries()
        self.initialize_patterns()
        self.initialize_semantic_rules()

    def initialize_dictionaries(self):
        """初始化词典"""

        # 九域文化特定词汇
        self.cultural_terms = {
            # 组织机构
            "organizations": [
                "王朝", "议会", "殿", "宗门", "门派", "府", "司", "院", "堂", "社", "团",
                "天命王朝", "祭司议会", "冥司殿", "守源会", "巡链司", "缚司", "县府"
            ],

            # 重要概念
            "concepts": [
                "法则", "链", "术", "功", "诀", "道", "理", "法", "式", "制",
                "链籍", "法则链", "断链术", "环印", "三等制", "师承制", "血契制"
            ],

            # 文化物品
            "items": [
                "票", "器", "盘", "珠", "石", "符", "印", "镜", "册", "书", "卷", "典",
                "链票", "镇魂器", "稳乱器", "回响盘", "环印", "链籍"
            ],

            # 仪式活动
            "rituals": [
                "礼", "节", "夜", "月", "典", "仪", "祭", "庆", "会",
                "裂世夜", "归环礼", "狂环月", "拾链礼", "链诞节", "断链仪"
            ],

            # 身份等级
            "identities": [
                "籍", "等", "级", "品", "阶", "身份", "地位",
                "黄籍", "灰籍", "黑籍", "良籍", "苦役", "罪籍"
            ],

            # 地理概念
            "locations": [
                "域", "城", "府", "县", "乡", "坊", "市", "港", "岛",
                "人域", "天域", "荒域", "冥域", "魔域", "虚域", "海域", "源域"
            ]
        }

        # 语义关系词汇
        self.relation_words = {
            "control": ["控制", "统治", "管理", "掌管", "主管", "负责", "治理"],
            "contain": ["包含", "含有", "设有", "拥有", "具备"],
            "belong": ["属于", "隶属于", "归属", "从属"],
            "origin": ["来源于", "源自", "衍生自", "起源于", "产生于"],
            "influence": ["影响", "感化", "作用于", "左右"],
            "conflict": ["冲突", "对立", "敌对", "反对", "抵制", "对抗"],
            "similar": ["相似", "类似", "相近", "相当", "如同"],
            "use": ["使用", "运用", "应用", "采用", "利用"],
            "create": ["创造", "制造", "建立", "设立", "创建"],
            "destroy": ["摧毁", "破坏", "消灭", "毁灭", "废除"]
        }

        # 修饰词汇
        self.modifiers = {
            "scale": ["庞大", "巨大", "宏大", "小型", "微型", "精小", "中等", "适中"],
            "time": ["古代", "古时", "远古", "上古", "现代", "当前", "如今", "现在", "传统", "古老", "悠久"],
            "importance": ["重要", "关键", "核心", "主要", "次要", "重大", "根本", "基础"],
            "quality": ["优秀", "杰出", "卓越", "普通", "一般", "特殊", "独特", "神秘", "禁忌"],
            "frequency": ["常见", "罕见", "稀有", "普遍", "广泛", "少见", "频繁", "偶尔"]
        }

    def initialize_patterns(self):
        """初始化正则模式"""

        # 标题模式
        self.title_patterns = [
            r'^#{1,6}\s*(.+)',  # Markdown标题
            r'^([A-F])[\.、\s]*(.+)',  # A. B. C. 等维度标题
            r'^(\d+)[\.、\s]*(.+)',  # 1. 2. 3. 等编号
            r'^([^。！？\n]{2,20})[：:]$',  # 冒号结尾的标题
            r'^【([^】]+)】',  # 方括号标题
        ]

        # 列表项模式
        self.list_patterns = [
            r'^[\s]*[·•▪▫]\s*(.+)',  # 项目符号
            r'^[\s]*[-*+]\s*(.+)',  # 破折号
            r'^[\s]*\d+[\.、)]\s*(.+)',  # 数字编号
            r'^[\s]*[①②③④⑤⑥⑦⑧⑨⑩]\s*(.+)',  # 圆圈数字
        ]

        # 定义模式
        self.definition_patterns = [
            r'([^，。！？：\n]{2,15})[：:]([^。！？\n]+)',  # 名词：定义
            r'([^，。！？\n]{2,15})(?:是|指|表示|代表)([^，。！？\n]+)',  # 名词是/指定义
            r'所谓([^，。！？\n]{2,15})[，：]([^，。！？\n]+)',  # 所谓名词，定义
        ]

        # 关系模式
        self.relation_patterns = {
            "control": [
                r'([^，。！？\n]{2,15})(?:控制|统治|管理|掌管)([^，。！？\n]{2,15})',
                r'([^，。！？\n]{2,15})(?:的|之)(?:统治者|管理者|控制者)(?:是|为)([^，。！？\n]{2,15})'
            ],
            "contain": [
                r'([^，。！？\n]{2,15})(?:包含|含有|设有|拥有)([^，。！？\n]{2,15})',
                r'([^，。！？\n]{2,15})(?:属于|隶属于|设在)([^，。！？\n]{2,15})'
            ],
            "conflict": [
                r'([^，。！？\n]{2,15})(?:与|和)([^，。！？\n]{2,15})(?:冲突|对立|敌对)',
                r'([^，。！？\n]{2,15})(?:反对|抵制|对抗)([^，。！？\n]{2,15})'
            ]
        }

    def initialize_semantic_rules(self):
        """初始化语义规则"""

        # 上下文语义规则
        self.context_rules = {
            "政治权力": {
                "keywords": ["权力", "政治", "统治", "管理", "法律", "制度"],
                "entities": ["王朝", "议会", "府", "司", "官员", "法则"],
                "relations": ["control", "govern", "rule"]
            },
            "宗教信仰": {
                "keywords": ["信仰", "神", "祭祀", "宗教", "神话", "仪式"],
                "entities": ["祭司", "神祇", "庙宇", "仪式", "信条"],
                "relations": ["worship", "believe", "ritual"]
            },
            "经济技术": {
                "keywords": ["经济", "技术", "工艺", "货币", "贸易", "产业"],
                "entities": ["货币", "技术", "工艺", "行业", "商会"],
                "relations": ["trade", "produce", "exchange"]
            }
        }

    def analyze_text_structure(self, text: str) -> List[TextSegment]:
        """分析文本结构"""
        segments = []
        lines = text.split('\n')
        current_pos = 0

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                current_pos += len(lines[i]) + 1
                continue

            segment_type, level = self._classify_line(line)

            segment = TextSegment(
                content=line,
                start_pos=current_pos,
                end_pos=current_pos + len(line),
                segment_type=segment_type,
                level=level
            )

            segments.append(segment)
            current_pos += len(lines[i]) + 1

        return segments

    def _classify_line(self, line: str) -> Tuple[str, int]:
        """分类文本行"""

        # 检查标题
        for pattern in self.title_patterns:
            match = re.match(pattern, line)
            if match:
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    return "header", level
                elif re.match(r'^[A-F][\.、]', line):
                    return "dimension_header", 1
                else:
                    return "header", 2

        # 检查列表项
        for pattern in self.list_patterns:
            if re.match(pattern, line):
                return "list_item", 3

        # 检查定义
        for pattern in self.definition_patterns:
            if re.match(pattern, line):
                return "definition", 3

        # 默认为内容
        return "content", 4

    def extract_named_entities(self, text: str) -> List[NamedEntity]:
        """提取命名实体"""
        entities = []

        # 使用jieba进行词性标注
        words = pseg.cut(text)

        current_pos = 0
        for word, flag in words:
            entity_type = self._classify_entity(word, flag)

            if entity_type:
                context = self._extract_word_context(text, word, current_pos)
                confidence = self._calculate_entity_confidence(word, entity_type, context)

                entity = NamedEntity(
                    text=word,
                    entity_type=entity_type,
                    confidence=confidence,
                    start_pos=current_pos,
                    end_pos=current_pos + len(word),
                    context=context,
                    attributes=self._extract_entity_attributes(word, context)
                )
                entities.append(entity)

            current_pos += len(word)

        # 使用自定义规则补充提取
        custom_entities = self._extract_custom_entities(text)
        entities.extend(custom_entities)

        return entities

    def _classify_entity(self, word: str, pos_flag: str) -> Optional[str]:
        """分类实体"""

        # 基于词性标注
        if pos_flag in ['nr', 'nrt']:  # 人名、机构名
            return "PERSON_ORG"
        elif pos_flag in ['ns', 'nt']:  # 地名、时间
            return "LOCATION_TIME"
        elif pos_flag == 'n':  # 普通名词，需要进一步判断
            pass
        else:
            return None

        # 基于文化词典
        for category, terms in self.cultural_terms.items():
            if any(term in word for term in terms):
                return category.upper()

        # 特殊模式匹配
        if re.search(r'[王帝皇]', word) and len(word) <= 4:
            return "ROYAL_TITLE"

        if re.search(r'[府司院堂]$', word):
            return "ORGANIZATION"

        if re.search(r'[术法诀功]$', word):
            return "TECHNIQUE"

        return None

    def _extract_word_context(self, text: str, word: str, position: int, window: int = 50) -> str:
        """提取词汇上下文"""
        start = max(0, position - window)
        end = min(len(text), position + len(word) + window)
        return text[start:end]

    def _calculate_entity_confidence(self, word: str, entity_type: str, context: str) -> float:
        """计算实体置信度"""
        confidence = 0.5  # 基础置信度

        # 长度因子
        if len(word) >= 3:
            confidence += 0.2

        # 文化词典匹配
        for category, terms in self.cultural_terms.items():
            if category.upper() == entity_type and word in terms:
                confidence += 0.3
                break

        # 上下文支持
        context_keywords = self._get_context_keywords(entity_type)
        context_support = sum(1 for keyword in context_keywords if keyword in context)
        confidence += min(context_support * 0.1, 0.2)

        return min(confidence, 1.0)

    def _get_context_keywords(self, entity_type: str) -> List[str]:
        """获取实体类型的上下文关键词"""
        context_map = {
            "ORGANIZATIONS": ["管理", "控制", "负责", "设立", "组织"],
            "CONCEPTS": ["理论", "概念", "原理", "规则", "体系"],
            "ITEMS": ["使用", "制作", "持有", "物品", "器具"],
            "RITUALS": ["举行", "参与", "庆祝", "仪式", "典礼"],
            "LOCATIONS": ["位于", "地方", "区域", "境内", "当地"]
        }
        return context_map.get(entity_type, [])

    def _extract_entity_attributes(self, word: str, context: str) -> Dict[str, Any]:
        """提取实体属性"""
        attributes = {}

        # 规模属性
        for modifier in self.modifiers["scale"]:
            if modifier in context:
                attributes["scale"] = modifier
                break

        # 时间属性
        for modifier in self.modifiers["time"]:
            if modifier in context:
                attributes["temporal"] = modifier
                break

        # 重要性属性
        for modifier in self.modifiers["importance"]:
            if modifier in context:
                attributes["importance"] = modifier
                break

        # 质量属性
        for modifier in self.modifiers["quality"]:
            if modifier in context:
                attributes["quality"] = modifier
                break

        return attributes

    def _extract_custom_entities(self, text: str) -> List[NamedEntity]:
        """使用自定义规则提取实体"""
        entities = []

        # 专有名词模式
        patterns = [
            (r'([^，。！？\s]{2,8}(?:王朝|议会|殿|宗|门|派|府|司|院|堂))', "ORGANIZATION"),
            (r'([^，。！？\s]{2,8}(?:法则|链|术|功|诀|道|理|法|式|制))', "CONCEPT"),
            (r'([^，。！？\s]{2,8}(?:票|器|盘|珠|石|符|印|镜|册|书|卷))', "ITEM"),
            (r'([^，。！？\s]{2,8}(?:礼|节|夜|月|典|仪|祭|庆|会))', "RITUAL"),
        ]

        for pattern, entity_type in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                word = match.group(1)
                start_pos = match.start(1)
                end_pos = match.end(1)

                context = self._extract_word_context(text, word, start_pos)
                confidence = self._calculate_entity_confidence(word, entity_type, context)

                entity = NamedEntity(
                    text=word,
                    entity_type=entity_type,
                    confidence=confidence,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    context=context,
                    attributes=self._extract_entity_attributes(word, context)
                )
                entities.append(entity)

        return entities

    def extract_semantic_relations(self, text: str, entities: List[NamedEntity]) -> List[SemanticRelation]:
        """提取语义关系"""
        relations = []

        # 基于模式的关系提取
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    subject = match.group(1).strip()
                    obj = match.group(2).strip()

                    # 验证实体存在
                    if self._validate_entity_pair(subject, obj, entities):
                        context = text[max(0, match.start()-50):match.end()+50]
                        confidence = self._calculate_relation_confidence(subject, obj, relation_type, context)

                        relation = SemanticRelation(
                            subject=subject,
                            predicate=relation_type,
                            object=obj,
                            confidence=confidence,
                            context=context
                        )
                        relations.append(relation)

        # 基于上下文的关系推理
        inferred_relations = self._infer_relations_from_context(text, entities)
        relations.extend(inferred_relations)

        return relations

    def _validate_entity_pair(self, subject: str, obj: str, entities: List[NamedEntity]) -> bool:
        """验证实体对是否有效"""
        entity_texts = [e.text for e in entities]
        return (any(subject in text for text in entity_texts) and
                any(obj in text for text in entity_texts))

    def _calculate_relation_confidence(self, subject: str, obj: str, relation_type: str, context: str) -> float:
        """计算关系置信度"""
        confidence = 0.6  # 基础置信度

        # 关系词支持
        relation_words = self.relation_words.get(relation_type, [])
        word_support = sum(1 for word in relation_words if word in context)
        confidence += min(word_support * 0.1, 0.3)

        # 实体类型匹配
        if self._check_entity_type_compatibility(subject, obj, relation_type):
            confidence += 0.1

        return min(confidence, 1.0)

    def _check_entity_type_compatibility(self, subject: str, obj: str, relation_type: str) -> bool:
        """检查实体类型兼容性"""
        # 简化的兼容性检查
        compatibility_rules = {
            "control": [("ORGANIZATION", "ORGANIZATION"), ("PERSON", "ORGANIZATION")],
            "contain": [("ORGANIZATION", "CONCEPT"), ("LOCATION", "ORGANIZATION")],
            "conflict": [("ORGANIZATION", "ORGANIZATION"), ("CONCEPT", "CONCEPT")]
        }

        # 这里需要更复杂的逻辑来确定实体类型
        return True  # 简化返回

    def _infer_relations_from_context(self, text: str, entities: List[NamedEntity]) -> List[SemanticRelation]:
        """从上下文推理关系"""
        relations = []

        # 共现分析
        entity_pairs = []
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                if abs(entity1.start_pos - entity2.start_pos) < 100:  # 距离阈值
                    entity_pairs.append((entity1, entity2))

        # 为共现实体对推理关系
        for entity1, entity2 in entity_pairs:
            context_start = min(entity1.start_pos, entity2.start_pos) - 50
            context_end = max(entity1.end_pos, entity2.end_pos) + 50
            context = text[max(0, context_start):min(len(text), context_end)]

            # 基于上下文关键词推理关系类型
            inferred_relation = self._infer_relation_type(context, entity1, entity2)
            if inferred_relation:
                relations.append(inferred_relation)

        return relations

    def _infer_relation_type(self, context: str, entity1: NamedEntity, entity2: NamedEntity) -> Optional[SemanticRelation]:
        """推理关系类型"""
        # 检查上下文中的关系指示词
        for relation_type, words in self.relation_words.items():
            if any(word in context for word in words):
                return SemanticRelation(
                    subject=entity1.text,
                    predicate=relation_type,
                    object=entity2.text,
                    confidence=0.4,  # 推理关系置信度较低
                    context=context
                )

        # 默认关联关系
        return SemanticRelation(
            subject=entity1.text,
            predicate="related_to",
            object=entity2.text,
            confidence=0.3,
            context=context
        )

    def analyze_cultural_themes(self, text: str) -> Dict[str, float]:
        """分析文化主题"""
        themes = defaultdict(float)

        # 主题关键词权重
        theme_keywords = {
            "政治权力": ["权力", "政治", "统治", "管理", "法律", "制度", "王朝", "官员"] * 2,
            "宗教信仰": ["信仰", "神", "祭祀", "宗教", "神话", "仪式", "祭司", "神祇"] * 2,
            "经济技术": ["经济", "技术", "工艺", "货币", "贸易", "产业", "商业", "制作"] * 2,
            "社会文化": ["社会", "文化", "传统", "习俗", "艺术", "教育", "家庭", "婚姻"] * 2,
            "军事战争": ["军事", "战争", "武器", "战斗", "军队", "将军", "士兵", "防御"] * 2,
        }

        # 计算主题权重
        for theme, keywords in theme_keywords.items():
            for keyword in keywords:
                count = text.count(keyword)
                themes[theme] += count * (1.0 / len(keywords))

        # 归一化
        total = sum(themes.values())
        if total > 0:
            themes = {theme: score/total for theme, score in themes.items()}

        return dict(themes)

    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成文本摘要"""
        # 简化的摘要生成
        sentences = re.split(r'[。！？]', text)

        # 计算句子重要性
        sentence_scores = []
        for sentence in sentences:
            if len(sentence.strip()) < 10:
                continue

            score = 0
            # 基于关键词计算分数
            for category, terms in self.cultural_terms.items():
                for term in terms:
                    score += sentence.count(term)

            sentence_scores.append((sentence.strip(), score))

        # 选择最重要的句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)

        summary = ""
        for sentence, score in sentence_scores:
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break

        return summary.strip()

    def extract_key_concepts(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """提取关键概念"""
        # 词频统计
        words = jieba.cut(text)
        word_freq = Counter(words)

        # 过滤停用词和短词
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}

        concept_scores = []
        for word, freq in word_freq.items():
            if len(word) < 2 or word in stopwords:
                continue

            # 计算概念重要性分数
            score = freq

            # 文化词典加权
            for category, terms in self.cultural_terms.items():
                if word in terms:
                    score *= 2
                    break

            # 长度加权
            if len(word) >= 3:
                score *= 1.5

            concept_scores.append((word, score))

        # 排序并返回top-k
        concept_scores.sort(key=lambda x: x[1], reverse=True)
        return concept_scores[:top_k]