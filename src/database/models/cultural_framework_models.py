"""
文化框架数据模型 - 六维文化体系、实体关系、剧情钩子
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator

from .core_models import BaseModelWithTimestamp


class DomainType(str, Enum):
    """裂世九域类型枚举"""
    HUMAN_DOMAIN = "人域"
    HEAVEN_DOMAIN = "天域"
    WILD_DOMAIN = "荒域"
    UNDERWORLD_DOMAIN = "冥域"
    DEMON_DOMAIN = "魔域"
    VOID_DOMAIN = "虚域"
    SEA_DOMAIN = "海域"
    SOURCE_DOMAIN = "源域"


class CulturalDimension(str, Enum):
    """六维文化枚举"""
    MYTHOLOGY_RELIGION = "神话与宗教"  # A维度
    POWER_LAW = "权力与法律"         # B维度
    ECONOMY_TECHNOLOGY = "经济与技术"  # C维度
    FAMILY_EDUCATION = "家庭与教育"   # D维度
    RITUAL_DAILY = "仪式与日常"      # E维度
    ART_ENTERTAINMENT = "艺术与娱乐"  # F维度


class EntityType(str, Enum):
    """文化实体类型枚举"""
    ORGANIZATION = "组织机构"
    CONCEPT = "重要概念"
    ITEM = "文化物品"
    RITUAL = "仪式活动"
    SYSTEM = "身份制度"
    CURRENCY = "货币体系"
    TECHNOLOGY = "技术工艺"
    BELIEF = "信仰体系"
    CUSTOM = "习俗传统"


class RelationType(str, Enum):
    """关系类型枚举"""
    CONTAINS = "包含"
    RELATED_TO = "关联"
    CONFLICTS_WITH = "冲突"
    DERIVED_FROM = "衍生自"
    CONTROLS = "控制"
    INFLUENCED_BY = "受影响于"
    SIMILAR_TO = "相似于"


class CulturalFramework(BaseModelWithTimestamp):
    """文化框架主模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    domain_type: DomainType = Field(..., description="所属域")
    dimension: CulturalDimension = Field(..., description="文化维度")

    # 结构化数据
    title: str = Field(..., min_length=1, max_length=500, description="标题")
    summary: Optional[str] = Field(None, description="概要描述")
    key_elements: List[str] = Field(default_factory=list, description="关键要素列表")
    detailed_content: str = Field(..., description="详细内容")

    # 元数据
    tags: List[str] = Field(default_factory=list, description="标签")
    priority: int = Field(default=5, ge=1, le=10, description="重要性等级")
    completion_status: float = Field(default=1.0, ge=0.0, le=1.0, description="完整度")

    @validator('title')
    def validate_title(cls, v):
        if not v or v.isspace():
            raise ValueError('标题不能为空')
        return v.strip()


class CulturalEntity(BaseModelWithTimestamp):
    """文化实体模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    framework_id: Optional[UUID] = Field(None, description="关联的文化框架ID")

    # 基本信息
    name: str = Field(..., min_length=1, max_length=255, description="实体名称")
    entity_type: EntityType = Field(..., description="实体类型")
    domain_type: Optional[DomainType] = Field(None, description="所属域")
    dimensions: List[CulturalDimension] = Field(default_factory=list, description="关联的文化维度")

    # 详细信息
    description: str = Field(..., description="详细描述")
    characteristics: Dict[str, Any] = Field(default_factory=dict, description="特征属性")
    functions: List[str] = Field(default_factory=list, description="功能作用")
    significance: Optional[str] = Field(None, description="重要意义")

    # 上下文信息
    origin_story: Optional[str] = Field(None, description="起源故事")
    historical_context: Optional[str] = Field(None, description="历史背景")
    current_status: Optional[str] = Field(None, description="当前状态")

    # 元数据
    aliases: List[str] = Field(default_factory=list, description="别名")
    tags: List[str] = Field(default_factory=list, description="标签")
    text_references: List[str] = Field(default_factory=list, description="引用文本片段")

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('实体名称不能为空')
        return v.strip()


class CulturalRelation(BaseModelWithTimestamp):
    """文化实体关系模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")

    # 关系双方
    source_entity_id: UUID = Field(..., description="源实体ID")
    target_entity_id: UUID = Field(..., description="目标实体ID")
    relation_type: RelationType = Field(..., description="关系类型")

    # 关系描述
    description: Optional[str] = Field(None, description="关系描述")
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="关系强度")
    context: Optional[str] = Field(None, description="关系上下文")

    # 跨域关系标识
    is_cross_domain: bool = Field(default=False, description="是否为跨域关系")
    source_domain: Optional[DomainType] = Field(None, description="源域")
    target_domain: Optional[DomainType] = Field(None, description="目标域")


