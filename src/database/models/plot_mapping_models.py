"""
剧情功能映射数据模型定义
扩展地理实体，添加剧情功能映射相关模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .models import BaseDBModel


# =============================================================================
# 剧情功能相关枚举
# =============================================================================

class PlotFunctionCode(str, Enum):
    """剧情功能代码枚举"""
    F1 = "F1"   # 仪式触发器
    F2 = "F2"   # 法条杠杆点
    F3 = "F3"   # 门槛/关卡
    F4 = "F4"   # 资源据点
    F5 = "F5"   # 舆论扩音场
    F6 = "F6"   # 成长试炼场
    F7 = "F7"   # 盟友集散地
    F8 = "F8"   # 背叛/伏笔场
    F9 = "F9"   # 追逐/奇袭场
    F10 = "F10" # 谜底/档案库
    F11 = "F11" # 决战舞台
    F12 = "F12" # 避难/整备地
    F13 = "F13" # 环境杀/灾变触发
    F14 = "F14" # 赦免/翻案场
    F15 = "F15" # 黑市/灰地
    F16 = "F16" # 训练/精修场
    F17 = "F17" # 劫案/渗透目标
    F18 = "F18" # 情感落点/归乡
    F19 = "F19" # 交易/金融枢
    F20 = "F20" # 跨域节点


class PlotNodeCode(str, Enum):
    """剧情节点代码枚举"""
    NODE_1 = "①"  # 起源
    NODE_2 = "②"  # 门槛
    NODE_3 = "③"  # 试炼
    NODE_4 = "④"  # 深渊
    NODE_5 = "⑤"  # 重生
    NODE_6 = "⑥"  # 最终试炼
    NODE_7 = "⑦"  # 缔造


class FunctionCategory(str, Enum):
    """功能分类枚举"""
    EMOTIONAL = "emotional"    # 情感驱动
    CONFLICT = "conflict"      # 冲突推进
    INFO = "info"             # 信息揭示
    GROWTH = "growth"         # 角色成长
    WORLD = "world"           # 世界建构


# =============================================================================
# 基础模型
# =============================================================================

class PlotFunctionType(BaseDBModel):
    """剧情功能类型模型"""
    code: str = Field(..., max_length=10, description="功能代码")
    name: str = Field(..., max_length=50, description="功能名称")
    description: str = Field(..., description="详细描述")
    category: Optional[FunctionCategory] = Field(None, description="功能分类")
    usage_examples: Optional[str] = Field(None, description="使用示例")
    is_active: bool = Field(True, description="是否激活")


class PlotNodeType(BaseDBModel):
    """剧情节点类型模型"""
    code: str = Field(..., max_length=10, description="节点代码")
    name: str = Field(..., max_length=20, description="节点名称")
    description: str = Field(..., description="详细描述")
    sequence_order: int = Field(..., description="序列顺序")
    narrative_purpose: Optional[str] = Field(None, description="叙事目的")
    typical_events: Optional[str] = Field(None, description="典型事件")
    is_active: bool = Field(True, description="是否激活")

    @validator('sequence_order')
    def validate_sequence_order(cls, v):
        if not 1 <= v <= 7:
            raise ValueError('序列顺序必须在1-7之间')
        return v


class GeographicPlotMapping(BaseDBModel):
    """地理实体剧情映射模型"""
    novel_id: int = Field(..., description="所属小说ID")
    entity_id: int = Field(..., description="地理实体ID")

    # 功能映射
    function_codes: List[str] = Field(default_factory=list, description="功能代码列表")
    node_codes: List[str] = Field(default_factory=list, description="节点代码列表")

    # 剧情钩子
    hook_title: Optional[str] = Field(None, max_length=200, description="钩子标题")
    hook_description: Optional[str] = Field(None, description="钩子描述")
    hook_urgency: int = Field(3, description="紧急程度")
    hook_drama_level: int = Field(5, description="戏剧性水平")

    # 适用条件
    required_conditions: Dict[str, Any] = Field(default_factory=dict, description="触发条件")
    narrative_triggers: Dict[str, Any] = Field(default_factory=dict, description="叙事触发器")

    # 扩展属性
    conflict_types: List[str] = Field(default_factory=list, description="冲突类型")
    emotional_tags: List[str] = Field(default_factory=list, description="情感标签")
    difficulty_level: int = Field(3, description="难度等级")

    # 使用状态
    usage_count: int = Field(0, description="使用次数")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")
    is_active: bool = Field(True, description="是否激活")

    @validator('hook_urgency')
    def validate_urgency(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('紧急程度必须在1-5之间')
        return v

    @validator('hook_drama_level')
    def validate_drama_level(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('戏剧性水平必须在1-10之间')
        return v

    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('难度等级必须在1-5之间')
        return v


class PlotHookDetail(BaseDBModel):
    """剧情钩子详情模型"""
    mapping_id: int = Field(..., description="映射ID")
    novel_id: int = Field(..., description="所属小说ID")

    # 详细设定
    background_context: Optional[str] = Field(None, description="背景上下文")
    character_motivations: Dict[str, Any] = Field(default_factory=dict, description="角色动机")
    environmental_factors: Dict[str, Any] = Field(default_factory=dict, description="环境因素")

    # 发展路径
    escalation_paths: Dict[str, Any] = Field(default_factory=dict, description="升级路径")
    resolution_options: Dict[str, Any] = Field(default_factory=dict, description="解决选项")
    consequences: Dict[str, Any] = Field(default_factory=dict, description="后果影响")

    # 关联要素
    related_entities: List[str] = Field(default_factory=list, description="相关实体ID")
    required_items: List[str] = Field(default_factory=list, description="需要物品")
    required_skills: List[str] = Field(default_factory=list, description="需要技能")

    # 时机控制
    timing_constraints: Dict[str, Any] = Field(default_factory=dict, description="时机限制")
    cooldown_period: int = Field(0, description="冷却期（天）")
    seasonal_availability: Optional[str] = Field(None, description="季节性可用")


class PlotFunctionUsage(BaseDBModel):
    """剧情功能使用记录模型"""
    novel_id: int = Field(..., description="所属小说ID")
    mapping_id: int = Field(..., description="映射ID")

    # 使用信息
    used_in_chapter: Optional[str] = Field(None, max_length=50, description="使用章节")
    used_at: datetime = Field(default_factory=datetime.utcnow, description="使用时间")
    function_codes_used: List[str] = Field(..., description="使用的功能码")
    node_codes_used: List[str] = Field(..., description="使用的节点码")

    # 使用效果
    player_choices: Dict[str, Any] = Field(default_factory=dict, description="玩家选择")
    outcome_achieved: Optional[str] = Field(None, max_length=100, description="达成结果")
    impact_level: int = Field(3, description="影响等级")

    # 反馈数据
    effectiveness_score: Optional[int] = Field(None, description="效果评分")
    player_engagement: Optional[int] = Field(None, description="玩家参与度")
    narrative_satisfaction: Optional[int] = Field(None, description="叙事满意度")

    # 后续影响
    follow_up_hooks: List[str] = Field(default_factory=list, description="后续钩子")
    unlocked_content: List[str] = Field(default_factory=list, description="解锁内容")

    # 元数据
    session_id: Optional[str] = Field(None, max_length=100, description="游戏会话ID")
    notes: Optional[str] = Field(None, description="备注")

    @validator('impact_level', 'effectiveness_score', 'player_engagement', 'narrative_satisfaction')
    def validate_scores(cls, v, field):
        if v is not None:
            if field.name == 'impact_level' and not 1 <= v <= 5:
                raise ValueError('影响等级必须在1-5之间')
            elif field.name in ['effectiveness_score', 'player_engagement', 'narrative_satisfaction'] and not 1 <= v <= 10:
                raise ValueError(f'{field.name}必须在1-10之间')
        return v


# =============================================================================
# 查询和响应模型
# =============================================================================

class GeographicPlotView(BaseModel):
    """地理实体剧情视图模型"""
    entity_id: int = Field(..., description="实体ID")
    novel_id: int = Field(..., description="小说ID")
    entity_name: str = Field(..., description="实体名称")
    entity_type: str = Field(..., description="实体类型")
    domain_code: Optional[str] = Field(None, description="域代码")
    region_name: Optional[str] = Field(None, description="区域名称")

    # 剧情映射信息
    function_codes: List[str] = Field(default_factory=list, description="功能代码")
    node_codes: List[str] = Field(default_factory=list, description="节点代码")
    hook_title: Optional[str] = Field(None, description="钩子标题")
    hook_description: Optional[str] = Field(None, description="钩子描述")
    hook_urgency: int = Field(3, description="紧急程度")
    hook_drama_level: int = Field(5, description="戏剧性水平")
    difficulty_level: int = Field(3, description="难度等级")
    usage_count: int = Field(0, description="使用次数")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")

    # 功能和节点名称
    function_names: List[str] = Field(default_factory=list, description="功能名称")
    node_names: List[str] = Field(default_factory=list, description="节点名称")

    priority: int = Field(0, description="优先级")
    created_at: datetime = Field(..., description="创建时间")


class PlotFunctionStats(BaseModel):
    """剧情功能统计模型"""
    novel_id: int = Field(..., description="小说ID")
    function_code: str = Field(..., description="功能代码")
    function_name: str = Field(..., description="功能名称")
    category: Optional[str] = Field(None, description="功能分类")
    entity_count: int = Field(0, description="实体数量")
    avg_drama_level: float = Field(0.0, description="平均戏剧性")
    avg_difficulty_level: float = Field(0.0, description="平均难度")
    total_usage_count: int = Field(0, description="总使用次数")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")


# =============================================================================
# 请求模型
# =============================================================================

class PlotFunctionQuery(BaseModel):
    """剧情功能查询请求模型"""
    novel_id: int = Field(..., description="小说ID")

    # 功能筛选
    function_codes: List[str] = Field(default_factory=list, description="功能代码列表")
    node_codes: List[str] = Field(default_factory=list, description="节点代码列表")
    categories: List[FunctionCategory] = Field(default_factory=list, description="功能分类列表")

    # 地理筛选
    domain_codes: List[str] = Field(default_factory=list, description="域代码列表")
    entity_types: List[str] = Field(default_factory=list, description="实体类型列表")
    region_names: List[str] = Field(default_factory=list, description="区域名称列表")

    # 剧情属性筛选
    min_drama_level: Optional[int] = Field(None, description="最小戏剧性")
    max_drama_level: Optional[int] = Field(None, description="最大戏剧性")
    min_difficulty: Optional[int] = Field(None, description="最小难度")
    max_difficulty: Optional[int] = Field(None, description="最大难度")
    urgency_levels: List[int] = Field(default_factory=list, description="紧急程度列表")

    # 使用状态筛选
    max_usage_count: Optional[int] = Field(None, description="最大使用次数")
    unused_only: bool = Field(False, description="只显示未使用的")

    # 排序和分页
    sort_by: str = Field("hook_drama_level", description="排序字段")
    sort_desc: bool = Field(True, description="降序排列")
    limit: int = Field(20, description="限制数量")
    offset: int = Field(0, description="偏移量")

    @validator('min_drama_level', 'max_drama_level')
    def validate_drama_levels(cls, v):
        if v is not None and not 1 <= v <= 10:
            raise ValueError('戏剧性水平必须在1-10之间')
        return v

    @validator('min_difficulty', 'max_difficulty')
    def validate_difficulty_levels(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('难度等级必须在1-5之间')
        return v


class CreatePlotMappingRequest(BaseModel):
    """创建剧情映射请求模型"""
    novel_id: int = Field(..., description="小说ID")
    entity_id: int = Field(..., description="地理实体ID")

    # 功能映射
    function_codes: List[str] = Field(..., description="功能代码列表")
    node_codes: List[str] = Field(..., description="节点代码列表")

    # 剧情钩子
    hook_title: str = Field(..., max_length=200, description="钩子标题")
    hook_description: str = Field(..., description="钩子描述")
    hook_urgency: int = Field(3, description="紧急程度")
    hook_drama_level: int = Field(5, description="戏剧性水平")
    difficulty_level: int = Field(3, description="难度等级")

    # 扩展属性
    conflict_types: List[str] = Field(default_factory=list, description="冲突类型")
    emotional_tags: List[str] = Field(default_factory=list, description="情感标签")
    required_conditions: Dict[str, Any] = Field(default_factory=dict, description="触发条件")

    # 详细设定（可选）
    background_context: Optional[str] = Field(None, description="背景上下文")
    escalation_paths: Dict[str, Any] = Field(default_factory=dict, description="升级路径")
    resolution_options: Dict[str, Any] = Field(default_factory=dict, description="解决选项")


class UpdatePlotMappingRequest(BaseModel):
    """更新剧情映射请求模型"""
    function_codes: Optional[List[str]] = Field(None, description="功能代码列表")
    node_codes: Optional[List[str]] = Field(None, description="节点代码列表")
    hook_title: Optional[str] = Field(None, max_length=200, description="钩子标题")
    hook_description: Optional[str] = Field(None, description="钩子描述")
    hook_urgency: Optional[int] = Field(None, description="紧急程度")
    hook_drama_level: Optional[int] = Field(None, description="戏剧性水平")
    difficulty_level: Optional[int] = Field(None, description="难度等级")
    conflict_types: Optional[List[str]] = Field(None, description="冲突类型")
    emotional_tags: Optional[List[str]] = Field(None, description="情感标签")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RecordPlotUsageRequest(BaseModel):
    """记录剧情使用请求模型"""
    novel_id: int = Field(..., description="小说ID")
    mapping_id: int = Field(..., description="映射ID")
    used_in_chapter: Optional[str] = Field(None, description="使用章节")
    function_codes_used: List[str] = Field(..., description="使用的功能码")
    node_codes_used: List[str] = Field(..., description="使用的节点码")
    player_choices: Dict[str, Any] = Field(default_factory=dict, description="玩家选择")
    outcome_achieved: Optional[str] = Field(None, description="达成结果")
    impact_level: int = Field(3, description="影响等级")
    session_id: Optional[str] = Field(None, description="游戏会话ID")
    notes: Optional[str] = Field(None, description="备注")


# =============================================================================
# 批量导入模型
# =============================================================================

class PlotMappingImportData(BaseModel):
    """剧情映射导入数据模型"""
    entity_name: str = Field(..., description="实体名称")
    entity_type: str = Field(..., description="实体类型")
    domain_code: str = Field(..., description="域代码")
    function_codes: List[str] = Field(..., description="功能代码")
    node_codes: List[str] = Field(..., description="节点代码")
    hook_title: str = Field(..., description="钩子标题")
    hook_description: str = Field(..., description="钩子描述")
    hook_urgency: int = Field(3, description="紧急程度")
    hook_drama_level: int = Field(5, description="戏剧性水平")
    difficulty_level: int = Field(3, description="难度等级")


class BatchPlotMappingImport(BaseModel):
    """批量剧情映射导入模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_code: str = Field(..., description="域代码")
    mappings: List[PlotMappingImportData] = Field(..., description="映射数据列表")
    overwrite_existing: bool = Field(False, description="是否覆盖现有映射")


# =============================================================================
# 响应模型
# =============================================================================

class PlotFunctionQueryResponse(BaseModel):
    """剧情功能查询响应模型"""
    items: List[GeographicPlotView] = Field(..., description="查询结果")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

    # 统计信息
    function_distribution: Dict[str, int] = Field(default_factory=dict, description="功能分布")
    node_distribution: Dict[str, int] = Field(default_factory=dict, description="节点分布")
    avg_drama_level: float = Field(0.0, description="平均戏剧性")
    avg_difficulty_level: float = Field(0.0, description="平均难度")