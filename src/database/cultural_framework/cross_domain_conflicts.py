"""
跨域冲突矩阵管理模块
处理域间冲突的数据访问和业务逻辑
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncpg
from dataclasses import dataclass

from ..models.cultural_models import (
    Domain, CulturalConflict, PlotHook, CulturalElement,
    ConflictType, HookType, ElementType
)


@dataclass
class ConflictMatrix:
    """冲突矩阵数据结构"""
    domain_pairs: List[Tuple[str, str]]
    intensities: Dict[Tuple[str, str], int]
    conflict_types: Dict[Tuple[str, str], str]
    current_status: Dict[Tuple[str, str], str]


@dataclass
class ConflictAnalysis:
    """冲突分析结果"""
    total_conflicts: int
    average_intensity: float
    high_risk_pairs: List[Tuple[str, str]]
    escalating_conflicts: List[Dict[str, Any]]
    available_hooks: List[Dict[str, Any]]


class CrossDomainConflictManager:
    """跨域冲突管理器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_conflict_matrix(self, novel_id: int) -> ConflictMatrix:
        """获取冲突矩阵"""
        async with self.db_pool.acquire() as conn:
            # 获取所有域
            domains_query = """
                SELECT code, name FROM domains
                WHERE novel_id = $1 AND is_active = true
                ORDER BY sort_order
            """
            domains = await conn.fetch(domains_query, novel_id)
            domain_codes = [d['code'] for d in domains]

            # 获取冲突数据
            conflicts_query = """
                SELECT
                    d1.code as primary_code,
                    d2.code as secondary_code,
                    cc.intensity_level,
                    cc.conflict_type,
                    cc.status
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1
            """
            conflicts = await conn.fetch(conflicts_query, novel_id)

            # 构建矩阵
            domain_pairs = []
            intensities = {}
            conflict_types = {}
            current_status = {}

            for conflict in conflicts:
                pair = (conflict['primary_code'], conflict['secondary_code'])
                domain_pairs.append(pair)
                intensities[pair] = conflict['intensity_level']
                conflict_types[pair] = conflict['conflict_type']
                current_status[pair] = conflict['status']

                # 添加反向对
                reverse_pair = (conflict['secondary_code'], conflict['primary_code'])
                domain_pairs.append(reverse_pair)
                intensities[reverse_pair] = conflict['intensity_level']
                conflict_types[reverse_pair] = conflict['conflict_type']
                current_status[reverse_pair] = conflict['status']

            return ConflictMatrix(
                domain_pairs=list(set(domain_pairs)),
                intensities=intensities,
                conflict_types=conflict_types,
                current_status=current_status
            )

    async def create_conflict(self, novel_id: int, conflict_data: Dict[str, Any]) -> int:
        """创建新冲突"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO cultural_conflicts (
                    novel_id, primary_domain_id, secondary_domain_id,
                    conflict_type, conflict_name, description,
                    intensity_level, historical_depth, resolution_difficulty,
                    status, current_manifestation, affected_areas, stakeholders
                ) VALUES (
                    $1,
                    (SELECT id FROM domains WHERE code = $2 AND novel_id = $1),
                    (SELECT id FROM domains WHERE code = $3 AND novel_id = $1),
                    $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
                ) RETURNING id
            """
            conflict_id = await conn.fetchval(
                query,
                novel_id,
                conflict_data['primary_domain_code'],
                conflict_data['secondary_domain_code'],
                conflict_data['conflict_type'],
                conflict_data['conflict_name'],
                conflict_data.get('description', ''),
                conflict_data['intensity_level'],
                conflict_data.get('historical_depth', 1),
                conflict_data.get('resolution_difficulty', 5),
                conflict_data.get('status', 'ongoing'),
                conflict_data.get('current_manifestation', ''),
                conflict_data.get('affected_areas', {}),
                conflict_data.get('stakeholders', [])
            )
            return conflict_id

    async def update_conflict_intensity(self, conflict_id: int, new_intensity: int,
                                      manifestation: str = None) -> bool:
        """更新冲突强度"""
        async with self.db_pool.acquire() as conn:
            if manifestation:
                query = """
                    UPDATE cultural_conflicts
                    SET intensity_level = $1, current_manifestation = $2, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $3
                """
                await conn.execute(query, new_intensity, manifestation, conflict_id)
            else:
                query = """
                    UPDATE cultural_conflicts
                    SET intensity_level = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                """
                await conn.execute(query, new_intensity, conflict_id)
            return True

    async def get_conflicts_by_domain(self, novel_id: int, domain_code: str) -> List[Dict[str, Any]]:
        """获取特定域的所有冲突"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT
                    cc.*,
                    d1.name as primary_domain_name,
                    d1.code as primary_domain_code,
                    d2.name as secondary_domain_name,
                    d2.code as secondary_domain_code
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1 AND (d1.code = $2 OR d2.code = $2)
                ORDER BY cc.intensity_level DESC
            """
            conflicts = await conn.fetch(query, novel_id, domain_code)
            return [dict(conflict) for conflict in conflicts]

    async def analyze_conflicts(self, novel_id: int) -> ConflictAnalysis:
        """分析冲突情况"""
        async with self.db_pool.acquire() as conn:
            # 基础统计
            stats_query = """
                SELECT
                    COUNT(*) as total_conflicts,
                    AVG(intensity_level) as avg_intensity,
                    COUNT(CASE WHEN intensity_level >= 8 THEN 1 END) as high_intensity_count
                FROM cultural_conflicts
                WHERE novel_id = $1
            """
            stats = await conn.fetchrow(stats_query, novel_id)

            # 高风险域对
            high_risk_query = """
                SELECT d1.code, d2.code, cc.intensity_level
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1 AND cc.intensity_level >= 8
                ORDER BY cc.intensity_level DESC
            """
            high_risk = await conn.fetch(high_risk_query, novel_id)
            high_risk_pairs = [(row['code'], row['code_1']) for row in high_risk]

            # 升级中的冲突
            escalating_query = """
                SELECT
                    cc.conflict_name,
                    cc.intensity_level,
                    cc.current_manifestation,
                    d1.name as primary_domain,
                    d2.name as secondary_domain
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1 AND cc.status = 'escalating'
                ORDER BY cc.intensity_level DESC
            """
            escalating = await conn.fetch(escalating_query, novel_id)

            # 可用的剧情钩子
            hooks_query = """
                SELECT
                    ph.title,
                    ph.drama_level,
                    ph.urgency_level,
                    d.name as domain_name
                FROM plot_hooks ph
                LEFT JOIN domains d ON ph.domain_id = d.id
                WHERE ph.novel_id = $1 AND ph.status = 'available'
                ORDER BY ph.drama_level DESC
                LIMIT 10
            """
            hooks = await conn.fetch(hooks_query, novel_id)

            return ConflictAnalysis(
                total_conflicts=stats['total_conflicts'],
                average_intensity=float(stats['avg_intensity'] or 0),
                high_risk_pairs=high_risk_pairs,
                escalating_conflicts=[dict(row) for row in escalating],
                available_hooks=[dict(row) for row in hooks]
            )

    async def get_conflict_heatmap_data(self, novel_id: int) -> Dict[str, Any]:
        """获取冲突热度图数据"""
        async with self.db_pool.acquire() as conn:
            # 获取域列表
            domains_query = """
                SELECT code, name FROM domains
                WHERE novel_id = $1 AND is_active = true
                ORDER BY sort_order
            """
            domains = await conn.fetch(domains_query, novel_id)

            # 获取冲突矩阵
            conflicts_query = """
                SELECT
                    d1.code as primary_code,
                    d2.code as secondary_code,
                    cc.intensity_level,
                    cc.conflict_type,
                    cc.status
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1
            """
            conflicts = await conn.fetch(conflicts_query, novel_id)

            # 构建热度图数据
            domain_codes = [d['code'] for d in domains]
            domain_names = {d['code']: d['name'] for d in domains}

            heatmap = {}
            for d1 in domain_codes:
                heatmap[d1] = {}
                for d2 in domain_codes:
                    if d1 == d2:
                        heatmap[d1][d2] = 0  # 自己对自己没有冲突
                    else:
                        heatmap[d1][d2] = 0  # 默认无冲突

            # 填充实际冲突数据
            for conflict in conflicts:
                primary = conflict['primary_code']
                secondary = conflict['secondary_code']
                intensity = conflict['intensity_level']

                heatmap[primary][secondary] = intensity
                heatmap[secondary][primary] = intensity  # 对称矩阵

            return {
                'domain_codes': domain_codes,
                'domain_names': domain_names,
                'heatmap': heatmap,
                'conflicts_detail': [dict(c) for c in conflicts]
            }


