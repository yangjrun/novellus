-- 文化框架数据库表结构
-- PostgreSQL Schema for Cultural Framework System
-- 优化版本：支持复杂文化数据模型和高性能查询

-- 1. 文化框架主表 (PostgreSQL) - 六维文化体系核心
CREATE TABLE IF NOT EXISTS cultural_frameworks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    domain_type VARCHAR(50) NOT NULL CHECK (domain_type IN ('人域', '天域', '荒域', '冥域', '魔域', '虚域', '海域', '源域', '永恒域')),
    dimension VARCHAR(50) NOT NULL CHECK (dimension IN ('神话与宗教', '权力与法律', '经济与技术', '家庭与教育', '仪式与日常', '艺术与娱乐')),

    -- 基本信息
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    key_elements TEXT[], -- PostgreSQL数组类型
    detailed_content TEXT NOT NULL,

    -- 处理状态和质量评估
    processing_status VARCHAR(50) DEFAULT 'draft' CHECK (processing_status IN ('draft', 'processed', 'validated', 'published')),
    confidence_score DECIMAL(4,3) DEFAULT 0.500 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    analysis_metadata JSONB DEFAULT '{}', -- 分析过程元数据

    -- 元数据
    tags TEXT[],
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    completion_status DECIMAL(3,2) DEFAULT 1.0 CHECK (completion_status >= 0.0 AND completion_status <= 1.0),

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    UNIQUE(novel_id, domain_type, dimension)
);

-- 2. 文化实体表 (PostgreSQL) - 组织、概念、物品、仪式等实体
CREATE TABLE IF NOT EXISTS cultural_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    framework_id UUID REFERENCES cultural_frameworks(id) ON DELETE SET NULL,

    -- 基本信息
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('组织机构', '重要概念', '文化物品', '仪式活动', '身份制度', '货币体系', '技术工艺', '信仰体系', '习俗传统', '地理位置', '人物角色')),
    domain_type VARCHAR(50) CHECK (domain_type IN ('人域', '天域', '荒域', '冥域', '魔域', '虚域', '海域', '源域', '永恒域')),
    dimensions TEXT[], -- 关联的文化维度

    -- 详细信息
    description TEXT NOT NULL,
    characteristics JSONB DEFAULT '{}',
    functions TEXT[],
    significance TEXT,

    -- 上下文信息
    origin_story TEXT,
    historical_context TEXT,
    current_status TEXT,

    -- 识别和分析信息
    confidence_score DECIMAL(4,3) DEFAULT 0.500 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    extraction_method VARCHAR(100) DEFAULT 'manual', -- 提取方法：manual, ai_analysis, pattern_match
    validation_status VARCHAR(50) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'rejected', 'needs_review')),

    -- 元数据
    aliases TEXT[],
    tags TEXT[],
    references TEXT[], -- 引用文本片段
    source_text_location JSONB DEFAULT '{}', -- 源文本位置信息

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    UNIQUE(novel_id, name, entity_type)
);

-- 3. 文化关系表 (PostgreSQL) - 实体间复杂关系网络
CREATE TABLE IF NOT EXISTS cultural_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 关系双方
    source_entity_id UUID NOT NULL REFERENCES cultural_entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES cultural_entities(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL CHECK (relation_type IN ('包含', '关联', '冲突', '衍生自', '控制', '受影响于', '相似于', '依赖', '替代', '合作', '敌对')),

    -- 关系描述
    description TEXT,
    strength DECIMAL(3,2) DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
    context TEXT,

    -- 跨域关系标识
    is_cross_domain BOOLEAN DEFAULT FALSE,
    source_domain VARCHAR(50),
    target_domain VARCHAR(50),

    -- 关系分析信息
    confidence_score DECIMAL(4,3) DEFAULT 0.500 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    detection_method VARCHAR(100) DEFAULT 'manual', -- 检测方法：manual, text_analysis, pattern_inference
    bidirectional BOOLEAN DEFAULT FALSE, -- 是否为双向关系
    temporal_context VARCHAR(100), -- 时间上下文：historical, current, future_potential

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CHECK (source_entity_id != target_entity_id),
    UNIQUE(source_entity_id, target_entity_id, relation_type)
);

