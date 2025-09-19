"""
跨域冲突矩阵数据模型
专门用于处理域间冲突关系、升级路径、实体网络等复杂数据
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator
import numpy as np

from .core_models import BaseModelWithTimestamp


class ConflictIntensityLevel(str, Enum):
    """冲突强度等级"""
    NONE = "无"
    LOW = "低"
    MEDIUM = "中"
    MEDIUM_HIGH = "中高"
    HIGH = "高"
    CRITICAL = "极高"


class ConflictType(str, Enum):
    """冲突类型"""
    RESOURCE_DISPUTE = "资源争夺"
    REGULATORY_CONFLICT = "监管冲突"
    TERRITORIAL_DISPUTE = "领土争端"
    TRADE_FRICTION = "贸易摩擦"
    LEGAL_CONFLICT = "法律冲突"
    IDEOLOGICAL_CONFLICT = "意识形态冲突"
    POWER_STRUGGLE = "权力斗争"
    IDENTITY_CRISIS = "身份认同冲突"


class EscalationTrigger(str, Enum):
    """升级触发因素"""
    RESOURCE_SCARCITY = "资源稀缺"
    POLICY_CHANGE = "政策变化"
    EXTERNAL_PRESSURE = "外部压力"
    HISTORICAL_GRUDGE = "历史恩怨"
    LEADERSHIP_CHANGE = "领导层变动"
    ECONOMIC_CRISIS = "经济危机"
    MILITARY_BUILDUP = "军事集结"
    DIPLOMATIC_FAILURE = "外交失败"


class ConflictEntity(BaseModelWithTimestamp):
    """冲突相关实体模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="所属小说ID")

    # 基本信息
    name: str = Field(..., min_length=1, max_length=255, description="实体名称")
    entity_type: str = Field(..., description="实体类型：核心资源、法条制度、关键角色、冲突场景等")
    category: str = Field(..., description="实体分类")

    # 域信息
    primary_domain: Optional[str] = Field(None, description="主要所属域")
    involved_domains: List[str] = Field(default_factory=list, description="涉及的所有域")

    # 详细信息
    description: str = Field(..., description="详细描述")
    characteristics: Dict[str, Any] = Field(default_factory=dict, description="特征属性")
    importance_level: int = Field(default=5, ge=1, le=10, description="重要性等级")

    # 冲突相关属性
    conflict_roles: List[str] = Field(default_factory=list, description="在冲突中的角色")
    strategic_value: float = Field(default=1.0, ge=0.0, le=10.0, description="战略价值")
    scarcity_level: float = Field(default=1.0, ge=0.0, le=10.0, description="稀缺程度")

    # 元数据
    aliases: List[str] = Field(default_factory=list, description="别名")
    tags: List[str] = Field(default_factory=list, description="标签")
    references: List[str] = Field(default_factory=list, description="引用来源")


