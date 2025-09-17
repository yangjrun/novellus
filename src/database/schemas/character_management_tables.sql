-- =============================================================================
-- 角色管理表设计
-- 支持跨域角色版本管理和复杂角色数据存储
-- =============================================================================

-- =============================================================================
-- 1. 扩展现有实体表以支持角色版本管理
-- =============================================================================

-- 为 entities 表添加角色版本管理字段
ALTER TABLE entities ADD COLUMN IF NOT EXISTS domain_code VARCHAR(20);
ALTER TABLE entities ADD COLUMN IF NOT EXISTS character_version VARCHAR(20) DEFAULT '1.0';
ALTER TABLE entities ADD COLUMN IF NOT EXISTS previous_version_id INTEGER REFERENCES entities(id);
ALTER TABLE entities ADD COLUMN IF NOT EXISTS transition_notes TEXT;
ALTER TABLE entities ADD COLUMN IF NOT EXISTS is_current_version BOOLEAN DEFAULT true;

-- 添加角色ID字段（用于跨版本追踪同一角色）
ALTER TABLE entities ADD COLUMN IF NOT EXISTS character_unique_id VARCHAR(100);

-- 为角色版本管理添加约束
ALTER TABLE entities ADD CONSTRAINT IF NOT EXISTS chk_character_version
    CHECK (character_version ~ '^[0-9]+\.[0-9]+$');

-- 确保同一小说中同一角色在同一域只有一个当前版本
CREATE UNIQUE INDEX IF NOT EXISTS idx_entities_current_character_version
    ON entities(novel_id, character_unique_id, domain_code)
    WHERE is_current_version = true AND character_unique_id IS NOT NULL;

-- =============================================================================
-- 2. 角色实体类型初始化
-- =============================================================================

-- 为角色创建标准实体类型（如果不存在）
INSERT INTO entity_types (novel_id, name, display_name, schema_definition, validation_rules, display_config)
SELECT
    n.id as novel_id,
    'character' as name,
    '角色' as display_name,
    '{
        "required": ["name", "age", "gender"],
        "properties": {
            "name": {"type": "string", "description": "角色姓名"},
            "age": {"type": "integer", "description": "年龄"},
            "gender": {"type": "string", "enum": ["male", "female", "other"], "description": "性别"},
            "occupation": {"type": "string", "description": "职业"},
            "socialStatus": {"type": "string", "description": "社会地位"}
        }
    }' as schema_definition,
    '{
        "name": {"minLength": 1, "maxLength": 200},
        "age": {"minimum": 0, "maximum": 10000}
    }' as validation_rules,
    '{
        "listFields": ["name", "age", "occupation"],
        "detailFields": ["name", "age", "gender", "occupation", "socialStatus"],
        "searchFields": ["name", "occupation"]
    }' as display_config
FROM novels n
WHERE NOT EXISTS (
    SELECT 1 FROM entity_types et
    WHERE et.novel_id = n.id AND et.name = 'character'
);

-- =============================================================================
-- 3. 角色版本历史表
-- =============================================================================

