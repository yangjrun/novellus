-- ==================================================================
-- pgvector扩展和向量存储基础设施
-- 适用于Novellus项目的完整向量数据库解决方案
-- ==================================================================

-- 开始事务以确保原子性
BEGIN;

-- ==================================================================
-- 1. 检查PostgreSQL版本兼容性和扩展安装
-- ==================================================================

-- 检查PostgreSQL版本 (需要11+支持pgvector)
DO $$
BEGIN
    IF current_setting('server_version_num')::int < 110000 THEN
        RAISE EXCEPTION 'pgvector requires PostgreSQL 11 or higher. Current version: %',
            current_setting('server_version');
    END IF;
    RAISE NOTICE 'PostgreSQL version check passed: %', current_setting('server_version');
END $$;

-- 安装pgvector扩展
-- 注意：在生产环境中，可能需要预先安装pgvector包
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS btree_gist;  -- 用于复合索引
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- 用于文本相似度搜索

-- 验证扩展安装
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE EXCEPTION 'pgvector extension is not available. Please install pgvector package first.';
    END IF;
    RAISE NOTICE 'pgvector extension installed successfully';
END $$;

-- ==================================================================
-- 2. 数据库性能优化配置
-- ==================================================================

-- 设置向量操作的内存参数
-- 这些设置应该在postgresql.conf中配置，但我们在这里设置会话级别的参数
SET maintenance_work_mem = '2GB';  -- 用于索引构建
SET work_mem = '256MB';            -- 用于向量搜索
SET effective_cache_size = '4GB';   -- 系统缓存估计

-- 向量搜索相关参数
SET ivfflat.probes = 10;           -- IVFFLAT索引探测数量，影响召回率和性能

-- ==================================================================
-- 3. 创建向量存储表结构
-- ==================================================================

-- 3.1 内容嵌入表 (支持1536维向量)
CREATE TABLE IF NOT EXISTS content_embeddings (
    id BIGSERIAL PRIMARY KEY,
    content_id UUID NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'text',  -- text, image, audio, etc.
    content_hash VARCHAR(64) NOT NULL,  -- SHA-256哈希，用于去重
    content_text TEXT,  -- 原始文本内容
    content_metadata JSONB DEFAULT '{}',  -- 内容元数据
    embedding vector(1536) NOT NULL,  -- OpenAI ada-002嵌入向量
    model_name VARCHAR(100) NOT NULL DEFAULT 'text-embedding-ada-002',
    embedding_version INTEGER NOT NULL DEFAULT 1,

    -- 法则链系统集成
    novel_id UUID,  -- 关联到小说
    chain_id UUID,  -- 关联到法则链定义
    character_id UUID,  -- 关联到角色
    scene_id UUID,  -- 关联到场景

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 确保内容哈希唯一性
    CONSTRAINT unique_content_hash UNIQUE (content_hash, model_name, embedding_version),

    -- 检查向量维度
    CONSTRAINT check_embedding_dimension CHECK (vector_dims(embedding) = 1536),

    -- 内容类型检查
    CONSTRAINT check_content_type CHECK (content_type IN ('text', 'image', 'audio', 'video', 'document', 'law_chain', 'character', 'scene', 'dialogue'))
);

-- 添加表注释
COMMENT ON TABLE content_embeddings IS '内容嵌入向量存储表，支持多模态内容的1536维向量存储';
COMMENT ON COLUMN content_embeddings.embedding IS '1536维向量，兼容OpenAI text-embedding-ada-002模型';
COMMENT ON COLUMN content_embeddings.content_hash IS 'SHA-256内容哈希，用于去重和快速查找';

-- 3.2 语义缓存表
CREATE TABLE IF NOT EXISTS semantic_cache (
    id BIGSERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) NOT NULL,  -- 查询哈希
    query_embedding vector(1536) NOT NULL,  -- 查询向量
    response_data JSONB NOT NULL,  -- 缓存的响应数据
    response_metadata JSONB DEFAULT '{}',  -- 响应元数据
    similarity_threshold FLOAT DEFAULT 0.8,  -- 相似度阈值
    hit_count INTEGER DEFAULT 0,  -- 缓存命中次数
    last_hit_at TIMESTAMP WITH TIME ZONE,  -- 最后命中时间
    expires_at TIMESTAMP WITH TIME ZONE,  -- 缓存过期时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 查询哈希唯一性
    CONSTRAINT unique_query_hash UNIQUE (query_hash),

    -- 检查向量维度
    CONSTRAINT check_query_embedding_dimension CHECK (vector_dims(query_embedding) = 1536),

    -- 相似度阈值范围检查
    CONSTRAINT check_similarity_threshold CHECK (similarity_threshold >= 0 AND similarity_threshold <= 1)
);

