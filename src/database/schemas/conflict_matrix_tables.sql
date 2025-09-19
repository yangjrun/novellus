-- 跨域冲突矩阵专用数据库表结构
-- PostgreSQL Schema for Cross-Domain Conflict Matrix System
-- 为"裂世九域·法则链纪元"小说设计的跨域冲突分析系统

-- =============================================
-- 核心冲突矩阵表
-- =============================================

-- 1. 跨域冲突矩阵主表
CREATE TABLE IF NOT EXISTS cross_domain_conflict_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,

    -- 冲突基本信息
    matrix_name VARCHAR(255) NOT NULL,
    matrix_version VARCHAR(20) DEFAULT '1.0',
    description TEXT,

    -- 冲突域信息
    domain_a VARCHAR(50) NOT NULL CHECK (domain_a IN ('人域', '天域', '灵域', '荒域', '冥域', '魔域', '虚域', '海域', '源域')),
    domain_b VARCHAR(50) NOT NULL CHECK (domain_b IN ('人域', '天域', '灵域', '荒域', '冥域', '魔域', '虚域', '海域', '源域')),

    -- 冲突强度和特征
    intensity DECIMAL(3,1) NOT NULL CHECK (intensity >= 0 AND intensity <= 5),
    conflict_type VARCHAR(100) DEFAULT '综合冲突',
    risk_level INTEGER DEFAULT 5 CHECK (risk_level >= 1 AND risk_level <= 10),

    -- 核心争议元素
    core_resources TEXT[] NOT NULL DEFAULT '{}',
    trigger_laws TEXT[] NOT NULL DEFAULT '{}',
    typical_scenarios TEXT[] NOT NULL DEFAULT '{}',
    key_roles TEXT[] NOT NULL DEFAULT '{}',

    -- 影响评估
    economic_impact INTEGER DEFAULT 5 CHECK (economic_impact >= 1 AND economic_impact <= 10),
    political_impact INTEGER DEFAULT 5 CHECK (political_impact >= 1 AND political_impact <= 10),
    social_impact INTEGER DEFAULT 5 CHECK (social_impact >= 1 AND social_impact <= 10),
    cultural_impact INTEGER DEFAULT 5 CHECK (cultural_impact >= 1 AND cultural_impact <= 10),

    -- 状态和元数据
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'escalated', 'dormant')),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    tags TEXT[] DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    UNIQUE(novel_id, domain_a, domain_b),
    CHECK (domain_a != domain_b)
);

-- 2. 冲突实体表 (扩展版)
CREATE TABLE IF NOT EXISTS conflict_entities (
    id UUID PRIMARY KEY,
    novel_id UUID NOT NULL,
    conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE SET NULL,

    -- 实体基本信息
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL CHECK (entity_type IN (
        '核心资源', '法条制度', '关键角色', '冲突场景', '组织机构', '技术工艺',
        '贸易商品', '地理位置', '文化符号', '权力象征'
    )),
    entity_subtype VARCHAR(100),

    -- 域和归属
    primary_domain VARCHAR(50),
    involved_domains TEXT[] NOT NULL DEFAULT '{}',
    domain_stance JSONB DEFAULT '{}', -- 各域对该实体的立场

    -- 实体特征
    description TEXT NOT NULL,
    characteristics JSONB DEFAULT '{}',
    functions TEXT[] DEFAULT '{}',

    -- 价值评估
    strategic_value DECIMAL(3,1) DEFAULT 5.0 CHECK (strategic_value >= 0 AND strategic_value <= 10),
    economic_value DECIMAL(3,1) DEFAULT 5.0 CHECK (economic_value >= 0 AND economic_value <= 10),
    symbolic_value DECIMAL(3,1) DEFAULT 5.0 CHECK (symbolic_value >= 0 AND symbolic_value <= 10),
    scarcity_level DECIMAL(3,1) DEFAULT 5.0 CHECK (scarcity_level >= 0 AND scarcity_level <= 10),

    -- 冲突相关属性
    conflict_roles TEXT[] DEFAULT '{}',
    dispute_intensity INTEGER DEFAULT 5 CHECK (dispute_intensity >= 1 AND dispute_intensity <= 10),
    control_status VARCHAR(50) DEFAULT 'disputed',

    -- 历史和背景
    origin_story TEXT,
    historical_significance TEXT,
    current_status TEXT,

    -- 识别和验证
    confidence_score DECIMAL(4,3) DEFAULT 0.800 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    validation_status VARCHAR(50) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'rejected', 'needs_review')),

    -- 元数据
    aliases TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    references TEXT[] DEFAULT '{}',
    source_locations JSONB DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 索引约束
    UNIQUE(novel_id, name, entity_type)
);

