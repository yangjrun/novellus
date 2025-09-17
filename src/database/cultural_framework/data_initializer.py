"""
数据初始化和管理模块
提供跨域冲突矩阵的自动化初始化和管理功能
"""

import os
from typing import Dict, Any, List, Optional
import asyncpg
import asyncio
from pathlib import Path
from datetime import datetime

from .cross_domain_conflicts import CrossDomainConflictManager, PlotHookManager
from .cultural_elements_manager import CulturalElementManager, CulturalFrameworkManager
from .conflict_analyzer import ConflictAnalyzer


class ConflictMatrixInitializer:
    """冲突矩阵初始化器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.conflict_manager = CrossDomainConflictManager(db_pool)
        self.hook_manager = PlotHookManager(db_pool)
        self.element_manager = CulturalElementManager(db_pool)
        self.framework_manager = CulturalFrameworkManager(db_pool)
        self.analyzer = ConflictAnalyzer(db_pool)

    async def initialize_from_sql(self, novel_id: int, sql_file_path: str) -> Dict[str, Any]:
        """从SQL文件初始化数据"""
        try:
            # 读取SQL文件
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 替换小说ID占位符
            sql_content = sql_content.replace('novel_id = 1', f'novel_id = {novel_id}')
            sql_content = sql_content.replace('WHERE cf.novel_id = 1', f'WHERE cf.novel_id = {novel_id}')

            async with self.db_pool.acquire() as conn:
                # 执行SQL脚本
                await conn.execute(sql_content)

                # 验证数据
                verification = await self._verify_initialization(conn, novel_id)

                return {
                    'success': True,
                    'novel_id': novel_id,
                    'sql_file': sql_file_path,
                    'verification': verification,
                    'message': '冲突矩阵初始化成功'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '冲突矩阵初始化失败'
            }

    async def initialize_programmatically(self, novel_id: int,
                                        config: Dict[str, Any]) -> Dict[str, Any]:
        """通过代码初始化数据"""
        try:
            results = {
                'domains_created': 0,
                'conflicts_created': 0,
                'hooks_created': 0,
                'frameworks_created': 0,
                'elements_created': 0
            }

            # 1. 创建域
            if 'domains' in config:
                for domain_data in config['domains']:
                    await self._create_domain(novel_id, domain_data)
                    results['domains_created'] += 1

            # 2. 创建文化框架
            if 'frameworks' in config:
                for framework_data in config['frameworks']:
                    framework_id = await self.framework_manager.create_framework(
                        novel_id, framework_data
                    )
                    results['frameworks_created'] += 1

            # 3. 创建冲突
            if 'conflicts' in config:
                for conflict_data in config['conflicts']:
                    conflict_id = await self.conflict_manager.create_conflict(
                        novel_id, conflict_data
                    )
                    results['conflicts_created'] += 1

            # 4. 创建剧情钩子
            if 'plot_hooks' in config:
                for hook_data in config['plot_hooks']:
                    hook_id = await self.hook_manager.create_hook(novel_id, hook_data)
                    results['hooks_created'] += 1

            # 5. 创建文化要素
            if 'cultural_elements' in config:
                for element_data in config['cultural_elements']:
                    element_id = await self.element_manager.create_element(
                        novel_id, element_data
                    )
                    results['elements_created'] += 1

            return {
                'success': True,
                'novel_id': novel_id,
                'results': results,
                'message': '编程方式初始化成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '编程方式初始化失败'
            }

    async def create_default_conflict_matrix(self, novel_id: int) -> Dict[str, Any]:
        """创建默认的冲突矩阵（裂世九域）"""
        config = {
            'domains': [
                {
                    'code': 'ren_yu',
                    'name': '人域',
                    'display_name': '人族聚居域',
                    'dominant_law': '链籍法系',
                    'ruling_power': '乡绅里正体系',
                    'power_level': 4,
                    'civilization_level': 6,
                    'stability_level': 7,
                    'sort_order': 1
                },
                {
                    'code': 'tian_yu',
                    'name': '天域',
                    'display_name': '天链统御域',
                    'dominant_law': '环约律令',
                    'ruling_power': '御环台体系',
                    'power_level': 8,
                    'civilization_level': 9,
                    'stability_level': 6,
                    'sort_order': 2
                },
                {
                    'code': 'ling_yu',
                    'name': '灵域',
                    'display_name': '器工造化域',
                    'dominant_law': '工程链契',
                    'ruling_power': '宗匠公会体系',
                    'power_level': 7,
                    'civilization_level': 8,
                    'stability_level': 7,
                    'sort_order': 3
                },
                {
                    'code': 'huang_yu',
                    'name': '荒域',
                    'display_name': '断链部落域',
                    'dominant_law': '部落火典',
                    'ruling_power': '断链祭司体系',
                    'power_level': 6,
                    'civilization_level': 4,
                    'stability_level': 4,
                    'sort_order': 4
                }
            ],
            'conflicts': [
                {
                    'primary_domain_code': 'tian_yu',
                    'secondary_domain_code': 'ren_yu',
                    'conflict_type': 'power',
                    'conflict_name': '税役征收冲突',
                    'description': '天域通过链籍制度对人域实施严格的税收和人役征收，引发民众不满',
                    'intensity_level': 8,
                    'status': 'ongoing'
                },
                {
                    'primary_domain_code': 'tian_yu',
                    'secondary_domain_code': 'ling_yu',
                    'conflict_type': 'power',
                    'conflict_name': '评印权争夺',
                    'description': '天域试图控制灵域的技术标准和评印权，与宗匠自治传统冲突',
                    'intensity_level': 7,
                    'status': 'escalating'
                },
                {
                    'primary_domain_code': 'tian_yu',
                    'secondary_domain_code': 'huang_yu',
                    'conflict_type': 'territory',
                    'conflict_name': '边域控制争端',
                    'description': '天域军镇与荒域部落在边境资源和断链者庇护问题上长期对立',
                    'intensity_level': 9,
                    'status': 'escalating'
                }
            ],
            'plot_hooks': [
                {
                    'domain_code': 'tian_yu',
                    'title': '黑籍配额暗增',
                    'description': '链祭日前夕，县府突然增加"黑籍配额"，里社档册被秘密修改',
                    'hook_type': 'crisis',
                    'drama_level': 8,
                    'urgency_level': 4
                },
                {
                    'domain_code': 'ling_yu',
                    'title': '界核招标内幕',
                    'description': '御前项目"界核·九阶"招标中，技术标准被指控为利益输送',
                    'hook_type': 'conflict',
                    'drama_level': 9,
                    'urgency_level': 4
                }
            ]
        }

        return await self.initialize_programmatically(novel_id, config)

    async def export_conflict_data(self, novel_id: int,
                                 export_format: str = 'json') -> Dict[str, Any]:
        """导出冲突数据"""
        try:
            # 获取所有相关数据
            matrix = await self.conflict_manager.get_conflict_matrix(novel_id)
            conflicts = await self.conflict_manager.get_conflicts_by_domain(novel_id, None)
            analysis = await self.analyzer.generate_conflict_report(novel_id)

            export_data = {
                'novel_id': novel_id,
                'exported_at': datetime.utcnow().isoformat(),
                'conflict_matrix': {
                    'domain_pairs': matrix.domain_pairs,
                    'intensities': matrix.intensities,
                    'conflict_types': matrix.conflict_types,
                    'current_status': matrix.current_status
                },
                'conflicts': conflicts,
                'analysis': analysis
            }

            if export_format == 'json':
                return {
                    'success': True,
                    'format': 'json',
                    'data': export_data
                }
            elif export_format == 'sql':
                sql_data = await self._generate_sql_export(export_data)
                return {
                    'success': True,
                    'format': 'sql',
                    'data': sql_data
                }
            else:
                raise ValueError(f"不支持的导出格式: {export_format}")

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '导出失败'
            }

    async def backup_conflict_data(self, novel_id: int, backup_name: str) -> Dict[str, Any]:
        """备份冲突数据"""
        try:
            # 导出数据
            export_result = await self.export_conflict_data(novel_id, 'json')

            if not export_result['success']:
                return export_result

            # 保存备份
            backup_data = {
                'backup_name': backup_name,
                'created_at': datetime.utcnow().isoformat(),
                'novel_id': novel_id,
                'data': export_result['data']
            }

            async with self.db_pool.acquire() as conn:
                # 假设有备份表
                backup_query = """
                    INSERT INTO conflict_backups (novel_id, backup_name, backup_data, created_at)
                    VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                    RETURNING id
                """
                try:
                    backup_id = await conn.fetchval(
                        backup_query, novel_id, backup_name, backup_data
                    )
                    return {
                        'success': True,
                        'backup_id': backup_id,
                        'backup_name': backup_name,
                        'message': '备份创建成功'
                    }
                except asyncpg.UndefinedTableError:
                    # 如果备份表不存在，创建文件备份
                    return await self._create_file_backup(backup_data, backup_name)

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '备份失败'
            }

    async def restore_conflict_data(self, novel_id: int, backup_name: str) -> Dict[str, Any]:
        """恢复冲突数据"""
        try:
            async with self.db_pool.acquire() as conn:
                # 获取备份数据
                backup_query = """
                    SELECT backup_data FROM conflict_backups
                    WHERE novel_id = $1 AND backup_name = $2
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                backup_record = await conn.fetchrow(backup_query, novel_id, backup_name)

                if not backup_record:
                    return {
                        'success': False,
                        'message': f'未找到备份: {backup_name}'
                    }

                backup_data = backup_record['backup_data']

                # 清理现有数据
                await self._cleanup_existing_data(conn, novel_id)

                # 恢复数据
                restore_result = await self._restore_from_backup(backup_data)

                return {
                    'success': True,
                    'backup_name': backup_name,
                    'restore_result': restore_result,
                    'message': '数据恢复成功'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '数据恢复失败'
            }

    async def _create_domain(self, novel_id: int, domain_data: Dict[str, Any]) -> int:
        """创建域"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO domains (
                    novel_id, name, code, display_name, dominant_law, ruling_power,
                    power_level, civilization_level, stability_level, sort_order
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
            """
            domain_id = await conn.fetchval(
                query,
                novel_id,
                domain_data['name'],
                domain_data['code'],
                domain_data['display_name'],
                domain_data['dominant_law'],
                domain_data['ruling_power'],
                domain_data['power_level'],
                domain_data['civilization_level'],
                domain_data['stability_level'],
                domain_data['sort_order']
            )
            return domain_id

    async def _verify_initialization(self, conn: asyncpg.Connection,
                                   novel_id: int) -> Dict[str, Any]:
        """验证初始化结果"""
        # 统计数据
        domains_count = await conn.fetchval(
            "SELECT COUNT(*) FROM domains WHERE novel_id = $1", novel_id
        )
        conflicts_count = await conn.fetchval(
            "SELECT COUNT(*) FROM cultural_conflicts WHERE novel_id = $1", novel_id
        )
        hooks_count = await conn.fetchval(
            "SELECT COUNT(*) FROM plot_hooks WHERE novel_id = $1", novel_id
        )
        frameworks_count = await conn.fetchval(
            "SELECT COUNT(*) FROM cultural_frameworks WHERE novel_id = $1", novel_id
        )
        elements_count = await conn.fetchval(
            "SELECT COUNT(*) FROM cultural_elements WHERE novel_id = $1", novel_id
        )

        return {
            'domains': domains_count,
            'conflicts': conflicts_count,
            'plot_hooks': hooks_count,
            'frameworks': frameworks_count,
            'cultural_elements': elements_count,
            'total_records': (domains_count + conflicts_count + hooks_count +
                            frameworks_count + elements_count)
        }

    async def _generate_sql_export(self, export_data: Dict[str, Any]) -> str:
        """生成SQL导出"""
        sql_lines = [
            "-- 冲突矩阵数据导出",
            f"-- 导出时间: {export_data['exported_at']}",
            f"-- 小说ID: {export_data['novel_id']}",
            ""
        ]

        # 这里可以添加生成SQL INSERT语句的逻辑
        # 暂时返回简化版本
        sql_lines.append("-- SQL导出功能待完善")

        return "\n".join(sql_lines)

    async def _create_file_backup(self, backup_data: Dict[str, Any],
                                backup_name: str) -> Dict[str, Any]:
        """创建文件备份"""
        import json
        from datetime import datetime

        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{backup_name}_{timestamp}.json"
        filepath = backup_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        return {
            'success': True,
            'backup_file': str(filepath),
            'message': '文件备份创建成功'
        }

    async def _cleanup_existing_data(self, conn: asyncpg.Connection, novel_id: int):
        """清理现有数据"""
        # 按依赖关系顺序删除
        await conn.execute("DELETE FROM cultural_elements WHERE novel_id = $1", novel_id)
        await conn.execute("DELETE FROM plot_hooks WHERE novel_id = $1", novel_id)
        await conn.execute("DELETE FROM cultural_conflicts WHERE novel_id = $1", novel_id)
        await conn.execute("DELETE FROM cultural_frameworks WHERE novel_id = $1", novel_id)
        await conn.execute("DELETE FROM domains WHERE novel_id = $1", novel_id)

    async def _restore_from_backup(self, backup_data: Dict[str, Any]) -> Dict[str, Any]:
        """从备份恢复数据"""
        # 这里应该实现完整的恢复逻辑
        # 暂时返回简化版本
        return {
            'restored_tables': ['domains', 'conflicts', 'plot_hooks'],
            'records_restored': 0
        }


