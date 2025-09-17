"""
地理数据模型定义
扩展原有models.py，添加地理实体相关模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .models import BaseDBModel, Entity


# =============================================================================
# 地理相关枚举
# =============================================================================

class GeographicType(str, Enum):
    """地理类型枚举"""
    PLAIN = "平原"
    HILLS = "丘陵"
    HIGHLAND = "高地"
    MOUNTAIN = "山地"
    WATER_NETWORK = "水网"
    BASIN = "盆地"
    CORRIDOR = "走带"


class PopulationLevel(str, Enum):
    """人口规模枚举"""
    MEGA = "特大"
    LARGE = "大"
    MEDIUM = "中"
    SMALL = "小"


class AdministrativeLevel(str, Enum):
    """行政等级枚举"""
    CAPITAL = "都城"
    PREFECTURE = "府城"
    STATE = "州城"
    COUNTY = "县城"


class TownType(str, Enum):
    """城镇类型枚举"""
    COUNTY_SEAT = "县城"
    MARKET_TOWN = "集镇"
    WORKSHOP_TOWN = "坊镇"
    BORDER_TOWN = "关镇"
    TRADE_TOWN = "市镇"


class VillageType(str, Enum):
    """村庄类型枚举"""
    FARMING = "农村"
    FISHING = "渔村"
    CRAFTSMAN = "工匠村"
    MANOR = "庄园"
    CAMP = "营地"
    FORTRESS = "堡村"


class LandmarkType(str, Enum):
    """地标类型枚举"""
    ALTAR = "祭台"
    ACADEMY = "书院"
    PLATFORM = "高台"
    TOWER = "石塔"
    SQUARE = "广场"
    TEST_SITE = "试验场"
    RITUAL_GROUND = "祭场"


class BuildingType(str, Enum):
    """建筑类型枚举"""
    GOVERNMENT = "官署"
    RELIGIOUS = "宗教"
    COMMERCIAL = "商业"
    WORKSHOP = "工坊"
    STORAGE = "库房"
    ACADEMY = "学院"
    RESIDENTIAL = "住宅"
    MILITARY = "军事"


class NaturalFeatureType(str, Enum):
    """自然景观类型枚举"""
    RIVER = "河流"
    MOUNTAIN = "山川"
    LAKE = "湖泊"
    FOREST = "森林"
    WETLAND = "湿地"
    CANYON = "峡谷"
    PLAIN = "平原"
    CAVE = "洞穴"
    HOT_SPRING = "温泉"


class InfrastructureType(str, Enum):
    """基础设施类型枚举"""
    ROAD = "道路"
    BRIDGE = "桥梁"
    CHECKPOINT = "关卡"
    DOCK = "码头"
    POST_STATION = "驿站"
    BEACON = "烽台"
    WATER_CONSERVANCY = "水利"
    CITY_GATE = "城门"


class Accessibility(str, Enum):
    """可达性枚举"""
    EASY = "易达"
    NORMAL = "一般"
    DIFFICULT = "困难"
    DANGEROUS = "危险"
    PUBLIC = "公开"
    RESTRICTED = "限制"
    FORBIDDEN = "禁止"
    SPECIAL = "特殊"


class MaintenanceLevel(str, Enum):
    """维护状况枚举"""
    GOOD = "良好"
    FAIR = "一般"
    NEEDS_REPAIR = "需修"
    DAMAGED = "破损"


class TrafficFlow(str, Enum):
    """通行状况枚举"""
    BUSY = "繁忙"
    NORMAL = "正常"
    SPARSE = "稀少"
    ABANDONED = "废弃"


# =============================================================================
# 地理实体基础模型
# =============================================================================

class GeographicEntity(Entity):
    """地理实体基础模型"""
    domain_code: Optional[str] = Field(None, max_length=20, description="所属域代码")
    region_name: Optional[str] = Field(None, max_length=100, description="所属区域")
    parent_entity_id: Optional[int] = Field(None, description="父级实体ID")

    # 地理坐标（可选，用于地图显示）
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")

    # 地理属性
    geographic_importance: int = Field(1, description="地理重要性")
    accessibility_level: Optional[Accessibility] = Field(None, description="可达性")

    @validator('geographic_importance')
    def validate_importance(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('地理重要性必须在1-10之间')
        return v


# =============================================================================
# 具体地理实体模型
# =============================================================================

class Region(GeographicEntity):
    """区域模型"""
    geographic_type: Optional[GeographicType] = Field(None, description="地理类型")
    main_feature: Optional[str] = Field(None, max_length=200, description="主要特征")
    economic_focus: Optional[str] = Field(None, max_length=200, description="经济重点")

    # 区域统计
    city_count: int = Field(0, description="城市数量")
    town_count: int = Field(0, description="城镇数量")
    village_count: int = Field(0, description="村庄数量")


class City(GeographicEntity):
    """城市模型"""
    population_level: Optional[PopulationLevel] = Field(None, description="人口规模")
    administrative_level: Optional[AdministrativeLevel] = Field(None, description="行政等级")
    main_industries: List[str] = Field(default_factory=list, description="主要产业")
    defensive_features: Optional[str] = Field(None, max_length=200, description="防御特征")

    # 城市统计
    building_count: int = Field(0, description="建筑数量")
    landmark_count: int = Field(0, description="地标数量")


class Town(GeographicEntity):
    """城镇模型"""
    town_type: Optional[TownType] = Field(None, description="城镇类型")
    specialties: List[str] = Field(default_factory=list, description="特色产业")
    parent_city: Optional[str] = Field(None, max_length=100, description="归属城市")


class Village(GeographicEntity):
    """村庄模型"""
    village_type: Optional[VillageType] = Field(None, description="村庄类型")
    main_livelihood: Optional[str] = Field(None, max_length=200, description="主要生计")
    special_features: List[str] = Field(default_factory=list, description="特殊特征")
    parent_town: Optional[str] = Field(None, max_length=100, description="归属城镇")


class Landmark(GeographicEntity):
    """地标模型"""
    landmark_type: Optional[LandmarkType] = Field(None, description="地标类型")
    significance: Optional[str] = Field(None, max_length=300, description="重要意义")
    historical_importance: int = Field(1, description="历史重要性")

    @validator('historical_importance')
    def validate_historical_importance(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('历史重要性必须在1-10之间')
        return v


class Building(GeographicEntity):
    """建筑模型"""
    building_type: Optional[BuildingType] = Field(None, description="建筑类型")
    function: Optional[str] = Field(None, max_length=200, description="主要功能")
    importance_level: int = Field(1, description="重要程度")
    owner_organization: Optional[str] = Field(None, max_length=100, description="所属组织")
    capacity: Optional[str] = Field(None, max_length=100, description="容量规模")

    @validator('importance_level')
    def validate_importance_level(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('重要程度必须在1-10之间')
        return v


class NaturalFeature(GeographicEntity):
    """自然景观模型"""
    feature_type: Optional[NaturalFeatureType] = Field(None, description="地貌类型")
    resources: List[str] = Field(default_factory=list, description="相关资源")
    seasonal_changes: Optional[str] = Field(None, max_length=300, description="季节变化")
    hazards: List[str] = Field(default_factory=list, description="潜在危险")


class Infrastructure(GeographicEntity):
    """基础设施模型"""
    infrastructure_type: Optional[InfrastructureType] = Field(None, description="设施类型")
    capacity: Optional[str] = Field(None, max_length=100, description="容量规模")
    strategic_importance: int = Field(1, description="战略重要性")
    maintenance_level: Optional[MaintenanceLevel] = Field(None, description="维护状况")
    traffic_flow: Optional[TrafficFlow] = Field(None, description="通行状况")

    @validator('strategic_importance')
    def validate_strategic_importance(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('战略重要性必须在1-10之间')
        return v


# =============================================================================
# 地理关系模型
# =============================================================================

class GeographicRelationshipType(str, Enum):
    """地理关系类型枚举"""
    # 空间关系
    CONTAINS = "contains"
    CONTAINED_BY = "contained_by"
    LOCATED_IN = "located_in"
    ADJACENT_TO = "adjacent_to"

    # 功能关系
    SERVES = "serves"
    SERVED_BY = "served_by"
    CONNECTS = "connects"
    CONNECTED_BY = "connected_by"
    SUPPLIES = "supplies"
    SUPPLIED_BY = "supplied_by"

    # 管理关系
    GOVERNS = "governs"
    GOVERNED_BY = "governed_by"
    ADMINISTERS = "administers"
    ADMINISTERED_BY = "administered_by"

    # 交通关系
    ACCESSIBLE_VIA = "accessible_via"
    PROVIDES_ACCESS_TO = "provides_access_to"
    TRADE_ROUTE = "trade_route"

    # 战略关系
    DEFENDS = "defends"
    DEFENDED_BY = "defended_by"
    CONTROLS = "controls"
    CONTROLLED_BY = "controlled_by"


class GeographicRelationship(BaseDBModel):
    """地理关系模型"""
    novel_id: int = Field(..., description="所属小说ID")
    source_entity_id: int = Field(..., description="源实体ID")
    target_entity_id: int = Field(..., description="目标实体ID")
    relationship_type: GeographicRelationshipType = Field(..., description="关系类型")

    # 关系属性
    distance: Optional[float] = Field(None, description="距离（里）")
    travel_time: Optional[str] = Field(None, max_length=50, description="旅行时间")
    difficulty: Optional[int] = Field(None, description="通行难度")
    cost: Optional[str] = Field(None, max_length=100, description="通行成本")

    # 季节性和条件
    seasonal_availability: Optional[str] = Field(None, max_length=200, description="季节性可用")
    conditions: Optional[str] = Field(None, max_length=300, description="通行条件")

    # 关系强度
    strength: int = Field(1, description="关系强度")
    importance: int = Field(1, description="关系重要性")

    @validator('strength', 'importance')
    def validate_levels(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('等级必须在1-10之间')
        return v

    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('通行难度必须在1-5之间')
        return v


# =============================================================================
# 地理查询和响应模型
# =============================================================================

class GeographicQuery(BaseModel):
    """地理查询模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_codes: List[str] = Field(default_factory=list, description="域代码列表")
    entity_types: List[str] = Field(default_factory=list, description="实体类型列表")
    region_names: List[str] = Field(default_factory=list, description="区域名称列表")

    # 空间查询
    center_entity_id: Optional[int] = Field(None, description="中心实体ID")
    max_distance: Optional[float] = Field(None, description="最大距离")

    # 属性过滤
    min_importance: Optional[int] = Field(None, description="最小重要性")
    accessibility: Optional[List[Accessibility]] = Field(None, description="可达性筛选")

    # 分页
    limit: int = Field(20, description="限制数量")
    offset: int = Field(0, description="偏移量")


