"""
高级跨域冲突网络分析器
扩展基础分析器，添加社群发现、路径分析、动态建模等高级功能
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
import itertools
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 网络分析相关库
try:
    import community as community_louvain  # python-louvain
except ImportError:
    community_louvain = None

try:
    import igraph as ig
except ImportError:
    ig = None

# 可视化库
import matplotlib.pyplot as plt
import seaborn as sns
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    import plotly.io as pio
except ImportError:
    go = px = make_subplots = pyo = pio = None

# 从基础分析器导入
from conflict_network_analyzer import ConflictNetworkAnalyzer, NetworkMetrics, CentralityMetrics

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CommunityStructure:
    """社群结构"""
    communities: Dict[int, List[str]]
    modularity: float
    num_communities: int
    community_sizes: List[int]
    cross_domain_edges: int
    intra_domain_edges: int
    community_centralities: Dict[int, Dict[str, float]]

@dataclass
class ConflictPath:
    """冲突路径"""
    source: str
    target: str
    path: List[str]
    length: int
    strength: float
    conflict_types: List[str]
    domains_involved: List[str]
    escalation_potential: float

@dataclass
class NetworkRobustness:
    """网络鲁棒性"""
    random_attack_results: Dict[str, Any]
    targeted_attack_results: Dict[str, Any]
    critical_nodes: List[str]
    vulnerability_score: float

class AdvancedNetworkAnalyzer(ConflictNetworkAnalyzer):
    """高级网络分析器"""

    def __init__(self, data_path: str = None):
        """初始化高级分析器"""
        super().__init__(data_path)

        # 扩展的分析结果
        self.community_structure = None
        self.critical_paths = []
        self.network_robustness = None
        self.escalation_model = None

        # 高级配置
        self.conflict_weights = {
            '对立': 1.0,
            '竞争': 0.8,
            '制约': 0.6,
            '依赖': 0.4
        }

    def detect_communities_advanced(self, graph: nx.Graph = None, methods: List[str] = None) -> Dict[str, CommunityStructure]:
        """高级社群检测，使用多种算法对比"""
        if graph is None:
            graph = self.main_network

        if methods is None:
            methods = ['louvain', 'greedy', 'label_propagation', 'spectral']

        logger.info("执行高级社群检测...")

        # 转换为无向图
        undirected_graph = graph.to_undirected() if graph.is_directed() else graph

        results = {}

        for method in methods:
            try:
                logger.info(f"使用 {method} 算法...")

                if method == 'louvain' and community_louvain:
                    partition = community_louvain.best_partition(undirected_graph)
                    modularity = community_louvain.modularity(partition, undirected_graph)

                elif method == 'greedy':
                    communities = nx.community.greedy_modularity_communities(undirected_graph)
                    partition = {}\n                    for i, community in enumerate(communities):\n                        for node in community:\n                            partition[node] = i\n                    modularity = nx.community.modularity(undirected_graph, communities)

                elif method == 'label_propagation':
                    communities = nx.community.label_propagation_communities(undirected_graph)
                    partition = {}
                    for i, community in enumerate(communities):
                        for node in community:
                            partition[node] = i
                    modularity = nx.community.modularity(undirected_graph, communities)

                elif method == 'spectral':
                    # 使用k-means聚类进行光谱聚类
                    try:
                        eigenvalues, eigenvectors = nx.linalg.laplacianmatrix.laplacian_spectrum(undirected_graph)
                        # 选择最优的k值（基于特征值间隙）
                        k = self._estimate_optimal_k(eigenvalues)

                        # 获取邻接矩阵
                        adj_matrix = nx.adjacency_matrix(undirected_graph).toarray()

                        # 光谱聚类
                        spectral = SpectralClustering(n_clusters=k, random_state=42)
                        node_list = list(undirected_graph.nodes())
                        labels = spectral.fit_predict(adj_matrix)

                        partition = {node_list[i]: labels[i] for i in range(len(node_list))}
                        communities_list = [set(n for n, c in partition.items() if c == i) for i in set(partition.values())]
                        modularity = nx.community.modularity(undirected_graph, communities_list)

                    except Exception as e:
                        logger.warning(f"光谱聚类失败: {e}, 使用标签传播替代")
                        continue

                else:
                    continue

                # 组织社群结构
                communities_dict = defaultdict(list)
                for node, comm_id in partition.items():
                    communities_dict[comm_id].append(node)

                # 计算社群中心性
                community_centralities = self._calculate_community_centralities(graph, communities_dict)

                # 计算跨域边和域内边
                cross_domain_edges, intra_domain_edges = self._count_cross_domain_edges(graph, partition)

                structure = CommunityStructure(
                    communities=dict(communities_dict),
                    modularity=modularity,
                    num_communities=len(communities_dict),
                    community_sizes=[len(comm) for comm in communities_dict.values()],
                    cross_domain_edges=cross_domain_edges,
                    intra_domain_edges=intra_domain_edges,
                    community_centralities=community_centralities
                )

                results[method] = structure
                logger.info(f"{method}: {structure.num_communities}个社群, 模块度: {structure.modularity:.4f}")

            except Exception as e:
                logger.error(f"{method}算法失败: {e}")
                continue

        # 选择最佳结果
        if results:
            best_method = max(results.keys(), key=lambda m: results[m].modularity)
            self.community_structure = results[best_method]
            logger.info(f"最佳社群检测方法: {best_method}")

        return results

    def _estimate_optimal_k(self, eigenvalues: np.ndarray) -> int:
        """估计最优的聚类数k"""
        # 使用特征值间隙来估计
        gaps = np.diff(eigenvalues)
        k = np.argmax(gaps) + 2  # +2因为diff减少了一个元素，且k从2开始
        return min(max(k, 2), 10)  # 限制在2-10之间

    def _calculate_community_centralities(self, graph: nx.Graph, communities: Dict) -> Dict[int, Dict[str, float]]:
        """计算社群中心性"""
        centralities = {}

        for comm_id, nodes in communities.items():
            subgraph = graph.subgraph(nodes)

            # 社群内部密度
            internal_density = nx.density(subgraph)

            # 社群与外部的连接度
            external_edges = 0
            total_possible_external = 0

            for node in nodes:
                for neighbor in graph.neighbors(node):
                    if neighbor not in nodes:
                        external_edges += 1
                total_possible_external += graph.number_of_nodes() - len(nodes)

            external_connectivity = external_edges / max(total_possible_external, 1)

            # 社群大小相对重要性
            size_importance = len(nodes) / graph.number_of_nodes()

            centralities[comm_id] = {
                'internal_density': internal_density,
                'external_connectivity': external_connectivity,
                'size_importance': size_importance,
                'total_centrality': internal_density * size_importance + external_connectivity * 0.5
            }

        return centralities

    def _count_cross_domain_edges(self, graph: nx.Graph, partition: Dict) -> Tuple[int, int]:
        """计算跨域边和域内边"""
        cross_domain = 0
        intra_domain = 0

        for source, target in graph.edges():
            source_comm = partition.get(source, -1)
            target_comm = partition.get(target, -1)

            if source_comm != target_comm:
                cross_domain += 1
            else:
                intra_domain += 1

        return cross_domain, intra_domain

    def identify_critical_paths_advanced(self, graph: nx.Graph = None, top_k: int = 50) -> List[ConflictPath]:
        """高级关键路径识别"""
        if graph is None:
            graph = self.main_network

        logger.info("识别关键冲突传播路径...")

        critical_paths = []

        # 获取所有域
        domains = set()
        node_domains = {}
        for node, data in graph.nodes(data=True):
            node_domains[node] = data.get('domains', [])
            domains.update(data.get('domains', []))

        # 分析跨域路径
        for source_domain, target_domain in itertools.combinations(domains, 2):
            source_nodes = [n for n, doms in node_domains.items() if source_domain in doms]
            target_nodes = [n for n, doms in node_domains.items() if target_domain in doms]

            # 限制节点数量以提高性能
            source_sample = np.random.choice(source_nodes, min(10, len(source_nodes)), replace=False)
            target_sample = np.random.choice(target_nodes, min(10, len(target_nodes)), replace=False)

            for source in source_sample:
                for target in target_sample:
                    try:
                        # 找到所有简单路径（长度限制）
                        paths = list(nx.all_simple_paths(graph, source, target, cutoff=5))

                        for path in paths[:3]:  # 每对节点最多3条路径
                            # 计算路径特征
                            path_strength = self._calculate_path_strength_advanced(graph, path)
                            conflict_types = self._extract_path_conflict_types(graph, path)
                            domains_involved = self._extract_path_domains(graph, path)
                            escalation_potential = self._calculate_escalation_potential(graph, path)

                            conflict_path = ConflictPath(
                                source=source,
                                target=target,
                                path=path,
                                length=len(path) - 1,
                                strength=path_strength,
                                conflict_types=conflict_types,
                                domains_involved=domains_involved,
                                escalation_potential=escalation_potential
                            )

                            critical_paths.append(conflict_path)

                    except nx.NetworkXNoPath:
                        continue
                    except Exception as e:
                        logger.warning(f"路径计算失败 {source}->{target}: {e}")
                        continue

        # 按升级潜力排序
        critical_paths.sort(key=lambda x: x.escalation_potential, reverse=True)

        self.critical_paths = critical_paths[:top_k]
        logger.info(f"识别到 {len(self.critical_paths)} 条关键路径")

        return self.critical_paths

    def _calculate_path_strength_advanced(self, graph: nx.Graph, path: List[str]) -> float:
        """高级路径强度计算"""
        if len(path) < 2:
            return 0.0

        total_strength = 0.0
        conflict_bonus = 0.0

        for i in range(len(path) - 1):
            source, target = path[i], path[i + 1]
            if graph.has_edge(source, target):
                edge_data = graph[source][target]
                base_strength = edge_data.get('strength', 1.0)
                relation_type = edge_data.get('relation_type', '')

                # 根据关系类型调整权重
                type_weight = self.conflict_weights.get(relation_type, 0.5)
                adjusted_strength = base_strength * type_weight

                total_strength += adjusted_strength

                # 冲突关系额外加分
                if relation_type in ['对立', '竞争']:
                    conflict_bonus += 0.2

        # 考虑路径长度和冲突强度
        path_score = (total_strength + conflict_bonus) / len(path)
        return path_score

    def _extract_path_conflict_types(self, graph: nx.Graph, path: List[str]) -> List[str]:
        """提取路径中的冲突类型"""
        conflict_types = []

        for i in range(len(path) - 1):
            source, target = path[i], path[i + 1]
            if graph.has_edge(source, target):
                relation_type = graph[source][target].get('relation_type', '')
                if relation_type and relation_type not in conflict_types:
                    conflict_types.append(relation_type)

        return conflict_types

    def _extract_path_domains(self, graph: nx.Graph, path: List[str]) -> List[str]:
        """提取路径涉及的域"""
        domains = set()

        for node in path:
            if node in graph.nodes:
                node_domains = graph.nodes[node].get('domains', [])
                domains.update(node_domains)

        return list(domains)

    def _calculate_escalation_potential(self, graph: nx.Graph, path: List[str]) -> float:
        """计算冲突升级潜力"""
        if len(path) < 2:
            return 0.0

        escalation_score = 0.0

        # 因素1: 路径中的冲突强度
        conflict_intensity = 0.0
        for i in range(len(path) - 1):
            source, target = path[i], path[i + 1]
            if graph.has_edge(source, target):
                relation_type = graph[source][target].get('relation_type', '')
                if relation_type in ['对立', '竞争']:
                    conflict_intensity += 1.0
                elif relation_type == '制约':
                    conflict_intensity += 0.5

        escalation_score += conflict_intensity / (len(path) - 1)

        # 因素2: 节点重要性
        importance_bonus = 0.0
        for node in path:
            if node in graph.nodes:
                importance = graph.nodes[node].get('importance_weight', 1.0)
                importance_bonus += importance

        escalation_score += importance_bonus / len(path) * 0.5

        # 因素3: 跨域程度
        domains = self._extract_path_domains(graph, path)
        cross_domain_bonus = len(domains) / 4.0  # 假设最多4个域
        escalation_score += cross_domain_bonus * 0.3

        return min(escalation_score, 1.0)  # 限制在0-1之间

    def analyze_network_robustness_advanced(self, graph: nx.Graph = None) -> NetworkRobustness:
        """高级网络鲁棒性分析"""
        if graph is None:
            graph = self.main_network

        logger.info("执行高级网络鲁棒性分析...")

        # 转换为无向图进行分析
        undirected_graph = graph.to_undirected() if graph.is_directed() else graph

        # 原始网络指标
        original_nodes = undirected_graph.number_of_nodes()
        original_edges = undirected_graph.number_of_edges()
        original_components = nx.number_connected_components(undirected_graph)
        original_largest_cc = len(max(nx.connected_components(undirected_graph), key=len))

        # 计算各种中心性
        degree_centrality = nx.degree_centrality(undirected_graph)
        betweenness_centrality = nx.betweenness_centrality(undirected_graph)
        closeness_centrality = nx.closeness_centrality(undirected_graph)

        # 随机攻击模拟
        random_attack_results = self._simulate_random_attack(undirected_graph, [0.1, 0.2, 0.3, 0.4, 0.5])

        # 目标攻击模拟（不同策略）
        targeted_attacks = {
            'degree': sorted(degree_centrality.keys(), key=lambda x: degree_centrality[x], reverse=True),
            'betweenness': sorted(betweenness_centrality.keys(), key=lambda x: betweenness_centrality[x], reverse=True),
            'closeness': sorted(closeness_centrality.keys(), key=lambda x: closeness_centrality[x], reverse=True)
        }

        targeted_attack_results = {}
        for strategy, node_order in targeted_attacks.items():
            targeted_attack_results[strategy] = self._simulate_targeted_attack(
                undirected_graph, node_order, [0.1, 0.2, 0.3, 0.4, 0.5]
            )

        # 识别关键节点
        critical_nodes = self._identify_critical_nodes(undirected_graph)

        # 计算总体脆弱性分数
        vulnerability_score = self._calculate_vulnerability_score(
            random_attack_results, targeted_attack_results, original_largest_cc
        )

        robustness = NetworkRobustness(
            random_attack_results=random_attack_results,
            targeted_attack_results=targeted_attack_results,
            critical_nodes=critical_nodes,
            vulnerability_score=vulnerability_score
        )

        self.network_robustness = robustness
        logger.info(f"网络鲁棒性分析完成，脆弱性分数: {vulnerability_score:.4f}")

        return robustness

    def _simulate_random_attack(self, graph: nx.Graph, removal_fractions: List[float]) -> Dict[str, List]:
        """模拟随机攻击"""
        results = {'removal_fraction': [], 'largest_cc_size': [], 'num_components': []}

        for fraction in removal_fractions:
            num_nodes_to_remove = int(graph.number_of_nodes() * fraction)
            nodes_to_remove = np.random.choice(
                list(graph.nodes()), size=num_nodes_to_remove, replace=False
            )

            temp_graph = graph.copy()
            temp_graph.remove_nodes_from(nodes_to_remove)

            if temp_graph.number_of_nodes() > 0:
                largest_cc_size = len(max(nx.connected_components(temp_graph), key=len))
                num_components = nx.number_connected_components(temp_graph)
            else:
                largest_cc_size = 0
                num_components = 0

            results['removal_fraction'].append(fraction)
            results['largest_cc_size'].append(largest_cc_size)
            results['num_components'].append(num_components)

        return results

    def _simulate_targeted_attack(self, graph: nx.Graph, node_order: List[str],
                                 removal_fractions: List[float]) -> Dict[str, List]:
        """模拟目标攻击"""
        results = {'removal_fraction': [], 'largest_cc_size': [], 'num_components': []}

        for fraction in removal_fractions:
            num_nodes_to_remove = int(graph.number_of_nodes() * fraction)
            nodes_to_remove = node_order[:num_nodes_to_remove]

            temp_graph = graph.copy()
            temp_graph.remove_nodes_from(nodes_to_remove)

            if temp_graph.number_of_nodes() > 0:
                largest_cc_size = len(max(nx.connected_components(temp_graph), key=len))
                num_components = nx.number_connected_components(temp_graph)
            else:
                largest_cc_size = 0
                num_components = 0

            results['removal_fraction'].append(fraction)
            results['largest_cc_size'].append(largest_cc_size)
            results['num_components'].append(num_components)

        return results

    def _identify_critical_nodes(self, graph: nx.Graph, top_k: int = 10) -> List[str]:
        """识别关键节点"""
        # 综合多种中心性指标
        degree_centrality = nx.degree_centrality(graph)
        betweenness_centrality = nx.betweenness_centrality(graph)
        closeness_centrality = nx.closeness_centrality(graph)

        # 计算综合重要性分数
        importance_scores = {}
        for node in graph.nodes():
            score = (
                degree_centrality.get(node, 0) * 0.4 +
                betweenness_centrality.get(node, 0) * 0.4 +
                closeness_centrality.get(node, 0) * 0.2
            )
            importance_scores[node] = score

        # 返回最重要的节点
        critical_nodes = sorted(importance_scores.keys(),
                              key=lambda x: importance_scores[x], reverse=True)[:top_k]

        return critical_nodes

    def _calculate_vulnerability_score(self, random_results: Dict, targeted_results: Dict,
                                     original_largest_cc: int) -> float:
        """计算网络脆弱性分数"""
        # 基于20%节点移除后的性能计算
        removal_idx = 1  # 对应20%移除

        # 随机攻击后的最大连通分量
        random_cc = random_results['largest_cc_size'][removal_idx]
        random_resilience = random_cc / original_largest_cc

        # 目标攻击后的最大连通分量（取最严重的情况）
        worst_targeted_cc = min([
            results['largest_cc_size'][removal_idx]
            for results in targeted_results.values()
        ])
        targeted_resilience = worst_targeted_cc / original_largest_cc

        # 脆弱性分数（越高越脆弱）
        vulnerability = 1.0 - (random_resilience * 0.3 + targeted_resilience * 0.7)

        return max(0.0, min(1.0, vulnerability))

if __name__ == "__main__":
    # 测试高级分析器
    analyzer = AdvancedNetworkAnalyzer()

    # 加载数据
    json_path = "/d/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
    analyzer.load_data(json_path=json_path)

    # 构建网络
    analyzer.build_main_network()

    # 高级分析
    communities = analyzer.detect_communities_advanced()
    critical_paths = analyzer.identify_critical_paths_advanced()
    robustness = analyzer.analyze_network_robustness_advanced()

    print("高级网络分析完成！")
    print(f"最佳社群检测模块度: {analyzer.community_structure.modularity:.4f}")
    print(f"识别关键路径: {len(critical_paths)} 条")
    print(f"网络脆弱性分数: {robustness.vulnerability_score:.4f}")