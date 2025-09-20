"""
内容数据模型 - 物品、事件、知识库等MongoDB文档模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, field_validator

from .core_models import BaseModelWithTimestamp
from .character_models import (
    ItemType, ItemRarity, EventType, EventStatus, KnowledgeCategory
)


class ItemBasicInfo(BaseModel):
    """物品基本信息"""
    grade: Optional[str] = None
    origin: Optional[str] = None
    creator: Optional[str] = None
    age: Optional[str] = None
    value: Dict[str, Any] = Field(default_factory=dict)


class PhysicalProperties(BaseModel):
    """物理属性"""
    appearance: Optional[str] = None
    material: Optional[str] = None
    weight: Optional[str] = None
    size: Optional[str] = None
    durability: Optional[int] = Field(None, ge=0, le=100)
    special_markings: List[str] = Field(default_factory=list)


class ItemAbilities(BaseModel):
    """物品能力"""
    passive_effects: List[str] = Field(default_factory=list)
    active_abilities: List[str] = Field(default_factory=list)
    special_techniques: List[str] = Field(default_factory=list)
    cultivation_bonuses: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)


class LawChainConnection(BaseModel):
    """法则链连接"""
    chain_name: str = Field(..., description="法则链名称")
    resonance_level: int = Field(..., ge=1, le=10, description="共鸣等级")
    enhancement_type: str = Field(..., description="增强类型")


class ItemRequirements(BaseModel):
    """物品需求"""
    cultivation_stage: Optional[str] = None
    spiritual_power: Optional[int] = Field(None, ge=0)
    bloodline: Optional[str] = None
    special_conditions: List[str] = Field(default_factory=list)


class ItemHistory(BaseModel):
    """物品历史"""
    creation_story: Optional[str] = None
    previous_owners: List[str] = Field(default_factory=list)
    legendary_deeds: List[str] = Field(default_factory=list)
    curses_blessings: List[str] = Field(default_factory=list)


class CurrentStatus(BaseModel):
    """当前状态"""
    location: Optional[str] = None
    owner: Optional[str] = None
    condition: Optional[str] = None
    accessibility: Optional[str] = None


class ItemStoryRole(BaseModel):
    """物品故事角色"""
    plot_importance: int = Field(default=1, ge=1, le=10)
    symbolic_significance: Optional[str] = None
    character_connections: List[str] = Field(default_factory=list)
    planned_usage: List[str] = Field(default_factory=list)


class Item(BaseModelWithTimestamp):
    """物品模型 - MongoDB文档"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    novel_id: str = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="物品名称")
    item_type: ItemType = Field(..., description="物品类型")
    rarity: ItemRarity = Field(default=ItemRarity.COMMON, description="稀有度")
    basic_info: ItemBasicInfo = Field(default_factory=ItemBasicInfo)
    physical_properties: PhysicalProperties = Field(default_factory=PhysicalProperties)
    abilities: ItemAbilities = Field(default_factory=ItemAbilities)
    law_chain_connections: List[LawChainConnection] = Field(default_factory=list)
    requirements: ItemRequirements = Field(default_factory=ItemRequirements)
    history: ItemHistory = Field(default_factory=ItemHistory)
    current_status: CurrentStatus = Field(default_factory=CurrentStatus)
    story_role: ItemStoryRole = Field(default_factory=ItemStoryRole)
    tags: List[str] = Field(default_factory=list)

    @field_validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('物品名称不能为空')
        return v.strip()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TimelineInfo(BaseModel):
    """时间线信息"""
    chronological_order: Optional[int] = Field(None, description="时间顺序")
    duration: Optional[str] = None
    time_period: Optional[str] = None
    parallel_events: List[str] = Field(default_factory=list)


class EventParticipant(BaseModel):
    """事件参与者"""
    character_id: str = Field(..., description="角色ID")
    role: str = Field(..., description="角色作用")
    importance: int = Field(default=1, ge=1, le=10, description="重要程度")
    outcome: Optional[str] = None


class EventLocationInfo(BaseModel):
    """事件地点信息"""
    primary_location: Optional[str] = None
    secondary_locations: List[str] = Field(default_factory=list)
    environmental_factors: List[str] = Field(default_factory=list)


class EventDescription(BaseModel):
    """事件描述"""
    summary: Optional[str] = None
    detailed_account: Optional[str] = None
    key_moments: List[str] = Field(default_factory=list)
    emotional_beats: List[str] = Field(default_factory=list)


class EventConsequences(BaseModel):
    """事件后果"""
    immediate_effects: List[str] = Field(default_factory=list)
    long_term_impacts: List[str] = Field(default_factory=list)
    character_changes: List[str] = Field(default_factory=list)
    world_changes: List[str] = Field(default_factory=list)


