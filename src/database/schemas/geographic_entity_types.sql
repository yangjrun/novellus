-- =============================================================================
-- 地理实体类型表结构定义
-- 定义地理相关实体的数据结构和约束
-- =============================================================================

-- 注意：具体的地理实体类型数据和分类数据已移动到 default_data.sql 文件
-- 此处仅定义表结构、索引和约束

-- =============================================================================
-- 1. 地理实体相关的索引优化
-- =============================================================================

-- 为地理实体查询优化添加索引
CREATE INDEX IF NOT EXISTS idx_entities_geographic_type
    ON entities(novel_id, (attributes->>'geographic_type'))
    WHERE attributes ? 'geographic_type';

CREATE INDEX IF NOT EXISTS idx_entities_domain_code
    ON entities(novel_id, (attributes->>'domain_code'))
    WHERE attributes ? 'domain_code';

CREATE INDEX IF NOT EXISTS idx_entities_region_name
    ON entities(novel_id, (attributes->>'region_name'))
    WHERE attributes ? 'region_name';

-- 为人口规模查询优化
CREATE INDEX IF NOT EXISTS idx_entities_population_level
    ON entities(novel_id, (attributes->>'population_level'))
    WHERE attributes ? 'population_level';

-- 为行政等级查询优化
CREATE INDEX IF NOT EXISTS idx_entities_administrative_level
    ON entities(novel_id, (attributes->>'administrative_level'))
    WHERE attributes ? 'administrative_level';

-- =============================================================================
-- 2. 地理实体类型约束函数
-- =============================================================================

-- 验证地理实体属性的函数
CREATE OR REPLACE FUNCTION validate_geographic_entity(
    entity_type_name VARCHAR,
    attributes JSONB
) RETURNS BOOLEAN AS $$
BEGIN
    -- 根据实体类型验证必要字段
    CASE entity_type_name
        WHEN 'region' THEN
            RETURN attributes ? 'name' AND attributes ? 'note';
        WHEN 'city' THEN
            RETURN attributes ? 'name' AND attributes ? 'note';
        WHEN 'town' THEN
            RETURN attributes ? 'name' AND attributes ? 'note';
        WHEN 'village' THEN
            RETURN attributes ? 'name' AND attributes ? 'note';
        WHEN 'landmark' THEN
            RETURN attributes ? 'name' AND attributes ? 'note';
        WHEN 'building' THEN
            RETURN attributes ? 'name' AND attributes ? 'note' AND attributes ? 'building_type';
        WHEN 'natural_feature' THEN
            RETURN attributes ? 'name' AND attributes ? 'note' AND attributes ? 'feature_type';
        WHEN 'infrastructure' THEN
            RETURN attributes ? 'name' AND attributes ? 'note' AND attributes ? 'infrastructure_type';
        ELSE
            RETURN TRUE; -- 对于未知类型，暂不验证
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 3. 地理实体关系的辅助视图
-- =============================================================================

-- 地理层级关系视图
CREATE OR REPLACE VIEW geographic_hierarchy AS
SELECT
    e1.id as parent_id,
    e1.name as parent_name,
    e1.attributes->>'geographic_type' as parent_type,
    e2.id as child_id,
    e2.name as child_name,
    e2.attributes->>'geographic_type' as child_type,
    er.relationship_type,
    er.novel_id
FROM entities e1
JOIN entity_relationships er ON e1.id = er.source_entity_id
JOIN entities e2 ON e2.id = er.target_entity_id
JOIN entity_types et1 ON e1.entity_type_id = et1.id
JOIN entity_types et2 ON e2.entity_type_id = et2.id
WHERE er.relationship_type IN ('contains', 'belongs_to', 'part_of')
    AND et1.name IN ('region', 'city', 'town', 'village')
    AND et2.name IN ('region', 'city', 'town', 'village', 'building', 'landmark')
    AND e1.status = 'active'
    AND e2.status = 'active';

-- 同域地理实体视图
CREATE OR REPLACE VIEW geographic_entities_by_domain AS
SELECT
    e.novel_id,
    e.attributes->>'domain_code' as domain_code,
    et.display_name as entity_type_display,
    et.name as entity_type,
    COUNT(e.id) as entity_count,
    array_agg(e.name ORDER BY e.name) as entity_names
FROM entities e
JOIN entity_types et ON e.entity_type_id = et.id
WHERE et.name IN ('region', 'city', 'town', 'village', 'landmark', 'building', 'natural_feature', 'infrastructure')
    AND e.status = 'active'
    AND e.attributes ? 'domain_code'
GROUP BY e.novel_id, e.attributes->>'domain_code', et.display_name, et.name
ORDER BY e.novel_id, domain_code, et.name;

-- =============================================================================
-- 4. 地理实体统计函数
-- =============================================================================

-- 获取小说的地理实体统计
CREATE OR REPLACE FUNCTION get_geographic_entity_stats(p_novel_id INTEGER)
RETURNS TABLE (
    entity_type VARCHAR,
    entity_count BIGINT,
    domains_covered BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        et.name as entity_type,
        COUNT(e.id) as entity_count,
        COUNT(DISTINCT e.attributes->>'domain_code') as domains_covered
    FROM entities e
    JOIN entity_types et ON e.entity_type_id = et.id
    WHERE e.novel_id = p_novel_id
        AND et.name IN ('region', 'city', 'town', 'village', 'landmark', 'building', 'natural_feature', 'infrastructure')
        AND e.status = 'active'
    GROUP BY et.name
    ORDER BY entity_count DESC;
END;
$$ LANGUAGE plpgsql;

-- 获取域内地理实体详情
CREATE OR REPLACE FUNCTION get_domain_geographic_entities(
    p_novel_id INTEGER,
    p_domain_code VARCHAR
)
RETURNS TABLE (
    entity_id INTEGER,
    entity_name VARCHAR,
    entity_type VARCHAR,
    geographic_type VARCHAR,
    main_feature VARCHAR,
    population_level VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id as entity_id,
        e.name as entity_name,
        et.name as entity_type,
        e.attributes->>'geographic_type' as geographic_type,
        e.attributes->>'main_feature' as main_feature,
        e.attributes->>'population_level' as population_level
    FROM entities e
    JOIN entity_types et ON e.entity_type_id = et.id
    WHERE e.novel_id = p_novel_id
        AND e.attributes->>'domain_code' = p_domain_code
        AND et.name IN ('region', 'city', 'town', 'village', 'landmark', 'building', 'natural_feature', 'infrastructure')
        AND e.status = 'active'
    ORDER BY
        CASE et.name
            WHEN 'region' THEN 1
            WHEN 'city' THEN 2
            WHEN 'town' THEN 3
            WHEN 'village' THEN 4
            ELSE 5
        END,
        e.name;
END;
$$ LANGUAGE plpgsql;