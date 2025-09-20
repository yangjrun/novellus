"""
世界观数据模型 - 九域、修炼体系、权力组织、法则链等
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, field_validator

from .core_models import BaseModelWithTimestamp


class DomainType(str, Enum):
    """九大域类型枚举"""
    HUMAN_DOMAIN = "人域"
    HEAVEN_DOMAIN = "天域"
    SPIRIT_DOMAIN = "灵域"
    DEMON_DOMAIN = "魔域"
    IMMORTAL_DOMAIN = "仙域"
    GOD_DOMAIN = "神域"
    VOID_DOMAIN = "虚域"
    CHAOS_DOMAIN = "混沌域"
    ETERNAL_DOMAIN = "永恒域"


class CultivationStageType(str, Enum):
    """修炼阶段类型枚举"""
    MORTAL_BODY = "凡身"
    OPENING_MERIDIANS = "开脉"
    RETURNING_SOURCE = "归源"
    FEUDAL_LORD = "封侯"
    BREAKING_BOUNDARY = "破界"
    EMPEROR_REALM = "帝境"
    WORLD_SPLITTER = "裂世者"


class OrganizationType(str, Enum):
    """权力组织类型枚举"""
    DESTINY_DYNASTY = "天命王朝"
    LAW_SECT = "法则宗门"
    PRIEST_COUNCIL = "祭司议会"
    WORLD_SPLITTER_REBELS = "裂世反叛军"
    OTHER = "其他"


class EntityStatus(str, Enum):
    """实体状态枚举"""
    ACTIVE = "active"
    DECLINING = "declining"
    DESTROYED = "destroyed"
    REFORMED = "reformed"


class ItemRarity(str, Enum):
    """物品稀有度枚举"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"


class Domain(BaseModelWithTimestamp):
    """九大域模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="域名称")
    domain_type: DomainType = Field(..., description="域类型")
    description: Optional[str] = Field(None, description="域描述")
    characteristics: Dict[str, Any] = Field(default_factory=dict, description="域的特征")
    rules: Dict[str, Any] = Field(default_factory=dict, description="域的规则")
    power_level: int = Field(..., ge=1, le=9, description="力量等级(1-9)")
    location_info: Dict[str, Any] = Field(default_factory=dict, description="地理信息")
    climate_info: Dict[str, Any] = Field(default_factory=dict, description="气候信息")
    resources: Dict[str, Any] = Field(default_factory=dict, description="资源信息")
    dangers: Dict[str, Any] = Field(default_factory=dict, description="危险信息")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('域名称不能为空')
        return v.strip()


class CultivationSystem(BaseModelWithTimestamp):
    """修炼体系模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    system_name: str = Field(..., min_length=1, max_length=255, description="体系名称")
    system_type: str = Field(default="法则链修炼", max_length=100, description="体系类型")
    description: Optional[str] = Field(None, description="体系描述")
    stages: List[Dict[str, Any]] = Field(default_factory=list, description="修炼阶段数组")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="修炼要求")
    benefits: Dict[str, Any] = Field(default_factory=dict, description="修炼益处")
    risks: Dict[str, Any] = Field(default_factory=dict, description="修炼风险")

    @field_validator('system_name')
    def validate_system_name(cls, v):
        if not v or v.isspace():
            raise ValueError('体系名称不能为空')
        return v.strip()


class CultivationStage(BaseModelWithTimestamp):
    """修炼阶段详情模型"""
    id: UUID = Field(default_factory=uuid4)
    system_id: UUID = Field(..., description="关联的修炼体系ID")
    stage_name: str = Field(..., min_length=1, max_length=255, description="阶段名称")
    stage_level: int = Field(..., ge=1, description="阶段等级")
    stage_type: CultivationStageType = Field(..., description="阶段类型")
    description: Optional[str] = Field(None, description="阶段描述")
    power_description: Optional[str] = Field(None, description="力量描述")
    advancement_requirements: Dict[str, Any] = Field(default_factory=dict, description="晋级要求")
    typical_abilities: Dict[str, Any] = Field(default_factory=dict, description="典型能力")
    lifespan_increase: int = Field(default=0, ge=0, description="寿命增加（年）")

    @field_validator('stage_name')
    def validate_stage_name(cls, v):
        if not v or v.isspace():
            raise ValueError('阶段名称不能为空')
        return v.strip()