class ConflictRelation(BaseModelWithTimestamp):
    """冲突实体关系模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="所属小说ID")

    # 关系双方
    source_entity_id: UUID = Field(..., description="源实体ID")
    target_entity_id: UUID = Field(..., description="目标实体ID")

    # 关系属性
    relation_type: str = Field(..., description="关系类型：争夺、控制、依赖、影响等")
    relation_subtype: Optional[str] = Field(None, description="关系子类型")

    # 关系强度和特征
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="关系强度")
    directionality: str = Field(default="bidirectional", description="方向性：unidirectional/bidirectional")
    stability: float = Field(default=0.5, ge=0.0, le=1.0, description="关系稳定性")

    # 上下文信息
    context: Optional[str] = Field(None, description="关系上下文")
    conditions: List[str] = Field(default_factory=list, description="关系成立条件")
    effects: List[str] = Field(default_factory=list, description="关系效果")

    # 跨域标识
    is_cross_domain: bool = Field(default=False, description="是否跨域关系")
    domains_involved: List[str] = Field(default_factory=list, description="涉及的域")


class EscalationLevel(BaseModelWithTimestamp):
    """冲突升级等级模型"""
    id: UUID = Field(default_factory=uuid4)
    conflict_matrix_id: UUID = Field(..., description="所属冲突矩阵ID")

    # 等级信息
    level: int = Field(..., ge=1, le=10, description="升级等级")
    level_name: str = Field(..., description="等级名称")
    description: str = Field(..., description="等级描述")

    # 触发条件
    triggers: List[str] = Field(default_factory=list, description="触发条件")
    prerequisites: List[str] = Field(default_factory=list, description="前置条件")

    # 结果和影响
    consequences: List[str] = Field(default_factory=list, description="直接后果")
    collateral_effects: List[str] = Field(default_factory=list, description="连带影响")
    affected_entities: List[UUID] = Field(default_factory=list, description="受影响实体ID列表")

    # 概率和风险评估
    escalation_probability: float = Field(default=0.5, ge=0.0, le=1.0, description="升级概率")
    risk_level: int = Field(default=5, ge=1, le=10, description="风险等级")
    reversibility: float = Field(default=0.5, ge=0.0, le=1.0, description="可逆性")

    # 持续时间和影响范围
    estimated_duration: Optional[str] = Field(None, description="预估持续时间")
    impact_scope: List[str] = Field(default_factory=list, description="影响范围")

    # 下一级关系
    next_level_ids: List[UUID] = Field(default_factory=list, description="可能的下一级ID列表")


class ConflictMatrix(BaseModelWithTimestamp):
    """跨域冲突矩阵主模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="所属小说ID")

    # 基本信息
    matrix_name: str = Field(..., description="矩阵名称")
    description: str = Field(..., description="矩阵描述")
    version: str = Field(default="1.0", description="版本号")

    # 域信息
    domains: List[str] = Field(..., min_items=2, description="参与的域列表")
    domain_count: int = Field(..., ge=2, description="域数量")

    # 矩阵数据
    intensity_matrix: List[List[float]] = Field(..., description="冲突强度矩阵")
    conflict_types_matrix: Dict[str, Dict[str, List[str]]] = Field(
        default_factory=dict,
        description="冲突类型矩阵"
    )

    # 分析结果
    total_conflicts: int = Field(default=0, description="总冲突数")
    average_intensity: float = Field(default=0.0, description="平均冲突强度")
    max_intensity: float = Field(default=0.0, description="最大冲突强度")
    high_risk_pairs: List[Tuple[str, str]] = Field(default_factory=list, description="高风险域对")

    # 网络特征
    network_density: float = Field(default=0.0, description="网络密度")
    clustering_coefficient: float = Field(default=0.0, description="聚类系数")
    centrality_scores: Dict[str, float] = Field(default_factory=dict, description="中心性得分")

    # 元数据
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="分析元数据")
    tags: List[str] = Field(default_factory=list, description="标签")

    @validator('intensity_matrix')
    def validate_matrix_dimensions(cls, v, values):
        if 'domain_count' in values:
            expected_size = values['domain_count']
            if len(v) != expected_size or any(len(row) != expected_size for row in v):
                raise ValueError(f'矩阵维度必须为 {expected_size}x{expected_size}')
        return v


