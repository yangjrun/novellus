# -*- coding: utf-8 -*-
"""
文化框架系统 - 跨域冲突矩阵模块
提供完整的跨域冲突管理、分析和剧情生成功能
"""

from .cross_domain_conflicts import (
    CrossDomainConflictManager,
    PlotHookManager,
    ConflictMatrix,
    ConflictAnalysis
)

from .cultural_elements_manager import (
    CulturalElementManager,
    CulturalFrameworkManager
)

from .conflict_analyzer import (
    ConflictAnalyzer,
    TrendAnalysis,
    ConflictCluster,
    PlotOpportunity
)

from .data_initializer import (
    ConflictMatrixInitializer,
    ConflictMatrixManager
)

__all__ = [
    # 冲突管理
    'CrossDomainConflictManager',
    'PlotHookManager',
    'ConflictMatrix',
    'ConflictAnalysis',

    # 文化要素管理
    'CulturalElementManager',
    'CulturalFrameworkManager',

    # 分析工具
    'ConflictAnalyzer',
    'TrendAnalysis',
    'ConflictCluster',
    'PlotOpportunity',

    # 初始化管理
    'ConflictMatrixInitializer',
    'ConflictMatrixManager'
]


# 便捷函数
async def create_conflict_matrix_system(db_pool, novel_id: int):
    """创建完整的冲突矩阵系统"""
    manager = ConflictMatrixManager(db_pool)
    initializer = ConflictMatrixInitializer(db_pool)

    # 初始化默认数据
    result = await initializer.create_default_conflict_matrix(novel_id)

    if result['success']:
        # 获取系统状态
        status = await manager.get_system_status(novel_id)
        return {
            'system_created': True,
            'initialization_result': result,
            'system_status': status
        }
    else:
        return {
            'system_created': False,
            'error': result.get('error', '未知错误')
        }


async def get_conflict_overview(db_pool, novel_id: int):
    """获取冲突概览"""
    analyzer = ConflictAnalyzer(db_pool)
    conflict_manager = CrossDomainConflictManager(db_pool)

    # 生成综合报告
    report = await analyzer.generate_conflict_report(novel_id)

    # 获取冲突矩阵
    matrix = await conflict_manager.get_conflict_matrix(novel_id)

    # 获取热度图数据
    heatmap = await conflict_manager.get_conflict_heatmap_data(novel_id)

    return {
        'report': report,
        'matrix': {
            'domain_pairs': matrix.domain_pairs,
            'intensities': matrix.intensities,
            'conflict_types': matrix.conflict_types,
            'current_status': matrix.current_status
        },
        'heatmap': heatmap
    }