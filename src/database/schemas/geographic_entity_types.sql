-- =============================================================================
-- 地理实体类型初始化脚本
-- 为裂世九域小说创建地理相关的实体类型
-- =============================================================================

-- 插入地理实体类型定义
-- 假设 novel_id = 1 对应"裂世九域"小说

-- 1. 区域 (Region)
INSERT INTO entity_types (novel_id, name, display_name, schema_definition, validation_rules, display_config) VALUES
(1, 'region', '区域',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["geographic_type", "main_feature", "economic_focus", "domain_code"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "区域名称"},
    "note": {"type": "string", "max_length": 500, "description": "区域描述"},
    "geographic_type": {"type": "enum", "values": ["平原", "丘陵", "高地", "山地", "水网", "盆地", "走带"], "description": "地理类型"},
    "main_feature": {"type": "string", "max_length": 200, "description": "主要特征"},
    "economic_focus": {"type": "string", "max_length": 200, "description": "经济重点"},
    "domain_code": {"type": "string", "max_length": 20, "description": "所属域代码"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "geographic_type", "main_feature"],
  "detail_tabs": ["basic_info", "geographic_features", "economic_info"],
  "color_scheme": "#8FBC8F"
}'),

-- 2. 城市 (City)
(1, 'city', '城市',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["population_level", "administrative_level", "main_industries", "defensive_features", "region_name"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "城市名称"},
    "note": {"type": "string", "max_length": 500, "description": "城市描述"},
    "population_level": {"type": "enum", "values": ["特大", "大", "中", "小"], "description": "人口规模"},
    "administrative_level": {"type": "enum", "values": ["都城", "府城", "州城", "县城"], "description": "行政等级"},
    "main_industries": {"type": "array", "item_type": "string", "description": "主要产业"},
    "defensive_features": {"type": "string", "max_length": 200, "description": "防御特征"},
    "region_name": {"type": "string", "max_length": 100, "description": "所属区域"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "administrative_level", "population_level"],
  "detail_tabs": ["basic_info", "administration", "economy", "defense"],
  "color_scheme": "#4682B4"
}'),

-- 3. 城镇 (Town)
(1, 'town', '城镇',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["town_type", "specialties", "administrative_level", "parent_city"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "城镇名称"},
    "note": {"type": "string", "max_length": 500, "description": "城镇描述"},
    "town_type": {"type": "enum", "values": ["县城", "集镇", "坊镇", "关镇", "市镇"], "description": "城镇类型"},
    "specialties": {"type": "array", "item_type": "string", "description": "特色产业"},
    "administrative_level": {"type": "string", "max_length": 50, "description": "行政等级"},
    "parent_city": {"type": "string", "max_length": 100, "description": "归属城市"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "town_type", "specialties"],
  "detail_tabs": ["basic_info", "specialties", "administration"],
  "color_scheme": "#20B2AA"
}'),

-- 4. 村庄 (Village)
(1, 'village', '村庄',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["village_type", "main_livelihood", "special_features", "parent_town"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "村庄名称"},
    "note": {"type": "string", "max_length": 500, "description": "村庄描述"},
    "village_type": {"type": "enum", "values": ["农村", "渔村", "工匠村", "庄园", "营地", "堡村"], "description": "村庄类型"},
    "main_livelihood": {"type": "string", "max_length": 200, "description": "主要生计"},
    "special_features": {"type": "array", "item_type": "string", "description": "特殊特征"},
    "parent_town": {"type": "string", "max_length": 100, "description": "归属城镇"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "village_type", "main_livelihood"],
  "detail_tabs": ["basic_info", "livelihood", "features"],
  "color_scheme": "#DAA520"
}'),

-- 5. 地标 (Landmark)
(1, 'landmark', '地标',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["landmark_type", "significance", "historical_importance", "accessibility"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "地标名称"},
    "note": {"type": "string", "max_length": 500, "description": "地标描述"},
    "landmark_type": {"type": "enum", "values": ["祭台", "书院", "高台", "石塔", "广场", "试验场", "祭场"], "description": "地标类型"},
    "significance": {"type": "string", "max_length": 300, "description": "重要意义"},
    "historical_importance": {"type": "integer", "min": 1, "max": 10, "description": "历史重要性"},
    "accessibility": {"type": "enum", "values": ["公开", "限制", "禁止", "特殊"], "description": "可达性"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "landmark_type", "historical_importance"],
  "detail_tabs": ["basic_info", "significance", "access"],
  "color_scheme": "#CD853F"
}'),

