"""
综合跨域冲突网络模型
实现完整的网络分析框架，包括拓扑分析、强度建模、社团发现、
中心性分析、传播动力学、稳定性分析、时序演化和多层网络建模
"""

import json
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter, deque
import logging
from pathlib import Path
import itertools
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats, sparse, optimize
from scipy.spatial.distance import pdist, squareform
from scipy.integrate import odeint
from sklearn.cluster import KMeans, SpectralClustering, DBSCAN
from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA, NMF
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import time
import datetime

# 网络分析相关库
try:
    import community as community_louvain  # python-louvain
    HAS_LOUVAIN = True
except ImportError:
    community_louvain = None
    HAS_LOUVAIN = False

try:
    import igraph as ig
    HAS_IGRAPH = True
except ImportError:
    ig = None
    HAS_IGRAPH = False

# 可视化库
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    import plotly.io as pio
    HAS_PLOTLY = True
except ImportError:
    go = px = make_subplots = pyo = pio = None
    HAS_PLOTLY = False

# 设置警告过滤
warnings.filterwarnings('ignore', category=FutureWarning)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NetworkTopologyMetrics:
    """网络拓扑指标"""
    # 基础指标
    num_nodes: int
    num_edges: int
    density: float
    avg_degree: float
    degree_variance: float

    # 连通性指标
    is_connected: bool
    num_components: int
    largest_component_size: int
    component_sizes: List[int]

    # 路径指标
    avg_path_length: float
    diameter: int
    radius: int
    eccentricity_stats: Dict[str, float]

    # 聚类指标
    global_clustering: float
    local_clustering_avg: float
    transitivity: float

    # 度分布指标
    degree_distribution: Dict[int, int]
    power_law_exponent: Optional[float]
    power_law_fit_quality: Optional[float]

    # 同配性
    degree_assortativity: float
    attribute_assortativity: Dict[str, float]

    # 小世界性质
    small_world_sigma: Optional[float]
    small_world_omega: Optional[float]

@dataclass
class ConflictIntensityModel:
    """冲突强度模型"""
    intensity_matrix: np.ndarray
    node_intensities: Dict[str, float]
    edge_intensities: Dict[Tuple[str, str], float]

    # 强度分布
    intensity_distribution: Dict[str, float]
    intensity_percentiles: Dict[int, float]

    # 动态参数
    decay_rate: float
    escalation_threshold: float
    diffusion_coefficient: float

    # 预测模型
    intensity_predictor: Any
    prediction_accuracy: float

@dataclass
class CommunityStructure:
    """社团结构分析"""
    # Louvain算法结果
    louvain_communities: Dict[int, List[str]]
    louvain_modularity: float

    # 其他算法结果
    spectral_communities: Dict[int, List[str]]
    infomap_communities: Optional[Dict[int, List[str]]]

    # 社团特征
    num_communities: int
    community_sizes: List[int]
    community_densities: Dict[int, float]
    community_conductance: Dict[int, float]

    # 跨域分析
    cross_domain_edges: int
    intra_domain_edges: int
    domain_mixing_matrix: np.ndarray

    # 社团中心性
    community_centralities: Dict[int, Dict[str, float]]
    bridge_nodes: List[str]

@dataclass
class CentralityAnalysis:
    """中心性分析结果"""
    # 基础中心性
    degree_centrality: Dict[str, float]
    betweenness_centrality: Dict[str, float]
    closeness_centrality: Dict[str, float]
    eigenvector_centrality: Dict[str, float]

    # 高级中心性
    pagerank: Dict[str, float]
    hits_hubs: Dict[str, float]
    hits_authorities: Dict[str, float]
    katz_centrality: Dict[str, float]

    # 自定义中心性
    conflict_centrality: Dict[str, float]
    cross_domain_centrality: Dict[str, float]

    # 排名和分析
    centrality_rankings: Dict[str, List[Tuple[str, float]]]
    centrality_correlations: np.ndarray
    critical_nodes: Dict[str, List[str]]

@dataclass
class ConflictPropagationModel:
    """冲突传播动力学模型"""
    # 传播参数
    transmission_rate: float
    recovery_rate: float
    spontaneous_rate: float

    # 网络效应
    influence_matrix: np.ndarray
    propagation_paths: Dict[str, List[List[str]]]

    # 级联分析
    cascade_size_distribution: Dict[int, int]
    critical_cascade_threshold: float

    # 时间序列预测
    propagation_timeline: Dict[str, List[float]]
    peak_conflict_times: Dict[str, float]

@dataclass
class NetworkRobustness:
    """网络稳定性和韧性"""
    # 攻击测试结果
    random_attack_threshold: float
    targeted_attack_threshold: float

    # 脆弱性分析
    vulnerability_scores: Dict[str, float]
    critical_failure_nodes: List[str]

    # 恢复能力
    recovery_times: Dict[str, float]
    resilience_metrics: Dict[str, float]

    # 风险评估
    systemic_risk_score: float
    failure_probability: Dict[str, float]

@dataclass
class TemporalEvolution:
    """时序演化模型"""
    # 历史数据
    historical_snapshots: List[nx.Graph]
    evolution_timeline: List[datetime.datetime]

    # 变化检测
    structural_changes: List[Dict[str, Any]]
    change_points: List[int]

    # 预测模型
    evolution_predictor: Any
    future_predictions: Dict[str, Any]

    # 生命周期分析
    relationship_lifecycles: Dict[Tuple[str, str], Dict[str, float]]
    emergence_patterns: Dict[str, float]
    dissolution_patterns: Dict[str, float]

@dataclass
class MultilayerNetworkModel:
    """多层网络模型"""
    # 层定义
    layers: Dict[str, nx.Graph]
    layer_weights: Dict[str, float]

    # 跨层连接
    interlayer_edges: Dict[Tuple[str, str], List[Tuple[str, str]]]
    layer_coupling_strength: Dict[Tuple[str, str], float]

    # 多层指标
    multilayer_centrality: Dict[str, Dict[str, float]]
    layer_relevance: Dict[str, float]

    # 聚合网络
    aggregated_network: nx.Graph
    aggregation_weights: Dict[Tuple[str, str], float]

