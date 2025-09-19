-- 裂世九域·法则链纪元 PostgreSQL数据库初始化脚本
-- 支持多批次文本内容的渐进式管理系统

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 用于文本搜索
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- 用于复合索引优化

-- =============================================================================
-- 项目和小说管理表
-- =============================================================================

-- 项目表
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    genre VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'archived')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 小说表（支持一个项目多部小说）
CREATE TABLE IF NOT EXISTS novels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    volume_number INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'planning' CHECK (status IN ('planning', 'writing', 'reviewing', 'published', 'archived')),
    word_count INTEGER DEFAULT 0,
    chapter_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, name)
);

-- =============================================================================
-- 批次管理系统
-- =============================================================================

-- 内容批次表 - 用于管理分批次的文本内容
CREATE TABLE IF NOT EXISTS content_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    batch_name VARCHAR(255) NOT NULL,
    batch_number INTEGER NOT NULL,
    batch_type VARCHAR(50) NOT NULL CHECK (batch_type IN ('worldbuilding', 'characters', 'plot', 'scenes', 'dialogue', 'revision')),
    description TEXT,
    word_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'planning' CHECK (status IN ('planning', 'in_progress', 'completed', 'reviewed', 'archived')),
    priority INTEGER DEFAULT 0,
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_id, batch_number)
);

-- 内容段落表 - 存储实际的文本内容
CREATE TABLE IF NOT EXISTS content_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID NOT NULL REFERENCES content_batches(id) ON DELETE CASCADE,
    segment_type VARCHAR(50) NOT NULL CHECK (segment_type IN ('narrative', 'dialogue', 'description', 'action', 'thought', 'flashback')),
    title VARCHAR(500),
    content TEXT NOT NULL,
    word_count INTEGER NOT NULL DEFAULT 0,
    sequence_order INTEGER NOT NULL,
    tags TEXT[], -- PostgreSQL数组类型，用于标签
    emotions TEXT[], -- 情感标签
    characters UUID[], -- 涉及的角色ID数组
    locations UUID[], -- 涉及的地点ID数组
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'published')),
    revision_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 九域世界观核心表
-- =============================================================================

-- 九大域系统表
CREATE TABLE IF NOT EXISTS domains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    domain_type VARCHAR(50) NOT NULL CHECK (domain_type IN ('人域', '天域', '灵域', '魔域', '仙域', '神域', '虚域', '混沌域', '永恒域')),
    description TEXT,
    characteristics JSONB DEFAULT '{}', -- 域的特征
    rules JSONB DEFAULT '{}', -- 域的规则
    power_level INTEGER CHECK (power_level BETWEEN 1 AND 9),
    location_info JSONB DEFAULT '{}', -- 地理信息
    climate_info JSONB DEFAULT '{}', -- 气候信息
    resources JSONB DEFAULT '{}', -- 资源信息
    dangers JSONB DEFAULT '{}', -- 危险信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_id, name)
);

-- 修炼体系表
CREATE TABLE IF NOT EXISTS cultivation_systems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    system_name VARCHAR(255) NOT NULL,
    system_type VARCHAR(100) NOT NULL DEFAULT '法则链修炼',
    description TEXT,
    stages JSONB NOT NULL DEFAULT '[]', -- 修炼阶段数组
    requirements JSONB DEFAULT '{}', -- 修炼要求
    benefits JSONB DEFAULT '{}', -- 修炼益处
    risks JSONB DEFAULT '{}', -- 修炼风险
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_id, system_name)
);

-- 修炼阶段详情表
CREATE TABLE IF NOT EXISTS cultivation_stages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system_id UUID NOT NULL REFERENCES cultivation_systems(id) ON DELETE CASCADE,
    stage_name VARCHAR(255) NOT NULL,
    stage_level INTEGER NOT NULL,
    stage_type VARCHAR(100) NOT NULL CHECK (stage_type IN ('凡身', '开脉', '归源', '封侯', '破界', '帝境', '裂世者')),
    description TEXT,
    power_description TEXT,
    advancement_requirements JSONB DEFAULT '{}',
    typical_abilities JSONB DEFAULT '{}',
    lifespan_increase INTEGER DEFAULT 0, -- 寿命增加（年）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(system_id, stage_level)
);

-- 权力组织表
CREATE TABLE IF NOT EXISTS power_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(100) NOT NULL CHECK (organization_type IN ('天命王朝', '法则宗门', '祭司议会', '裂世反叛军', '其他')),
    description TEXT,
    hierarchy JSONB DEFAULT '{}', -- 组织架构
    ideology JSONB DEFAULT '{}', -- 理念信仰
    resources JSONB DEFAULT '{}', -- 资源实力
    territories JSONB DEFAULT '{}', -- 控制区域
    relationships JSONB DEFAULT '{}', -- 对外关系
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'declining', 'destroyed', 'reformed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_id, name)
);

-- =============================================================================
-- 法则链核心概念表
-- =============================================================================

-- 法则链表
CREATE TABLE IF NOT EXISTS law_chains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    chain_type VARCHAR(100) NOT NULL, -- 法则类型
    description TEXT,
    origin_story TEXT, -- 起源故事
    power_level INTEGER CHECK (power_level BETWEEN 1 AND 10),
    activation_conditions JSONB DEFAULT '{}',
    effects JSONB DEFAULT '{}',
    limitations JSONB DEFAULT '{}',
    corruption_risk INTEGER DEFAULT 0 CHECK (corruption_risk BETWEEN 0 AND 100),
    rarity VARCHAR(50) DEFAULT 'common' CHECK (rarity IN ('common', 'uncommon', 'rare', 'legendary', 'mythical')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_id, name)
);