COMMENT ON TABLE semantic_cache IS '语义缓存表，基于向量相似度的智能缓存系统';
COMMENT ON COLUMN semantic_cache.query_embedding IS '查询文本的1536维向量表示';
COMMENT ON COLUMN semantic_cache.similarity_threshold IS '语义相似度阈值，用于缓存匹配';

-- 3.3 法则链语义映射表 (针对法则链系统优化)
CREATE TABLE IF NOT EXISTS law_chain_embeddings (
    id BIGSERIAL PRIMARY KEY,
    chain_id UUID NOT NULL,  -- 关联到law_chain_definitions
    chain_description_embedding vector(1536),  -- 法则链描述向量
    chain_abilities_embedding vector(1536),    -- 法则链能力向量
    chain_combination_embedding vector(1536),  -- 组合兼容性向量

    -- 组合特征向量
    domain_preference_vector vector(4),         -- 四域偏好向量[人域,天域,灵域,荒域]
    cost_risk_vector vector(5),                 -- 代价风险向量[因果债,寿债,污染,链疲劳,正当性风险]

    -- 语义标签
    semantic_tags TEXT[],                       -- 语义标签数组

    -- 相似度阈值
    similarity_thresholds JSONB DEFAULT '{
        "description": 0.8,
        "abilities": 0.7,
        "combination": 0.75,
        "domain": 0.6,
        "cost_risk": 0.65
    }',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(chain_id)
);

COMMENT ON TABLE law_chain_embeddings IS '法则链专用向量表，支持多维度语义相似度匹配';

-- 3.4 角色语义档案表
CREATE TABLE IF NOT EXISTS character_semantic_profiles (
    id BIGSERIAL PRIMARY KEY,
    character_id UUID NOT NULL,

    -- 角色特征向量
    personality_embedding vector(1536),         -- 性格特征向量
    skill_preference_embedding vector(1536),    -- 技能偏好向量
    decision_pattern_embedding vector(1536),    -- 决策模式向量

    -- 法则链亲和度向量
    chain_affinity_vector vector(12),           -- 对12种法则链的亲和度

    -- 行为模式向量
    behavior_patterns JSONB DEFAULT '{}',

    -- 语义进化记录
    evolution_history JSONB DEFAULT '[]',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(character_id)
);

COMMENT ON TABLE character_semantic_profiles IS '角色语义档案表，用于角色行为和偏好的向量化分析';

-- 3.3 向量搜索日志表 (用于性能监控和优化)
CREATE TABLE IF NOT EXISTS vector_search_logs (
    id BIGSERIAL PRIMARY KEY,
    search_type VARCHAR(50) NOT NULL,  -- similarity, cache_lookup, etc.
    query_vector vector(1536),
    search_params JSONB DEFAULT '{}',  -- 搜索参数
    result_count INTEGER,
    execution_time_ms FLOAT,  -- 执行时间(毫秒)
    similarity_scores FLOAT[],  -- 相似度分数数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 搜索类型检查
    CONSTRAINT check_search_type CHECK (search_type IN ('similarity', 'cache_lookup', 'hybrid'))
);

COMMENT ON TABLE vector_search_logs IS '向量搜索性能监控日志表';

-- ==================================================================
-- 4. 创建向量索引 (IVFFLAT)
-- ==================================================================

-- 为content_embeddings创建IVFFLAT索引
-- lists参数设置为行数的平方根，适合中等规模数据集
CREATE INDEX IF NOT EXISTS idx_content_embeddings_vector_cosine
ON content_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 为content_embeddings创建L2距离索引
CREATE INDEX IF NOT EXISTS idx_content_embeddings_vector_l2
ON content_embeddings USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- 为semantic_cache创建余弦相似度索引
CREATE INDEX IF NOT EXISTS idx_semantic_cache_vector_cosine
ON semantic_cache USING ivfflat (query_embedding vector_cosine_ops)
WITH (lists = 50);

-- 为law_chain_embeddings创建多维度向量索引
CREATE INDEX IF NOT EXISTS idx_law_chain_description_vector
ON law_chain_embeddings USING ivfflat (chain_description_embedding vector_cosine_ops)
WITH (lists = 30);

CREATE INDEX IF NOT EXISTS idx_law_chain_abilities_vector
ON law_chain_embeddings USING ivfflat (chain_abilities_embedding vector_cosine_ops)
WITH (lists = 30);

CREATE INDEX IF NOT EXISTS idx_law_chain_combination_vector
ON law_chain_embeddings USING ivfflat (chain_combination_embedding vector_cosine_ops)
WITH (lists = 30);

-- 为character_semantic_profiles创建向量索引
CREATE INDEX IF NOT EXISTS idx_character_personality_vector
ON character_semantic_profiles USING ivfflat (personality_embedding vector_cosine_ops)
WITH (lists = 20);