class PlotHook(BaseModelWithTimestamp):
    """剧情钩子模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    domain_type: DomainType = Field(..., description="所属域")

    # 钩子内容
    title: str = Field(..., min_length=1, max_length=500, description="钩子标题")
    description: str = Field(..., description="钩子描述")
    trigger_conditions: List[str] = Field(default_factory=list, description="触发条件")
    potential_outcomes: List[str] = Field(default_factory=list, description="可能结果")

    # 关联文化元素
    related_entities: List[UUID] = Field(default_factory=list, description="相关实体ID列表")
    cultural_dimensions: List[CulturalDimension] = Field(default_factory=list, description="涉及的文化维度")

    # 元数据
    complexity_level: int = Field(default=5, ge=1, le=10, description="复杂度等级")
    story_impact: int = Field(default=5, ge=1, le=10, description="故事影响力")
    tags: List[str] = Field(default_factory=list, description="标签")

    @validator('title')
    def validate_title(cls, v):
        if not v or v.isspace():
            raise ValueError('钩子标题不能为空')
        return v.strip()


class ConceptDictionary(BaseModelWithTimestamp):
    """概念词典模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")

    # 概念信息
    term: str = Field(..., min_length=1, max_length=255, description="术语")
    definition: str = Field(..., description="定义")
    category: str = Field(..., max_length=100, description="分类")
    domain_type: Optional[DomainType] = Field(None, description="所属域")

    # 详细信息
    etymology: Optional[str] = Field(None, description="词源")
    usage_examples: List[str] = Field(default_factory=list, description="使用示例")
    related_terms: List[str] = Field(default_factory=list, description="相关术语")

    # 元数据
    frequency: int = Field(default=1, ge=1, description="出现频率")
    importance: int = Field(default=5, ge=1, le=10, description="重要程度")

    @validator('term')
    def validate_term(cls, v):
        if not v or v.isspace():
            raise ValueError('术语不能为空')
        return v.strip()


# 创建请求/响应模型
class CulturalFrameworkCreate(BaseModel):
    """创建文化框架请求模型"""
    novel_id: UUID
    domain_type: DomainType
    dimension: CulturalDimension
    title: str = Field(..., min_length=1, max_length=500)
    summary: Optional[str] = None
    key_elements: List[str] = Field(default_factory=list)
    detailed_content: str
    tags: List[str] = Field(default_factory=list)
    priority: int = Field(default=5, ge=1, le=10)


class CulturalEntityCreate(BaseModel):
    """创建文化实体请求模型"""
    novel_id: UUID
    framework_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    entity_type: EntityType
    domain_type: Optional[DomainType] = None
    dimensions: List[CulturalDimension] = Field(default_factory=list)
    description: str
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    functions: List[str] = Field(default_factory=list)
    significance: Optional[str] = None
    origin_story: Optional[str] = None
    historical_context: Optional[str] = None
    current_status: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    text_references: List[str] = Field(default_factory=list)


class CulturalRelationCreate(BaseModel):
    """创建文化关系请求模型"""
    novel_id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    relation_type: RelationType
    description: Optional[str] = None
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    context: Optional[str] = None
    is_cross_domain: bool = Field(default=False)
    source_domain: Optional[DomainType] = None
    target_domain: Optional[DomainType] = None


class PlotHookCreate(BaseModel):
    """创建剧情钩子请求模型"""
    novel_id: UUID
    domain_type: DomainType
    title: str = Field(..., min_length=1, max_length=500)
    description: str
    trigger_conditions: List[str] = Field(default_factory=list)
    potential_outcomes: List[str] = Field(default_factory=list)
    related_entities: List[UUID] = Field(default_factory=list)
    cultural_dimensions: List[CulturalDimension] = Field(default_factory=list)
    complexity_level: int = Field(default=5, ge=1, le=10)
    story_impact: int = Field(default=5, ge=1, le=10)
    tags: List[str] = Field(default_factory=list)


class ConceptDictionaryCreate(BaseModel):
    """创建概念词典请求模型"""
    novel_id: UUID
    term: str = Field(..., min_length=1, max_length=255)
    definition: str
    category: str = Field(..., max_length=100)
    domain_type: Optional[DomainType] = None
    etymology: Optional[str] = None
    usage_examples: List[str] = Field(default_factory=list)
    related_terms: List[str] = Field(default_factory=list)
    frequency: int = Field(default=1, ge=1)
    importance: int = Field(default=5, ge=1, le=10)


# 批量处理模型
class CulturalFrameworkBatch(BaseModel):
    """批量文化框架数据"""
    frameworks: List[CulturalFrameworkCreate] = Field(default_factory=list)
    entities: List[CulturalEntityCreate] = Field(default_factory=list)
    relations: List[CulturalRelationCreate] = Field(default_factory=list)
    plot_hooks: List[PlotHookCreate] = Field(default_factory=list)
    concepts: List[ConceptDictionaryCreate] = Field(default_factory=list)


# 查询和响应模型
class CulturalFrameworkQuery(BaseModel):
    """文化框架查询模型"""
    novel_id: Optional[UUID] = None
    domain_type: Optional[DomainType] = None
    dimension: Optional[CulturalDimension] = None
    tags: Optional[List[str]] = None
    priority_min: Optional[int] = None
    priority_max: Optional[int] = None


class CulturalEntityQuery(BaseModel):
    """文化实体查询模型"""
    novel_id: Optional[UUID] = None
    entity_type: Optional[EntityType] = None
    domain_type: Optional[DomainType] = None
    dimensions: Optional[List[CulturalDimension]] = None
    tags: Optional[List[str]] = None
    name_search: Optional[str] = None


class CrossDomainAnalysis(BaseModel):
    """跨域分析结果模型"""
    novel_id: UUID
    domain_relationships: Dict[str, List[Dict[str, Any]]]
    conflict_points: List[Dict[str, Any]]
    cultural_exchanges: List[Dict[str, Any]]
    shared_concepts: List[Dict[str, Any]]
    analysis_summary: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)