class PowerOrganization(BaseModelWithTimestamp):
    """权力组织模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="组织名称")
    organization_type: OrganizationType = Field(..., description="组织类型")
    description: Optional[str] = Field(None, description="组织描述")
    hierarchy: Dict[str, Any] = Field(default_factory=dict, description="组织架构")
    ideology: Dict[str, Any] = Field(default_factory=dict, description="理念信仰")
    resources: Dict[str, Any] = Field(default_factory=dict, description="资源实力")
    territories: Dict[str, Any] = Field(default_factory=dict, description="控制区域")
    relationships: Dict[str, Any] = Field(default_factory=dict, description="对外关系")
    status: EntityStatus = Field(default=EntityStatus.ACTIVE, description="组织状态")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('组织名称不能为空')
        return v.strip()


class LawChain(BaseModelWithTimestamp):
    """法则链模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="法则链名称")
    chain_type: str = Field(..., min_length=1, max_length=100, description="法则类型")
    description: Optional[str] = Field(None, description="法则链描述")
    origin_story: Optional[str] = Field(None, description="起源故事")
    power_level: int = Field(..., ge=1, le=10, description="力量等级(1-10)")
    activation_conditions: Dict[str, Any] = Field(default_factory=dict, description="激活条件")
    effects: Dict[str, Any] = Field(default_factory=dict, description="效果")
    limitations: Dict[str, Any] = Field(default_factory=dict, description="限制")
    corruption_risk: int = Field(default=0, ge=0, le=100, description="腐化风险(0-100)")
    rarity: ItemRarity = Field(default=ItemRarity.COMMON, description="稀有度")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('法则链名称不能为空')
        return v.strip()

    @field_validator('chain_type')
    def validate_chain_type(cls, v):
        if not v or v.isspace():
            raise ValueError('法则类型不能为空')
        return v.strip()


class ChainMark(BaseModelWithTimestamp):
    """链痕模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="链痕名称")
    mark_type: str = Field(..., min_length=1, max_length=100, description="链痕类型")
    description: Optional[str] = Field(None, description="链痕描述")
    visual_description: Optional[str] = Field(None, description="视觉描述")
    associated_chain: Optional[UUID] = Field(None, description="关联的法则链ID")
    power_boost: int = Field(default=0, description="力量增幅")
    side_effects: Dict[str, Any] = Field(default_factory=dict, description="副作用")
    acquisition_method: Optional[str] = Field(None, description="获得方法")
    removal_method: Optional[str] = Field(None, description="移除方法")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('链痕名称不能为空')
        return v.strip()

    @field_validator('mark_type')
    def validate_mark_type(cls, v):
        if not v or v.isspace():
            raise ValueError('链痕类型不能为空')
        return v.strip()


# 创建请求/响应模型
class DomainCreate(BaseModel):
    """创建域请求模型"""
    novel_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    domain_type: DomainType
    description: Optional[str] = None
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    rules: Dict[str, Any] = Field(default_factory=dict)
    power_level: int = Field(..., ge=1, le=9)
    location_info: Dict[str, Any] = Field(default_factory=dict)
    climate_info: Dict[str, Any] = Field(default_factory=dict)
    resources: Dict[str, Any] = Field(default_factory=dict)
    dangers: Dict[str, Any] = Field(default_factory=dict)


class DomainUpdate(BaseModel):
    """更新域请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain_type: Optional[DomainType] = None
    description: Optional[str] = None
    characteristics: Optional[Dict[str, Any]] = None
    rules: Optional[Dict[str, Any]] = None
    power_level: Optional[int] = Field(None, ge=1, le=9)
    location_info: Optional[Dict[str, Any]] = None
    climate_info: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    dangers: Optional[Dict[str, Any]] = None


class CultivationSystemCreate(BaseModel):
    """创建修炼体系请求模型"""
    novel_id: UUID
    system_name: str = Field(..., min_length=1, max_length=255)
    system_type: str = Field(default="法则链修炼", max_length=100)
    description: Optional[str] = None
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    benefits: Dict[str, Any] = Field(default_factory=dict)
    risks: Dict[str, Any] = Field(default_factory=dict)


class CultivationStageCreate(BaseModel):
    """创建修炼阶段请求模型"""
    system_id: UUID
    stage_name: str = Field(..., min_length=1, max_length=255)
    stage_level: int = Field(..., ge=1)
    stage_type: CultivationStageType
    description: Optional[str] = None
    power_description: Optional[str] = None
    advancement_requirements: Dict[str, Any] = Field(default_factory=dict)
    typical_abilities: Dict[str, Any] = Field(default_factory=dict)
    lifespan_increase: int = Field(default=0, ge=0)


class PowerOrganizationCreate(BaseModel):
    """创建权力组织请求模型"""
    novel_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    organization_type: OrganizationType
    description: Optional[str] = None
    hierarchy: Dict[str, Any] = Field(default_factory=dict)
    ideology: Dict[str, Any] = Field(default_factory=dict)
    resources: Dict[str, Any] = Field(default_factory=dict)
    territories: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)


class LawChainCreate(BaseModel):
    """创建法则链请求模型"""
    novel_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    chain_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    origin_story: Optional[str] = None
    power_level: int = Field(..., ge=1, le=10)
    activation_conditions: Dict[str, Any] = Field(default_factory=dict)
    effects: Dict[str, Any] = Field(default_factory=dict)
    limitations: Dict[str, Any] = Field(default_factory=dict)
    corruption_risk: int = Field(default=0, ge=0, le=100)
    rarity: ItemRarity = Field(default=ItemRarity.COMMON)


class ChainMarkCreate(BaseModel):
    """创建链痕请求模型"""
    novel_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    mark_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    visual_description: Optional[str] = None
    associated_chain: Optional[UUID] = None
    power_boost: int = Field(default=0)
    side_effects: Dict[str, Any] = Field(default_factory=dict)
    acquisition_method: Optional[str] = None
    removal_method: Optional[str] = None