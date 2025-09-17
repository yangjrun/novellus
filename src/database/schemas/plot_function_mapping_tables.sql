-- =============================================================================
-- 剧情功能映射数据库表设计
-- 将地理实体与剧情功能、节点编号、事件钩子关联
-- =============================================================================

-- =============================================================================
-- 1. 剧情功能类型表 (Plot Function Types)
-- =============================================================================

-- 剧情功能类型字典表
CREATE TABLE plot_function_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,      -- F1, F2, ..., F20
    name VARCHAR(50) NOT NULL,             -- 仪式触发器、法条杠杆点等
    description TEXT NOT NULL,             -- 详细描述
    category VARCHAR(20),                  -- emotional, conflict, info, growth, world
    usage_examples TEXT,                   -- 使用示例
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入功能类型数据
INSERT INTO plot_function_types (code, name, description, category, usage_examples) VALUES
('F1', '仪式触发器', '处决/赦免/就职/誓言等重要仪式场所', 'emotional', '处决仪式、就职典礼、誓言广场'),
('F2', '法条杠杆点', '法理/条款/审批/通告等法律相关场所', 'conflict', '法院、政务大厅、公告板'),
('F3', '门槛/关卡', '跨域/越境/卡点/检票等阻碍通行场所', 'conflict', '关卡、城门、检查站'),
('F4', '资源据点', '粮、矿、钱、器、情报等重要资源集中地', 'world', '粮仓、矿山、银库、档案馆'),
('F5', '舆论扩音场', '广场/学府/博览/朝会等信息传播场所', 'info', '广场、学院、议事厅'),
('F6', '成长试炼场', '比试/考试/小副本等角色成长场所', 'growth', '竞技场、考场、训练场'),
('F7', '盟友集散地', '招募/结义/公会/书院等联盟建立场所', 'growth', '酒馆、公会、书院'),
('F8', '背叛/伏笔场', '黑箱/内鬼/双面等阴谋策划场所', 'conflict', '密室、后巷、私人会所'),
('F9', '追逐/奇袭场', '巷战/码头/城门/驿路等动作场景场所', 'conflict', '街巷、码头、山道'),
('F10', '谜底/档案库', '档册/账本/证据/机密等信息揭示场所', 'info', '图书馆、档案室、密库'),
('F11', '决战舞台', '终局/层层推进的大战层等最终对决场所', 'conflict', '王座大厅、城墙、决斗场'),
('F12', '避难/整备地', '补给/修整/庇护等安全休整场所', 'world', '避难所、客栈、医馆'),
('F13', '环境杀/灾变触发', '洪/风/链崩/疫等环境危险场所', 'conflict', '河堤、悬崖、毒沼'),
('F14', '赦免/翻案场', '翻盘/平反/特赦等转机逆转场所', 'emotional', '法庭、祭台、宫殿'),
('F15', '黑市/灰地', '走私/地下交易/灰产等非法交易场所', 'world', '地下市场、废弃仓库'),
('F16', '训练/精修场', '隐修/闭关/试验等技能提升场所', 'growth', '道场、实验室、静修室'),
('F17', '劫案/渗透目标', '库/塔/殿/试场等潜入目标场所', 'conflict', '宝库、高塔、宫殿'),
('F18', '情感落点/归乡', '家门/祖地/祭台等情感共鸣场所', 'emotional', '故乡、墓地、纪念碑'),
('F19', '交易/金融枢', '票据/招标/承兑等经济活动场所', 'world', '银行、交易所、商会'),
('F20', '跨域节点', '关隘/帝路/港/传讯网等跨区域连接点', 'world', '大桥、驿站、港口');

-- =============================================================================
-- 2. 剧情节点类型表 (Plot Node Types)
-- =============================================================================