-- 链痕表
CREATE TABLE IF NOT EXISTS chain_marks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    mark_type VARCHAR(100) NOT NULL,
    description TEXT,
    visual_description TEXT, -- 视觉描述
    associated_chain UUID REFERENCES law_chains(id),
    power_boost INTEGER DEFAULT 0,
    side_effects JSONB DEFAULT '{}',
    acquisition_method TEXT,
    removal_method TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_id, name)
);

-- =============================================================================
-- 索引创建
-- =============================================================================

-- 项目和小说索引
CREATE INDEX IF NOT EXISTS idx_novels_project_id ON novels(project_id);
CREATE INDEX IF NOT EXISTS idx_novels_status ON novels(status);

-- 批次管理索引
CREATE INDEX IF NOT EXISTS idx_content_batches_novel_id ON content_batches(novel_id);
CREATE INDEX IF NOT EXISTS idx_content_batches_status ON content_batches(status);
CREATE INDEX IF NOT EXISTS idx_content_batches_type ON content_batches(batch_type);
CREATE INDEX IF NOT EXISTS idx_content_segments_batch_id ON content_segments(batch_id);
CREATE INDEX IF NOT EXISTS idx_content_segments_sequence ON content_segments(batch_id, sequence_order);

-- 文本搜索索引
CREATE INDEX IF NOT EXISTS idx_content_segments_content_gin ON content_segments USING gin(to_tsvector('simple', content));
CREATE INDEX IF NOT EXISTS idx_content_segments_title_gin ON content_segments USING gin(to_tsvector('simple', title));

-- 世界观索引
CREATE INDEX IF NOT EXISTS idx_domains_novel_id ON domains(novel_id);
CREATE INDEX IF NOT EXISTS idx_cultivation_systems_novel_id ON cultivation_systems(novel_id);
CREATE INDEX IF NOT EXISTS idx_cultivation_stages_system_id ON cultivation_stages(system_id);
CREATE INDEX IF NOT EXISTS idx_power_organizations_novel_id ON power_organizations(novel_id);
CREATE INDEX IF NOT EXISTS idx_law_chains_novel_id ON law_chains(novel_id);
CREATE INDEX IF NOT EXISTS idx_chain_marks_novel_id ON chain_marks(novel_id);

-- JSON字段索引
CREATE INDEX IF NOT EXISTS idx_content_segments_metadata ON content_segments USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_domains_characteristics ON domains USING gin(characteristics);
CREATE INDEX IF NOT EXISTS idx_law_chains_effects ON law_chains USING gin(effects);

-- =============================================================================
-- 触发器函数
-- =============================================================================

-- 更新时间戳触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建更新时间戳触发器
CREATE OR REPLACE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_novels_updated_at BEFORE UPDATE ON novels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_content_batches_updated_at BEFORE UPDATE ON content_batches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_content_segments_updated_at BEFORE UPDATE ON content_segments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_domains_updated_at BEFORE UPDATE ON domains FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_cultivation_systems_updated_at BEFORE UPDATE ON cultivation_systems FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_cultivation_stages_updated_at BEFORE UPDATE ON cultivation_stages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_power_organizations_updated_at BEFORE UPDATE ON power_organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_law_chains_updated_at BEFORE UPDATE ON law_chains FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE OR REPLACE TRIGGER update_chain_marks_updated_at BEFORE UPDATE ON chain_marks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 字数统计触发器函数
CREATE OR REPLACE FUNCTION update_word_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.word_count = length(regexp_replace(NEW.content, '\s+', '', 'g'));
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_content_segments_word_count BEFORE INSERT OR UPDATE ON content_segments FOR EACH ROW EXECUTE FUNCTION update_word_count();

-- 批次字数统计更新函数
CREATE OR REPLACE FUNCTION update_batch_word_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE content_batches
    SET word_count = (
        SELECT COALESCE(SUM(word_count), 0)
        FROM content_segments
        WHERE batch_id = COALESCE(NEW.batch_id, OLD.batch_id)
    )
    WHERE id = COALESCE(NEW.batch_id, OLD.batch_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_batch_word_count_trigger AFTER INSERT OR UPDATE OR DELETE ON content_segments FOR EACH ROW EXECUTE FUNCTION update_batch_word_count();

-- 小说统计更新函数
CREATE OR REPLACE FUNCTION update_novel_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE novels
    SET
        word_count = (
            SELECT COALESCE(SUM(cb.word_count), 0)
            FROM content_batches cb
            WHERE cb.novel_id = COALESCE(NEW.novel_id, OLD.novel_id)
        ),
        chapter_count = (
            SELECT COUNT(*)
            FROM content_batches cb
            WHERE cb.novel_id = COALESCE(NEW.novel_id, OLD.novel_id)
            AND cb.batch_type IN ('plot', 'scenes')
        )
    WHERE id = COALESCE(NEW.novel_id, OLD.novel_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_novel_stats_trigger AFTER INSERT OR UPDATE OR DELETE ON content_batches FOR EACH ROW EXECUTE FUNCTION update_novel_stats();