class GeographicHierarchy(BaseModel):
    """地理层级模型"""
    domain: Optional[str] = None
    region: Optional[Region] = None
    city: Optional[City] = None
    town: Optional[Town] = None
    village: Optional[Village] = None
    entities: List[GeographicEntity] = Field(default_factory=list)


class GeographicSummary(BaseModel):
    """地理概要模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_code: str = Field(..., description="域代码")

    # 统计信息
    total_regions: int = Field(0, description="区域总数")
    total_cities: int = Field(0, description="城市总数")
    total_towns: int = Field(0, description="城镇总数")
    total_villages: int = Field(0, description="村庄总数")
    total_landmarks: int = Field(0, description="地标总数")
    total_buildings: int = Field(0, description="建筑总数")
    total_natural_features: int = Field(0, description="自然景观总数")
    total_infrastructure: int = Field(0, description="基础设施总数")

    # 层级数据
    hierarchies: List[GeographicHierarchy] = Field(default_factory=list)


# =============================================================================
# 创建和更新请求模型
# =============================================================================

class CreateGeographicEntityRequest(BaseModel):
    """创建地理实体请求模型"""
    novel_id: int = Field(..., description="小说ID")
    entity_type: str = Field(..., description="实体类型")
    name: str = Field(..., max_length=100, description="实体名称")
    note: str = Field(..., max_length=500, description="实体描述")

    # 位置信息
    domain_code: Optional[str] = Field(None, max_length=20, description="所属域代码")
    region_name: Optional[str] = Field(None, max_length=100, description="所属区域")
    parent_entity_id: Optional[int] = Field(None, description="父级实体ID")

    # 扩展属性
    attributes: Dict[str, Any] = Field(default_factory=dict, description="扩展属性")
    tags: List[str] = Field(default_factory=list, description="标签")
    geographic_importance: int = Field(1, description="地理重要性")


class UpdateGeographicEntityRequest(BaseModel):
    """更新地理实体请求模型"""
    name: Optional[str] = Field(None, max_length=100, description="实体名称")
    note: Optional[str] = Field(None, max_length=500, description="实体描述")
    attributes: Optional[Dict[str, Any]] = Field(None, description="扩展属性")
    tags: Optional[List[str]] = Field(None, description="标签")
    geographic_importance: Optional[int] = Field(None, description="地理重要性")
    accessibility_level: Optional[Accessibility] = Field(None, description="可达性")


class CreateGeographicRelationshipRequest(BaseModel):
    """创建地理关系请求模型"""
    novel_id: int = Field(..., description="小说ID")
    source_entity_id: int = Field(..., description="源实体ID")
    target_entity_id: int = Field(..., description="目标实体ID")
    relationship_type: GeographicRelationshipType = Field(..., description="关系类型")

    # 关系属性
    distance: Optional[float] = Field(None, description="距离")
    travel_time: Optional[str] = Field(None, description="旅行时间")
    difficulty: Optional[int] = Field(None, description="通行难度")
    strength: int = Field(1, description="关系强度")
    importance: int = Field(1, description="关系重要性")


# =============================================================================
# 地理数据导入模型
# =============================================================================

class GeographicDataImport(BaseModel):
    """地理数据导入模型"""
    novel_id: int = Field(..., description="小说ID")
    domain_code: str = Field(..., description="域代码")

    regions: List[Dict[str, str]] = Field(default_factory=list, description="区域数据")
    cities: List[Dict[str, str]] = Field(default_factory=list, description="城市数据")
    towns: List[Dict[str, str]] = Field(default_factory=list, description="城镇数据")
    villages: List[Dict[str, str]] = Field(default_factory=list, description="村庄数据")
    landmarks: List[Dict[str, str]] = Field(default_factory=list, description="地标数据")
    buildings: List[Dict[str, str]] = Field(default_factory=list, description="建筑数据")
    natural_features: List[Dict[str, str]] = Field(default_factory=list, description="自然景观数据")
    infrastructure: List[Dict[str, str]] = Field(default_factory=list, description="基础设施数据")