-- 角色版本变更历史记录表
CREATE TABLE IF NOT EXISTS character_version_history (
    id SERIAL PRIMARY KEY,
    character_entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    character_unique_id VARCHAR(100) NOT NULL,

    -- 版本信息
    from_domain_code VARCHAR(20),
    to_domain_code VARCHAR(20) NOT NULL,
    from_version VARCHAR(20),
    to_version VARCHAR(20) NOT NULL,

    -- 变更信息
    transition_type VARCHAR(50) DEFAULT 'domain_transfer', -- domain_transfer/growth/event_triggered
    transition_reason TEXT,
    transition_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 变更摘要
    major_changes JSONB DEFAULT '{}', -- 主要变化的摘要
    preserved_aspects JSONB DEFAULT '{}', -- 保持不变的方面

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system'
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_version_history_character ON character_version_history(character_unique_id);
CREATE INDEX IF NOT EXISTS idx_version_history_novel ON character_version_history(novel_id);
CREATE INDEX IF NOT EXISTS idx_version_history_domain_transfer ON character_version_history(from_domain_code, to_domain_code);
CREATE INDEX IF NOT EXISTS idx_version_history_date ON character_version_history(transition_date DESC);

-- =============================================================================
-- 4. 角色关系版本管理
-- =============================================================================

-- 为实体关系表添加版本相关字段
ALTER TABLE entity_relationships ADD COLUMN IF NOT EXISTS domain_context VARCHAR(20);
ALTER TABLE entity_relationships ADD COLUMN IF NOT EXISTS relationship_version VARCHAR(20) DEFAULT '1.0';
ALTER TABLE entity_relationships ADD COLUMN IF NOT EXISTS is_cross_domain BOOLEAN DEFAULT false;

-- 角色关系变迁记录表
CREATE TABLE IF NOT EXISTS character_relationship_evolution (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,

    -- 关系主体
    source_character_id VARCHAR(100) NOT NULL,
    target_character_id VARCHAR(100) NOT NULL,

    -- 版本和域信息
    domain_code VARCHAR(20) NOT NULL,
    version VARCHAR(20) NOT NULL,

    -- 关系变化
    previous_relationship_type VARCHAR(100),
    current_relationship_type VARCHAR(100) NOT NULL,
    change_reason TEXT,

    -- 时间信息
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    in_story_context TEXT, -- 故事内的变化背景

    -- 影响评估
    impact_level INTEGER DEFAULT 1 CHECK (impact_level >= 1 AND impact_level <= 10),
    affects_other_relationships BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_rel_evolution_characters ON character_relationship_evolution(source_character_id, target_character_id);
CREATE INDEX IF NOT EXISTS idx_rel_evolution_domain ON character_relationship_evolution(novel_id, domain_code);

-- =============================================================================
-- 5. 角色统计和元数据视图
-- =============================================================================

-- 角色版本概览视图
CREATE OR REPLACE VIEW character_version_overview AS
SELECT
    e.id as entity_id,
    e.novel_id,
    e.character_unique_id,
    e.name as character_name,
    e.domain_code,
    e.character_version,
    e.is_current_version,
    e.created_at as version_created_at,
    e.updated_at as version_updated_at,

    -- 统计信息
    (SELECT COUNT(*) FROM character_version_history cvh
     WHERE cvh.character_unique_id = e.character_unique_id) as total_versions,

    -- 关系统计
    (SELECT COUNT(*) FROM entity_relationships er
     WHERE er.source_entity_id = e.id OR er.target_entity_id = e.id) as relationship_count,

    -- 前一版本信息
    prev.name as previous_version_name,
    prev.domain_code as previous_domain_code,
    prev.character_version as previous_version_number

FROM entities e
LEFT JOIN entities prev ON e.previous_version_id = prev.id
WHERE e.character_unique_id IS NOT NULL
ORDER BY e.character_unique_id, e.character_version DESC;

-- 角色域分布统计视图
CREATE OR REPLACE VIEW character_domain_distribution AS
SELECT
    n.title as novel_title,
    n.code as novel_code,
    e.domain_code,
    COUNT(DISTINCT e.character_unique_id) as unique_characters,
    COUNT(*) as total_versions,
    COUNT(CASE WHEN e.is_current_version THEN 1 END) as current_versions
FROM novels n
JOIN entities e ON n.id = e.novel_id
WHERE e.character_unique_id IS NOT NULL
GROUP BY n.id, n.title, n.code, e.domain_code
ORDER BY n.id, e.domain_code;

-- =============================================================================
-- 6. 触发器和函数
-- =============================================================================

-- 角色版本历史记录触发器函数
CREATE OR REPLACE FUNCTION record_character_version_change()
RETURNS TRIGGER AS $$
BEGIN
    -- 当角色的域或版本发生变化时，记录到历史表
    IF (OLD.domain_code IS DISTINCT FROM NEW.domain_code OR
        OLD.character_version IS DISTINCT FROM NEW.character_version) AND
        NEW.character_unique_id IS NOT NULL THEN

        INSERT INTO character_version_history (
            character_entity_id,
            novel_id,
            character_unique_id,
            from_domain_code,
            to_domain_code,
            from_version,
            to_version,
            transition_reason
        ) VALUES (
            NEW.id,
            NEW.novel_id,
            NEW.character_unique_id,
            OLD.domain_code,
            NEW.domain_code,
            OLD.character_version,
            NEW.character_version,
            NEW.transition_notes
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为 entities 表添加版本变更触发器
DROP TRIGGER IF EXISTS trigger_character_version_change ON entities;
CREATE TRIGGER trigger_character_version_change
    AFTER UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION record_character_version_change();

-- 确保角色版本一致性的函数
CREATE OR REPLACE FUNCTION ensure_character_version_consistency()
RETURNS TRIGGER AS $$
BEGIN
    -- 当设置为当前版本时，将同一角色的其他版本设为非当前
    IF NEW.is_current_version = true AND NEW.character_unique_id IS NOT NULL THEN
        UPDATE entities
        SET is_current_version = false,
            updated_at = CURRENT_TIMESTAMP
        WHERE novel_id = NEW.novel_id
            AND character_unique_id = NEW.character_unique_id
            AND domain_code = NEW.domain_code
            AND id != NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为 entities 表添加版本一致性触发器
DROP TRIGGER IF EXISTS trigger_character_version_consistency ON entities;
CREATE TRIGGER trigger_character_version_consistency
    BEFORE INSERT OR UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION ensure_character_version_consistency();

-- =============================================================================
-- 7. 为现有表添加必要索引
-- =============================================================================

-- 角色相关索引
CREATE INDEX IF NOT EXISTS idx_entities_character_unique_id ON entities(character_unique_id);
CREATE INDEX IF NOT EXISTS idx_entities_domain_version ON entities(novel_id, domain_code, character_version);
CREATE INDEX IF NOT EXISTS idx_entities_current_version ON entities(novel_id, is_current_version) WHERE character_unique_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entities_character_domain ON entities(character_unique_id, domain_code);

-- 关系表索引优化
CREATE INDEX IF NOT EXISTS idx_relationships_domain_context ON entity_relationships(novel_id, domain_context);
CREATE INDEX IF NOT EXISTS idx_relationships_cross_domain ON entity_relationships(is_cross_domain) WHERE is_cross_domain = true;

-- JSONB 字段的 GIN 索引（如果还没有的话）
CREATE INDEX IF NOT EXISTS idx_entities_attributes_character_gin ON entities USING GIN(attributes)
WHERE character_unique_id IS NOT NULL;

-- =============================================================================
-- 8. 数据完整性检查
-- =============================================================================

-- 检查和清理数据的函数
CREATE OR REPLACE FUNCTION validate_character_data()
RETURNS TABLE(
    issue_type TEXT,
    entity_id INTEGER,
    character_unique_id VARCHAR(100),
    description TEXT
) AS $$
BEGIN
    -- 检查重复的当前版本
    RETURN QUERY
    SELECT
        'duplicate_current_version'::TEXT,
        e.id,
        e.character_unique_id,
        format('Character %s has multiple current versions in domain %s',
               e.character_unique_id, e.domain_code)
    FROM entities e
    WHERE e.character_unique_id IS NOT NULL
        AND e.is_current_version = true
    GROUP BY e.character_unique_id, e.domain_code, e.novel_id
    HAVING COUNT(*) > 1;

    -- 检查版本链断裂
    RETURN QUERY
    SELECT
        'broken_version_chain'::TEXT,
        e.id,
        e.character_unique_id,
        format('Character %s version chain may be broken', e.character_unique_id)
    FROM entities e
    WHERE e.character_unique_id IS NOT NULL
        AND e.previous_version_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM entities prev
            WHERE prev.id = e.previous_version_id
                AND prev.character_unique_id = e.character_unique_id
        );
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 9. 示例数据插入（仅用于测试）
-- =============================================================================

-- 为"裂世九域"小说创建角色实体类型（如果需要的话）
DO $$
DECLARE
    novel_id_val INTEGER;
    character_type_id INTEGER;
BEGIN
    -- 获取小说ID
    SELECT id INTO novel_id_val FROM novels WHERE code = 'lieshi_jiuyu' LIMIT 1;

    IF novel_id_val IS NOT NULL THEN
        -- 获取或创建角色实体类型
        SELECT id INTO character_type_id
        FROM entity_types
        WHERE novel_id = novel_id_val AND name = 'character';

        IF character_type_id IS NOT NULL THEN
            -- 这里可以插入示例角色数据
            -- 实际使用时应该通过应用代码插入
            NULL;
        END IF;
    END IF;
END;
$$;