CREATE INDEX IF NOT EXISTS idx_character_skill_vector
ON character_semantic_profiles USING ivfflat (skill_preference_embedding vector_cosine_ops)
WITH (lists = 20);

CREATE INDEX IF NOT EXISTS idx_character_decision_vector
ON character_semantic_profiles USING ivfflat (decision_pattern_embedding vector_cosine_ops)
WITH (lists = 20);

-- ==================================================================
-- 5. 创建常规索引优化查询性能
-- ==================================================================

-- content_embeddings表索引
CREATE INDEX IF NOT EXISTS idx_content_embeddings_content_id ON content_embeddings(content_id);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_content_type ON content_embeddings(content_type);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_content_hash ON content_embeddings(content_hash);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_model_name ON content_embeddings(model_name);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_created_at ON content_embeddings(created_at);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_metadata ON content_embeddings USING gin(content_metadata);

-- 法则链系统集成索引
CREATE INDEX IF NOT EXISTS idx_content_embeddings_novel_id ON content_embeddings(novel_id);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_chain_id ON content_embeddings(chain_id);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_character_id ON content_embeddings(character_id);
CREATE INDEX IF NOT EXISTS idx_content_embeddings_scene_id ON content_embeddings(scene_id);

-- law_chain_embeddings表索引
CREATE INDEX IF NOT EXISTS idx_law_chain_embeddings_chain_id ON law_chain_embeddings(chain_id);
CREATE INDEX IF NOT EXISTS idx_law_chain_embeddings_tags ON law_chain_embeddings USING gin(semantic_tags);

-- character_semantic_profiles表索引
CREATE INDEX IF NOT EXISTS idx_character_semantic_character_id ON character_semantic_profiles(character_id);
CREATE INDEX IF NOT EXISTS idx_character_semantic_patterns ON character_semantic_profiles USING gin(behavior_patterns);

-- semantic_cache表索引
CREATE INDEX IF NOT EXISTS idx_semantic_cache_query_hash ON semantic_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_semantic_cache_expires_at ON semantic_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_semantic_cache_hit_count ON semantic_cache(hit_count DESC);
CREATE INDEX IF NOT EXISTS idx_semantic_cache_last_hit_at ON semantic_cache(last_hit_at);

-- vector_search_logs表索引
CREATE INDEX IF NOT EXISTS idx_vector_search_logs_search_type ON vector_search_logs(search_type);
CREATE INDEX IF NOT EXISTS idx_vector_search_logs_created_at ON vector_search_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_vector_search_logs_execution_time ON vector_search_logs(execution_time_ms);

-- ==================================================================
-- 6. 创建向量搜索Helper函数
-- ==================================================================