-- 4. 剧情钩子表 (PostgreSQL)
CREATE TABLE IF NOT EXISTS plot_hooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    domain_type VARCHAR(50) NOT NULL CHECK (domain_type IN ('人域', '天域', '荒域', '冥域', '魔域', '虚域', '海域', '源域')),

    -- 钩子内容
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    trigger_conditions TEXT[],
    potential_outcomes TEXT[],

    -- 关联文化元素
    related_entities UUID[], -- 相关实体ID数组
    cultural_dimensions TEXT[], -- 涉及的文化维度

    -- 元数据
    complexity_level INTEGER DEFAULT 5 CHECK (complexity_level >= 1 AND complexity_level <= 10),
    story_impact INTEGER DEFAULT 5 CHECK (story_impact >= 1 AND story_impact <= 10),
    tags TEXT[],

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. 概念词典表 (PostgreSQL)
CREATE TABLE IF NOT EXISTS concept_dictionary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,

    -- 概念信息
    term VARCHAR(255) NOT NULL,
    definition TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    domain_type VARCHAR(50) CHECK (domain_type IN ('人域', '天域', '荒域', '冥域', '魔域', '虚域', '海域', '源域')),

    -- 详细信息
    etymology TEXT,
    usage_examples TEXT[],
    related_terms TEXT[],

    -- 元数据
    frequency INTEGER DEFAULT 1,
    importance INTEGER DEFAULT 5 CHECK (importance >= 1 AND importance <= 10),

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    UNIQUE(novel_id, term)
);

-- 6. 跨域冲突分析表 (PostgreSQL)
CREATE TABLE IF NOT EXISTS cross_domain_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,

    -- 冲突域
    domain_a VARCHAR(50) NOT NULL,
    domain_b VARCHAR(50) NOT NULL,

    -- 冲突分析
    conflict_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    severity INTEGER DEFAULT 5 CHECK (severity >= 1 AND severity <= 10),

    -- 相关实体
    entities_involved UUID[],
    cultural_dimensions TEXT[],

    -- 分析结果
    potential_resolutions TEXT[],
    story_implications TEXT[],

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CHECK (domain_a != domain_b),
    UNIQUE(novel_id, domain_a, domain_b, conflict_type)
);

-- 创建高性能索引以提升查询性能
-- 文化框架索引
CREATE INDEX IF NOT EXISTS idx_cultural_frameworks_novel_domain ON cultural_frameworks(novel_id, domain_type);
CREATE INDEX IF NOT EXISTS idx_cultural_frameworks_dimension ON cultural_frameworks(dimension);
CREATE INDEX IF NOT EXISTS idx_cultural_frameworks_status ON cultural_frameworks(processing_status);
CREATE INDEX IF NOT EXISTS idx_cultural_frameworks_confidence ON cultural_frameworks(confidence_score DESC);

