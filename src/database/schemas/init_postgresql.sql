-- 网络小说世界观数据库初始化脚本
-- 支持多小说的通用架构

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. 小说项目管理表
-- =============================================================================

-- 小说项目表
CREATE TABLE novels (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE, -- 代码标识：lieshi_jiuyu
    author VARCHAR(100),
    genre VARCHAR(50), -- 玄幻、仙侠、都市等
    status VARCHAR(20) DEFAULT 'active', -- active/paused/completed/archived

    -- 世界观类型
    world_type VARCHAR(50), -- cultivation/magic/scifi/modern等

    -- 配置信息
    settings JSONB DEFAULT '{}', -- 小说特有配置

    -- 统计信息
    entity_count INTEGER DEFAULT 0,
    event_count INTEGER DEFAULT 0,

    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

-- 小说模板表
CREATE TABLE novel_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- "修仙世界观模板"
    world_type VARCHAR(50) NOT NULL,
    description TEXT,

    -- 默认配置模板
    default_settings JSONB DEFAULT '{}',

    -- 默认的实体类型配置
    default_schemas JSONB DEFAULT '{}', -- 定义该类型小说的标准实体结构

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 2. 通用实体系统
-- =============================================================================

-- 实体类型定义表
CREATE TABLE entity_types (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL, -- character/location/organization/item/ability
    display_name VARCHAR(100) NOT NULL, -- 角色/地点/势力/物品/技能

    -- 字段定义
    schema_definition JSONB NOT NULL DEFAULT '{}', -- 定义该实体类型的字段结构

    -- 约束和验证规则
    validation_rules JSONB DEFAULT '{}',

    -- 显示配置
    display_config JSONB DEFAULT '{}', -- UI显示相关配置

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, name)
);

-- 通用实体表
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    entity_type_id INTEGER NOT NULL REFERENCES entity_types(id) ON DELETE CASCADE,

    -- 基础属性
    name VARCHAR(200) NOT NULL,
    code VARCHAR(100), -- 实体的唯一标识符
    status VARCHAR(20) DEFAULT 'active', -- active/inactive/deleted

    -- 动态属性（根据entity_type的schema存储）
    attributes JSONB NOT NULL DEFAULT '{}',

    -- 计算属性（用于查询优化）
    computed_values JSONB DEFAULT '{}',

    -- 元数据
    tags TEXT[] DEFAULT '{}', -- 标签数组
    priority INTEGER DEFAULT 0, -- 重要性：主角>重要NPC>普通NPC

    -- 版本控制
    version INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 在同一小说内name和code应该唯一
    UNIQUE(novel_id, code)
);

-- 实体关系表
CREATE TABLE entity_relationships (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    source_entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,

    relationship_type VARCHAR(100) NOT NULL, -- belongs_to/controls/masters/loves/hates

    -- 关系属性
    attributes JSONB DEFAULT '{}',

    -- 关系强度和状态
    strength INTEGER DEFAULT 1 CHECK (strength >= 1 AND strength <= 10),
    status VARCHAR(20) DEFAULT 'active',

    -- 时效性
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 防止重复关系
    UNIQUE(source_entity_id, target_entity_id, relationship_type, valid_from)
);

-- =============================================================================
-- 3. 分类和层级系统
-- =============================================================================

-- 通用分类表（域、境界、势力等级等）
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- domain/realm/rank/faction_type等

    name VARCHAR(100) NOT NULL,
    code VARCHAR(50),
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,

    -- 层级信息
    level INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,

    -- 属性配置
    attributes JSONB DEFAULT '{}',

    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, type, code)
);

-- 实体分类关联表
CREATE TABLE entity_categories (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,

    -- 关联属性（如在某个境界的进度）
    attributes JSONB DEFAULT '{}',

    -- 时效性
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(entity_id, category_id, valid_from)
);

-- =============================================================================
-- 4. 事件和时间线系统
-- =============================================================================

