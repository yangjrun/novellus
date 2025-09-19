"""
综合跨域冲突网络分析报告生成器
生成详细的分析报告和可操作的洞察
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import datetime
import logging
from dataclasses import asdict

# 导入分析模型
from comprehensive_conflict_network_model import ComprehensiveConflictNetworkModel
from network_visualization_toolkit import NetworkVisualizationToolkit

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveAnalysisReport:
    """综合分析报告生成器"""

    def __init__(self, model: ComprehensiveConflictNetworkModel):
        """
        初始化报告生成器

        Args:
            model: 综合冲突网络模型实例
        """
        self.model = model
        self.viz_toolkit = NetworkVisualizationToolkit(model)
        self.report_data = {}
        self.insights = []
        self.recommendations = []

    def generate_comprehensive_report(self,
                                    output_dir: str,
                                    include_visualizations: bool = True) -> str:
        """
        生成综合分析报告

        Args:
            output_dir: 输出目录
            include_visualizations: 是否包含可视化图表

        Returns:
            str: 报告文件路径
        """
        logger.info("开始生成综合分析报告...")

        # 确保输出目录存在
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 收集分析数据
        self._collect_analysis_data()

        # 生成洞察和建议
        self._generate_insights()
        self._generate_recommendations()

        # 生成可视化（如果需要）
        if include_visualizations:
            self._generate_visualizations(output_path)

        # 生成报告文档
        report_path = self._generate_report_document(output_path)

        # 生成数据摘要
        self._generate_data_summary(output_path)

        # 生成执行摘要
        self._generate_executive_summary(output_path)

        logger.info(f"综合分析报告生成完成: {report_path}")
        return str(report_path)

    def _collect_analysis_data(self):
        """收集分析数据"""
        logger.info("收集分析数据...")

        self.report_data = {
            'generation_time': datetime.datetime.now().isoformat(),
            'model_info': {
                'data_source': self.model.data_path,
                'analysis_config': self.model.config
            }
        }

        # 基础网络信息
        if self.model.main_network:
            self.report_data['network_basic'] = {
                'num_nodes': self.model.main_network.number_of_nodes(),
                'num_edges': self.model.main_network.number_of_edges(),
                'network_type': 'directed' if self.model.main_network.is_directed() else 'undirected'
            }

        # 拓扑指标
        if self.model.topology_metrics:
            self.report_data['topology_metrics'] = asdict(self.model.topology_metrics)

        # 强度模型
        if self.model.intensity_model:
            self.report_data['intensity_model'] = {
                'average_intensity': self.model.intensity_model.intensity_distribution['mean'],
                'intensity_std': self.model.intensity_model.intensity_distribution['std'],
                'intensity_range': (
                    self.model.intensity_model.intensity_distribution['min'],
                    self.model.intensity_model.intensity_distribution['max']
                ),
                'escalation_threshold': self.model.intensity_model.escalation_threshold,
                'prediction_accuracy': self.model.intensity_model.prediction_accuracy
            }

        # 社团结构
        if self.model.community_structure:
            self.report_data['community_structure'] = {
                'num_communities': self.model.community_structure.num_communities,
                'modularity': self.model.community_structure.louvain_modularity,
                'community_sizes': self.model.community_structure.community_sizes,
                'cross_domain_ratio': self.model.community_structure.cross_domain_edges /
                                     (self.model.community_structure.cross_domain_edges +
                                      self.model.community_structure.intra_domain_edges)
                                     if (self.model.community_structure.cross_domain_edges +
                                         self.model.community_structure.intra_domain_edges) > 0 else 0
            }

        # 中心性分析
        if self.model.centrality_analysis:
            self.report_data['centrality_analysis'] = {
                'critical_nodes_count': {k: len(v) for k, v in self.model.centrality_analysis.critical_nodes.items()},
                'top_degree_nodes': self.model.centrality_analysis.centrality_rankings.get('degree', [])[:10],
                'top_betweenness_nodes': self.model.centrality_analysis.centrality_rankings.get('betweenness', [])[:10],
                'top_pagerank_nodes': self.model.centrality_analysis.centrality_rankings.get('pagerank', [])[:10],
                'top_conflict_nodes': self.model.centrality_analysis.centrality_rankings.get('conflict', [])[:10]
            }

        # 传播模型
        if self.model.propagation_model:
            self.report_data['propagation_model'] = {
                'transmission_rate': self.model.propagation_model.transmission_rate,
                'recovery_rate': self.model.propagation_model.recovery_rate,
                'critical_cascade_threshold': self.model.propagation_model.critical_cascade_threshold,
                'average_cascade_size': np.mean(list(self.model.propagation_model.cascade_size_distribution.keys()))
            }

        # 鲁棒性分析
        if self.model.robustness_analysis:
            self.report_data['robustness_analysis'] = {
                'random_attack_threshold': self.model.robustness_analysis.random_attack_threshold,
                'targeted_attack_threshold': self.model.robustness_analysis.targeted_attack_threshold,
                'systemic_risk_score': self.model.robustness_analysis.systemic_risk_score,
                'critical_failure_nodes': self.model.robustness_analysis.critical_failure_nodes[:10],
                'resilience_metrics': self.model.robustness_analysis.resilience_metrics
            }

    def _generate_insights(self):
        """生成分析洞察"""
        logger.info("生成分析洞察...")

        insights = []

        # 网络结构洞察
        if 'topology_metrics' in self.report_data:
            topology = self.report_data['topology_metrics']

            if topology['density'] < 0.1:
                insights.append({
                    'category': '网络结构',
                    'type': '稀疏网络',
                    'description': f"网络密度为{topology['density']:.4f}，表明网络连接相对稀疏",
                    'implication': '实体间直接冲突关系有限，但可能存在间接影响路径',
                    'severity': 'medium'
                })

            if topology['num_components'] > 1:
                insights.append({
                    'category': '网络结构',
                    'type': '网络分离',
                    'description': f"网络存在{topology['num_components']}个独立连通分量",
                    'implication': '不同组件间缺乏直接联系，冲突可能呈现孤立性传播',
                    'severity': 'high'
                })

            if topology.get('small_world_sigma', 0) > 3:
                insights.append({
                    'category': '网络结构',
                    'type': '小世界特性',
                    'description': f"网络具有显著的小世界特性(σ={topology['small_world_sigma']:.2f})",
                    'implication': '信息和冲突可以在网络中快速传播，存在级联风险',
                    'severity': 'high'
                })

            if topology['global_clustering'] > 0.5:
                insights.append({
                    'category': '网络结构',
                    'type': '高聚类性',
                    'description': f"网络聚类系数为{topology['global_clustering']:.3f}，显著高于随机网络",
                    'implication': '实体间形成紧密的局部集群，冲突可能在集群内快速扩散',
                    'severity': 'medium'
                })

        # 冲突强度洞察
        if 'intensity_model' in self.report_data:
            intensity = self.report_data['intensity_model']

            if intensity['average_intensity'] > intensity['escalation_threshold'] * 0.8:
                insights.append({
                    'category': '冲突强度',
                    'type': '高强度冲突',
                    'description': f"平均冲突强度({intensity['average_intensity']:.3f})接近升级阈值",
                    'implication': '网络处于高冲突状态，存在快速升级风险',
                    'severity': 'critical'
                })

            if intensity['prediction_accuracy'] < 0.7:
                insights.append({
                    'category': '冲突强度',
                    'type': '预测不确定性',
                    'description': f"强度预测模型准确度为{intensity['prediction_accuracy']:.3f}",
                    'implication': '冲突强度存在较大不确定性，需要更多数据改进模型',
                    'severity': 'medium'
                })

        # 社团结构洞察
        if 'community_structure' in self.report_data:
            community = self.report_data['community_structure']

            if community['cross_domain_ratio'] > 0.4:
                insights.append({
                    'category': '社团结构',
                    'type': '跨域冲突频繁',
                    'description': f"跨域冲突连接占比{community['cross_domain_ratio']:.3f}",
                    'implication': '域间冲突激烈，可能导致全局性冲突升级',
                    'severity': 'high'
                })

            if community['modularity'] < 0.3:
                insights.append({
                    'category': '社团结构',
                    'type': '社团结构不明显',
                    'description': f"网络模块度为{community['modularity']:.3f}，社团划分不清晰",
                    'implication': '实体间关系复杂，难以形成稳定的联盟或阵营',
                    'severity': 'medium'
                })

        # 关键节点洞察
        if 'centrality_analysis' in self.report_data:
            centrality = self.report_data['centrality_analysis']

            high_centrality_count = centrality['critical_nodes_count'].get('high_centrality', 0)
            if high_centrality_count < self.report_data['network_basic']['num_nodes'] * 0.05:
                insights.append({
                    'category': '关键节点',
                    'type': '少数关键节点',
                    'description': f"仅有{high_centrality_count}个高中心性节点",
                    'implication': '网络控制权高度集中，关键节点失效将严重影响网络功能',
                    'severity': 'high'
                })

        # 鲁棒性洞察
        if 'robustness_analysis' in self.report_data:
            robustness = self.report_data['robustness_analysis']

            if robustness['targeted_attack_threshold'] < 0.2:
                insights.append({
                    'category': '网络鲁棒性',
                    'type': '脆弱的目标攻击抵抗',
                    'description': f"目标攻击阈值仅为{robustness['targeted_attack_threshold']:.3f}",
                    'implication': '网络对针对性攻击极其脆弱，少数关键节点失效即可瘫痪网络',
                    'severity': 'critical'
                })

            if robustness['systemic_risk_score'] > 0.7:
                insights.append({
                    'category': '网络鲁棒性',
                    'type': '高系统性风险',
                    'description': f"系统性风险评分为{robustness['systemic_risk_score']:.3f}",
                    'implication': '网络面临高系统性风险，需要紧急采取风险缓解措施',
                    'severity': 'critical'
                })

        # 传播动力学洞察
        if 'propagation_model' in self.report_data:
            propagation = self.report_data['propagation_model']

            if propagation['transmission_rate'] > 0.6:
                insights.append({
                    'category': '冲突传播',
                    'type': '高传播率',
                    'description': f"冲突传播率为{propagation['transmission_rate']:.3f}",
                    'implication': '冲突具有强传播性，局部冲突可能快速扩散至全网',
                    'severity': 'high'
                })

            if propagation['critical_cascade_threshold'] < 0.3:
                insights.append({
                    'category': '冲突传播',
                    'type': '易发生级联',
                    'description': f"临界级联阈值为{propagation['critical_cascade_threshold']:.3f}",
                    'implication': '网络容易发生大规模级联效应，小扰动可能导致系统性崩溃',
                    'severity': 'critical'
                })

        self.insights = insights

    def _generate_recommendations(self):
        """生成行动建议"""
        logger.info("生成行动建议...")

        recommendations = []

        # 基于洞察生成建议
        for insight in self.insights:
            if insight['type'] == '网络分离':
                recommendations.append({
                    'category': '网络结构优化',
                    'priority': 'high',
                    'action': '建立跨组件桥梁节点',
                    'description': '在独立连通分量间建立连接，增强网络整体连通性',
                    'expected_impact': '提高信息流通，减少孤立性冲突风险',
                    'implementation': [
                        '识别各连通分量的关键节点',
                        '设计跨组件协调机制',
                        '建立信息共享平台'
                    ]
                })

            elif insight['type'] == '少数关键节点':
                recommendations.append({
                    'category': '关键节点保护',
                    'priority': 'critical',
                    'action': '实施关键节点保护策略',
                    'description': '对高中心性节点进行重点保护和备份',
                    'expected_impact': '提高网络抗攻击能力，降低单点故障风险',
                    'implementation': [
                        '建立关键节点监控体系',
                        '设计冗余机制和备份方案',
                        '制定应急响应预案'
                    ]
                })

            elif insight['type'] == '高强度冲突':
                recommendations.append({
                    'category': '冲突管理',
                    'priority': 'urgent',
                    'action': '实施冲突降级措施',
                    'description': '采取积极措施降低整体冲突强度',
                    'expected_impact': '防止冲突升级，维护网络稳定',
                    'implementation': [
                        '识别高强度冲突源头',
                        '实施调解和协商机制',
                        '建立冲突预警系统'
                    ]
                })

            elif insight['type'] == '跨域冲突频繁':
                recommendations.append({
                    'category': '跨域协调',
                    'priority': 'high',
                    'action': '加强跨域治理机制',
                    'description': '建立有效的跨域冲突解决机制',
                    'expected_impact': '减少域间冲突，促进跨域合作',
                    'implementation': [
                        '设立跨域协调委员会',
                        '制定跨域冲突处理规程',
                        '建立利益平衡机制'
                    ]
                })

            elif insight['type'] == '高传播率':
                recommendations.append({
                    'category': '传播控制',
                    'priority': 'high',
                    'action': '建立传播阻断机制',
                    'description': '在关键位置设置传播阻断点',
                    'expected_impact': '控制冲突传播范围，防止系统性扩散',
                    'implementation': [
                        '识别传播关键路径',
                        '设置传播阻断节点',
                        '建立快速响应机制'
                    ]
                })

        # 通用建议
        general_recommendations = [
            {
                'category': '监控预警',
                'priority': 'high',
                'action': '建立综合监控体系',
                'description': '构建全方位的网络状态监控和预警系统',
                'expected_impact': '及时发现风险，提前预警潜在问题',
                'implementation': [
                    '部署实时监控系统',
                    '建立预警指标体系',
                    '设置自动报警机制'
                ]
            },
            {
                'category': '数据优化',
                'priority': 'medium',
                'action': '完善数据收集体系',
                'description': '增强数据质量和覆盖范围，提高分析精度',
                'expected_impact': '提高分析准确性，支持更好的决策',
                'implementation': [
                    '扩大数据收集范围',
                    '提高数据质量标准',
                    '建立数据验证机制'
                ]
            },
            {
                'category': '能力建设',
                'priority': 'medium',
                'action': '提升网络分析能力',
                'description': '培养专业分析团队，提升分析工具和方法',
                'expected_impact': '增强分析深度，提供更精准的洞察',
                'implementation': [
                    '组建专业分析团队',
                    '采用先进分析工具',
                    '定期开展能力培训'
                ]
            }
        ]

        recommendations.extend(general_recommendations)
        self.recommendations = sorted(recommendations,
                                    key=lambda x: {'urgent': 0, 'critical': 1, 'high': 2, 'medium': 3}[x['priority']])

    def _generate_visualizations(self, output_path: Path):
        """生成可视化图表"""
        logger.info("生成可视化图表...")

        viz_dir = output_path / 'visualizations'
        viz_dir.mkdir(exist_ok=True)

        try:
            # 网络概览图
            self.viz_toolkit.plot_network_overview(
                save_path=str(viz_dir / 'network_overview.png'),
                color_scheme='domains'
            )

            # 中心性热力图
            self.viz_toolkit.plot_centrality_heatmap(
                save_path=str(viz_dir / 'centrality_heatmap.png')
            )

            # 社团结构图
            self.viz_toolkit.plot_community_structure(
                save_path=str(viz_dir / 'community_structure.png')
            )

            # 综合仪表板
            self.viz_toolkit.plot_network_metrics_dashboard(
                save_path=str(viz_dir / 'metrics_dashboard.png')
            )

            # 域子网络图
            self.viz_toolkit.plot_domain_networks(
                save_dir=str(viz_dir / 'domain_networks')
            )

        except Exception as e:
            logger.warning(f"部分可视化生成失败: {e}")

    def _generate_report_document(self, output_path: Path) -> Path:
        """生成报告文档"""
        logger.info("生成报告文档...")

        report_path = output_path / 'comprehensive_analysis_report.md'

        with open(report_path, 'w', encoding='utf-8') as f:
            # 报告标题
            f.write("# 裂世九域·法则链纪元 跨域冲突网络分析报告\n\n")
            f.write(f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 执行摘要
            f.write("## 执行摘要\n\n")
            self._write_executive_summary(f)

            # 网络概况
            f.write("\n## 网络概况\n\n")
            self._write_network_overview(f)

            # 详细分析结果
            f.write("\n## 详细分析结果\n\n")
            self._write_detailed_analysis(f)

            # 关键洞察
            f.write("\n## 关键洞察\n\n")
            self._write_insights(f)

            # 行动建议
            f.write("\n## 行动建议\n\n")
            self._write_recommendations(f)

            # 技术附录
            f.write("\n## 技术附录\n\n")
            self._write_technical_appendix(f)

        return report_path

    def _write_executive_summary(self, f):
        """写入执行摘要"""
        network_basic = self.report_data.get('network_basic', {})
        robustness = self.report_data.get('robustness_analysis', {})

        f.write(f"本报告对包含{network_basic.get('num_nodes', 'N/A')}个冲突实体和{network_basic.get('num_edges', 'N/A')}个冲突关系的")
        f.write("跨域冲突网络进行了全面分析。\n\n")

        # 风险等级评估
        risk_score = robustness.get('systemic_risk_score', 0)
        if risk_score > 0.7:
            risk_level = "**高风险**"
            risk_desc = "网络面临严重的系统性风险"
        elif risk_score > 0.4:
            risk_level = "**中等风险**"
            risk_desc = "网络存在一定的稳定性问题"
        else:
            risk_level = "**低风险**"
            risk_desc = "网络整体较为稳定"

        f.write(f"**风险等级**: {risk_level}\n\n")
        f.write(f"{risk_desc}，系统性风险评分为{risk_score:.3f}。\n\n")

        # 主要发现
        f.write("### 主要发现\n\n")
        critical_insights = [insight for insight in self.insights if insight['severity'] == 'critical']
        high_insights = [insight for insight in self.insights if insight['severity'] == 'high']

        if critical_insights:
            f.write("**关键风险**:\n")
            for insight in critical_insights[:3]:
                f.write(f"- {insight['description']}\n")
            f.write("\n")

        if high_insights:
            f.write("**重要发现**:\n")
            for insight in high_insights[:3]:
                f.write(f"- {insight['description']}\n")
            f.write("\n")

        # 紧急建议
        urgent_recommendations = [rec for rec in self.recommendations if rec['priority'] in ['urgent', 'critical']]
        if urgent_recommendations:
            f.write("### 紧急建议\n\n")
            for rec in urgent_recommendations[:3]:
                f.write(f"- **{rec['action']}**: {rec['description']}\n")
            f.write("\n")

    def _write_network_overview(self, f):
        """写入网络概况"""
        network_basic = self.report_data.get('network_basic', {})
        topology = self.report_data.get('topology_metrics', {})

        f.write("### 基础统计\n\n")
        f.write(f"- **节点数量**: {network_basic.get('num_nodes', 'N/A')}\n")
        f.write(f"- **边数量**: {network_basic.get('num_edges', 'N/A')}\n")
        f.write(f"- **网络密度**: {topology.get('density', 'N/A'):.4f}\n")
        f.write(f"- **平均度**: {topology.get('avg_degree', 'N/A'):.2f}\n")
        f.write(f"- **连通分量数**: {topology.get('num_components', 'N/A')}\n\n")

        f.write("### 网络特征\n\n")
        f.write(f"- **平均路径长度**: {topology.get('avg_path_length', 'N/A'):.4f}\n")
        f.write(f"- **聚类系数**: {topology.get('global_clustering', 'N/A'):.4f}\n")
        f.write(f"- **网络直径**: {topology.get('diameter', 'N/A')}\n")

        if topology.get('small_world_sigma'):
            f.write(f"- **小世界指数**: {topology['small_world_sigma']:.3f}\n")

        if topology.get('power_law_exponent'):
            f.write(f"- **幂律指数**: {topology['power_law_exponent']:.3f}\n")

        f.write("\n")

    def _write_detailed_analysis(self, f):
        """写入详细分析结果"""

        # 冲突强度分析
        if 'intensity_model' in self.report_data:
            f.write("### 冲突强度分析\n\n")
            intensity = self.report_data['intensity_model']
            f.write(f"- **平均冲突强度**: {intensity['average_intensity']:.3f}\n")
            f.write(f"- **强度标准差**: {intensity['intensity_std']:.3f}\n")
            f.write(f"- **强度范围**: {intensity['intensity_range'][0]:.3f} - {intensity['intensity_range'][1]:.3f}\n")
            f.write(f"- **升级阈值**: {intensity['escalation_threshold']:.3f}\n")
            f.write(f"- **预测准确度**: {intensity['prediction_accuracy']:.3f}\n\n")

        # 社团结构分析
        if 'community_structure' in self.report_data:
            f.write("### 社团结构分析\n\n")
            community = self.report_data['community_structure']
            f.write(f"- **社团数量**: {community['num_communities']}\n")
            f.write(f"- **模块度**: {community['modularity']:.3f}\n")
            f.write(f"- **跨域连接比例**: {community['cross_domain_ratio']:.3f}\n")
            f.write(f"- **社团大小**: {community['community_sizes']}\n\n")

        # 中心性分析
        if 'centrality_analysis' in self.report_data:
            f.write("### 关键节点分析\n\n")
            centrality = self.report_data['centrality_analysis']

            # Top PageRank 节点
            f.write("**Top 5 PageRank 节点**:\n")
            for i, (node, score) in enumerate(centrality['top_pagerank_nodes'][:5], 1):
                node_name = self.model.main_network.nodes[node].get('name', node) if self.model.main_network else node
                f.write(f"{i}. {node_name} (分数: {score:.4f})\n")
            f.write("\n")

            # Top 冲突节点
            if centrality['top_conflict_nodes']:
                f.write("**Top 5 冲突节点**:\n")
                for i, (node, score) in enumerate(centrality['top_conflict_nodes'][:5], 1):
                    node_name = self.model.main_network.nodes[node].get('name', node) if self.model.main_network else node
                    f.write(f"{i}. {node_name} (冲突强度: {score:.4f})\n")
                f.write("\n")

        # 传播动力学
        if 'propagation_model' in self.report_data:
            f.write("### 冲突传播分析\n\n")
            propagation = self.report_data['propagation_model']
            f.write(f"- **传播率**: {propagation['transmission_rate']:.3f}\n")
            f.write(f"- **恢复率**: {propagation['recovery_rate']:.3f}\n")
            f.write(f"- **临界级联阈值**: {propagation['critical_cascade_threshold']:.3f}\n")
            f.write(f"- **平均级联大小**: {propagation['average_cascade_size']:.1f}\n\n")

        # 鲁棒性分析
        if 'robustness_analysis' in self.report_data:
            f.write("### 网络鲁棒性分析\n\n")
            robustness = self.report_data['robustness_analysis']
            f.write(f"- **随机攻击阈值**: {robustness['random_attack_threshold']:.3f}\n")
            f.write(f"- **目标攻击阈值**: {robustness['targeted_attack_threshold']:.3f}\n")
            f.write(f"- **系统性风险评分**: {robustness['systemic_risk_score']:.3f}\n")

            if robustness['critical_failure_nodes']:
                f.write("\n**关键失效节点**:\n")
                for i, node in enumerate(robustness['critical_failure_nodes'][:5], 1):
                    node_name = self.model.main_network.nodes[node].get('name', node) if self.model.main_network else node
                    f.write(f"{i}. {node_name}\n")
            f.write("\n")

    def _write_insights(self, f):
        """写入关键洞察"""
        # 按严重程度分组
        insights_by_severity = {}
        for insight in self.insights:
            severity = insight['severity']
            if severity not in insights_by_severity:
                insights_by_severity[severity] = []
            insights_by_severity[severity].append(insight)

        severity_order = ['critical', 'high', 'medium', 'low']
        severity_titles = {
            'critical': '🔴 关键风险',
            'high': '🟠 重要发现',
            'medium': '🟡 中等关注',
            'low': '🟢 一般观察'
        }

        for severity in severity_order:
            if severity in insights_by_severity:
                f.write(f"### {severity_titles[severity]}\n\n")
                for insight in insights_by_severity[severity]:
                    f.write(f"**{insight['type']}**\n")
                    f.write(f"- *描述*: {insight['description']}\n")
                    f.write(f"- *影响*: {insight['implication']}\n\n")

    def _write_recommendations(self, f):
        """写入行动建议"""
        # 按优先级分组
        rec_by_priority = {}
        for rec in self.recommendations:
            priority = rec['priority']
            if priority not in rec_by_priority:
                rec_by_priority[priority] = []
            rec_by_priority[priority].append(rec)

        priority_order = ['urgent', 'critical', 'high', 'medium']
        priority_titles = {
            'urgent': '🚨 紧急行动',
            'critical': '🔴 关键措施',
            'high': '🟠 重要建议',
            'medium': '🟡 中期规划'
        }

        for priority in priority_order:
            if priority in rec_by_priority:
                f.write(f"### {priority_titles[priority]}\n\n")
                for i, rec in enumerate(rec_by_priority[priority], 1):
                    f.write(f"#### {i}. {rec['action']}\n\n")
                    f.write(f"**类别**: {rec['category']}\n\n")
                    f.write(f"**描述**: {rec['description']}\n\n")
                    f.write(f"**预期影响**: {rec['expected_impact']}\n\n")
                    f.write("**实施步骤**:\n")
                    for step in rec['implementation']:
                        f.write(f"- {step}\n")
                    f.write("\n")

    def _write_technical_appendix(self, f):
        """写入技术附录"""
        f.write("### 分析方法\n\n")
        f.write("本报告采用复杂网络分析方法，主要包括:\n\n")
        f.write("- **网络拓扑分析**: 计算基础网络指标，评估网络结构特征\n")
        f.write("- **中心性分析**: 识别网络中的关键节点和重要角色\n")
        f.write("- **社团发现**: 使用Louvain算法识别网络社团结构\n")
        f.write("- **冲突强度建模**: 构建多维冲突强度量化模型\n")
        f.write("- **传播动力学**: 基于SIR模型分析冲突传播机制\n")
        f.write("- **鲁棒性分析**: 评估网络对攻击和故障的抵抗能力\n\n")

        f.write("### 数据来源\n\n")
        f.write(f"- **数据文件**: {self.model.data_path}\n")
        f.write(f"- **实体数量**: {self.report_data['network_basic'].get('num_nodes', 'N/A')}\n")
        f.write(f"- **关系数量**: {self.report_data['network_basic'].get('num_edges', 'N/A')}\n")
        f.write(f"- **分析时间**: {self.report_data['generation_time']}\n\n")

        f.write("### 限制说明\n\n")
        f.write("- 分析结果基于当前可获得的数据，可能存在不完整性\n")
        f.write("- 预测模型的准确性依赖于历史数据的代表性\n")
        f.write("- 建议的实施效果需要根据实际情况进行调整\n")
        f.write("- 网络结构可能随时间变化，需要定期更新分析\n\n")

    def _generate_data_summary(self, output_path: Path):
        """生成数据摘要"""
        summary_path = output_path / 'data_summary.json'

        summary_data = {
            'analysis_metadata': {
                'generation_time': self.report_data['generation_time'],
                'model_version': '1.0',
                'data_source': self.model.data_path
            },
            'network_statistics': self.report_data.get('network_basic', {}),
            'key_metrics': {
                'density': self.report_data.get('topology_metrics', {}).get('density'),
                'clustering': self.report_data.get('topology_metrics', {}).get('global_clustering'),
                'modularity': self.report_data.get('community_structure', {}).get('modularity'),
                'risk_score': self.report_data.get('robustness_analysis', {}).get('systemic_risk_score')
            },
            'insights_summary': {
                'total_insights': len(self.insights),
                'critical_insights': len([i for i in self.insights if i['severity'] == 'critical']),
                'high_insights': len([i for i in self.insights if i['severity'] == 'high'])
            },
            'recommendations_summary': {
                'total_recommendations': len(self.recommendations),
                'urgent_actions': len([r for r in self.recommendations if r['priority'] == 'urgent']),
                'critical_actions': len([r for r in self.recommendations if r['priority'] == 'critical'])
            }
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

    def _generate_executive_summary(self, output_path: Path):
        """生成执行摘要"""
        summary_path = output_path / 'executive_summary.txt'

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("裂世九域·法则链纪元 跨域冲突网络分析 - 执行摘要\n")
            f.write("=" * 60 + "\n\n")

            # 关键指标
            network_basic = self.report_data.get('network_basic', {})
            robustness = self.report_data.get('robustness_analysis', {})

            f.write("关键指标:\n")
            f.write(f"• 网络规模: {network_basic.get('num_nodes', 'N/A')} 节点, {network_basic.get('num_edges', 'N/A')} 边\n")
            f.write(f"• 系统风险: {robustness.get('systemic_risk_score', 'N/A'):.3f}\n")
            f.write(f"• 攻击抵抗: {robustness.get('targeted_attack_threshold', 'N/A'):.3f}\n\n")

            # 风险等级
            risk_score = robustness.get('systemic_risk_score', 0)
            if risk_score > 0.7:
                f.write("风险等级: 高风险 ⚠️\n")
            elif risk_score > 0.4:
                f.write("风险等级: 中等风险 ⚠️\n")
            else:
                f.write("风险等级: 低风险 ✅\n")

            # 紧急建议
            urgent_recs = [r for r in self.recommendations if r['priority'] in ['urgent', 'critical']]
            if urgent_recs:
                f.write(f"\n紧急行动 ({len(urgent_recs)} 项):\n")
                for i, rec in enumerate(urgent_recs[:3], 1):
                    f.write(f"{i}. {rec['action']}\n")

            f.write(f"\n生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    # 测试报告生成
    try:
        # 初始化模型并运行分析
        model = ComprehensiveConflictNetworkModel()
        data_path = "D:/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
        model.load_data(data_path)

        # 运行完整分析
        results = model.run_comprehensive_analysis()

        # 生成报告
        report_generator = ComprehensiveAnalysisReport(model)
        report_path = report_generator.generate_comprehensive_report(
            output_dir="D:/work/novellus/analysis_report",
            include_visualizations=True
        )

        print("=== 分析报告生成完成 ===")
        print(f"报告路径: {report_path}")
        print(f"发现 {len(report_generator.insights)} 个洞察")
        print(f"提供 {len(report_generator.recommendations)} 项建议")

    except Exception as e:
        logger.error(f"报告生成测试失败: {e}")
        print(f"报告生成过程中出现错误: {e}")
        import traceback
        traceback.print_exc()