-- 文化实体索引
CREATE INDEX IF NOT EXISTS idx_cultural_entities_novel_type ON cultural_entities(novel_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_cultural_entities_domain ON cultural_entities(domain_type);
CREATE INDEX IF NOT EXISTS idx_cultural_entities_name ON cultural_entities USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_cultural_entities_validation ON cultural_entities(validation_status);
CREATE INDEX IF NOT EXISTS idx_cultural_entities_confidence ON cultural_entities(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_cultural_entities_framework ON cultural_entities(framework_id);

-- 文化关系索引
CREATE INDEX IF NOT EXISTS idx_cultural_relations_source ON cultural_relations(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_cultural_relations_target ON cultural_relations(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_cultural_relations_cross_domain ON cultural_relations(is_cross_domain);
CREATE INDEX IF NOT EXISTS idx_cultural_relations_type ON cultural_relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_cultural_relations_strength ON cultural_relations(strength DESC);
CREATE INDEX IF NOT EXISTS idx_cultural_relations_bidirectional ON cultural_relations(bidirectional);

-- 剧情钩子索引
CREATE INDEX IF NOT EXISTS idx_plot_hooks_novel_domain ON plot_hooks(novel_id, domain_type);
CREATE INDEX IF NOT EXISTS idx_plot_hooks_complexity ON plot_hooks(complexity_level);
CREATE INDEX IF NOT EXISTS idx_plot_hooks_impact ON plot_hooks(story_impact DESC);

-- 概念词典索引
CREATE INDEX IF NOT EXISTS idx_concept_dictionary_novel_term ON concept_dictionary(novel_id, term);
CREATE INDEX IF NOT EXISTS idx_concept_dictionary_category ON concept_dictionary(category);
CREATE INDEX IF NOT EXISTS idx_concept_dictionary_importance ON concept_dictionary(importance DESC);

-- 跨域冲突索引
CREATE INDEX IF NOT EXISTS idx_cross_domain_conflicts_novel ON cross_domain_conflicts(novel_id);
CREATE INDEX IF NOT EXISTS idx_cross_domain_conflicts_domains ON cross_domain_conflicts(domain_a, domain_b);
CREATE INDEX IF NOT EXISTS idx_cross_domain_conflicts_severity ON cross_domain_conflicts(severity DESC);

-- 分析结果索引
CREATE INDEX IF NOT EXISTS idx_cultural_analysis_novel_type ON cultural_analysis_results(novel_id, analysis_type);
CREATE INDEX IF NOT EXISTS idx_cultural_analysis_confidence ON cultural_analysis_results(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_cultural_analysis_status ON cultural_analysis_results(validation_status);

-- 导入任务索引
CREATE INDEX IF NOT EXISTS idx_cultural_import_jobs_novel ON cultural_import_jobs(novel_id);
CREATE INDEX IF NOT EXISTS idx_cultural_import_jobs_status ON cultural_import_jobs(status);
CREATE INDEX IF NOT EXISTS idx_cultural_import_jobs_created ON cultural_import_jobs(created_at DESC);

-- 创建全文搜索索引 (需要 pg_trgm 扩展)
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_cultural_entities_description_search ON cultural_entities USING gin(description gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS idx_cultural_frameworks_content_search ON cultural_frameworks USING gin(detailed_content gin_trgm_ops);

-- 创建更新时间戳触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表创建更新时间戳触发器
CREATE TRIGGER update_cultural_frameworks_updated_at BEFORE UPDATE ON cultural_frameworks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cultural_entities_updated_at BEFORE UPDATE ON cultural_entities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cultural_relations_updated_at BEFORE UPDATE ON cultural_relations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_plot_hooks_updated_at BEFORE UPDATE ON plot_hooks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_concept_dictionary_updated_at BEFORE UPDATE ON concept_dictionary FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cross_domain_conflicts_updated_at BEFORE UPDATE ON cross_domain_conflicts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 7. 文化数据分析表 (PostgreSQL) - 支持数据处理和质量评估
CREATE TABLE IF NOT EXISTS cultural_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100) NOT NULL CHECK (analysis_type IN ('entity_extraction', 'relation_inference', 'domain_analysis', 'conflict_detection', 'consistency_check')),

    -- 分析结果
    source_text TEXT,
    results JSONB NOT NULL DEFAULT '{}',
    confidence_score DECIMAL(4,3) DEFAULT 0.500 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),

    -- 分析元数据
    analysis_method VARCHAR(100) NOT NULL, -- ai_model, pattern_match, manual_review
    processor_version VARCHAR(50),
    processing_time_ms INTEGER,

    -- 验证状态
    validation_status VARCHAR(50) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'rejected', 'needs_review')),
    validator_notes TEXT,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. 批量导入任务表 (PostgreSQL) - 支持大规模数据导入
CREATE TABLE IF NOT EXISTS cultural_import_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 任务信息
    job_name VARCHAR(255) NOT NULL,
    job_type VARCHAR(100) NOT NULL CHECK (job_type IN ('full_import', 'incremental_update', 'validation_only', 'rollback')),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),

    -- 导入配置
    source_file_path TEXT,
    import_config JSONB DEFAULT '{}',

    -- 处理统计
    total_records INTEGER DEFAULT 0,
    processed_records INTEGER DEFAULT 0,
    successful_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,

    -- 结果信息
    error_messages TEXT[],
    warnings TEXT[],
    processing_log JSONB DEFAULT '{}',

    -- 时间戳
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);