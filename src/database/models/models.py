"""
数据库模型定义
支持多小说的通用实体模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class NovelStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class EntityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class RelationshipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ENDED = "ended"


class EventStatus(str, Enum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# =============================================================================
# 基础模型类
# =============================================================================

class BaseDBModel(BaseModel):
    """数据库模型基类"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# =============================================================================
# 小说项目管理模型
# =============================================================================

class NovelTemplate(BaseDBModel):
    """小说模板模型"""
    name: str = Field(..., max_length=100, description="模板名称")
    world_type: str = Field(..., max_length=50, description="世界观类型")
    description: Optional[str] = Field(None, description="模板描述")
    default_settings: Dict[str, Any] = Field(default_factory=dict, description="默认配置")
    default_schemas: Dict[str, Any] = Field(default_factory=dict, description="默认实体架构")
    is_active: bool = Field(True, description="是否激活")


class Novel(BaseDBModel):
    """小说项目模型"""
    title: str = Field(..., max_length=200, description="小说标题")
    code: str = Field(..., max_length=50, description="小说代码标识")
    author: Optional[str] = Field(None, max_length=100, description="作者")
    genre: Optional[str] = Field(None, max_length=50, description="小说类型")
    status: NovelStatus = Field(NovelStatus.ACTIVE, description="小说状态")
    world_type: Optional[str] = Field(None, max_length=50, description="世界观类型")
    settings: Dict[str, Any] = Field(default_factory=dict, description="小说配置")
    entity_count: int = Field(0, description="实体数量")
    event_count: int = Field(0, description="事件数量")
    published_at: Optional[datetime] = Field(None, description="发布时间")

    @validator('code')
    def validate_code(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('代码标识只能包含字母、数字、下划线和连字符')
        return v.lower()


# =============================================================================
# 实体系统模型
# =============================================================================

class EntityType(BaseDBModel):
    """实体类型模型"""
    novel_id: int = Field(..., description="所属小说ID")
    name: str = Field(..., max_length=100, description="实体类型名称")
    display_name: str = Field(..., max_length=100, description="显示名称")
    schema_definition: Dict[str, Any] = Field(default_factory=dict, description="字段定义")
    validation_rules: Dict[str, Any] = Field(default_factory=dict, description="验证规则")
    display_config: Dict[str, Any] = Field(default_factory=dict, description="显示配置")
    is_active: bool = Field(True, description="是否激活")


class Entity(BaseDBModel):
    """通用实体模型"""
    novel_id: int = Field(..., description="所属小说ID")
    entity_type_id: int = Field(..., description="实体类型ID")
    name: str = Field(..., max_length=200, description="实体名称")
    code: Optional[str] = Field(None, max_length=100, description="实体代码")
    status: EntityStatus = Field(EntityStatus.ACTIVE, description="实体状态")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="动态属性")
    computed_values: Dict[str, Any] = Field(default_factory=dict, description="计算属性")
    tags: List[str] = Field(default_factory=list, description="标签")
    priority: int = Field(0, description="重要性级别")
    version: int = Field(1, description="版本号")

    @validator('priority')
    def validate_priority(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('优先级必须在0-100之间')
        return v


class EntityRelationship(BaseDBModel):
    """实体关系模型"""
    novel_id: int = Field(..., description="所属小说ID")
    source_entity_id: int = Field(..., description="源实体ID")
    target_entity_id: int = Field(..., description="目标实体ID")
    relationship_type: str = Field(..., max_length=100, description="关系类型")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="关系属性")
    strength: int = Field(1, description="关系强度")
    status: RelationshipStatus = Field(RelationshipStatus.ACTIVE, description="关系状态")
    valid_from: datetime = Field(default_factory=datetime.utcnow, description="生效时间")
    valid_to: Optional[datetime] = Field(None, description="失效时间")

    @validator('strength')
    def validate_strength(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('关系强度必须在1-10之间')
        return v

    @validator('target_entity_id')
    def validate_no_self_relationship(cls, v, values):
        if 'source_entity_id' in values and v == values['source_entity_id']:
            raise ValueError('不能建立自引用关系')
        return v


# =============================================================================
# 分类系统模型
# =============================================================================

class Category(BaseDBModel):
    """分类模型"""
    novel_id: int = Field(..., description="所属小说ID")
    type: str = Field(..., max_length=50, description="分类类型")
    name: str = Field(..., max_length=100, description="分类名称")
    code: Optional[str] = Field(None, max_length=50, description="分类代码")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    level: int = Field(1, description="层级")
    sort_order: int = Field(0, description="排序")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="分类属性")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(True, description="是否激活")


