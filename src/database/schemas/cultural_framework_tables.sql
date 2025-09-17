-- =============================================================================
-- 文化框架数据库表设计
-- 支持九域六维文化框架的结构化存储
-- =============================================================================

-- =============================================================================
-- 1. 域（Domain）管理表
-- =============================================================================

-- 域定义表
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 基础信息
    name VARCHAR(50) NOT NULL,           -- 人域、天域、灵域等
    code VARCHAR(20) NOT NULL,           -- ren_yu, tian_yu, ling_yu等
    display_name VARCHAR(100) NOT NULL,  -- 完整显示名称

    -- 域的核心特征
    dominant_law VARCHAR(100),           -- 主导法则链
    ruling_power VARCHAR(100),           -- 统治力量

    -- 域的基本属性
    power_level INTEGER DEFAULT 1 CHECK (power_level >= 1 AND power_level <= 10),
    civilization_level INTEGER DEFAULT 1 CHECK (civilization_level >= 1 AND civilization_level <= 10),
    stability_level INTEGER DEFAULT 5 CHECK (stability_level >= 1 AND stability_level <= 10),

    -- 地理和环境
    geographic_features JSONB DEFAULT '{}', -- 地理特征
    climate_info JSONB DEFAULT '{}',        -- 气候信息
    resources JSONB DEFAULT '{}',           -- 资源分布

    -- 域间关系
    allied_domains TEXT[] DEFAULT '{}',     -- 盟友域
    hostile_domains TEXT[] DEFAULT '{}',    -- 敌对域
    trade_partners TEXT[] DEFAULT '{}',     -- 贸易伙伴

    -- 元数据
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, code)
);

-- =============================================================================
-- 2. 文化维度（Cultural Dimension）定义表
-- =============================================================================

-- 文化维度表
CREATE TABLE cultural_dimensions (
    id SERIAL PRIMARY KEY,

    -- 维度基础信息
    code VARCHAR(20) NOT NULL UNIQUE,    -- myth_religion, power_law等
    name VARCHAR(50) NOT NULL,           -- 神话与宗教、权力与法律等
    display_name VARCHAR(100) NOT NULL,
    description TEXT,

    -- 维度特征
    dimension_type VARCHAR(20) DEFAULT 'cultural', -- cultural/social/economic/political
    importance_weight INTEGER DEFAULT 5 CHECK (importance_weight >= 1 AND importance_weight <= 10),

    -- 维度的标准要素类型
    standard_elements JSONB DEFAULT '{}', -- 标准要素模板

    -- 排序和状态
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 3. 文化框架（Cultural Framework）主表
-- =============================================================================

-- 文化框架表（域+维度的组合）
CREATE TABLE cultural_frameworks (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    dimension_id INTEGER NOT NULL REFERENCES cultural_dimensions(id) ON DELETE CASCADE,

    -- 框架基础信息
    framework_name VARCHAR(200), -- 如："人域神话与宗教框架"
    version VARCHAR(20) DEFAULT '1.0',

    -- 框架概要
    core_concept TEXT,              -- 核心理念
    key_features JSONB DEFAULT '{}', -- 关键特征

    -- 框架状态
    completeness_score INTEGER DEFAULT 0 CHECK (completeness_score >= 0 AND completeness_score <= 100),
    last_reviewed TIMESTAMP,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, domain_id, dimension_id)
);

-- =============================================================================
-- 4. 文化要素（Cultural Element）表
-- =============================================================================

