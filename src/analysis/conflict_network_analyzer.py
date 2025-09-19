"""
跨域冲突网络分析器
实现复杂网络分析、多层网络建模、中心性分析、社群发现等功能
"""

import json
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging
from pathlib import Path

# 网络分析相关库
try:
    import community as community_louvain  # python-louvain
except ImportError:
    community_louvain = None

try:
    import igraph as ig
except ImportError:
    ig = None

# 科学计算库
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

# 可视化库
import matplotlib.pyplot as plt
import seaborn as sns
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
except ImportError:
    go = px = make_subplots = pyo = None

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NetworkMetrics:
    """网络基础指标"""
    num_nodes: int
    num_edges: int
    density: float
    avg_path_length: float
    clustering_coefficient: float
    transitivity: float
    diameter: int
    radius: int
    is_connected: bool
    num_components: int
    assortativity: float

@dataclass
class CentralityMetrics:
    """中心性指标"""
    degree_centrality: Dict[str, float]
    betweenness_centrality: Dict[str, float]
    closeness_centrality: Dict[str, float]
    eigenvector_centrality: Dict[str, float]
    pagerank: Dict[str, float]

@dataclass
class CommunityStructure:
    """社群结构"""
    communities: Dict[int, List[str]]
    modularity: float
    num_communities: int
    community_sizes: List[int]
    cross_domain_edges: int
    intra_domain_edges: int

