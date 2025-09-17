"""
冲突矩阵分析工具
提供复杂的冲突分析、趋势预测和剧情生成功能
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncpg
import json
from collections import defaultdict


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    trend_direction: str  # 'escalating', 'de-escalating', 'stable'
    intensity_change: float
    prediction_confidence: float
    key_factors: List[str]
    recommended_actions: List[str]


@dataclass
class ConflictCluster:
    """冲突集群"""
    cluster_id: str
    domains: List[str]
    total_intensity: int
    cluster_type: str  # 'alliance', 'opposition', 'complex'
    stability: float
    key_conflicts: List[Dict[str, Any]]


@dataclass
class PlotOpportunity:
    """剧情机会"""
    opportunity_type: str
    description: str
    involved_domains: List[str]
    drama_potential: int
    urgency: int
    suggested_hooks: List[str]
    prerequisites: List[str]


class ConflictAnalyzer:
    """冲突分析器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def analyze_conflict_trends(self, novel_id: int,
                                    time_window_days: int = 30) -> Dict[str, TrendAnalysis]:
        """分析冲突趋势"""
        async with self.db_pool.acquire() as conn:
            # 获取历史冲突数据（模拟）
            conflicts_query = """
                SELECT
                    cc.*,
                    d1.code as primary_code,
                    d2.code as secondary_code,
                    d1.name as primary_name,
                    d2.name as secondary_name
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1
                ORDER BY cc.updated_at DESC
            """
            conflicts = await conn.fetch(conflicts_query, novel_id)

            trends = {}
            for conflict in conflicts:
                pair_key = f"{conflict['primary_code']}-{conflict['secondary_code']}"

                # 分析趋势（基于强度和状态）
                trend_direction = self._analyze_trend_direction(conflict)
                intensity_change = self._calculate_intensity_change(conflict)
                confidence = self._calculate_prediction_confidence(conflict)
                key_factors = self._identify_key_factors(conflict)
                recommendations = self._generate_recommendations(conflict)

                trends[pair_key] = TrendAnalysis(
                    trend_direction=trend_direction,
                    intensity_change=intensity_change,
                    prediction_confidence=confidence,
                    key_factors=key_factors,
                    recommended_actions=recommendations
                )

            return trends

    async def identify_conflict_clusters(self, novel_id: int) -> List[ConflictCluster]:
        """识别冲突集群"""
        async with self.db_pool.acquire() as conn:
            # 获取冲突网络数据
            conflicts_query = """
                SELECT
                    cc.*,
                    d1.code as primary_code,
                    d1.name as primary_name,
                    d2.code as secondary_code,
                    d2.name as secondary_name
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1
            """
            conflicts = await conn.fetch(conflicts_query, novel_id)

            # 构建冲突图
            conflict_graph = defaultdict(list)
            domain_conflicts = defaultdict(list)

            for conflict in conflicts:
                primary = conflict['primary_code']
                secondary = conflict['secondary_code']

                conflict_graph[primary].append({
                    'target': secondary,
                    'intensity': conflict['intensity_level'],
                    'type': conflict['conflict_type'],
                    'conflict': dict(conflict)
                })

                domain_conflicts[primary].append(conflict['intensity_level'])
                domain_conflicts[secondary].append(conflict['intensity_level'])

            # 识别集群
            clusters = []
            visited = set()

            for domain in conflict_graph:
                if domain in visited:
                    continue

                cluster = self._find_conflict_cluster(domain, conflict_graph, visited)
                if len(cluster['domains']) >= 2:  # 至少包含2个域
                    clusters.append(cluster)

            return clusters

    async def find_plot_opportunities(self, novel_id: int) -> List[PlotOpportunity]:
        """发现剧情机会"""
        async with self.db_pool.acquire() as conn:
            opportunities = []

            # 1. 基于高强度冲突的机会
            high_conflict_query = """
                SELECT
                    cc.*,
                    d1.code as primary_code,
                    d1.name as primary_name,
                    d2.code as secondary_code,
                    d2.name as secondary_name
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1 AND cc.intensity_level >= 8
                ORDER BY cc.intensity_level DESC
            """
            high_conflicts = await conn.fetch(high_conflict_query, novel_id)

            for conflict in high_conflicts:
                opportunity = PlotOpportunity(
                    opportunity_type='crisis_escalation',
                    description=f"{conflict['primary_name']}与{conflict['secondary_name']}的{conflict['conflict_name']}即将达到临界点",
                    involved_domains=[conflict['primary_code'], conflict['secondary_code']],
                    drama_potential=conflict['intensity_level'],
                    urgency=5,
                    suggested_hooks=[
                        f"突发事件导致{conflict['conflict_name']}全面爆发",
                        f"第三方势力试图利用{conflict['conflict_name']}获利",
                        f"内部叛徒加剧{conflict['conflict_name']}"
                    ],
                    prerequisites=[f"冲突强度达到{conflict['intensity_level']}"]
                )
                opportunities.append(opportunity)

            # 2. 基于文化要素冲突的机会
            element_conflicts_query = """
                SELECT
                    ce1.name as element1_name,
                    ce1.element_type as element1_type,
                    d1.code as domain1_code,
                    d1.name as domain1_name,
                    ce2.name as element2_name,
                    ce2.element_type as element2_type,
                    d2.code as domain2_code,
                    d2.name as domain2_name,
                    ce1.importance + ce2.importance as total_importance
                FROM cultural_elements ce1
                JOIN cultural_frameworks cf1 ON ce1.framework_id = cf1.id
                JOIN domains d1 ON cf1.domain_id = d1.id
                JOIN cultural_elements ce2 ON ce1.novel_id = ce2.novel_id
                JOIN cultural_frameworks cf2 ON ce2.framework_id = cf2.id
                JOIN domains d2 ON cf2.domain_id = d2.id
                WHERE ce1.novel_id = $1
                AND ce1.id < ce2.id
                AND d1.id != d2.id
                AND ce1.element_type = ce2.element_type
                AND ce1.status = 'active' AND ce2.status = 'active'
                ORDER BY total_importance DESC
                LIMIT 5
            """
            element_conflicts = await conn.fetch(element_conflicts_query, novel_id)

            for ec in element_conflicts:
                opportunity = PlotOpportunity(
                    opportunity_type='cultural_clash',
                    description=f"{ec['domain1_name']}的{ec['element1_name']}与{ec['domain2_name']}的{ec['element2_name']}产生文化冲突",
                    involved_domains=[ec['domain1_code'], ec['domain2_code']],
                    drama_potential=min(10, ec['total_importance']),
                    urgency=3,
                    suggested_hooks=[
                        f"两种{ec['element1_type']}制度发生直接冲突",
                        f"跨域人员因文化差异发生误解",
                        f"古老传统与新制度的碰撞"
                    ],
                    prerequisites=[f"涉及{ec['element1_type']}类型的文化要素"]
                )
                opportunities.append(opportunity)

            # 3. 基于可用剧情钩子的机会
            available_hooks_query = """
                SELECT
                    ph.*,
                    d.code as domain_code,
                    d.name as domain_name
                FROM plot_hooks ph
                LEFT JOIN domains d ON ph.domain_id = d.id
                WHERE ph.novel_id = $1 AND ph.status = 'available'
                AND ph.drama_level >= 7
                ORDER BY ph.drama_level DESC, ph.urgency_level DESC
                LIMIT 10
            """
            available_hooks = await conn.fetch(available_hooks_query, novel_id)

            for hook in available_hooks:
                opportunity = PlotOpportunity(
                    opportunity_type='ready_plot',
                    description=f"现成剧情钩子：{hook['title']}",
                    involved_domains=[hook['domain_code']] if hook['domain_code'] else [],
                    drama_potential=hook['drama_level'],
                    urgency=hook['urgency_level'],
                    suggested_hooks=[hook['title']],
                    prerequisites=hook['required_capabilities'] or []
                )
                opportunities.append(opportunity)

            return opportunities

    async def generate_conflict_report(self, novel_id: int) -> Dict[str, Any]:
        """生成综合冲突报告"""
        async with self.db_pool.acquire() as conn:
            # 基础统计
            basic_stats_query = """
                SELECT
                    COUNT(*) as total_conflicts,
                    AVG(intensity_level) as avg_intensity,
                    MAX(intensity_level) as max_intensity,
                    COUNT(CASE WHEN status = 'escalating' THEN 1 END) as escalating_count,
                    COUNT(CASE WHEN intensity_level >= 8 THEN 1 END) as critical_count
                FROM cultural_conflicts
                WHERE novel_id = $1
            """
            basic_stats = await conn.fetchrow(basic_stats_query, novel_id)

            # 域间关系网络
            network_query = """
                SELECT
                    d1.name as domain1,
                    d2.name as domain2,
                    cc.intensity_level,
                    cc.conflict_type,
                    cc.status
                FROM cultural_conflicts cc
                JOIN domains d1 ON cc.primary_domain_id = d1.id
                JOIN domains d2 ON cc.secondary_domain_id = d2.id
                WHERE cc.novel_id = $1
                ORDER BY cc.intensity_level DESC
            """
            network_data = await conn.fetch(network_query, novel_id)

            # 冲突类型分布
            type_distribution_query = """
                SELECT
                    conflict_type,
                    COUNT(*) as count,
                    AVG(intensity_level) as avg_intensity
                FROM cultural_conflicts
                WHERE novel_id = $1
                GROUP BY conflict_type
                ORDER BY count DESC
            """
            type_distribution = await conn.fetch(type_distribution_query, novel_id)

            # 剧情钩子统计
            hooks_stats_query = """
                SELECT
                    status,
                    COUNT(*) as count,
                    AVG(drama_level) as avg_drama
                FROM plot_hooks
                WHERE novel_id = $1
                GROUP BY status
                ORDER BY count DESC
            """
            hooks_stats = await conn.fetch(hooks_stats_query, novel_id)

            # 文化要素冲突分析
            element_conflicts = await self._analyze_element_conflicts(conn, novel_id)

            # 趋势分析
            trends = await self.analyze_conflict_trends(novel_id)

            # 冲突集群
            clusters = await self.identify_conflict_clusters(novel_id)

            # 剧情机会
            opportunities = await self.find_plot_opportunities(novel_id)

            return {
                'generated_at': datetime.utcnow().isoformat(),
                'novel_id': novel_id,
                'basic_statistics': dict(basic_stats),
                'network_data': [dict(row) for row in network_data],
                'type_distribution': [dict(row) for row in type_distribution],
                'hooks_statistics': [dict(row) for row in hooks_stats],
                'element_conflicts': element_conflicts,
                'trends_analysis': {k: {
                    'direction': v.trend_direction,
                    'intensity_change': v.intensity_change,
                    'confidence': v.prediction_confidence,
                    'key_factors': v.key_factors,
                    'recommendations': v.recommended_actions
                } for k, v in trends.items()},
                'conflict_clusters': [{
                    'id': c.cluster_id,
                    'domains': c.domains,
                    'intensity': c.total_intensity,
                    'type': c.cluster_type,
                    'stability': c.stability
                } for c in clusters],
                'plot_opportunities': [{
                    'type': op.opportunity_type,
                    'description': op.description,
                    'domains': op.involved_domains,
                    'drama_potential': op.drama_potential,
                    'urgency': op.urgency,
                    'suggested_hooks': op.suggested_hooks,
                    'prerequisites': op.prerequisites
                } for op in opportunities],
                'recommendations': self._generate_global_recommendations(
                    basic_stats, trends, clusters, opportunities
                )
            }

    def _analyze_trend_direction(self, conflict: Dict[str, Any]) -> str:
        """分析冲突趋势方向"""
        intensity = conflict['intensity_level']
        status = conflict['status']

        if status == 'escalating' or intensity >= 9:
            return 'escalating'
        elif status == 'de-escalating' or intensity <= 3:
            return 'de-escalating'
        else:
            return 'stable'

    def _calculate_intensity_change(self, conflict: Dict[str, Any]) -> float:
        """计算强度变化（模拟）"""
        # 实际实现中应该基于历史数据计算
        intensity = conflict['intensity_level']
        status = conflict['status']

        if status == 'escalating':
            return min(2.0, 10 - intensity)
        elif status == 'de-escalating':
            return max(-2.0, 1 - intensity)
        else:
            return 0.0

    def _calculate_prediction_confidence(self, conflict: Dict[str, Any]) -> float:
        """计算预测置信度"""
        # 基于冲突的历史深度和数据完整性
        historical_depth = conflict.get('historical_depth', 1)
        return min(1.0, 0.5 + (historical_depth * 0.1))

    def _identify_key_factors(self, conflict: Dict[str, Any]) -> List[str]:
        """识别关键因素"""
        factors = []

        if conflict['intensity_level'] >= 8:
            factors.append('高强度冲突')

        if conflict['status'] == 'escalating':
            factors.append('持续升级')

        if conflict['conflict_type'] == 'power':
            factors.append('权力争夺')
        elif conflict['conflict_type'] == 'resource':
            factors.append('资源稀缺')
        elif conflict['conflict_type'] == 'territory':
            factors.append('领土争端')

        return factors

    def _generate_recommendations(self, conflict: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []

        if conflict['intensity_level'] >= 8:
            recommendations.append('紧急介入以防止冲突升级')
            recommendations.append('启动危机管理机制')

        if conflict['status'] == 'escalating':
            recommendations.append('寻找调解第三方')
            recommendations.append('识别共同利益点')

        if conflict['conflict_type'] == 'resource':
            recommendations.append('探索资源共享方案')
            recommendations.append('开发替代资源')

        return recommendations

    def _find_conflict_cluster(self, start_domain: str, conflict_graph: Dict,
                             visited: set) -> ConflictCluster:
        """查找冲突集群"""
        cluster_domains = set([start_domain])
        total_intensity = 0
        key_conflicts = []

        # 简单的深度优先搜索
        stack = [start_domain]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)

            for edge in conflict_graph.get(current, []):
                target = edge['target']
                intensity = edge['intensity']

                if intensity >= 6:  # 只考虑中高强度冲突
                    cluster_domains.add(target)
                    total_intensity += intensity
                    key_conflicts.append(edge['conflict'])

                    if target not in visited:
                        stack.append(target)

        # 确定集群类型
        if len(cluster_domains) == 2:
            cluster_type = 'opposition'
        elif len(cluster_domains) <= 4:
            cluster_type = 'alliance'
        else:
            cluster_type = 'complex'

        # 计算稳定性（基于冲突强度的方差）
        if key_conflicts:
            intensities = [c['intensity_level'] for c in key_conflicts]
            avg_intensity = sum(intensities) / len(intensities)
            variance = sum((i - avg_intensity) ** 2 for i in intensities) / len(intensities)
            stability = max(0, 1 - (variance / 25))  # 归一化到0-1
        else:
            stability = 1.0

        return ConflictCluster(
            cluster_id=f"cluster_{len(cluster_domains)}_{start_domain}",
            domains=list(cluster_domains),
            total_intensity=total_intensity,
            cluster_type=cluster_type,
            stability=stability,
            key_conflicts=key_conflicts
        )

    async def _analyze_element_conflicts(self, conn: asyncpg.Connection,
                                       novel_id: int) -> Dict[str, Any]:
        """分析文化要素冲突"""
        query = """
            SELECT
                ce1.element_type,
                COUNT(*) as conflict_count,
                AVG(ce1.importance + ce2.importance) as avg_importance
            FROM cultural_elements ce1
            JOIN cultural_frameworks cf1 ON ce1.framework_id = cf1.id
            JOIN domains d1 ON cf1.domain_id = d1.id
            JOIN cultural_elements ce2 ON ce1.novel_id = ce2.novel_id
            JOIN cultural_frameworks cf2 ON ce2.framework_id = cf2.id
            JOIN domains d2 ON cf2.domain_id = d2.id
            WHERE ce1.novel_id = $1
            AND ce1.id < ce2.id
            AND d1.id != d2.id
            AND ce1.element_type = ce2.element_type
            AND ce1.status = 'active' AND ce2.status = 'active'
            GROUP BY ce1.element_type
            ORDER BY conflict_count DESC
        """
        conflicts = await conn.fetch(query, novel_id)

        return {
            'by_type': [dict(row) for row in conflicts],
            'total_conflicts': sum(row['conflict_count'] for row in conflicts)
        }

    def _generate_global_recommendations(self, basic_stats: Dict, trends: Dict,
                                       clusters: List, opportunities: List) -> List[str]:
        """生成全局建议"""
        recommendations = []

        critical_count = basic_stats['critical_count']
        avg_intensity = basic_stats['avg_intensity']

        if critical_count > 0:
            recommendations.append(f"有{critical_count}个危险冲突需要立即关注")

        if avg_intensity > 7:
            recommendations.append("整体冲突强度过高，需要系统性干预")

        escalating_trends = sum(1 for t in trends.values() if t.trend_direction == 'escalating')
        if escalating_trends > len(trends) * 0.3:
            recommendations.append("多个冲突呈升级趋势，建议预防性措施")

        if len(clusters) > 2:
            recommendations.append("冲突集群化严重，可能引发连锁反应")

        high_drama_opportunities = sum(1 for op in opportunities if op.drama_potential >= 8)
        if high_drama_opportunities > 0:
            recommendations.append(f"发现{high_drama_opportunities}个高戏剧性剧情机会")

        return recommendations