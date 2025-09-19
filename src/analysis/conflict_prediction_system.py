"""
冲突预警和情景分析系统
实现早期预警、风险评估、情景模拟、干预策略评估等功能
"""

import json
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from dataclasses import dataclass, field
import logging
from pathlib import Path
import itertools
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 机器学习库
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.cluster import KMeans

# 统计和优化
from scipy import stats
from scipy.optimize import minimize
from scipy.special import expit

# 时间序列
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# 从分析器导入
from dynamic_conflict_analyzer import DynamicConflictAnalyzer, ConflictState, EscalationPath
from network_visualizer import NetworkVisualizer

# 设置中文字体
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RiskIndicator:
    """风险指标"""
    indicator_id: str
    name: str
    current_value: float
    threshold_low: float
    threshold_medium: float
    threshold_high: float
    risk_level: str
    trend: str  # 'increasing', 'decreasing', 'stable'
    description: str

@dataclass
class ConflictAlert:
    """冲突预警"""
    alert_id: str
    alert_type: str  # 'immediate', 'short_term', 'medium_term', 'long_term'
    severity: str  # 'low', 'medium', 'high', 'critical'
    entities_involved: List[str]
    domains_affected: List[str]
    probability: float
    time_to_event: float  # 预期发生时间（天）
    triggers: List[str]
    recommendations: List[str]
    confidence: float

@dataclass
class InterventionStrategy:
    """干预策略"""
    strategy_id: str
    name: str
    target_entities: List[str]
    target_relations: List[str]
    intervention_type: str  # 'strengthen', 'weaken', 'remove', 'add'
    cost: float
    effectiveness: float
    side_effects: List[str]
    implementation_time: float

@dataclass
class ScenarioAnalysis:
    """情景分析"""
    scenario_id: str
    name: str
    description: str
    initial_conditions: Dict[str, Any]
    interventions: List[InterventionStrategy]
    predicted_outcomes: Dict[str, float]
    risk_changes: Dict[str, float]
    confidence_interval: Tuple[float, float]