class ConflictMatrixManager:
    """冲突矩阵统一管理器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.initializer = ConflictMatrixInitializer(db_pool)
        self.conflict_manager = CrossDomainConflictManager(db_pool)
        self.analyzer = ConflictAnalyzer(db_pool)

    async def get_system_status(self, novel_id: int) -> Dict[str, Any]:
        """获取系统状态"""
        async with self.db_pool.acquire() as conn:
            # 数据统计
            verification = await self.initializer._verify_initialization(conn, novel_id)

            # 分析状态
            analysis = await self.analyzer.analyze_conflicts(novel_id)

            # 系统健康度
            health_score = self._calculate_health_score(verification, analysis)

            return {
                'novel_id': novel_id,
                'data_statistics': verification,
                'conflict_analysis': {
                    'total_conflicts': analysis.total_conflicts,
                    'average_intensity': analysis.average_intensity,
                    'high_risk_pairs_count': len(analysis.high_risk_pairs),
                    'escalating_conflicts_count': len(analysis.escalating_conflicts),
                    'available_hooks_count': len(analysis.available_hooks)
                },
                'health_score': health_score,
                'recommendations': self._generate_system_recommendations(verification, analysis)
            }

    def _calculate_health_score(self, verification: Dict, analysis) -> float:
        """计算系统健康度"""
        # 基于数据完整性和冲突状态计算
        data_score = min(100, verification['total_records'] * 2)  # 数据完整性

        if analysis.total_conflicts > 0:
            conflict_score = max(0, 100 - (analysis.average_intensity * 10))  # 冲突强度
        else:
            conflict_score = 100

        return (data_score * 0.4 + conflict_score * 0.6)

    def _generate_system_recommendations(self, verification: Dict, analysis) -> List[str]:
        """生成系统建议"""
        recommendations = []

        if verification['total_records'] < 20:
            recommendations.append("数据量较少，建议添加更多文化要素和剧情钩子")

        if analysis.average_intensity > 7:
            recommendations.append("冲突强度过高，建议采取缓解措施")

        if len(analysis.available_hooks) < 5:
            recommendations.append("可用剧情钩子不足，建议生成更多钩子")

        return recommendations