class ConflictNetworkAnalyzer:
    """跨域冲突网络分析器主类"""

    def __init__(self, data_path: str = None):
        """
        初始化网络分析器

        Args:
            data_path: 数据文件路径
        """
        self.data_path = data_path
        self.entities_df = None
        self.relations_df = None
        self.conflict_data = None

        # 网络对象
        self.main_network = None
        self.domain_networks = {}
        self.type_networks = {}
        self.relation_networks = {}

        # 分析结果
        self.network_metrics = None
        self.centrality_metrics = None
        self.community_structure = None

        # 可视化设置
        self.colors = {
            '人域域': '#FF6B6B',
            '天域域': '#4ECDC4',
            '灵域域': '#45B7D1',
            '荒域域': '#96CEB4',
            '核心资源': '#FFD93D',
            '法条制度': '#6BCF7F',
            '关键角色': '#DDA0DD',
            '推断实体': '#F4A261'
        }

    def load_data(self, entities_path: str = None, relations_path: str = None, json_path: str = None):
        """
        加载数据

        Args:
            entities_path: 实体CSV文件路径
            relations_path: 关系CSV文件路径
            json_path: JSON数据文件路径
        """
        try:
            if json_path:
                logger.info(f"从JSON文件加载数据: {json_path}")
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.conflict_data = json.load(f)

                # 转换为DataFrame
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
                        '提取方法': entity.get('extraction_method', 'auto')
                    })
                self.entities_df = pd.DataFrame(entities_data)

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
                        '置信度': relation.get('confidence', 0.8)
                    })
                self.relations_df = pd.DataFrame(relations_data)

            else:
                # 从CSV文件加载
                if entities_path:
                    logger.info(f"加载实体数据: {entities_path}")
                    self.entities_df = pd.read_csv(entities_path)

                if relations_path:
                    logger.info(f"加载关系数据: {relations_path}")
                    self.relations_df = pd.read_csv(relations_path)

            # 数据预处理
            self._preprocess_data()
            logger.info(f"数据加载完成: {len(self.entities_df)} 个实体, {len(self.relations_df)} 个关系")

        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            raise

    def _preprocess_data(self):
        """数据预处理"""
        if self.entities_df is not None:
            # 处理域归属字段
            self.entities_df['域列表'] = self.entities_df['域归属'].apply(
                lambda x: [d.strip() for d in str(x).split(';')] if pd.notna(x) else []
            )

            # 重要性权重映射
            importance_weights = {'高': 3, '中高': 2, '中': 1, '低': 0.5}
            self.entities_df['重要性权重'] = self.entities_df['重要性'].map(importance_weights).fillna(1)

        if self.relations_df is not None:
            # 确保关系强度为数值类型
            self.relations_df['强度'] = pd.to_numeric(self.relations_df['强度'], errors='coerce').fillna(1.0)

    def build_main_network(self) -> nx.Graph:
        """构建主网络图"""
        try:
            logger.info("构建主网络图...")

            # 创建有向图
            G = nx.DiGraph()

            # 添加节点
            for _, entity in self.entities_df.iterrows():
                domains = entity.get('域列表', [])
                G.add_node(
                    entity['ID'],
                    name=entity['名称'],
                    entity_type=entity['实体类型'],
                    domains=domains,
                    importance=entity['重要性'],
                    importance_weight=entity.get('重要性权重', 1),
                    description=entity.get('描述', ''),
                    confidence=entity.get('置信度', 0.8)
                )

            # 添加边
            for _, relation in self.relations_df.iterrows():
                source = relation['源实体ID']
                target = relation['目标实体ID']

                if source in G.nodes and target in G.nodes:
                    G.add_edge(
                        source,
                        target,
                        relation_type=relation['关系类型'],
                        strength=relation['强度'],
                        cross_domain=relation.get('跨域', False),
                        description=relation.get('描述', ''),
                        confidence=relation.get('置信度', 0.8)
                    )

            self.main_network = G
            logger.info(f"主网络构建完成: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
            return G

        except Exception as e:
            logger.error(f"主网络构建失败: {e}")
            raise

    def build_domain_networks(self) -> Dict[str, nx.Graph]:
        """构建按域分层的网络"""
        if self.main_network is None:
            self.build_main_network()

        logger.info("构建域分层网络...")
        domain_networks = {}

        # 获取所有域
        all_domains = set()
        for node, data in self.main_network.nodes(data=True):
            all_domains.update(data.get('domains', []))

        # 为每个域构建子网络
        for domain in all_domains:
            if not domain:
                continue

            # 筛选属于该域的节点
            domain_nodes = []
            for node, data in self.main_network.nodes(data=True):
                if domain in data.get('domains', []):
                    domain_nodes.append(node)

            # 创建子图
            domain_subgraph = self.main_network.subgraph(domain_nodes).copy()
            domain_networks[domain] = domain_subgraph

            logger.info(f"域 {domain}: {domain_subgraph.number_of_nodes()} 节点, {domain_subgraph.number_of_edges()} 边")

        self.domain_networks = domain_networks
        return domain_networks

    def build_type_networks(self) -> Dict[str, nx.Graph]:
        """构建按实体类型分层的网络"""
        if self.main_network is None:
            self.build_main_network()

        logger.info("构建类型分层网络...")
        type_networks = {}

        # 获取所有实体类型
        entity_types = set()
        for node, data in self.main_network.nodes(data=True):
            entity_types.add(data.get('entity_type', ''))

        # 为每种类型构建子网络
        for entity_type in entity_types:
            if not entity_type:
                continue

            # 筛选该类型的节点
            type_nodes = []
            for node, data in self.main_network.nodes(data=True):
                if data.get('entity_type') == entity_type:
                    type_nodes.append(node)

            # 创建子图
            type_subgraph = self.main_network.subgraph(type_nodes).copy()
            type_networks[entity_type] = type_subgraph

            logger.info(f"类型 {entity_type}: {type_subgraph.number_of_nodes()} 节点, {type_subgraph.number_of_edges()} 边")

        self.type_networks = type_networks
        return type_networks

    def build_relation_networks(self) -> Dict[str, nx.Graph]:
        """构建按关系类型分层的网络"""
        if self.main_network is None:
            self.build_main_network()

        logger.info("构建关系分层网络...")
        relation_networks = {}

        # 获取所有关系类型
        relation_types = set()
        for _, _, data in self.main_network.edges(data=True):
            relation_types.add(data.get('relation_type', ''))

        # 为每种关系类型构建网络
        for relation_type in relation_types:
            if not relation_type:
                continue

            # 创建只包含该关系类型的网络
            G = nx.DiGraph()

            # 添加所有节点
            G.add_nodes_from(self.main_network.nodes(data=True))

            # 只添加指定类型的边
            for source, target, data in self.main_network.edges(data=True):
                if data.get('relation_type') == relation_type:
                    G.add_edge(source, target, **data)

            relation_networks[relation_type] = G
            logger.info(f"关系 {relation_type}: {G.number_of_edges()} 边")

        self.relation_networks = relation_networks
        return relation_networks

    def calculate_network_metrics(self, graph: nx.Graph = None) -> NetworkMetrics:
        """计算网络基础指标"""
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        logger.info("计算网络基础指标...")

        # 转换为无向图进行某些计算
        undirected_graph = graph.to_undirected() if graph.is_directed() else graph

        try:
            # 基础指标
            num_nodes = graph.number_of_nodes()
            num_edges = graph.number_of_edges()
            density = nx.density(graph)

            # 连通性
            if graph.is_directed():
                is_connected = nx.is_weakly_connected(graph)
                num_components = nx.number_weakly_connected_components(graph)
            else:
                is_connected = nx.is_connected(graph)
                num_components = nx.number_connected_components(graph)

            # 路径长度指标
            if is_connected:
                avg_path_length = nx.average_shortest_path_length(undirected_graph)
                diameter = nx.diameter(undirected_graph)
                radius = nx.radius(undirected_graph)
            else:
                # 对于不连通的图，计算最大连通分量的指标
                largest_cc = max(nx.connected_components(undirected_graph), key=len)
                largest_subgraph = undirected_graph.subgraph(largest_cc)
                avg_path_length = nx.average_shortest_path_length(largest_subgraph)
                diameter = nx.diameter(largest_subgraph)
                radius = nx.radius(largest_subgraph)

            # 聚类系数
            clustering_coefficient = nx.average_clustering(undirected_graph)
            transitivity = nx.transitivity(undirected_graph)

            # 同配性
            try:
                # 按度同配性
                assortativity = nx.degree_assortativity_coefficient(undirected_graph)
            except:
                assortativity = 0.0

            metrics = NetworkMetrics(
                num_nodes=num_nodes,
                num_edges=num_edges,
                density=density,
                avg_path_length=avg_path_length,
                clustering_coefficient=clustering_coefficient,
                transitivity=transitivity,
                diameter=diameter,
                radius=radius,
                is_connected=is_connected,
                num_components=num_components,
                assortativity=assortativity
            )

            self.network_metrics = metrics
            logger.info("网络基础指标计算完成")
            return metrics

        except Exception as e:
            logger.error(f"网络指标计算失败: {e}")
            raise

    def calculate_centrality_metrics(self, graph: nx.Graph = None) -> CentralityMetrics:
        """计算中心性指标"""
        if graph is None:
            graph = self.main_network

        if graph is None:
            raise ValueError("网络图未构建")

        logger.info("计算中心性指标...")

        try:
            # 度中心性
            degree_centrality = nx.degree_centrality(graph)

            # 介数中心性
            betweenness_centrality = nx.betweenness_centrality(graph)

            # 接近中心性
            closeness_centrality = nx.closeness_centrality(graph)

            # 特征向量中心性
            try:
                eigenvector_centrality = nx.eigenvector_centrality(graph, max_iter=1000)
            except:
                # 如果计算失败，使用度中心性代替
                eigenvector_centrality = degree_centrality
                logger.warning("特征向量中心性计算失败，使用度中心性代替")

            # PageRank
            pagerank = nx.pagerank(graph)

            metrics = CentralityMetrics(
                degree_centrality=degree_centrality,
                betweenness_centrality=betweenness_centrality,
                closeness_centrality=closeness_centrality,
                eigenvector_centrality=eigenvector_centrality,
                pagerank=pagerank
            )

            self.centrality_metrics = metrics
            logger.info("中心性指标计算完成")
            return metrics

        except Exception as e:
            logger.error(f"中心性指标计算失败: {e}")
            raise

if __name__ == "__main__":
    # 测试代码
    analyzer = ConflictNetworkAnalyzer()

    # 加载数据
    json_path = "/d/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
    analyzer.load_data(json_path=json_path)

    # 构建网络
    main_net = analyzer.build_main_network()
    domain_nets = analyzer.build_domain_networks()
    type_nets = analyzer.build_type_networks()
    relation_nets = analyzer.build_relation_networks()

    # 计算指标
    network_metrics = analyzer.calculate_network_metrics()
    centrality_metrics = analyzer.calculate_centrality_metrics()

    print("网络分析完成！")
    print(f"网络密度: {network_metrics.density:.4f}")
    print(f"平均路径长度: {network_metrics.avg_path_length:.4f}")
    print(f"聚类系数: {network_metrics.clustering_coefficient:.4f}")