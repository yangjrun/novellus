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

-- =============================================================================
-- 表和字段注释
-- =============================================================================

-- 域定义表注释
COMMENT ON TABLE domains IS '域定义表：存储小说世界观中各个域的基本信息和特征';
COMMENT ON COLUMN domains.id IS '域唯一标识符';
COMMENT ON COLUMN domains.novel_id IS '所属小说项目';
COMMENT ON COLUMN domains.name IS '域名称：人域、天域、灵域等';
COMMENT ON COLUMN domains.code IS '域代码：ren_yu, tian_yu, ling_yu等';
COMMENT ON COLUMN domains.display_name IS '完整显示名称';
COMMENT ON COLUMN domains.dominant_law IS '主导法则链';
COMMENT ON COLUMN domains.ruling_power IS '统治力量';
COMMENT ON COLUMN domains.power_level IS '力量等级（1-10）';
COMMENT ON COLUMN domains.civilization_level IS '文明等级（1-10）';
COMMENT ON COLUMN domains.stability_level IS '稳定等级（1-10）';
COMMENT ON COLUMN domains.geographic_features IS '地理特征描述';
COMMENT ON COLUMN domains.climate_info IS '气候环境信息';
COMMENT ON COLUMN domains.resources IS '资源分布情况';
COMMENT ON COLUMN domains.allied_domains IS '盟友域列表';
COMMENT ON COLUMN domains.hostile_domains IS '敌对域列表';
COMMENT ON COLUMN domains.trade_partners IS '贸易伙伴列表';
COMMENT ON COLUMN domains.sort_order IS '显示排序';
COMMENT ON COLUMN domains.is_active IS '是否启用';
COMMENT ON COLUMN domains.created_at IS '创建时间';
COMMENT ON COLUMN domains.updated_at IS '更新时间';

-- 文化维度表注释
COMMENT ON TABLE cultural_dimensions IS '文化维度定义表：定义文化分析的各个维度（全局共享）';
COMMENT ON COLUMN cultural_dimensions.id IS '维度唯一标识符';
COMMENT ON COLUMN cultural_dimensions.code IS '维度代码';
COMMENT ON COLUMN cultural_dimensions.name IS '维度名称';
COMMENT ON COLUMN cultural_dimensions.display_name IS '维度显示名称';
COMMENT ON COLUMN cultural_dimensions.description IS '维度描述';
COMMENT ON COLUMN cultural_dimensions.dimension_type IS '维度类型：cultural/social/economic/political';
COMMENT ON COLUMN cultural_dimensions.importance_weight IS '重要性权重（1-10）';
COMMENT ON COLUMN cultural_dimensions.standard_elements IS '标准要素模板';
COMMENT ON COLUMN cultural_dimensions.sort_order IS '显示排序';
COMMENT ON COLUMN cultural_dimensions.is_active IS '是否启用';
COMMENT ON COLUMN cultural_dimensions.created_at IS '创建时间';

-- 文化框架表注释
-- COMMENT ON TABLE cultural_frameworks IS '文化框架表：连接域和文化维度的映射关系';
-- COMMENT ON COLUMN cultural_frameworks.id IS '框架唯一标识符';
-- COMMENT ON COLUMN cultural_frameworks.novel_id IS '所属小说项目';
-- COMMENT ON COLUMN cultural_frameworks.domain_id IS '关联的域';
-- COMMENT ON COLUMN cultural_frameworks.dimension_id IS '关联的文化维度';
-- COMMENT ON COLUMN cultural_frameworks.framework_name IS '框架名称';
-- COMMENT ON COLUMN cultural_frameworks.value_orientation IS '价值取向';
-- COMMENT ON COLUMN cultural_frameworks.implementation_method IS '实现方式';
-- COMMENT ON COLUMN cultural_frameworks.social_structure IS '社会结构';
-- COMMENT ON COLUMN cultural_frameworks.belief_system IS '信仰体系';
-- COMMENT ON COLUMN cultural_frameworks.behavioral_norms IS '行为规范';
-- COMMENT ON COLUMN cultural_frameworks.created_at IS '创建时间';
-- COMMENT ON COLUMN cultural_frameworks.updated_at IS '更新时间';