-- 6.1 余弦相似度搜索函数
CREATE OR REPLACE FUNCTION search_similar_content(
    query_embedding vector(1536),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10,
    content_type_filter VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    content_id UUID,
    content_text TEXT,
    content_metadata JSONB,
    similarity_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ce.content_id,
        ce.content_text,
        ce.content_metadata,
        1 - (ce.embedding <=> query_embedding) AS similarity_score,
        ce.created_at
    FROM content_embeddings ce
    WHERE
        (content_type_filter IS NULL OR ce.content_type = content_type_filter)
        AND 1 - (ce.embedding <=> query_embedding) >= similarity_threshold
    ORDER BY ce.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_similar_content IS '基于余弦相似度的内容搜索函数';

-- 6.2 语义缓存查找函数
CREATE OR REPLACE FUNCTION search_semantic_cache(
    input_embedding vector(1536),
    similarity_threshold FLOAT DEFAULT 0.85
)
RETURNS TABLE (
    cache_id BIGINT,
    query_text TEXT,
    response_data JSONB,
    similarity_score FLOAT,
    hit_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sc.id,
        sc.query_text,
        sc.response_data,
        1 - (sc.query_embedding <=> input_embedding) AS similarity_score,
        sc.hit_count
    FROM semantic_cache sc
    WHERE
        (sc.expires_at IS NULL OR sc.expires_at > CURRENT_TIMESTAMP)
        AND 1 - (sc.query_embedding <=> input_embedding) >= similarity_threshold
    ORDER BY sc.query_embedding <=> input_embedding
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_semantic_cache IS '语义缓存查找函数，基于向量相似度匹配缓存项';

-- 6.3 批量向量搜索函数
CREATE OR REPLACE FUNCTION batch_similarity_search(
    query_embeddings vector(1536)[],
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results_per_query INTEGER DEFAULT 5
)
RETURNS TABLE (
    query_index INTEGER,
    content_id UUID,
    content_text TEXT,
    similarity_score FLOAT
) AS $$
DECLARE
    query_emb vector(1536);
    idx INTEGER := 1;
BEGIN
    FOREACH query_emb IN ARRAY query_embeddings
    LOOP
        RETURN QUERY
        SELECT
            idx AS query_index,
            ce.content_id,
            ce.content_text,
            1 - (ce.embedding <=> query_emb) AS similarity_score
        FROM content_embeddings ce
        WHERE 1 - (ce.embedding <=> query_emb) >= similarity_threshold
        ORDER BY ce.embedding <=> query_emb
        LIMIT max_results_per_query;

        idx := idx + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION batch_similarity_search IS '批量向量相似度搜索函数';

-- 6.4 法则链语义搜索函数
CREATE OR REPLACE FUNCTION search_similar_law_chains(
    query_embedding vector(1536),
    search_type VARCHAR DEFAULT 'description',  -- description, abilities, combination
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10,
    novel_id_filter UUID DEFAULT NULL
)
RETURNS TABLE (
    chain_id UUID,
    similarity_score FLOAT,
    semantic_tags TEXT[],
    chain_name VARCHAR,
    chain_category VARCHAR
) AS $$
DECLARE
    embedding_column TEXT;
    threshold_key TEXT;
    actual_threshold FLOAT;
BEGIN
    -- 根据搜索类型选择向量列
    CASE search_type
        WHEN 'description' THEN
            embedding_column := 'chain_description_embedding';
            threshold_key := 'description';
        WHEN 'abilities' THEN
            embedding_column := 'chain_abilities_embedding';
            threshold_key := 'abilities';
        WHEN 'combination' THEN
            embedding_column := 'chain_combination_embedding';
            threshold_key := 'combination';
        ELSE
            RAISE EXCEPTION 'Invalid search_type. Must be description, abilities, or combination';
    END CASE;

    RETURN QUERY EXECUTE format('
        SELECT
            lce.chain_id,
            1 - (lce.%I <=> $1) AS similarity_score,
            lce.semantic_tags,
            NULL::VARCHAR as chain_name,
            NULL::VARCHAR as chain_category
        FROM law_chain_embeddings lce
        WHERE
            lce.%I IS NOT NULL
            AND 1 - (lce.%I <=> $1) >= COALESCE(
                (lce.similarity_thresholds->>$3)::FLOAT,
                $2
            )
        ORDER BY lce.%I <=> $1
        LIMIT $4',
        embedding_column, embedding_column, embedding_column, embedding_column
    ) USING query_embedding, similarity_threshold, threshold_key, max_results;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_similar_law_chains IS '法则链多维度语义搜索函数';

-- 6.5 角色行为预测函数
CREATE OR REPLACE FUNCTION predict_character_behavior(
    target_character_id UUID,
    situation_embedding vector(1536),
    similarity_threshold FLOAT DEFAULT 0.75,
    prediction_type VARCHAR DEFAULT 'personality'  -- personality, skill, decision
)
RETURNS TABLE (
    similar_character_id UUID,
    similarity_score FLOAT,
    predicted_behavior JSONB,
    confidence_level FLOAT
) AS $$
DECLARE
    embedding_column TEXT;
BEGIN
    -- 根据预测类型选择向量列
    CASE prediction_type
        WHEN 'personality' THEN
            embedding_column := 'personality_embedding';
        WHEN 'skill' THEN
            embedding_column := 'skill_preference_embedding';
        WHEN 'decision' THEN
            embedding_column := 'decision_pattern_embedding';
        ELSE
            RAISE EXCEPTION 'Invalid prediction_type. Must be personality, skill, or decision';
    END CASE;

    RETURN QUERY EXECUTE format('
        SELECT
            csp.character_id,
            1 - (csp.%I <=> $1) AS similarity_score,
            csp.behavior_patterns,
            CASE
                WHEN 1 - (csp.%I <=> $1) >= 0.9 THEN 0.95::FLOAT
                WHEN 1 - (csp.%I <=> $1) >= 0.8 THEN 0.85::FLOAT
                WHEN 1 - (csp.%I <=> $1) >= 0.7 THEN 0.75::FLOAT
                ELSE 0.6::FLOAT
            END AS confidence_level
        FROM character_semantic_profiles csp
        WHERE
            csp.character_id != $2
            AND csp.%I IS NOT NULL
            AND 1 - (csp.%I <=> $1) >= $3
        ORDER BY csp.%I <=> $1
        LIMIT 5',
        embedding_column, embedding_column, embedding_column, embedding_column,
        embedding_column, embedding_column, embedding_column
    ) USING situation_embedding, target_character_id, similarity_threshold;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION predict_character_behavior IS '基于语义相似度的角色行为预测函数';

-- 6.6 法则链组合推荐函数
CREATE OR REPLACE FUNCTION recommend_chain_combinations(
    character_id_input UUID,
    target_effect_embedding vector(1536),
    max_combinations INTEGER DEFAULT 5,
    risk_tolerance FLOAT DEFAULT 0.7  -- 0-1, 1表示可接受高风险
)
RETURNS TABLE (
    chain_ids UUID[],
    combination_name VARCHAR,
    effectiveness_score FLOAT,
    risk_score FLOAT,
    recommendation_reason TEXT
) AS $$
BEGIN
    -- 简化版本的推荐逻辑，基于现有的向量数据
    RETURN QUERY
    SELECT
        ARRAY[lce.chain_id] as chain_ids,
        'Auto Generated Combination'::VARCHAR as combination_name,
        COALESCE(
            1 - (lce.chain_combination_embedding <=> target_effect_embedding),
            0.5
        ) as effectiveness_score,
        0.5::FLOAT as risk_score,
        CASE
            WHEN COALESCE(1 - (lce.chain_combination_embedding <=> target_effect_embedding), 0) >= 0.8
            THEN '高度匹配目标效果'
            ELSE '中等匹配度'
        END as recommendation_reason
    FROM law_chain_embeddings lce
    WHERE
        lce.chain_combination_embedding IS NOT NULL
        AND COALESCE(1 - (lce.chain_combination_embedding <=> target_effect_embedding), 0) >= 0.3
    ORDER BY
        COALESCE(1 - (lce.chain_combination_embedding <=> target_effect_embedding), 0) DESC
    LIMIT max_combinations;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION recommend_chain_combinations IS '基于目标效果和风险承受度的法则链组合推荐函数';

-- 6.4 更新缓存命中计数函数
CREATE OR REPLACE FUNCTION update_cache_hit(cache_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE semantic_cache
    SET
        hit_count = hit_count + 1,
        last_hit_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = cache_id;
END;
$$ LANGUAGE plpgsql;

-- 6.5 清理过期缓存函数
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM semantic_cache
    WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ==================================================================
-- 7. 创建触发器和自动化维护
-- ==================================================================

-- 7.1 自动更新时间戳触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为各表创建更新时间戳触发器
CREATE TRIGGER update_content_embeddings_updated_at
    BEFORE UPDATE ON content_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_semantic_cache_updated_at
    BEFORE UPDATE ON semantic_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 7.2 向量搜索日志记录触发器函数
CREATE OR REPLACE FUNCTION log_vector_search()
RETURNS TRIGGER AS $$
BEGIN
    -- 这里可以添加搜索日志记录逻辑
    -- 实际使用中建议在应用层记录以避免性能影响
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==================================================================
-- 8. 创建视图和统计信息
-- ==================================================================

-- 8.1 内容统计视图
CREATE OR REPLACE VIEW content_statistics AS
SELECT
    content_type,
    model_name,
    COUNT(*) as total_embeddings,
    AVG(LENGTH(content_text)) as avg_text_length,
    MIN(created_at) as earliest_created,
    MAX(created_at) as latest_created
FROM content_embeddings
GROUP BY content_type, model_name;

COMMENT ON VIEW content_statistics IS '内容嵌入统计信息视图';

-- 8.2 缓存性能视图
CREATE OR REPLACE VIEW cache_performance AS
SELECT
    COUNT(*) as total_cache_entries,
    SUM(hit_count) as total_hits,
    AVG(hit_count) as avg_hits_per_entry,
    COUNT(CASE WHEN expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP THEN 1 END) as active_entries,
    COUNT(CASE WHEN expires_at IS NOT NULL AND expires_at <= CURRENT_TIMESTAMP THEN 1 END) as expired_entries
FROM semantic_cache;

COMMENT ON VIEW cache_performance IS '语义缓存性能统计视图';

-- 8.3 法则链向量统计视图（简化版本，不依赖外部表）
CREATE OR REPLACE VIEW law_chain_vector_statistics AS
SELECT
    COUNT(*) as total_chain_embeddings,
    COUNT(chain_description_embedding) as description_embeddings,
    COUNT(chain_abilities_embedding) as abilities_embeddings,
    COUNT(chain_combination_embedding) as combination_embeddings,
    AVG(array_length(semantic_tags, 1)) as avg_semantic_tags,
    MIN(created_at) as earliest_embedding,
    MAX(created_at) as latest_embedding
FROM law_chain_embeddings;

COMMENT ON VIEW law_chain_vector_statistics IS '法则链向量化统计信息视图';

-- 8.4 角色语义档案统计视图
CREATE OR REPLACE VIEW character_semantic_statistics AS
SELECT
    COUNT(*) as total_profiles,
    COUNT(personality_embedding) as personality_embeddings,
    COUNT(skill_preference_embedding) as skill_embeddings,
    COUNT(decision_pattern_embedding) as decision_embeddings,
    AVG(vector_dims(chain_affinity_vector)) as avg_chain_affinities,
    COUNT(CASE WHEN behavior_patterns != '{}' THEN 1 END) as profiles_with_patterns
FROM character_semantic_profiles;

COMMENT ON VIEW character_semantic_statistics IS '角色语义档案统计信息视图';

-- 8.5 向量搜索性能视图
CREATE OR REPLACE VIEW vector_search_performance AS
SELECT
    search_type,
    COUNT(*) as total_searches,
    AVG(execution_time_ms) as avg_execution_time,
    MIN(execution_time_ms) as min_execution_time,
    MAX(execution_time_ms) as max_execution_time,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY execution_time_ms) as median_execution_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) as p95_execution_time,
    AVG(result_count) as avg_results_per_search
FROM vector_search_logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY search_type;

COMMENT ON VIEW vector_search_performance IS '向量搜索性能分析视图（最近7天）';

-- ==================================================================
-- 9. 性能测试查询示例
-- ==================================================================

-- 创建性能测试函数
CREATE OR REPLACE FUNCTION run_vector_performance_test(
    test_vector vector(1536) DEFAULT NULL,
    num_iterations INTEGER DEFAULT 100
)
RETURNS TABLE (
    test_name TEXT,
    avg_execution_time_ms FLOAT,
    min_execution_time_ms FLOAT,
    max_execution_time_ms FLOAT,
    iterations INTEGER
) AS $$
DECLARE
    test_embedding vector(1536);
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    execution_times FLOAT[] := '{}';
    exec_time FLOAT;
    i INTEGER;
BEGIN
    -- 使用提供的向量或生成随机测试向量
    IF test_vector IS NULL THEN
        test_embedding := (SELECT embedding FROM content_embeddings LIMIT 1);
    ELSE
        test_embedding := test_vector;
    END IF;

    -- 如果仍然没有向量，跳过测试
    IF test_embedding IS NULL THEN
        RETURN QUERY SELECT 'No test data available'::TEXT, 0::FLOAT, 0::FLOAT, 0::FLOAT, 0;
        RETURN;
    END IF;

    -- 测试余弦相似度搜索
    FOR i IN 1..num_iterations LOOP
        start_time := clock_timestamp();

        PERFORM * FROM search_similar_content(test_embedding, 0.7, 10);

        end_time := clock_timestamp();
        exec_time := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
        execution_times := execution_times || exec_time;
    END LOOP;

    RETURN QUERY SELECT
        'Cosine Similarity Search'::TEXT,
        (SELECT AVG(unnest) FROM unnest(execution_times)),
        (SELECT MIN(unnest) FROM unnest(execution_times)),
        (SELECT MAX(unnest) FROM unnest(execution_times)),
        num_iterations;

    -- 重置执行时间数组
    execution_times := '{}';

    -- 测试语义缓存搜索
    FOR i IN 1..num_iterations LOOP
        start_time := clock_timestamp();

        PERFORM * FROM search_semantic_cache(test_embedding, 0.85);

        end_time := clock_timestamp();
        exec_time := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
        execution_times := execution_times || exec_time;
    END LOOP;

    RETURN QUERY SELECT
        'Semantic Cache Lookup'::TEXT,
        (SELECT AVG(unnest) FROM unnest(execution_times)),
        (SELECT MIN(unnest) FROM unnest(execution_times)),
        (SELECT MAX(unnest) FROM unnest(execution_times)),
        num_iterations;

    -- 重置执行时间数组
    execution_times := '{}';

    -- 测试法则链语义搜索（如果有数据）
    IF EXISTS (SELECT 1 FROM law_chain_embeddings LIMIT 1) THEN
        FOR i IN 1..num_iterations LOOP
            start_time := clock_timestamp();

            PERFORM * FROM search_similar_law_chains(test_embedding, 'description', 0.7, 5);

            end_time := clock_timestamp();
            exec_time := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
            execution_times := execution_times || exec_time;
        END LOOP;

        RETURN QUERY SELECT
            'Law Chain Semantic Search'::TEXT,
            (SELECT AVG(unnest) FROM unnest(execution_times)),
            (SELECT MIN(unnest) FROM unnest(execution_times)),
            (SELECT MAX(unnest) FROM unnest(execution_times)),
            num_iterations;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION run_vector_performance_test IS '向量搜索性能测试函数';

-- ==================================================================
-- 10. 数据维护和清理程序
-- ==================================================================

-- 10.1 重建向量索引函数 (用于性能优化)
CREATE OR REPLACE FUNCTION rebuild_vector_indexes()
RETURNS TEXT AS $$
DECLARE
    content_count INTEGER;
    cache_count INTEGER;
    chain_count INTEGER;
BEGIN
    -- 计算记录数量
    SELECT COUNT(*) INTO content_count FROM content_embeddings;
    SELECT COUNT(*) INTO cache_count FROM semantic_cache;
    SELECT COUNT(*) INTO chain_count FROM law_chain_embeddings;

    -- 重建content_embeddings向量索引
    DROP INDEX IF EXISTS idx_content_embeddings_vector_cosine;
    DROP INDEX IF EXISTS idx_content_embeddings_vector_l2;

    EXECUTE format('CREATE INDEX idx_content_embeddings_vector_cosine
        ON content_embeddings USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = %s)', GREATEST(10, content_count / 1000));

    EXECUTE format('CREATE INDEX idx_content_embeddings_vector_l2
        ON content_embeddings USING ivfflat (embedding vector_l2_ops)
        WITH (lists = %s)', GREATEST(10, content_count / 1000));

    -- 重建semantic_cache向量索引
    DROP INDEX IF EXISTS idx_semantic_cache_vector_cosine;

    EXECUTE format('CREATE INDEX idx_semantic_cache_vector_cosine
        ON semantic_cache USING ivfflat (query_embedding vector_cosine_ops)
        WITH (lists = %s)', GREATEST(10, cache_count / 1000));

    -- 重建law_chain_embeddings向量索引
    DROP INDEX IF EXISTS idx_law_chain_description_vector;
    DROP INDEX IF EXISTS idx_law_chain_abilities_vector;
    DROP INDEX IF EXISTS idx_law_chain_combination_vector;

    EXECUTE format('CREATE INDEX idx_law_chain_description_vector
        ON law_chain_embeddings USING ivfflat (chain_description_embedding vector_cosine_ops)
        WITH (lists = %s)', GREATEST(10, chain_count / 100));

    EXECUTE format('CREATE INDEX idx_law_chain_abilities_vector
        ON law_chain_embeddings USING ivfflat (chain_abilities_embedding vector_cosine_ops)
        WITH (lists = %s)', GREATEST(10, chain_count / 100));

    EXECUTE format('CREATE INDEX idx_law_chain_combination_vector
        ON law_chain_embeddings USING ivfflat (chain_combination_embedding vector_cosine_ops)
        WITH (lists = %s)', GREATEST(10, chain_count / 100));

    RETURN 'Vector indexes rebuilt successfully';
END;
$$ LANGUAGE plpgsql;

-- 10.2 数据库统计信息更新函数
CREATE OR REPLACE FUNCTION update_vector_statistics()
RETURNS TEXT AS $$
BEGIN
    ANALYZE content_embeddings;
    ANALYZE semantic_cache;
    ANALYZE vector_search_logs;

    RETURN 'Vector table statistics updated successfully';
END;
$$ LANGUAGE plpgsql;

-- ==================================================================
-- 11. 错误处理和回滚方案
-- ==================================================================

-- 创建回滚函数（慎用！）
CREATE OR REPLACE FUNCTION rollback_pgvector_setup()
RETURNS TEXT AS $$
BEGIN
    -- 警告信息
    RAISE NOTICE 'WARNING: This will remove all pgvector related tables and data!';

    -- 删除表（注意依赖关系）
    DROP VIEW IF EXISTS content_statistics CASCADE;
    DROP VIEW IF EXISTS cache_performance CASCADE;

    DROP TABLE IF EXISTS vector_search_logs CASCADE;
    DROP TABLE IF EXISTS semantic_cache CASCADE;
    DROP TABLE IF EXISTS content_embeddings CASCADE;

    -- 删除函数
    DROP FUNCTION IF EXISTS search_similar_content CASCADE;
    DROP FUNCTION IF EXISTS search_semantic_cache CASCADE;
    DROP FUNCTION IF EXISTS batch_similarity_search CASCADE;
    DROP FUNCTION IF EXISTS update_cache_hit CASCADE;
    DROP FUNCTION IF EXISTS cleanup_expired_cache CASCADE;
    DROP FUNCTION IF EXISTS run_vector_performance_test CASCADE;
    DROP FUNCTION IF EXISTS rebuild_vector_indexes CASCADE;
    DROP FUNCTION IF EXISTS update_vector_statistics CASCADE;
    DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
    DROP FUNCTION IF EXISTS log_vector_search CASCADE;

    RETURN 'pgvector setup rolled back successfully';
END;
$$ LANGUAGE plpgsql;

-- ==================================================================
-- 12. 初始化和验证
-- ==================================================================

-- 验证安装
DO $$
DECLARE
    table_count INTEGER;
    function_count INTEGER;
    index_count INTEGER;
BEGIN
    -- 检查表创建
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_name IN ('content_embeddings', 'semantic_cache', 'vector_search_logs', 'law_chain_embeddings', 'character_semantic_profiles');

    -- 检查函数创建
    SELECT COUNT(*) INTO function_count
    FROM information_schema.routines
    WHERE routine_name IN ('search_similar_content', 'search_semantic_cache', 'batch_similarity_search', 'search_similar_law_chains', 'predict_character_behavior', 'recommend_chain_combinations');

    -- 检查索引创建
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE indexname LIKE 'idx_%vector%';

    RAISE NOTICE 'Installation verification:';
    RAISE NOTICE 'Tables created: % (expected: 5)', table_count;
    RAISE NOTICE 'Functions created: % (expected: >= 6)', function_count;
    RAISE NOTICE 'Vector indexes created: % (expected: >= 8)', index_count;

    IF table_count = 5 AND function_count >= 6 AND index_count >= 8 THEN
        RAISE NOTICE 'pgvector setup with law chain integration completed successfully!';
    ELSE
        RAISE WARNING 'pgvector setup may be incomplete. Please check the logs above.';
    END IF;
END $$;

-- 提交事务
COMMIT;

-- ==================================================================
-- 使用示例和性能测试
-- ==================================================================

-- 示例：插入测试数据
/*
-- 1. 插入内容嵌入数据
INSERT INTO content_embeddings (content_id, content_type, content_hash, content_text, embedding, content_metadata, novel_id, chain_id)
VALUES
    (gen_random_uuid(), 'law_chain', 'hash1', '命运链能够预见并操控概率和命运走向', '[0.1,0.2,0.3,...]'::vector, '{"category": "命运"}', gen_random_uuid(), gen_random_uuid()),
    (gen_random_uuid(), 'character', 'hash2', '沉着冷静的分析型角色，偏好逻辑推理', '[0.2,0.3,0.4,...]'::vector, '{"type": "protagonist"}', gen_random_uuid(), NULL);

-- 2. 插入法则链语义映射数据
INSERT INTO law_chain_embeddings (chain_id, chain_description_embedding, chain_abilities_embedding, semantic_tags)
VALUES
    (gen_random_uuid(), '[0.1,0.2,0.3,...]'::vector, '[0.2,0.3,0.4,...]'::vector, ARRAY['fate', 'probability', 'prediction']),
    (gen_random_uuid(), '[0.3,0.4,0.5,...]'::vector, '[0.4,0.5,0.6,...]'::vector, ARRAY['causality', 'logic', 'consequence']);

-- 3. 插入角色语义档案数据
INSERT INTO character_semantic_profiles (character_id, personality_embedding, chain_affinity_vector)
VALUES
    (gen_random_uuid(), '[0.1,0.2,0.3,...]'::vector, '[0.8,0.3,0.6,0.2,0.1,0.9,0.4,0.7,0.5,0.3,0.8,0.6]'::vector),
    (gen_random_uuid(), '[0.2,0.3,0.4,...]'::vector, '[0.2,0.9,0.4,0.8,0.6,0.3,0.7,0.1,0.5,0.8,0.2,0.9]'::vector);

-- 4. 基础向量搜索示例
SELECT * FROM search_similar_content('[0.1,0.2,0.3,...]'::vector, 0.7, 5);

-- 5. 法则链语义搜索示例
SELECT * FROM search_similar_law_chains('[0.1,0.2,0.3,...]'::vector, 'description', 0.7, 5);

-- 6. 角色行为预测示例
SELECT * FROM predict_character_behavior(gen_random_uuid(), '[0.1,0.2,0.3,...]'::vector, 0.75, 'personality');

-- 7. 法则链组合推荐示例
SELECT * FROM recommend_chain_combinations(gen_random_uuid(), '[0.1,0.2,0.3,...]'::vector, 5, 0.7);

-- 8. 性能测试
SELECT * FROM run_vector_performance_test();

-- 9. 统计信息查看
SELECT * FROM content_statistics;
SELECT * FROM cache_performance;
SELECT * FROM law_chain_vector_statistics;
SELECT * FROM character_semantic_statistics;
SELECT * FROM vector_search_performance;

-- 10. 维护操作
SELECT cleanup_expired_cache();
SELECT update_vector_statistics();
SELECT rebuild_vector_indexes();
*/

-- 脚本完成提示
\echo 'pgvector extension and vector storage infrastructure setup completed!'
\echo 'Tables created: content_embeddings, semantic_cache, vector_search_logs, law_chain_embeddings, character_semantic_profiles'
\echo 'Vector indexes: IVFFLAT indexes for cosine similarity and L2 distance across all vector columns'
\echo 'Helper functions: search_similar_content, search_semantic_cache, batch_similarity_search'
\echo 'Law chain functions: search_similar_law_chains, predict_character_behavior, recommend_chain_combinations'
\echo 'Performance monitoring: vector_search_logs table and comprehensive performance test functions'
\echo 'Statistics views: content_statistics, cache_performance, law_chain_vector_statistics, character_semantic_statistics'
\echo 'Use SELECT * FROM run_vector_performance_test(); to run comprehensive performance tests'
\echo 'Law chain integration ready for semantic search and AI-powered recommendations!'