-- 3. 冲突关系网络表
CREATE TABLE IF NOT EXISTS conflict_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE SET NULL,

    -- 关系双方
    source_entity_id UUID NOT NULL REFERENCES conflict_entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES conflict_entities(id) ON DELETE CASCADE,

    -- 关系类型和特征
    relation_type VARCHAR(50) NOT NULL CHECK (relation_type IN (
        '争夺', '控制', '依赖', '影响', '制约', '触发', '衍生', '替代',
        '合作', '敌对', '竞争', '互补', '冲突', '协调'
    )),
    relation_subtype VARCHAR(100),

    -- 关系强度和方向
    strength DECIMAL(3,2) DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
    directionality VARCHAR(20) DEFAULT 'bidirectional' CHECK (directionality IN ('unidirectional', 'bidirectional')),
    stability DECIMAL(3,2) DEFAULT 0.5 CHECK (stability >= 0.0 AND stability <= 1.0),

    -- 关系上下文
    description TEXT,
    context TEXT,
    conditions TEXT[] DEFAULT '{}',
    effects TEXT[] DEFAULT '{}',

    -- 跨域特征
    is_cross_domain BOOLEAN DEFAULT FALSE,
    source_domain VARCHAR(50),
    target_domain VARCHAR(50),

    -- 时间和动态特征
    temporal_context VARCHAR(100), -- historical, current, future_potential
    evolution_trend VARCHAR(50), -- strengthening, weakening, stable, fluctuating

    -- 影响评估
    impact_level INTEGER DEFAULT 5 CHECK (impact_level >= 1 AND impact_level <= 10),
    visibility VARCHAR(20) DEFAULT 'public' CHECK (visibility IN ('public', 'hidden', 'secret')),

    -- 验证信息
    confidence_score DECIMAL(4,3) DEFAULT 0.700 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    detection_method VARCHAR(100) DEFAULT 'manual',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CHECK (source_entity_id != target_entity_id),
    UNIQUE(source_entity_id, target_entity_id, relation_type)
);

-- =============================================
-- 冲突升级和动态表
-- =============================================

-- 4. 冲突升级路径表
CREATE TABLE IF NOT EXISTS conflict_escalation_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conflict_matrix_id UUID NOT NULL REFERENCES cross_domain_conflict_matrix(id) ON DELETE CASCADE,

    -- 升级等级信息
    level INTEGER NOT NULL CHECK (level >= 1 AND level <= 10),
    level_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,

    -- 触发机制
    triggers TEXT[] NOT NULL DEFAULT '{}',
    prerequisites TEXT[] DEFAULT '{}',
    environmental_factors TEXT[] DEFAULT '{}',

    -- 结果和影响
    immediate_consequences TEXT[] DEFAULT '{}',
    long_term_effects TEXT[] DEFAULT '{}',
    collateral_damage TEXT[] DEFAULT '{}',
    affected_entities UUID[] DEFAULT '{}',

    -- 概率和风险评估
    escalation_probability DECIMAL(3,2) DEFAULT 0.5 CHECK (escalation_probability >= 0.0 AND escalation_probability <= 1.0),
    success_probability DECIMAL(3,2) DEFAULT 0.5 CHECK (success_probability >= 0.0 AND success_probability <= 1.0),
    risk_level INTEGER DEFAULT 5 CHECK (risk_level >= 1 AND risk_level <= 10),
    threat_level VARCHAR(20) DEFAULT 'medium' CHECK (threat_level IN ('low', 'medium', 'high', 'critical')),

    -- 可控性和可逆性
    controllability DECIMAL(3,2) DEFAULT 0.5 CHECK (controllability >= 0.0 AND controllability <= 1.0),
    reversibility DECIMAL(3,2) DEFAULT 0.5 CHECK (reversibility >= 0.0 AND reversibility <= 1.0),
    intervention_points TEXT[] DEFAULT '{}',

    -- 时间估算
    estimated_duration VARCHAR(100),
    warning_time VARCHAR(100),
    resolution_time VARCHAR(100),

    -- 影响范围
    impact_scope TEXT[] DEFAULT '{}',
    affected_domains TEXT[] DEFAULT '{}',
    spillover_effects TEXT[] DEFAULT '{}',

    -- 路径关系
    previous_level_id UUID REFERENCES conflict_escalation_paths(id),
    next_level_ids UUID[] DEFAULT '{}',
    alternative_paths UUID[] DEFAULT '{}',

    -- 历史记录
    historical_precedents TEXT[] DEFAULT '{}',
    real_world_examples TEXT[] DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. 冲突场景表
