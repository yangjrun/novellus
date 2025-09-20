"""
法则链系统数据模型
包含12条法则链的完整管理模型
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
import uuid


# =============================================================================
# 枚举类型定义
# =============================================================================

class ChainCategory(str, Enum):
    """法则链类别"""
    FATE = "命运"        # 命运链
    CAUSE = "因果"       # 因果链
    SPACE = "时空"       # 时空链
    LIFE = "生死"        # 生死链
    CHAOS = "混沌"       # 混沌链
    AUTHORITY = "权柄"   # 权柄链
    TRUE_NAME = "名真"   # 名真链
    MEMORY = "记忆"      # 记忆链
    REALM = "界域"       # 界域链
    FORM = "形质"        # 形质链
    REFLECTION = "映象"  # 映象链
    RESONANCE = "共鸣"   # 共鸣链


class LearningLevel(int, Enum):
    """学习等级"""
    L0 = 0  # 感知
    L1 = 1  # 安全操作
    L2 = 2  # 接口熟练
    L3 = 3  # 低风险组合
    L4 = 4  # 标准化
    L5 = 5  # 枢轴权
    L6 = 6  # 受控极限


class RarityLevel(int, Enum):
    """稀有度等级"""
    R0 = 0  # 普适
    R1 = 1  # 常见
    R2 = 2  # 进阶
    R3 = 3  # 稀有
    R4 = 4  # 至稀
    R5 = 5  # 禁忌


class AcquisitionChannel(str, Enum):
    """获取渠道"""
    FATE_PATTERN = "命格"    # 命格
    INHERITANCE = "师承"     # 师承
    CONTRACT = "契约"        # 契约
    ARTIFACT = "器物"        # 器物
    AUTHORITY = "权柄"       # 权柄
    BARRIER = "结界"         # 结界
    WINDOW = "窗口"          # 窗口
    CRUCIBLE = "坩埚"        # 坩埚
    RESONANCE = "共鸣"       # 共鸣


class CombinationType(str, Enum):
    """组合类型"""
    SYNERGY = "同相相长"      # 同相相长
    TACTICAL = "战术联动"     # 战术联动
    COUNTER = "硬克制"        # 硬克制


class CostType(str, Enum):
    """代价类型"""
    CAUSAL_DEBT = "因果债"    # 因果债(C)
    LIFE_DEBT = "寿债"        # 寿债(L)
    POLLUTION = "污染"        # 污染(P)
    CHAIN_FATIGUE = "链疲劳"  # 链疲劳(F)
    LEGITIMACY_RISK = "正当性风险"  # 正当性风险(N)


class DomainType(str, Enum):
    """四域类型"""
    HUMAN = "人域"    # 人域
    HEAVEN = "天域"   # 天域
    SPIRIT = "灵域"   # 灵域
    WILD = "荒域"     # 荒域


# =============================================================================
# 核心数据模型
# =============================================================================

class DomainAffinity(BaseModel):
    """四域偏好"""
    human: float = Field(default=0, ge=0, le=100)    # 人域亲和度
    heaven: float = Field(default=0, ge=0, le=100)   # 天域亲和度
    spirit: float = Field(default=0, ge=0, le=100)   # 灵域亲和度
    wild: float = Field(default=0, ge=0, le=100)     # 荒域亲和度


class LawChainDefinition(BaseModel):
    """法则链定义"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    novel_id: str
    chain_code: str  # FATE, CAUSE, SPACE等
    chain_name: str  # 命运链、因果链等
    chain_category: ChainCategory
    description: str
    origin_story: Optional[str] = None

    max_level: int = Field(default=6, ge=0, le=6)
    base_rarity: int = Field(default=0, ge=0, le=5)

    domain_affinity: DomainAffinity = Field(default_factory=DomainAffinity)
    base_attributes: Dict[str, Any] = Field(default_factory=dict)
    special_traits: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LevelRequirement(BaseModel):
    """等级要求"""
    min_cultivation_stage: Optional[str] = None
    min_comprehension: int = Field(default=0, ge=0)
    min_practice_hours: int = Field(default=0, ge=0)
    prerequisite_chains: List[str] = Field(default_factory=list)
    required_resources: Dict[str, int] = Field(default_factory=dict)