-- 剧情节点编号表
CREATE TABLE plot_node_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,      -- ①, ②, ..., ⑦
    name VARCHAR(20) NOT NULL,             -- 起源、门槛等
    description TEXT NOT NULL,             -- 详细描述
    sequence_order INTEGER NOT NULL,       -- 1-7的顺序
    narrative_purpose TEXT,                -- 叙事目的
    typical_events TEXT,                   -- 典型事件
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入节点类型数据
INSERT INTO plot_node_types (code, name, description, sequence_order, narrative_purpose, typical_events) VALUES
('①', '起源', '故事开始，角色背景建立，世界观展现', 1, '建立角色动机，展现初始状态', '出生地访问，童年回忆，家族传承'),
('②', '门槛', '离开舒适圈，进入冒险世界，面临第一次挑战', 2, '推动角色踏出第一步', '离开家乡，通过关卡，接受任务'),
('③', '试炼', '各种挑战与考验，技能成长，世界探索', 3, '角色成长与世界建构', '技能学习，战斗训练，解谜探索'),
('④', '深渊', '最大危机，失败边缘，考验角色意志', 4, '制造最大冲突与绝望', '重大失败，盟友背叛，敌人得逞'),
('⑤', '重生', '获得新力量，转机出现，内心蜕变', 5, '角色突破与转折', '顿悟觉醒，获得神器，盟友支援'),
('⑥', '最终试炼', '运用所学面对最终敌人，证明成长', 6, '展现成长成果', '最终决战，拯救世界，证明自己'),
('⑦', '缔造', '新秩序建立，角色完成蜕变，故事圆满', 7, '完成角色弧光，建立新秩序', '加冕称王，建立组织，改变世界');

-- =============================================================================
-- 3. 地理实体剧情映射表 (Geographic Plot Mapping)
-- =============================================================================

-- 地理实体剧情功能映射表
CREATE TABLE geographic_plot_mappings (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,

    -- 功能映射
    function_codes TEXT[] NOT NULL DEFAULT '{}',  -- 如: ['F1', 'F5', 'F14']
    node_codes TEXT[] NOT NULL DEFAULT '{}',      -- 如: ['①', '④', '⑤']

    -- 剧情钩子
    hook_title VARCHAR(200),                      -- 钩子标题
    hook_description TEXT,                        -- 钩子详细描述
    hook_urgency INTEGER DEFAULT 3,              -- 紧急程度 1-5
    hook_drama_level INTEGER DEFAULT 5,          -- 戏剧性水平 1-10

    -- 适用条件
    required_conditions JSONB DEFAULT '{}',      -- 触发条件
    narrative_triggers JSONB DEFAULT '{}',       -- 叙事触发器

    -- 扩展属性
    conflict_types TEXT[] DEFAULT '{}',          -- 冲突类型
    emotional_tags TEXT[] DEFAULT '{}',          -- 情感标签
    difficulty_level INTEGER DEFAULT 3,          -- 难度等级 1-5

    -- 使用状态
    usage_count INTEGER DEFAULT 0,               -- 使用次数
    last_used_at TIMESTAMP,                      -- 最后使用时间
    is_active BOOLEAN DEFAULT true,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    UNIQUE(novel_id, entity_id)
);

-- =============================================================================
-- 4. 剧情钩子详情表 (Plot Hook Details)
-- =============================================================================

