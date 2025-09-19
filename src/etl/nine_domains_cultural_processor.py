"""
裂世九域·法则链纪元 - 专门的文化框架数据处理器
针对九域六维文化体系进行深度解析和结构化处理
"""

import re
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum

from ..database.models.cultural_framework_models import (
    DomainType, CulturalDimension, EntityType, RelationType,
    CulturalFrameworkCreate, CulturalEntityCreate, CulturalRelationCreate,
    PlotHookCreate, ConceptDictionaryCreate, CulturalFrameworkBatch
)


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class EntityExtractionRule:
    """实体提取规则"""
    patterns: List[str]
    entity_type: EntityType
    confidence_boost: float = 0.0
    context_keywords: List[str] = field(default_factory=list)
    domain_specific: Optional[DomainType] = None


@dataclass
class CulturalSection:
    """文化段落数据"""
    domain: DomainType
    dimension: CulturalDimension
    title: str
    content: str
    raw_text: str
    entities: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    plot_hooks: List[str] = field(default_factory=list)


class NineDomainsCulturalProcessor:
    """九域文化框架专门处理器"""

    def __init__(self):
        self.initialize_patterns()
        self.initialize_extraction_rules()
        self.initialize_validation_rules()

    def initialize_patterns(self):
        """初始化模式匹配规则"""

        # 域识别模式 - 更精确的识别
        self.domain_patterns = {
            "人域": {
                "keywords": ["链籍", "环祖", "乡祭", "缚司", "县府", "宗门驻坊", "巡链司"],
                "indicators": ["黄籍", "灰籍", "黑籍", "良籍", "苦役", "罪籍"]
            },
            "天域": {
                "keywords": ["天命王朝", "帝都", "龙阙", "司天监", "御史台"],
                "indicators": ["王侯", "世家", "官品", "天命"]
            },
            "荒域": {
                "keywords": ["野人", "萨满", "图腾", "狩猎", "游牧"],
                "indicators": ["部落", "长老", "血仇", "野性"]
            },
            "冥域": {
                "keywords": ["冥司殿", "渡链僧", "镇魂器", "冥籍", "阴兵"],
                "indicators": ["亡魂", "超度", "轮回", "冥法"]
            },
            "魔域": {
                "keywords": ["血契", "魔祭", "噬魂", "血池", "魔典"],
                "indicators": ["血誓", "献祭", "魔化", "堕落"]
            },
            "虚域": {
                "keywords": ["虚空", "法则", "悟道", "无为", "空明"],
                "indicators": ["超脱", "虚无", "法则", "道境"]
            },
            "海域": {
                "keywords": ["港市", "商会", "航海", "岛屿", "潮汐"],
                "indicators": ["船队", "贸易", "风暴", "海族"]
            },
            "源域": {
                "keywords": ["源流", "古籍", "守源会", "秘典", "源力"],
                "indicators": ["起源", "古老", "神秘", "禁忌"]
            }
        }

        # 维度识别模式
        self.dimension_patterns = {
            "神话与宗教": {
                "keywords": ["信条", "神祇", "祭司", "信仰", "祭祀", "丧葬", "神话", "宗教"],
                "markers": ["A.", "A、", "神话与宗教"]
            },
            "权力与法律": {
                "keywords": ["权力", "法律", "结构", "身份", "刑罚", "执法", "政治", "统治"],
                "markers": ["B.", "B、", "权力与法律"]
            },
            "经济与技术": {
                "keywords": ["产业", "金融", "技术", "工艺", "货币", "贸易", "经济"],
                "markers": ["C.", "C、", "经济与技术"]
            },
            "家庭与教育": {
                "keywords": ["家庭", "教育", "婚姻", "血缘", "传承", "师承", "学习"],
                "markers": ["D.", "D、", "家庭与教育"]
            },
            "仪式与日常": {
                "keywords": ["仪式", "日常", "习俗", "节日", "庆典", "礼仪", "生活"],
                "markers": ["E.", "E、", "仪式与日常"]
            },
            "艺术与娱乐": {
                "keywords": ["艺术", "娱乐", "美学", "竞技", "表演", "文艺", "音乐"],
                "markers": ["F.", "F、", "艺术与娱乐"]
            }
        }

    def initialize_extraction_rules(self):
        """初始化实体提取规则"""

        self.extraction_rules = [
            # 组织机构规则
            EntityExtractionRule(
                patterns=[
                    r'([^，。！？\s]{2,8}(?:王朝|议会|殿|会|宗|门|派|府|司|院|堂|社|团|联盟|组织))',
                    r'(天命王朝|祭司议会|冥司殿|守源会|巡链司|缚司|县府)',
                    r'([^，。！？\s]{2,6}(?:坊|寺|观|庙|祠))'
                ],
                entity_type=EntityType.ORGANIZATION,
                context_keywords=["管理", "统治", "控制", "负责", "主管"]
            ),

            # 重要概念规则
            EntityExtractionRule(
                patterns=[
                    r'([^，。！？\s]{2,8}(?:法则|链|术|功|诀|道|理|法|式|制))',
                    r'(链籍|法则链|断链术|环印|三等制|师承制|血契制)',
                    r'([^，。！？\s]{2,6}(?:籍|等|级|品|阶))'
                ],
                entity_type=EntityType.CONCEPT,
                context_keywords=["规则", "制度", "体系", "概念", "理论"]
            ),

            # 文化物品规则
            EntityExtractionRule(
                patterns=[
                    r'([^，。！？\s]{2,8}(?:票|器|盘|珠|石|符|印|镜|册|书|卷|典))',
                    r'(链票|镇魂器|稳乱器|回响盘|环印|链籍|家谱)',
                    r'([^，。！？\s]{2,6}(?:剑|刀|锤|杖|袍|冠|玉|宝))'
                ],
                entity_type=EntityType.ITEM,
                context_keywords=["使用", "持有", "佩戴", "收藏", "制作"]
            ),

            # 仪式活动规则
            EntityExtractionRule(
                patterns=[
                    r'([^，。！？\s]{2,8}(?:礼|节|夜|月|典|仪|祭|庆|会))',
                    r'(裂世夜|归环礼|狂环月|拾链礼|链诞节|断链仪)',
                    r'([^，。！？\s]{2,6}(?:祭|祀|拜|诵|奠|葬))'
                ],
                entity_type=EntityType.RITUAL,
                context_keywords=["举行", "参与", "庆祝", "纪念", "祭祀"]
            ),

            # 身份制度规则
            EntityExtractionRule(
                patterns=[
                    r'([^，。！？\s]{2,6}(?:籍|等|级|品|阶|身份|地位))',
                    r'(黄籍|灰籍|黑籍|良籍|苦役|罪籍)',
                    r'([^，。！？\s]{2,6}(?:官|吏|民|奴|仆))'
                ],
                entity_type=EntityType.SYSTEM,
                context_keywords=["身份", "等级", "地位", "分类", "区分"]
            ),

            # 货币体系规则
            EntityExtractionRule(
                patterns=[
                    r'([^，。！？\s]{2,8}(?:币|钱|金|银|铜|晶|石|珠))',
                    r'(环币|链金|法则晶|灵石|链票)',
                ],
                entity_type=EntityType.CURRENCY,
                context_keywords=["支付", "交易", "购买", "价值", "流通"]
            ),

            # 技术工艺规则
            EntityExtractionRule(
                patterns=[
                    r'([^，。！？\s]{2,8}(?:技|工艺|法|术|学|道|艺))',
                    r'(锻链术|环铸法|法则工艺|链接技术)',
                ],
                entity_type=EntityType.TECHNOLOGY,
                context_keywords=["制作", "学习", "掌握", "传授", "技能"]
            )
        ]

    def initialize_validation_rules(self):
        """初始化验证规则"""

        # 九域验证规则
        self.domain_validation = {
            DomainType.HUMAN_DOMAIN: {
                "required_elements": ["链籍", "环祖", "乡祭"],
                "optional_elements": ["县府", "宗门", "缚司"],
                "forbidden_elements": ["魔祭", "血池", "虚空"]
            },
            DomainType.DEMON_DOMAIN: {
                "required_elements": ["血契", "魔祭"],
                "forbidden_elements": ["链籍", "环祖"]
            }
        }

    async def process_nine_domains_text(self, text: str, novel_id: UUID) -> CulturalFrameworkBatch:
        """处理九域文化框架文本"""
        logger.info(f"开始处理九域文化文本，长度: {len(text)}")

        try:
            # 1. 预处理文本
            cleaned_text = self._preprocess_text(text)

            # 2. 按域分割
            domain_sections = self._extract_domain_sections(cleaned_text)

            # 3. 按维度解析每个域
            cultural_sections = []
            for domain_name, domain_text in domain_sections.items():
                sections = self._parse_domain_dimensions(domain_name, domain_text)
                cultural_sections.extend(sections)

            # 4. 创建批量数据
            batch = await self._create_batch_data(cultural_sections, novel_id)

            # 5. 增强数据质量
            batch = await self._enhance_batch_data(batch, cleaned_text)

            # 6. 验证数据
            validation_result = await self._validate_cultural_data(batch)
            if not validation_result["valid"]:
                logger.warning(f"数据验证发现问题: {validation_result['warnings']}")

            logger.info(f"九域文化处理完成，生成 {len(batch.frameworks)} 个框架，{len(batch.entities)} 个实体")
            return batch

        except Exception as e:
            logger.error(f"九域文化处理失败: {e}")
            raise

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 清理多余空白
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        # 修复常见格式问题
        text = re.sub(r'([A-F])[\.、\s]*([^A-F\n]{2,})', r'\1. \2', text)

        # 规范化域标记
        for domain in self.domain_patterns.keys():
            text = re.sub(f'{domain}[｜|]+六维文化框架', f'{domain}｜六维文化框架', text)

        return text

    def _extract_domain_sections(self, text: str) -> Dict[str, str]:
        """提取域段落"""
        domain_sections = {}
        current_domain = None
        current_content = []

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测域标题
            domain_found = None
            for domain_name in self.domain_patterns.keys():
                # 匹配模式：人域｜六维文化框架 或 ## 人域 等
                if (f'{domain_name}｜' in line or
                    (line.startswith('#') and domain_name in line) or
                    (line.startswith(domain_name) and len(line.split()) <= 3)):
                    domain_found = domain_name
                    break

            if domain_found:
                # 保存前一个域
                if current_domain and current_content:
                    domain_sections[current_domain] = '\n'.join(current_content)

                # 开始新域
                current_domain = domain_found
                current_content = []
                logger.debug(f"发现域标题: {domain_found}")
            elif current_domain:
                current_content.append(line)

        # 保存最后一个域
        if current_domain and current_content:
            domain_sections[current_domain] = '\n'.join(current_content)

        logger.info(f"提取到 {len(domain_sections)} 个域段落")
        return domain_sections

    def _parse_domain_dimensions(self, domain_name: str, domain_text: str) -> List[CulturalSection]:
        """解析域的文化维度"""
        sections = []
        current_dimension = None
        current_content = []
        current_title = ""

        lines = domain_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测维度标记
            dimension_found = None
            title_found = ""

            # 匹配 A. 神话与宗教 格式
            dimension_match = re.match(r'^([A-F])[\.、\s]*(.+)', line)
            if dimension_match:
                dim_letter = dimension_match.group(1)
                dim_title = dimension_match.group(2)

                # 映射维度
                dimension_map = {
                    'A': CulturalDimension.MYTHOLOGY_RELIGION,
                    'B': CulturalDimension.POWER_LAW,
                    'C': CulturalDimension.ECONOMY_TECHNOLOGY,
                    'D': CulturalDimension.FAMILY_EDUCATION,
                    'E': CulturalDimension.RITUAL_DAILY,
                    'F': CulturalDimension.ART_ENTERTAINMENT
                }

                dimension_found = dimension_map.get(dim_letter)
                title_found = dim_title

            if dimension_found:
                # 保存前一个维度
                if current_dimension and current_content:
                    section = CulturalSection(
                        domain=DomainType(domain_name),
                        dimension=current_dimension,
                        title=current_title,
                        content='\n'.join(current_content),
                        raw_text='\n'.join([current_title] + current_content)
                    )
                    sections.append(section)

                # 开始新维度
                current_dimension = dimension_found
                current_title = title_found
                current_content = []
                logger.debug(f"发现维度: {domain_name} - {dimension_found.value}")
            elif current_dimension:
                current_content.append(line)

        # 保存最后一个维度
        if current_dimension and current_content:
            section = CulturalSection(
                domain=DomainType(domain_name),
                dimension=current_dimension,
                title=current_title,
                content='\n'.join(current_content),
                raw_text='\n'.join([current_title] + current_content)
            )
            sections.append(section)

        logger.info(f"{domain_name} 解析出 {len(sections)} 个维度段落")
        return sections

    async def _create_batch_data(self, cultural_sections: List[CulturalSection], novel_id: UUID) -> CulturalFrameworkBatch:
        """创建批量数据"""
        batch = CulturalFrameworkBatch()
        entity_registry = {}  # 避免重复实体

        for section in cultural_sections:
            # 1. 创建文化框架
            framework = self._create_framework(section, novel_id)
            batch.frameworks.append(framework)

            # 2. 提取实体
            entities = await self._extract_section_entities(section, novel_id, entity_registry)
            batch.entities.extend(entities)

            # 3. 识别剧情钩子
            plot_hooks = await self._extract_plot_hooks(section, novel_id)
            batch.plot_hooks.extend(plot_hooks)

        # 4. 提取概念词典
        all_text = '\n'.join([s.content for s in cultural_sections])
        concepts = await self._extract_cultural_concepts(all_text, novel_id)
        batch.concepts.extend(concepts)

        # 5. 分析实体关系
        relations = await self._analyze_entity_relations(batch.entities, novel_id)
        batch.relations.extend(relations)

        return batch

    def _create_framework(self, section: CulturalSection, novel_id: UUID) -> CulturalFrameworkCreate:
        """创建文化框架"""
        # 提取关键要素
        key_elements = self._extract_key_elements(section.content)

        # 生成摘要
        summary = self._generate_section_summary(section.content)

        # 提取标签
        tags = self._extract_section_tags(section)

        # 计算优先级
        priority = self._calculate_section_priority(section)

        return CulturalFrameworkCreate(
            novel_id=novel_id,
            domain_type=section.domain,
            dimension=section.dimension,
            title=f"{section.domain.value} - {section.dimension.value}",
            summary=summary,
            key_elements=key_elements,
            detailed_content=section.content,
            tags=tags,
            priority=priority
        )

    def _extract_key_elements(self, content: str) -> List[str]:
        """提取关键要素"""
        elements = []

        # 提取冒号前的关键词
        patterns = [
            r'([^，。！？：\n]{2,10})：',
            r'([^，。！？\n]{2,10})(?:是|为|指)',
            r'信条[：:]([^，。！？\n]+)',
            r'结构[：:]([^，。！？\n]+)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            elements.extend([match.strip() for match in matches if len(match.strip()) >= 2])

        # 去重并限制数量
        elements = list(dict.fromkeys(elements))[:8]
        return elements

    def _generate_section_summary(self, content: str, max_length: int = 150) -> str:
        """生成段落摘要"""
        # 提取前几句作为摘要
        sentences = re.split(r'[。！？]', content)
        summary = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break

        return summary.strip() or content[:max_length] + "..."

    def _extract_section_tags(self, section: CulturalSection) -> List[str]:
        """提取段落标签"""
        tags = [section.domain.value, section.dimension.value]

        # 基于内容提取标签
        content_tags = {
            "政治": ["政治", "权力", "统治", "管理", "法律"],
            "经济": ["经济", "货币", "贸易", "商业", "产业"],
            "宗教": ["信仰", "神", "祭祀", "宗教", "神话"],
            "技术": ["技术", "工艺", "法术", "技能", "制作"],
            "社会": ["社会", "制度", "阶层", "身份", "等级"],
            "文化": ["文化", "传统", "习俗", "艺术", "仪式"]
        }

        for tag, keywords in content_tags.items():
            if any(keyword in section.content for keyword in keywords):
                tags.append(tag)

        return tags

    def _calculate_section_priority(self, section: CulturalSection) -> int:
        """计算段落优先级"""
        priority = 5  # 基础值

        # 基于长度
        if len(section.content) > 500:
            priority += 1
        if len(section.content) > 1000:
            priority += 1

        # 基于重要关键词
        important_keywords = ["核心", "重要", "关键", "主要", "根本", "基础"]
        for keyword in important_keywords:
            if keyword in section.content:
                priority += 1
                break

        # 基于域重要性（人域作为核心域）
        if section.domain == DomainType.HUMAN_DOMAIN:
            priority += 1

        return min(priority, 10)

    async def _extract_section_entities(self, section: CulturalSection, novel_id: UUID, entity_registry: Dict[str, str]) -> List[CulturalEntityCreate]:
        """提取段落实体"""
        entities = []

        for rule in self.extraction_rules:
            for pattern in rule.patterns:
                matches = re.findall(pattern, section.content, re.IGNORECASE)

                for match in matches:
                    entity_name = match if isinstance(match, str) else match[0]
                    entity_name = entity_name.strip()

                    # 过滤太短或重复的实体
                    if len(entity_name) < 2 or entity_name in entity_registry:
                        continue

                    entity_registry[entity_name] = str(uuid4())

                    # 创建实体
                    entity = await self._create_cultural_entity(
                        entity_name, rule.entity_type, section, novel_id
                    )
                    entities.append(entity)

        return entities

    async def _create_cultural_entity(self, name: str, entity_type: EntityType, section: CulturalSection, novel_id: UUID) -> CulturalEntityCreate:
        """创建文化实体"""
        # 提取上下文
        context = self._extract_entity_context(section.content, name)

        # 提取特征
        characteristics = self._extract_entity_characteristics(context, entity_type, section.domain)

        # 提取功能
        functions = self._extract_entity_functions(context, entity_type)

        # 提取别名
        aliases = self._extract_entity_aliases(context, name)

        # 提取意义
        significance = self._extract_entity_significance(context, entity_type)

        return CulturalEntityCreate(
            novel_id=novel_id,
            name=name,
            entity_type=entity_type,
            domain_type=section.domain,
            dimensions=[section.dimension],
            description=context,
            characteristics=characteristics,
            functions=functions,
            significance=significance,
            aliases=aliases,
            tags=[section.domain.value, entity_type.value, section.dimension.value],
            references=[self._extract_reference_snippet(section.content, name)]
        )

    def _extract_entity_context(self, content: str, entity_name: str, window: int = 80) -> str:
        """提取实体上下文"""
        index = content.find(entity_name)
        if index == -1:
            return f"在{entity_name}相关内容中提及"

        start = max(0, index - window)
        end = min(len(content), index + len(entity_name) + window)

        context = content[start:end].strip()

        # 确保上下文完整性
        if start > 0 and not context.startswith('。'):
            # 找到前一个句号
            prev_period = content.rfind('。', 0, index)
            if prev_period != -1 and index - prev_period < window * 2:
                start = prev_period + 1
                context = content[start:end].strip()

        return context

    def _extract_entity_characteristics(self, context: str, entity_type: EntityType, domain: DomainType) -> Dict[str, Any]:
        """提取实体特征"""
        characteristics = {
            "entity_type": entity_type.value,
            "domain": domain.value
        }

        # 基于实体类型的特定特征
        if entity_type == EntityType.ORGANIZATION:
            if "王朝" in context:
                characteristics["governance_type"] = "王朝制"
            elif "议会" in context:
                characteristics["governance_type"] = "议会制"
            elif "殿" in context:
                characteristics["governance_type"] = "神权制"

            # 组织规模
            if any(word in context for word in ["大", "巨", "庞大"]):
                characteristics["scale"] = "大型"
            elif any(word in context for word in ["小", "微", "精"]):
                characteristics["scale"] = "小型"
            else:
                characteristics["scale"] = "中型"

        elif entity_type == EntityType.CONCEPT:
            if "制度" in context or "制" in context:
                characteristics["concept_category"] = "制度体系"
            elif "法则" in context or "术" in context:
                characteristics["concept_category"] = "技能法术"
            elif "籍" in context:
                characteristics["concept_category"] = "身份体系"

        elif entity_type == EntityType.ITEM:
            if "器" in context:
                characteristics["item_category"] = "器具类"
            elif "票" in context:
                characteristics["item_category"] = "凭证类"
            elif "印" in context:
                characteristics["item_category"] = "印章类"

        elif entity_type == EntityType.RITUAL:
            if "祭" in context:
                characteristics["ritual_type"] = "祭祀类"
            elif "礼" in context:
                characteristics["ritual_type"] = "礼仪类"
            elif "节" in context:
                characteristics["ritual_type"] = "节庆类"

        return characteristics

    def _extract_entity_functions(self, context: str, entity_type: EntityType) -> List[str]:
        """提取实体功能"""
        functions = []

        # 功能识别模式
        function_patterns = [
            r'(?:用于|用来|可以|能够|负责|主管|掌管)([^，。！？\n]{3,20})',
            r'(?:作用是|功能是|目的是|旨在)([^，。！？\n]{3,20})',
            r'(?:专门|主要|特别)([^，。！？\n]{3,20})',
        ]

        for pattern in function_patterns:
            matches = re.findall(pattern, context)
            functions.extend([match.strip() for match in matches])

        # 基于实体类型的默认功能
        if not functions:
            if entity_type == EntityType.ORGANIZATION:
                functions = ["组织管理", "权力行使"]
            elif entity_type == EntityType.CONCEPT:
                functions = ["概念界定", "体系规范"]
            elif entity_type == EntityType.ITEM:
                functions = ["物品使用", "价值体现"]
            elif entity_type == EntityType.RITUAL:
                functions = ["仪式举行", "文化传承"]

        return functions[:5]  # 限制数量

    def _extract_entity_aliases(self, context: str, entity_name: str) -> List[str]:
        """提取实体别名"""
        aliases = []

        # 别名识别模式
        alias_patterns = [
            fr'{entity_name}(?:又称|也称|别名|简称|俗称)([^，。！？\n]+)',
            fr'([^，。！？\n]+)(?:又称|也称|即|也就是){entity_name}',
            fr'所谓([^，。！？\n]+)[，。]?(?:即|就是){entity_name}',
        ]

        for pattern in alias_patterns:
            matches = re.findall(pattern, context)
            aliases.extend([match.strip() for match in matches if match.strip()])

        return aliases[:3]  # 限制数量

    def _extract_entity_significance(self, context: str, entity_type: EntityType) -> Optional[str]:
        """提取实体意义"""
        significance_patterns = [
            r'(?:重要性|意义|作用|价值)(?:在于|是|为)([^，。！？\n]{5,30})',
            r'(?:象征|代表|体现)(?:着|了)?([^，。！？\n]{5,30})',
            r'(?:核心|关键|重要)(?:的|之)([^，。！？\n]{5,30})',
        ]

        for pattern in significance_patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1).strip()

        return None

    def _extract_reference_snippet(self, content: str, entity_name: str, length: int = 60) -> str:
        """提取引用片段"""
        context = self._extract_entity_context(content, entity_name, length//2)
        if len(context) > length:
            return context[:length] + "..."
        return context

    async def _extract_plot_hooks(self, section: CulturalSection, novel_id: UUID) -> List[PlotHookCreate]:
        """提取剧情钩子"""
        hooks = []

        # 剧情钩子识别模式
        hook_indicators = [
            "冲突", "矛盾", "对立", "争议", "分歧", "问题",
            "危机", "挑战", "困境", "威胁", "机会",
            "秘密", "谜团", "神秘", "未知", "禁忌"
        ]

        sentences = re.split(r'[。！？]', section.content)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            # 检查是否包含钩子指示词
            hook_score = sum(1 for indicator in hook_indicators if indicator in sentence)

            if hook_score >= 1:  # 至少包含一个指示词
                hook = await self._create_plot_hook(sentence, section, novel_id, hook_score)
                hooks.append(hook)

        return hooks

    async def _create_plot_hook(self, content: str, section: CulturalSection, novel_id: UUID, complexity_hint: int) -> PlotHookCreate:
        """创建剧情钩子"""
        # 生成标题
        title = content[:50] + "..." if len(content) > 50 else content

        # 提取触发条件
        trigger_conditions = self._extract_trigger_conditions(content)

        # 提取可能结果
        potential_outcomes = self._extract_potential_outcomes(content)

        # 计算复杂度和影响力
        complexity_level = min(5 + complexity_hint, 10)
        story_impact = self._calculate_story_impact(content, section.domain)

        return PlotHookCreate(
            novel_id=novel_id,
            domain_type=section.domain,
            title=title,
            description=content,
            trigger_conditions=trigger_conditions,
            potential_outcomes=potential_outcomes,
            cultural_dimensions=[section.dimension],
            complexity_level=complexity_level,
            story_impact=story_impact,
            tags=[section.domain.value, "剧情钩子", section.dimension.value]
        )

    def _extract_trigger_conditions(self, content: str) -> List[str]:
        """提取触发条件"""
        conditions = []

        condition_patterns = [
            r'(?:当|如果|若|假如|一旦)([^，。！？\n]+)',
            r'(?:需要|要求|条件是)([^，。！？\n]+)',
            r'(?:前提|基础|依据)(?:是|为)([^，。！？\n]+)',
        ]

        for pattern in condition_patterns:
            matches = re.findall(pattern, content)
            conditions.extend([match.strip() for match in matches])

        return conditions[:3]

    def _extract_potential_outcomes(self, content: str) -> List[str]:
        """提取可能结果"""
        outcomes = []

        outcome_patterns = [
            r'(?:将会|可能|或许|结果|导致)([^，。！？\n]+)',
            r'(?:后果|影响|效果)(?:是|为)([^，。！？\n]+)',
            r'(?:最终|最后|终将)([^，。！？\n]+)',
        ]

        for pattern in outcome_patterns:
            matches = re.findall(pattern, content)
            outcomes.extend([match.strip() for match in matches])

        return outcomes[:3]

    def _calculate_story_impact(self, content: str, domain: DomainType) -> int:
        """计算故事影响力"""
        impact = 5

        # 影响力关键词
        high_impact_keywords = ["重大", "关键", "决定性", "核心", "根本"]
        medium_impact_keywords = ["重要", "主要", "显著", "明显"]

        for keyword in high_impact_keywords:
            if keyword in content:
                impact += 2
                break
        else:
            for keyword in medium_impact_keywords:
                if keyword in content:
                    impact += 1
                    break

        # 域权重
        domain_weights = {
            DomainType.HUMAN_DOMAIN: 1,
            DomainType.HEAVEN_DOMAIN: 2,
            DomainType.DEMON_DOMAIN: 2,
            DomainType.VOID_DOMAIN: 1,
            DomainType.SOURCE_DOMAIN: 2,
        }

        impact += domain_weights.get(domain, 0)

        return min(impact, 10)

    async def _extract_cultural_concepts(self, text: str, novel_id: UUID) -> List[ConceptDictionaryCreate]:
        """提取文化概念"""
        concepts = []

        # 九域特有概念
        nine_domains_concepts = {
            # 核心概念
            "法则链": "power_system",
            "链籍": "identity_system",
            "断链术": "forbidden_technique",
            "环印": "authentication_item",
            "裂世": "world_structure",

            # 人域概念
            "环祖": "ancestor_worship",
            "乡祭": "local_priest",
            "三等制": "social_hierarchy",
            "缚司": "law_enforcement",
            "巡链司": "imperial_oversight",

            # 天域概念
            "天命王朝": "imperial_dynasty",
            "龙阙": "imperial_palace",
            "司天监": "astronomical_bureau",

            # 冥域概念
            "冥司殿": "underworld_court",
            "渡链僧": "soul_guide_monk",
            "镇魂器": "soul_binding_artifact",
            "归环文": "death_ritual_text",

            # 魔域概念
            "血契": "blood_pact",
            "魔祭": "demonic_sacrifice",
            "噬魂": "soul_devouring",

            # 虚域概念
            "虚空": "void_space",
            "无为": "non_action_philosophy",
            "空明": "emptiness_enlightenment",

            # 海域概念
            "港市": "port_city",
            "潮汐": "tidal_patterns",

            # 源域概念
            "守源会": "source_guardian_order",
            "源流": "origin_stream",
            "古籍": "ancient_texts",
        }

        for term, category in nine_domains_concepts.items():
            if term in text:
                # 提取定义
                definition = self._extract_concept_definition(text, term)

                # 提取使用示例
                usage_examples = self._extract_concept_usage(text, term)

                # 识别所属域
                domain_type = self._identify_concept_domain(text, term)

                # 计算重要性
                importance = self._calculate_concept_importance(text, term, category)

                concept = ConceptDictionaryCreate(
                    novel_id=novel_id,
                    term=term,
                    definition=definition,
                    category=category,
                    domain_type=domain_type,
                    usage_examples=usage_examples,
                    frequency=text.count(term),
                    importance=importance
                )
                concepts.append(concept)

        return concepts

    def _extract_concept_definition(self, text: str, term: str) -> str:
        """提取概念定义"""
        # 定义模式
        definition_patterns = [
            fr'{term}[：:]([^，。！？\n]+)',
            fr'{term}(?:是|指|表示|代表)([^，。！？\n]+)',
            fr'所谓{term}[，：]([^，。！？\n]+)',
            fr'{term}[，]?即([^，。！？\n]+)',
        ]

        for pattern in definition_patterns:
            match = re.search(pattern, text)
            if match:
                definition = match.group(1).strip()
                if len(definition) > 10:  # 确保定义有意义
                    return definition

        # 如果没找到明确定义，提取上下文
        context = self._extract_entity_context(text, term, 40)
        return context or f"{term}是九域文化体系中的重要概念"

    def _extract_concept_usage(self, text: str, term: str) -> List[str]:
        """提取概念使用示例"""
        examples = []

        # 找到包含术语的句子
        sentences = re.split(r'[。！？]', text)
        for sentence in sentences:
            if term in sentence and len(sentence.strip()) > 15:
                examples.append(sentence.strip())
                if len(examples) >= 3:
                    break

        return examples

    def _identify_concept_domain(self, text: str, term: str) -> Optional[DomainType]:
        """识别概念所属域"""
        context = self._extract_entity_context(text, term, 200)

        # 域特征词汇
        domain_indicators = {
            DomainType.HUMAN_DOMAIN: ["链籍", "环祖", "县府", "乡祭"],
            DomainType.HEAVEN_DOMAIN: ["天命", "龙阙", "帝都", "王朝"],
            DomainType.UNDERWORLD_DOMAIN: ["冥司", "亡魂", "镇魂", "渡链"],
            DomainType.DEMON_DOMAIN: ["血契", "魔祭", "噬魂", "血池"],
            DomainType.VOID_DOMAIN: ["虚空", "无为", "空明", "超脱"],
            DomainType.SEA_DOMAIN: ["港市", "潮汐", "航海", "海族"],
            DomainType.SOURCE_DOMAIN: ["守源", "源流", "古籍", "起源"],
        }

        max_score = 0
        identified_domain = None

        for domain, indicators in domain_indicators.items():
            score = sum(1 for indicator in indicators if indicator in context)
            if score > max_score:
                max_score = score
                identified_domain = domain

        return identified_domain

    def _calculate_concept_importance(self, text: str, term: str, category: str) -> int:
        """计算概念重要性"""
        importance = 5

        # 基于频率
        frequency = text.count(term)
        if frequency >= 5:
            importance += 2
        elif frequency >= 3:
            importance += 1

        # 基于类别
        high_importance_categories = ["power_system", "identity_system", "world_structure"]
        if category in high_importance_categories:
            importance += 2

        # 基于上下文重要性关键词
        context = self._extract_entity_context(text, term, 100)
        importance_keywords = ["核心", "重要", "关键", "基础", "根本"]
        for keyword in importance_keywords:
            if keyword in context:
                importance += 1
                break

        return min(importance, 10)

    async def _analyze_entity_relations(self, entities: List[CulturalEntityCreate], novel_id: UUID) -> List[CulturalRelationCreate]:
        """分析实体关系"""
        relations = []

        # 创建实体映射
        entity_map = {entity.name: entity for entity in entities}

        for i, source_entity in enumerate(entities):
            for j, target_entity in enumerate(entities):
                if i >= j:  # 避免重复和自关联
                    continue

                # 分析关系
                relation_info = self._analyze_entity_pair_relation(
                    source_entity, target_entity
                )

                if relation_info["relation_type"]:
                    relation = CulturalRelationCreate(
                        novel_id=novel_id,
                        source_entity_id=uuid4(),  # 临时ID
                        target_entity_id=uuid4(),  # 临时ID
                        relation_type=relation_info["relation_type"],
                        description=relation_info["description"],
                        strength=relation_info["strength"],
                        context=relation_info["context"],
                        is_cross_domain=(source_entity.domain_type != target_entity.domain_type),
                        source_domain=source_entity.domain_type,
                        target_domain=target_entity.domain_type
                    )
                    relations.append(relation)

        return relations

    def _analyze_entity_pair_relation(self, entity1: CulturalEntityCreate, entity2: CulturalEntityCreate) -> Dict[str, Any]:
        """分析实体对关系"""
        # 合并描述文本
        combined_text = f"{entity1.description} {entity2.description}"

        # 关系模式匹配
        relation_patterns = {
            RelationType.CONTROLS: [
                rf'{entity1.name}.*(?:控制|管理|统治|掌管).*{entity2.name}',
                rf'{entity2.name}.*(?:受|被).*{entity1.name}.*(?:控制|管理)',
            ],
            RelationType.CONTAINS: [
                rf'{entity1.name}.*(?:包含|含有|设有).*{entity2.name}',
                rf'{entity2.name}.*(?:属于|隶属于|设在).*{entity1.name}',
            ],
            RelationType.CONFLICTS_WITH: [
                rf'{entity1.name}.*(?:与|和).*{entity2.name}.*(?:冲突|对立|敌对)',
                rf'{entity1.name}.*(?:反对|抵制|对抗).*{entity2.name}',
            ],
            RelationType.DERIVED_FROM: [
                rf'{entity1.name}.*(?:来源于|源自|衍生自).*{entity2.name}',
                rf'{entity1.name}.*(?:由|从).*{entity2.name}.*(?:发展|演化|产生)',
            ],
            RelationType.INFLUENCED_BY: [
                rf'{entity1.name}.*(?:受到|受).*{entity2.name}.*(?:影响|感化)',
                rf'{entity2.name}.*(?:影响|感化).*{entity1.name}',
            ],
        }

        for relation_type, patterns in relation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return {
                        "relation_type": relation_type,
                        "description": f"{entity1.name}与{entity2.name}存在{relation_type.value}关系",
                        "strength": 0.8,
                        "context": combined_text[:100] + "..."
                    }

        # 检查域内关系
        if entity1.domain_type == entity2.domain_type:
            # 同维度关系
            if any(dim in entity2.dimensions for dim in entity1.dimensions):
                return {
                    "relation_type": RelationType.RELATED_TO,
                    "description": f"{entity1.name}与{entity2.name}在同一文化维度中相关",
                    "strength": 0.6,
                    "context": "同域同维度关系"
                }

            # 同域关系
            return {
                "relation_type": RelationType.RELATED_TO,
                "description": f"{entity1.name}与{entity2.name}属于同一域",
                "strength": 0.4,
                "context": "同域关系"
            }

        return {"relation_type": None, "description": "", "strength": 0.0, "context": ""}

    async def _enhance_batch_data(self, batch: CulturalFrameworkBatch, original_text: str) -> CulturalFrameworkBatch:
        """增强批量数据质量"""
        # 1. 去重处理
        batch = self._deduplicate_batch_data(batch)

        # 2. 增强实体描述
        batch = await self._enhance_entity_descriptions(batch, original_text)

        # 3. 完善关系网络
        batch = await self._enhance_relationship_network(batch)

        # 4. 优化标签和分类
        batch = self._optimize_tags_and_categories(batch)

        return batch

    def _deduplicate_batch_data(self, batch: CulturalFrameworkBatch) -> CulturalFrameworkBatch:
        """去重处理"""
        # 实体去重
        seen_entities = set()
        unique_entities = []

        for entity in batch.entities:
            entity_key = f"{entity.name}_{entity.entity_type.value}"
            if entity_key not in seen_entities:
                seen_entities.add(entity_key)
                unique_entities.append(entity)

        batch.entities = unique_entities

        # 概念去重
        seen_concepts = set()
        unique_concepts = []

        for concept in batch.concepts:
            if concept.term not in seen_concepts:
                seen_concepts.add(concept.term)
                unique_concepts.append(concept)

        batch.concepts = unique_concepts

        return batch

    async def _enhance_entity_descriptions(self, batch: CulturalFrameworkBatch, original_text: str) -> CulturalFrameworkBatch:
        """增强实体描述"""
        for entity in batch.entities:
            # 扩展描述
            extended_context = self._extract_entity_context(original_text, entity.name, 150)
            if len(extended_context) > len(entity.description):
                entity.description = extended_context

            # 增强特征
            additional_chars = self._extract_additional_characteristics(original_text, entity.name)
            entity.characteristics.update(additional_chars)

        return batch

    def _extract_additional_characteristics(self, text: str, entity_name: str) -> Dict[str, Any]:
        """提取额外特征"""
        characteristics = {}
        context = self._extract_entity_context(text, entity_name, 200)

        # 时间特征
        time_patterns = [
            r'(?:古代|古时|远古|上古)',
            r'(?:现代|当前|如今|现在)',
            r'(?:传统|古老|悠久)',
        ]

        for pattern in time_patterns:
            if re.search(pattern, context):
                characteristics["temporal_context"] = pattern.strip('(?:)')
                break

        # 规模特征
        scale_patterns = [
            r'(?:庞大|巨大|宏大)',
            r'(?:小型|微型|精小)',
            r'(?:中等|适中)',
        ]

        for pattern in scale_patterns:
            if re.search(pattern, context):
                characteristics["scale_description"] = pattern.strip('(?:)')
                break

        return characteristics

    async def _enhance_relationship_network(self, batch: CulturalFrameworkBatch) -> CulturalFrameworkBatch:
        """完善关系网络"""
        # 分析跨域关系
        cross_domain_relations = []

        for relation in batch.relations:
            if relation.is_cross_domain:
                # 为跨域关系添加更多上下文
                relation.context = f"跨域关系：{relation.source_domain.value} - {relation.target_domain.value}"
                cross_domain_relations.append(relation)

        # 添加隐含关系
        implicit_relations = self._discover_implicit_relations(batch.entities)
        batch.relations.extend(implicit_relations)

        return batch

    def _discover_implicit_relations(self, entities: List[CulturalEntityCreate]) -> List[CulturalRelationCreate]:
        """发现隐含关系"""
        implicit_relations = []

        # 同类实体关系
        entity_groups = {}
        for entity in entities:
            key = f"{entity.entity_type.value}_{entity.domain_type.value if entity.domain_type else 'unknown'}"
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)

        # 为同组实体建立相似关系
        for group_entities in entity_groups.values():
            if len(group_entities) > 1:
                for i, entity1 in enumerate(group_entities):
                    for entity2 in group_entities[i+1:]:
                        relation = CulturalRelationCreate(
                            novel_id=entity1.novel_id,
                            source_entity_id=uuid4(),
                            target_entity_id=uuid4(),
                            relation_type=RelationType.SIMILAR_TO,
                            description=f"{entity1.name}与{entity2.name}同属{entity1.entity_type.value}",
                            strength=0.5,
                            context="同类实体关系",
                            is_cross_domain=entity1.domain_type != entity2.domain_type,
                            source_domain=entity1.domain_type,
                            target_domain=entity2.domain_type
                        )
                        implicit_relations.append(relation)

        return implicit_relations

    def _optimize_tags_and_categories(self, batch: CulturalFrameworkBatch) -> CulturalFrameworkBatch:
        """优化标签和分类"""
        # 统一标签格式
        for entity in batch.entities:
            entity.tags = list(set(entity.tags))  # 去重
            entity.tags.sort()  # 排序

        for concept in batch.concepts:
            # 为概念添加额外标签
            if "制" in concept.term:
                concept.category = "制度体系"
            elif "术" in concept.term:
                concept.category = "技术法术"
            elif "籍" in concept.term:
                concept.category = "身份体系"

        return batch

    async def _validate_cultural_data(self, batch: CulturalFrameworkBatch) -> Dict[str, Any]:
        """验证文化数据"""
        errors = []
        warnings = []

        # 1. 基础验证
        if not batch.frameworks:
            errors.append("未解析到文化框架数据")

        if not batch.entities:
            warnings.append("未解析到文化实体")

        # 2. 九域完整性验证
        covered_domains = set(f.domain_type for f in batch.frameworks)
        missing_domains = set(DomainType) - covered_domains
        if missing_domains:
            warnings.append(f"缺少域数据: {[d.value for d in missing_domains]}")

        # 3. 六维完整性验证
        covered_dimensions = set(f.dimension for f in batch.frameworks)
        missing_dimensions = set(CulturalDimension) - covered_dimensions
        if missing_dimensions:
            warnings.append(f"缺少维度数据: {[d.value for d in missing_dimensions]}")

        # 4. 实体名称验证
        entity_names = [e.name for e in batch.entities]
        duplicate_names = [name for name in set(entity_names) if entity_names.count(name) > 1]
        if duplicate_names:
            warnings.append(f"重复实体名称: {duplicate_names}")

        # 5. 关系有效性验证
        for relation in batch.relations:
            if relation.strength < 0 or relation.strength > 1:
                errors.append(f"关系强度超出范围: {relation.strength}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "statistics": {
                "domains_covered": len(covered_domains),
                "dimensions_covered": len(covered_dimensions),
                "entities_extracted": len(batch.entities),
                "relations_found": len(batch.relations),
                "concepts_identified": len(batch.concepts),
                "plot_hooks_extracted": len(batch.plot_hooks)
            }
        }