"""
跨域冲突网络分析系统主程序
整合所有分析模块，提供统一的分析入口
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入分析模块
from src.analysis.conflict_network_analyzer import ConflictNetworkAnalyzer
from src.analysis.advanced_network_analyzer import AdvancedNetworkAnalyzer
from src.analysis.dynamic_conflict_analyzer import DynamicConflictAnalyzer
from src.analysis.network_visualizer import NetworkVisualizer
from src.analysis.conflict_prediction_system import ConflictPredictionSystem
from src.analysis.comprehensive_report_generator import ComprehensiveReportGenerator, ConflictAnalysisAPI

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/d/work/novellus/logs/conflict_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConflictAnalysisSystem:
    """跨域冲突分析系统主类"""

    def __init__(self, config: Dict[str, Any] = None):
        """初始化分析系统"""
        self.config = config or self._default_config()
        self.analyzer = None
        self.prediction_system = None
        self.report_generator = None
        self.api_server = None

        # 确保输出目录存在
        self._ensure_directories()

        logger.info("跨域冲突分析系统初始化完成")

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "data": {
                "entities_path": "/d/work/novellus/enhanced_conflict_output/entities.csv",
                "relations_path": "/d/work/novellus/enhanced_conflict_output/relations.csv",
                "json_path": "/d/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
            },
            "analysis": {
                "enable_advanced_analysis": True,
                "enable_dynamic_analysis": True,
                "enable_prediction": True,
                "enable_visualization": True
            },
            "output": {
                "base_dir": "/d/work/novellus/output",
                "generate_html_report": True,
                "generate_json_report": True,
                "generate_visualizations": True
            },
            "api": {
                "enable_api_server": False,
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False
            },
            "visualization": {
                "layout_algorithm": "spring",
                "color_scheme": "domain",
                "interactive": True,
                "export_static_charts": True
            },
            "prediction": {
                "model_types": ["random_forest", "gradient_boosting", "logistic_regression"],
                "risk_thresholds": {
                    "network_density": {"low": 0.1, "medium": 0.3, "high": 0.5},
                    "conflict_intensity": {"low": 0.2, "medium": 0.5, "high": 0.8}
                }
            }
        }

    def _ensure_directories(self):
        """确保必要的目录存在"""
        dirs = [
            Path("/d/work/novellus/output"),
            Path("/d/work/novellus/output/visualizations"),
            Path("/d/work/novellus/output/reports"),
            Path("/d/work/novellus/logs")
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def load_data(self, data_source: str = None) -> bool:
        """加载数据"""
        try:
            logger.info("开始加载数据...")

            # 初始化分析器
            self.analyzer = DynamicConflictAnalyzer()

            # 确定数据源
            if data_source:
                if data_source.endswith('.json'):
                    self.analyzer.load_data(json_path=data_source)
                else:
                    logger.error(f"不支持的数据格式: {data_source}")
                    return False
            else:
                # 使用配置中的数据路径
                data_config = self.config["data"]
                if Path(data_config["json_path"]).exists():
                    self.analyzer.load_data(json_path=data_config["json_path"])
                elif Path(data_config["entities_path"]).exists() and Path(data_config["relations_path"]).exists():
                    self.analyzer.load_data(
                        entities_path=data_config["entities_path"],
                        relations_path=data_config["relations_path"]
                    )
                else:
                    logger.error("未找到有效的数据文件")
                    return False

            logger.info("数据加载完成")
            return True

        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            return False

    def run_analysis(self) -> bool:
        """运行完整分析"""
        try:
            logger.info("开始执行网络分析...")

            if not self.analyzer:
                logger.error("分析器未初始化，请先加载数据")
                return False

            # 1. 基础网络分析
            logger.info("执行基础网络分析...")
            self.analyzer.build_main_network()
            self.analyzer.calculate_network_metrics()
            self.analyzer.calculate_centrality_metrics()

            # 2. 多层网络分析
            if self.config["analysis"]["enable_advanced_analysis"]:
                logger.info("执行高级网络分析...")
                self.analyzer.build_domain_networks()
                self.analyzer.build_type_networks()
                self.analyzer.build_relation_networks()
                self.analyzer.detect_communities_advanced()
                self.analyzer.identify_critical_paths_advanced()
                self.analyzer.analyze_network_robustness_advanced()

            # 3. 动态分析
            if self.config["analysis"]["enable_dynamic_analysis"]:
                logger.info("执行动态网络分析...")
                self.analyzer.build_conflict_state_model()
                self.analyzer.analyze_temporal_patterns()

            # 4. 预测分析
            if self.config["analysis"]["enable_prediction"]:
                logger.info("执行预测分析...")
                self.prediction_system = ConflictPredictionSystem(self.analyzer)
                self.prediction_system.build_prediction_models()
                self.prediction_system.calculate_risk_indicators()
                self.prediction_system.generate_conflict_alerts()

            logger.info("网络分析完成")
            return True

        except Exception as e:
            logger.error(f"网络分析失败: {e}")
            return False

    def generate_report(self, title: str = "跨域冲突网络分析报告") -> Optional[str]:
        """生成分析报告"""
        try:
            logger.info("开始生成分析报告...")

            if not self.prediction_system:
                logger.error("预测系统未初始化，请先运行分析")
                return None

            # 初始化报告生成器
            self.report_generator = ComprehensiveReportGenerator(self.prediction_system)

            # 生成报告
            report = self.report_generator.generate_comprehensive_report(title)

            logger.info(f"报告生成完成: {report.report_id}")
            return report.report_id

        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return None

    def create_visualizations(self) -> bool:
        """创建可视化"""
        try:
            if not self.config["analysis"]["enable_visualization"]:
                logger.info("可视化功能已禁用")
                return True

            logger.info("开始创建可视化...")

            if not self.analyzer:
                logger.error("分析器未初始化")
                return False

            # 初始化可视化器
            visualizer = NetworkVisualizer(self.analyzer)

            # 创建交互式网络图
            network_fig = visualizer.create_interactive_network_plot()
            if network_fig:
                visualizer.export_visualization(network_fig, "interactive_network", "html")

            # 创建多层网络可视化
            multilayer_fig = visualizer.create_multilayer_visualization()
            if multilayer_fig:
                visualizer.export_visualization(multilayer_fig, "multilayer_network", "html")

            # 创建指标仪表盘
            dashboard_fig = visualizer.create_metrics_dashboard()
            if dashboard_fig:
                visualizer.export_visualization(dashboard_fig, "metrics_dashboard", "html")

            logger.info("可视化创建完成")
            return True

        except Exception as e:
            logger.error(f"可视化创建失败: {e}")
            return False

    def start_api_server(self):
        """启动API服务器"""
        try:
            if not self.config["api"]["enable_api_server"]:
                logger.info("API服务器已禁用")
                return

            if not self.report_generator:
                logger.error("报告生成器未初始化，请先运行分析")
                return

            logger.info("启动API服务器...")

            self.api_server = ConflictAnalysisAPI(self.report_generator)
            api_config = self.config["api"]

            self.api_server.run(
                host=api_config["host"],
                port=api_config["port"],
                debug=api_config["debug"]
            )

        except Exception as e:
            logger.error(f"API服务器启动失败: {e}")

    def run_complete_analysis(self, data_source: str = None, report_title: str = None) -> Dict[str, Any]:
        """运行完整的分析流程"""
        results = {
            "success": False,
            "report_id": None,
            "error_message": None,
            "analysis_summary": {}
        }

        try:
            # 1. 加载数据
            if not self.load_data(data_source):
                results["error_message"] = "数据加载失败"
                return results

            # 2. 执行分析
            if not self.run_analysis():
                results["error_message"] = "网络分析失败"
                return results

            # 3. 创建可视化
            self.create_visualizations()

            # 4. 生成报告
            report_title = report_title or "跨域冲突网络分析报告"
            report_id = self.generate_report(report_title)

            if not report_id:
                results["error_message"] = "报告生成失败"
                return results

            # 5. 收集分析摘要
            analysis_summary = self._collect_analysis_summary()

            results.update({
                "success": True,
                "report_id": report_id,
                "analysis_summary": analysis_summary
            })

            logger.info("完整分析流程执行成功")
            return results

        except Exception as e:
            logger.error(f"完整分析流程失败: {e}")
            results["error_message"] = str(e)
            return results

    def _collect_analysis_summary(self) -> Dict[str, Any]:
        """收集分析摘要"""
        summary = {}

        try:
            # 网络基础指标
            if self.analyzer and self.analyzer.network_metrics:
                metrics = self.analyzer.network_metrics
                summary["network_metrics"] = {
                    "nodes": metrics.num_nodes,
                    "edges": metrics.num_edges,
                    "density": round(metrics.density, 4),
                    "clustering_coefficient": round(metrics.clustering_coefficient, 4),
                    "avg_path_length": round(metrics.avg_path_length, 2)
                }

            # 社群结构
            if self.analyzer and self.analyzer.community_structure:
                community = self.analyzer.community_structure
                summary["community_structure"] = {
                    "num_communities": community.num_communities,
                    "modularity": round(community.modularity, 4),
                    "cross_domain_edges": community.cross_domain_edges,
                    "intra_domain_edges": community.intra_domain_edges
                }

            # 风险评估
            if self.prediction_system and self.prediction_system.risk_indicators:
                high_risk_count = len([ind for ind in self.prediction_system.risk_indicators
                                     if ind.risk_level in ['high', 'critical']])
                summary["risk_assessment"] = {
                    "total_indicators": len(self.prediction_system.risk_indicators),
                    "high_risk_indicators": high_risk_count,
                    "active_alerts": len(self.prediction_system.active_alerts)
                }

            # 预测模型
            if self.prediction_system and self.prediction_system.prediction_models:
                best_model = max(self.prediction_system.prediction_models.keys(),
                               key=lambda k: self.prediction_system.prediction_models[k]['score'])
                summary["prediction_models"] = {
                    "best_model": best_model,
                    "model_count": len(self.prediction_system.prediction_models),
                    "best_score": round(self.prediction_system.prediction_models[best_model]['score'], 4)
                }

        except Exception as e:
            logger.error(f"分析摘要收集失败: {e}")

        return summary

    def print_analysis_summary(self):
        """打印分析摘要"""
        if not self.analyzer:
            print("分析器未初始化")
            return

        print("\n" + "="*50)
        print("跨域冲突网络分析摘要")
        print("="*50)

        # 网络基础信息
        if self.analyzer.network_metrics:
            metrics = self.analyzer.network_metrics
            print(f"\n网络基础指标:")
            print(f"  节点数: {metrics.num_nodes}")
            print(f"  边数: {metrics.num_edges}")
            print(f"  网络密度: {metrics.density:.4f}")
            print(f"  平均路径长度: {metrics.avg_path_length:.2f}")
            print(f"  聚类系数: {metrics.clustering_coefficient:.4f}")
            print(f"  连通性: {'是' if metrics.is_connected else '否'}")

        # 社群结构
        if self.analyzer.community_structure:
            community = self.analyzer.community_structure
            print(f"\n社群结构:")
            print(f"  社群数量: {community.num_communities}")
            print(f"  模块度: {community.modularity:.4f}")
            print(f"  跨域连接: {community.cross_domain_edges}")
            print(f"  域内连接: {community.intra_domain_edges}")

        # 关键路径
        if hasattr(self.analyzer, 'critical_paths') and self.analyzer.critical_paths:
            print(f"\n关键路径:")
            print(f"  识别路径数: {len(self.analyzer.critical_paths)}")
            top_paths = sorted(self.analyzer.critical_paths,
                             key=lambda x: getattr(x, 'escalation_potential', 0), reverse=True)[:3]
            for i, path in enumerate(top_paths, 1):
                escalation = getattr(path, 'escalation_potential', 0)
                print(f"  路径{i}升级潜力: {escalation:.3f}")

        # 风险评估
        if self.prediction_system and self.prediction_system.risk_indicators:
            indicators = self.prediction_system.risk_indicators
            risk_levels = [ind.risk_level for ind in indicators]
            print(f"\n风险评估:")
            print(f"  风险指标总数: {len(indicators)}")
            print(f"  高风险指标: {risk_levels.count('high')}个")
            print(f"  关键风险指标: {risk_levels.count('critical')}个")
            print(f"  活跃预警: {len(self.prediction_system.active_alerts)}个")

        # 预测模型
        if self.prediction_system and self.prediction_system.prediction_models:
            models = self.prediction_system.prediction_models
            best_model = max(models.keys(), key=lambda k: models[k]['score'])
            print(f"\n预测模型:")
            print(f"  训练模型数: {len(models)}")
            print(f"  最佳模型: {best_model}")
            print(f"  最佳得分: {models[best_model]['score']:.4f}")

        print("="*50)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='跨域冲突网络分析系统')
    parser.add_argument('--data', type=str, help='数据文件路径')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--output', type=str, help='输出目录')
    parser.add_argument('--title', type=str, default='跨域冲突网络分析报告', help='报告标题')
    parser.add_argument('--api', action='store_true', help='启动API服务器')
    parser.add_argument('--port', type=int, default=5000, help='API服务器端口')
    parser.add_argument('--debug', action='store_true', help='调试模式')

    args = parser.parse_args()

    # 加载配置
    config = None
    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    # 初始化系统
    system = ConflictAnalysisSystem(config)

    # 更新配置
    if args.output:
        system.config["output"]["base_dir"] = args.output

    if args.api:
        system.config["api"]["enable_api_server"] = True
        system.config["api"]["port"] = args.port
        system.config["api"]["debug"] = args.debug

    try:
        # 运行完整分析
        results = system.run_complete_analysis(
            data_source=args.data,
            report_title=args.title
        )

        if results["success"]:
            print(f"\n分析完成！报告ID: {results['report_id']}")
            system.print_analysis_summary()

            # 启动API服务器
            if args.api:
                system.start_api_server()
        else:
            print(f"分析失败: {results['error_message']}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n分析中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"系统错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()