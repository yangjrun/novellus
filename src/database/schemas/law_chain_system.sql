-- =============================================================================
-- 法则链系统数据库架构
-- 完整的12条法则链管理系统
-- =============================================================================

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "cube";  -- 用于多维度计算
CREATE EXTENSION IF NOT EXISTS "earthdistance";  -- 用于距离计算

-- =============================================================================
-- 核心法则链定义表
-- =============================================================================

-- 法则链基础定义表（12条核心法则链）
CREATE TABLE IF NOT EXISTS law_chain_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    chain_code VARCHAR(20) NOT NULL,  -- 命运FATE, 因果CAUSE, 时空SPACE等
    chain_name VARCHAR(50) NOT NULL,   -- 命运链、因果链等
    chain_category VARCHAR(20) NOT NULL CHECK (chain_category IN ('命运', '因果', '时空', '生死', '混沌', '权柄', '名真', '记忆', '界域', '形质', '映象', '共鸣')),
    description TEXT NOT NULL,
    origin_story TEXT,
    max_level INTEGER DEFAULT 6 CHECK (max_level BETWEEN 0 AND 6),  -- L0-L6
    base_rarity INTEGER DEFAULT 0 CHECK (base_rarity BETWEEN 0 AND 5),  -- R0-R5

    -- 四域偏好（人域、天域、灵域、荒域）
    domain_affinity JSONB DEFAULT '{
        "人域": 0,
        "天域": 0,
        "灵域": 0,
        "荒域": 0
    }',

    -- 基础属性
    base_attributes JSONB DEFAULT '{}',

    -- 法则链特性
    special_traits JSONB DEFAULT '[]',

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, chain_code)
);

-- 法则链学习等级定义表
CREATE TABLE IF NOT EXISTS law_chain_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chain_id UUID NOT NULL REFERENCES law_chain_definitions(id) ON DELETE CASCADE,
    level_code VARCHAR(10) NOT NULL,  -- L0, L1, L2等
    level_number INTEGER NOT NULL CHECK (level_number BETWEEN 0 AND 6),
    level_name VARCHAR(100) NOT NULL,  -- 感知、安全操作、接口熟练等
    description TEXT NOT NULL,

    -- 等级要求
    requirements JSONB DEFAULT '{
        "min_cultivation_stage": null,
        "min_comprehension": 0,
        "min_practice_hours": 0,
        "prerequisite_chains": [],
        "required_resources": []
    }',

    -- 等级能力
    abilities JSONB DEFAULT '[]',

    -- 等级限制
    limitations JSONB DEFAULT '[]',

    -- 解锁的组合
    unlocked_combinations JSONB DEFAULT '[]',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(chain_id, level_number)
);

-- 法则链稀有度定义表
CREATE TABLE IF NOT EXISTS law_chain_rarities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    rarity_code VARCHAR(10) NOT NULL,  -- R0, R1, R2等
    rarity_level INTEGER NOT NULL CHECK (rarity_level BETWEEN 0 AND 5),
    rarity_name VARCHAR(50) NOT NULL,  -- 普适、常见、进阶、稀有、至稀、禁忌
    description TEXT NOT NULL,

    -- 稀有度属性
    attributes JSONB DEFAULT '{
        "drop_rate": 0.0,
        "power_multiplier": 1.0,
        "cost_multiplier": 1.0,
        "risk_multiplier": 1.0
    }',

    -- 获取条件
    acquisition_conditions JSONB DEFAULT '[]',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, rarity_level)
);

-- =============================================================================
-- 获取渠道系统
-- =============================================================================

-- 法则链获取渠道表（九大渠道）
CREATE TABLE IF NOT EXISTS law_chain_acquisition_channels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    channel_type VARCHAR(50) NOT NULL CHECK (channel_type IN ('命格', '师承', '契约', '器物', '权柄', '结界', '窗口', '坩埚', '共鸣')),
    channel_name VARCHAR(100) NOT NULL,
    description TEXT,

    -- 渠道特性
    channel_traits JSONB DEFAULT '{
        "difficulty": "medium",
        "stability": "stable",
        "risk_level": "low",
        "resource_cost": "moderate"
    }',

    -- 可获取的法则链
    available_chains JSONB DEFAULT '[]',  -- 链接到law_chain_definitions

    -- 渠道限制
    restrictions JSONB DEFAULT '{}',

    -- 成功率计算
    success_rate_formula TEXT,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, channel_type)
);

-- =============================================================================
-- 法则链掌握者系统
-- =============================================================================

