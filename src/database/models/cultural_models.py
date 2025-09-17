"""
文化框架数据模型定义
扩展原有models.py，添加文化框架相关模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .models import BaseDBModel


# =============================================================================
# 文化框架相关枚举
# =============================================================================

class DimensionType(str, Enum):
    CULTURAL = "cultural"
    SOCIAL = "social"
    ECONOMIC = "economic"
    POLITICAL = "political"


class ElementType(str, Enum):
    INSTITUTION = "institution"
    BELIEF = "belief"
    PRACTICE = "practice"
    RULE = "rule"
    TRADITION = "tradition"
    SYMBOL = "symbol"
    TABOO = "taboo"
    RITUAL = "ritual"


class ConflictType(str, Enum):
    VALUE = "value"
    PRACTICE = "practice"
    TERRITORY = "territory"
    RESOURCE = "resource"
    POWER = "power"
    RELIGIOUS = "religious"


class EvolutionType(str, Enum):
    GRADUAL = "gradual"
    REVOLUTIONARY = "revolutionary"
    IMPOSED = "imposed"
    NATURAL = "natural"


class HookType(str, Enum):
    CONFLICT = "conflict"
    MYSTERY = "mystery"
    DISCOVERY = "discovery"
    CRISIS = "crisis"
    OPPORTUNITY = "opportunity"
    BETRAYAL = "betrayal"


# =============================================================================
# PostgreSQL 模型（结构化数据）
# =============================================================================

class Domain(BaseDBModel):
    """域模型"""
    novel_id: int = Field(..., description="所属小说ID")
    name: str = Field(..., max_length=50, description="域名")
    code: str = Field(..., max_length=20, description="域代码")
    display_name: str = Field(..., max_length=100, description="显示名称")

    # 域的核心特征
    dominant_law: Optional[str] = Field(None, max_length=100, description="主导法则链")
    ruling_power: Optional[str] = Field(None, max_length=100, description="统治力量")

    # 域的基本属性
    power_level: int = Field(1, description="力量等级")
    civilization_level: int = Field(1, description="文明等级")
    stability_level: int = Field(5, description="稳定程度")

    # 地理和环境
    geographic_features: Dict[str, Any] = Field(default_factory=dict, description="地理特征")
    climate_info: Dict[str, Any] = Field(default_factory=dict, description="气候信息")
    resources: Dict[str, Any] = Field(default_factory=dict, description="资源分布")

    # 域间关系
    allied_domains: List[str] = Field(default_factory=list, description="盟友域")
    hostile_domains: List[str] = Field(default_factory=list, description="敌对域")
    trade_partners: List[str] = Field(default_factory=list, description="贸易伙伴")

    # 元数据
    sort_order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否激活")

    @validator('power_level', 'civilization_level')
    def validate_levels(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('等级必须在1-10之间')
        return v

    @validator('stability_level')
    def validate_stability(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('稳定度必须在1-10之间')
        return v


class CulturalDimension(BaseDBModel):
    """文化维度模型"""
    code: str = Field(..., max_length=20, description="维度代码")
    name: str = Field(..., max_length=50, description="维度名称")
    display_name: str = Field(..., max_length=100, description="显示名称")
    description: Optional[str] = Field(None, description="维度描述")

    # 维度特征
    dimension_type: DimensionType = Field(DimensionType.CULTURAL, description="维度类型")
    importance_weight: int = Field(5, description="重要性权重")

    # 维度的标准要素类型
    standard_elements: Dict[str, Any] = Field(default_factory=dict, description="标准要素模板")

    # 排序和状态
    sort_order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否激活")

    @validator('importance_weight')
    def validate_weight(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('重要性权重必须在1-10之间')
        return v


class CulturalFramework(BaseDBModel):
    """文化框架模型"""
    novel_id: int = Field(..., description="所属小说ID")
    domain_id: int = Field(..., description="域ID")
    dimension_id: int = Field(..., description="维度ID")

    # 框架基础信息
    framework_name: Optional[str] = Field(None, max_length=200, description="框架名称")
    version: str = Field("1.0", max_length=20, description="版本")

    # 框架概要
    core_concept: Optional[str] = Field(None, description="核心理念")
    key_features: Dict[str, Any] = Field(default_factory=dict, description="关键特征")

    # 框架状态
    completeness_score: int = Field(0, description="完整度评分")
    last_reviewed: Optional[datetime] = Field(None, description="最后审查时间")

    @validator('completeness_score')
    def validate_completeness(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('完整度评分必须在0-100之间')
        return v


class CulturalElement(BaseDBModel):
    """文化要素模型"""
    novel_id: int = Field(..., description="所属小说ID")
    framework_id: int = Field(..., description="文化框架ID")

    # 要素基础信息
    element_type: ElementType = Field(..., description="要素类型")
    name: str = Field(..., max_length=200, description="要素名称")
    code: Optional[str] = Field(None, max_length=100, description="要素代码")

    # 要素分类
    category: Optional[str] = Field(None, max_length=50, description="二级分类")
    subcategory: Optional[str] = Field(None, max_length=50, description="三级分类")

    # 要素属性
    attributes: Dict[str, Any] = Field(default_factory=dict, description="要素的具体属性")
    importance: int = Field(1, description="重要性")
    influence_scope: str = Field("local", max_length=20, description="影响范围")

    # 要素状态
    status: str = Field("active", max_length=20, description="状态")

    # 关联信息
    related_entities: List[str] = Field(default_factory=list, description="关联的实体ID")
    parent_element_id: Optional[int] = Field(None, description="父要素ID")

    # 时间信息
    established_time: Optional[str] = Field(None, max_length=100, description="建立时间")
    active_period: Optional[str] = Field(None, max_length=100, description="活跃期间")

    # 元数据
    tags: List[str] = Field(default_factory=list, description="标签")

    @validator('importance')
    def validate_importance(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('重要性必须在1-10之间')
        return v


class PlotHook(BaseDBModel):
    """剧情钩子模型"""
    novel_id: int = Field(..., description="所属小说ID")

    # 钩子关联
    domain_id: Optional[int] = Field(None, description="域ID")
    framework_id: Optional[int] = Field(None, description="文化框架ID")
    element_id: Optional[int] = Field(None, description="文化要素ID")

    # 钩子基础信息
    title: str = Field(..., max_length=200, description="钩子标题")
    description: str = Field(..., description="钩子描述")
    hook_type: HookType = Field(..., description="钩子类型")

    # 钩子属性
    drama_level: int = Field(5, description="戏剧性水平")
    scope: str = Field("local", max_length=20, description="影响范围")
    urgency_level: int = Field(3, description="紧急程度")

    # 参与角色
    involved_entities: List[str] = Field(default_factory=list, description="涉及的实体ID")
    required_capabilities: List[str] = Field(default_factory=list, description="需要的能力或资源")

    # 剧情发展
    potential_outcomes: Dict[str, Any] = Field(default_factory=dict, description="可能的结果")
    follow_up_hooks: List[str] = Field(default_factory=list, description="后续钩子")

    # 使用状态
    status: str = Field("available", max_length=20, description="使用状态")
    used_in_events: List[str] = Field(default_factory=list, description="已用于的事件ID")

    @validator('drama_level')
    def validate_drama(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('戏剧性水平必须在1-10之间')
        return v

    @validator('urgency_level')
    def validate_urgency(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('紧急程度必须在1-5之间')
        return v


class CulturalConflict(BaseDBModel):
    """文化冲突模型"""
    novel_id: int = Field(..., description="所属小说ID")

    # 冲突双方
    primary_domain_id: Optional[int] = Field(None, description="主要域ID")
    secondary_domain_id: Optional[int] = Field(None, description="次要域ID")
    primary_element_id: Optional[int] = Field(None, description="主要要素ID")
    secondary_element_id: Optional[int] = Field(None, description="次要要素ID")

    # 冲突信息
    conflict_type: ConflictType = Field(..., description="冲突类型")
    conflict_name: str = Field(..., max_length=200, description="冲突名称")
    description: Optional[str] = Field(None, description="冲突描述")

    # 冲突特征
    intensity_level: int = Field(3, description="冲突强度")
    historical_depth: int = Field(1, description="历史深度")
    resolution_difficulty: int = Field(5, description="解决难度")

    # 冲突状态
    status: str = Field("ongoing", max_length=20, description="冲突状态")
    current_manifestation: Optional[str] = Field(None, description="当前表现形式")

    # 影响分析
    affected_areas: Dict[str, Any] = Field(default_factory=dict, description="受影响的领域")
    stakeholders: List[str] = Field(default_factory=list, description="利益相关者")

    @validator('intensity_level', 'resolution_difficulty')
    def validate_levels(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('等级必须在1-10之间')
        return v


class CulturalEvolution(BaseDBModel):
    """文化变迁模型"""
    novel_id: int = Field(..., description="所属小说ID")

    # 变迁目标
    domain_id: Optional[int] = Field(None, description="域ID")
    element_id: Optional[int] = Field(None, description="要素ID")

    # 变迁信息
    evolution_type: EvolutionType = Field(..., description="变迁类型")
    change_name: str = Field(..., max_length=200, description="变迁名称")
    description: Optional[str] = Field(None, description="变迁描述")

    # 变迁前后状态
    before_state: Dict[str, Any] = Field(default_factory=dict, description="变迁前状态")
    after_state: Dict[str, Any] = Field(default_factory=dict, description="变迁后状态")
    change_factors: Dict[str, Any] = Field(default_factory=dict, description="变迁因素")

    # 时间线
    started_at: Optional[str] = Field(None, max_length=100, description="开始时间")
    completed_at: Optional[str] = Field(None, max_length=100, description="完成时间")
    duration_type: str = Field("medium", max_length=20, description="持续时间类型")

    # 影响评估
    impact_scope: str = Field("local", max_length=20, description="影响范围")
    resistance_level: int = Field(3, description="阻力水平")
    success_level: int = Field(5, description="成功程度")

    # 相关事件
    triggering_events: List[str] = Field(default_factory=list, description="触发事件")
    related_conflicts: List[str] = Field(default_factory=list, description="相关冲突")

    @validator('resistance_level', 'success_level')
    def validate_levels(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('等级必须在1-10之间')
        return v


# =============================================================================
# MongoDB 文档模型
# =============================================================================

class DomainCulture(BaseModel):
    """域文化总览模型"""
    novel_id: int = Field(..., description="小说ID")
    novel_code: str = Field(..., description="小说代码")
    domain_code: str = Field(..., description="域代码")
    domain_name: str = Field(..., description="域名称")

    cultural_profile: Dict[str, Any] = Field(..., description="文化概况")
    detailed_frameworks: Dict[str, Any] = Field(..., description="详细框架")
    plot_seeds: List[Dict[str, Any]] = Field(default_factory=list, description="剧情种子")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class CulturalContent(BaseModel):
    """详细文化内容模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_code: str = Field(..., description="域代码")
    dimension_code: str = Field(..., description="维度代码")
    framework_id: Optional[int] = Field(None, description="框架ID")

    content_type: str = Field(..., description="内容类型")
    title: str = Field(..., description="标题")
    content: Dict[str, Any] = Field(..., description="详细内容")

    cross_references: List[str] = Field(default_factory=list, description="交叉引用")
    tags: List[str] = Field(default_factory=list, description="标签")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class CulturalPractice(BaseModel):
    """文化实践模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_code: str = Field(..., description="域代码")

    practice_type: str = Field(..., description="实践类型")
    name: str = Field(..., description="实践名称")
    description: str = Field(..., description="实践描述")

    participants: List[str] = Field(default_factory=list, description="参与者")
    procedures: List[Dict[str, Any]] = Field(default_factory=list, description="程序步骤")
    significance: str = Field(..., description="意义")

    frequency: str = Field(..., description="频率")
    timing: Dict[str, Any] = Field(default_factory=dict, description="时机")
    location_requirements: List[str] = Field(default_factory=list, description="地点要求")

    importance_level: int = Field(1, description="重要性等级")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class PlotHookDetail(BaseModel):
    """剧情钩子详情模型"""
    novel_id: int = Field(..., description="小说ID")
    hook_id: int = Field(..., description="钩子ID")
    domain_code: str = Field(..., description="域代码")

    detailed_setup: str = Field(..., description="详细设定")
    background_context: Dict[str, Any] = Field(..., description="背景上下文")

    character_motivations: Dict[str, Any] = Field(default_factory=dict, description="角色动机")
    environmental_factors: Dict[str, Any] = Field(default_factory=dict, description="环境因素")

    escalation_paths: List[Dict[str, Any]] = Field(default_factory=list, description="升级路径")
    resolution_options: List[Dict[str, Any]] = Field(default_factory=list, description="解决选项")

    narrative_themes: List[str] = Field(default_factory=list, description="叙事主题")
    drama_level: int = Field(5, description="戏剧性水平")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# =============================================================================
# 查询和响应模型
# =============================================================================

class DomainWithCulture(Domain):
    """带文化信息的域模型"""
    framework_count: int = Field(0, description="框架数量")
    element_count: int = Field(0, description="要素数量")
    hook_count: int = Field(0, description="钩子数量")
    cultural_profile: Optional[Dict[str, Any]] = None


class FrameworkWithElements(CulturalFramework):
    """带要素的框架模型"""
    domain_name: Optional[str] = None
    dimension_name: Optional[str] = None
    elements: List[CulturalElement] = Field(default_factory=list)


class CulturalAnalysisRequest(BaseModel):
    """文化分析请求模型"""
    novel_id: int = Field(..., description="小说ID")
    analysis_type: str = Field(..., description="分析类型")
    target_domains: List[str] = Field(default_factory=list, description="目标域")
    focus_dimensions: List[str] = Field(default_factory=list, description="关注维度")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")


class CulturalAnalysisResponse(BaseModel):
    """文化分析响应模型"""
    analysis_id: str = Field(..., description="分析ID")
    novel_id: int = Field(..., description="小说ID")
    analysis_type: str = Field(..., description="分析类型")

    summary: Dict[str, Any] = Field(..., description="分析摘要")
    detailed_findings: Dict[str, Any] = Field(..., description="详细发现")
    cultural_patterns: List[Dict[str, Any]] = Field(default_factory=list, description="文化模式")

    recommendations: List[str] = Field(default_factory=list, description="建议")
    plot_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="剧情机会")

    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# =============================================================================
# 创建和更新请求模型
# =============================================================================

class CreateDomainRequest(BaseModel):
    """创建域请求模型"""
    novel_id: int = Field(..., description="小说ID")
    name: str = Field(..., max_length=50, description="域名")
    code: str = Field(..., max_length=20, description="域代码")
    display_name: str = Field(..., max_length=100, description="显示名称")
    dominant_law: Optional[str] = None
    ruling_power: Optional[str] = None
    power_level: int = Field(1, description="力量等级")
    sort_order: int = Field(0, description="排序")


class CreateFrameworkRequest(BaseModel):
    """创建文化框架请求模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_id: int = Field(..., description="域ID")
    dimension_code: str = Field(..., description="维度代码")
    framework_name: Optional[str] = None
    core_concept: Optional[str] = None
    key_features: Dict[str, Any] = Field(default_factory=dict)