CREATE TABLE IF NOT EXISTS conflict_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE CASCADE,
    escalation_level_id UUID REFERENCES conflict_escalation_paths(id) ON DELETE SET NULL,

    -- 场景基本信息
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    scenario_type VARCHAR(50) DEFAULT '跨域冲突',
    scenario_subtype VARCHAR(100),

    -- 参与方信息
    primary_domains TEXT[] NOT NULL,
    secondary_domains TEXT[] DEFAULT '{}',
    key_participants UUID[] DEFAULT '{}', -- 引用conflict_entities
    participant_roles JSONB DEFAULT '{}',

    -- 场景设定
    setting_location TEXT,
    setting_time VARCHAR(100),
    environmental_context TEXT,

    -- 触发和发展
    trigger_events TEXT[] DEFAULT '{}',
    preconditions TEXT[] DEFAULT '{}',
    catalysts TEXT[] DEFAULT '{}',
    escalation_factors TEXT[] DEFAULT '{}',

    -- 进程和结果
    typical_progression TEXT[] DEFAULT '{}',
    decision_points TEXT[] DEFAULT '{}',
    possible_outcomes TEXT[] DEFAULT '{}',
    resolution_methods TEXT[] DEFAULT '{}',

    -- 复杂性评估
    complexity_level INTEGER DEFAULT 5 CHECK (complexity_level >= 1 AND complexity_level <= 10),
    unpredictability INTEGER DEFAULT 5 CHECK (unpredictability >= 1 AND unpredictability <= 10),
    moral_complexity INTEGER DEFAULT 5 CHECK (moral_complexity >= 1 AND moral_complexity <= 10),

    -- 影响评估
    impact_scale INTEGER DEFAULT 5 CHECK (impact_scale >= 1 AND impact_scale <= 10),
    duration_estimate VARCHAR(100),
    resource_requirements TEXT[] DEFAULT '{}',

    -- 故事价值
    drama_potential INTEGER DEFAULT 5 CHECK (drama_potential >= 1 AND drama_potential <= 10),
    character_development_potential INTEGER DEFAULT 5 CHECK (character_development_potential >= 1 AND character_development <= 10),
    plot_integration_value INTEGER DEFAULT 5 CHECK (plot_integration_value >= 1 AND plot_integration_value <= 10),

    -- 关联和引用
    related_scenarios UUID[] DEFAULT '{}',
    historical_parallels TEXT[] DEFAULT '{}',

    -- 创作元数据
    inspiration_sources TEXT[] DEFAULT '{}',
    thematic_elements TEXT[] DEFAULT '{}',
    genre_tags TEXT[] DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 故事创作支持表
-- =============================================

-- 6. 故事钩子表 (扩展版)
CREATE TABLE IF NOT EXISTS conflict_story_hooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE SET NULL,
    scenario_id UUID REFERENCES conflict_scenarios(id) ON DELETE SET NULL,

    -- 钩子基本信息
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    hook_type VARCHAR(50) DEFAULT '综合冲突' CHECK (hook_type IN (
        '悬疑推理', '政治阴谋', '权力斗争', '身份认同', '道德冲突',
        '生存危机', '情感纠葛', '复仇故事', '成长历程', '综合冲突'
    )),
    hook_subtype VARCHAR(100),

    -- 冲突相关
    conflict_types TEXT[] DEFAULT '{}',
    domains_involved TEXT[] NOT NULL,
    key_entities UUID[] DEFAULT '{}',

    -- 故事要素
    main_characters TEXT[] DEFAULT '{}',
    character_archetypes TEXT[] DEFAULT '{}',
    character_motivations TEXT[] DEFAULT '{}',
    moral_themes TEXT[] DEFAULT '{}',
    emotional_beats TEXT[] DEFAULT '{}',

    -- 情节结构
    setup_requirements TEXT[] DEFAULT '{}',
    inciting_incident TEXT,
    rising_action_elements TEXT[] DEFAULT '{}',
    climax_potential TEXT[] DEFAULT '{}',
    resolution_options TEXT[] DEFAULT '{}',

    -- 发展路径
    development_paths TEXT[] DEFAULT '{}',
    branching_points TEXT[] DEFAULT '{}',
    alternative_endings TEXT[] DEFAULT '{}',

    -- 创作评估
    originality INTEGER DEFAULT 5 CHECK (originality >= 1 AND originality <= 10),
    complexity INTEGER DEFAULT 5 CHECK (complexity >= 1 AND complexity <= 10),
    emotional_impact INTEGER DEFAULT 5 CHECK (emotional_impact >= 1 AND emotional_impact <= 10),
    plot_integration INTEGER DEFAULT 5 CHECK (plot_integration >= 1 AND plot_integration <= 10),
    character_development INTEGER DEFAULT 5 CHECK (character_development >= 1 AND character_development <= 10),

    -- 市场价值
    target_audience VARCHAR(100),
    genre_appeal INTEGER DEFAULT 5 CHECK (genre_appeal >= 1 AND genre_appeal <= 10),
    marketability DECIMAL(3,1) DEFAULT 5.0 CHECK (marketability >= 0 AND marketability <= 10),
    adaptation_potential INTEGER DEFAULT 5 CHECK (adaptation_potential >= 1 AND adaptation_potential <= 10),

    -- 综合评分
    overall_score DECIMAL(3,1) DEFAULT 5.0 CHECK (overall_score >= 0 AND overall_score <= 10),
    priority_level INTEGER DEFAULT 5 CHECK (priority_level >= 1 AND priority_level <= 10),

    -- 使用统计
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2) DEFAULT 0.0,
    last_used TIMESTAMP WITH TIME ZONE,

    -- AI生成追踪
    is_ai_generated BOOLEAN DEFAULT FALSE,
    generation_method VARCHAR(100),
    generation_parameters JSONB DEFAULT '{}',
    generation_model VARCHAR(100),
    generation_version VARCHAR(50),
    human_validation_status VARCHAR(50) DEFAULT 'pending' CHECK (human_validation_status IN ('pending', 'approved', 'rejected', 'needs_revision')),
    human_validator_id UUID,
    validation_notes TEXT,
    validation_date TIMESTAMP WITH TIME ZONE,

    -- 标签和分类
    tags TEXT[] DEFAULT '{}',
    genres TEXT[] DEFAULT '{}',
    themes TEXT[] DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 分析和智能支持表
