"""
综合分析报告生成器和API接口
整合所有分析结果，生成完整的跨域冲突网络分析报告
"""

import json
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
from datetime import datetime, timedelta
import base64
from io import BytesIO

# Web框架
try:
    from flask import Flask, jsonify, request, send_file
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# 报告生成
try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

# PDF生成
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

# 可视化
import matplotlib.pyplot as plt
import seaborn as sns

# 从分析器导入
from conflict_prediction_system import ConflictPredictionSystem, RiskIndicator, ConflictAlert
from network_visualizer import NetworkVisualizer
from dynamic_conflict_analyzer import DynamicConflictAnalyzer

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisReport:
    """分析报告数据结构"""
    report_id: str
    title: str
    generated_time: datetime
    summary: Dict[str, Any]
    network_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    predictions: Dict[str, Any]
    recommendations: List[str]
    visualizations: Dict[str, str]  # 可视化文件路径
    raw_data: Dict[str, Any]

class ComprehensiveReportGenerator:
    """综合报告生成器"""

    def __init__(self, prediction_system: ConflictPredictionSystem):
        """初始化报告生成器"""
        self.prediction_system = prediction_system
        self.analyzer = prediction_system.analyzer
        self.visualizer = NetworkVisualizer(self.analyzer)

        # 输出目录
        self.output_dir = Path("/d/work/novellus/output")
        self.output_dir.mkdir(exist_ok=True)

        # 报告模板
        self.report_template = self._create_report_template()

    def generate_comprehensive_report(self, report_title: str = "跨域冲突网络分析报告") -> AnalysisReport:
        """生成综合分析报告"""
        logger.info("生成综合分析报告...")

        report_id = f"conflict_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 1. 执行完整分析流程
        self._run_complete_analysis()

        # 2. 收集分析结果
        summary = self._generate_summary()
        network_analysis = self._generate_network_analysis()
        risk_assessment = self._generate_risk_assessment()
        predictions = self._generate_predictions()
        recommendations = self._generate_recommendations()

        # 3. 生成可视化
        visualizations = self._generate_visualizations(report_id)

        # 4. 收集原始数据
        raw_data = self._collect_raw_data()

        # 5. 创建报告对象
        report = AnalysisReport(
            report_id=report_id,
            title=report_title,
            generated_time=datetime.now(),
            summary=summary,
            network_analysis=network_analysis,
            risk_assessment=risk_assessment,
            predictions=predictions,
            recommendations=recommendations,
            visualizations=visualizations,
            raw_data=raw_data
        )

        # 6. 保存报告
        self._save_report(report)

        logger.info(f"报告生成完成: {report_id}")
        return report

    def _run_complete_analysis(self):
        """运行完整分析流程"""
        logger.info("执行完整分析流程...")

        # 基础网络分析
        if not self.analyzer.network_metrics:
            self.analyzer.calculate_network_metrics()

        if not self.analyzer.centrality_metrics:
            self.analyzer.calculate_centrality_metrics()

        # 高级分析
        if not self.analyzer.community_structure:
            self.analyzer.detect_communities_advanced()

        if not hasattr(self.analyzer, 'critical_paths') or not self.analyzer.critical_paths:
            self.analyzer.identify_critical_paths_advanced()

        if not self.analyzer.network_robustness:
            self.analyzer.analyze_network_robustness_advanced()

        # 动态分析
        if not self.analyzer.conflict_dynamics:
            self.analyzer.build_conflict_state_model()

        if not self.analyzer.time_series_features:
            self.analyzer.analyze_temporal_patterns()

        # 预测分析
        if not self.prediction_system.prediction_models:
            self.prediction_system.build_prediction_models()

        if not self.prediction_system.risk_indicators:
            self.prediction_system.calculate_risk_indicators()

        if not self.prediction_system.active_alerts:
            self.prediction_system.generate_conflict_alerts()

    def _generate_summary(self) -> Dict[str, Any]:
        """生成摘要"""
        summary = {
            "数据概览": {
                "实体总数": len(self.analyzer.entities_df) if self.analyzer.entities_df is not None else 0,
                "关系总数": len(self.analyzer.relations_df) if self.analyzer.relations_df is not None else 0,
                "跨域关系数": len(self.analyzer.relations_df[self.analyzer.relations_df['跨域'] == True]) if self.analyzer.relations_df is not None else 0
            },
            "网络特征": {},
            "风险状况": {},
            "主要发现": []
        }

        # 网络特征
        if self.analyzer.network_metrics:
            metrics = self.analyzer.network_metrics
            summary["网络特征"] = {
                "网络密度": round(metrics.density, 4),
                "平均路径长度": round(metrics.avg_path_length, 2),
                "聚类系数": round(metrics.clustering_coefficient, 4),
                "连通性": "连通" if metrics.is_connected else "非连通",
                "连通分量数": metrics.num_components
            }

        # 风险状况
        if self.prediction_system.risk_indicators:
            high_risk_count = len([ind for ind in self.prediction_system.risk_indicators
                                 if ind.risk_level in ['high', 'critical']])
            summary["风险状况"] = {
                "风险指标总数": len(self.prediction_system.risk_indicators),
                "高风险指标数": high_risk_count,
                "活跃预警数": len(self.prediction_system.active_alerts)
            }

        # 主要发现
        findings = []

        # 网络密度发现
        if self.analyzer.network_metrics and self.analyzer.network_metrics.density > 0.3:
            findings.append("网络密度较高，冲突传播风险较大")

        # 社群发现
        if self.analyzer.community_structure and self.analyzer.community_structure.num_communities > 5:
            findings.append(f"发现{self.analyzer.community_structure.num_communities}个社群结构")

        # 升级路径发现
        if hasattr(self.analyzer, 'critical_paths') and len(self.analyzer.critical_paths) > 10:
            findings.append(f"识别{len(self.analyzer.critical_paths)}条关键升级路径")

        # 风险发现
        if self.prediction_system.active_alerts:
            critical_alerts = [alert for alert in self.prediction_system.active_alerts
                             if alert.severity == 'critical']
            if critical_alerts:
                findings.append(f"发现{len(critical_alerts)}个关键风险预警")

        summary["主要发现"] = findings

        return summary

    def _generate_network_analysis(self) -> Dict[str, Any]:
        """生成网络分析结果"""
        analysis = {
            "基础指标": {},
            "中心性分析": {},
            "社群结构": {},
            "鲁棒性分析": {},
            "小世界特性": {}
        }

        # 基础指标
        if self.analyzer.network_metrics:
            metrics = self.analyzer.network_metrics
            analysis["基础指标"] = {
                "节点数": metrics.num_nodes,
                "边数": metrics.num_edges,
                "密度": metrics.density,
                "平均路径长度": metrics.avg_path_length,
                "聚类系数": metrics.clustering_coefficient,
                "传递性": metrics.transitivity,
                "直径": metrics.diameter,
                "半径": metrics.radius,
                "是否连通": metrics.is_connected,
                "连通分量数": metrics.num_components,
                "同配性": metrics.assortativity
            }

        # 中心性分析
        if self.analyzer.centrality_metrics:
            centrality = self.analyzer.centrality_metrics

            # 取前5个最重要的节点
            top_degree = sorted(centrality.degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            top_betweenness = sorted(centrality.betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            top_pagerank = sorted(centrality.pagerank.items(), key=lambda x: x[1], reverse=True)[:5]

            analysis["中心性分析"] = {
                "度中心性排名": [(node, round(score, 4)) for node, score in top_degree],
                "介数中心性排名": [(node, round(score, 4)) for node, score in top_betweenness],
                "PageRank排名": [(node, round(score, 4)) for node, score in top_pagerank]
            }

        # 社群结构
        if self.analyzer.community_structure:
            community = self.analyzer.community_structure
            analysis["社群结构"] = {
                "社群数量": community.num_communities,
                "模块度": round(community.modularity, 4),
                "社群大小分布": community.community_sizes,
                "跨域边数": community.cross_domain_edges,
                "域内边数": community.intra_domain_edges,
                "跨域边比例": round(community.cross_domain_edges / (community.cross_domain_edges + community.intra_domain_edges), 4) if (community.cross_domain_edges + community.intra_domain_edges) > 0 else 0
            }

        # 鲁棒性分析
        if self.analyzer.network_robustness:
            robustness = self.analyzer.network_robustness
            analysis["鲁棒性分析"] = {
                "脆弱性分数": round(robustness.vulnerability_score, 4),
                "关键节点": robustness.critical_nodes[:10],
                "随机攻击结果": robustness.random_attack_results,
                "目标攻击结果": robustness.targeted_attack_results
            }

        return analysis

    def _generate_risk_assessment(self) -> Dict[str, Any]:
        """生成风险评估结果"""
        assessment = {
            "风险指标": [],
            "预警列表": [],
            "风险分布": {},
            "趋势分析": {}
        }

        # 风险指标
        if self.prediction_system.risk_indicators:
            assessment["风险指标"] = [
                {
                    "指标名称": ind.name,
                    "当前值": round(ind.current_value, 4),
                    "风险等级": ind.risk_level,
                    "趋势": ind.trend,
                    "描述": ind.description
                }
                for ind in self.prediction_system.risk_indicators
            ]

        # 预警列表
        if self.prediction_system.active_alerts:
            assessment["预警列表"] = [
                {
                    "预警ID": alert.alert_id,
                    "类型": alert.alert_type,
                    "严重程度": alert.severity,
                    "涉及实体": alert.entities_involved[:5],  # 限制显示数量
                    "影响域": alert.domains_affected,
                    "概率": round(alert.probability, 4),
                    "预期时间": alert.time_to_event,
                    "触发因素": alert.triggers,
                    "建议": alert.recommendations,
                    "置信度": round(alert.confidence, 4)
                }
                for alert in self.prediction_system.active_alerts[:10]  # 只显示前10个
            ]

        # 风险分布
        if self.prediction_system.risk_indicators:
            risk_levels = [ind.risk_level for ind in self.prediction_system.risk_indicators]
            risk_distribution = {level: risk_levels.count(level) for level in set(risk_levels)}
            assessment["风险分布"] = risk_distribution

        return assessment

    def _generate_predictions(self) -> Dict[str, Any]:
        """生成预测结果"""
        predictions = {
            "模型性能": {},
            "升级路径": [],
            "时间序列预测": {},
            "情景分析": []
        }

        # 模型性能
        if self.prediction_system.prediction_models:
            predictions["模型性能"] = {
                model_name: {
                    "交叉验证得分": round(model_data['score'], 4)
                }
                for model_name, model_data in self.prediction_system.prediction_models.items()
            }

        # 升级路径
        if hasattr(self.analyzer, 'critical_paths'):
            predictions["升级路径"] = [
                {
                    "路径ID": f"path_{i}",
                    "源节点": path.source if hasattr(path, 'source') else "未知",
                    "目标节点": path.target if hasattr(path, 'target') else "未知",
                    "路径长度": path.length if hasattr(path, 'length') else 0,
                    "升级潜力": round(path.escalation_potential, 4) if hasattr(path, 'escalation_potential') else 0,
                    "涉及域": path.domains_involved if hasattr(path, 'domains_involved') else []
                }
                for i, path in enumerate(self.analyzer.critical_paths[:10])
            ]

        # 时间序列预测
        if self.analyzer.time_series_features:
            ts_features = self.analyzer.time_series_features
            predictions["时间序列预测"] = {
                "趋势": ts_features.trend,
                "季节性": ts_features.seasonality,
                "周期性": ts_features.periodicity,
                "波动性": round(ts_features.volatility, 4),
                "平稳性": ts_features.stationarity,
                "预测长度": len(ts_features.forecast) if ts_features.forecast is not None else 0
            }

        return predictions

    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于风险指标的建议
        if self.prediction_system.risk_indicators:
            high_risk_indicators = [ind for ind in self.prediction_system.risk_indicators
                                  if ind.risk_level in ['high', 'critical']]

            for indicator in high_risk_indicators:
                if indicator.indicator_id == 'network_density':
                    recommendations.append("建议优化网络结构，减少不必要的连接以降低冲突传播风险")
                elif indicator.indicator_id == 'conflict_intensity':
                    recommendations.append("建议加强冲突调解机制，重点关注高强度冲突关系")
                elif indicator.indicator_id == 'stability_score':
                    recommendations.append("建议加强系统稳定性建设，增加依赖关系的比重")

        # 基于社群结构的建议
        if self.analyzer.community_structure:
            if self.analyzer.community_structure.cross_domain_edges > self.analyzer.community_structure.intra_domain_edges:
                recommendations.append("建议建立跨域协调机制，管理跨域冲突")

        # 基于预警的建议
        if self.prediction_system.active_alerts:
            critical_alerts = [alert for alert in self.prediction_system.active_alerts
                             if alert.severity == 'critical']
            if critical_alerts:
                recommendations.append("建议立即关注关键预警，实施紧急干预措施")

        # 通用建议
        recommendations.extend([
            "建立常态化监控机制，定期更新风险评估",
            "制定应急预案，提高系统对突发冲突的响应能力",
            "加强各域间的沟通协调，建立信息共享机制"
        ])

        return recommendations[:10]  # 限制建议数量

    def _generate_visualizations(self, report_id: str) -> Dict[str, str]:
        """生成可视化图表"""
        logger.info("生成可视化图表...")

        viz_dir = self.output_dir / "visualizations" / report_id
        viz_dir.mkdir(parents=True, exist_ok=True)

        visualizations = {}

        try:
            # 网络图
            network_fig = self.visualizer.create_interactive_network_plot()
            if network_fig:
                network_path = viz_dir / "network_graph.html"
                self.visualizer.export_visualization(network_fig, str(network_path.stem), 'html')
                visualizations["网络图"] = str(network_path)

            # 仪表盘
            dashboard_fig = self.visualizer.create_metrics_dashboard()
            if dashboard_fig:
                dashboard_path = viz_dir / "metrics_dashboard.html"
                self.visualizer.export_visualization(dashboard_fig, str(dashboard_path.stem), 'html')
                visualizations["指标仪表盘"] = str(dashboard_path)

            # 多层网络
            multilayer_fig = self.visualizer.create_multilayer_visualization()
            if multilayer_fig:
                multilayer_path = viz_dir / "multilayer_network.html"
                self.visualizer.export_visualization(multilayer_fig, str(multilayer_path.stem), 'html')
                visualizations["多层网络"] = str(multilayer_path)

        except Exception as e:
            logger.error(f"可视化生成失败: {e}")

        # 生成静态图表
        try:
            # 风险分布图
            risk_chart_path = self._create_risk_distribution_chart(viz_dir)
            if risk_chart_path:
                visualizations["风险分布图"] = str(risk_chart_path)

            # 网络指标图
            metrics_chart_path = self._create_network_metrics_chart(viz_dir)
            if metrics_chart_path:
                visualizations["网络指标图"] = str(metrics_chart_path)

        except Exception as e:
            logger.error(f"静态图表生成失败: {e}")

        return visualizations

    def _create_risk_distribution_chart(self, viz_dir: Path) -> Optional[Path]:
        """创建风险分布图"""
        if not self.prediction_system.risk_indicators:
            return None

        plt.figure(figsize=(10, 6))

        # 风险等级分布
        risk_levels = [ind.risk_level for ind in self.prediction_system.risk_indicators]
        risk_counts = pd.Series(risk_levels).value_counts()

        colors = {'low': '#28a745', 'medium': '#ffc107', 'high': '#fd7e14', 'critical': '#dc3545'}
        risk_colors = [colors.get(level, '#6c757d') for level in risk_counts.index]

        plt.subplot(1, 2, 1)
        plt.pie(risk_counts.values, labels=risk_counts.index, colors=risk_colors, autopct='%1.1f%%')
        plt.title('风险等级分布')

        # 风险指标值分布
        plt.subplot(1, 2, 2)
        risk_values = [ind.current_value for ind in self.prediction_system.risk_indicators]
        plt.hist(risk_values, bins=10, alpha=0.7, color='steelblue')
        plt.xlabel('风险值')
        plt.ylabel('频次')
        plt.title('风险值分布')

        plt.tight_layout()

        chart_path = viz_dir / "risk_distribution.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        return chart_path

    def _create_network_metrics_chart(self, viz_dir: Path) -> Optional[Path]:
        """创建网络指标图"""
        if not self.analyzer.network_metrics:
            return None

        plt.figure(figsize=(12, 8))

        metrics = self.analyzer.network_metrics

        # 指标名称和值
        metric_names = ['密度', '聚类系数', '传递性', '同配性']
        metric_values = [
            metrics.density,
            metrics.clustering_coefficient,
            metrics.transitivity,
            abs(metrics.assortativity)  # 取绝对值
        ]

        # 雷达图
        angles = np.linspace(0, 2 * np.pi, len(metric_names), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # 闭合图形
        values = metric_values + [metric_values[0]]  # 闭合图形

        plt.subplot(2, 2, 1, projection='polar')
        plt.plot(angles, values, 'o-', linewidth=2, color='steelblue')
        plt.fill(angles, values, alpha=0.25, color='steelblue')
        plt.thetagrids(angles[:-1] * 180/np.pi, metric_names)
        plt.ylim(0, 1)
        plt.title('网络指标雷达图')

        # 中心性分布
        if self.analyzer.centrality_metrics:
            centrality = self.analyzer.centrality_metrics

            plt.subplot(2, 2, 2)
            degree_values = list(centrality.degree_centrality.values())
            plt.hist(degree_values, bins=20, alpha=0.7, color='orange')
            plt.xlabel('度中心性')
            plt.ylabel('频次')
            plt.title('度中心性分布')

            plt.subplot(2, 2, 3)
            betweenness_values = list(centrality.betweenness_centrality.values())
            plt.hist(betweenness_values, bins=20, alpha=0.7, color='green')
            plt.xlabel('介数中心性')
            plt.ylabel('频次')
            plt.title('介数中心性分布')

        # 社群大小分布
        if self.analyzer.community_structure:
            plt.subplot(2, 2, 4)
            community_sizes = self.analyzer.community_structure.community_sizes
            plt.bar(range(len(community_sizes)), community_sizes, color='purple', alpha=0.7)
            plt.xlabel('社群ID')
            plt.ylabel('社群大小')
            plt.title('社群大小分布')

        plt.tight_layout()

        chart_path = viz_dir / "network_metrics.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        return chart_path

    def _collect_raw_data(self) -> Dict[str, Any]:
        """收集原始数据"""
        raw_data = {}

        # 网络数据
        if self.analyzer.main_network:
            raw_data["网络统计"] = {
                "节点数": self.analyzer.main_network.number_of_nodes(),
                "边数": self.analyzer.main_network.number_of_edges()
            }

        # 实体数据统计
        if self.analyzer.entities_df is not None:
            raw_data["实体统计"] = {
                "总数": len(self.analyzer.entities_df),
                "类型分布": self.analyzer.entities_df['实体类型'].value_counts().to_dict()
            }

        # 关系数据统计
        if self.analyzer.relations_df is not None:
            raw_data["关系统计"] = {
                "总数": len(self.analyzer.relations_df),
                "类型分布": self.analyzer.relations_df['关系类型'].value_counts().to_dict(),
                "跨域关系数": len(self.analyzer.relations_df[self.analyzer.relations_df['跨域'] == True])
            }

        return raw_data

    def _save_report(self, report: AnalysisReport):
        """保存报告"""
        # 保存JSON格式
        json_path = self.output_dir / f"{report.report_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2, default=str)

        # 生成HTML报告
        html_path = self.output_dir / f"{report.report_id}.html"
        self._generate_html_report(report, html_path)

        logger.info(f"报告已保存: {json_path}, {html_path}")

    def _create_report_template(self) -> str:
        """创建报告模板"""
        template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }
        .section { margin: 30px 0; }
        .section h2 { color: #333; border-left: 4px solid #007bff; padding-left: 10px; }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .metric-card { border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        .risk-high { border-left: 4px solid #dc3545; }
        .risk-medium { border-left: 4px solid #ffc107; }
        .risk-low { border-left: 4px solid #28a745; }
        .alert-critical { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        .alert-high { background-color: #fff3cd; border: 1px solid #ffeaa7; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .visualization { text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report.title }}</h1>
        <p>报告ID: {{ report.report_id }}</p>
        <p>生成时间: {{ report.generated_time.strftime('%Y-%m-%d %H:%M:%S') }}</p>
    </div>

    <div class="section">
        <h2>执行摘要</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <h3>数据概览</h3>
                <p>实体总数: {{ report.summary['数据概览']['实体总数'] }}</p>
                <p>关系总数: {{ report.summary['数据概览']['关系总数'] }}</p>
                <p>跨域关系数: {{ report.summary['数据概览']['跨域关系数'] }}</p>
            </div>
            <div class="metric-card">
                <h3>网络特征</h3>
                {% for key, value in report.summary['网络特征'].items() %}
                <p>{{ key }}: {{ value }}</p>
                {% endfor %}
            </div>
            <div class="metric-card">
                <h3>风险状况</h3>
                {% for key, value in report.summary['风险状况'].items() %}
                <p>{{ key }}: {{ value }}</p>
                {% endfor %}
            </div>
        </div>

        <h3>主要发现</h3>
        <ul>
        {% for finding in report.summary['主要发现'] %}
            <li>{{ finding }}</li>
        {% endfor %}
        </ul>
    </div>

    <div class="section">
        <h2>网络分析结果</h2>

        <h3>基础网络指标</h3>
        <table>
            <tr><th>指标</th><th>值</th></tr>
            {% for key, value in report.network_analysis['基础指标'].items() %}
            <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
            {% endfor %}
        </table>

        <h3>中心性分析</h3>
        {% if report.network_analysis['中心性分析'] %}
        <h4>度中心性排名</h4>
        <ol>
        {% for node, score in report.network_analysis['中心性分析']['度中心性排名'] %}
            <li>{{ node }}: {{ score }}</li>
        {% endfor %}
        </ol>
        {% endif %}
    </div>

    <div class="section">
        <h2>风险评估</h2>

        <h3>风险指标</h3>
        {% for indicator in report.risk_assessment['风险指标'] %}
        <div class="metric-card risk-{{ indicator['风险等级'] }}">
            <h4>{{ indicator['指标名称'] }}</h4>
            <p>当前值: {{ indicator['当前值'] }}</p>
            <p>风险等级: {{ indicator['风险等级'] }}</p>
            <p>趋势: {{ indicator['趋势'] }}</p>
            <p>{{ indicator['描述'] }}</p>
        </div>
        {% endfor %}

        <h3>活跃预警</h3>
        {% for alert in report.risk_assessment['预警列表'] %}
        <div class="metric-card alert-{{ alert['严重程度'] }}">
            <h4>{{ alert['预警ID'] }}</h4>
            <p>类型: {{ alert['类型'] }}</p>
            <p>严重程度: {{ alert['严重程度'] }}</p>
            <p>预期时间: {{ alert['预期时间'] }}天</p>
            <p>置信度: {{ alert['置信度'] }}</p>
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>建议措施</h2>
        <ol>
        {% for recommendation in report.recommendations %}
            <li>{{ recommendation }}</li>
        {% endfor %}
        </ol>
    </div>

    <div class="section">
        <h2>技术附录</h2>
        <h3>原始数据统计</h3>
        <pre>{{ report.raw_data }}</pre>
    </div>

    <footer style="margin-top: 50px; text-align: center; color: #666;">
        <p>跨域冲突网络分析系统 - 自动生成报告</p>
    </footer>
</body>
</html>
        '''
        return template

    def _generate_html_report(self, report: AnalysisReport, output_path: Path):
        """生成HTML报告"""
        if not JINJA2_AVAILABLE:
            logger.warning("Jinja2不可用，无法生成HTML报告")
            return

        try:
            template = Template(self.report_template)
            html_content = template.render(report=report)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"HTML报告已生成: {output_path}")

        except Exception as e:
            logger.error(f"HTML报告生成失败: {e}")

# API接口
class ConflictAnalysisAPI:
    """冲突分析API接口"""

    def __init__(self, report_generator: ComprehensiveReportGenerator):
        """初始化API"""
        self.report_generator = report_generator
        self.app = None

        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            CORS(self.app)
            self._setup_routes()

    def _setup_routes(self):
        """设置API路由"""

        @self.app.route('/api/analyze', methods=['POST'])
        def analyze():
            """执行完整分析"""
            try:
                data = request.get_json()
                title = data.get('title', '跨域冲突网络分析报告')

                report = self.report_generator.generate_comprehensive_report(title)

                return jsonify({
                    'status': 'success',
                    'report_id': report.report_id,
                    'message': '分析完成'
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        @self.app.route('/api/report/<report_id>', methods=['GET'])
        def get_report(report_id):
            """获取报告"""
            try:
                report_path = self.report_generator.output_dir / f"{report_id}.json"

                if not report_path.exists():
                    return jsonify({
                        'status': 'error',
                        'message': '报告不存在'
                    }), 404

                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)

                return jsonify({
                    'status': 'success',
                    'data': report_data
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        @self.app.route('/api/reports', methods=['GET'])
        def list_reports():
            """获取报告列表"""
            try:
                reports = []
                for json_file in self.report_generator.output_dir.glob("*.json"):
                    if json_file.stem.startswith("conflict_analysis_"):
                        reports.append({
                            'report_id': json_file.stem,
                            'created_time': datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
                        })

                reports.sort(key=lambda x: x['created_time'], reverse=True)

                return jsonify({
                    'status': 'success',
                    'data': reports
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            })

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行API服务"""
        if not FLASK_AVAILABLE:
            logger.error("Flask不可用，无法启动API服务")
            return

        logger.info(f"启动API服务: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # 测试报告生成器
    from dynamic_conflict_analyzer import DynamicConflictAnalyzer
    from conflict_prediction_system import ConflictPredictionSystem

    # 初始化系统
    analyzer = DynamicConflictAnalyzer()

    # 加载数据
    json_path = "/d/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
    analyzer.load_data(json_path=json_path)

    # 构建网络
    analyzer.build_main_network()

    # 预测系统
    prediction_system = ConflictPredictionSystem(analyzer)

    # 报告生成器
    report_generator = ComprehensiveReportGenerator(prediction_system)

    # 生成报告
    report = report_generator.generate_comprehensive_report()

    print("综合报告生成完成！")
    print(f"报告ID: {report.report_id}")
    print(f"报告文件: {report_generator.output_dir / f'{report.report_id}.html'}")

    # 启动API服务（可选）
    # api = ConflictAnalysisAPI(report_generator)
    # api.run(debug=True)