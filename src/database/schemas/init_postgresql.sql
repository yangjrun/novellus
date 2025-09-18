-- 网络小说世界观数据库初始化脚本
-- 支持多小说的通用架构

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. 小说项目管理表
-- =============================================================================

-- 小说项目表：管理多个小说项目的基本信息和配置
CREATE TABLE novels (
    id SERIAL PRIMARY KEY,                                  -- 小说唯一标识符
    title VARCHAR(200) NOT NULL UNIQUE,                     -- 小说标题，用于显示
    code VARCHAR(50) NOT NULL UNIQUE,                       -- 代码标识：如 lieshi_jiuyu，用于系统内部引用
    author VARCHAR(100),                                     -- 作者名称
    genre VARCHAR(50),                                       -- 小说类型：玄幻、仙侠、都市、科幻等
    status VARCHAR(20) DEFAULT 'active',                     -- 项目状态：active/paused/completed/archived

    -- 世界观类型配置
    world_type VARCHAR(50),                                  -- 世界观类型：cultivation/magic/scifi/modern等，影响默认实体结构

    -- 项目配置信息
    settings JSONB DEFAULT '{}',                             -- 小说特有的自定义配置参数

    -- 统计信息（通过触发器自动维护）
    entity_count INTEGER DEFAULT 0,                          -- 实体总数统计
    event_count INTEGER DEFAULT 0,                           -- 事件总数统计

    -- 时间戳信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 项目创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 最后更新时间
    published_at TIMESTAMP                                   -- 发布时间（可选）
);

-- 小说模板表：预定义的世界观模板，为创建新小说提供标准化配置
CREATE TABLE novel_templates (
    id SERIAL PRIMARY KEY,                                  -- 模板唯一标识符
    name VARCHAR(100) NOT NULL UNIQUE,                      -- 模板名称：如"修仙世界观模板"
    world_type VARCHAR(50) NOT NULL,                        -- 对应的世界观类型
    description TEXT,                                        -- 模板详细描述

    -- 默认配置模板
    default_settings JSONB DEFAULT '{}',                    -- 该类型小说的默认配置参数

    -- 默认的实体类型配置
    default_schemas JSONB DEFAULT '{}',                     -- 定义该类型小说的标准实体结构和字段

    is_active BOOLEAN DEFAULT true,                         -- 模板是否可用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP          -- 模板创建时间
);

-- =============================================================================
-- 2. 通用实体系统
-- =============================================================================

-- 实体类型定义表：定义小说中不同类型实体的结构和行为
CREATE TABLE entity_types (
    id SERIAL PRIMARY KEY,                                          -- 实体类型唯一标识符
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,  -- 所属小说项目
    name VARCHAR(100) NOT NULL,                                     -- 类型内部名称：character/location/organization/item/ability
    display_name VARCHAR(100) NOT NULL,                             -- 类型显示名称：角色/地点/势力/物品/技能

    -- 字段结构定义
    schema_definition JSONB NOT NULL DEFAULT '{}',                 -- 定义该实体类型的字段结构、数据类型和约束

    -- 数据验证规则
    validation_rules JSONB DEFAULT '{}',                           -- 字段验证规则：长度限制、格式要求等

    -- UI显示配置
    display_config JSONB DEFAULT '{}',                             -- 界面显示相关配置：列表字段、详情布局等

    is_active BOOLEAN DEFAULT true,                                -- 实体类型是否可用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                -- 创建时间

    -- 约束：同一小说内实体类型名称唯一
    UNIQUE(novel_id, name)
);

-- 通用实体表：存储小说中的所有实体数据（角色、地点、物品等）
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,                                          -- 实体唯一标识符
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,     -- 所属小说项目
    entity_type_id INTEGER NOT NULL REFERENCES entity_types(id) ON DELETE CASCADE,  -- 实体类型

    -- 基础属性
    name VARCHAR(200) NOT NULL,                                     -- 实体名称，用于显示
    code VARCHAR(100),                                              -- 实体代码标识符，用于系统内部引用
    status VARCHAR(20) DEFAULT 'active',                            -- 实体状态：active/inactive/deleted

    -- 动态属性存储（EAV模式）
    attributes JSONB NOT NULL DEFAULT '{}',                         -- 根据实体类型schema定义的动态属性数据

    -- 性能优化字段
    computed_values JSONB DEFAULT '{}',                             -- 预计算的派生属性，用于加速查询

    -- 元数据和分类
    tags TEXT[] DEFAULT '{}',                                       -- 自定义标签数组，用于分类和筛选
    priority INTEGER DEFAULT 0,                                    -- 重要性等级：主角>重要NPC>普通NPC，影响显示排序

    -- 版本控制
    version INTEGER DEFAULT 1,                                     -- 数据版本号，支持变更追踪

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                -- 最后更新时间

    -- 约束：同一小说内代码标识唯一
    UNIQUE(novel_id, code)
);

