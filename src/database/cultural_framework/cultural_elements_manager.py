"""
文化要素管理模块
处理法条、仪式、实践等文化要素的CRUD操作
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg

from ..models.cultural_models import (
    CulturalElement, CulturalFramework, Domain, CulturalDimension,
    ElementType
)


class CulturalElementManager:
    """文化要素管理器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def create_element(self, novel_id: int, element_data: Dict[str, Any]) -> int:
        """创建文化要素"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO cultural_elements (
                    novel_id, framework_id, element_type, name, code,
                    category, subcategory, attributes, importance,
                    influence_scope, status, related_entities,
                    parent_element_id, established_time, active_period, tags
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
                ) RETURNING id
            """
            element_id = await conn.fetchval(
                query,
                novel_id,
                element_data['framework_id'],
                element_data['element_type'],
                element_data['name'],
                element_data.get('code'),
                element_data.get('category'),
                element_data.get('subcategory'),
                element_data.get('attributes', {}),
                element_data.get('importance', 1),
                element_data.get('influence_scope', 'local'),
                element_data.get('status', 'active'),
                element_data.get('related_entities', []),
                element_data.get('parent_element_id'),
                element_data.get('established_time'),
                element_data.get('active_period'),
                element_data.get('tags', [])
            )
            return element_id

    async def get_element_by_id(self, element_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取文化要素"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT
                    ce.*,
                    cf.framework_name,
                    d.name as domain_name,
                    d.code as domain_code,
                    cd.name as dimension_name,
                    cd.code as dimension_code
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                WHERE ce.id = $1
            """
            result = await conn.fetchrow(query, element_id)
            return dict(result) if result else None

    async def get_elements_by_framework(self, framework_id: int) -> List[Dict[str, Any]]:
        """获取框架下的所有文化要素"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT ce.*
                FROM cultural_elements ce
                WHERE ce.framework_id = $1
                ORDER BY ce.importance DESC, ce.created_at ASC
            """
            elements = await conn.fetch(query, framework_id)
            return [dict(element) for element in elements]

    async def get_elements_by_domain(self, novel_id: int, domain_code: str,
                                   element_type: str = None) -> List[Dict[str, Any]]:
        """获取特定域的文化要素"""
        async with self.db_pool.acquire() as conn:
            base_query = """
                SELECT
                    ce.*,
                    cf.framework_name,
                    cd.name as dimension_name,
                    cd.code as dimension_code
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                WHERE ce.novel_id = $1 AND d.code = $2
            """

            if element_type:
                query = base_query + " AND ce.element_type = $3 ORDER BY ce.importance DESC"
                elements = await conn.fetch(query, novel_id, domain_code, element_type)
            else:
                query = base_query + " ORDER BY ce.importance DESC"
                elements = await conn.fetch(query, novel_id, domain_code)

            return [dict(element) for element in elements]

    async def get_elements_by_type(self, novel_id: int, element_type: str) -> List[Dict[str, Any]]:
        """获取特定类型的文化要素"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT
                    ce.*,
                    cf.framework_name,
                    d.name as domain_name,
                    d.code as domain_code,
                    cd.name as dimension_name
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                WHERE ce.novel_id = $1 AND ce.element_type = $2
                ORDER BY d.sort_order, ce.importance DESC
            """
            elements = await conn.fetch(query, novel_id, element_type)
            return [dict(element) for element in elements]

    async def update_element(self, element_id: int, updates: Dict[str, Any]) -> bool:
        """更新文化要素"""
        async with self.db_pool.acquire() as conn:
            # 构建动态更新查询
            set_clauses = []
            values = []
            param_index = 1

            for field, value in updates.items():
                if field in ['name', 'code', 'category', 'subcategory', 'attributes',
                           'importance', 'influence_scope', 'status', 'related_entities',
                           'established_time', 'active_period', 'tags']:
                    set_clauses.append(f"{field} = ${param_index}")
                    values.append(value)
                    param_index += 1

            if not set_clauses:
                return False

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            query = f"""
                UPDATE cultural_elements
                SET {', '.join(set_clauses)}
                WHERE id = ${param_index}
            """
            values.append(element_id)

            await conn.execute(query, *values)
            return True

    async def delete_element(self, element_id: int) -> bool:
        """删除文化要素（软删除）"""
        async with self.db_pool.acquire() as conn:
            query = """
                UPDATE cultural_elements
                SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """
            await conn.execute(query, element_id)
            return True

    async def search_elements(self, novel_id: int, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索文化要素"""
        async with self.db_pool.acquire() as conn:
            conditions = ["ce.novel_id = $1"]
            values = [novel_id]
            param_index = 2

            # 构建搜索条件
            if search_params.get('keyword'):
                conditions.append(f"(ce.name ILIKE ${param_index} OR ce.description ILIKE ${param_index})")
                values.append(f"%{search_params['keyword']}%")
                param_index += 1

            if search_params.get('element_type'):
                conditions.append(f"ce.element_type = ${param_index}")
                values.append(search_params['element_type'])
                param_index += 1

            if search_params.get('domain_code'):
                conditions.append(f"d.code = ${param_index}")
                values.append(search_params['domain_code'])
                param_index += 1

            if search_params.get('dimension_code'):
                conditions.append(f"cd.code = ${param_index}")
                values.append(search_params['dimension_code'])
                param_index += 1

            if search_params.get('status'):
                conditions.append(f"ce.status = ${param_index}")
                values.append(search_params['status'])
                param_index += 1

            if search_params.get('min_importance'):
                conditions.append(f"ce.importance >= ${param_index}")
                values.append(search_params['min_importance'])
                param_index += 1

            if search_params.get('tags'):
                conditions.append(f"ce.tags && ${param_index}")
                values.append(search_params['tags'])
                param_index += 1

            query = f"""
                SELECT
                    ce.*,
                    cf.framework_name,
                    d.name as domain_name,
                    d.code as domain_code,
                    cd.name as dimension_name,
                    cd.code as dimension_code
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                WHERE {' AND '.join(conditions)}
                ORDER BY ce.importance DESC, ce.created_at DESC
                LIMIT {search_params.get('limit', 50)}
                OFFSET {search_params.get('offset', 0)}
            """

            elements = await conn.fetch(query, *values)
            return [dict(element) for element in elements]

    async def get_element_relationships(self, element_id: int) -> Dict[str, Any]:
        """获取文化要素的关系网络"""
        async with self.db_pool.acquire() as conn:
            # 获取子要素
            children_query = """
                SELECT id, name, element_type, importance
                FROM cultural_elements
                WHERE parent_element_id = $1 AND status = 'active'
                ORDER BY importance DESC
            """
            children = await conn.fetch(children_query, element_id)

            # 获取父要素
            parent_query = """
                SELECT ce2.id, ce2.name, ce2.element_type, ce2.importance
                FROM cultural_elements ce1
                JOIN cultural_elements ce2 ON ce1.parent_element_id = ce2.id
                WHERE ce1.id = $1
            """
            parent = await conn.fetchrow(parent_query, element_id)

            # 获取相关实体
            element_query = """
                SELECT related_entities FROM cultural_elements WHERE id = $1
            """
            element = await conn.fetchrow(element_query, element_id)
            related_entities = element['related_entities'] if element else []

            # 获取同框架的相关要素
            siblings_query = """
                SELECT ce2.id, ce2.name, ce2.element_type, ce2.importance
                FROM cultural_elements ce1
                JOIN cultural_elements ce2 ON ce1.framework_id = ce2.framework_id
                WHERE ce1.id = $1 AND ce2.id != $1 AND ce2.status = 'active'
                ORDER BY ce2.importance DESC
                LIMIT 10
            """
            siblings = await conn.fetch(siblings_query, element_id)

            return {
                'children': [dict(child) for child in children],
                'parent': dict(parent) if parent else None,
                'related_entities': related_entities,
                'siblings': [dict(sibling) for sibling in siblings]
            }

    async def analyze_elements_by_domain(self, novel_id: int, domain_code: str) -> Dict[str, Any]:
        """分析特定域的文化要素"""
        async with self.db_pool.acquire() as conn:
            # 要素类型分布
            type_distribution_query = """
                SELECT
                    ce.element_type,
                    COUNT(*) as count,
                    AVG(ce.importance) as avg_importance
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                WHERE ce.novel_id = $1 AND d.code = $2 AND ce.status = 'active'
                GROUP BY ce.element_type
                ORDER BY count DESC
            """
            type_distribution = await conn.fetch(type_distribution_query, novel_id, domain_code)

            # 维度分布
            dimension_distribution_query = """
                SELECT
                    cd.name as dimension_name,
                    cd.code as dimension_code,
                    COUNT(ce.id) as element_count,
                    AVG(ce.importance) as avg_importance
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                WHERE ce.novel_id = $1 AND d.code = $2 AND ce.status = 'active'
                GROUP BY cd.id, cd.name, cd.code
                ORDER BY element_count DESC
            """
            dimension_distribution = await conn.fetch(dimension_distribution_query, novel_id, domain_code)

            # 重要性分布
            importance_distribution_query = """
                SELECT
                    CASE
                        WHEN ce.importance >= 8 THEN 'high'
                        WHEN ce.importance >= 5 THEN 'medium'
                        ELSE 'low'
                    END as importance_level,
                    COUNT(*) as count
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                WHERE ce.novel_id = $1 AND d.code = $2 AND ce.status = 'active'
                GROUP BY importance_level
                ORDER BY count DESC
            """
            importance_distribution = await conn.fetch(importance_distribution_query, novel_id, domain_code)

            # 影响范围分析
            scope_analysis_query = """
                SELECT
                    ce.influence_scope,
                    COUNT(*) as count,
                    AVG(ce.importance) as avg_importance
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                WHERE ce.novel_id = $1 AND d.code = $2 AND ce.status = 'active'
                GROUP BY ce.influence_scope
                ORDER BY count DESC
            """
            scope_analysis = await conn.fetch(scope_analysis_query, novel_id, domain_code)

            # 最重要的要素
            top_elements_query = """
                SELECT
                    ce.name,
                    ce.element_type,
                    ce.importance,
                    ce.influence_scope,
                    cd.name as dimension_name
                FROM cultural_elements ce
                JOIN cultural_frameworks cf ON ce.framework_id = cf.id
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                WHERE ce.novel_id = $1 AND d.code = $2 AND ce.status = 'active'
                ORDER BY ce.importance DESC
                LIMIT 10
            """
            top_elements = await conn.fetch(top_elements_query, novel_id, domain_code)

            return {
                'type_distribution': [dict(row) for row in type_distribution],
                'dimension_distribution': [dict(row) for row in dimension_distribution],
                'importance_distribution': [dict(row) for row in importance_distribution],
                'scope_analysis': [dict(row) for row in scope_analysis],
                'top_elements': [dict(row) for row in top_elements]
            }

    async def get_conflicting_elements(self, novel_id: int) -> List[Dict[str, Any]]:
        """获取可能产生冲突的文化要素"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT
                    ce1.id as element1_id,
                    ce1.name as element1_name,
                    ce1.element_type as element1_type,
                    d1.name as domain1_name,
                    ce2.id as element2_id,
                    ce2.name as element2_name,
                    ce2.element_type as element2_type,
                    d2.name as domain2_name,
                    CASE
                        WHEN ce1.element_type = ce2.element_type THEN 'type_conflict'
                        WHEN ce1.influence_scope = 'cross_domain' OR ce2.influence_scope = 'cross_domain' THEN 'scope_conflict'
                        WHEN ce1.attributes ? 'conflicts_with' AND ce2.code = ANY(ARRAY(SELECT jsonb_array_elements_text(ce1.attributes->'conflicts_with'))) THEN 'explicit_conflict'
                        ELSE 'potential_conflict'
                    END as conflict_type
                FROM cultural_elements ce1
                JOIN cultural_frameworks cf1 ON ce1.framework_id = cf1.id
                JOIN domains d1 ON cf1.domain_id = d1.id
                JOIN cultural_elements ce2 ON ce1.novel_id = ce2.novel_id
                JOIN cultural_frameworks cf2 ON ce2.framework_id = cf2.id
                JOIN domains d2 ON cf2.domain_id = d2.id
                WHERE ce1.novel_id = $1
                AND ce1.id < ce2.id  -- 避免重复
                AND d1.id != d2.id   -- 跨域
                AND ce1.status = 'active' AND ce2.status = 'active'
                AND (
                    -- 同类型要素可能冲突
                    ce1.element_type = ce2.element_type
                    -- 跨域影响的要素可能冲突
                    OR ce1.influence_scope = 'cross_domain'
                    OR ce2.influence_scope = 'cross_domain'
                    -- 明确标记冲突的要素
                    OR (ce1.attributes ? 'conflicts_with' AND ce2.code = ANY(ARRAY(SELECT jsonb_array_elements_text(ce1.attributes->'conflicts_with'))))
                    OR (ce2.attributes ? 'conflicts_with' AND ce1.code = ANY(ARRAY(SELECT jsonb_array_elements_text(ce2.attributes->'conflicts_with'))))
                )
                ORDER BY ce1.importance + ce2.importance DESC
            """
            conflicts = await conn.fetch(query, novel_id)
            return [dict(conflict) for conflict in conflicts]


class CulturalFrameworkManager:
    """文化框架管理器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def create_framework(self, novel_id: int, framework_data: Dict[str, Any]) -> int:
        """创建文化框架"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO cultural_frameworks (
                    novel_id, domain_id, dimension_id, framework_name,
                    version, core_concept, key_features, completeness_score
                ) VALUES (
                    $1,
                    (SELECT id FROM domains WHERE code = $2 AND novel_id = $1),
                    (SELECT id FROM cultural_dimensions WHERE code = $3),
                    $4, $5, $6, $7, $8
                ) RETURNING id
            """
            framework_id = await conn.fetchval(
                query,
                novel_id,
                framework_data['domain_code'],
                framework_data['dimension_code'],
                framework_data['framework_name'],
                framework_data.get('version', '1.0'),
                framework_data.get('core_concept', ''),
                framework_data.get('key_features', {}),
                framework_data.get('completeness_score', 0)
            )
            return framework_id

    async def get_framework_overview(self, novel_id: int) -> List[Dict[str, Any]]:
        """获取文化框架概览"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT
                    cf.*,
                    d.name as domain_name,
                    d.code as domain_code,
                    cd.name as dimension_name,
                    cd.code as dimension_code,
                    COUNT(ce.id) as element_count
                FROM cultural_frameworks cf
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                LEFT JOIN cultural_elements ce ON cf.id = ce.framework_id AND ce.status = 'active'
                WHERE cf.novel_id = $1
                GROUP BY cf.id, d.id, cd.id
                ORDER BY d.sort_order, cd.sort_order
            """
            frameworks = await conn.fetch(query, novel_id)
            return [dict(framework) for framework in frameworks]

    async def update_framework_completeness(self, framework_id: int) -> int:
        """更新框架完整度评分"""
        async with self.db_pool.acquire() as conn:
            # 基于要素数量和重要性计算完整度
            score_query = """
                SELECT
                    COUNT(*) as total_elements,
                    COUNT(CASE WHEN importance >= 8 THEN 1 END) as high_importance,
                    COUNT(CASE WHEN importance >= 5 THEN 1 END) as medium_importance,
                    COUNT(DISTINCT element_type) as type_diversity
                FROM cultural_elements
                WHERE framework_id = $1 AND status = 'active'
            """
            stats = await conn.fetchrow(score_query, framework_id)

            # 计算完整度评分
            total = stats['total_elements']
            high = stats['high_importance']
            medium = stats['medium_importance']
            diversity = stats['type_diversity']

            # 评分算法：基础分 + 要素数量 + 重要性权重 + 类型多样性
            score = min(100,
                       (total * 5) +           # 每个要素5分
                       (high * 10) +           # 高重要性额外10分
                       (medium * 5) +          # 中重要性额外5分
                       (diversity * 15))       # 类型多样性每种15分

            # 更新完整度评分
            update_query = """
                UPDATE cultural_frameworks
                SET completeness_score = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
                RETURNING completeness_score
            """
            new_score = await conn.fetchval(update_query, score, framework_id)
            return new_score