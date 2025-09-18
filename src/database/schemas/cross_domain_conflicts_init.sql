-- =============================================================================
-- 跨域冲突管理表结构定义
-- 支持多域世界观中的冲突关系和剧情钩子管理
-- =============================================================================

-- 注意：具体的域设定和冲突数据已移动到 default_data.sql 文件
-- 此处仅定义表结构、索引和约束函数

-- =============================================================================
-- 1. 跨域冲突分析函数
-- =============================================================================

-- 获取两个域之间的冲突强度
CREATE OR REPLACE FUNCTION get_domain_conflict_intensity(
    p_novel_id INTEGER,
    p_domain1_code VARCHAR,
    p_domain2_code VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    conflict_intensity INTEGER := 0;
BEGIN
    SELECT cc.intensity_level INTO conflict_intensity
    FROM cultural_conflicts cc
    JOIN domains d1 ON cc.primary_domain_id = d1.id
    JOIN domains d2 ON cc.secondary_domain_id = d2.id
    WHERE cc.novel_id = p_novel_id
        AND ((d1.code = p_domain1_code AND d2.code = p_domain2_code)
             OR (d1.code = p_domain2_code AND d2.code = p_domain1_code))
    ORDER BY cc.intensity_level DESC
    LIMIT 1;

    RETURN COALESCE(conflict_intensity, 0);
END;
$$ LANGUAGE plpgsql;

-- 获取域的可用剧情钩子
CREATE OR REPLACE FUNCTION get_available_plot_hooks(
    p_novel_id INTEGER,
    p_domain_code VARCHAR DEFAULT NULL,
    p_urgency_min INTEGER DEFAULT 1,
    p_drama_min INTEGER DEFAULT 1
)
RETURNS TABLE (
    hook_id INTEGER,
    domain_name VARCHAR,
    hook_title VARCHAR,
    hook_description TEXT,
    urgency_level INTEGER,
    drama_level INTEGER,
    scope VARCHAR,
    potential_outcomes TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ph.id as hook_id,
        d.name as domain_name,
        ph.title as hook_title,
        ph.description as hook_description,
        ph.urgency_level,
        ph.drama_level,
        ph.scope,
        ph.potential_outcomes
    FROM plot_hooks ph
    JOIN domains d ON ph.domain_id = d.id
    WHERE ph.novel_id = p_novel_id
        AND ph.status = 'available'
        AND ph.urgency_level >= p_urgency_min
        AND ph.drama_level >= p_drama_min
        AND (p_domain_code IS NULL OR d.code = p_domain_code)
    ORDER BY ph.urgency_level DESC, ph.drama_level DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 2. 域间关系分析视图
-- =============================================================================

-- 域间冲突矩阵视图
CREATE OR REPLACE VIEW domain_conflict_matrix AS
SELECT
    d1.name as domain1_name,
    d1.code as domain1_code,
    d2.name as domain2_name,
    d2.code as domain2_code,
    cc.conflict_type,
    cc.conflict_name,
    cc.intensity_level,
    cc.historical_depth,
    cc.resolution_difficulty,
    cc.status,
    cc.novel_id
FROM cultural_conflicts cc
JOIN domains d1 ON cc.primary_domain_id = d1.id
JOIN domains d2 ON cc.secondary_domain_id = d2.id
ORDER BY cc.novel_id, cc.intensity_level DESC;

-- 域的综合实力对比视图
CREATE OR REPLACE VIEW domain_power_comparison AS
SELECT
    d.novel_id,
    d.name as domain_name,
    d.code as domain_code,
    d.power_level,
    d.civilization_level,
    d.stability_level,
    -- 计算综合实力指数
    (d.power_level * 0.4 + d.civilization_level * 0.3 + d.stability_level * 0.3) as composite_power_index,
    d.ruling_power,
    d.dominant_law,
    RANK() OVER (PARTITION BY d.novel_id ORDER BY d.power_level DESC) as power_rank,
    RANK() OVER (PARTITION BY d.novel_id ORDER BY d.civilization_level DESC) as civilization_rank,
    RANK() OVER (PARTITION BY d.novel_id ORDER BY d.stability_level DESC) as stability_rank
FROM domains d
WHERE d.is_active = true;

-- =============================================================================
-- 3. 剧情钩子管理函数
-- =============================================================================

-- 激活剧情钩子
CREATE OR REPLACE FUNCTION activate_plot_hook(
    p_hook_id INTEGER,
    p_activation_reason TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    hook_exists BOOLEAN := FALSE;
BEGIN
    -- 检查钩子是否存在且可用
    SELECT EXISTS(
        SELECT 1 FROM plot_hooks
        WHERE id = p_hook_id AND status = 'available'
    ) INTO hook_exists;

    IF NOT hook_exists THEN
        RETURN FALSE;
    END IF;

    -- 更新钩子状态
    UPDATE plot_hooks SET
        status = 'active',
        activated_at = CURRENT_TIMESTAMP,
        activation_reason = p_activation_reason,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_hook_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 完成剧情钩子
CREATE OR REPLACE FUNCTION complete_plot_hook(
    p_hook_id INTEGER,
    p_resolution TEXT DEFAULT NULL,
    p_outcome VARCHAR DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    hook_exists BOOLEAN := FALSE;
BEGIN
    -- 检查钩子是否存在且已激活
    SELECT EXISTS(
        SELECT 1 FROM plot_hooks
        WHERE id = p_hook_id AND status = 'active'
    ) INTO hook_exists;

    IF NOT hook_exists THEN
        RETURN FALSE;
    END IF;

    -- 更新钩子状态
    UPDATE plot_hooks SET
        status = 'completed',
        completed_at = CURRENT_TIMESTAMP,
        resolution = p_resolution,
        actual_outcome = p_outcome,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_hook_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 4. 冲突强度评估函数
-- =============================================================================

-- 计算域间总体冲突指数
CREATE OR REPLACE FUNCTION calculate_domain_conflict_index(p_novel_id INTEGER)
RETURNS TABLE (
    domain_code VARCHAR,
    domain_name VARCHAR,
    total_conflicts INTEGER,
    avg_intensity NUMERIC,
    max_intensity INTEGER,
    conflict_index NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.code as domain_code,
        d.name as domain_name,
        COUNT(cc.id)::INTEGER as total_conflicts,
        ROUND(AVG(cc.intensity_level), 2) as avg_intensity,
        MAX(cc.intensity_level) as max_intensity,
        ROUND(
            (COUNT(cc.id) * AVG(cc.intensity_level) * MAX(cc.historical_depth)) / 100.0,
            2
        ) as conflict_index
    FROM domains d
    LEFT JOIN cultural_conflicts cc ON (d.id = cc.primary_domain_id OR d.id = cc.secondary_domain_id)
        AND cc.novel_id = p_novel_id
    WHERE d.novel_id = p_novel_id AND d.is_active = true
    GROUP BY d.code, d.name
    ORDER BY conflict_index DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 5. 索引优化
-- =============================================================================

-- 为跨域查询优化的索引
CREATE INDEX IF NOT EXISTS idx_cultural_conflicts_domains
    ON cultural_conflicts(novel_id, primary_domain_id, secondary_domain_id);

CREATE INDEX IF NOT EXISTS idx_cultural_conflicts_intensity
    ON cultural_conflicts(novel_id, intensity_level DESC);

CREATE INDEX IF NOT EXISTS idx_plot_hooks_domain_status
    ON plot_hooks(novel_id, domain_id, status);

CREATE INDEX IF NOT EXISTS idx_plot_hooks_urgency_drama
    ON plot_hooks(novel_id, urgency_level DESC, drama_level DESC)
    WHERE status = 'available';

CREATE INDEX IF NOT EXISTS idx_domains_power_levels
    ON domains(novel_id, power_level DESC, civilization_level DESC, stability_level DESC)
    WHERE is_active = true;

-- =============================================================================
-- 6. 触发器
-- =============================================================================

-- 域冲突历史记录触发器
CREATE OR REPLACE FUNCTION log_conflict_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- 当冲突状态改变时，记录到历史表
    IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
        INSERT INTO conflict_status_history (
            novel_id, conflict_id, old_status, new_status,
            change_reason, changed_at
        ) VALUES (
            NEW.novel_id, NEW.id, OLD.status, NEW.status,
            'Status changed', CURRENT_TIMESTAMP
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为冲突表添加状态变更日志触发器
DROP TRIGGER IF EXISTS trigger_log_conflict_changes ON cultural_conflicts;
CREATE TRIGGER trigger_log_conflict_changes
    AFTER UPDATE ON cultural_conflicts
    FOR EACH ROW
    EXECUTE FUNCTION log_conflict_changes();