-- 剧情钩子扩展详情表
CREATE TABLE plot_hook_details (
    id SERIAL PRIMARY KEY,
    mapping_id INTEGER NOT NULL REFERENCES geographic_plot_mappings(id) ON DELETE CASCADE,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 详细设定
    background_context TEXT,                     -- 背景上下文
    character_motivations JSONB DEFAULT '{}',   -- 角色动机
    environmental_factors JSONB DEFAULT '{}',   -- 环境因素

    -- 发展路径
    escalation_paths JSONB DEFAULT '{}',        -- 升级路径
    resolution_options JSONB DEFAULT '{}',      -- 解决选项
    consequences JSONB DEFAULT '{}',            -- 后果影响

    -- 关联要素
    related_entities TEXT[] DEFAULT '{}',       -- 相关实体ID
    required_items TEXT[] DEFAULT '{}',         -- 需要物品
    required_skills TEXT[] DEFAULT '{}',        -- 需要技能

    -- 时机控制
    timing_constraints JSONB DEFAULT '{}',      -- 时机限制
    cooldown_period INTEGER DEFAULT 0,          -- 冷却期（天）
    seasonal_availability TEXT,                 -- 季节性可用

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 5. 剧情功能使用记录表 (Plot Function Usage)
-- =============================================================================

-- 剧情功能使用记录表
CREATE TABLE plot_function_usage (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    mapping_id INTEGER NOT NULL REFERENCES geographic_plot_mappings(id) ON DELETE CASCADE,

    -- 使用信息
    used_in_chapter VARCHAR(50),                -- 使用章节
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 使用时间
    function_codes_used TEXT[] NOT NULL,        -- 使用的功能码
    node_codes_used TEXT[] NOT NULL,            -- 使用的节点码

    -- 使用效果
    player_choices JSONB DEFAULT '{}',          -- 玩家选择
    outcome_achieved VARCHAR(100),              -- 达成结果
    impact_level INTEGER DEFAULT 3,            -- 影响等级 1-5

    -- 反馈数据
    effectiveness_score INTEGER,               -- 效果评分 1-10
    player_engagement INTEGER,                 -- 玩家参与度 1-10
    narrative_satisfaction INTEGER,            -- 叙事满意度 1-10

    -- 后续影响
    follow_up_hooks TEXT[] DEFAULT '{}',       -- 后续钩子
    unlocked_content TEXT[] DEFAULT '{}',      -- 解锁内容

    -- 元数据
    session_id VARCHAR(100),                   -- 游戏会话ID
    notes TEXT,                                -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 6. 索引优化
-- =============================================================================

-- 剧情功能类型索引
CREATE INDEX idx_plot_function_types_code ON plot_function_types(code);
CREATE INDEX idx_plot_function_types_category ON plot_function_types(category);

-- 剧情节点类型索引
CREATE INDEX idx_plot_node_types_code ON plot_node_types(code);
CREATE INDEX idx_plot_node_types_sequence ON plot_node_types(sequence_order);

-- 地理剧情映射索引
CREATE INDEX idx_geographic_plot_mappings_novel ON geographic_plot_mappings(novel_id);
CREATE INDEX idx_geographic_plot_mappings_entity ON geographic_plot_mappings(entity_id);
CREATE INDEX idx_geographic_plot_mappings_functions ON geographic_plot_mappings USING GIN(function_codes);
CREATE INDEX idx_geographic_plot_mappings_nodes ON geographic_plot_mappings USING GIN(node_codes);
CREATE INDEX idx_geographic_plot_mappings_active ON geographic_plot_mappings(novel_id, is_active);
CREATE INDEX idx_geographic_plot_mappings_difficulty ON geographic_plot_mappings(difficulty_level);
CREATE INDEX idx_geographic_plot_mappings_drama ON geographic_plot_mappings(hook_drama_level DESC);

-- 剧情钩子详情索引
CREATE INDEX idx_plot_hook_details_mapping ON plot_hook_details(mapping_id);
CREATE INDEX idx_plot_hook_details_novel ON plot_hook_details(novel_id);

-- 功能使用记录索引
CREATE INDEX idx_plot_function_usage_novel ON plot_function_usage(novel_id);
CREATE INDEX idx_plot_function_usage_mapping ON plot_function_usage(mapping_id);
CREATE INDEX idx_plot_function_usage_time ON plot_function_usage(used_at DESC);
CREATE INDEX idx_plot_function_usage_chapter ON plot_function_usage(novel_id, used_in_chapter);

-- =============================================================================
-- 7. 触发器和函数
-- =============================================================================

-- 更新updated_at字段的触发器
CREATE TRIGGER update_geographic_plot_mappings_updated_at
    BEFORE UPDATE ON geographic_plot_mappings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plot_hook_details_updated_at
    BEFORE UPDATE ON plot_hook_details
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 使用计数更新函数
CREATE OR REPLACE FUNCTION update_plot_mapping_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE geographic_plot_mappings
    SET
        usage_count = usage_count + 1,
        last_used_at = NEW.used_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.mapping_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 使用记录触发器
CREATE TRIGGER update_plot_mapping_usage_trigger
    AFTER INSERT ON plot_function_usage
    FOR EACH ROW EXECUTE FUNCTION update_plot_mapping_usage();

-- =============================================================================
-- 8. 便于查询的视图
-- =============================================================================

-- 地理实体剧情功能完整视图
CREATE VIEW geographic_plot_complete_view AS
SELECT
    e.id as entity_id,
    e.novel_id,
    e.name as entity_name,
    et.name as entity_type,
    e.attributes->>'domain_code' as domain_code,
    e.attributes->>'region_name' as region_name,

    -- 剧情映射信息
    gpm.function_codes,
    gpm.node_codes,
    gpm.hook_title,
    gpm.hook_description,
    gpm.hook_urgency,
    gpm.hook_drama_level,
    gpm.difficulty_level,
    gpm.usage_count,
    gpm.last_used_at,

    -- 功能类型名称
    array(
        SELECT pft.name
        FROM plot_function_types pft
        WHERE pft.code = ANY(gpm.function_codes)
    ) as function_names,

    -- 节点类型名称
    array(
        SELECT pnt.name
        FROM plot_node_types pnt
        WHERE pnt.code = ANY(gpm.node_codes)
    ) as node_names,

    e.priority,
    e.created_at
FROM entities e
JOIN entity_types et ON e.entity_type_id = et.id
LEFT JOIN geographic_plot_mappings gpm ON e.id = gpm.entity_id AND gpm.is_active = true
WHERE e.status = 'active'
  AND et.name IN ('region', 'city', 'town', 'village', 'landmark', 'building', 'natural_feature', 'infrastructure');

-- 剧情功能统计视图
CREATE VIEW plot_function_stats_view AS
SELECT
    novel_id,
    function_code,
    pft.name as function_name,
    pft.category,
    COUNT(DISTINCT gpm.entity_id) as entity_count,
    AVG(gpm.hook_drama_level) as avg_drama_level,
    AVG(gpm.difficulty_level) as avg_difficulty_level,
    SUM(gpm.usage_count) as total_usage_count,
    MAX(gpm.last_used_at) as last_used_at
FROM geographic_plot_mappings gpm
CROSS JOIN UNNEST(gpm.function_codes) as function_code
JOIN plot_function_types pft ON pft.code = function_code
WHERE gpm.is_active = true
GROUP BY novel_id, function_code, pft.name, pft.category;

-- =============================================================================
-- 9. 示例查询
-- =============================================================================

/*
-- 查询特定功能类型的所有地点
SELECT * FROM geographic_plot_complete_view
WHERE novel_id = 1 AND 'F1' = ANY(function_codes)
ORDER BY hook_drama_level DESC;

-- 查询特定节点的剧情地点
SELECT * FROM geographic_plot_complete_view
WHERE novel_id = 1 AND '③' = ANY(node_codes)
ORDER BY difficulty_level;

-- 查询某个域的剧情功能分布
SELECT
    domain_code,
    function_codes,
    COUNT(*) as location_count
FROM geographic_plot_complete_view
WHERE novel_id = 1 AND domain_code = 'ren_yu'
GROUP BY domain_code, function_codes;

-- 查询高戏剧性且未使用的剧情钩子
SELECT * FROM geographic_plot_complete_view
WHERE novel_id = 1
  AND hook_drama_level >= 8
  AND (usage_count = 0 OR usage_count IS NULL)
ORDER BY hook_drama_level DESC;
*/

-- =============================================================================
-- 10. 数据权限设置
-- =============================================================================

-- 为相关表添加审计触发器
CREATE TRIGGER audit_geographic_plot_mappings
    AFTER INSERT OR UPDATE OR DELETE ON geographic_plot_mappings
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_plot_function_usage
    AFTER INSERT OR UPDATE OR DELETE ON plot_function_usage
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- =============================================================================
-- 脚本总结
-- =============================================================================

/*
剧情功能映射数据库设计完成总结：

✅ 已创建表结构：
1. plot_function_types - 20种功能类型字典 (F1-F20)
2. plot_node_types - 7种节点类型 (①-⑦)
3. geographic_plot_mappings - 地理实体剧情映射主表
4. plot_hook_details - 剧情钩子详情扩展表
5. plot_function_usage - 使用记录追踪表

🔧 核心功能：
- 完整的功能类型和节点类型标准化
- 地理实体与剧情功能的多对多映射
- 即写即用的事件钩子存储
- 使用情况追踪和效果评估
- 丰富的查询视图和统计分析

📊 支持查询：
- 按功能类型查找适合的地点
- 按节点编号规划剧情发展
- 按戏剧性和难度筛选钩子
- 按域和区域分析功能分布
- 追踪剧情功能使用效果

🎯 与现有系统集成：
- 完全兼容现有地理实体系统
- 支持审计日志和版本控制
- 提供标准化的API接口
- 可扩展的属性存储设计

使用方式：
1. 导入基础功能和节点类型数据
2. 为地理实体创建剧情映射
3. 在创作时查询合适的场景
4. 记录使用情况和效果反馈
*/