-- 事件表
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    name VARCHAR(200) NOT NULL,
    event_type VARCHAR(50), -- battle/breakthrough/meeting/discovery

    -- 时间信息
    occurred_at TIMESTAMP,
    in_world_time VARCHAR(100), -- 小说世界内的时间表示
    sequence_order INTEGER, -- 剧情顺序

    -- 地点
    location_entity_id INTEGER REFERENCES entities(id) ON DELETE SET NULL,

    -- 影响和重要性
    impact_level INTEGER DEFAULT 1 CHECK (impact_level >= 1 AND impact_level <= 10),
    scope VARCHAR(20) DEFAULT 'local', -- local/regional/domain/world

    -- 事件属性
    attributes JSONB DEFAULT '{}',

    description TEXT,
    status VARCHAR(20) DEFAULT 'completed', -- planned/ongoing/completed/cancelled

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 事件参与者表
CREATE TABLE event_participants (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,

    role VARCHAR(50), -- protagonist/antagonist/witness/victim/supporter
    importance INTEGER DEFAULT 1 CHECK (importance >= 1 AND importance <= 10),

    -- 参与详情
    attributes JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(event_id, entity_id)
);

-- =============================================================================
-- 5. 版本和审计系统
-- =============================================================================

-- 数据版本表
CREATE TABLE schema_versions (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,

    -- 变更信息
    changes JSONB DEFAULT '{}',
    migration_script TEXT,

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100) DEFAULT 'system'
);

-- 审计日志表
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER REFERENCES novels(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    operation VARCHAR(20) NOT NULL, -- INSERT/UPDATE/DELETE

    old_values JSONB,
    new_values JSONB,

    user_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 6. 索引优化
-- =============================================================================

-- 核心查询索引
CREATE INDEX idx_novels_code ON novels(code);
CREATE INDEX idx_novels_status ON novels(status);
CREATE INDEX idx_novels_world_type ON novels(world_type);

CREATE INDEX idx_entity_types_novel ON entity_types(novel_id);
CREATE INDEX idx_entity_types_novel_name ON entity_types(novel_id, name);

CREATE INDEX idx_entities_novel_type ON entities(novel_id, entity_type_id);
CREATE INDEX idx_entities_novel_name ON entities(novel_id, name);
CREATE INDEX idx_entities_novel_code ON entities(novel_id, code);
CREATE INDEX idx_entities_status ON entities(novel_id, status);
CREATE INDEX idx_entities_priority ON entities(novel_id, priority DESC);

-- JSONB 字段的 GIN 索引
CREATE INDEX idx_entities_attributes_gin ON entities USING GIN(attributes);
CREATE INDEX idx_entities_computed_gin ON entities USING GIN(computed_values);
CREATE INDEX idx_entities_tags_gin ON entities USING GIN(tags);

CREATE INDEX idx_relationships_novel ON entity_relationships(novel_id);
CREATE INDEX idx_relationships_source ON entity_relationships(source_entity_id);
CREATE INDEX idx_relationships_target ON entity_relationships(target_entity_id);
CREATE INDEX idx_relationships_type ON entity_relationships(novel_id, relationship_type);
CREATE INDEX idx_relationships_status ON entity_relationships(novel_id, status);

CREATE INDEX idx_categories_novel_type ON categories(novel_id, type);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_level ON categories(novel_id, type, level);

CREATE INDEX idx_entity_categories_novel ON entity_categories(novel_id);
CREATE INDEX idx_entity_categories_entity ON entity_categories(entity_id);
CREATE INDEX idx_entity_categories_category ON entity_categories(category_id);

CREATE INDEX idx_events_novel_sequence ON events(novel_id, sequence_order);
CREATE INDEX idx_events_novel_time ON events(novel_id, occurred_at);
CREATE INDEX idx_events_type ON events(novel_id, event_type);
CREATE INDEX idx_events_location ON events(location_entity_id);

CREATE INDEX idx_event_participants_event ON event_participants(event_id);
CREATE INDEX idx_event_participants_entity ON event_participants(entity_id);

CREATE INDEX idx_audit_logs_novel ON audit_logs(novel_id);
CREATE INDEX idx_audit_logs_table ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- =============================================================================
-- 7. 触发器和函数
-- =============================================================================

-- 更新 updated_at 字段的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加 updated_at 触发器
CREATE TRIGGER update_novels_updated_at BEFORE UPDATE ON novels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 审计日志触发器函数
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    novel_id_val INTEGER;
BEGIN
    -- 尝试获取 novel_id
    IF TG_TABLE_NAME = 'novels' THEN
        novel_id_val := COALESCE(NEW.id, OLD.id);
    ELSE
        novel_id_val := COALESCE(NEW.novel_id, OLD.novel_id);
    END IF;

    -- 插入审计记录
    INSERT INTO audit_logs (novel_id, table_name, record_id, operation, old_values, new_values)
    VALUES (
        novel_id_val,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        CASE WHEN TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 为关键表添加审计触发器
CREATE TRIGGER audit_novels AFTER INSERT OR UPDATE OR DELETE ON novels
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_entities AFTER INSERT OR UPDATE OR DELETE ON entities
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_entity_relationships AFTER INSERT OR UPDATE OR DELETE ON entity_relationships
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- 统计信息更新函数
CREATE OR REPLACE FUNCTION update_novel_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE novels SET
            entity_count = entity_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.novel_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE novels SET
            entity_count = entity_count - 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.novel_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 实体统计触发器
CREATE TRIGGER update_novel_entity_stats AFTER INSERT OR DELETE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_novel_stats();

-- =============================================================================
-- 8. 初始化基础数据
-- =============================================================================

-- 插入默认的小说模板
INSERT INTO novel_templates (name, world_type, description, default_settings, default_schemas) VALUES
('修仙世界观模板', 'cultivation', '传统修仙小说的世界观模板，包含境界体系、宗门势力等',
'{
  "cultivation_system": {
    "type": "traditional",
    "realms": ["练气", "筑基", "金丹", "元婴", "化神", "炼虚", "合体", "大乘", "渡劫", "真仙"],
    "power_source": "spiritual_energy"
  },
  "world_structure": {
    "type": "hierarchical",
    "levels": ["下界", "中界", "上界"],
    "governance": "sect_based"
  }
}',
'{
  "character": {
    "required": ["name", "realm", "sect"],
    "optional": ["spiritual_root", "techniques", "treasures"]
  },
  "location": {
    "required": ["name", "type", "controlling_sect"],
    "optional": ["spiritual_energy", "resources"]
  },
  "organization": {
    "required": ["name", "type", "territory"],
    "optional": ["founder", "specialties", "allies"]
  }
}'),

('现代都市模板', 'modern', '现代都市背景的小说模板',
'{
  "setting": "modern_city",
  "time_period": "contemporary",
  "technology_level": "current"
}',
'{
  "character": {
    "required": ["name", "occupation", "location"],
    "optional": ["background", "skills", "relationships"]
  },
  "location": {
    "required": ["name", "type", "district"],
    "optional": ["description", "owner"]
  }
}'),