-- 法则链掌握者表（角色的法则链状态）
CREATE TABLE IF NOT EXISTS law_chain_masters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL,  -- 关联到角色系统
    chain_id UUID NOT NULL REFERENCES law_chain_definitions(id),

    -- 学习进度
    current_level INTEGER DEFAULT 0 CHECK (current_level BETWEEN 0 AND 6),
    current_rarity INTEGER DEFAULT 0 CHECK (current_rarity BETWEEN 0 AND 5),
    mastery_progress DECIMAL(5,2) DEFAULT 0 CHECK (mastery_progress BETWEEN 0 AND 100),

    -- 获取信息
    acquisition_channel VARCHAR(50),
    acquisition_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acquisition_details JSONB DEFAULT '{}',

    -- 使用统计
    total_uses INTEGER DEFAULT 0,
    successful_uses INTEGER DEFAULT 0,
    failed_uses INTEGER DEFAULT 0,

    -- 链疲劳度
    chain_fatigue DECIMAL(5,2) DEFAULT 0 CHECK (chain_fatigue BETWEEN 0 AND 100),
    last_recovery_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 污染度
    pollution_level DECIMAL(5,2) DEFAULT 0 CHECK (pollution_level BETWEEN 0 AND 100),

    -- 特殊状态
    special_states JSONB DEFAULT '[]',  -- 如觉醒、暴走、封印等

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(character_id, chain_id)
);

-- =============================================================================
-- 法则链组合系统
-- =============================================================================

-- 法则链组合定义表
CREATE TABLE IF NOT EXISTS law_chain_combinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    combination_name VARCHAR(255) NOT NULL,
    combination_type VARCHAR(50) NOT NULL CHECK (combination_type IN ('同相相长', '战术联动', '硬克制')),
    description TEXT,

    -- 组合成分（需要哪些法则链）
    required_chains JSONB NOT NULL DEFAULT '[]',  -- [{chain_id, min_level, min_rarity}]

    -- 组合效果
    effects JSONB DEFAULT '{
        "power_boost": 0,
        "range_extension": 0,
        "duration_bonus": 0,
        "special_effects": []
    }',

    -- 组合条件
    activation_conditions JSONB DEFAULT '{}',

    -- 组合代价
    combination_cost JSONB DEFAULT '{
        "chain_fatigue": 0,
        "pollution_risk": 0,
        "resource_consumption": {}
    }',

    -- 稳定性
    stability_rating INTEGER DEFAULT 50 CHECK (stability_rating BETWEEN 0 AND 100),

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, combination_name)
);

-- 角色的法则链组合记录
CREATE TABLE IF NOT EXISTS character_chain_combinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL,
    combination_id UUID NOT NULL REFERENCES law_chain_combinations(id),

    -- 组合熟练度
    proficiency_level INTEGER DEFAULT 0 CHECK (proficiency_level BETWEEN 0 AND 100),

    -- 使用统计
    total_uses INTEGER DEFAULT 0,
    successful_uses INTEGER DEFAULT 0,
    critical_successes INTEGER DEFAULT 0,
    failures INTEGER DEFAULT 0,

    -- 组合状态
    is_active BOOLEAN DEFAULT FALSE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    cooldown_until TIMESTAMP WITH TIME ZONE,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(character_id, combination_id)
);

-- =============================================================================
-- 代价系统
-- =============================================================================

-- 法则链代价记录表
CREATE TABLE IF NOT EXISTS law_chain_costs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL,
    chain_id UUID REFERENCES law_chain_definitions(id),
    combination_id UUID REFERENCES law_chain_combinations(id),

    -- 代价类型
    cost_type VARCHAR(50) NOT NULL CHECK (cost_type IN ('因果债', '寿债', '污染', '链疲劳', '正当性风险')),
    cost_code VARCHAR(10) NOT NULL,  -- C, L, P, F, N

    -- 代价数值
    cost_value DECIMAL(10,2) NOT NULL,
    accumulated_value DECIMAL(10,2) DEFAULT 0,

    -- 代价状态
    is_paid BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(100),
    payment_date TIMESTAMP WITH TIME ZONE,

    -- 代价来源
    source_action TEXT,
    source_location VARCHAR(255),
    source_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 代价影响
    effects JSONB DEFAULT '{}',

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 因果债务追踪表
CREATE TABLE IF NOT EXISTS causal_debts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL,
    debt_type VARCHAR(50) NOT NULL,

    -- 债务信息
    original_amount DECIMAL(10,2) NOT NULL,
    current_amount DECIMAL(10,2) NOT NULL,
    interest_rate DECIMAL(5,2) DEFAULT 0,

    -- 债权方
    creditor_type VARCHAR(50),  -- 天道、法则、个体等
    creditor_id UUID,

    -- 债务状态
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'partial', 'paid', 'defaulted', 'transferred')),
    due_date TIMESTAMP WITH TIME ZONE,

    -- 债务来源
    source_event TEXT,
    source_chains JSONB DEFAULT '[]',

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 场强系统
-- =============================================================================