class PlotHookManager:
    """剧情钩子管理器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def create_hook(self, novel_id: int, hook_data: Dict[str, Any]) -> int:
        """创建剧情钩子"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO plot_hooks (
                    novel_id, domain_id, framework_id, element_id,
                    title, description, hook_type,
                    drama_level, scope, urgency_level,
                    potential_outcomes, involved_entities, required_capabilities,
                    follow_up_hooks, status
                ) VALUES (
                    $1,
                    (SELECT id FROM domains WHERE code = $2 AND novel_id = $1),
                    $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
                ) RETURNING id
            """
            hook_id = await conn.fetchval(
                query,
                novel_id,
                hook_data.get('domain_code'),
                hook_data.get('framework_id'),
                hook_data.get('element_id'),
                hook_data['title'],
                hook_data['description'],
                hook_data['hook_type'],
                hook_data.get('drama_level', 5),
                hook_data.get('scope', 'local'),
                hook_data.get('urgency_level', 3),
                hook_data.get('potential_outcomes', {}),
                hook_data.get('involved_entities', []),
                hook_data.get('required_capabilities', []),
                hook_data.get('follow_up_hooks', []),
                hook_data.get('status', 'available')
            )
            return hook_id

    async def get_hooks_by_conflict(self, novel_id: int, conflict_id: int) -> List[Dict[str, Any]]:
        """获取与特定冲突相关的钩子"""
        async with self.db_pool.acquire() as conn:
            # 先获取冲突涉及的域
            conflict_query = """
                SELECT primary_domain_id, secondary_domain_id
                FROM cultural_conflicts
                WHERE id = $1 AND novel_id = $2
            """
            conflict = await conn.fetchrow(conflict_query, conflict_id, novel_id)

            if not conflict:
                return []

            # 获取相关钩子
            hooks_query = """
                SELECT
                    ph.*,
                    d.name as domain_name,
                    d.code as domain_code
                FROM plot_hooks ph
                LEFT JOIN domains d ON ph.domain_id = d.id
                WHERE ph.novel_id = $1
                AND (ph.domain_id = $2 OR ph.domain_id = $3)
                ORDER BY ph.drama_level DESC, ph.urgency_level DESC
            """
            hooks = await conn.fetch(
                hooks_query,
                novel_id,
                conflict['primary_domain_id'],
                conflict['secondary_domain_id']
            )
            return [dict(hook) for hook in hooks]

    async def activate_hook(self, hook_id: int, event_id: int = None) -> bool:
        """激活剧情钩子"""
        async with self.db_pool.acquire() as conn:
            if event_id:
                query = """
                    UPDATE plot_hooks
                    SET status = 'in_use',
                        used_in_events = array_append(used_in_events, $2::text),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                """
                await conn.execute(query, hook_id, str(event_id))
            else:
                query = """
                    UPDATE plot_hooks
                    SET status = 'in_use', updated_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                """
                await conn.execute(query, hook_id)
            return True

    async def resolve_hook(self, hook_id: int, outcome: str) -> bool:
        """解决剧情钩子"""
        async with self.db_pool.acquire() as conn:
            query = """
                UPDATE plot_hooks
                SET status = 'resolved',
                    potential_outcomes = potential_outcomes || $2::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """
            await conn.execute(query, hook_id, f'{{"resolution": "{outcome}"}}')
            return True

    async def generate_hooks_for_conflict(self, novel_id: int, conflict_id: int,
                                        count: int = 3) -> List[int]:
        """为特定冲突生成新的剧情钩子"""
        async with self.db_pool.acquire() as conn:
            # 获取冲突详情
            conflict_query = """
                SELECT
                    cc.*,
                    d1.code as primary_code,
                    d2.code as secondary_code,
                    d1.name as primary_name,
                    d2.name as secondary_name
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.id = $1 AND cc.novel_id = $2
            """
            conflict = await conn.fetchrow(conflict_query, conflict_id, novel_id)

            if not conflict:
                return []

            # 基于冲突类型生成钩子模板
            hook_templates = self._generate_hook_templates(conflict)

            created_hooks = []
            for i, template in enumerate(hook_templates[:count]):
                hook_data = {
                    'domain_code': conflict['primary_code'],
                    'title': template['title'],
                    'description': template['description'],
                    'hook_type': template['hook_type'],
                    'drama_level': template['drama_level'],
                    'scope': template['scope'],
                    'urgency_level': template['urgency_level'],
                    'potential_outcomes': template['potential_outcomes'],
                    'involved_entities': template['involved_entities']
                }
                hook_id = await self.create_hook(novel_id, hook_data)
                created_hooks.append(hook_id)

            return created_hooks

    def _generate_hook_templates(self, conflict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据冲突生成钩子模板"""
        templates = []
        conflict_type = conflict['conflict_type']
        intensity = conflict['intensity_level']
        primary_name = conflict['primary_name']
        secondary_name = conflict['secondary_name']

        if conflict_type == 'power':
            templates.extend([
                {
                    'title': f'{primary_name}权力过度扩张',
                    'description': f'{primary_name}试图进一步扩大对{secondary_name}的控制，引发抵抗',
                    'hook_type': 'conflict',
                    'drama_level': min(intensity + 1, 10),
                    'scope': 'domain',
                    'urgency_level': 4,
                    'potential_outcomes': {
                        'success': f'{primary_name}成功扩大控制',
                        'failure': f'{secondary_name}成功抵抗',
                        'escalation': '冲突升级到更高层次'
                    },
                    'involved_entities': ['统治者', '抵抗者', '中立方']
                },
                {
                    'title': f'{secondary_name}秘密联盟',
                    'description': f'{secondary_name}秘密联合其他势力对抗{primary_name}的统治',
                    'hook_type': 'betrayal',
                    'drama_level': intensity,
                    'scope': 'cross_domain',
                    'urgency_level': 3,
                    'potential_outcomes': {
                        'exposure': '联盟被发现，遭到镇压',
                        'success': '联盟成功挑战统治',
                        'infiltration': '联盟内部被渗透'
                    },
                    'involved_entities': ['联盟领袖', '间谍', '忠诚派']
                }
            ])

        elif conflict_type == 'resource':
            templates.extend([
                {
                    'title': f'关键资源争夺战',
                    'description': f'{primary_name}与{secondary_name}为争夺稀缺资源发生直接冲突',
                    'hook_type': 'conflict',
                    'drama_level': intensity,
                    'scope': 'regional',
                    'urgency_level': 5,
                    'potential_outcomes': {
                        'victory': '一方获得资源控制权',
                        'compromise': '达成资源分享协议',
                        'devastation': '资源在争夺中被破坏'
                    },
                    'involved_entities': ['资源守护者', '争夺者', '商人']
                },
                {
                    'title': f'资源走私网络',
                    'description': f'秘密走私网络在{primary_name}和{secondary_name}间转移违禁资源',
                    'hook_type': 'mystery',
                    'drama_level': intensity - 1,
                    'scope': 'cross_domain',
                    'urgency_level': 3,
                    'potential_outcomes': {
                        'bust': '走私网络被破获',
                        'corruption': '发现官员参与走私',
                        'expansion': '走私网络扩大规模'
                    },
                    'involved_entities': ['走私者', '执法者', '腐败官员']
                }
            ])

        elif conflict_type == 'territory':
            templates.extend([
                {
                    'title': f'边境冲突升级',
                    'description': f'{primary_name}与{secondary_name}在边境地区发生武装冲突',
                    'hook_type': 'crisis',
                    'drama_level': intensity + 1,
                    'scope': 'regional',
                    'urgency_level': 5,
                    'potential_outcomes': {
                        'war': '冲突升级为全面战争',
                        'ceasefire': '达成停火协议',
                        'intervention': '第三方势力介入调停'
                    },
                    'involved_entities': ['边境守军', '难民', '调停者']
                }
            ])

        return templates