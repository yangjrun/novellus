"""
跨域冲突矩阵分析系统演示脚本
展示系统的核心功能和分析结果
"""

from conflict_matrix_query_tool import ConflictMatrixQueryTool
import json


def demo_conflict_analysis():
    """演示冲突分析系统功能"""
    print("=" * 60)
    print("     裂世九域跨域冲突矩阵分析系统演示")
    print("=" * 60)

    # 初始化查询工具
    try:
        tool = ConflictMatrixQueryTool("D:/work/novellus/cross_domain_conflict_analysis_report.json")
        print("[OK] 分析数据加载成功\n")
    except Exception as e:
        print(f"[ERROR] 数据加载失败: {e}")
        return

    # 1. 显示系统概要
    print("1. 系统概要")
    print("-" * 40)
    summary = tool.get_conflict_matrix_summary()
    basic_stats = summary['总体概况']

    print(f"分析范围: {basic_stats['分析范围']}")
    print(f"总冲突对数: {basic_stats['总冲突对数']}")
    print(f"平均冲突强度: {basic_stats['平均冲突强度']}")
    print(f"最高冲突强度: {basic_stats['最高冲突强度']}")

    high_risk = summary['高风险冲突对']
    print(f"高风险冲突对: {', '.join([f'{pair[0]}<->{pair[1]}' for pair in high_risk])}")
    print()

    # 2. 冲突强度排名
    print("2. 冲突强度排名")
    print("-" * 40)
    ranking = tool.get_conflict_intensity_ranking()
    for rank in ranking:
        print(f"{rank['排名']}. {rank['冲突对']} - 强度: {rank['强度']} ({rank['风险等级']})")
    print()

    # 3. 各域特征分析
    print("3. 各域特征分析")
    print("-" * 40)
    domain_analysis = tool.get_domain_analysis()
    for domain, analysis in domain_analysis.items():
        print(f"{domain}: {analysis['冲突倾向']}")
        print(f"  参与冲突: {analysis['参与冲突数']}个")
        print(f"  平均强度: {analysis['平均冲突强度']:.2f}")
        print(f"  最高强度: {analysis['最高冲突强度']}")
    print()

    # 4. 展示高价值冲突详情
    print("4. 高风险冲突详情: 人域↔天域")
    print("-" * 40)
    conflict_details = tool.get_conflict_pair_details("人域", "天域")
    if "error" not in conflict_details:
        print(f"冲突强度: {conflict_details['冲突强度']}")
        print(f"核心资源: {', '.join(conflict_details['核心资源'])}")
        print(f"触发法条: {', '.join(conflict_details['触发法条'])}")
        print("典型场景:")
        for i, scenario in enumerate(conflict_details['典型场景'], 1):
            print(f"  {i}. {scenario}")
    print()

    # 5. 升级路径分析
    print("5. 冲突升级路径: 人域↔天域")
    print("-" * 40)
    escalation = tool.get_escalation_analysis("人域", "天域")
    if "error" not in escalation:
        path_data = escalation['路径详情']
        print(f"基础强度: {path_data['基础强度']}")
        print(f"最大升级等级: {path_data['最大升级等级']}")
        print(f"总体风险: {path_data['总体风险']:.2f}")
        print("升级等级:")
        for level in path_data['升级等级']:
            print(f"  Level {level['level']}: {level['desc']} (概率: {level['probability']})")
    print()

    # 6. 故事钩子展示
    print("6. 高价值故事钩子")
    print("-" * 40)
    hooks = tool.get_story_hooks()
    high_value_hooks = [h for h in hooks if h['戏剧价值'] >= 7]
    for i, hook in enumerate(high_value_hooks[:5], 1):
        print(f"{i}. {hook['标题']}")
        print(f"   描述: {hook['描述']}")
        print(f"   类型: {hook['类型']}, 戏剧价值: {hook['戏剧价值']}/10")
        print(f"   涉及域: {', '.join(hook['涉及域'])}")
        print()

    # 7. 故事潜力排名
    print("7. 故事潜力排名")
    print("-" * 40)
    story_ranking = tool.get_story_potential_ranking()
    for item in story_ranking:
        print(f"{item['冲突域']}: 故事潜力 {item['故事潜力']}/10")
        print(f"  钩子数量: {item['钩子数量']}, 复杂度: {item['平均复杂度']:.1f}, 戏剧价值: {item['平均戏剧价值']:.1f}")
    print()

    # 8. 实体统计
    print("8. 冲突实体统计")
    print("-" * 40)
    entity_analysis = tool.get_entity_analysis()
    stats = entity_analysis['统计信息']
    print(f"实体总数: {stats['总体统计']['total_entities']}")
    print(f"关系总数: {stats['总体统计']['total_relations']}")
    print(f"平均关系密度: {stats['总体统计']['avg_relations_per_entity']:.1f} 关系/实体")

    type_dist = stats['类型分布']
    print("实体类型分布:")
    for entity_type, count in type_dist.items():
        print(f"  {entity_type}: {count}个")
    print()

    # 9. 内容搜索演示
    print("9. 内容搜索演示")
    print("-" * 40)
    keywords = ["税收", "器械", "走私"]
    for keyword in keywords:
        results = tool.search_content(keyword)
        total_results = sum(len(items) for items in results.values())
        print(f"关键词 '{keyword}': 找到 {total_results} 个相关结果")

        for category, items in results.items():
            if items:
                print(f"  {category}: {len(items)}个")
    print()

    # 10. 生成详细报告
    print("10. 生成天域↔荒域冲突详细报告")
    print("-" * 40)
    detailed_report = tool.generate_conflict_report("天域", "荒域")
    if "error" not in detailed_report:
        basic_info = detailed_report['冲突基础信息']
        print(f"冲突强度: {basic_info['冲突强度']}")
        print(f"核心资源: {', '.join(basic_info['核心资源'][:2])}...")

        hooks = detailed_report['相关故事钩子']
        print(f"相关故事钩子: {len(hooks)}个")

        entities = detailed_report['涉及实体']
        print(f"涉及实体: {len(entities)}个")

        recommendations = detailed_report['分析建议']
        print("分析建议:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec}")
    print()

    print("=" * 60)
    print("     演示完成！更多功能请使用交互式查询工具")
    print("     运行命令: python conflict_matrix_query_tool.py")
    print("=" * 60)


if __name__ == "__main__":
    demo_conflict_analysis()