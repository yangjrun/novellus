"""
角色数据模型 - MongoDB存储的复杂角色信息
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator

from .core_models import BaseModelWithTimestamp


class CharacterType(str, Enum):
    """角色类型枚举"""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    BACKGROUND = "background"
    MENTOR = "mentor"
    LOVE_INTEREST = "love_interest"


class CharacterStatus(str, Enum):
    """角色状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"
    MISSING = "missing"
    TRANSFORMED = "transformed"


class LocationType(str, Enum):
    """地点类型枚举"""
    DOMAIN = "domain"
    CITY = "city"
    SECT = "sect"
    PALACE = "palace"
    MOUNTAIN = "mountain"
    FOREST = "forest"
    RUIN = "ruin"
    BATTLEFIELD = "battlefield"
    CULTIVATION_GROUND = "cultivation_ground"
    SECRET_REALM = "secret_realm"


class LocationStatus(str, Enum):
    """地点状态枚举"""
    ACTIVE = "active"
    DESTROYED = "destroyed"
    ABANDONED = "abandoned"
    HIDDEN = "hidden"
    TRANSFORMED = "transformed"


class ItemType(str, Enum):
    """物品类型枚举"""
    WEAPON = "weapon"
    ARMOR = "armor"
    PILL = "pill"
    CULTIVATION_MANUAL = "cultivation_manual"
    TREASURE = "treasure"
    ARTIFACT = "artifact"
    MATERIAL = "material"
    CONSUMABLE = "consumable"


class ItemRarity(str, Enum):
    """物品稀有度枚举"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    DIVINE = "divine"


class EventType(str, Enum):
    """事件类型枚举"""
    BATTLE = "battle"
    CULTIVATION_BREAKTHROUGH = "cultivation_breakthrough"
    POLITICAL_INTRIGUE = "political_intrigue"
    DISCOVERY = "discovery"
    BETRAYAL = "betrayal"
    ALLIANCE = "alliance"
    ROMANCE = "romance"
    TRAGEDY = "tragedy"
    MYSTERY = "mystery"


class EventStatus(str, Enum):
    """事件状态枚举"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVISED = "revised"
    CANCELLED = "cancelled"


class KnowledgeCategory(str, Enum):
    """知识分类枚举"""
    WORLD_HISTORY = "world_history"
    CULTIVATION_THEORY = "cultivation_theory"
    POLITICS = "politics"
    GEOGRAPHY = "geography"
    CULTURE = "culture"
    LANGUAGE = "language"
    MYTHOLOGY = "mythology"
    TECHNOLOGY = "technology"
    ECONOMICS = "economics"


class BasicInfo(BaseModel):
    """角色基本信息"""
    full_name: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    age: Optional[int] = Field(None, ge=0)
    gender: Optional[str] = None
    race: Optional[str] = None
    birthplace: Optional[str] = None
    current_domain: Optional[str] = None


class CultivationInfo(BaseModel):
    """修炼信息"""
    current_stage: Optional[str] = None
    cultivation_method: Optional[str] = None
    law_chains: List[str] = Field(default_factory=list)
    chain_marks: List[str] = Field(default_factory=list)
    special_abilities: List[str] = Field(default_factory=list)
    cultivation_history: List[Dict[str, Any]] = Field(default_factory=list)


class Personality(BaseModel):
    """性格信息"""
    traits: List[str] = Field(default_factory=list)
    motivations: List[str] = Field(default_factory=list)
    fears: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    moral_alignment: Optional[str] = None
    personality_type: Optional[str] = None


class Appearance(BaseModel):
    """外貌信息"""
    height: Optional[str] = None
    build: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    distinctive_features: List[str] = Field(default_factory=list)
    clothing_style: Optional[str] = None
    aura_description: Optional[str] = None


class Background(BaseModel):
    """背景信息"""
    origin_story: Optional[str] = None
    family_background: Dict[str, Any] = Field(default_factory=dict)
    education: Optional[str] = None
    major_events: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    secrets: List[str] = Field(default_factory=list)


class Relationship(BaseModel):
    """关系信息"""
    character_id: str = Field(..., description="关联角色ID")
    relationship_type: str = Field(..., description="关系类型")
    relationship_status: str = Field(..., description="关系状态")
    description: Optional[str] = None
    importance_level: int = Field(default=1, ge=1, le=10)


class StoryRole(BaseModel):
    """故事角色"""
    importance_level: int = Field(default=1, ge=1, le=10)
    screen_time: Optional[str] = None
    character_arc: Optional[str] = None
    plot_functions: List[str] = Field(default_factory=list)
    symbolic_meaning: Optional[str] = None


