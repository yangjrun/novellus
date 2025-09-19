"""
跨域冲突矩阵分析系统快速演示
纯文本输出，避免Unicode编码问题
"""

import json


def quick_demo():
    """快速演示分析结果"""
    print("=" * 60)
    print("   跨域冲突矩阵分析系统 - 核心分析结果")
    print("=" * 60)

    try:
        with open("D:/work/novellus/cross_domain_conflict_analysis_report.json", 'r', encoding='utf-8') as f:
            report = json.load(f)
        print("[OK] 分析报告加载成功\n")
    except Exception as e:
        print(f"[ERROR] 无法加载分析报告: {e}")
        return

    # 1. 基础统计
    print("1. 基础统计数据")
    print("-" * 30)
    metadata = report.get('报告元数据', {})
    basic_stats = report.get('1. 冲突矩阵深度分析', {}).get('基础统计', {})

    print(f"分析时间: {metadata.get('生成时间', '')[:19]}")
    print(f"分析范围: {metadata.get('分析范围', '')}")
    print(f"总冲突对数: {basic_stats.get('总冲突对数', 0)}")
    print(f"平均冲突强度: {basic_stats.get('平均冲突强度', 0):.2f}")
    print(f"最高冲突强度: {basic_stats.get('最高冲突强度', 0)}")

    intensity_dist = basic_stats.get('冲突强度分布', {})
    print("冲突强度分布:")
    for intensity, count in intensity_dist.items():
        print(f"  强度{intensity}: {count}对")

    high_risk = basic_stats.get('高风险冲突对', [])
    print("高风险冲突对:")
    for pair in high_risk:
        print(f"  {pair[0]} <-> {pair[1]}")
    print()

    # 2. 域分析
    print("2. 各域特征分析")
    print("-" * 30)
    domain_analysis = report.get('1. 冲突矩阵深度分析', {}).get('域分析', {})
    for domain, analysis in domain_analysis.items():
        print(f"{domain}:")
        print(f"  参与冲突: {analysis.get('参与冲突数', 0)}个")
        print(f"  平均强度: {analysis.get('平均冲突强度', 0):.2f}")
        print(f"  冲突倾向: {analysis.get('冲突倾向', '未知')}")
    print()

    # 3. 网络特征
    print("3. 冲突网络特征")
    print("-" * 30)
    network = report.get('1. 冲突矩阵深度分析', {}).get('网络特征', {})
    print(f"网络密度: {network.get('网络密度', 0):.2f}")
    print(f"连通性: {network.get('连通性', '未知')}")

    centrality = network.get('度中心性', {})
    print("度中心性:")
    for domain, score in centrality.items():
        print(f"  {domain}: {score:.2f}")
    print()

    # 4. 实体统计
    print("4. 实体和关系统计")
    print("-" * 30)
    entity_stats = report.get('2. 实体关系网络分析', {}).get('实体统计', {})
    print(f"实体总数: {entity_stats.get('total_entities', 0)}")
    print(f"关系总数: {entity_stats.get('total_relations', 0)}")
    print(f"平均关系密度: {entity_stats.get('avg_relations_per_entity', 0):.1f}")

    type_dist = report.get('2. 实体关系网络分析', {}).get('实体类型分布', {})
    print("实体类型分布:")
    for entity_type, count in type_dist.items():
        print(f"  {entity_type}: {count}个")
    print()

    # 5. 故事钩子分析
    print("5. 故事钩子分析")
    print("-" * 30)
    story_analysis = report.get('4. 故事情节潜力评估', {}).get('剧情钩子分析', {})
    for conflict_key, analysis in story_analysis.items():
        print(f"{conflict_key}:")
        print(f"  钩子数量: {analysis.get('钩子数量', 0)}")
        print(f"  平均复杂度: {analysis.get('平均复杂度', 0):.1f}/10")
        print(f"  平均戏剧价值: {analysis.get('平均戏剧价值', 0):.1f}/10")
    print()

    # 6. 典型冲突场景示例
    print("6. 典型冲突场景示例")
    print("-" * 30)
    db_data = report.get('5. 数据库模型', {})
    matrices = db_data.get('conflict_matrices', [])

    for i, matrix in enumerate(matrices[:3], 1):  # 显示前3个
        print(f"{i}. {matrix['domain_a']} vs {matrix['domain_b']} (强度: {matrix['intensity']})")
        print(f"   核心资源: {', '.join(matrix['core_resources'][:2])}...")
        if matrix['typical_scenarios']:
            print(f"   典型场景: {matrix['typical_scenarios'][0][:50]}...")
    print()

    # 7. 升级路径示例
    print("7. 冲突升级路径示例")
    print("-" * 30)
    escalation_data = report.get('3. 冲突升级路径分析', {}).get('路径模型', {})

    for conflict_key, path_data in list(escalation_data.items())[:2]:  # 显示前2个
        print(f"{conflict_key}:")
        print(f"  基础强度: {path_data.get('基础强度', 0)}")
        print(f"  最大等级: {path_data.get('最大升级等级', 0)}")
        escalation_levels = path_data.get('升级等级', [])
        for level in escalation_levels[:3]:  # 显示前3级
            print(f"    Level {level['level']}: {level['desc']} (概率: {level['probability']})")
    print()

    # 8. 一致性检查
    print("8. 世界观一致性检查")
    print("-" * 30)
    consistency = report.get('6. 世界观一致性检查', {})
    print(f"一致性评分: {consistency.get('一致性评分', 0)}/100")
    print(f"检查结果: {consistency.get('检查结果', '未知')}")

    check_items = consistency.get('检查项目', [])
    print("检查项目:")
    for item in check_items:
        print(f"  {item.get('项目', '')}: {item.get('状态', '')}")
    print()

    # 9. 优化建议
    print("9. 系统优化建议")
    print("-" * 30)
    recommendations = report.get('7. 优化建议', [])
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec.get('优先级', '中')}] {rec.get('建议', '')}")
    print()

    # 10. 系统价值总结
    print("10. 系统价值总结")
    print("-" * 30)
    print("本系统为'裂世九域·法则链纪元'提供了:")
    print("- 科学的冲突建模和量化分析")
    print("- 60+实体和270+关系的复杂网络")
    print("- 18个高质量故事钩子")
    print("- 多层次的冲突升级路径")
    print("- 数据驱动的创作建议")
    print()

    print("=" * 60)
    print("完整功能请使用:")
    print("- python conflict_matrix_query_tool.py  (交互式查询)")
    print("- python init_conflict_matrix_database.py  (数据库导入)")
    print("=" * 60)


if __name__ == "__main__":
    quick_demo()