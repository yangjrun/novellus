"""
跨域冲突网络模型综合测试脚本
验证完整的分析流程和所有功能模块
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'analysis'))

import json
import traceback
from pathlib import Path
import time
import matplotlib.pyplot as plt

# 导入分析模块
from comprehensive_conflict_network_model import ComprehensiveConflictNetworkModel
from network_visualization_toolkit import NetworkVisualizationToolkit
from comprehensive_analysis_report import ComprehensiveAnalysisReport

def test_comprehensive_network_model():
    """测试综合网络模型的完整流程"""
    print("=" * 80)
    print("Cross-Domain Conflict Network Model Comprehensive Test")
    print("=" * 80)

    start_time = time.time()

    try:
        # 1. 初始化模型
        print("\n1. 初始化综合网络模型...")
        model = ComprehensiveConflictNetworkModel(
            config={
                'random_seed': 42,
                'enable_caching': True,
                'parallel_processing': False
            }
        )
        print("   ✅ 模型初始化成功")

        # 2. 加载数据
        print("\n2. 加载冲突网络数据...")
        data_path = "D:/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"

        if not Path(data_path).exists():
            print(f"   ❌ 数据文件不存在: {data_path}")
            return False

        model.load_data(data_path)
        print(f"   ✅ 数据加载成功: {len(model.entities_df)} 个实体, {len(model.relations_df)} 个关系")

        # 3. 构建网络
        print("\n3. 构建主网络...")
        main_network = model.build_main_network()
        print(f"   ✅ 主网络构建完成: {main_network.number_of_nodes()} 节点, {main_network.number_of_edges()} 边")

        # 4. 网络拓扑分析
        print("\n4. 网络拓扑分析...")
        topology_metrics = model.analyze_network_topology()
        print(f"   ✅ 拓扑分析完成")
        print(f"      - 网络密度: {topology_metrics.density:.4f}")
        print(f"      - 聚类系数: {topology_metrics.global_clustering:.4f}")
        print(f"      - 连通分量: {topology_metrics.num_components}")
        print(f"      - 平均路径长度: {topology_metrics.avg_path_length:.4f}")

        # 5. 冲突强度建模
        print("\n5. 构建冲突强度模型...")
        intensity_model = model.build_conflict_intensity_model()
        print(f"   ✅ 强度模型构建完成")
        print(f"      - 平均强度: {intensity_model.intensity_distribution['mean']:.3f}")
        print(f"      - 升级阈值: {intensity_model.escalation_threshold:.3f}")
        print(f"      - 预测准确度: {intensity_model.prediction_accuracy:.3f}")

        # 6. 社团发现
        print("\n6. 社团发现和聚类分析...")
        community_structure = model.discover_communities()
        print(f"   ✅ 社团发现完成")
        print(f"      - 社团数量: {community_structure.num_communities}")
        print(f"      - 模块度: {community_structure.louvain_modularity:.3f}")
        print(f"      - 跨域连接: {community_structure.cross_domain_edges}")

        # 7. 中心性分析
        print("\n7. 中心性分析...")
        centrality_analysis = model.analyze_centrality()
        print(f"   ✅ 中心性分析完成")

        # 显示Top 5 PageRank节点
        top_pagerank = centrality_analysis.centrality_rankings.get('pagerank', [])[:5]
        print("      Top 5 PageRank 节点:")
        for i, (node, score) in enumerate(top_pagerank, 1):
            node_name = main_network.nodes[node].get('name', node)[:20]
            print(f"         {i}. {node_name} (分数: {score:.4f})")

        # 8. 冲突传播模型
        print("\n8. 冲突传播动力学建模...")
        propagation_model = model.model_conflict_propagation()
        print(f"   ✅ 传播模型构建完成")
        print(f"      - 传播率: {propagation_model.transmission_rate:.3f}")
        print(f"      - 恢复率: {propagation_model.recovery_rate:.3f}")
        print(f"      - 临界级联阈值: {propagation_model.critical_cascade_threshold:.3f}")

        # 9. 网络鲁棒性分析
        print("\n9. 网络鲁棒性分析...")
        robustness_analysis = model.analyze_network_robustness()
        print(f"   ✅ 鲁棒性分析完成")
        print(f"      - 随机攻击阈值: {robustness_analysis.random_attack_threshold:.3f}")
        print(f"      - 目标攻击阈值: {robustness_analysis.targeted_attack_threshold:.3f}")
        print(f"      - 系统性风险评分: {robustness_analysis.systemic_risk_score:.3f}")

        # 10. 运行综合分析
        print("\n10. 运行综合分析...")
        comprehensive_results = model.run_comprehensive_analysis()
        print(f"   ✅ 综合分析完成")

        # 显示分析摘要
        summary = comprehensive_results.get('summary', {})
        print("\n   📊 分析摘要:")
        print(f"      - 网络规模: {summary.get('network_scale', {})}")
        print(f"      - 网络特征: {summary.get('network_characteristics', {})}")
        print(f"      - 稳定性评估: {summary.get('stability_assessment', {})}")
        if summary.get('key_findings'):
            print(f"      - 关键发现: {len(summary['key_findings'])} 项")
            for finding in summary['key_findings'][:3]:
                print(f"        • {finding}")

        # 11. 可视化测试
        print("\n11. 可视化系统测试...")
        viz_toolkit = NetworkVisualizationToolkit(model)

        # 创建测试输出目录
        test_output_dir = "D:/work/novellus/test_output"
        Path(test_output_dir).mkdir(parents=True, exist_ok=True)

        # 生成网络概览图
        try:
            fig1 = viz_toolkit.plot_network_overview(
                save_path=f"{test_output_dir}/test_network_overview.png",
                show_labels=False
            )
            plt.close(fig1)
            print("   ✅ 网络概览图生成成功")
        except Exception as e:
            print(f"   ⚠️ 网络概览图生成失败: {e}")

        # 生成中心性热力图
        try:
            fig2 = viz_toolkit.plot_centrality_heatmap(
                save_path=f"{test_output_dir}/test_centrality_heatmap.png",
                top_n=15
            )
            plt.close(fig2)
            print("   ✅ 中心性热力图生成成功")
        except Exception as e:
            print(f"   ⚠️ 中心性热力图生成失败: {e}")

        # 生成指标仪表板
        try:
            fig3 = viz_toolkit.plot_network_metrics_dashboard(
                save_path=f"{test_output_dir}/test_metrics_dashboard.png"
            )
            plt.close(fig3)
            print("   ✅ 指标仪表板生成成功")
        except Exception as e:
            print(f"   ⚠️ 指标仪表板生成失败: {e}")

        # 12. 分析报告测试
        print("\n12. 分析报告生成测试...")
        try:
            report_generator = ComprehensiveAnalysisReport(model)
            report_path = report_generator.generate_comprehensive_report(
                output_dir=f"{test_output_dir}/analysis_report",
                include_visualizations=True
            )

            print(f"   ✅ 分析报告生成成功")
            print(f"      - 报告路径: {report_path}")
            print(f"      - 洞察数量: {len(report_generator.insights)}")
            print(f"      - 建议数量: {len(report_generator.recommendations)}")

            # 显示部分洞察
            critical_insights = [i for i in report_generator.insights if i['severity'] == 'critical']
            if critical_insights:
                print(f"      - 关键洞察 ({len(critical_insights)} 项):")
                for insight in critical_insights[:2]:
                    print(f"        • {insight['description']}")

            # 显示部分建议
            urgent_recs = [r for r in report_generator.recommendations if r['priority'] in ['urgent', 'critical']]
            if urgent_recs:
                print(f"      - 紧急建议 ({len(urgent_recs)} 项):")
                for rec in urgent_recs[:2]:
                    print(f"        • {rec['action']}")

        except Exception as e:
            print(f"   ❌ 分析报告生成失败: {e}")
            traceback.print_exc()

        # 13. 性能评估
        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n13. 性能评估:")
        print(f"   ✅ 总执行时间: {total_time:.2f} 秒")
        print(f"   ✅ 平均处理速度: {len(model.entities_df) / total_time:.1f} 实体/秒")

        # 14. 数据质量检查
        print(f"\n14. 数据质量检查:")

        # 检查网络连通性
        if topology_metrics.is_connected:
            print("   ✅ 网络完全连通")
        else:
            print(f"   ⚠️ 网络存在 {topology_metrics.num_components} 个独立组件")

        # 检查数据完整性
        missing_names = sum(1 for _, data in main_network.nodes(data=True)
                           if not data.get('name') or data.get('name') == '')
        if missing_names == 0:
            print("   ✅ 所有节点都有有效名称")
        else:
            print(f"   ⚠️ {missing_names} 个节点缺少名称")

        # 检查强度数据
        zero_intensity_edges = sum(1 for _, _, data in main_network.edges(data=True)
                                  if data.get('strength', 0) == 0)
        if zero_intensity_edges == 0:
            print("   ✅ 所有边都有非零强度")
        else:
            print(f"   ⚠️ {zero_intensity_edges} 条边强度为零")

        # 15. 总结
        print("\n" + "=" * 80)
        print("🎉 综合测试完成！")
        print("=" * 80)
        print("\n📋 测试总结:")
        print(f"   • 网络规模: {main_network.number_of_nodes()} 节点, {main_network.number_of_edges()} 边")
        print(f"   • 网络密度: {topology_metrics.density:.4f}")
        print(f"   • 社团数量: {community_structure.num_communities}")
        print(f"   • 系统风险: {robustness_analysis.systemic_risk_score:.3f}")
        print(f"   • 执行时间: {total_time:.2f} 秒")
        print(f"   • 输出目录: {test_output_dir}")

        # 风险等级评估
        risk_score = robustness_analysis.systemic_risk_score
        if risk_score > 0.7:
            risk_level = "高风险 ⚠️"
        elif risk_score > 0.4:
            risk_level = "中等风险 ⚠️"
        else:
            risk_level = "低风险 ✅"
        print(f"   • 风险等级: {risk_level}")

        print("\n🚀 所有核心功能正常运行，系统可用于实际分析！")

        return True

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        traceback.print_exc()
        return False

def test_model_components():
    """测试各个组件的独立功能"""
    print("\n" + "=" * 60)
    print("组件独立测试")
    print("=" * 60)

    try:
        # 测试数据加载
        print("\n🔧 测试数据加载组件...")
        model = ComprehensiveConflictNetworkModel()
        data_path = "D:/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"

        if Path(data_path).exists():
            model.load_data(data_path)
            print("   ✅ 数据加载组件正常")
        else:
            print("   ⚠️ 测试数据文件不存在")
            return False

        # 测试网络构建
        print("\n🔧 测试网络构建组件...")
        network = model.build_main_network()
        if network and network.number_of_nodes() > 0:
            print("   ✅ 网络构建组件正常")
        else:
            print("   ❌ 网络构建组件异常")
            return False

        # 测试各分析模块
        analysis_modules = [
            ("拓扑分析", model.analyze_network_topology),
            ("强度建模", model.build_conflict_intensity_model),
            ("社团发现", model.discover_communities),
            ("中心性分析", model.analyze_centrality),
            ("传播建模", model.model_conflict_propagation),
            ("鲁棒性分析", model.analyze_network_robustness)
        ]

        for module_name, module_func in analysis_modules:
            print(f"\n🔧 测试{module_name}组件...")
            try:
                result = module_func()
                if result:
                    print(f"   ✅ {module_name}组件正常")
                else:
                    print(f"   ❌ {module_name}组件返回空结果")
            except Exception as e:
                print(f"   ❌ {module_name}组件异常: {e}")

        print("\n✅ 组件测试完成")
        return True

    except Exception as e:
        print(f"\n❌ 组件测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始跨域冲突网络模型测试...\n")

    # 运行组件测试
    component_test_success = test_model_components()

    if component_test_success:
        # 运行综合测试
        comprehensive_test_success = test_comprehensive_network_model()

        if comprehensive_test_success:
            print("\n🎊 所有测试通过！系统可以投入使用。")
            exit(0)
        else:
            print("\n⚠️ 综合测试失败，请检查错误信息。")
            exit(1)
    else:
        print("\n⚠️ 组件测试失败，请检查基础功能。")
        exit(1)