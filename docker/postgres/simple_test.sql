-- 简化的pgvector功能测试

-- 1. 测试基本向量功能
\echo '=== 测试向量类型 ==='
SELECT '[0.1,0.2,0.3]'::vector(3) as test_vector;

-- 2. 插入简单测试数据
\echo '=== 插入测试数据 ==='
INSERT INTO content_embeddings (content_id, content_type, content_hash, content_text, embedding)
VALUES
(gen_random_uuid(), 'test', 'test001', '测试内容1', array_fill(0.1, ARRAY[1536])::vector(1536)),
(gen_random_uuid(), 'test', 'test002', '测试内容2', array_fill(0.2, ARRAY[1536])::vector(1536));

-- 3. 测试向量相似度计算
\echo '=== 测试向量相似度 ==='
SELECT
    content_text,
    1 - (embedding <=> array_fill(0.15, ARRAY[1536])::vector(1536)) as similarity
FROM content_embeddings
WHERE content_type = 'test'
ORDER BY embedding <=> array_fill(0.15, ARRAY[1536])::vector(1536)
LIMIT 5;

-- 4. 测试search_similar_content函数
\echo '=== 测试相似内容搜索 ==='
SELECT * FROM search_similar_content(
    array_fill(0.15, ARRAY[1536])::vector(1536),
    0.0,
    5,
    'test'
);

-- 5. 查看统计信息
\echo '=== 内容统计 ==='
SELECT * FROM content_statistics;

\echo '测试完成！'