class PlotConnections(BaseModel):
    """情节连接"""
    triggers: List[str] = Field(default_factory=list)
    leads_to: List[str] = Field(default_factory=list)
    foreshadowing: List[str] = Field(default_factory=list)
    callbacks: List[str] = Field(default_factory=list)


class Event(BaseModelWithTimestamp):
    """事件模型 - MongoDB文档"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    novel_id: str = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="事件名称")
    event_type: EventType = Field(..., description="事件类型")
    timeline_info: TimelineInfo = Field(default_factory=TimelineInfo)
    participants: List[EventParticipant] = Field(default_factory=list)
    location_info: EventLocationInfo = Field(default_factory=EventLocationInfo)
    description: EventDescription = Field(default_factory=EventDescription)
    consequences: EventConsequences = Field(default_factory=EventConsequences)
    plot_connections: PlotConnections = Field(default_factory=PlotConnections)
    themes: List[str] = Field(default_factory=list, description="事件体现的主题")
    status: EventStatus = Field(default=EventStatus.PLANNED)
    tags: List[str] = Field(default_factory=list)

    @field_validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('事件名称不能为空')
        return v.strip()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KnowledgeContent(BaseModel):
    """知识内容"""
    summary: Optional[str] = None
    detailed_info: Optional[str] = None
    examples: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)


class RelatedEntity(BaseModel):
    """相关实体"""
    entity_type: str = Field(..., description="实体类型")
    entity_id: str = Field(..., description="实体ID")
    relationship: str = Field(..., description="关系描述")


class KnowledgeBase(BaseModelWithTimestamp):
    """知识库模型 - MongoDB文档"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    novel_id: str = Field(..., description="关联的小说ID")
    title: str = Field(..., min_length=1, max_length=255, description="知识标题")
    category: KnowledgeCategory = Field(..., description="知识分类")
    content: KnowledgeContent = Field(default_factory=KnowledgeContent)
    related_entities: List[RelatedEntity] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list, description="信息来源")
    reliability: int = Field(default=5, ge=1, le=10, description="信息可靠度(1-10)")
    tags: List[str] = Field(default_factory=list)

    @field_validator('title')
    def validate_title(cls, v):
        if not v or v.isspace():
            raise ValueError('知识标题不能为空')
        return v.strip()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 创建请求模型
class CharacterCreate(BaseModel):
    """创建角色请求模型"""
    novel_id: str
    name: str = Field(..., min_length=1, max_length=255)
    character_type: str
    basic_info: Optional[Dict[str, Any]] = None
    cultivation_info: Optional[Dict[str, Any]] = None
    personality: Optional[Dict[str, Any]] = None
    appearance: Optional[Dict[str, Any]] = None
    background: Optional[Dict[str, Any]] = None
    story_role: Optional[Dict[str, Any]] = None
    dialogue_style: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)


class LocationCreate(BaseModel):
    """创建地点请求模型"""
    novel_id: str
    name: str = Field(..., min_length=1, max_length=255)
    location_type: str
    domain_affiliation: Optional[str] = None
    geographical_info: Optional[Dict[str, Any]] = None
    political_info: Optional[Dict[str, Any]] = None
    cultivation_aspects: Optional[Dict[str, Any]] = None
    physical_description: Optional[Dict[str, Any]] = None
    history: Optional[Dict[str, Any]] = None
    story_significance: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)


class ItemCreate(BaseModel):
    """创建物品请求模型"""
    novel_id: str
    name: str = Field(..., min_length=1, max_length=255)
    item_type: str
    rarity: str = Field(default="common")
    basic_info: Optional[Dict[str, Any]] = None
    physical_properties: Optional[Dict[str, Any]] = None
    abilities: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None
    history: Optional[Dict[str, Any]] = None
    current_status: Optional[Dict[str, Any]] = None
    story_role: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)


class EventCreate(BaseModel):
    """创建事件请求模型"""
    novel_id: str
    name: str = Field(..., min_length=1, max_length=255)
    event_type: str
    timeline_info: Optional[Dict[str, Any]] = None
    description: Optional[Dict[str, Any]] = None
    participants: List[Dict[str, Any]] = Field(default_factory=list)
    location_info: Optional[Dict[str, Any]] = None
    consequences: Optional[Dict[str, Any]] = None
    plot_connections: Optional[Dict[str, Any]] = None
    themes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求模型"""
    novel_id: str
    title: str = Field(..., min_length=1, max_length=255)
    category: str
    content: Optional[Dict[str, Any]] = None
    related_entities: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    reliability: int = Field(default=5, ge=1, le=10)
    tags: List[str] = Field(default_factory=list)