-- =============================================

-- 7. 冲突分析结果表
CREATE TABLE IF NOT EXISTS conflict_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE CASCADE,

    -- 分析基本信息
    analysis_type VARCHAR(100) NOT NULL CHECK (analysis_type IN (
        '冲突矩阵分析', '实体关系网络分析', '冲突升级路径分析',
        '故事情节潜力评估', '世界观一致性检查', '角色发展分析',
        '情节连贯性分析', '主题深度分析', '市场价值评估'
    )),
    analysis_version VARCHAR(50) NOT NULL,
    analysis_method VARCHAR(100),

    -- 分析配置
    analyzer_config JSONB DEFAULT '{}',
    input_parameters JSONB DEFAULT '{}',

    -- 分析结果
    results JSONB NOT NULL,
    summary TEXT,
    insights TEXT[] DEFAULT '{}',
    recommendations TEXT[] DEFAULT '{}',
    warnings TEXT[] DEFAULT '{}',

    -- 质量评估
    confidence_score DECIMAL(4,3) DEFAULT 0.800 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    completeness DECIMAL(3,2) DEFAULT 1.0 CHECK (completeness >= 0.0 AND completeness <= 1.0),
    accuracy_estimate DECIMAL(3,2) DEFAULT 0.8 CHECK (accuracy_estimate >= 0.0 AND accuracy_estimate <= 1.0),
    reliability_score DECIMAL(3,2) DEFAULT 0.8 CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),

    -- 验证状态
    validation_status VARCHAR(50) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'rejected', 'needs_review')),
    validator_id UUID,
    validator_notes TEXT,
    validation_date TIMESTAMP WITH TIME ZONE,

    -- 性能统计
    processing_time_ms INTEGER,
    memory_usage_mb INTEGER,
    cpu_usage_percent DECIMAL(5,2),
    resource_usage JSONB DEFAULT '{}',

    -- 比较和版本
    baseline_version UUID REFERENCES conflict_analysis_results(id),
    improvement_metrics JSONB DEFAULT '{}',
    regression_flags TEXT[] DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. 冲突预测表