-- 文化元素表注释
-- COMMENT ON TABLE cultural_elements IS '文化元素表：存储具体的文化实践和表现';
-- COMMENT ON COLUMN cultural_elements.id IS '元素唯一标识符';
-- COMMENT ON COLUMN cultural_elements.novel_id IS '所属小说项目';
-- COMMENT ON COLUMN cultural_elements.framework_id IS '所属文化框架';
-- COMMENT ON COLUMN cultural_elements.element_type IS '元素类型：ritual/custom/law/institution等';
-- COMMENT ON COLUMN cultural_elements.name IS '元素名称';
-- COMMENT ON COLUMN cultural_elements.description IS '详细描述';
-- COMMENT ON COLUMN cultural_elements.manifestation IS '具体表现形式';
-- COMMENT ON COLUMN cultural_elements.participants IS '参与者';
-- COMMENT ON COLUMN cultural_elements.significance_level IS '重要性等级（1-10）';
-- COMMENT ON COLUMN cultural_elements.frequency IS '出现频率';
-- COMMENT ON COLUMN cultural_elements.seasonal_timing IS '季节性时机';
-- COMMENT ON COLUMN cultural_elements.status IS '状态：active/deprecated/forbidden/evolving';
-- COMMENT ON COLUMN cultural_elements.created_at IS '创建时间';
-- COMMENT ON COLUMN cultural_elements.updated_at IS '更新时间';

-- 剧情钩子表注释
-- COMMENT ON TABLE plot_hooks IS '剧情钩子表：存储基于文化背景的剧情触发点';
-- COMMENT ON COLUMN plot_hooks.id IS '钩子唯一标识符';
-- COMMENT ON COLUMN plot_hooks.novel_id IS '所属小说项目';
-- COMMENT ON COLUMN plot_hooks.domain_id IS '关联的域';
-- COMMENT ON COLUMN plot_hooks.element_id IS '关联的文化元素';
-- COMMENT ON COLUMN plot_hooks.title IS '钩子标题';
-- COMMENT ON COLUMN plot_hooks.description IS '详细描述';
-- COMMENT ON COLUMN plot_hooks.hook_type IS '钩子类型：conflict/opportunity/mystery/challenge';
-- COMMENT ON COLUMN plot_hooks.drama_level IS '戏剧性水平（1-10）';
-- COMMENT ON COLUMN plot_hooks.scope IS '影响范围：personal/local/regional/domain/inter_domain';
-- COMMENT ON COLUMN plot_hooks.urgency_level IS '紧急程度（1-5）';
-- COMMENT ON COLUMN plot_hooks.potential_outcomes IS '可能结果列表';
-- COMMENT ON COLUMN plot_hooks.required_resources IS '所需资源';
-- COMMENT ON COLUMN plot_hooks.involved_entities IS '涉及实体';
-- COMMENT ON COLUMN plot_hooks.status IS '状态：available/active/used/expired';
-- COMMENT ON COLUMN plot_hooks.activation_reason IS '激活原因';
-- COMMENT ON COLUMN plot_hooks.activated_at IS '激活时间';
-- COMMENT ON COLUMN plot_hooks.completed_at IS '完成时间';
-- COMMENT ON COLUMN plot_hooks.resolution IS '解决方案';
-- COMMENT ON COLUMN plot_hooks.actual_outcome IS '实际结果';
-- COMMENT ON COLUMN plot_hooks.created_at IS '创建时间';
-- COMMENT ON COLUMN plot_hooks.updated_at IS '更新时间';