-- 6. 建筑 (Building)
(1, 'building', '建筑',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["building_type", "function", "importance_level", "owner_organization", "capacity"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "建筑名称"},
    "note": {"type": "string", "max_length": 500, "description": "建筑描述"},
    "building_type": {"type": "enum", "values": ["官署", "宗教", "商业", "工坊", "库房", "学院", "住宅", "军事"], "description": "建筑类型"},
    "function": {"type": "string", "max_length": 200, "description": "主要功能"},
    "importance_level": {"type": "integer", "min": 1, "max": 10, "description": "重要程度"},
    "owner_organization": {"type": "string", "max_length": 100, "description": "所属组织"},
    "capacity": {"type": "string", "max_length": 100, "description": "容量规模"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "building_type", "function", "importance_level"],
  "detail_tabs": ["basic_info", "function", "organization"],
  "color_scheme": "#A0522D"
}'),

-- 7. 自然景观 (Natural Feature)
(1, 'natural_feature', '自然景观',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["feature_type", "resources", "accessibility", "seasonal_changes", "hazards"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "景观名称"},
    "note": {"type": "string", "max_length": 500, "description": "景观描述"},
    "feature_type": {"type": "enum", "values": ["河流", "山川", "湖泊", "森林", "湿地", "峡谷", "平原", "洞穴", "温泉"], "description": "地貌类型"},
    "resources": {"type": "array", "item_type": "string", "description": "相关资源"},
    "accessibility": {"type": "enum", "values": ["易达", "一般", "困难", "危险"], "description": "可达性"},
    "seasonal_changes": {"type": "string", "max_length": 300, "description": "季节变化"},
    "hazards": {"type": "array", "item_type": "string", "description": "潜在危险"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "feature_type", "accessibility"],
  "detail_tabs": ["basic_info", "resources", "environment"],
  "color_scheme": "#228B22"
}'),

-- 8. 基础设施 (Infrastructure)
(1, 'infrastructure', '基础设施',
'{
  "required_fields": ["name", "note"],
  "optional_fields": ["infrastructure_type", "capacity", "strategic_importance", "maintenance_level", "traffic_flow"],
  "field_definitions": {
    "name": {"type": "string", "max_length": 100, "description": "设施名称"},
    "note": {"type": "string", "max_length": 500, "description": "设施描述"},
    "infrastructure_type": {"type": "enum", "values": ["道路", "桥梁", "关卡", "码头", "驿站", "烽台", "水利", "城门"], "description": "设施类型"},
    "capacity": {"type": "string", "max_length": 100, "description": "容量规模"},
    "strategic_importance": {"type": "integer", "min": 1, "max": 10, "description": "战略重要性"},
    "maintenance_level": {"type": "enum", "values": ["良好", "一般", "需修", "破损"], "description": "维护状况"},
    "traffic_flow": {"type": "enum", "values": ["繁忙", "正常", "稀少", "废弃"], "description": "通行状况"}
  }
}',
'{
  "name": {"required": true, "min_length": 2},
  "note": {"required": true, "min_length": 5}
}',
'{
  "list_display": ["name", "infrastructure_type", "strategic_importance"],
  "detail_tabs": ["basic_info", "capacity", "maintenance"],
  "color_scheme": "#696969"
}');

-- 创建地理分类体系
INSERT INTO categories (novel_id, type, name, code, level, sort_order, description) VALUES
-- 地理层级分类
(1, 'geographic_level', '域级', 'domain_level', 1, 1, '最高地理层级'),
(1, 'geographic_level', '区域级', 'region_level', 2, 2, '大区域地理层级'),
(1, 'geographic_level', '城市级', 'city_level', 3, 3, '城市地理层级'),
(1, 'geographic_level', '城镇级', 'town_level', 4, 4, '城镇地理层级'),
(1, 'geographic_level', '村庄级', 'village_level', 5, 5, '村庄地理层级'),
(1, 'geographic_level', '设施级', 'facility_level', 6, 6, '具体设施层级'),

-- 地理功能分类
(1, 'geographic_function', '行政管理', 'administrative', 1, 1, '行政管理功能'),
(1, 'geographic_function', '经济贸易', 'economic', 1, 2, '经济贸易功能'),
(1, 'geographic_function', '军事防御', 'military', 1, 3, '军事防御功能'),
(1, 'geographic_function', '宗教文化', 'religious', 1, 4, '宗教文化功能'),
(1, 'geographic_function', '工艺制造', 'crafting', 1, 5, '工艺制造功能'),
(1, 'geographic_function', '交通运输', 'transport', 1, 6, '交通运输功能'),
(1, 'geographic_function', '农业生产', 'agriculture', 1, 7, '农业生产功能'),
(1, 'geographic_function', '资源开采', 'resource', 1, 8, '资源开采功能');

-- 更新统计信息
UPDATE novels SET entity_count = entity_count + 8 WHERE id = 1;

COMMIT;