-- 场强定义表
CREATE TABLE IF NOT EXISTS field_strength_zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    zone_name VARCHAR(255) NOT NULL,
    zone_type VARCHAR(50) NOT NULL,

    -- 位置信息
    location_data JSONB NOT NULL DEFAULT '{
        "coordinates": null,
        "radius": 0,
        "shape": "sphere"
    }',

    -- 场强值（0-5）
    base_field_strength DECIMAL(3,2) DEFAULT 0 CHECK (base_field_strength BETWEEN 0 AND 5),
    current_field_strength DECIMAL(3,2) DEFAULT 0 CHECK (current_field_strength BETWEEN 0 AND 5),

    -- 时段调整
    time_modifiers JSONB DEFAULT '{
        "dawn": 0,
        "morning": 0,
        "noon": 0,
        "afternoon": 0,
        "dusk": 0,
        "night": 0,
        "midnight": 0
    }',

    -- 人群共振
    resonance_factors JSONB DEFAULT '{
        "min_people": 0,
        "resonance_multiplier": 1.0,
        "special_conditions": []
    }',

    -- 影响的法则链
    affected_chains JSONB DEFAULT '[]',

    -- 特殊事件
    special_events JSONB DEFAULT '[]',

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(novel_id, zone_name)
);

-- 实时场强计算表
CREATE TABLE IF NOT EXISTS field_strength_calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_id UUID NOT NULL REFERENCES field_strength_zones(id),
    calculation_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 计算参数
    location_factor DECIMAL(3,2),
    time_factor DECIMAL(3,2),
    people_count INTEGER,
    resonance_factor DECIMAL(3,2),

    -- 计算结果
    calculated_strength DECIMAL(3,2) CHECK (calculated_strength BETWEEN 0 AND 5),

    -- 活跃的法则链
    active_chains JSONB DEFAULT '[]',

    -- 特殊修正
    special_modifiers JSONB DEFAULT '{}',

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 法则链使用记录
-- =============================================================================

-- 法则链使用日志表
CREATE TABLE IF NOT EXISTS law_chain_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL,
    chain_id UUID REFERENCES law_chain_definitions(id),
    combination_id UUID REFERENCES law_chain_combinations(id),

    -- 使用信息
    action_type VARCHAR(100) NOT NULL,
    action_description TEXT,

    -- 使用参数
    input_parameters JSONB DEFAULT '{}',

    -- 场强影响
    field_strength DECIMAL(3,2),
    zone_id UUID REFERENCES field_strength_zones(id),

    -- 使用结果
    success BOOLEAN DEFAULT TRUE,
    output_results JSONB DEFAULT '{}',

    -- 代价记录
    costs_incurred JSONB DEFAULT '{
        "因果债": 0,
        "寿债": 0,
        "污染": 0,
        "链疲劳": 0,
        "正当性风险": 0
    }',

    -- 副作用
    side_effects JSONB DEFAULT '[]',

    -- 时间戳
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 分析视图
-- =============================================================================

-- 角色法则链概览视图
CREATE OR REPLACE VIEW character_chain_overview AS
SELECT
    cm.character_id,
    cm.chain_id,
    lcd.chain_name,
    lcd.chain_category,
    cm.current_level,
    cm.current_rarity,
    cm.mastery_progress,
    cm.chain_fatigue,
    cm.pollution_level,
    cm.total_uses,
    cm.successful_uses,
    CASE
        WHEN cm.successful_uses > 0
        THEN ROUND((cm.successful_uses::DECIMAL / cm.total_uses) * 100, 2)
        ELSE 0
    END as success_rate
FROM law_chain_masters cm
JOIN law_chain_definitions lcd ON cm.chain_id = lcd.id;

-- 法则链组合效率视图
CREATE OR REPLACE VIEW combination_efficiency AS
SELECT
    ccc.character_id,
    ccc.combination_id,
    lcc.combination_name,
    lcc.combination_type,
    ccc.proficiency_level,
    ccc.total_uses,
    ccc.successful_uses,
    CASE
        WHEN ccc.total_uses > 0
        THEN ROUND((ccc.successful_uses::DECIMAL / ccc.total_uses) * 100, 2)
        ELSE 0
    END as success_rate,
    ccc.last_used_at
FROM character_chain_combinations ccc
JOIN law_chain_combinations lcc ON ccc.combination_id = lcc.id;

-- =============================================================================
-- 索引创建
-- =============================================================================