-- 文化冲突表注释
-- COMMENT ON TABLE cultural_conflicts IS '文化冲突表：记录不同文化元素间的冲突关系';
-- COMMENT ON COLUMN cultural_conflicts.id IS '冲突唯一标识符';
-- COMMENT ON COLUMN cultural_conflicts.novel_id IS '所属小说项目';
-- COMMENT ON COLUMN cultural_conflicts.primary_domain_id IS '主要涉及的域';
-- COMMENT ON COLUMN cultural_conflicts.secondary_domain_id IS '次要涉及的域';
-- COMMENT ON COLUMN cultural_conflicts.primary_element_id IS '主要文化元素';
-- COMMENT ON COLUMN cultural_conflicts.secondary_element_id IS '次要文化元素';
-- COMMENT ON COLUMN cultural_conflicts.conflict_type IS '冲突类型：value/practice/territory/resource等';
-- COMMENT ON COLUMN cultural_conflicts.conflict_name IS '冲突名称';
-- COMMENT ON COLUMN cultural_conflicts.description IS '冲突描述';
-- COMMENT ON COLUMN cultural_conflicts.intensity_level IS '冲突强度（1-10）';
-- COMMENT ON COLUMN cultural_conflicts.historical_depth IS '历史深度（代数）';
-- COMMENT ON COLUMN cultural_conflicts.resolution_difficulty IS '解决难度（1-10）';
-- COMMENT ON COLUMN cultural_conflicts.status IS '冲突状态：dormant/simmering/ongoing/escalating/resolved';
-- COMMENT ON COLUMN cultural_conflicts.current_manifestation IS '当前表现形式';
-- COMMENT ON COLUMN cultural_conflicts.affected_areas IS '受影响的领域';
-- COMMENT ON COLUMN cultural_conflicts.stakeholders IS '利益相关者';
-- COMMENT ON COLUMN cultural_conflicts.created_at IS '创建时间';
-- COMMENT ON COLUMN cultural_conflicts.updated_at IS '更新时间';

-- 文化变迁表注释
-- COMMENT ON TABLE cultural_evolutions IS '文化变迁记录表：追踪文化的演变过程';
-- COMMENT ON COLUMN cultural_evolutions.id IS '变迁记录唯一标识符';
-- COMMENT ON COLUMN cultural_evolutions.novel_id IS '所属小说项目';
-- COMMENT ON COLUMN cultural_evolutions.domain_id IS '相关的域';
-- COMMENT ON COLUMN cultural_evolutions.element_id IS '相关的文化元素';
-- COMMENT ON COLUMN cultural_evolutions.evolution_type IS '变迁类型：gradual/revolutionary/imposed/natural';
-- COMMENT ON COLUMN cultural_evolutions.change_name IS '变迁名称';
-- COMMENT ON COLUMN cultural_evolutions.description IS '变迁描述';
-- COMMENT ON COLUMN cultural_evolutions.before_state IS '变迁前状态';
-- COMMENT ON COLUMN cultural_evolutions.after_state IS '变迁后状态';
-- COMMENT ON COLUMN cultural_evolutions.change_factors IS '变迁因素';
-- COMMENT ON COLUMN cultural_evolutions.started_at IS '开始时间（小说内时间）';
-- COMMENT ON COLUMN cultural_evolutions.completed_at IS '完成时间（小说内时间）';
-- COMMENT ON COLUMN cultural_evolutions.created_at IS '记录创建时间';

-- 冲突状态历史表注释
-- COMMENT ON TABLE conflict_status_history IS '冲突状态历史表：记录冲突状态的变化历史';
-- COMMENT ON COLUMN conflict_status_history.id IS '历史记录唯一标识符';
-- COMMENT ON COLUMN conflict_status_history.novel_id IS '所属小说项目';
-- COMMENT ON COLUMN conflict_status_history.conflict_id IS '相关冲突';
-- COMMENT ON COLUMN conflict_status_history.old_status IS '原状态';
-- COMMENT ON COLUMN conflict_status_history.new_status IS '新状态';
-- COMMENT ON COLUMN conflict_status_history.change_reason IS '状态变化原因';
-- COMMENT ON COLUMN conflict_status_history.changed_at IS '变化时间';

-- 视图注释
-- COMMENT ON VIEW cultural_framework_summary IS '文化框架汇总视图：提供文化框架的统计信息';
-- COMMENT ON VIEW domain_summary IS '域概览视图：提供域的综合统计信息';