class EntityCategory(BaseDBModel):
    """实体分类关联模型"""
    novel_id: int = Field(..., description="所属小说ID")
    entity_id: int = Field(..., description="实体ID")
    category_id: int = Field(..., description="分类ID")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="关联属性")
    valid_from: datetime = Field(default_factory=datetime.utcnow, description="生效时间")
    valid_to: Optional[datetime] = Field(None, description="失效时间")


# =============================================================================
# 事件系统模型
# =============================================================================

class Event(BaseDBModel):
    """事件模型"""
    novel_id: int = Field(..., description="所属小说ID")
    name: str = Field(..., max_length=200, description="事件名称")
    event_type: Optional[str] = Field(None, max_length=50, description="事件类型")
    occurred_at: Optional[datetime] = Field(None, description="发生时间")
    in_world_time: Optional[str] = Field(None, max_length=100, description="小说内时间")
    sequence_order: Optional[int] = Field(None, description="剧情顺序")
    location_entity_id: Optional[int] = Field(None, description="地点实体ID")
    impact_level: int = Field(1, description="影响级别")
    scope: str = Field("local", max_length=20, description="影响范围")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="事件属性")
    description: Optional[str] = Field(None, description="事件描述")
    status: EventStatus = Field(EventStatus.COMPLETED, description="事件状态")

    @validator('impact_level')
    def validate_impact_level(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('影响级别必须在1-10之间')
        return v


class EventParticipant(BaseDBModel):
    """事件参与者模型"""
    novel_id: int = Field(..., description="所属小说ID")
    event_id: int = Field(..., description="事件ID")
    entity_id: int = Field(..., description="参与实体ID")
    role: Optional[str] = Field(None, max_length=50, description="角色")
    importance: int = Field(1, description="重要性")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="参与属性")

    @validator('importance')
    def validate_importance(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('重要性必须在1-10之间')
        return v


# =============================================================================
# 版本和审计模型
# =============================================================================

class SchemaVersion(BaseDBModel):
    """架构版本模型"""
    novel_id: int = Field(..., description="所属小说ID")
    version: str = Field(..., max_length=20, description="版本号")
    changes: Dict[str, Any] = Field(default_factory=dict, description="变更信息")
    migration_script: Optional[str] = Field(None, description="迁移脚本")
    applied_at: datetime = Field(default_factory=datetime.utcnow, description="应用时间")
    applied_by: str = Field("system", max_length=100, description="应用者")


class AuditLog(BaseDBModel):
    """审计日志模型"""
    novel_id: Optional[int] = Field(None, description="所属小说ID")
    table_name: str = Field(..., max_length=100, description="表名")
    record_id: Optional[int] = Field(None, description="记录ID")
    operation: str = Field(..., max_length=20, description="操作类型")
    old_values: Optional[Dict[str, Any]] = Field(None, description="原值")
    new_values: Optional[Dict[str, Any]] = Field(None, description="新值")
    user_id: Optional[str] = Field(None, max_length=100, description="用户ID")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")


# =============================================================================
# MongoDB 文档模型
# =============================================================================

class NovelWorldbuilding(BaseModel):
    """小说世界观配置模型"""
    novel_id: int = Field(..., description="小说ID")
    novel_code: str = Field(..., description="小说代码")
    config_type: str = Field(..., description="配置类型")
    version: str = Field("1.0", description="版本")
    content: Dict[str, Any] = Field(..., description="配置内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class EntityProfile(BaseModel):
    """实体详细档案模型"""
    novel_id: int = Field(..., description="小说ID")
    novel_code: str = Field(..., description="小说代码")
    entity_id: int = Field(..., description="实体ID")
    entity_type: str = Field(..., description="实体类型")
    profile: Dict[str, Any] = Field(..., description="详细档案")
    development: Dict[str, Any] = Field(default_factory=dict, description="发展轨迹")
    current_status: Dict[str, Any] = Field(default_factory=dict, description="当前状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class StoryContent(BaseModel):
    """故事内容模型"""
    novel_id: int = Field(..., description="小说ID")
    novel_code: str = Field(..., description="小说代码")
    story_node_id: Optional[int] = Field(None, description="故事节点ID")
    content: Dict[str, Any] = Field(..., description="故事内容")
    impact: Dict[str, Any] = Field(default_factory=dict, description="影响分析")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class CrossNovelAnalysis(BaseModel):
    """跨小说分析模型"""
    analysis_type: str = Field(..., description="分析类型")
    scope: Dict[str, Any] = Field(..., description="分析范围")
    analysis: Dict[str, Any] = Field(..., description="分析结果")
    insights: List[str] = Field(default_factory=list, description="洞察")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")


# =============================================================================
# 查询和响应模型
# =============================================================================

class EntityWithProfile(Entity):
    """带档案的实体模型"""
    entity_type_name: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    categories: List[Category] = Field(default_factory=list)
    relationships: List[EntityRelationship] = Field(default_factory=list)


class NovelSummary(BaseModel):
    """小说摘要模型"""
    novel: Novel
    entity_types: List[EntityType] = Field(default_factory=list)
    entity_counts: Dict[str, int] = Field(default_factory=dict)
    recent_events: List[Event] = Field(default_factory=list)


class QueryRequest(BaseModel):
    """查询请求模型"""
    novel_id: int = Field(..., description="小说ID")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")
    sort: Optional[str] = Field(None, description="排序字段")
    limit: int = Field(20, description="限制数量")
    offset: int = Field(0, description="偏移量")

    @validator('limit')
    def validate_limit(cls, v):
        if not 1 <= v <= 1000:
            raise ValueError('限制数量必须在1-1000之间')
        return v


class CreateEntityRequest(BaseModel):
    """创建实体请求模型"""
    novel_id: int = Field(..., description="小说ID")
    entity_type_name: str = Field(..., description="实体类型名称")
    name: str = Field(..., description="实体名称")
    code: Optional[str] = Field(None, description="实体代码")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="属性")
    tags: List[str] = Field(default_factory=list, description="标签")
    priority: int = Field(0, description="优先级")
    profile: Optional[Dict[str, Any]] = Field(None, description="详细档案")


class UpdateEntityRequest(BaseModel):
    """更新实体请求模型"""
    name: Optional[str] = Field(None, description="实体名称")
    code: Optional[str] = Field(None, description="实体代码")
    status: Optional[EntityStatus] = Field(None, description="状态")
    attributes: Optional[Dict[str, Any]] = Field(None, description="属性")
    tags: Optional[List[str]] = Field(None, description="标签")
    priority: Optional[int] = Field(None, description="优先级")
    profile: Optional[Dict[str, Any]] = Field(None, description="详细档案")


# =============================================================================
# 响应模型
# =============================================================================

class StandardResponse(BaseModel):
    """标准响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="消息")
    data: Optional[Any] = Field(None, description="数据")
    error: Optional[str] = Field(None, description="错误信息")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any] = Field(..., description="数据项")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")