CREATE TABLE IF NOT EXISTS conflict_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conflict_matrix_id UUID NOT NULL REFERENCES cross_domain_conflict_matrix(id) ON DELETE CASCADE,
    analysis_result_id UUID REFERENCES conflict_analysis_results(id) ON DELETE SET NULL,

    -- 预测基本信息
    prediction_type VARCHAR(100) NOT NULL,
    prediction_horizon VARCHAR(50), -- short_term, medium_term, long_term
    scenario_name VARCHAR(255),

    -- 预测内容
    predicted_escalation_path INTEGER[] DEFAULT '{}',
    probability_scores DECIMAL(3,2)[] DEFAULT '{}',
    confidence_intervals JSONB DEFAULT '{}',

    -- 时间估算
    time_estimates TEXT[] DEFAULT '{}',
    critical_timepoints TIMESTAMP WITH TIME ZONE[] DEFAULT '{}',

    -- 风险因素
    risk_factors TEXT[] DEFAULT '{}',
    uncertainty_factors TEXT[] DEFAULT '{}',
    external_variables TEXT[] DEFAULT '{}',

    -- 预防和缓解
    early_warning_indicators TEXT[] DEFAULT '{}',
    intervention_opportunities TEXT[] DEFAULT '{}',
    mitigation_strategies TEXT[] DEFAULT '{}',
    prevention_measures TEXT[] DEFAULT '{}',

    -- 模型信息
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    training_data_period VARCHAR(100),
    feature_importance JSONB DEFAULT '{}',

    -- 预测质量
    prediction_confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (prediction_confidence >= 0.0 AND prediction_confidence <= 1.0),
    model_accuracy DECIMAL(3,2),
    validation_score DECIMAL(3,2),

    -- 实际结果跟踪
    actual_outcome TEXT,
    outcome_recorded_at TIMESTAMP WITH TIME ZONE,
    prediction_accuracy DECIMAL(3,2),
    error_analysis TEXT,

    -- 时间戳
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 网络分析和图论支持表
-- =============================================

-- 9. 网络分析结果表
CREATE TABLE IF NOT EXISTS network_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE CASCADE,
    analysis_result_id UUID REFERENCES conflict_analysis_results(id) ON DELETE SET NULL,

    -- 分析基本信息
    analysis_type VARCHAR(100) NOT NULL CHECK (analysis_type IN (
        '度分布分析', '中心性分析', '社团检测', '路径分析', '网络密度分析',
        '小世界特性', '无标度特性', '传播动力学', '拓扑稳定性', '网络演化'
    )),
    network_type VARCHAR(50) DEFAULT '冲突关系网络',
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 网络全局指标
    network_density DECIMAL(6,4),
    average_clustering_coefficient DECIMAL(6,4),
    average_path_length DECIMAL(6,2),
    diameter INTEGER,
    radius INTEGER,
    assortativity DECIMAL(6,4),
    modularity DECIMAL(6,4),

    -- 度分布特征
    degree_distribution JSONB DEFAULT '{}',
    average_degree DECIMAL(6,2),
    max_degree INTEGER,
    min_degree INTEGER,
    degree_variance DECIMAL(8,4),
    power_law_exponent DECIMAL(6,4),
    is_scale_free BOOLEAN DEFAULT FALSE,

    -- 中心性分析
    centrality_measures JSONB DEFAULT '{}', -- 存储所有节点的中心性指标
    top_betweenness_nodes UUID[] DEFAULT '{}',
    top_closeness_nodes UUID[] DEFAULT '{}',
    top_eigenvector_nodes UUID[] DEFAULT '{}',
    top_pagerank_nodes UUID[] DEFAULT '{}',

    -- 社团结构
    community_count INTEGER,
    community_structure JSONB DEFAULT '{}',
    modularity_optimization_method VARCHAR(100),
    significant_communities JSONB DEFAULT '{}',

    -- 路径分析
    shortest_paths_analysis JSONB DEFAULT '{}',
    critical_paths JSONB DEFAULT '{}',
    bottleneck_nodes UUID[] DEFAULT '{}',
    bridge_edges JSONB DEFAULT '{}',

    -- 网络稳定性
    robustness_measures JSONB DEFAULT '{}',
    vulnerability_analysis JSONB DEFAULT '{}',
    failure_scenarios JSONB DEFAULT '{}',

    -- 动态特征
    growth_patterns JSONB DEFAULT '{}',
    temporal_analysis JSONB DEFAULT '{}',
    change_detection JSONB DEFAULT '{}',

    -- 分析质量
    analysis_confidence DECIMAL(3,2) DEFAULT 0.8,
    computational_complexity VARCHAR(50),
    processing_time_seconds DECIMAL(8,2),
    memory_usage_mb INTEGER,

    -- 可视化数据
    layout_coordinates JSONB DEFAULT '{}',
    visualization_config JSONB DEFAULT '{}',
    export_formats TEXT[] DEFAULT '{}',

    -- 比较分析
    baseline_comparison JSONB DEFAULT '{}',
    trend_analysis JSONB DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. AI生成内容管理表