class LawChainLevel(BaseModel):
    """法则链等级"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    chain_id: str
    level_code: str  # L0, L1, L2等
    level_number: LearningLevel
    level_name: str  # 感知、安全操作等
    description: str

    requirements: LevelRequirement = Field(default_factory=LevelRequirement)
    abilities: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    unlocked_combinations: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AcquisitionChannelInfo(BaseModel):
    """获取渠道信息"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    novel_id: str
    channel_type: AcquisitionChannel
    channel_name: str
    description: Optional[str] = None

    channel_traits: Dict[str, Any] = Field(default_factory=lambda: {
        "difficulty": "medium",
        "stability": "stable",
        "risk_level": "low",
        "resource_cost": "moderate"
    })

    available_chains: List[str] = Field(default_factory=list)
    restrictions: Dict[str, Any] = Field(default_factory=dict)
    success_rate_formula: Optional[str] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# 角色法则链管理
# =============================================================================

class LawChainMaster(BaseModel):
    """法则链掌握者"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    chain_id: str

    # 学习进度
    current_level: LearningLevel = Field(default=LearningLevel.L0)
    current_rarity: RarityLevel = Field(default=RarityLevel.R0)
    mastery_progress: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    # 获取信息
    acquisition_channel: Optional[AcquisitionChannel] = None
    acquisition_date: datetime = Field(default_factory=datetime.now)
    acquisition_details: Dict[str, Any] = Field(default_factory=dict)

    # 使用统计
    total_uses: int = Field(default=0, ge=0)
    successful_uses: int = Field(default=0, ge=0)
    failed_uses: int = Field(default=0, ge=0)

    # 链疲劳度
    chain_fatigue: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    last_recovery_time: datetime = Field(default_factory=datetime.now)

    # 污染度
    pollution_level: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    # 特殊状态
    special_states: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_uses == 0:
            return 0.0
        return (self.successful_uses / self.total_uses) * 100

    @property
    def is_exhausted(self) -> bool:
        """是否疲劳过度"""
        return self.chain_fatigue >= 80

    @property
    def is_polluted(self) -> bool:
        """是否污染严重"""
        return self.pollution_level >= 70


# =============================================================================
# 法则链组合系统
# =============================================================================

class ChainRequirement(BaseModel):
    """组合所需法则链"""
    chain_id: str
    min_level: LearningLevel = Field(default=LearningLevel.L0)
    min_rarity: RarityLevel = Field(default=RarityLevel.R0)


class CombinationEffect(BaseModel):
    """组合效果"""
    power_boost: int = Field(default=0, ge=0)
    range_extension: int = Field(default=0, ge=0)
    duration_bonus: int = Field(default=0, ge=0)
    special_effects: List[str] = Field(default_factory=list)


class CombinationCost(BaseModel):
    """组合代价"""
    chain_fatigue: Decimal = Field(default=Decimal("0"), ge=0)
    pollution_risk: Decimal = Field(default=Decimal("0"), ge=0)
    resource_consumption: Dict[str, int] = Field(default_factory=dict)


class LawChainCombination(BaseModel):
    """法则链组合"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    novel_id: str
    combination_name: str
    combination_type: CombinationType
    description: Optional[str] = None

    required_chains: List[ChainRequirement] = Field(default_factory=list)
    effects: CombinationEffect = Field(default_factory=CombinationEffect)
    activation_conditions: Dict[str, Any] = Field(default_factory=dict)
    combination_cost: CombinationCost = Field(default_factory=CombinationCost)

    stability_rating: int = Field(default=50, ge=0, le=100)

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CharacterChainCombination(BaseModel):
    """角色的法则链组合"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    combination_id: str

    proficiency_level: int = Field(default=0, ge=0, le=100)

    # 使用统计
    total_uses: int = Field(default=0, ge=0)
    successful_uses: int = Field(default=0, ge=0)
    critical_successes: int = Field(default=0, ge=0)
    failures: int = Field(default=0, ge=0)

    # 组合状态
    is_active: bool = Field(default=False)
    last_used_at: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_uses == 0:
            return 0.0
        return (self.successful_uses / self.total_uses) * 100

    @property
    def is_on_cooldown(self) -> bool:
        """是否在冷却中"""
        if self.cooldown_until is None:
            return False
        return datetime.now() < self.cooldown_until


# =============================================================================
# 代价系统
# =============================================================================

class LawChainCost(BaseModel):
    """法则链代价"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    chain_id: Optional[str] = None
    combination_id: Optional[str] = None

    cost_type: CostType
    cost_code: str  # C, L, P, F, N

    cost_value: Decimal = Field(ge=0)
    accumulated_value: Decimal = Field(default=Decimal("0"), ge=0)

    is_paid: bool = Field(default=False)
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None

    source_action: Optional[str] = None
    source_location: Optional[str] = None
    source_timestamp: datetime = Field(default_factory=datetime.now)

    effects: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CausalDebt(BaseModel):
    """因果债务"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    debt_type: str

    original_amount: Decimal = Field(ge=0)
    current_amount: Decimal = Field(ge=0)
    interest_rate: Decimal = Field(default=Decimal("0"), ge=0)

    creditor_type: Optional[str] = None  # 天道、法则、个体等
    creditor_id: Optional[str] = None

    status: str = Field(default="active")  # active, partial, paid, defaulted, transferred
    due_date: Optional[datetime] = None

    source_event: Optional[str] = None
    source_chains: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def is_overdue(self) -> bool:
        """是否逾期"""
        if self.due_date is None:
            return False
        return datetime.now() > self.due_date and self.status == "active"

    @property
    def remaining_amount(self) -> Decimal:
        """剩余债务"""
        return self.current_amount


# =============================================================================
# 场强系统
# =============================================================================

class LocationData(BaseModel):
    """位置数据"""
    coordinates: Optional[List[float]] = None
    radius: float = Field(default=0, ge=0)
    shape: str = Field(default="sphere")


class TimeModifiers(BaseModel):
    """时段修正"""
    dawn: float = Field(default=0)      # 黎明
    morning: float = Field(default=0)   # 早晨
    noon: float = Field(default=0)      # 正午
    afternoon: float = Field(default=0) # 下午
    dusk: float = Field(default=0)      # 黄昏
    night: float = Field(default=0)     # 夜晚
    midnight: float = Field(default=0)  # 午夜


class ResonanceFactor(BaseModel):
    """共振因素"""
    min_people: int = Field(default=0, ge=0)
    resonance_multiplier: float = Field(default=1.0, ge=0)
    special_conditions: List[str] = Field(default_factory=list)


class FieldStrengthZone(BaseModel):
    """场强区域"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    novel_id: str
    zone_name: str
    zone_type: str

    location_data: LocationData = Field(default_factory=LocationData)

    base_field_strength: Decimal = Field(default=Decimal("0"), ge=0, le=5)
    current_field_strength: Decimal = Field(default=Decimal("0"), ge=0, le=5)

    time_modifiers: TimeModifiers = Field(default_factory=TimeModifiers)
    resonance_factors: ResonanceFactor = Field(default_factory=ResonanceFactor)

    affected_chains: List[str] = Field(default_factory=list)
    special_events: List[Dict[str, Any]] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FieldStrengthCalculation(BaseModel):
    """场强计算"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    zone_id: str
    calculation_time: datetime = Field(default_factory=datetime.now)

    location_factor: Decimal = Field(ge=0, le=5)
    time_factor: Decimal = Field(ge=0, le=5)
    people_count: int = Field(default=0, ge=0)
    resonance_factor: Decimal = Field(default=1.0, ge=0)

    calculated_strength: Decimal = Field(ge=0, le=5)

    active_chains: List[str] = Field(default_factory=list)
    special_modifiers: Dict[str, Any] = Field(default_factory=dict)

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# 使用记录
# =============================================================================

class CostRecord(BaseModel):
    """代价记录"""
    causal_debt: Decimal = Field(default=Decimal("0"), ge=0)
    life_debt: Decimal = Field(default=Decimal("0"), ge=0)
    pollution: Decimal = Field(default=Decimal("0"), ge=0)
    chain_fatigue: Decimal = Field(default=Decimal("0"), ge=0)
    legitimacy_risk: Decimal = Field(default=Decimal("0"), ge=0)


class LawChainUsageLog(BaseModel):
    """法则链使用日志"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    chain_id: Optional[str] = None
    combination_id: Optional[str] = None

    action_type: str
    action_description: Optional[str] = None

    input_parameters: Dict[str, Any] = Field(default_factory=dict)

    field_strength: Optional[Decimal] = None
    zone_id: Optional[str] = None

    success: bool = Field(default=True)
    output_results: Dict[str, Any] = Field(default_factory=dict)

    costs_incurred: CostRecord = Field(default_factory=CostRecord)
    side_effects: List[str] = Field(default_factory=list)

    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# 分析和统计模型
# =============================================================================

class ChainMasteryStats(BaseModel):
    """法则链掌握统计"""
    character_id: str
    total_chains_mastered: int
    average_level: float
    average_rarity: float
    total_uses: int
    overall_success_rate: float
    most_used_chain: Optional[str] = None
    highest_level_chain: Optional[str] = None


class CombinationStats(BaseModel):
    """组合统计"""
    character_id: str
    total_combinations: int
    average_proficiency: float
    most_successful_combination: Optional[str] = None
    total_combination_uses: int
    critical_success_rate: float


class DebtSummary(BaseModel):
    """债务汇总"""
    character_id: str
    total_causal_debt: Decimal
    total_life_debt: Decimal
    total_pollution: Decimal
    active_debts_count: int
    overdue_debts_count: int
    highest_interest_debt: Optional[str] = None