class ConflictScenario(BaseModelWithTimestamp):
    """冲突场景模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="所属小说ID")
    conflict_matrix_id: UUID = Field(..., description="所属冲突矩阵ID")

    # 场景基本信息
    title: str = Field(..., description="场景标题")
    description: str = Field(..., description="场景描述")
    scenario_type: str = Field(..., description="场景类型")

    # 参与方信息
    primary_domains: List[str] = Field(..., min_items=2, description="主要参与域")
    secondary_domains: List[str] = Field(default_factory=list, description="次要参与域")
    key_participants: List[UUID] = Field(default_factory=list, description="关键参与者实体ID")

    # 触发和条件
    trigger_events: List[str] = Field(default_factory=list, description="触发事件")
    preconditions: List[str] = Field(default_factory=list, description="前置条件")
    environmental_factors: List[str] = Field(default_factory=list, description="环境因素")

    # 发展和结果
    typical_progression: List[str] = Field(default_factory=list, description="典型发展过程")
    possible_outcomes: List[str] = Field(default_factory=list, description="可能结果")
    resolution_methods: List[str] = Field(default_factory=list, description="解决方法")

    # 评估指标
    complexity_level: int = Field(default=5, ge=1, le=10, description="复杂度等级")
    impact_scale: int = Field(default=5, ge=1, le=10, description="影响规模")
    drama_potential: int = Field(default=5, ge=1, le=10, description="戏剧潜力")
    story_value: float = Field(default=5.0, ge=0.0, le=10.0, description="故事价值")

    # 关联数据
    related_scenarios: List[UUID] = Field(default_factory=list, description="相关场景ID")
    escalation_path_id: Optional[UUID] = Field(None, description="关联的升级路径ID")


class StoryHook(BaseModelWithTimestamp):
    """剧情钩子模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="所属小说ID")
    conflict_matrix_id: Optional[UUID] = Field(None, description="关联冲突矩阵ID")
    scenario_id: Optional[UUID] = Field(None, description="关联场景ID")

    # 钩子基本信息
    title: str = Field(..., description="钩子标题")
    description: str = Field(..., description="钩子描述")
    hook_type: str = Field(..., description="钩子类型：悬疑、冲突、情感、动作等")

    # 冲突相关
    conflict_types: List[str] = Field(default_factory=list, description="涉及的冲突类型")
    domains_involved: List[str] = Field(default_factory=list, description="涉及的域")
    key_entities: List[UUID] = Field(default_factory=list, description="关键实体ID")

    # 故事要素
    main_characters: List[str] = Field(default_factory=list, description="主要角色类型")
    character_motivations: List[str] = Field(default_factory=list, description="角色动机")
    moral_themes: List[str] = Field(default_factory=list, description="道德主题")
    emotional_beats: List[str] = Field(default_factory=list, description="情感节拍")

    # 发展潜力
    setup_requirements: List[str] = Field(default_factory=list, description="设置要求")
    development_paths: List[str] = Field(default_factory=list, description="发展路径")
    climax_potential: List[str] = Field(default_factory=list, description="高潮潜力")
    resolution_options: List[str] = Field(default_factory=list, description="解决选项")

    # 评估指标
    complexity: int = Field(default=5, ge=1, le=10, description="复杂度")
    originality: int = Field(default=5, ge=1, le=10, description="原创性")
    emotional_impact: int = Field(default=5, ge=1, le=10, description="情感冲击力")
    plot_integration: int = Field(default=5, ge=1, le=10, description="情节融合度")
    character_development: int = Field(default=5, ge=1, le=10, description="角色发展潜力")

    # 综合评分
    overall_score: float = Field(default=5.0, ge=0.0, le=10.0, description="综合评分")
    marketability: float = Field(default=5.0, ge=0.0, le=10.0, description="市场价值")

    # 使用统计
    usage_count: int = Field(default=0, description="使用次数")
    last_used: Optional[datetime] = Field(None, description="最后使用时间")