CREATE TABLE IF NOT EXISTS ai_generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    content_type VARCHAR(100) NOT NULL CHECK (content_type IN (
        '故事钩子', '冲突场景', '角色关系', '情节发展', '对话内容',
        '背景描述', '世界观设定', '文化元素', '技术设定', '其他'
    )),
    parent_entity_id UUID, -- 关联的父实体ID
    parent_entity_type VARCHAR(100), -- 父实体类型

    -- 生成内容
    title VARCHAR(500),
    content TEXT NOT NULL,
    structured_data JSONB DEFAULT '{}',

    -- 生成参数
    ai_model VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    generation_method VARCHAR(100),
    prompt_template TEXT,
    input_parameters JSONB DEFAULT '{}',
    generation_config JSONB DEFAULT '{}',

    -- 生成上下文
    context_entities UUID[] DEFAULT '{}',
    context_relationships UUID[] DEFAULT '{}',
    context_constraints TEXT[] DEFAULT '{}',
    inspiration_sources TEXT[] DEFAULT '{}',

    -- 质量评估
    ai_confidence_score DECIMAL(4,3) DEFAULT 0.5,
    quality_metrics JSONB DEFAULT '{}',
    coherence_score DECIMAL(3,2),
    creativity_score DECIMAL(3,2),
    relevance_score DECIMAL(3,2),
    originality_score DECIMAL(3,2),

    -- 人工验证
    human_validation_status VARCHAR(50) DEFAULT 'pending' CHECK (human_validation_status IN (
        'pending', 'approved', 'rejected', 'needs_revision', 'in_review'
    )),
    human_validator_id UUID,
    validation_score DECIMAL(3,2),
    validation_notes TEXT,
    validation_date TIMESTAMP WITH TIME ZONE,
    revision_suggestions TEXT[] DEFAULT '{}',

    -- 版本控制
    version_number INTEGER DEFAULT 1,
    parent_version_id UUID REFERENCES ai_generated_content(id),
    is_current_version BOOLEAN DEFAULT TRUE,
    version_notes TEXT,

    -- 使用跟踪
    usage_count INTEGER DEFAULT 0,
    effectiveness_rating DECIMAL(3,2),
    user_feedback TEXT[] DEFAULT '{}',
    last_used TIMESTAMP WITH TIME ZONE,

    -- 改进和优化
    optimization_suggestions TEXT[] DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    ab_test_results JSONB DEFAULT '{}',

    -- 审核和合规
    content_flags TEXT[] DEFAULT '{}',
    safety_check_passed BOOLEAN DEFAULT TRUE,
    ethical_review_status VARCHAR(50) DEFAULT 'not_required',
    compliance_notes TEXT,

    -- 标签和分类
    tags TEXT[] DEFAULT '{}',
    categories TEXT[] DEFAULT '{}',
    domains_involved TEXT[] DEFAULT '{}',

    -- 时间戳
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 高性能索引创建
-- =============================================

-- 冲突矩阵索引
CREATE INDEX IF NOT EXISTS idx_conflict_matrix_novel_domains ON cross_domain_conflict_matrix(novel_id, domain_a, domain_b);
CREATE INDEX IF NOT EXISTS idx_conflict_matrix_intensity ON cross_domain_conflict_matrix(intensity DESC);
CREATE INDEX IF NOT EXISTS idx_conflict_matrix_risk ON cross_domain_conflict_matrix(risk_level DESC);
CREATE INDEX IF NOT EXISTS idx_conflict_matrix_status ON cross_domain_conflict_matrix(status);
CREATE INDEX IF NOT EXISTS idx_conflict_matrix_priority ON cross_domain_conflict_matrix(priority DESC);