class ComprehensiveConflictNetworkModel:
    """综合跨域冲突网络模型主类"""

    def __init__(self, data_path: str = None, config: Dict[str, Any] = None):
        """
        初始化综合网络模型

        Args:
            data_path: 数据文件路径
            config: 配置参数字典
        """
        self.data_path = data_path
        self.config = config or {}

        # 数据存储
        self.entities_df = None
        self.relations_df = None
        self.conflict_data = None

        # 网络对象
        self.main_network = None
        self.domain_networks = {}
        self.type_networks = {}
        self.relation_networks = {}

        # 分析结果
        self.topology_metrics = None
        self.intensity_model = None
        self.community_structure = None
        self.centrality_analysis = None
        self.propagation_model = None
        self.robustness_analysis = None
        self.temporal_evolution = None
        self.multilayer_model = None

        # 配置参数
        self.random_seed = self.config.get('random_seed', 42)
        self.enable_caching = self.config.get('enable_caching', True)
        self.parallel_processing = self.config.get('parallel_processing', False)

        # 设置随机种子
        np.random.seed(self.random_seed)

        # 缓存
        self._cache = {} if self.enable_caching else None

        logger.info("综合冲突网络模型初始化完成")

    def load_data(self, data_source: Union[str, Dict[str, Any]] = None):
        """
        加载数据

        Args:
            data_source: 数据源，可以是文件路径或数据字典
        """
        try:
            if data_source is None:
                data_source = self.data_path

            if isinstance(data_source, str):
                logger.info(f"从文件加载数据: {data_source}")
                with open(data_source, 'r', encoding='utf-8') as f:
                    self.conflict_data = json.load(f)
            elif isinstance(data_source, dict):
                logger.info("从字典加载数据")
                self.conflict_data = data_source
            else:
                raise ValueError("不支持的数据源类型")

            # 转换为DataFrame
            self._convert_to_dataframes()
            self._preprocess_data()

            logger.info(f"数据加载完成: {len(self.entities_df)} 个实体, {len(self.relations_df)} 个关系")

        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            raise

    def _convert_to_dataframes(self):
        """将数据转换为DataFrame格式"""
        # 实体数据
        entities_data = []
        for entity in self.conflict_data.get('entities', []):
            entities_data.append({
                'ID': entity['id'],
                '名称': entity['name'],
                '实体类型': entity['entity_type'],
                '域归属': ';'.join(entity.get('domains', [])),
                '重要性': entity.get('importance', '中'),
                '描述': entity.get('description', ''),
                '置信度': entity.get('confidence', 0.8),
                '提取方法': entity.get('extraction_method', 'auto'),
                '坐标': entity.get('coordinates', [0, 0]),
                '创建时间': entity.get('created_at', datetime.datetime.now().isoformat())
            })
        self.entities_df = pd.DataFrame(entities_data)

        # 关系数据
        relations_data = []
        for relation in self.conflict_data.get('relations', []):
            relations_data.append({
                'ID': relation['id'],
                '源实体ID': relation['source_entity_id'],
                '目标实体ID': relation['target_entity_id'],
                '关系类型': relation['relation_type'],
                '强度': relation.get('strength', 1.0),
                '描述': relation.get('description', ''),
                '跨域': relation.get('cross_domain', False),
                '置信度': relation.get('confidence', 0.8),
                '摩擦热度': relation.get('friction_heat', 0.5),
                '升级潜力': relation.get('escalation_potential', 0.3),
                '创建时间': relation.get('created_at', datetime.datetime.now().isoformat())
            })
        self.relations_df = pd.DataFrame(relations_data)

    def _preprocess_data(self):
        """数据预处理"""
        if self.entities_df is not None:
            # 处理域归属字段
            self.entities_df['域列表'] = self.entities_df['域归属'].apply(
                lambda x: [d.strip() for d in str(x).split(';')] if pd.notna(x) else []
            )

            # 重要性权重映射
            importance_weights = {'高': 3, '中高': 2.5, '中': 2, '中低': 1.5, '低': 1}
            self.entities_df['重要性权重'] = self.entities_df['重要性'].map(importance_weights).fillna(2)

            # 处理坐标数据
            self.entities_df['x坐标'] = self.entities_df['坐标'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.random.uniform(-1, 1))
            self.entities_df['y坐标'] = self.entities_df['坐标'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.random.uniform(-1, 1))

        if self.relations_df is not None:
            # 确保数值字段为浮点类型
            numeric_cols = ['强度', '置信度', '摩擦热度', '升级潜力']
            for col in numeric_cols:
                if col in self.relations_df.columns:
                    self.relations_df[col] = pd.to_numeric(self.relations_df[col], errors='coerce').fillna(0.5)

    def build_main_network(self) -> nx.Graph:
        """构建主网络图"""
        try:
            logger.info("构建主网络图...")

            # 创建有向多重图以支持多种关系类型
            G = nx.MultiDiGraph()

            # 添加节点
            for _, entity in self.entities_df.iterrows():
                G.add_node(
                    entity['ID'],
                    name=entity['名称'],
                    entity_type=entity['实体类型'],
                    domains=entity.get('域列表', []),
                    importance=entity['重要性'],
                    importance_weight=entity.get('重要性权重', 2),
                    description=entity.get('描述', ''),
                    confidence=entity.get('置信度', 0.8),
                    x=entity.get('x坐标', 0),
                    y=entity.get('y坐标', 0),
                    created_at=entity.get('创建时间', '')
                )

            # 添加边
            for _, relation in self.relations_df.iterrows():
                source = relation['源实体ID']
                target = relation['目标实体ID']

                if source in G.nodes and target in G.nodes:
                    G.add_edge(
                        source,
                        target,
                        key=relation['ID'],
                        relation_type=relation['关系类型'],
                        strength=relation['强度'],
                        cross_domain=relation.get('跨域', False),
                        description=relation.get('描述', ''),
                        confidence=relation.get('置信度', 0.8),
                        friction_heat=relation.get('摩擦热度', 0.5),
                        escalation_potential=relation.get('升级潜力', 0.3),
                        created_at=relation.get('创建时间', '')
                    )

            self.main_network = G
            logger.info(f"主网络构建完成: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
            return G

        except Exception as e:
            logger.error(f"主网络构建失败: {e}")
            raise

    def build_conflict_intensity_model(self, graph: nx.Graph = None) -> ConflictIntensityModel:
        """
        构建冲突强度量化模型

        Args:
            graph: 要分析的网络图，默认为主网络

        Returns:
            ConflictIntensityModel: 冲突强度模型结果
        """
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        logger.info("构建冲突强度模型...")

        try:
            # 获取所有节点和边
            nodes = list(graph.nodes())
            edges = list(graph.edges(data=True))

            # 构建强度矩阵
            node_to_idx = {node: idx for idx, node in enumerate(nodes)}
            n_nodes = len(nodes)
            intensity_matrix = np.zeros((n_nodes, n_nodes))

            # 边强度字典
            edge_intensities = {}

            # 基于多维因素计算强度
            for source, target, data in edges:
                source_idx = node_to_idx[source]
                target_idx = node_to_idx[target]

                # 基础强度
                base_strength = data.get('strength', 1.0)

                # 摩擦热度
                friction_heat = data.get('friction_heat', 0.5)

                # 升级潜力
                escalation_potential = data.get('escalation_potential', 0.3)

                # 置信度权重
                confidence = data.get('confidence', 0.8)

                # 跨域加权
                cross_domain_weight = 1.5 if data.get('cross_domain', False) else 1.0

                # 关系类型权重
                relation_type_weights = {
                    '对立': 2.0,
                    '竞争': 1.5,
                    '制约': 1.3,
                    '依赖': 0.8,
                    '合作': 0.5
                }
                relation_weight = relation_type_weights.get(data.get('relation_type', ''), 1.0)

                # 综合强度计算
                total_intensity = (
                    base_strength * 0.3 +
                    friction_heat * 0.25 +
                    escalation_potential * 0.25 +
                    cross_domain_weight * 0.1 +
                    relation_weight * 0.1
                ) * confidence

                intensity_matrix[source_idx, target_idx] = total_intensity
                edge_intensities[(source, target)] = total_intensity

            # 节点强度计算
            node_intensities = {}
            for node in nodes:
                idx = node_to_idx[node]

                # 出度强度
                out_intensity = np.sum(intensity_matrix[idx, :])

                # 入度强度
                in_intensity = np.sum(intensity_matrix[:, idx])

                # 节点属性权重
                node_data = graph.nodes[node]
                importance_weight = node_data.get('importance_weight', 2)

                # 综合节点强度
                node_intensity = (out_intensity + in_intensity) * importance_weight / 2
                node_intensities[node] = node_intensity

            # 强度分布统计
            all_intensities = list(edge_intensities.values()) + list(node_intensities.values())
            intensity_distribution = {
                'mean': np.mean(all_intensities),
                'std': np.std(all_intensities),
                'min': np.min(all_intensities),
                'max': np.max(all_intensities),
                'median': np.median(all_intensities)
            }

            # 强度百分位数
            intensity_percentiles = {}
            for p in [10, 25, 50, 75, 90, 95, 99]:
                intensity_percentiles[p] = np.percentile(all_intensities, p)

            # 动态参数估计
            decay_rate = 0.1  # 冲突衰减率
            escalation_threshold = intensity_percentiles[75]  # 升级阈值
            diffusion_coefficient = 0.3  # 扩散系数

            # 简单的强度预测模型
            from sklearn.linear_model import LinearRegression

            # 构建特征矩阵用于预测
            X_features = []
            y_intensities = []

            for (source, target), intensity in edge_intensities.items():
                source_data = graph.nodes[source]
                target_data = graph.nodes[target]

                features = [
                    source_data.get('importance_weight', 2),
                    target_data.get('importance_weight', 2),
                    len(source_data.get('domains', [])),
                    len(target_data.get('domains', [])),
                    1 if set(source_data.get('domains', [])).intersection(set(target_data.get('domains', []))) else 0
                ]

                X_features.append(features)
                y_intensities.append(intensity)

            intensity_predictor = None
            prediction_accuracy = 0.0

            if len(X_features) > 5:  # 需要足够的样本
                try:
                    X = np.array(X_features)
                    y = np.array(y_intensities)

                    # 训练预测模型
                    intensity_predictor = LinearRegression()
                    intensity_predictor.fit(X, y)

                    # 计算预测准确度
                    y_pred = intensity_predictor.predict(X)
                    prediction_accuracy = 1 - np.mean(np.abs(y - y_pred) / (y + 1e-8))

                except Exception as e:
                    logger.warning(f"强度预测模型训练失败: {e}")

            # 构建结果对象
            intensity_model = ConflictIntensityModel(
                intensity_matrix=intensity_matrix,
                node_intensities=node_intensities,
                edge_intensities=edge_intensities,
                intensity_distribution=intensity_distribution,
                intensity_percentiles=intensity_percentiles,
                decay_rate=decay_rate,
                escalation_threshold=escalation_threshold,
                diffusion_coefficient=diffusion_coefficient,
                intensity_predictor=intensity_predictor,
                prediction_accuracy=prediction_accuracy
            )

            self.intensity_model = intensity_model
            logger.info(f"冲突强度模型构建完成，平均强度: {intensity_distribution['mean']:.3f}")
            return intensity_model

        except Exception as e:
            logger.error(f"冲突强度模型构建失败: {e}")
            raise

    def discover_communities(self, graph: nx.Graph = None, methods: List[str] = None) -> CommunityStructure:
        """
        社团发现和聚类分析

        Args:
            graph: 要分析的网络图，默认为主网络
            methods: 使用的社团发现方法列表

        Returns:
            CommunityStructure: 社团结构分析结果
        """
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        if methods is None:
            methods = ['louvain', 'spectral']

        logger.info("开始社团发现分析...")

        try:
            # 转换为无向图
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph

            # Louvain算法
            louvain_communities = {}
            louvain_modularity = 0.0

            if 'louvain' in methods and HAS_LOUVAIN:
                try:
                    partition = community_louvain.best_partition(undirected_graph)
                    louvain_modularity = community_louvain.modularity(partition, undirected_graph)

                    # 重组社团结构
                    communities_dict = defaultdict(list)
                    for node, community_id in partition.items():
                        communities_dict[community_id].append(node)
                    louvain_communities = dict(communities_dict)

                except Exception as e:
                    logger.warning(f"Louvain算法失败: {e}")

            # 谱聚类
            spectral_communities = {}

            if 'spectral' in methods:
                try:
                    # 使用邻接矩阵进行谱聚类
                    adj_matrix = nx.adjacency_matrix(undirected_graph).toarray()

                    # 估计最优聚类数
                    n_nodes = adj_matrix.shape[0]
                    max_clusters = min(10, n_nodes // 2)

                    if max_clusters >= 2:
                        best_score = -1
                        best_n_clusters = 2

                        for n_clusters in range(2, max_clusters + 1):
                            try:
                                clustering = SpectralClustering(
                                    n_clusters=n_clusters,
                                    affinity='precomputed',
                                    random_state=self.random_seed
                                )
                                cluster_labels = clustering.fit_predict(adj_matrix)
                                score = silhouette_score(adj_matrix, cluster_labels, metric='precomputed')

                                if score > best_score:
                                    best_score = score
                                    best_n_clusters = n_clusters
                            except:
                                continue

                        # 使用最优聚类数进行最终聚类
                        clustering = SpectralClustering(
                            n_clusters=best_n_clusters,
                            affinity='precomputed',
                            random_state=self.random_seed
                        )
                        cluster_labels = clustering.fit_predict(adj_matrix)

                        # 重组社团结构
                        nodes = list(undirected_graph.nodes())
                        communities_dict = defaultdict(list)
                        for i, label in enumerate(cluster_labels):
                            communities_dict[label].append(nodes[i])
                        spectral_communities = dict(communities_dict)

                except Exception as e:
                    logger.warning(f"谱聚类失败: {e}")

            # 使用Louvain结果作为主要结果
            main_communities = louvain_communities if louvain_communities else spectral_communities

            if not main_communities:
                # 如果所有方法都失败，创建单一社团
                main_communities = {0: list(graph.nodes())}

            # 社团特征分析
            num_communities = len(main_communities)
            community_sizes = [len(nodes) for nodes in main_communities.values()]

            # 社团密度计算
            community_densities = {}
            for comm_id, nodes in main_communities.items():
                subgraph = undirected_graph.subgraph(nodes)
                community_densities[comm_id] = nx.density(subgraph)

            # 社团导纳度计算
            community_conductance = {}
            for comm_id, nodes in main_communities.items():
                internal_edges = 0
                external_edges = 0

                for node in nodes:
                    for neighbor in undirected_graph.neighbors(node):
                        if neighbor in nodes:
                            internal_edges += 1
                        else:
                            external_edges += 1

                total_edges = internal_edges + external_edges
                if total_edges > 0:
                    community_conductance[comm_id] = external_edges / total_edges
                else:
                    community_conductance[comm_id] = 0.0

            # 跨域分析
            cross_domain_edges = 0
            intra_domain_edges = 0

            for u, v in undirected_graph.edges():
                u_domains = set(graph.nodes[u].get('domains', []))
                v_domains = set(graph.nodes[v].get('domains', []))

                if u_domains.intersection(v_domains):
                    intra_domain_edges += 1
                else:
                    cross_domain_edges += 1

            # 域混合矩阵
            all_domains = set()
            for node in graph.nodes():
                all_domains.update(graph.nodes[node].get('domains', []))

            domain_list = sorted(list(all_domains))
            domain_mixing_matrix = np.zeros((len(domain_list), len(domain_list)))

            for u, v in undirected_graph.edges():
                u_domains = graph.nodes[u].get('domains', [])
                v_domains = graph.nodes[v].get('domains', [])

                for u_domain in u_domains:
                    for v_domain in v_domains:
                        if u_domain in domain_list and v_domain in domain_list:
                            i = domain_list.index(u_domain)
                            j = domain_list.index(v_domain)
                            domain_mixing_matrix[i, j] += 1

            # 社团中心性计算
            community_centralities = {}
            try:
                centrality_metrics = self.analyze_centrality(graph)

                for comm_id, nodes in main_communities.items():
                    comm_centralities = {}

                    # 计算社团内节点的平均中心性
                    for centrality_name, centrality_dict in centrality_metrics.items():
                        if isinstance(centrality_dict, dict):
                            comm_values = [centrality_dict.get(node, 0) for node in nodes]
                            comm_centralities[centrality_name] = np.mean(comm_values) if comm_values else 0

                    community_centralities[comm_id] = comm_centralities
            except:
                community_centralities = {}

            # 桥梁节点识别
            bridge_nodes = []
            try:
                betweenness = nx.betweenness_centrality(undirected_graph)
                threshold = np.percentile(list(betweenness.values()), 80)
                bridge_nodes = [node for node, score in betweenness.items() if score >= threshold]
            except:
                pass

            # 构建结果对象
            community_structure = CommunityStructure(
                louvain_communities=louvain_communities,
                louvain_modularity=louvain_modularity,
                spectral_communities=spectral_communities,
                infomap_communities=None,  # 可以后续添加
                num_communities=num_communities,
                community_sizes=community_sizes,
                community_densities=community_densities,
                community_conductance=community_conductance,
                cross_domain_edges=cross_domain_edges,
                intra_domain_edges=intra_domain_edges,
                domain_mixing_matrix=domain_mixing_matrix,
                community_centralities=community_centralities,
                bridge_nodes=bridge_nodes
            )

            self.community_structure = community_structure
            logger.info(f"社团发现完成: 发现{num_communities}个社团，模块度: {louvain_modularity:.3f}")
            return community_structure

        except Exception as e:
            logger.error(f"社团发现失败: {e}")
            raise

    def analyze_centrality(self, graph: nx.Graph = None) -> CentralityAnalysis:
        """
        全面的中心性分析

        Args:
            graph: 要分析的网络图，默认为主网络

        Returns:
            CentralityAnalysis: 中心性分析结果
        """
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        logger.info("开始中心性分析...")

        try:
            # 转换为无向图进行某些计算
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph

            # 基础中心性指标
            degree_centrality = nx.degree_centrality(undirected_graph)
            betweenness_centrality = nx.betweenness_centrality(undirected_graph)
            closeness_centrality = nx.closeness_centrality(undirected_graph)

            # 特征向量中心性
            try:
                eigenvector_centrality = nx.eigenvector_centrality(undirected_graph, max_iter=1000)
            except:
                eigenvector_centrality = degree_centrality
                logger.warning("特征向量中心性计算失败，使用度中心性代替")

            # PageRank（适用于有向图）
            pagerank = nx.pagerank(graph)

            # HITS算法
            try:
                hits_hubs, hits_authorities = nx.hits(graph, max_iter=1000)
            except:
                hits_hubs = hits_authorities = degree_centrality
                logger.warning("HITS算法计算失败，使用度中心性代替")

            # Katz中心性
            try:
                katz_centrality = nx.katz_centrality(graph, max_iter=1000)
            except:
                katz_centrality = degree_centrality
                logger.warning("Katz中心性计算失败，使用度中心性代替")

            # 自定义冲突中心性
            conflict_centrality = {}
            for node in graph.nodes():
                # 基于冲突强度的中心性
                if self.intensity_model:
                    conflict_score = self.intensity_model.node_intensities.get(node, 0)
                else:
                    # 简单的冲突中心性计算
                    conflict_score = 0
                    for neighbor in graph.neighbors(node):
                        edge_data = graph.get_edge_data(node, neighbor)
                        if edge_data:
                            # 对于多重图，取最大强度
                            if isinstance(edge_data, dict) and 'strength' in edge_data:
                                conflict_score += edge_data['strength']
                            else:
                                # 多重边情况
                                max_strength = 0
                                for edge_key, edge_attr in edge_data.items():
                                    if isinstance(edge_attr, dict):
                                        max_strength = max(max_strength, edge_attr.get('strength', 0))
                                conflict_score += max_strength

                conflict_centrality[node] = conflict_score

            # 跨域中心性
            cross_domain_centrality = {}
            for node in graph.nodes():
                node_domains = set(graph.nodes[node].get('domains', []))
                cross_domain_score = 0

                for neighbor in graph.neighbors(node):
                    neighbor_domains = set(graph.nodes[neighbor].get('domains', []))
                    if not node_domains.intersection(neighbor_domains):  # 跨域连接
                        cross_domain_score += 1

                cross_domain_centrality[node] = cross_domain_score

            # 中心性排名
            centrality_rankings = {}
            centrality_dict = {
                'degree': degree_centrality,
                'betweenness': betweenness_centrality,
                'closeness': closeness_centrality,
                'eigenvector': eigenvector_centrality,
                'pagerank': pagerank,
                'conflict': conflict_centrality,
                'cross_domain': cross_domain_centrality
            }

            for name, centrality in centrality_dict.items():
                sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
                centrality_rankings[name] = sorted_nodes[:10]  # 取前10名

            # 中心性相关性分析
            centrality_values = []
            centrality_names = []

            for name, centrality in centrality_dict.items():
                values = [centrality.get(node, 0) for node in graph.nodes()]
                centrality_values.append(values)
                centrality_names.append(name)

            centrality_correlations = np.corrcoef(centrality_values)

            # 关键节点识别
            critical_nodes = {}

            # 高中心性节点
            high_centrality_nodes = set()
            for name, rankings in centrality_rankings.items():
                top_nodes = [node for node, score in rankings[:5]]
                high_centrality_nodes.update(top_nodes)
            critical_nodes['high_centrality'] = list(high_centrality_nodes)

            # 高冲突节点
            conflict_threshold = np.percentile(list(conflict_centrality.values()), 80)
            high_conflict_nodes = [node for node, score in conflict_centrality.items() if score >= conflict_threshold]
            critical_nodes['high_conflict'] = high_conflict_nodes

            # 跨域桥梁节点
            cross_domain_threshold = np.percentile(list(cross_domain_centrality.values()), 75)
            bridge_nodes = [node for node, score in cross_domain_centrality.items() if score >= cross_domain_threshold]
            critical_nodes['cross_domain_bridges'] = bridge_nodes

            # 构建结果对象
            centrality_analysis = CentralityAnalysis(
                degree_centrality=degree_centrality,
                betweenness_centrality=betweenness_centrality,
                closeness_centrality=closeness_centrality,
                eigenvector_centrality=eigenvector_centrality,
                pagerank=pagerank,
                hits_hubs=hits_hubs,
                hits_authorities=hits_authorities,
                katz_centrality=katz_centrality,
                conflict_centrality=conflict_centrality,
                cross_domain_centrality=cross_domain_centrality,
                centrality_rankings=centrality_rankings,
                centrality_correlations=centrality_correlations,
                critical_nodes=critical_nodes
            )

            self.centrality_analysis = centrality_analysis
            logger.info("中心性分析完成")
            return centrality_analysis

        except Exception as e:
            logger.error(f"中心性分析失败: {e}")
            raise

    def analyze_network_topology(self, graph: nx.Graph = None) -> NetworkTopologyMetrics:
        """
        全面的网络拓扑分析

        Args:
            graph: 要分析的网络图，默认为主网络

        Returns:
            NetworkTopologyMetrics: 拓扑分析结果
        """
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        logger.info("开始网络拓扑分析...")

        # 检查缓存
        cache_key = f"topology_metrics_{hash(str(sorted(graph.nodes())))}"
        if self._cache and cache_key in self._cache:
            logger.info("使用缓存的拓扑分析结果")
            return self._cache[cache_key]

        try:
            # 转换为简单无向图进行分析
            simple_graph = nx.Graph()
            for u, v in graph.edges():
                if not simple_graph.has_edge(u, v):
                    simple_graph.add_edge(u, v)

            # 基础指标
            num_nodes = simple_graph.number_of_nodes()
            num_edges = simple_graph.number_of_edges()
            density = nx.density(simple_graph)

            # 度分析
            degrees = dict(simple_graph.degree())
            degree_values = list(degrees.values())
            avg_degree = np.mean(degree_values) if degree_values else 0
            degree_variance = np.var(degree_values) if degree_values else 0

            # 连通性分析
            is_connected = nx.is_connected(simple_graph)
            components = list(nx.connected_components(simple_graph))
            num_components = len(components)
            component_sizes = [len(comp) for comp in components]
            largest_component_size = max(component_sizes) if component_sizes else 0

            # 路径分析
            if is_connected:
                avg_path_length = nx.average_shortest_path_length(simple_graph)
                diameter = nx.diameter(simple_graph)
                radius = nx.radius(simple_graph)
                eccentricities = nx.eccentricity(simple_graph)
            else:
                # 对最大连通分量进行分析
                if component_sizes:
                    largest_component = max(components, key=len)
                    largest_subgraph = simple_graph.subgraph(largest_component)
                    avg_path_length = nx.average_shortest_path_length(largest_subgraph)
                    diameter = nx.diameter(largest_subgraph)
                    radius = nx.radius(largest_subgraph)
                    eccentricities = nx.eccentricity(largest_subgraph)
                else:
                    avg_path_length = diameter = radius = 0
                    eccentricities = {}

            # 偏心率统计
            ecc_values = list(eccentricities.values()) if eccentricities else [0]
            eccentricity_stats = {
                'mean': np.mean(ecc_values),
                'std': np.std(ecc_values),
                'min': np.min(ecc_values),
                'max': np.max(ecc_values)
            }

            # 聚类分析
            global_clustering = nx.average_clustering(simple_graph)
            local_clustering = nx.clustering(simple_graph)
            local_clustering_avg = np.mean(list(local_clustering.values())) if local_clustering else 0
            transitivity = nx.transitivity(simple_graph)

            # 度分布分析
            degree_distribution = dict(Counter(degree_values))

            # 幂律拟合
            power_law_exponent = None
            power_law_fit_quality = None
            if len(set(degree_values)) > 2:
                try:
                    from scipy.stats import linregress
                    log_degrees = np.log10([d for d in degree_values if d > 0])
                    degree_counts = np.array([degree_distribution[d] for d in degree_values if d > 0])
                    log_counts = np.log10(degree_counts)

                    if len(log_degrees) > 1:
                        slope, intercept, r_value, p_value, std_err = linregress(log_degrees, log_counts)
                        power_law_exponent = -slope
                        power_law_fit_quality = r_value ** 2
                except:
                    pass

            # 同配性分析
            try:
                degree_assortativity = nx.degree_assortativity_coefficient(simple_graph)
            except:
                degree_assortativity = 0.0

            # 属性同配性
            attribute_assortativity = {}
            try:
                # 按实体类型计算同配性
                entity_types = nx.get_node_attributes(graph, 'entity_type')
                if entity_types:
                    attribute_assortativity['entity_type'] = nx.attribute_assortativity_coefficient(
                        simple_graph, 'entity_type'
                    )
            except:
                pass

            # 小世界性质分析
            small_world_sigma = None
            small_world_omega = None
            try:
                if is_connected and num_nodes >= 10:
                    # 计算小世界指标
                    random_graph = nx.erdos_renyi_graph(num_nodes, density)
                    random_clustering = nx.average_clustering(random_graph)
                    random_path_length = nx.average_shortest_path_length(random_graph) if nx.is_connected(random_graph) else avg_path_length

                    if random_clustering > 0 and random_path_length > 0:
                        clustering_ratio = global_clustering / random_clustering
                        path_length_ratio = avg_path_length / random_path_length
                        small_world_sigma = clustering_ratio / path_length_ratio

                        # Omega指标
                        lattice_graph = nx.watts_strogatz_graph(num_nodes, int(avg_degree), 0)
                        lattice_clustering = nx.average_clustering(lattice_graph)
                        lattice_path_length = nx.average_shortest_path_length(lattice_graph)

                        if lattice_clustering > 0 and random_path_length > 0:
                            small_world_omega = (avg_path_length / random_path_length) - (global_clustering / lattice_clustering)
            except:
                pass

            # 构建结果对象
            metrics = NetworkTopologyMetrics(
                num_nodes=num_nodes,
                num_edges=num_edges,
                density=density,
                avg_degree=avg_degree,
                degree_variance=degree_variance,
                is_connected=is_connected,
                num_components=num_components,
                largest_component_size=largest_component_size,
                component_sizes=component_sizes,
                avg_path_length=avg_path_length,
                diameter=diameter,
                radius=radius,
                eccentricity_stats=eccentricity_stats,
                global_clustering=global_clustering,
                local_clustering_avg=local_clustering_avg,
                transitivity=transitivity,
                degree_distribution=degree_distribution,
                power_law_exponent=power_law_exponent,
                power_law_fit_quality=power_law_fit_quality,
                degree_assortativity=degree_assortativity,
                attribute_assortativity=attribute_assortativity,
                small_world_sigma=small_world_sigma,
                small_world_omega=small_world_omega
            )

            # 缓存结果
            if self._cache:
                self._cache[cache_key] = metrics

            self.topology_metrics = metrics
            logger.info("网络拓扑分析完成")
            return metrics

        except Exception as e:
            logger.error(f"网络拓扑分析失败: {e}")
            raise

    def model_conflict_propagation(self, graph: nx.Graph = None,
                                   initial_conflicts: Dict[str, float] = None) -> ConflictPropagationModel:
        """
        构建冲突传播动力学模型

        Args:
            graph: 要分析的网络图，默认为主网络
            initial_conflicts: 初始冲突状态字典

        Returns:
            ConflictPropagationModel: 冲突传播模型结果
        """
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        logger.info("构建冲突传播动力学模型...")

        try:
            nodes = list(graph.nodes())
            n_nodes = len(nodes)

            # 传播参数估计
            if self.intensity_model:
                avg_intensity = self.intensity_model.intensity_distribution['mean']
                transmission_rate = min(0.8, max(0.1, avg_intensity / 2))
            else:
                transmission_rate = 0.3

            recovery_rate = 0.1  # 恢复率
            spontaneous_rate = 0.05  # 自发冲突率

            # 构建影响矩阵
            influence_matrix = np.zeros((n_nodes, n_nodes))
            node_to_idx = {node: idx for idx, node in enumerate(nodes)}

            for u, v, data in graph.edges(data=True):
                u_idx = node_to_idx[u]
                v_idx = node_to_idx[v]

                # 影响强度基于边权重和距离
                strength = data.get('strength', 1.0)
                friction = data.get('friction_heat', 0.5)
                influence = strength * friction * transmission_rate

                influence_matrix[u_idx, v_idx] = influence
                influence_matrix[v_idx, u_idx] = influence * 0.8  # 反向影响稍弱

            # 传播路径分析
            propagation_paths = {}
            for source in nodes[:min(20, len(nodes))]:  # 限制计算量
                paths = {}
                try:
                    # 计算从源节点到其他节点的最短路径
                    shortest_paths = nx.single_source_shortest_path(graph, source, cutoff=3)
                    for target, path in shortest_paths.items():
                        if len(path) > 1:  # 排除自身
                            paths[target] = path
                except:
                    pass
                propagation_paths[source] = paths

            # 级联分析 - 简化的级联模型
            cascade_sizes = []
            for _ in range(100):  # Monte Carlo 模拟
                # 随机选择初始节点
                initial_node = np.random.choice(nodes)
                cascade_size = self._simulate_cascade(graph, initial_node, transmission_rate)
                cascade_sizes.append(cascade_size)

            cascade_size_distribution = dict(Counter(cascade_sizes))

            # 临界级联阈值
            cascade_threshold_candidates = np.linspace(0.1, 0.9, 9)
            critical_cascade_threshold = 0.5  # 默认值

            for threshold in cascade_threshold_candidates:
                large_cascades = sum(1 for size in cascade_sizes if size > len(nodes) * threshold)
                if large_cascades / len(cascade_sizes) < 0.05:  # 5%的大级联
                    critical_cascade_threshold = threshold
                    break

            # 时间序列预测 - 简化的SIR模型
            propagation_timeline = {}
            peak_conflict_times = {}

            if initial_conflicts is None:
                # 随机初始化冲突状态
                initial_conflicts = {node: np.random.random() * 0.1 for node in nodes[:5]}

            for source_node, initial_intensity in initial_conflicts.items():
                timeline, peak_time = self._simulate_sir_propagation(
                    graph, source_node, initial_intensity,
                    transmission_rate, recovery_rate, spontaneous_rate
                )
                propagation_timeline[source_node] = timeline
                peak_conflict_times[source_node] = peak_time

            # 构建结果对象
            propagation_model = ConflictPropagationModel(
                transmission_rate=transmission_rate,
                recovery_rate=recovery_rate,
                spontaneous_rate=spontaneous_rate,
                influence_matrix=influence_matrix,
                propagation_paths=propagation_paths,
                cascade_size_distribution=cascade_size_distribution,
                critical_cascade_threshold=critical_cascade_threshold,
                propagation_timeline=propagation_timeline,
                peak_conflict_times=peak_conflict_times
            )

            self.propagation_model = propagation_model
            logger.info(f"冲突传播模型构建完成，传播率: {transmission_rate:.3f}")
            return propagation_model

        except Exception as e:
            logger.error(f"冲突传播模型构建失败: {e}")
            raise

    def _simulate_cascade(self, graph: nx.Graph, initial_node: str, transmission_rate: float) -> int:
        """简单的级联模拟"""
        infected = {initial_node}
        queue = [initial_node]

        while queue:
            current = queue.pop(0)
            for neighbor in graph.neighbors(current):
                if neighbor not in infected and np.random.random() < transmission_rate:
                    infected.add(neighbor)
                    queue.append(neighbor)

        return len(infected)

    def _simulate_sir_propagation(self, graph: nx.Graph, source_node: str,
                                  initial_intensity: float, transmission_rate: float,
                                  recovery_rate: float, spontaneous_rate: float) -> Tuple[List[float], float]:
        """SIR模型传播模拟"""
        nodes = list(graph.nodes())
        n_nodes = len(nodes)

        # 初始状态
        susceptible = np.ones(n_nodes)
        infected = np.zeros(n_nodes)
        recovered = np.zeros(n_nodes)

        source_idx = nodes.index(source_node) if source_node in nodes else 0
        infected[source_idx] = initial_intensity
        susceptible[source_idx] = 1 - initial_intensity

        timeline = []
        time_steps = 50

        for t in range(time_steps):
            # 记录当前状态
            total_infected = np.sum(infected)
            timeline.append(total_infected)

            # 更新状态
            new_infected = np.zeros(n_nodes)
            new_recovered = np.zeros(n_nodes)

            for i, node in enumerate(nodes):
                # 传播
                if infected[i] > 0:
                    for neighbor in graph.neighbors(node):
                        j = nodes.index(neighbor)
                        if susceptible[j] > 0:
                            transmission_prob = transmission_rate * infected[i] * susceptible[j]
                            transmission = min(transmission_prob, susceptible[j])
                            new_infected[j] += transmission

                # 恢复
                recovery = recovery_rate * infected[i]
                new_recovered[i] = recovery

                # 自发冲突
                spontaneous = spontaneous_rate * susceptible[i]
                new_infected[i] += spontaneous

            # 应用变化
            infected += new_infected - new_recovered
            susceptible -= new_infected + new_recovered * 0.5  # 部分恢复为易感
            recovered += new_recovered

            # 边界处理
            infected = np.clip(infected, 0, 1)
            susceptible = np.clip(susceptible, 0, 1)
            recovered = np.clip(recovered, 0, 1)

        # 找到峰值时间
        peak_time = float(np.argmax(timeline))

        return timeline, peak_time

    def analyze_network_robustness(self, graph: nx.Graph = None) -> NetworkRobustness:
        """
        网络稳定性和韧性分析

        Args:
            graph: 要分析的网络图，默认为主网络

        Returns:
            NetworkRobustness: 网络鲁棒性分析结果
        """
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        logger.info("开始网络鲁棒性分析...")

        try:
            # 转换为无向图
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph
            original_nodes = list(undirected_graph.nodes())
            n_nodes = len(original_nodes)

            # 随机攻击测试
            random_attack_results = self._simulate_random_attack(undirected_graph)

            # 目标攻击测试
            targeted_attack_results = self._simulate_targeted_attack(undirected_graph)

            # 脆弱性评分
            vulnerability_scores = {}
            if self.centrality_analysis:
                # 基于多种中心性的加权脆弱性评分
                for node in original_nodes:
                    score = 0
                    score += self.centrality_analysis.betweenness_centrality.get(node, 0) * 0.3
                    score += self.centrality_analysis.degree_centrality.get(node, 0) * 0.3
                    score += self.centrality_analysis.pagerank.get(node, 0) * 0.2
                    score += self.centrality_analysis.closeness_centrality.get(node, 0) * 0.2
                    vulnerability_scores[node] = score
            else:
                # 简单的度中心性评分
                degree_centrality = nx.degree_centrality(undirected_graph)
                vulnerability_scores = degree_centrality

            # 关键失效节点
            sorted_vulnerability = sorted(vulnerability_scores.items(), key=lambda x: x[1], reverse=True)
            critical_failure_nodes = [node for node, score in sorted_vulnerability[:10]]

            # 恢复时间估计
            recovery_times = {}
            for node in critical_failure_nodes:
                # 基于节点重要性估计恢复时间
                importance = vulnerability_scores[node]
                recovery_times[node] = importance * 10 + np.random.exponential(2)

            # 韧性指标
            resilience_metrics = {}

            # 连通韧性
            original_components = nx.number_connected_components(undirected_graph)
            resilience_metrics['connectivity_resilience'] = 1.0 / (original_components + 1)

            # 效率韧性
            try:
                original_efficiency = nx.global_efficiency(undirected_graph)
                resilience_metrics['efficiency_resilience'] = original_efficiency
            except:
                resilience_metrics['efficiency_resilience'] = 0.5

            # 结构韧性
            original_density = nx.density(undirected_graph)
            resilience_metrics['structural_resilience'] = original_density

            # 系统性风险评分
            systemic_risk_score = 0.0

            # 基于关键节点集中度
            top_10_vulnerability = sum(score for _, score in sorted_vulnerability[:10])
            total_vulnerability = sum(vulnerability_scores.values())
            if total_vulnerability > 0:
                concentration_risk = top_10_vulnerability / total_vulnerability
                systemic_risk_score += concentration_risk * 0.4

            # 基于网络密度
            if original_density < 0.1:
                systemic_risk_score += 0.3

            # 基于连通性
            if original_components > 1:
                systemic_risk_score += 0.3

            systemic_risk_score = min(1.0, systemic_risk_score)

            # 失效概率
            failure_probability = {}
            for node in original_nodes:
                # 基于脆弱性和外部因素的失效概率
                base_probability = vulnerability_scores[node] * 0.1

                # 考虑冲突强度
                if self.intensity_model and node in self.intensity_model.node_intensities:
                    conflict_factor = self.intensity_model.node_intensities[node] * 0.05
                    base_probability += conflict_factor

                failure_probability[node] = min(0.9, base_probability)

            # 构建结果对象
            robustness_analysis = NetworkRobustness(
                random_attack_threshold=random_attack_results['threshold'],
                targeted_attack_threshold=targeted_attack_results['threshold'],
                vulnerability_scores=vulnerability_scores,
                critical_failure_nodes=critical_failure_nodes,
                recovery_times=recovery_times,
                resilience_metrics=resilience_metrics,
                systemic_risk_score=systemic_risk_score,
                failure_probability=failure_probability
            )

            self.robustness_analysis = robustness_analysis
            logger.info(f"网络鲁棒性分析完成，系统性风险评分: {systemic_risk_score:.3f}")
            return robustness_analysis

        except Exception as e:
            logger.error(f"网络鲁棒性分析失败: {e}")
            raise

    def _simulate_random_attack(self, graph: nx.Graph) -> Dict[str, Any]:
        """模拟随机攻击"""
        nodes = list(graph.nodes())
        original_size = len(nodes)

        for removed_fraction in np.linspace(0, 0.9, 19):
            nodes_to_remove = int(removed_fraction * original_size)
            if nodes_to_remove == 0:
                continue

            # 随机移除节点
            removed_nodes = np.random.choice(nodes, size=nodes_to_remove, replace=False)
            remaining_graph = graph.copy()
            remaining_graph.remove_nodes_from(removed_nodes)

            # 检查连通性
            if nx.number_connected_components(remaining_graph) > 1:
                return {'threshold': removed_fraction, 'nodes_removed': nodes_to_remove}

        return {'threshold': 0.9, 'nodes_removed': int(0.9 * original_size)}

    def _simulate_targeted_attack(self, graph: nx.Graph) -> Dict[str, Any]:
        """模拟目标攻击"""
        # 按度中心性排序节点
        degree_centrality = nx.degree_centrality(graph)
        sorted_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)

        original_size = len(sorted_nodes)

        for i, (node, _) in enumerate(sorted_nodes):
            removed_fraction = (i + 1) / original_size

            # 移除高中心性节点
            remaining_graph = graph.copy()
            nodes_to_remove = [n for n, _ in sorted_nodes[:i+1]]
            remaining_graph.remove_nodes_from(nodes_to_remove)

            # 检查连通性
            if remaining_graph.number_of_nodes() == 0 or nx.number_connected_components(remaining_graph) > 1:
                return {'threshold': removed_fraction, 'nodes_removed': i + 1}

        return {'threshold': 1.0, 'nodes_removed': original_size}

    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        运行完整的综合分析

        Returns:
            Dict[str, Any]: 所有分析结果的汇总
        """
        logger.info("开始综合网络分析...")

        results = {}

        try:
            # 1. 构建网络
            if self.main_network is None:
                self.build_main_network()
            results['network_built'] = True

            # 2. 拓扑分析
            topology_metrics = self.analyze_network_topology()
            results['topology_metrics'] = asdict(topology_metrics)

            # 3. 强度建模
            intensity_model = self.build_conflict_intensity_model()
            results['intensity_model'] = {
                'average_intensity': intensity_model.intensity_distribution['mean'],
                'intensity_range': (intensity_model.intensity_distribution['min'],
                                   intensity_model.intensity_distribution['max']),
                'escalation_threshold': intensity_model.escalation_threshold,
                'prediction_accuracy': intensity_model.prediction_accuracy
            }

            # 4. 社团发现
            community_structure = self.discover_communities()
            results['community_structure'] = {
                'num_communities': community_structure.num_communities,
                'modularity': community_structure.louvain_modularity,
                'community_sizes': community_structure.community_sizes,
                'cross_domain_ratio': community_structure.cross_domain_edges /
                                     (community_structure.cross_domain_edges + community_structure.intra_domain_edges)
            }

            # 5. 中心性分析
            centrality_analysis = self.analyze_centrality()
            results['centrality_analysis'] = {
                'critical_nodes_count': {k: len(v) for k, v in centrality_analysis.critical_nodes.items()},
                'top_conflict_nodes': centrality_analysis.centrality_rankings.get('conflict', [])[:5]
            }

            # 6. 传播模型
            propagation_model = self.model_conflict_propagation()
            results['propagation_model'] = {
                'transmission_rate': propagation_model.transmission_rate,
                'critical_cascade_threshold': propagation_model.critical_cascade_threshold,
                'average_cascade_size': np.mean(list(propagation_model.cascade_size_distribution.keys()))
            }

            # 7. 鲁棒性分析
            robustness_analysis = self.analyze_network_robustness()
            results['robustness_analysis'] = {
                'random_attack_threshold': robustness_analysis.random_attack_threshold,
                'targeted_attack_threshold': robustness_analysis.targeted_attack_threshold,
                'systemic_risk_score': robustness_analysis.systemic_risk_score,
                'critical_failure_nodes_count': len(robustness_analysis.critical_failure_nodes)
            }

            # 8. 生成综合报告
            results['summary'] = self._generate_analysis_summary(results)

            logger.info("综合网络分析完成")
            return results

        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            raise

    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {}

        # 网络规模
        topology = results.get('topology_metrics', {})
        summary['network_scale'] = {
            'nodes': topology.get('num_nodes', 0),
            'edges': topology.get('num_edges', 0),
            'density': topology.get('density', 0)
        }

        # 网络特征
        summary['network_characteristics'] = {
            'small_world': topology.get('small_world_sigma', 0) > 1,
            'scale_free': topology.get('power_law_fit_quality', 0) > 0.8,
            'highly_clustered': topology.get('global_clustering', 0) > 0.3
        }

        # 冲突特征
        intensity = results.get('intensity_model', {})
        summary['conflict_characteristics'] = {
            'average_intensity': intensity.get('average_intensity', 0),
            'high_escalation_risk': intensity.get('escalation_threshold', 0) <
                                   intensity.get('average_intensity', 0) * 2
        }

        # 稳定性评估
        robustness = results.get('robustness_analysis', {})
        summary['stability_assessment'] = {
            'overall_stability': 'high' if robustness.get('systemic_risk_score', 1) < 0.3 else
                               'medium' if robustness.get('systemic_risk_score', 1) < 0.7 else 'low',
            'attack_resistance': 'high' if robustness.get('targeted_attack_threshold', 0) > 0.5 else 'low'
        }

        # 关键发现
        summary['key_findings'] = []

        if topology.get('num_components', 1) > 1:
            summary['key_findings'].append("网络存在多个独立组件")

        if results.get('community_structure', {}).get('cross_domain_ratio', 0) > 0.3:
            summary['key_findings'].append("存在大量跨域冲突连接")

        if robustness.get('systemic_risk_score', 0) > 0.7:
            summary['key_findings'].append("网络面临高系统性风险")

        return summary

if __name__ == "__main__":
    # 测试代码
    try:
        # 初始化模型
        model = ComprehensiveConflictNetworkModel()

        # 加载数据
        data_path = "D:/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
        model.load_data(data_path)

        # 运行完整分析
        print("=== 开始综合网络分析 ===")
        results = model.run_comprehensive_analysis()

        # 输出分析结果
        print("\n=== 分析结果汇总 ===")
        summary = results['summary']

        print(f"网络规模: {summary['network_scale']['nodes']} 节点, {summary['network_scale']['edges']} 边")
        print(f"网络密度: {summary['network_scale']['density']:.4f}")

        print(f"\n网络特征:")
        for feature, value in summary['network_characteristics'].items():
            print(f"  {feature}: {value}")

        print(f"\n冲突特征:")
        print(f"  平均强度: {summary['conflict_characteristics']['average_intensity']:.3f}")
        print(f"  高升级风险: {summary['conflict_characteristics']['high_escalation_risk']}")

        print(f"\n稳定性评估:")
        print(f"  整体稳定性: {summary['stability_assessment']['overall_stability']}")
        print(f"  攻击抵抗力: {summary['stability_assessment']['attack_resistance']}")

        if summary['key_findings']:
            print(f"\n关键发现:")
            for finding in summary['key_findings']:
                print(f"  - {finding}")

        # 详细指标
        print(f"\n=== 详细网络指标 ===")
        topology = results['topology_metrics']
        print(f"平均路径长度: {topology['avg_path_length']:.4f}")
        print(f"聚类系数: {topology['global_clustering']:.4f}")
        print(f"连通分量数: {topology['num_components']}")

        if topology.get('power_law_exponent'):
            print(f"幂律指数: {topology['power_law_exponent']:.3f}")

        if topology.get('small_world_sigma'):
            print(f"小世界指数: {topology['small_world_sigma']:.3f}")

        community = results['community_structure']
        print(f"\n=== 社团结构 ===")
        print(f"社团数量: {community['num_communities']}")
        print(f"模块度: {community['modularity']:.3f}")
        print(f"跨域连接比例: {community['cross_domain_ratio']:.3f}")

        intensity = results['intensity_model']
        print(f"\n=== 冲突强度模型 ===")
        print(f"平均强度: {intensity['average_intensity']:.3f}")
        print(f"强度范围: {intensity['intensity_range'][0]:.3f} - {intensity['intensity_range'][1]:.3f}")
        print(f"升级阈值: {intensity['escalation_threshold']:.3f}")
        print(f"预测准确度: {intensity['prediction_accuracy']:.3f}")

        propagation = results['propagation_model']
        print(f"\n=== 传播动力学 ===")
        print(f"传播率: {propagation['transmission_rate']:.3f}")
        print(f"临界级联阈值: {propagation['critical_cascade_threshold']:.3f}")
        print(f"平均级联大小: {propagation['average_cascade_size']:.1f}")

        robustness = results['robustness_analysis']
        print(f"\n=== 鲁棒性分析 ===")
        print(f"随机攻击阈值: {robustness['random_attack_threshold']:.3f}")
        print(f"目标攻击阈值: {robustness['targeted_attack_threshold']:.3f}")
        print(f"系统性风险评分: {robustness['systemic_risk_score']:.3f}")
        print(f"关键失效节点数: {robustness['critical_failure_nodes_count']}")

        print("\n=== 综合网络模型分析完成！ ===")

    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()