('西方魔幻模板', 'magic', '西方魔幻世界观模板',
'{
  "magic_system": {
    "type": "elemental",
    "elements": ["fire", "water", "earth", "air", "light", "dark"],
    "advancement": "spell_mastery"
  },
  "world_structure": {
    "type": "kingdom_based",
    "governance": "royal_council"
  }
}',
'{
  "character": {
    "required": ["name", "class", "level"],
    "optional": ["race", "spells", "equipment"]
  },
  "location": {
    "required": ["name", "type", "kingdom"],
    "optional": ["magic_level", "population"]
  }
}');

-- 创建视图，便于查询
CREATE VIEW novel_entity_summary AS
SELECT
    n.id as novel_id,
    n.title as novel_title,
    n.code as novel_code,
    et.name as entity_type,
    et.display_name as entity_type_display,
    COUNT(e.id) as entity_count
FROM novels n
LEFT JOIN entity_types et ON n.id = et.novel_id
LEFT JOIN entities e ON et.id = e.entity_type_id AND e.status = 'active'
WHERE n.status = 'active' AND et.is_active = true
GROUP BY n.id, n.title, n.code, et.id, et.name, et.display_name
ORDER BY n.id, et.id;

-- 权限设置（根据实际需要调整）
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO novel_app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO novel_app_user;