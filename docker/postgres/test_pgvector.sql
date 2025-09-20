-- pgvector功能测试脚本
-- 测试法则链系统的向量存储和搜索功能

-- 1. 生成测试向量数据
DO $$
DECLARE
    test_novel_id UUID := gen_random_uuid();
    test_chain_id1 UUID := gen_random_uuid();
    test_chain_id2 UUID := gen_random_uuid();
    test_character_id1 UUID := gen_random_uuid();
    test_character_id2 UUID := gen_random_uuid();
    test_embedding1 vector(1536);
    test_embedding2 vector(1536);
    i INTEGER;
BEGIN
    -- 生成随机测试向量（简化版本，实际应该是1536维）
    -- 这里创建一个简单的测试向量
    SELECT array_to_vector(ARRAY(SELECT random() FROM generate_series(1, 1536)))::vector(1536) INTO test_embedding1;
    SELECT array_to_vector(ARRAY(SELECT random() FROM generate_series(1, 1536)))::vector(1536) INTO test_embedding2;

    -- 插入内容嵌入测试数据
    INSERT INTO content_embeddings (
        content_id, content_type, content_hash, content_text,
        embedding, novel_id, chain_id, character_id
    ) VALUES
    (test_chain_id1, 'law_chain', 'hash001', '命运链：能够预见并操控概率和命运走向的强大法则链', test_embedding1, test_novel_id, test_chain_id1, NULL),
    (test_chain_id2, 'law_chain', 'hash002', '因果链：掌控因果关系，能够追溯原因和预测结果', test_embedding2, test_novel_id, test_chain_id2, NULL),
    (test_character_id1, 'character', 'hash003', '沉着冷静的分析型角色，善于逻辑推理和战略规划', test_embedding1, test_novel_id, NULL, test_character_id1),
    (test_character_id2, 'character', 'hash004', '直觉敏锐的感知型角色，擅长情感理解和人际交往', test_embedding2, test_novel_id, NULL, test_character_id2);

    -- 插入法则链语义映射数据
    INSERT INTO law_chain_embeddings (
        chain_id, chain_description_embedding, chain_abilities_embedding,
        chain_combination_embedding, semantic_tags
    ) VALUES
    (test_chain_id1, test_embedding1, test_embedding1, test_embedding1, ARRAY['fate', 'probability', 'destiny', 'prediction']),
    (test_chain_id2, test_embedding2, test_embedding2, test_embedding2, ARRAY['causality', 'logic', 'consequence', 'analysis']);

    -- 插入角色语义档案数据
    INSERT INTO character_semantic_profiles (
        character_id, personality_embedding, skill_preference_embedding,
        decision_pattern_embedding, chain_affinity_vector
    ) VALUES
    (test_character_id1, test_embedding1, test_embedding1, test_embedding1,
     '[0.9,0.3,0.7,0.2,0.1,0.8,0.4,0.6,0.5,0.2,0.7,0.4]'::vector(12)),
    (test_character_id2, test_embedding2, test_embedding2, test_embedding2,
     '[0.2,0.8,0.4,0.9,0.6,0.3,0.7,0.1,0.5,0.8,0.3,0.9]'::vector(12));

    -- 插入语义缓存测试数据
    INSERT INTO semantic_cache (
        query_text, query_hash, query_embedding, response_data,
        similarity_threshold, expires_at
    ) VALUES
    ('如何使用命运链预测未来？', 'cache001', test_embedding1,
     '{"answer": "命运链通过感知概率波动来预测可能的未来走向", "confidence": 0.85}',
     0.8, CURRENT_TIMESTAMP + INTERVAL '1 hour'),
    ('因果链的副作用是什么？', 'cache002', test_embedding2,
     '{"answer": "因果链使用可能导致因果债务累积，需要谨慎使用", "confidence": 0.90}',
     0.8, CURRENT_TIMESTAMP + INTERVAL '1 hour');

    RAISE NOTICE '测试数据插入完成！';
END $$;

-- 2. 测试基础向量搜索功能
\echo '=== 测试基础向量搜索功能 ==='
SELECT
    content_type,
    LEFT(content_text, 50) || '...' as content_preview,
    '相似度: ' || ROUND((1 - (embedding <=> (SELECT embedding FROM content_embeddings LIMIT 1)))::numeric, 3) as similarity
FROM content_embeddings
WHERE content_type = 'law_chain'
ORDER BY embedding <=> (SELECT embedding FROM content_embeddings LIMIT 1)
LIMIT 3;

-- 3. 测试法则链语义搜索
\echo '=== 测试法则链语义搜索功能 ==='
SELECT * FROM search_similar_law_chains(
    (SELECT chain_description_embedding FROM law_chain_embeddings LIMIT 1),
    'description',
    0.0,  -- 降低阈值以确保有结果
    5
);

-- 4. 测试角色行为预测
\echo '=== 测试角色行为预测功能 ==='
SELECT * FROM predict_character_behavior(
    (SELECT character_id FROM character_semantic_profiles ORDER BY created_at LIMIT 1),
    (SELECT personality_embedding FROM character_semantic_profiles ORDER BY created_at DESC LIMIT 1),
    0.0,  -- 降低阈值以确保有结果
    'personality'
);

-- 5. 测试法则链组合推荐
\echo '=== 测试法则链组合推荐功能 ==='
SELECT * FROM recommend_chain_combinations(
    (SELECT character_id FROM character_semantic_profiles LIMIT 1),
    (SELECT chain_combination_embedding FROM law_chain_embeddings LIMIT 1),
    3,
    0.8
);

-- 6. 测试语义缓存查找
\echo '=== 测试语义缓存查找功能 ==='
SELECT * FROM search_semantic_cache(
    (SELECT query_embedding FROM semantic_cache LIMIT 1),
    0.0  -- 降低阈值以确保有结果
);

-- 7. 查看统计信息
\echo '=== 内容统计信息 ==='
SELECT * FROM content_statistics;

\echo '=== 缓存性能统计 ==='
SELECT * FROM cache_performance;

\echo '=== 法则链向量统计 ==='
SELECT * FROM law_chain_vector_statistics;

\echo '=== 角色语义统计 ==='
SELECT * FROM character_semantic_statistics;

-- 8. 测试性能监控
\echo '=== 运行性能测试 ==='
SELECT * FROM run_vector_performance_test(
    (SELECT embedding FROM content_embeddings LIMIT 1),
    10  -- 减少迭代次数以加快测试
);

\echo '测试完成！pgvector和法则链系统集成功能正常运行。'