-- 实体关系表：定义实体间的各种关系和依赖
CREATE TABLE entity_relationships (
    id SERIAL PRIMARY KEY,                                          -- 关系唯一标识符
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,     -- 所属小说项目

    -- 关系的两端实体
    source_entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,  -- 关系发起方
    target_entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,  -- 关系接受方

    relationship_type VARCHAR(100) NOT NULL,                        -- 关系类型：belongs_to/controls/masters/loves/hates等

    -- 关系详细信息
    attributes JSONB DEFAULT '{}',                                  -- 关系的附加属性和描述信息

    -- 关系强度和状态
    strength INTEGER DEFAULT 1 CHECK (strength >= 1 AND strength <= 10),  -- 关系强度等级（1-10）
    status VARCHAR(20) DEFAULT 'active',                            -- 关系状态：active/inactive/ended

    -- 时间范围控制
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                -- 关系开始时间
    valid_to TIMESTAMP,                                            -- 关系结束时间（可选）

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                -- 记录创建时间

    -- 约束：防止相同关系在相同时间点重复
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
-- 8. 查询视图和辅助功能
-- =============================================================================

-- 创建小说实体统计视图，便于查询和管理
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

-- =============================================================================
-- 9. 表和字段注释
-- =============================================================================

-- 小说项目管理表注释
COMMENT ON TABLE novels IS '小说项目管理表：存储多个小说项目的基本信息和配置';
COMMENT ON COLUMN novels.id IS '小说唯一标识符';
COMMENT ON COLUMN novels.title IS '小说标题，用于显示';
COMMENT ON COLUMN novels.code IS '代码标识符，如 lieshi_jiuyu，用于系统内部引用';
COMMENT ON COLUMN novels.author IS '作者名称';
COMMENT ON COLUMN novels.genre IS '小说类型：玄幻、仙侠、都市、科幻等';
COMMENT ON COLUMN novels.status IS '项目状态：active/paused/completed/archived';
COMMENT ON COLUMN novels.world_type IS '世界观类型：cultivation/magic/scifi/modern等，影响默认实体结构';
COMMENT ON COLUMN novels.settings IS '小说特有的自定义配置参数';
COMMENT ON COLUMN novels.entity_count IS '实体总数统计，通过触发器自动维护';
COMMENT ON COLUMN novels.event_count IS '事件总数统计，通过触发器自动维护';
COMMENT ON COLUMN novels.created_at IS '项目创建时间';
COMMENT ON COLUMN novels.updated_at IS '最后更新时间';
COMMENT ON COLUMN novels.published_at IS '发布时间（可选）';

-- 小说模板表注释
COMMENT ON TABLE novel_templates IS '小说模板表：预定义的世界观模板，为创建新小说提供标准化配置';
COMMENT ON COLUMN novel_templates.id IS '模板唯一标识符';
COMMENT ON COLUMN novel_templates.name IS '模板名称，如"修仙世界观模板"';
COMMENT ON COLUMN novel_templates.world_type IS '对应的世界观类型';
COMMENT ON COLUMN novel_templates.description IS '模板详细描述';
COMMENT ON COLUMN novel_templates.default_settings IS '该类型小说的默认配置参数';
COMMENT ON COLUMN novel_templates.default_schemas IS '定义该类型小说的标准实体结构和字段';
COMMENT ON COLUMN novel_templates.is_active IS '模板是否可用';
COMMENT ON COLUMN novel_templates.created_at IS '模板创建时间';

-- 实体类型定义表注释
COMMENT ON TABLE entity_types IS '实体类型定义表：定义小说中不同类型实体的结构和行为';
COMMENT ON COLUMN entity_types.id IS '实体类型唯一标识符';
COMMENT ON COLUMN entity_types.novel_id IS '所属小说项目';
COMMENT ON COLUMN entity_types.name IS '类型内部名称：character/location/organization/item/ability';
COMMENT ON COLUMN entity_types.display_name IS '类型显示名称：角色/地点/势力/物品/技能';
COMMENT ON COLUMN entity_types.schema_definition IS '定义该实体类型的字段结构、数据类型和约束';
COMMENT ON COLUMN entity_types.validation_rules IS '字段验证规则：长度限制、格式要求等';
COMMENT ON COLUMN entity_types.display_config IS '界面显示相关配置：列表字段、详情布局等';
COMMENT ON COLUMN entity_types.is_active IS '实体类型是否可用';
COMMENT ON COLUMN entity_types.created_at IS '创建时间';

-- 通用实体表注释
COMMENT ON TABLE entities IS '通用实体表：存储小说中的所有实体数据（角色、地点、物品等）';
COMMENT ON COLUMN entities.id IS '实体唯一标识符';
COMMENT ON COLUMN entities.novel_id IS '所属小说项目';
COMMENT ON COLUMN entities.entity_type_id IS '实体类型';
COMMENT ON COLUMN entities.name IS '实体名称，用于显示';
COMMENT ON COLUMN entities.code IS '实体代码标识符，用于系统内部引用';
COMMENT ON COLUMN entities.status IS '实体状态：active/inactive/deleted';
COMMENT ON COLUMN entities.attributes IS '根据实体类型schema定义的动态属性数据';
COMMENT ON COLUMN entities.computed_values IS '预计算的派生属性，用于加速查询';
COMMENT ON COLUMN entities.tags IS '自定义标签数组，用于分类和筛选';
COMMENT ON COLUMN entities.priority IS '重要性等级：主角>重要NPC>普通NPC，影响显示排序';
COMMENT ON COLUMN entities.version IS '数据版本号，支持变更追踪';
COMMENT ON COLUMN entities.created_at IS '创建时间';
COMMENT ON COLUMN entities.updated_at IS '最后更新时间';

-- 实体关系表注释
COMMENT ON TABLE entity_relationships IS '实体关系表：定义实体间的各种关系和依赖';
COMMENT ON COLUMN entity_relationships.id IS '关系唯一标识符';
COMMENT ON COLUMN entity_relationships.novel_id IS '所属小说项目';
COMMENT ON COLUMN entity_relationships.source_entity_id IS '关系发起方';
COMMENT ON COLUMN entity_relationships.target_entity_id IS '关系接受方';
COMMENT ON COLUMN entity_relationships.relationship_type IS '关系类型：belongs_to/controls/masters/loves/hates等';
COMMENT ON COLUMN entity_relationships.attributes IS '关系的附加属性和描述信息';
COMMENT ON COLUMN entity_relationships.strength IS '关系强度等级（1-10）';
COMMENT ON COLUMN entity_relationships.status IS '关系状态：active/inactive/ended';
COMMENT ON COLUMN entity_relationships.valid_from IS '关系开始时间';
COMMENT ON COLUMN entity_relationships.valid_to IS '关系结束时间（可选）';
COMMENT ON COLUMN entity_relationships.created_at IS '记录创建时间';

-- 分类表注释
COMMENT ON TABLE categories IS '通用分类表：管理域、境界、势力等级等层级分类';
COMMENT ON COLUMN categories.id IS '分类唯一标识符';
COMMENT ON COLUMN categories.novel_id IS '所属小说项目';
COMMENT ON COLUMN categories.type IS '分类类型：domain/realm/rank/faction_type等';
COMMENT ON COLUMN categories.name IS '分类名称';
COMMENT ON COLUMN categories.code IS '分类代码';
COMMENT ON COLUMN categories.parent_id IS '父级分类ID，支持层级结构';
COMMENT ON COLUMN categories.level IS '层级深度';
COMMENT ON COLUMN categories.sort_order IS '排序顺序';
COMMENT ON COLUMN categories.attributes IS '分类的附加属性';
COMMENT ON COLUMN categories.description IS '分类描述';
COMMENT ON COLUMN categories.is_active IS '分类是否可用';
COMMENT ON COLUMN categories.created_at IS '创建时间';

-- 实体分类关联表注释
COMMENT ON TABLE entity_categories IS '实体分类关联表：将实体分配到各种分类中';
COMMENT ON COLUMN entity_categories.id IS '关联唯一标识符';
COMMENT ON COLUMN entity_categories.novel_id IS '所属小说项目';
COMMENT ON COLUMN entity_categories.entity_id IS '关联的实体';
COMMENT ON COLUMN entity_categories.category_id IS '关联的分类';
COMMENT ON COLUMN entity_categories.attributes IS '关联属性，如在某个境界的进度';
COMMENT ON COLUMN entity_categories.valid_from IS '关联开始时间';
COMMENT ON COLUMN entity_categories.valid_to IS '关联结束时间';
COMMENT ON COLUMN entity_categories.created_at IS '记录创建时间';

-- 事件表注释
COMMENT ON TABLE events IS '事件表：记录小说中发生的各种事件和剧情节点';
COMMENT ON COLUMN events.id IS '事件唯一标识符';
COMMENT ON COLUMN events.novel_id IS '所属小说项目';
COMMENT ON COLUMN events.name IS '事件名称';
COMMENT ON COLUMN events.event_type IS '事件类型：battle/breakthrough/meeting/discovery';
COMMENT ON COLUMN events.occurred_at IS '事件发生的现实时间';
COMMENT ON COLUMN events.in_world_time IS '小说世界内的时间表示';
COMMENT ON COLUMN events.sequence_order IS '剧情顺序';
COMMENT ON COLUMN events.location_entity_id IS '事件发生地点';
COMMENT ON COLUMN events.impact_level IS '影响程度等级（1-10）';
COMMENT ON COLUMN events.scope IS '影响范围：local/regional/domain/world';
COMMENT ON COLUMN events.attributes IS '事件的附加属性';
COMMENT ON COLUMN events.description IS '事件详细描述';
COMMENT ON COLUMN events.status IS '事件状态：planned/ongoing/completed/cancelled';
COMMENT ON COLUMN events.created_at IS '记录创建时间';
COMMENT ON COLUMN events.updated_at IS '最后更新时间';

-- 事件参与者表注释
COMMENT ON TABLE event_participants IS '事件参与者表：记录参与各个事件的实体及其角色';
COMMENT ON COLUMN event_participants.id IS '参与记录唯一标识符';
COMMENT ON COLUMN event_participants.novel_id IS '所属小说项目';
COMMENT ON COLUMN event_participants.event_id IS '关联的事件';
COMMENT ON COLUMN event_participants.entity_id IS '参与的实体';
COMMENT ON COLUMN event_participants.role IS '参与角色：protagonist/antagonist/witness/victim/supporter';
COMMENT ON COLUMN event_participants.importance IS '参与重要性等级（1-10）';
COMMENT ON COLUMN event_participants.attributes IS '参与的详细信息';
COMMENT ON COLUMN event_participants.created_at IS '记录创建时间';

-- 数据版本表注释
COMMENT ON TABLE schema_versions IS '数据版本表：记录数据库架构变更历史';
COMMENT ON COLUMN schema_versions.id IS '版本记录唯一标识符';
COMMENT ON COLUMN schema_versions.novel_id IS '相关小说项目';
COMMENT ON COLUMN schema_versions.version IS '版本号';
COMMENT ON COLUMN schema_versions.changes IS '变更详情';
COMMENT ON COLUMN schema_versions.migration_script IS '迁移脚本';
COMMENT ON COLUMN schema_versions.applied_at IS '应用时间';
COMMENT ON COLUMN schema_versions.applied_by IS '应用者';

-- 审计日志表注释
COMMENT ON TABLE audit_logs IS '审计日志表：记录数据变更历史，支持数据审计和恢复';
COMMENT ON COLUMN audit_logs.id IS '日志记录唯一标识符';
COMMENT ON COLUMN audit_logs.novel_id IS '相关小说项目';
COMMENT ON COLUMN audit_logs.table_name IS '操作的表名';
COMMENT ON COLUMN audit_logs.record_id IS '操作的记录ID';
COMMENT ON COLUMN audit_logs.operation IS '操作类型：INSERT/UPDATE/DELETE';
COMMENT ON COLUMN audit_logs.old_values IS '操作前的数据值';
COMMENT ON COLUMN audit_logs.new_values IS '操作后的数据值';
COMMENT ON COLUMN audit_logs.user_id IS '操作用户ID';
COMMENT ON COLUMN audit_logs.ip_address IS '操作来源IP地址';
COMMENT ON COLUMN audit_logs.user_agent IS '用户代理信息';
COMMENT ON COLUMN audit_logs.created_at IS '记录创建时间';

-- 视图注释
COMMENT ON VIEW novel_entity_summary IS '小说实体统计视图：提供按小说和实体类型的统计信息';

-- 权限设置（根据实际需要调整）
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO novel_app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO novel_app_user;