class ConflictAnalysisResult(BaseModelWithTimestamp):
    """冲突分析结果模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="所属小说ID")
    conflict_matrix_id: UUID = Field(..., description="分析的冲突矩阵ID")

    # 分析基本信息
    analysis_type: str = Field(..., description="分析类型")
    analysis_version: str = Field(default="1.0", description="分析版本")
    analyzer_config: Dict[str, Any] = Field(default_factory=dict, description="分析器配置")

    # 分析结果
    results: Dict[str, Any] = Field(..., description="分析结果数据")
    insights: List[str] = Field(default_factory=list, description="洞察发现")
    recommendations: List[str] = Field(default_factory=list, description="建议")

    # 质量评估
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="置信度")
    completeness: float = Field(default=1.0, ge=0.0, le=1.0, description="完整性")
    accuracy_estimate: float = Field(default=0.8, ge=0.0, le=1.0, description="准确性估计")

    # 验证状态
    validation_status: str = Field(default="pending", description="验证状态")
    validator_notes: Optional[str] = Field(None, description="验证者备注")
    validation_date: Optional[datetime] = Field(None, description="验证日期")

    # 处理时间
    processing_time_ms: Optional[int] = Field(None, description="处理时间(毫秒)")
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description="资源使用情况")


# 创建和更新请求模型
class ConflictMatrixCreate(BaseModel):
    """创建冲突矩阵请求模型"""
    novel_id: UUID
    matrix_name: str = Field(..., min_length=1, max_length=255)
    description: str
    domains: List[str] = Field(..., min_items=2)
    intensity_matrix: List[List[float]]
    conflict_types_matrix: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class ConflictEntityCreate(BaseModel):
    """创建冲突实体请求模型"""
    novel_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    entity_type: str
    category: str
    primary_domain: Optional[str] = None
    involved_domains: List[str] = Field(default_factory=list)
    description: str
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    importance_level: int = Field(default=5, ge=1, le=10)
    strategic_value: float = Field(default=1.0, ge=0.0, le=10.0)
    scarcity_level: float = Field(default=1.0, ge=0.0, le=10.0)


class EscalationLevelCreate(BaseModel):
    """创建升级等级请求模型"""
    conflict_matrix_id: UUID
    level: int = Field(..., ge=1, le=10)
    level_name: str
    description: str
    triggers: List[str] = Field(default_factory=list)
    consequences: List[str] = Field(default_factory=list)
    escalation_probability: float = Field(default=0.5, ge=0.0, le=1.0)
    risk_level: int = Field(default=5, ge=1, le=10)
    reversibility: float = Field(default=0.5, ge=0.0, le=1.0)


class StoryHookCreate(BaseModel):
    """创建剧情钩子请求模型"""
    novel_id: UUID
    title: str = Field(..., min_length=1, max_length=500)
    description: str
    hook_type: str
    conflict_types: List[str] = Field(default_factory=list)
    domains_involved: List[str] = Field(default_factory=list)
    main_characters: List[str] = Field(default_factory=list)
    complexity: int = Field(default=5, ge=1, le=10)
    emotional_impact: int = Field(default=5, ge=1, le=10)


# 批量操作模型
class ConflictMatrixBatch(BaseModel):
    """批量冲突矩阵数据"""
    matrix: ConflictMatrixCreate
    entities: List[ConflictEntityCreate] = Field(default_factory=list)
    relations: List[Dict[str, Any]] = Field(default_factory=list)
    escalation_levels: List[EscalationLevelCreate] = Field(default_factory=list)
    scenarios: List[Dict[str, Any]] = Field(default_factory=list)
    story_hooks: List[StoryHookCreate] = Field(default_factory=list)


# 查询模型
class ConflictMatrixQuery(BaseModel):
    """冲突矩阵查询模型"""
    novel_id: Optional[UUID] = None
    domains: Optional[List[str]] = None
    min_intensity: Optional[float] = None
    max_intensity: Optional[float] = None
    conflict_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ConflictAnalysisRequest(BaseModel):
    """冲突分析请求模型"""
    novel_id: UUID
    conflict_matrix_id: UUID
    analysis_types: List[str] = Field(..., description="要执行的分析类型列表")
    config: Dict[str, Any] = Field(default_factory=dict, description="分析配置")
    include_visualizations: bool = Field(default=False, description="是否包含可视化")
    output_format: str = Field(default="json", description="输出格式")


# 响应模型
class ConflictMatrixResponse(BaseModel):
    """冲突矩阵响应模型"""
    matrix: ConflictMatrix
    entities: List[ConflictEntity] = Field(default_factory=list)
    relations: List[ConflictRelation] = Field(default_factory=list)
    escalation_levels: List[EscalationLevel] = Field(default_factory=list)
    scenarios: List[ConflictScenario] = Field(default_factory=list)
    story_hooks: List[StoryHook] = Field(default_factory=list)
    analysis_results: List[ConflictAnalysisResult] = Field(default_factory=list)


class NetworkAnalysisResult(BaseModel):
    """网络分析结果模型"""
    node_count: int
    edge_count: int
    density: float
    average_clustering: float
    centrality_measures: Dict[str, Dict[str, float]]
    community_structure: Dict[str, Any]
    critical_paths: List[List[str]]
    bottlenecks: List[str]
    influence_ranking: List[Dict[str, Any]]


class ConflictPrediction(BaseModel):
    """冲突预测模型"""
    prediction_id: UUID = Field(default_factory=uuid4)
    conflict_matrix_id: UUID
    scenario_type: str
    predicted_escalation_path: List[int]
    probability_scores: List[float]
    time_estimates: List[str]
    risk_factors: List[str]
    mitigation_strategies: List[str]
    confidence_interval: Tuple[float, float]
    model_version: str
    prediction_date: datetime = Field(default_factory=datetime.utcnow)