class ConflictPredictionSystem:
    """冲突预测系统"""

    def __init__(self, analyzer: DynamicConflictAnalyzer):
        """初始化预测系统"""
        self.analyzer = analyzer
        self.prediction_models = {}
        self.risk_indicators = []
        self.active_alerts = []
        self.intervention_strategies = []
        self.scenario_cache = {}

        # 模型配置
        self.model_config = {
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            },
            'gradient_boosting': {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 6,
                'random_state': 42
            },
            'logistic_regression': {
                'random_state': 42,
                'max_iter': 1000
            }
        }

        # 风险阈值
        self.risk_thresholds = {
            'network_density': {'low': 0.1, 'medium': 0.3, 'high': 0.5},
            'conflict_intensity': {'low': 0.2, 'medium': 0.5, 'high': 0.8},
            'stability_score': {'low': 0.7, 'medium': 0.5, 'high': 0.3},
            'escalation_probability': {'low': 0.1, 'medium': 0.3, 'high': 0.6}
        }

    def build_prediction_models(self) -> Dict[str, Any]:
        """构建预测模型"""
        logger.info("构建冲突预测模型...")

        # 生成训练数据
        training_data = self._generate_training_data()

        if training_data is None or len(training_data) < 50:
            logger.warning("训练数据不足，使用模拟数据")
            training_data = self._generate_simulated_training_data()

        # 特征工程
        X, y = self._prepare_features(training_data)

        if X is None or len(X) == 0:
            logger.error("特征数据准备失败")
            return {}

        # 训练多个模型
        models = {}

        # 随机森林
        try:
            rf_model = RandomForestClassifier(**self.model_config['random_forest'])
            rf_model.fit(X, y)
            models['random_forest'] = {
                'model': rf_model,
                'score': cross_val_score(rf_model, X, y, cv=5).mean()
            }
            logger.info(f"随机森林模型训练完成，CV得分: {models['random_forest']['score']:.4f}")
        except Exception as e:
            logger.error(f"随机森林模型训练失败: {e}")

        # 梯度提升
        try:
            gb_model = GradientBoostingClassifier(**self.model_config['gradient_boosting'])
            gb_model.fit(X, y)
            models['gradient_boosting'] = {
                'model': gb_model,
                'score': cross_val_score(gb_model, X, y, cv=5).mean()
            }
            logger.info(f"梯度提升模型训练完成，CV得分: {models['gradient_boosting']['score']:.4f}")
        except Exception as e:
            logger.error(f"梯度提升模型训练失败: {e}")

        # 逻辑回归
        try:
            lr_model = LogisticRegression(**self.model_config['logistic_regression'])
            lr_model.fit(X, y)
            models['logistic_regression'] = {
                'model': lr_model,
                'score': cross_val_score(lr_model, X, y, cv=5).mean()
            }
            logger.info(f"逻辑回归模型训练完成，CV得分: {models['logistic_regression']['score']:.4f}")
        except Exception as e:
            logger.error(f"逻辑回归模型训练失败: {e}")

        # 选择最佳模型
        if models:
            best_model_name = max(models.keys(), key=lambda k: models[k]['score'])
            self.prediction_models = models
            logger.info(f"最佳模型: {best_model_name}")

        return models

    def _generate_training_data(self) -> Optional[List[Dict]]:
        """从现有数据生成训练样本"""
        if not self.analyzer.main_network:
            return None

        training_samples = []
        graph = self.analyzer.main_network

        # 基于社群结构生成样本
        if self.analyzer.community_structure:
            communities = self.analyzer.community_structure.communities

            for comm_id, nodes in communities.items():
                # 计算社群特征
                subgraph = graph.subgraph(nodes)
                features = self._extract_subgraph_features(subgraph, graph)

                # 生成标签（基于冲突强度）
                conflict_intensity = features.get('conflict_intensity', 0)
                label = 1 if conflict_intensity > 0.5 else 0

                sample = {
                    'features': features,
                    'label': label,
                    'timestamp': datetime.now(),
                    'entities': nodes
                }

                training_samples.append(sample)

        # 基于路径生成样本
        if hasattr(self.analyzer, 'critical_paths'):
            for path in self.analyzer.critical_paths[:20]:
                features = self._extract_path_features(path, graph)
                label = 1 if path.escalation_potential > 0.6 else 0

                sample = {
                    'features': features,
                    'label': label,
                    'timestamp': datetime.now(),
                    'entities': path.path
                }

                training_samples.append(sample)

        return training_samples if training_samples else None

    def _generate_simulated_training_data(self, n_samples: int = 1000) -> List[Dict]:
        """生成模拟训练数据"""
        logger.info(f"生成 {n_samples} 个模拟训练样本...")

        training_samples = []

        for i in range(n_samples):
            # 随机生成特征
            features = {
                'network_density': np.random.uniform(0.05, 0.8),
                'clustering_coefficient': np.random.uniform(0.1, 0.9),
                'avg_path_length': np.random.uniform(1.5, 8.0),
                'conflict_intensity': np.random.uniform(0.0, 1.0),
                'stability_score': np.random.uniform(0.1, 1.0),
                'cross_domain_ratio': np.random.uniform(0.0, 0.8),
                'num_entities': np.random.randint(3, 50),
                'num_domains': np.random.randint(1, 4),
                'importance_score': np.random.uniform(0.2, 3.0)
            }

            # 生成标签（基于复合规则）
            risk_score = (
                features['conflict_intensity'] * 0.4 +
                (1 - features['stability_score']) * 0.3 +
                features['cross_domain_ratio'] * 0.2 +
                min(features['network_density'], 0.5) * 0.1
            )

            # 添加噪声
            risk_score += np.random.normal(0, 0.1)
            label = 1 if risk_score > 0.5 else 0

            sample = {
                'features': features,
                'label': label,
                'timestamp': datetime.now() - timedelta(days=np.random.randint(0, 365)),
                'entities': [f'entity_{j}' for j in range(features['num_entities'])]
            }

            training_samples.append(sample)

        return training_samples

    def _extract_subgraph_features(self, subgraph: nx.Graph, main_graph: nx.Graph) -> Dict[str, float]:
        """提取子图特征"""
        features = {}

        # 基础网络特征
        features['network_density'] = nx.density(subgraph) if subgraph.number_of_nodes() > 1 else 0
        features['clustering_coefficient'] = nx.average_clustering(subgraph)

        # 路径长度特征
        if nx.is_connected(subgraph.to_undirected()) and subgraph.number_of_nodes() > 1:
            features['avg_path_length'] = nx.average_shortest_path_length(subgraph.to_undirected())
        else:
            features['avg_path_length'] = 0

        # 冲突特征
        conflict_edges = 0
        total_conflict_strength = 0
        for _, _, data in subgraph.edges(data=True):
            relation_type = data.get('relation_type', '')
            strength = data.get('strength', 1.0)

            if relation_type in ['对立', '竞争']:
                conflict_edges += 1
                total_conflict_strength += strength

        features['conflict_intensity'] = total_conflict_strength / max(subgraph.number_of_edges(), 1)
        features['conflict_edge_ratio'] = conflict_edges / max(subgraph.number_of_edges(), 1)

        # 稳定性特征
        dependency_edges = sum(1 for _, _, data in subgraph.edges(data=True)
                             if data.get('relation_type') == '依赖')
        features['stability_score'] = dependency_edges / max(subgraph.number_of_edges(), 1)

        # 跨域特征
        domains = set()
        for node in subgraph.nodes():
            if node in main_graph.nodes:
                node_domains = main_graph.nodes[node].get('domains', [])
                domains.update(node_domains)

        features['num_domains'] = len(domains)
        features['cross_domain_ratio'] = min(len(domains) / 4.0, 1.0)  # 假设最多4个域

        # 重要性特征
        total_importance = sum(main_graph.nodes[node].get('importance_weight', 1.0)
                             for node in subgraph.nodes() if node in main_graph.nodes)
        features['importance_score'] = total_importance / max(subgraph.number_of_nodes(), 1)

        # 规模特征
        features['num_entities'] = subgraph.number_of_nodes()
        features['num_relations'] = subgraph.number_of_edges()

        return features

    def _extract_path_features(self, path: Any, graph: nx.Graph) -> Dict[str, float]:
        """提取路径特征"""
        features = {}

        if hasattr(path, 'path') and hasattr(path, 'escalation_potential'):
            # 路径长度
            features['path_length'] = len(path.path) - 1

            # 升级潜力
            features['escalation_potential'] = path.escalation_potential

            # 路径强度
            features['path_strength'] = getattr(path, 'strength', 0.5)

            # 涉及域数量
            domains = set()
            for node in path.path:
                if node in graph.nodes:
                    node_domains = graph.nodes[node].get('domains', [])
                    domains.update(node_domains)

            features['num_domains'] = len(domains)
            features['cross_domain_ratio'] = min(len(domains) / 4.0, 1.0)

        else:
            # 默认特征
            features = {
                'path_length': 3,
                'escalation_potential': 0.5,
                'path_strength': 0.5,
                'num_domains': 2,
                'cross_domain_ratio': 0.5
            }

        return features

    def _prepare_features(self, training_data: List[Dict]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """准备特征数据"""
        if not training_data:
            return None, None

        # 提取特征和标签
        features_list = []
        labels = []

        for sample in training_data:
            features = sample['features']
            label = sample['label']

            # 标准化特征向量
            feature_vector = [
                features.get('network_density', 0),
                features.get('clustering_coefficient', 0),
                features.get('avg_path_length', 0),
                features.get('conflict_intensity', 0),
                features.get('stability_score', 0),
                features.get('cross_domain_ratio', 0),
                features.get('num_entities', 0),
                features.get('num_domains', 0),
                features.get('importance_score', 0)
            ]

            features_list.append(feature_vector)
            labels.append(label)

        X = np.array(features_list)
        y = np.array(labels)

        # 特征标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        return X_scaled, y

    def calculate_risk_indicators(self) -> List[RiskIndicator]:
        """计算风险指标"""
        logger.info("计算风险指标...")

        indicators = []

        # 网络密度指标
        if self.analyzer.network_metrics:
            density = self.analyzer.network_metrics.density
            density_indicator = RiskIndicator(
                indicator_id="network_density",
                name="网络密度",
                current_value=density,
                threshold_low=self.risk_thresholds['network_density']['low'],
                threshold_medium=self.risk_thresholds['network_density']['medium'],
                threshold_high=self.risk_thresholds['network_density']['high'],
                risk_level=self._assess_risk_level(density, 'network_density'),
                trend=self._analyze_trend([density]),  # 简化的趋势分析
                description="网络连接密度，过高可能导致冲突快速传播"
            )
            indicators.append(density_indicator)

        # 冲突强度指标
        conflict_intensity = self._calculate_overall_conflict_intensity()
        conflict_indicator = RiskIndicator(
            indicator_id="conflict_intensity",
            name="整体冲突强度",
            current_value=conflict_intensity,
            threshold_low=self.risk_thresholds['conflict_intensity']['low'],
            threshold_medium=self.risk_thresholds['conflict_intensity']['medium'],
            threshold_high=self.risk_thresholds['conflict_intensity']['high'],
            risk_level=self._assess_risk_level(conflict_intensity, 'conflict_intensity'),
            trend=self._analyze_trend([conflict_intensity]),
            description="整体冲突强度，反映系统内对立关系的激烈程度"
        )
        indicators.append(conflict_indicator)

        # 系统稳定性指标
        stability_score = self._calculate_system_stability()
        stability_indicator = RiskIndicator(
            indicator_id="stability_score",
            name="系统稳定性",
            current_value=stability_score,
            threshold_low=self.risk_thresholds['stability_score']['low'],
            threshold_medium=self.risk_thresholds['stability_score']['medium'],
            threshold_high=self.risk_thresholds['stability_score']['high'],
            risk_level=self._assess_risk_level(stability_score, 'stability_score', reverse=True),
            trend=self._analyze_trend([stability_score]),
            description="系统整体稳定性，越低表示越容易发生剧变"
        )
        indicators.append(stability_indicator)

        # 升级风险指标
        escalation_prob = self._calculate_escalation_probability()
        escalation_indicator = RiskIndicator(
            indicator_id="escalation_probability",
            name="升级概率",
            current_value=escalation_prob,
            threshold_low=self.risk_thresholds['escalation_probability']['low'],
            threshold_medium=self.risk_thresholds['escalation_probability']['medium'],
            threshold_high=self.risk_thresholds['escalation_probability']['high'],
            risk_level=self._assess_risk_level(escalation_prob, 'escalation_probability'),
            trend=self._analyze_trend([escalation_prob]),
            description="冲突升级的概率，基于历史模式和当前状态预测"
        )
        indicators.append(escalation_indicator)

        self.risk_indicators = indicators
        logger.info(f"计算完成 {len(indicators)} 个风险指标")

        return indicators

    def _calculate_overall_conflict_intensity(self) -> float:
        """计算整体冲突强度"""
        if not self.analyzer.main_network:
            return 0.0

        graph = self.analyzer.main_network
        conflict_edges = 0
        total_conflict_strength = 0
        total_edges = 0

        for _, _, data in graph.edges(data=True):
            relation_type = data.get('relation_type', '')
            strength = data.get('strength', 1.0)
            total_edges += 1

            if relation_type in ['对立', '竞争']:
                conflict_edges += 1
                total_conflict_strength += strength * 2  # 对立关系权重更高
            elif relation_type == '制约':
                conflict_edges += 0.5
                total_conflict_strength += strength

        if total_edges == 0:
            return 0.0

        # 标准化冲突强度
        conflict_ratio = conflict_edges / total_edges
        avg_strength = total_conflict_strength / total_edges
        return min(1.0, conflict_ratio * avg_strength)

    def _calculate_system_stability(self) -> float:
        """计算系统稳定性"""
        if not self.analyzer.main_network:
            return 1.0

        graph = self.analyzer.main_network

        # 因素1: 依赖关系比例
        dependency_ratio = 0.0
        if graph.number_of_edges() > 0:
            dependency_edges = sum(1 for _, _, data in graph.edges(data=True)
                                 if data.get('relation_type') == '依赖')
            dependency_ratio = dependency_edges / graph.number_of_edges()

        # 因素2: 网络聚类系数
        clustering_coeff = 0.0
        if self.analyzer.network_metrics:
            clustering_coeff = self.analyzer.network_metrics.clustering_coefficient

        # 因素3: 连通性
        connectivity_score = 1.0
        if self.analyzer.network_metrics:
            if not self.analyzer.network_metrics.is_connected:
                connectivity_score = 0.7

        # 综合稳定性分数
        stability = (dependency_ratio * 0.4 + clustering_coeff * 0.3 + connectivity_score * 0.3)
        return min(1.0, stability)

    def _calculate_escalation_probability(self) -> float:
        """计算升级概率"""
        if hasattr(self.analyzer, 'conflict_dynamics') and self.analyzer.conflict_dynamics:
            # 基于动态模型
            dynamics = self.analyzer.conflict_dynamics
            if dynamics.escalation_paths:
                avg_escalation_prob = np.mean([
                    path.escalation_probability for path in dynamics.escalation_paths[:10]
                ])
                return min(1.0, avg_escalation_prob)

        # 基于静态特征估算
        conflict_intensity = self._calculate_overall_conflict_intensity()
        stability_score = self._calculate_system_stability()

        # 简单的升级概率模型
        escalation_prob = conflict_intensity * (1 - stability_score) * 0.8

        return min(1.0, escalation_prob)

    def _assess_risk_level(self, value: float, indicator_type: str, reverse: bool = False) -> str:
        """评估风险等级"""
        thresholds = self.risk_thresholds.get(indicator_type, {})

        if not reverse:
            if value <= thresholds.get('low', 0.1):
                return 'low'
            elif value <= thresholds.get('medium', 0.3):
                return 'medium'
            elif value <= thresholds.get('high', 0.5):
                return 'high'
            else:
                return 'critical'
        else:
            # 对于稳定性等指标，值越低风险越高
            if value >= thresholds.get('low', 0.7):
                return 'low'
            elif value >= thresholds.get('medium', 0.5):
                return 'medium'
            elif value >= thresholds.get('high', 0.3):
                return 'high'
            else:
                return 'critical'

    def _analyze_trend(self, values: List[float]) -> str:
        """分析趋势"""
        if len(values) < 2:
            return 'stable'

        # 简单的趋势分析
        if len(values) == 1:
            return 'stable'

        slope = (values[-1] - values[0]) / len(values)

        if slope > 0.05:
            return 'increasing'
        elif slope < -0.05:
            return 'decreasing'
        else:
            return 'stable'

    def generate_conflict_alerts(self) -> List[ConflictAlert]:
        """生成冲突预警"""
        logger.info("生成冲突预警...")

        alerts = []

        # 基于风险指标生成预警
        for indicator in self.risk_indicators:
            if indicator.risk_level in ['high', 'critical']:
                alert = self._create_indicator_alert(indicator)
                if alert:
                    alerts.append(alert)

        # 基于社群分析生成预警
        if self.analyzer.community_structure:
            community_alerts = self._analyze_community_risks()
            alerts.extend(community_alerts)

        # 基于路径分析生成预警
        if hasattr(self.analyzer, 'critical_paths'):
            path_alerts = self._analyze_path_risks()
            alerts.extend(path_alerts)

        # 按严重程度排序
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        alerts.sort(key=lambda x: severity_order.get(x.severity, 0), reverse=True)

        self.active_alerts = alerts[:20]  # 保留前20个最重要的预警
        logger.info(f"生成 {len(self.active_alerts)} 个冲突预警")

        return self.active_alerts

    def _create_indicator_alert(self, indicator: RiskIndicator) -> Optional[ConflictAlert]:
        """基于指标创建预警"""
        if indicator.risk_level not in ['high', 'critical']:
            return None

        # 估算时间到事件
        if indicator.trend == 'increasing':
            time_to_event = 7  # 7天
        elif indicator.trend == 'stable':
            time_to_event = 30  # 30天
        else:
            time_to_event = 90  # 90天

        # 调整严重程度
        if indicator.risk_level == 'critical':
            severity = 'critical'
            time_to_event *= 0.5  # 更紧急
        else:
            severity = 'high'

        alert = ConflictAlert(
            alert_id=f"indicator_{indicator.indicator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            alert_type='medium_term' if time_to_event > 14 else 'short_term',
            severity=severity,
            entities_involved=[],  # 指标级别预警不涉及特定实体
            domains_affected=[],
            probability=indicator.current_value,
            time_to_event=time_to_event,
            triggers=[f"{indicator.name}达到{indicator.risk_level}风险等级"],
            recommendations=self._generate_indicator_recommendations(indicator),
            confidence=0.7
        )

        return alert

    def _analyze_community_risks(self) -> List[ConflictAlert]:
        """分析社群风险"""
        alerts = []

        if not self.analyzer.community_structure:
            return alerts

        communities = self.analyzer.community_structure.communities

        for comm_id, nodes in communities.items():
            subgraph = self.analyzer.main_network.subgraph(nodes)
            features = self._extract_subgraph_features(subgraph, self.analyzer.main_network)

            # 评估风险
            risk_score = (
                features.get('conflict_intensity', 0) * 0.4 +
                (1 - features.get('stability_score', 1)) * 0.3 +
                features.get('cross_domain_ratio', 0) * 0.3
            )

            if risk_score > 0.6:
                # 获取涉及的域
                domains = set()
                for node in nodes:
                    if node in self.analyzer.main_network.nodes:
                        node_domains = self.analyzer.main_network.nodes[node].get('domains', [])
                        domains.update(node_domains)

                alert = ConflictAlert(
                    alert_id=f"community_{comm_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type='short_term',
                    severity='high' if risk_score > 0.8 else 'medium',
                    entities_involved=nodes[:10],  # 限制数量
                    domains_affected=list(domains),
                    probability=risk_score,
                    time_to_event=14 if risk_score > 0.8 else 30,
                    triggers=[f"社群{comm_id}冲突强度过高"],
                    recommendations=self._generate_community_recommendations(comm_id, features),
                    confidence=0.8
                )

                alerts.append(alert)

        return alerts

    def _analyze_path_risks(self) -> List[ConflictAlert]:
        """分析路径风险"""
        alerts = []

        if not hasattr(self.analyzer, 'critical_paths'):
            return alerts

        for i, path in enumerate(self.analyzer.critical_paths[:10]):
            if hasattr(path, 'escalation_potential') and path.escalation_potential > 0.7:
                # 获取涉及的域
                domains = set()
                for node in path.path if hasattr(path, 'path') else []:
                    if node in self.analyzer.main_network.nodes:
                        node_domains = self.analyzer.main_network.nodes[node].get('domains', [])
                        domains.update(node_domains)

                alert = ConflictAlert(
                    alert_id=f"path_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_type='immediate' if path.escalation_potential > 0.9 else 'short_term',
                    severity='critical' if path.escalation_potential > 0.9 else 'high',
                    entities_involved=path.path if hasattr(path, 'path') else [],
                    domains_affected=list(domains),
                    probability=path.escalation_potential,
                    time_to_event=3 if path.escalation_potential > 0.9 else 7,
                    triggers=[f"升级路径{i}风险过高"],
                    recommendations=self._generate_path_recommendations(path),
                    confidence=0.9
                )

                alerts.append(alert)

        return alerts

    def _generate_indicator_recommendations(self, indicator: RiskIndicator) -> List[str]:
        """生成指标建议"""
        recommendations = []

        if indicator.indicator_id == 'network_density':
            if indicator.risk_level == 'high':
                recommendations.append("考虑减少不必要的连接关系")
                recommendations.append("加强关键节点的隔离保护")
        elif indicator.indicator_id == 'conflict_intensity':
            recommendations.append("优先处理高冲突强度的关系")
            recommendations.append("建立冲突调解机制")
        elif indicator.indicator_id == 'stability_score':
            recommendations.append("加强系统内依赖关系建设")
            recommendations.append("提高关键节点的稳定性")

        return recommendations

    def _generate_community_recommendations(self, comm_id: int, features: Dict) -> List[str]:
        """生成社群建议"""
        recommendations = []

        if features.get('conflict_intensity', 0) > 0.7:
            recommendations.append(f"对社群{comm_id}实施冲突调解")

        if features.get('stability_score', 1) < 0.3:
            recommendations.append(f"加强社群{comm_id}的内部稳定性")

        if features.get('cross_domain_ratio', 0) > 0.6:
            recommendations.append(f"建立社群{comm_id}的跨域协调机制")

        return recommendations

    def _generate_path_recommendations(self, path: Any) -> List[str]:
        """生成路径建议"""
        recommendations = [
            "监控升级路径中的关键节点",
            "实施早期干预措施",
            "加强路径中薄弱环节"
        ]

        return recommendations

if __name__ == "__main__":
    # 测试预测系统
    from dynamic_conflict_analyzer import DynamicConflictAnalyzer

    analyzer = DynamicConflictAnalyzer()

    # 加载数据
    json_path = "/d/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
    analyzer.load_data(json_path=json_path)

    # 分析
    analyzer.build_main_network()
    analyzer.calculate_network_metrics()
    analyzer.detect_communities_advanced()

    # 预测系统
    prediction_system = ConflictPredictionSystem(analyzer)

    # 构建模型
    models = prediction_system.build_prediction_models()

    # 风险评估
    risk_indicators = prediction_system.calculate_risk_indicators()

    # 预警生成
    alerts = prediction_system.generate_conflict_alerts()

    print("冲突预测系统测试完成！")
    print(f"训练模型: {len(models)} 个")
    print(f"风险指标: {len(risk_indicators)} 个")
    print(f"生成预警: {len(alerts)} 个")

    # 显示高风险指标
    high_risk = [ind for ind in risk_indicators if ind.risk_level in ['high', 'critical']]
    print(f"高风险指标: {len(high_risk)} 个")
    for ind in high_risk:
        print(f"  - {ind.name}: {ind.current_value:.3f} ({ind.risk_level})")