class CreateElementRequest(BaseModel):
    """创建文化要素请求模型"""
    novel_id: int = Field(..., description="小说ID")
    framework_id: int = Field(..., description="框架ID")
    element_type: ElementType = Field(..., description="要素类型")
    name: str = Field(..., max_length=200, description="要素名称")
    code: Optional[str] = None
    category: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    importance: int = Field(1, description="重要性")
    tags: List[str] = Field(default_factory=list)


class CreatePlotHookRequest(BaseModel):
    """创建剧情钩子请求模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_id: Optional[int] = None
    framework_id: Optional[int] = None
    element_id: Optional[int] = None
    title: str = Field(..., max_length=200, description="钩子标题")
    description: str = Field(..., description="钩子描述")
    hook_type: HookType = Field(..., description="钩子类型")
    drama_level: int = Field(5, description="戏剧性水平")
    scope: str = Field("local", description="影响范围")


# =============================================================================
# 查询请求模型
# =============================================================================

class CulturalQueryRequest(BaseModel):
    """文化查询请求模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_codes: List[str] = Field(default_factory=list, description="域代码列表")
    dimension_codes: List[str] = Field(default_factory=list, description="维度代码列表")
    element_types: List[ElementType] = Field(default_factory=list, description="要素类型列表")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")
    sort: Optional[str] = Field(None, description="排序字段")
    limit: int = Field(20, description="限制数量")
    offset: int = Field(0, description="偏移量")


# =============================================================================
# 分页响应模型
# =============================================================================

class PaginatedResponse(BaseModel):
    """分页响应基类"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class PaginatedDomainsResponse(PaginatedResponse):
    """分页域响应"""
    items: List[DomainWithCulture] = Field(..., description="域列表")


class PaginatedFrameworksResponse(PaginatedResponse):
    """分页框架响应"""
    items: List[FrameworkWithElements] = Field(..., description="框架列表")


class PaginatedElementsResponse(PaginatedResponse):
    """分页要素响应"""
    items: List[CulturalElement] = Field(..., description="要素列表")


class PaginatedHooksResponse(PaginatedResponse):
    """分页钩子响应"""
    items: List[PlotHook] = Field(..., description="钩子列表")