-- 冲突实体索引
CREATE INDEX IF NOT EXISTS idx_conflict_entities_novel_type ON conflict_entities(novel_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_conflict_entities_domains ON conflict_entities USING GIN(involved_domains);
CREATE INDEX IF NOT EXISTS idx_conflict_entities_name_search ON conflict_entities USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_conflict_entities_strategic_value ON conflict_entities(strategic_value DESC);
CREATE INDEX IF NOT EXISTS idx_conflict_entities_validation ON conflict_entities(validation_status);

-- 冲突关系索引
CREATE INDEX IF NOT EXISTS idx_conflict_relations_source ON conflict_relations(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_conflict_relations_target ON conflict_relations(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_conflict_relations_type ON conflict_relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_conflict_relations_strength ON conflict_relations(strength DESC);
CREATE INDEX IF NOT EXISTS idx_conflict_relations_cross_domain ON conflict_relations(is_cross_domain);

-- 升级路径索引
CREATE INDEX IF NOT EXISTS idx_escalation_paths_matrix ON conflict_escalation_paths(conflict_matrix_id);
CREATE INDEX IF NOT EXISTS idx_escalation_paths_level ON conflict_escalation_paths(level);
CREATE INDEX IF NOT EXISTS idx_escalation_paths_probability ON conflict_escalation_paths(escalation_probability DESC);
CREATE INDEX IF NOT EXISTS idx_escalation_paths_risk ON conflict_escalation_paths(risk_level DESC);

-- 冲突场景索引
CREATE INDEX IF NOT EXISTS idx_conflict_scenarios_novel_matrix ON conflict_scenarios(novel_id, conflict_matrix_id);
CREATE INDEX IF NOT EXISTS idx_conflict_scenarios_domains ON conflict_scenarios USING GIN(primary_domains);
CREATE INDEX IF NOT EXISTS idx_conflict_scenarios_complexity ON conflict_scenarios(complexity_level DESC);
CREATE INDEX IF NOT EXISTS idx_conflict_scenarios_drama ON conflict_scenarios(drama_potential DESC);

-- 故事钩子索引
CREATE INDEX IF NOT EXISTS idx_story_hooks_novel_type ON conflict_story_hooks(novel_id, hook_type);
CREATE INDEX IF NOT EXISTS idx_story_hooks_domains ON conflict_story_hooks USING GIN(domains_involved);
CREATE INDEX IF NOT EXISTS idx_story_hooks_score ON conflict_story_hooks(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_story_hooks_priority ON conflict_story_hooks(priority_level DESC);
CREATE INDEX IF NOT EXISTS idx_story_hooks_usage ON conflict_story_hooks(usage_count DESC);

-- 分析结果索引
CREATE INDEX IF NOT EXISTS idx_analysis_results_novel_type ON conflict_analysis_results(novel_id, analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_matrix ON conflict_analysis_results(conflict_matrix_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_confidence ON conflict_analysis_results(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created ON conflict_analysis_results(created_at DESC);

-- 预测结果索引
CREATE INDEX IF NOT EXISTS idx_predictions_matrix ON conflict_predictions(conflict_matrix_id);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON conflict_predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON conflict_predictions(prediction_confidence DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON conflict_predictions(prediction_date DESC);

-- 网络分析结果索引
CREATE INDEX IF NOT EXISTS idx_network_analysis_novel_type ON network_analysis_results(novel_id, analysis_type);
CREATE INDEX IF NOT EXISTS idx_network_analysis_matrix ON network_analysis_results(conflict_matrix_id);
CREATE INDEX IF NOT EXISTS idx_network_analysis_confidence ON network_analysis_results(analysis_confidence DESC);
CREATE INDEX IF NOT EXISTS idx_network_analysis_date ON network_analysis_results(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_network_analysis_node_count ON network_analysis_results(node_count DESC);
CREATE INDEX IF NOT EXISTS idx_network_analysis_edge_count ON network_analysis_results(edge_count DESC);
CREATE INDEX IF NOT EXISTS idx_network_analysis_density ON network_analysis_results(network_density DESC);

-- AI生成内容索引
CREATE INDEX IF NOT EXISTS idx_ai_content_novel_type ON ai_generated_content(novel_id, content_type);
CREATE INDEX IF NOT EXISTS idx_ai_content_parent ON ai_generated_content(parent_entity_id, parent_entity_type);
CREATE INDEX IF NOT EXISTS idx_ai_content_model ON ai_generated_content(ai_model);
CREATE INDEX IF NOT EXISTS idx_ai_content_validation ON ai_generated_content(human_validation_status);
CREATE INDEX IF NOT EXISTS idx_ai_content_version ON ai_generated_content(version_number, is_current_version);
CREATE INDEX IF NOT EXISTS idx_ai_content_quality ON ai_generated_content(ai_confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_ai_content_usage ON ai_generated_content(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_ai_content_generated_date ON ai_generated_content(generated_at DESC);

-- 全文搜索索引
CREATE INDEX IF NOT EXISTS idx_ai_content_title_search ON ai_generated_content USING gin(to_tsvector('simple', title));
CREATE INDEX IF NOT EXISTS idx_ai_content_content_search ON ai_generated_content USING gin(to_tsvector('simple', content));

-- =============================================
-- 触发器和函数
-- =============================================

-- 更新时间戳函数
CREATE OR REPLACE FUNCTION update_conflict_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表创建更新时间戳触发器
CREATE TRIGGER update_conflict_matrix_updated_at BEFORE UPDATE ON cross_domain_conflict_matrix FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_conflict_entities_updated_at BEFORE UPDATE ON conflict_entities FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_conflict_relations_updated_at BEFORE UPDATE ON conflict_relations FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_escalation_paths_updated_at BEFORE UPDATE ON conflict_escalation_paths FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_conflict_scenarios_updated_at BEFORE UPDATE ON conflict_scenarios FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_story_hooks_updated_at BEFORE UPDATE ON conflict_story_hooks FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_analysis_results_updated_at BEFORE UPDATE ON conflict_analysis_results FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_predictions_updated_at BEFORE UPDATE ON conflict_predictions FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_network_analysis_updated_at BEFORE UPDATE ON network_analysis_results FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();
CREATE TRIGGER update_ai_content_updated_at BEFORE UPDATE ON ai_generated_content FOR EACH ROW EXECUTE FUNCTION update_conflict_updated_at_column();

-- =============================================
-- 数据完整性检查函数
-- =============================================

-- 检查冲突矩阵完整性
CREATE OR REPLACE FUNCTION check_conflict_matrix_integrity()
RETURNS TABLE(domain_pair TEXT, issue_description TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (domain_a || ' ↔ ' || domain_b)::TEXT as domain_pair,
        CASE
            WHEN intensity < 1 THEN '冲突强度过低'
            WHEN intensity > 4 AND array_length(core_resources, 1) < 2 THEN '高强度冲突缺乏足够的核心资源'
            WHEN array_length(typical_scenarios, 1) < 1 THEN '缺少典型场景描述'
            WHEN array_length(key_roles, 1) < 2 THEN '关键角色数量不足'
            ELSE '正常'
        END::TEXT as issue_description
    FROM cross_domain_conflict_matrix
    WHERE intensity < 1
       OR (intensity > 4 AND array_length(core_resources, 1) < 2)
       OR array_length(typical_scenarios, 1) < 1
       OR array_length(key_roles, 1) < 2;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 统计分析视图
-- =============================================

-- 冲突强度统计视图
CREATE OR REPLACE VIEW conflict_intensity_stats AS
SELECT
    novel_id,
    COUNT(*) as total_conflicts,
    AVG(intensity) as avg_intensity,
    MAX(intensity) as max_intensity,
    MIN(intensity) as min_intensity,
    COUNT(CASE WHEN intensity >= 4 THEN 1 END) as high_intensity_conflicts,
    COUNT(CASE WHEN intensity >= 3 THEN 1 END) as medium_high_conflicts,
    array_agg(DISTINCT domain_a || '↔' || domain_b ORDER BY intensity DESC) as conflict_pairs_by_intensity
FROM cross_domain_conflict_matrix
GROUP BY novel_id;

-- 域参与度统计视图
CREATE OR REPLACE VIEW domain_participation_stats AS
WITH domain_conflicts AS (
    SELECT novel_id, domain_a as domain, intensity FROM cross_domain_conflict_matrix
    UNION ALL
    SELECT novel_id, domain_b as domain, intensity FROM cross_domain_conflict_matrix
)
SELECT
    novel_id,
    domain,
    COUNT(*) as conflict_count,
    AVG(intensity) as avg_conflict_intensity,
    MAX(intensity) as max_conflict_intensity,
    CASE
        WHEN AVG(intensity) >= 3.5 THEN '高冲突域'
        WHEN AVG(intensity) >= 2.5 THEN '中冲突域'
        ELSE '低冲突域'
    END as conflict_tendency
FROM domain_conflicts
GROUP BY novel_id, domain
ORDER BY novel_id, avg_conflict_intensity DESC;

-- 故事潜力统计视图
CREATE OR REPLACE VIEW story_potential_stats AS
SELECT
    h.novel_id,
    h.conflict_matrix_id,
    m.domain_a || '↔' || m.domain_b as conflict_pair,
    COUNT(h.id) as hook_count,
    AVG(h.overall_score) as avg_story_score,
    AVG(h.complexity) as avg_complexity,
    AVG(h.emotional_impact) as avg_emotional_impact,
    AVG(h.marketability) as avg_marketability,
    array_agg(h.hook_type) as hook_types
FROM conflict_story_hooks h
JOIN cross_domain_conflict_matrix m ON h.conflict_matrix_id = m.id
GROUP BY h.novel_id, h.conflict_matrix_id, m.domain_a, m.domain_b
ORDER BY avg_story_score DESC;

-- 实体重要性统计视图
CREATE OR REPLACE VIEW entity_importance_stats AS
SELECT
    novel_id,
    entity_type,
    COUNT(*) as entity_count,
    AVG(strategic_value) as avg_strategic_value,
    AVG(economic_value) as avg_economic_value,
    AVG(symbolic_value) as avg_symbolic_value,
    AVG(scarcity_level) as avg_scarcity,
    COUNT(CASE WHEN strategic_value >= 8 THEN 1 END) as high_value_entities
FROM conflict_entities
GROUP BY novel_id, entity_type
ORDER BY avg_strategic_value DESC;