-- 基础索引
CREATE INDEX IF NOT EXISTS idx_law_chain_definitions_novel_id ON law_chain_definitions(novel_id);
CREATE INDEX IF NOT EXISTS idx_law_chain_definitions_category ON law_chain_definitions(chain_category);
CREATE INDEX IF NOT EXISTS idx_law_chain_levels_chain_id ON law_chain_levels(chain_id);
CREATE INDEX IF NOT EXISTS idx_law_chain_masters_character_id ON law_chain_masters(character_id);
CREATE INDEX IF NOT EXISTS idx_law_chain_masters_chain_id ON law_chain_masters(chain_id);

-- 组合索引
CREATE INDEX IF NOT EXISTS idx_character_combinations ON character_chain_combinations(character_id, combination_id);
CREATE INDEX IF NOT EXISTS idx_combination_proficiency ON character_chain_combinations(proficiency_level);

-- 代价索引
CREATE INDEX IF NOT EXISTS idx_chain_costs_character ON law_chain_costs(character_id);
CREATE INDEX IF NOT EXISTS idx_chain_costs_type ON law_chain_costs(cost_type);
CREATE INDEX IF NOT EXISTS idx_causal_debts_character ON causal_debts(character_id);
CREATE INDEX IF NOT EXISTS idx_causal_debts_status ON causal_debts(status);

-- 场强索引
CREATE INDEX IF NOT EXISTS idx_field_zones_novel ON field_strength_zones(novel_id);
CREATE INDEX IF NOT EXISTS idx_field_calculations_zone ON field_strength_calculations(zone_id);
CREATE INDEX IF NOT EXISTS idx_field_calculations_time ON field_strength_calculations(calculation_time);

-- 使用日志索引
CREATE INDEX IF NOT EXISTS idx_usage_logs_character ON law_chain_usage_logs(character_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_chain ON law_chain_usage_logs(chain_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_time ON law_chain_usage_logs(started_at);

-- JSONB索引
CREATE INDEX IF NOT EXISTS idx_chain_definitions_attributes ON law_chain_definitions USING gin(base_attributes);
CREATE INDEX IF NOT EXISTS idx_chain_masters_states ON law_chain_masters USING gin(special_states);
CREATE INDEX IF NOT EXISTS idx_combinations_effects ON law_chain_combinations USING gin(effects);

-- =============================================================================
-- 触发器函数
-- =============================================================================

-- 自动更新链疲劳度恢复
CREATE OR REPLACE FUNCTION update_chain_fatigue_recovery()
RETURNS TRIGGER AS $$
DECLARE
    time_diff INTERVAL;
    recovery_rate DECIMAL;
BEGIN
    -- 计算时间差
    time_diff := CURRENT_TIMESTAMP - OLD.last_recovery_time;

    -- 计算恢复率（每小时恢复10%）
    recovery_rate := EXTRACT(EPOCH FROM time_diff) / 3600.0 * 10.0;

    -- 更新疲劳度
    NEW.chain_fatigue := GREATEST(0, OLD.chain_fatigue - recovery_rate);
    NEW.last_recovery_time := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_chain_fatigue_recovery
BEFORE UPDATE ON law_chain_masters
FOR EACH ROW
WHEN (NEW.chain_fatigue IS NOT NULL)
EXECUTE FUNCTION update_chain_fatigue_recovery();

-- 自动计算场强
CREATE OR REPLACE FUNCTION calculate_field_strength()
RETURNS TRIGGER AS $$
DECLARE
    time_mod DECIMAL;
    people_mod DECIMAL;
    final_strength DECIMAL;
BEGIN
    -- 获取时段修正
    time_mod := COALESCE(
        (NEW.time_modifiers->>to_char(NEW.calculation_time, 'HH24'))::DECIMAL,
        0
    );

    -- 计算人群共振
    IF NEW.people_count >= (NEW.resonance_factors->>'min_people')::INTEGER THEN
        people_mod := (NEW.resonance_factors->>'resonance_multiplier')::DECIMAL;
    ELSE
        people_mod := 1.0;
    END IF;

    -- 计算最终场强
    final_strength := NEW.location_factor + time_mod;
    final_strength := final_strength * people_mod;
    final_strength := LEAST(5, GREATEST(0, final_strength));

    NEW.calculated_strength := final_strength;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_calculate_field_strength
BEFORE INSERT OR UPDATE ON field_strength_calculations
FOR EACH ROW
EXECUTE FUNCTION calculate_field_strength();

-- 更新时间戳触发器
CREATE TRIGGER update_law_chain_definitions_updated_at BEFORE UPDATE ON law_chain_definitions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_law_chain_masters_updated_at BEFORE UPDATE ON law_chain_masters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_law_chain_combinations_updated_at BEFORE UPDATE ON law_chain_combinations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_field_strength_zones_updated_at BEFORE UPDATE ON field_strength_zones FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();