-- 文化要素表
CREATE TABLE cultural_elements (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    framework_id INTEGER NOT NULL REFERENCES cultural_frameworks(id) ON DELETE CASCADE,

    -- 要素基础信息
    element_type VARCHAR(50) NOT NULL,   -- institution, belief, practice, rule等
    name VARCHAR(200) NOT NULL,
    code VARCHAR(100),                   -- 便于引用的代码

    -- 要素分类
    category VARCHAR(50),                -- 二级分类
    subcategory VARCHAR(50),             -- 三级分类

    -- 要素属性
    attributes JSONB DEFAULT '{}',       -- 要素的具体属性
    importance INTEGER DEFAULT 1 CHECK (importance >= 1 AND importance <= 10),
    influence_scope VARCHAR(20) DEFAULT 'local', -- local/regional/domain/cross_domain

    -- 要素状态
    status VARCHAR(20) DEFAULT 'active', -- active/historical/legendary/forbidden

    -- 关联信息
    related_entities TEXT[] DEFAULT '{}', -- 关联的实体ID
    parent_element_id INTEGER REFERENCES cultural_elements(id) ON DELETE SET NULL,

    -- 时间信息
    established_time VARCHAR(100),       -- 建立时间
    active_period VARCHAR(100),          -- 活跃期间

    -- 元数据
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 5. 剧情钩子（Plot Hook）表
-- =============================================================================

-- 剧情钩子表
CREATE TABLE plot_hooks (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 钩子关联
    domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    framework_id INTEGER REFERENCES cultural_frameworks(id) ON DELETE CASCADE,
    element_id INTEGER REFERENCES cultural_elements(id) ON DELETE CASCADE,

    -- 钩子基础信息
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    hook_type VARCHAR(50),               -- conflict, mystery, discovery, crisis等

    -- 钩子属性
    drama_level INTEGER DEFAULT 5 CHECK (drama_level >= 1 AND drama_level <= 10),
    scope VARCHAR(20) DEFAULT 'local',   -- local/regional/domain/cross_domain
    urgency_level INTEGER DEFAULT 3 CHECK (urgency_level >= 1 AND urgency_level <= 5),

    -- 参与角色
    involved_entities TEXT[] DEFAULT '{}', -- 涉及的实体ID
    required_capabilities TEXT[] DEFAULT '{}', -- 需要的能力或资源

    -- 剧情发展
    potential_outcomes JSONB DEFAULT '{}', -- 可能的结果
    follow_up_hooks TEXT[] DEFAULT '{}',   -- 后续钩子

    -- 使用状态
    status VARCHAR(20) DEFAULT 'available', -- available/in_use/resolved/archived
    used_in_events TEXT[] DEFAULT '{}',      -- 已用于的事件ID

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 6. 文化冲突（Cultural Conflict）表
-- =============================================================================

-- 文化冲突表（记录不同域或文化要素间的冲突）
CREATE TABLE cultural_conflicts (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 冲突双方
    primary_domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    secondary_domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    primary_element_id INTEGER REFERENCES cultural_elements(id) ON DELETE CASCADE,
    secondary_element_id INTEGER REFERENCES cultural_elements(id) ON DELETE CASCADE,

    -- 冲突信息
    conflict_type VARCHAR(50) NOT NULL,  -- value, practice, territory, resource等
    conflict_name VARCHAR(200) NOT NULL,
    description TEXT,

    -- 冲突特征
    intensity_level INTEGER DEFAULT 3 CHECK (intensity_level >= 1 AND intensity_level <= 10),
    historical_depth INTEGER DEFAULT 1,  -- 历史深度（代数）
    resolution_difficulty INTEGER DEFAULT 5 CHECK (resolution_difficulty >= 1 AND resolution_difficulty <= 10),

    -- 冲突状态
    status VARCHAR(20) DEFAULT 'ongoing', -- dormant/simmering/ongoing/escalating/resolved
    current_manifestation TEXT,           -- 当前表现形式

    -- 影响分析
    affected_areas JSONB DEFAULT '{}',    -- 受影响的领域
    stakeholders TEXT[] DEFAULT '{}',     -- 利益相关者

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 7. 文化变迁（Cultural Evolution）记录表
-- =============================================================================

-- 文化变迁表
CREATE TABLE cultural_evolutions (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 变迁目标
    domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    element_id INTEGER REFERENCES cultural_elements(id) ON DELETE CASCADE,

    -- 变迁信息
    evolution_type VARCHAR(50) NOT NULL, -- gradual, revolutionary, imposed, natural
    change_name VARCHAR(200) NOT NULL,
    description TEXT,

    -- 变迁前后状态
    before_state JSONB DEFAULT '{}',
    after_state JSONB DEFAULT '{}',
    change_factors JSONB DEFAULT '{}',    -- 变迁因素

    -- 时间线
    started_at VARCHAR(100),              -- 小说内时间
    completed_at VARCHAR(100),
    duration_type VARCHAR(20) DEFAULT 'medium', -- instant/short/medium/long/generational

    -- 影响评估
    impact_scope VARCHAR(20) DEFAULT 'local',
    resistance_level INTEGER DEFAULT 3 CHECK (resistance_level >= 1 AND resistance_level <= 10),
    success_level INTEGER DEFAULT 5 CHECK (success_level >= 1 AND success_level <= 10),

    -- 相关事件
    triggering_events TEXT[] DEFAULT '{}',
    related_conflicts TEXT[] DEFAULT '{}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 8. 索引优化
-- =============================================================================

-- 域表索引
CREATE INDEX idx_domains_novel ON domains(novel_id);
CREATE INDEX idx_domains_code ON domains(novel_id, code);
CREATE INDEX idx_domains_power_level ON domains(power_level DESC);

-- 文化维度索引
CREATE INDEX idx_dimensions_code ON cultural_dimensions(code);
CREATE INDEX idx_dimensions_type ON cultural_dimensions(dimension_type);

-- 文化框架索引
CREATE INDEX idx_frameworks_novel ON cultural_frameworks(novel_id);
CREATE INDEX idx_frameworks_domain ON cultural_frameworks(domain_id);
CREATE INDEX idx_frameworks_dimension ON cultural_frameworks(dimension_id);
CREATE INDEX idx_frameworks_completeness ON cultural_frameworks(completeness_score DESC);

-- 文化要素索引
CREATE INDEX idx_elements_novel ON cultural_elements(novel_id);
CREATE INDEX idx_elements_framework ON cultural_elements(framework_id);
CREATE INDEX idx_elements_type ON cultural_elements(element_type);
CREATE INDEX idx_elements_importance ON cultural_elements(importance DESC);
CREATE INDEX idx_elements_scope ON cultural_elements(influence_scope);
CREATE INDEX idx_elements_status ON cultural_elements(status);

-- JSONB字段GIN索引
CREATE INDEX idx_elements_attributes_gin ON cultural_elements USING GIN(attributes);
CREATE INDEX idx_domains_features_gin ON domains USING GIN(geographic_features);
CREATE INDEX idx_domains_resources_gin ON domains USING GIN(resources);

-- 剧情钩子索引
CREATE INDEX idx_hooks_novel ON plot_hooks(novel_id);
CREATE INDEX idx_hooks_domain ON plot_hooks(domain_id);
CREATE INDEX idx_hooks_framework ON plot_hooks(framework_id);
CREATE INDEX idx_hooks_type ON plot_hooks(hook_type);
CREATE INDEX idx_hooks_status ON plot_hooks(status);
CREATE INDEX idx_hooks_drama_level ON plot_hooks(drama_level DESC);

-- 文化冲突索引
CREATE INDEX idx_conflicts_novel ON cultural_conflicts(novel_id);
CREATE INDEX idx_conflicts_domains ON cultural_conflicts(primary_domain_id, secondary_domain_id);
CREATE INDEX idx_conflicts_type ON cultural_conflicts(conflict_type);
CREATE INDEX idx_conflicts_status ON cultural_conflicts(status);

-- 文化变迁索引
CREATE INDEX idx_evolutions_novel ON cultural_evolutions(novel_id);
CREATE INDEX idx_evolutions_domain ON cultural_evolutions(domain_id);
CREATE INDEX idx_evolutions_type ON cultural_evolutions(evolution_type);

-- =============================================================================
-- 9. 触发器
-- =============================================================================

-- 更新updated_at字段的触发器
CREATE TRIGGER update_domains_updated_at BEFORE UPDATE ON domains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_frameworks_updated_at BEFORE UPDATE ON cultural_frameworks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_elements_updated_at BEFORE UPDATE ON cultural_elements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hooks_updated_at BEFORE UPDATE ON plot_hooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conflicts_updated_at BEFORE UPDATE ON cultural_conflicts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_evolutions_updated_at BEFORE UPDATE ON cultural_evolutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 审计触发器
CREATE TRIGGER audit_domains AFTER INSERT OR UPDATE OR DELETE ON domains
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_cultural_frameworks AFTER INSERT OR UPDATE OR DELETE ON cultural_frameworks
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_cultural_elements AFTER INSERT OR UPDATE OR DELETE ON cultural_elements
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- =============================================================================
-- 10. 便于查询的视图
-- =============================================================================

-- 完整文化框架视图
CREATE VIEW cultural_framework_overview AS
SELECT
    cf.id as framework_id,
    cf.novel_id,
    d.name as domain_name,
    d.code as domain_code,
    cd.name as dimension_name,
    cd.code as dimension_code,
    cf.framework_name,
    cf.core_concept,
    cf.completeness_score,
    COUNT(ce.id) as element_count,
    cf.created_at,
    cf.updated_at
FROM cultural_frameworks cf
JOIN domains d ON cf.domain_id = d.id
JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
LEFT JOIN cultural_elements ce ON cf.id = ce.framework_id AND ce.status = 'active'
WHERE cf.novel_id IS NOT NULL
GROUP BY cf.id, d.id, cd.id
ORDER BY d.sort_order, cd.sort_order;

-- 域总览视图
CREATE VIEW domain_summary AS
SELECT
    d.id,
    d.novel_id,
    d.name,
    d.code,
    d.dominant_law,
    d.ruling_power,
    d.power_level,
    COUNT(DISTINCT cf.id) as framework_count,
    COUNT(DISTINCT ce.id) as total_elements,
    COUNT(DISTINCT ph.id) as plot_hook_count,
    d.created_at
FROM domains d
LEFT JOIN cultural_frameworks cf ON d.id = cf.domain_id
LEFT JOIN cultural_elements ce ON cf.id = ce.framework_id AND ce.status = 'active'
LEFT JOIN plot_hooks ph ON d.id = ph.domain_id AND ph.status = 'available'
WHERE d.is_active = true
GROUP BY d.id
ORDER BY d.sort_order;