class DialogueStyle(BaseModel):
    """对话风格"""
    speech_patterns: List[str] = Field(default_factory=list)
    vocabulary_level: Optional[str] = None
    accent_dialect: Optional[str] = None
    common_phrases: List[str] = Field(default_factory=list)
    emotional_expressions: Dict[str, str] = Field(default_factory=dict)


class Character(BaseModelWithTimestamp):
    """角色模型 - MongoDB文档"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    novel_id: str = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="角色名称")
    character_type: CharacterType = Field(..., description="角色类型")
    basic_info: BasicInfo = Field(default_factory=BasicInfo)
    cultivation_info: CultivationInfo = Field(default_factory=CultivationInfo)
    personality: Personality = Field(default_factory=Personality)
    appearance: Appearance = Field(default_factory=Appearance)
    background: Background = Field(default_factory=Background)
    relationships: List[Relationship] = Field(default_factory=list)
    story_role: StoryRole = Field(default_factory=StoryRole)
    dialogue_style: DialogueStyle = Field(default_factory=DialogueStyle)
    status: CharacterStatus = Field(default=CharacterStatus.ACTIVE)
    tags: List[str] = Field(default_factory=list)

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('角色名称不能为空')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        return list(set(tag.strip() for tag in v if tag and tag.strip()))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GeographicalInfo(BaseModel):
    """地理信息"""
    coordinates: Dict[str, Any] = Field(default_factory=dict)
    size: Optional[str] = None
    terrain: Optional[str] = None
    climate: Optional[str] = None
    natural_resources: List[str] = Field(default_factory=list)
    dangers: List[str] = Field(default_factory=list)


class PoliticalInfo(BaseModel):
    """政治信息"""
    ruling_organization: Optional[str] = None
    population: Optional[int] = Field(None, ge=0)
    governance_system: Optional[str] = None
    laws_and_customs: List[str] = Field(default_factory=list)
    diplomatic_relations: List[Dict[str, Any]] = Field(default_factory=list)


class CultivationAspects(BaseModel):
    """修炼方面"""
    spiritual_energy_density: Optional[int] = Field(None, ge=0, le=10)
    law_chain_affinities: List[str] = Field(default_factory=list)
    cultivation_bonuses: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    special_phenomena: List[str] = Field(default_factory=list)


class PhysicalDescription(BaseModel):
    """物理描述"""
    architecture: Optional[str] = None
    landmarks: List[str] = Field(default_factory=list)
    atmosphere: Optional[str] = None
    sensory_details: Dict[str, str] = Field(default_factory=dict)
    notable_features: List[str] = Field(default_factory=list)


class LocationHistory(BaseModel):
    """地点历史"""
    founding_story: Optional[str] = None
    major_events: List[Dict[str, Any]] = Field(default_factory=list)
    previous_rulers: List[str] = Field(default_factory=list)
    legendary_figures: List[str] = Field(default_factory=list)
    mysterious_aspects: List[str] = Field(default_factory=list)


class ConnectedLocation(BaseModel):
    """连接地点"""
    location_id: str = Field(..., description="地点ID")
    connection_type: str = Field(..., description="连接类型")
    travel_method: Optional[str] = None
    travel_time: Optional[str] = None
    difficulty: Optional[str] = None


class StorySignificance(BaseModel):
    """故事意义"""
    plot_importance: int = Field(default=1, ge=1, le=10)
    symbolic_meaning: Optional[str] = None
    character_connections: List[str] = Field(default_factory=list)
    planned_scenes: List[str] = Field(default_factory=list)


class Location(BaseModelWithTimestamp):
    """地点模型 - MongoDB文档"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    novel_id: str = Field(..., description="关联的小说ID")
    name: str = Field(..., min_length=1, max_length=255, description="地点名称")
    location_type: LocationType = Field(..., description="地点类型")
    domain_affiliation: Optional[str] = None
    geographical_info: GeographicalInfo = Field(default_factory=GeographicalInfo)
    political_info: PoliticalInfo = Field(default_factory=PoliticalInfo)
    cultivation_aspects: CultivationAspects = Field(default_factory=CultivationAspects)
    physical_description: PhysicalDescription = Field(default_factory=PhysicalDescription)
    history: LocationHistory = Field(default_factory=LocationHistory)
    connected_locations: List[ConnectedLocation] = Field(default_factory=list)
    story_significance: StorySignificance = Field(default_factory=StorySignificance)
    status: LocationStatus = Field(default=LocationStatus.ACTIVE)
    tags: List[str] = Field(default_factory=list)

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('地点名称不能为空')
        return v.strip()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }