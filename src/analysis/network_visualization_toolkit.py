"""
跨域冲突网络可视化工具包
提供多种网络可视化和交互式展示功能
"""

import json
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Union
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from pathlib import Path
import logging

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

# 导入综合分析模型
from comprehensive_conflict_network_model import ComprehensiveConflictNetworkModel

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkVisualizationToolkit:
    """网络可视化工具包主类"""

    def __init__(self, model: ComprehensiveConflictNetworkModel = None):
        """
        初始化可视化工具包

        Args:
            model: 综合冲突网络模型实例
        """
        self.model = model
        self.color_schemes = {
            'domains': {
                '人域': '#FF6B6B',   # 红色
                '天域': '#4ECDC4',   # 青色
                '灵域': '#45B7D1',   # 蓝色
                '荒域': '#96CEB4',   # 绿色
                '混沌域': '#FFD93D', # 黄色
                '虚无域': '#DDA0DD', # 紫色
                '时间域': '#F4A261', # 橙色
                '空间域': '#2A9D8F', # 深绿
                '未知域': '#808080'  # 灰色
            },
            'entity_types': {
                '核心资源': '#FFD93D',   # 黄色
                '法条制度': '#6BCF7F',   # 绿色
                '关键角色': '#DDA0DD',   # 紫色
                '推断实体': '#F4A261',   # 橙色
                '地理实体': '#2A9D8F',   # 深绿
                '文化实体': '#E76F51',   # 红橙
                '未知类型': '#808080'    # 灰色
            },
            'relation_types': {
                '对立': '#FF4444',  # 红色
                '竞争': '#FF8C00',  # 橙色
                '制约': '#FFD700',  # 金色
                '依赖': '#32CD32',  # 绿色
                '合作': '#4169E1',  # 蓝色
                '未知': '#808080'   # 灰色
            },
            'intensity_levels': {
                'low': '#90EE90',     # 浅绿
                'medium': '#FFD700',  # 金色
                'high': '#FF6347',    # 红色
                'critical': '#DC143C' # 深红
            }
        }

        # 可视化设置
        self.default_figsize = (15, 10)
        self.default_dpi = 300
        self.node_size_range = (50, 1000)
        self.edge_width_range = (0.5, 5)

    def plot_network_overview(self,
                             layout: str = 'spring',
                             save_path: str = None,
                             show_labels: bool = True,
                             node_size_metric: str = 'degree',
                             edge_weight_metric: str = 'strength',
                             color_scheme: str = 'domains') -> plt.Figure:
        """
        绘制网络概览图

        Args:
            layout: 布局算法 ('spring', 'circular', 'kamada_kawai', 'spectral')
            save_path: 保存路径
            show_labels: 是否显示标签
            node_size_metric: 节点大小度量
            edge_weight_metric: 边权重度量
            color_scheme: 颜色方案

        Returns:
            matplotlib.figure.Figure: 图形对象
        """
        if self.model is None or self.model.main_network is None:
            raise ValueError("模型或网络未初始化")

        logger.info("绘制网络概览图...")

        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)

        G = self.model.main_network

        # 选择布局
        layout_funcs = {
            'spring': nx.spring_layout,
            'circular': nx.circular_layout,
            'kamada_kawai': nx.kamada_kawai_layout,
            'spectral': nx.spectral_layout
        }

        if layout not in layout_funcs:
            layout = 'spring'

        try:
            pos = layout_funcs[layout](G, k=1, iterations=50)
        except:
            pos = nx.spring_layout(G)

        # 计算节点大小
        node_sizes = self._calculate_node_sizes(G, node_size_metric)

        # 计算边权重
        edge_weights = self._calculate_edge_weights(G, edge_weight_metric)

        # 选择颜色方案
        node_colors = self._get_node_colors(G, color_scheme)

        # 绘制边
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            width=[edge_weights.get((u, v), 1) for u, v in G.edges()],
            alpha=0.6,
            edge_color='gray'
        )

        # 绘制节点
        nx.draw_networkx_nodes(
            G, pos, ax=ax,
            node_size=[node_sizes.get(node, 100) for node in G.nodes()],
            node_color=[node_colors.get(node, '#808080') for node in G.nodes()],
            alpha=0.8
        )

        # 绘制标签
        if show_labels:
            labels = {node: data.get('name', node)[:8] + '...' if len(data.get('name', node)) > 8
                     else data.get('name', node) for node, data in G.nodes(data=True)}
            nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8)

        # 设置标题和图例
        ax.set_title(f"跨域冲突网络概览图 ({len(G.nodes())} 节点, {len(G.edges())} 边)",
                    fontsize=16, fontweight='bold')

        # 添加图例
        self._add_legend(ax, color_scheme)

        ax.axis('off')
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.default_dpi, bbox_inches='tight')
            logger.info(f"网络概览图已保存至: {save_path}")

        return fig

    def plot_domain_networks(self,
                           save_dir: str = None,
                           layout: str = 'spring') -> Dict[str, plt.Figure]:
        """
        绘制各域的子网络图

        Args:
            save_dir: 保存目录
            layout: 布局算法

        Returns:
            Dict[str, plt.Figure]: 各域的图形对象字典
        """
        if self.model is None:
            raise ValueError("模型未初始化")

        if not hasattr(self.model, 'domain_networks') or not self.model.domain_networks:
            self.model.build_domain_networks()

        logger.info("绘制域子网络图...")

        figures = {}

        for domain, subgraph in self.model.domain_networks.items():
            if subgraph.number_of_nodes() == 0:
                continue

            fig, ax = plt.subplots(figsize=(12, 8), dpi=self.default_dpi)

            # 布局
            try:
                if layout == 'spring':
                    pos = nx.spring_layout(subgraph, k=1, iterations=50)
                elif layout == 'circular':
                    pos = nx.circular_layout(subgraph)
                else:
                    pos = nx.spring_layout(subgraph)
            except:
                pos = nx.spring_layout(subgraph)

            # 节点大小和颜色
            node_sizes = self._calculate_node_sizes(subgraph, 'degree')
            domain_color = self.color_schemes['domains'].get(domain, '#808080')

            # 绘制网络
            nx.draw_networkx_edges(
                subgraph, pos, ax=ax,
                alpha=0.6, edge_color='gray', width=1
            )

            nx.draw_networkx_nodes(
                subgraph, pos, ax=ax,
                node_size=[node_sizes.get(node, 100) for node in subgraph.nodes()],
                node_color=domain_color,
                alpha=0.8
            )

            # 标签
            labels = {node: data.get('name', node)[:6] + '...' if len(data.get('name', node)) > 6
                     else data.get('name', node) for node, data in subgraph.nodes(data=True)}
            nx.draw_networkx_labels(subgraph, pos, labels, ax=ax, font_size=8)

            ax.set_title(f"{domain} 子网络 ({subgraph.number_of_nodes()} 节点, {subgraph.number_of_edges()} 边)",
                        fontsize=14, fontweight='bold')
            ax.axis('off')

            figures[domain] = fig

            if save_dir:
                save_path = Path(save_dir) / f"{domain}_subnetwork.png"
                fig.savefig(save_path, dpi=self.default_dpi, bbox_inches='tight')

        logger.info(f"域子网络图绘制完成，共 {len(figures)} 个域")
        return figures

    def plot_centrality_heatmap(self,
                               save_path: str = None,
                               top_n: int = 20) -> plt.Figure:
        """
        绘制中心性热力图

        Args:
            save_path: 保存路径
            top_n: 显示的顶部节点数

        Returns:
            matplotlib.figure.Figure: 图形对象
        """
        if self.model is None or self.model.centrality_analysis is None:
            raise ValueError("模型或中心性分析结果未初始化")

        logger.info("绘制中心性热力图...")

        centrality_data = self.model.centrality_analysis

        # 准备数据
        centrality_metrics = {
            'Degree': centrality_data.degree_centrality,
            'Betweenness': centrality_data.betweenness_centrality,
            'Closeness': centrality_data.closeness_centrality,
            'Eigenvector': centrality_data.eigenvector_centrality,
            'PageRank': centrality_data.pagerank,
            'Conflict': centrality_data.conflict_centrality
        }

        # 获取前top_n个节点（按度中心性排序）
        top_nodes = sorted(centrality_data.degree_centrality.items(),
                          key=lambda x: x[1], reverse=True)[:top_n]
        top_node_ids = [node for node, _ in top_nodes]

        # 构建数据矩阵
        data_matrix = []
        for metric_name, metric_values in centrality_metrics.items():
            metric_row = [metric_values.get(node, 0) for node in top_node_ids]
            data_matrix.append(metric_row)

        data_matrix = np.array(data_matrix)

        # 标准化数据
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        data_matrix = scaler.fit_transform(data_matrix)

        # 绘制热力图
        fig, ax = plt.subplots(figsize=(15, 8), dpi=self.default_dpi)

        # 获取节点名称
        if self.model.main_network:
            node_names = [self.model.main_network.nodes[node].get('name', node)[:10]
                         for node in top_node_ids]
        else:
            node_names = [f"Node_{i}" for i in range(len(top_node_ids))]

        im = ax.imshow(data_matrix, cmap='RdYlBu_r', aspect='auto')

        # 设置刻度和标签
        ax.set_xticks(range(len(node_names)))
        ax.set_xticklabels(node_names, rotation=45, ha='right')
        ax.set_yticks(range(len(centrality_metrics)))
        ax.set_yticklabels(list(centrality_metrics.keys()))

        # 添加数值标注
        for i in range(len(centrality_metrics)):
            for j in range(len(node_names)):
                text = ax.text(j, i, f'{data_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('标准化中心性值', rotation=270, labelpad=20)

        ax.set_title(f'前{top_n}个节点的中心性热力图', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.default_dpi, bbox_inches='tight')
            logger.info(f"中心性热力图已保存至: {save_path}")

        return fig

    def plot_community_structure(self,
                               save_path: str = None,
                               layout: str = 'spring') -> plt.Figure:
        """
        绘制社团结构图

        Args:
            save_path: 保存路径
            layout: 布局算法

        Returns:
            matplotlib.figure.Figure: 图形对象
        """
        if self.model is None or self.model.community_structure is None:
            raise ValueError("模型或社团结构未初始化")

        logger.info("绘制社团结构图...")

        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)

        G = self.model.main_network
        communities = self.model.community_structure.louvain_communities

        # 布局
        try:
            if layout == 'spring':
                pos = nx.spring_layout(G, k=1, iterations=50)
            elif layout == 'circular':
                pos = nx.circular_layout(G)
            else:
                pos = nx.spring_layout(G)
        except:
            pos = nx.spring_layout(G)

        # 为每个社团分配颜色
        community_colors = plt.cm.Set3(np.linspace(0, 1, len(communities)))
        node_colors = {}

        for comm_id, nodes in communities.items():
            color = community_colors[comm_id % len(community_colors)]
            for node in nodes:
                node_colors[node] = color

        # 绘制边
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, edge_color='gray', width=0.5)

        # 按社团绘制节点
        for comm_id, nodes in communities.items():
            node_list = [node for node in nodes if node in G.nodes()]
            if node_list:
                color = community_colors[comm_id % len(community_colors)]
                node_positions = {node: pos[node] for node in node_list if node in pos}

                nx.draw_networkx_nodes(
                    G.subgraph(node_list), node_positions, ax=ax,
                    node_color=[color], node_size=200, alpha=0.8,
                    label=f'社团 {comm_id} ({len(node_list)} 节点)'
                )

        # 添加社团标签
        for comm_id, nodes in communities.items():
            if len(nodes) >= 3:  # 只为较大的社团添加标签
                # 计算社团中心
                node_positions = [pos[node] for node in nodes if node in pos]
                if node_positions:
                    center_x = np.mean([p[0] for p in node_positions])
                    center_y = np.mean([p[1] for p in node_positions])
                    ax.annotate(f'C{comm_id}', (center_x, center_y),
                              fontsize=12, fontweight='bold',
                              ha='center', va='center',
                              bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

        modularity = self.model.community_structure.louvain_modularity
        ax.set_title(f'社团结构图 ({len(communities)} 个社团, 模块度: {modularity:.3f})',
                    fontsize=16, fontweight='bold')

        # 图例
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.axis('off')
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.default_dpi, bbox_inches='tight')
            logger.info(f"社团结构图已保存至: {save_path}")

        return fig

    def plot_conflict_intensity_matrix(self,
                                     save_path: str = None,
                                     top_n: int = 30) -> plt.Figure:
        """
        绘制冲突强度矩阵热力图

        Args:
            save_path: 保存路径
            top_n: 显示的节点数

        Returns:
            matplotlib.figure.Figure: 图形对象
        """
        if self.model is None or self.model.intensity_model is None:
            raise ValueError("模型或强度模型未初始化")

        logger.info("绘制冲突强度矩阵...")

        intensity_matrix = self.model.intensity_model.intensity_matrix
        G = self.model.main_network
        nodes = list(G.nodes())

        # 选择前top_n个高强度节点
        node_intensities = self.model.intensity_model.node_intensities
        top_nodes = sorted(node_intensities.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_node_ids = [node for node, _ in top_nodes]

        # 构建节点索引映射
        node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        top_indices = [node_to_idx[node] for node in top_node_ids if node in node_to_idx]

        # 提取子矩阵
        sub_matrix = intensity_matrix[np.ix_(top_indices, top_indices)]

        fig, ax = plt.subplots(figsize=(12, 10), dpi=self.default_dpi)

        # 绘制热力图
        im = ax.imshow(sub_matrix, cmap='Reds', aspect='auto')

        # 获取节点名称
        node_names = [G.nodes[node].get('name', node)[:8] for node in top_node_ids]

        # 设置刻度
        ax.set_xticks(range(len(node_names)))
        ax.set_xticklabels(node_names, rotation=45, ha='right')
        ax.set_yticks(range(len(node_names)))
        ax.set_yticklabels(node_names)

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('冲突强度', rotation=270, labelpad=20)

        ax.set_title(f'冲突强度矩阵 (前{top_n}个高强度节点)', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.default_dpi, bbox_inches='tight')
            logger.info(f"冲突强度矩阵已保存至: {save_path}")

        return fig

    def plot_network_metrics_dashboard(self, save_path: str = None) -> plt.Figure:
        """
        绘制网络指标仪表板

        Args:
            save_path: 保存路径

        Returns:
            matplotlib.figure.Figure: 图形对象
        """
        if self.model is None:
            raise ValueError("模型未初始化")

        logger.info("绘制网络指标仪表板...")

        fig = plt.figure(figsize=(20, 12), dpi=self.default_dpi)

        # 创建子图网格
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

        # 1. 基础网络统计
        ax1 = fig.add_subplot(gs[0, 0])
        if self.model.topology_metrics:
            metrics = self.model.topology_metrics
            basic_stats = [
                ('节点数', metrics.num_nodes),
                ('边数', metrics.num_edges),
                ('密度', f"{metrics.density:.4f}"),
                ('连通分量', metrics.num_components)
            ]

            for i, (label, value) in enumerate(basic_stats):
                ax1.text(0.1, 0.8 - i*0.2, f"{label}: {value}", fontsize=12, transform=ax1.transAxes)

        ax1.set_title('基础统计', fontweight='bold')
        ax1.axis('off')

        # 2. 度分布
        ax2 = fig.add_subplot(gs[0, 1])
        if self.model.main_network:
            degrees = [d for n, d in self.model.main_network.degree()]
            ax2.hist(degrees, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax2.set_xlabel('度')
            ax2.set_ylabel('频数')
            ax2.set_title('度分布', fontweight='bold')

        # 3. 中心性排名
        ax3 = fig.add_subplot(gs[0, 2:])
        if self.model.centrality_analysis:
            centrality_rankings = self.model.centrality_analysis.centrality_rankings
            top_nodes = centrality_rankings.get('pagerank', [])[:10]

            if top_nodes:
                names = []
                scores = []
                for node, score in top_nodes:
                    name = self.model.main_network.nodes[node].get('name', node)[:10]
                    names.append(name)
                    scores.append(score)

                y_pos = np.arange(len(names))
                ax3.barh(y_pos, scores, color='lightcoral')
                ax3.set_yticks(y_pos)
                ax3.set_yticklabels(names)
                ax3.set_xlabel('PageRank 分数')
                ax3.set_title('Top 10 PageRank 节点', fontweight='bold')

        # 4. 社团大小分布
        ax4 = fig.add_subplot(gs[1, 0])
        if self.model.community_structure:
            community_sizes = self.model.community_structure.community_sizes
            ax4.bar(range(len(community_sizes)), sorted(community_sizes, reverse=True),
                   color='lightgreen', alpha=0.7)
            ax4.set_xlabel('社团排名')
            ax4.set_ylabel('社团大小')
            ax4.set_title('社团大小分布', fontweight='bold')

        # 5. 冲突强度分布
        ax5 = fig.add_subplot(gs[1, 1])
        if self.model.intensity_model:
            intensities = list(self.model.intensity_model.edge_intensities.values())
            ax5.hist(intensities, bins=20, alpha=0.7, color='orange', edgecolor='black')
            ax5.set_xlabel('冲突强度')
            ax5.set_ylabel('频数')
            ax5.set_title('冲突强度分布', fontweight='bold')

        # 6. 网络指标雷达图
        ax6 = fig.add_subplot(gs[1, 2:], projection='polar')
        if self.model.topology_metrics:
            metrics = self.model.topology_metrics

            # 标准化指标
            radar_metrics = {
                '密度': metrics.density,
                '聚类系数': metrics.global_clustering,
                '连通性': 1.0 if metrics.is_connected else 0.0,
                '传递性': metrics.transitivity,
                '同配性': (metrics.degree_assortativity + 1) / 2,  # 标准化到0-1
            }

            angles = np.linspace(0, 2*np.pi, len(radar_metrics), endpoint=False).tolist()
            values = list(radar_metrics.values())

            # 闭合图形
            angles += angles[:1]
            values += values[:1]

            ax6.plot(angles, values, 'o-', linewidth=2, color='blue')
            ax6.fill(angles, values, alpha=0.25, color='blue')
            ax6.set_xticks(angles[:-1])
            ax6.set_xticklabels(list(radar_metrics.keys()))
            ax6.set_ylim(0, 1)
            ax6.set_title('网络特征雷达图', fontweight='bold', pad=20)

        # 7. 攻击韧性
        ax7 = fig.add_subplot(gs[2, 0])
        if self.model.robustness_analysis:
            robustness = self.model.robustness_analysis
            attack_types = ['随机攻击', '目标攻击']
            thresholds = [robustness.random_attack_threshold, robustness.targeted_attack_threshold]

            colors = ['green' if t > 0.5 else 'orange' if t > 0.3 else 'red' for t in thresholds]
            ax7.bar(attack_types, thresholds, color=colors, alpha=0.7)
            ax7.set_ylabel('失效阈值')
            ax7.set_title('攻击韧性', fontweight='bold')
            ax7.set_ylim(0, 1)

        # 8. 系统风险评估
        ax8 = fig.add_subplot(gs[2, 1])
        if self.model.robustness_analysis:
            risk_score = self.model.robustness_analysis.systemic_risk_score

            # 风险等级饼图
            if risk_score < 0.3:
                risk_level = '低风险'
                colors = ['green', 'lightgray']
                sizes = [risk_score*100, (1-risk_score)*100]
            elif risk_score < 0.7:
                risk_level = '中风险'
                colors = ['orange', 'lightgray']
                sizes = [risk_score*100, (1-risk_score)*100]
            else:
                risk_level = '高风险'
                colors = ['red', 'lightgray']
                sizes = [risk_score*100, (1-risk_score)*100]

            ax8.pie(sizes, colors=colors, startangle=90,
                   labels=[f'{risk_level}\n{risk_score:.3f}', ''],
                   autopct='%1.1f%%' if risk_score > 0.1 else '')
            ax8.set_title('系统风险评估', fontweight='bold')

        # 9. 传播动力学
        ax9 = fig.add_subplot(gs[2, 2:])
        if self.model.propagation_model:
            propagation = self.model.propagation_model
            cascade_dist = propagation.cascade_size_distribution

            if cascade_dist:
                sizes = list(cascade_dist.keys())
                counts = list(cascade_dist.values())
                ax9.bar(sizes, counts, alpha=0.7, color='purple')
                ax9.set_xlabel('级联大小')
                ax9.set_ylabel('发生次数')
                ax9.set_title('级联分布', fontweight='bold')

        plt.suptitle('跨域冲突网络分析仪表板', fontsize=20, fontweight='bold', y=0.98)

        if save_path:
            fig.savefig(save_path, dpi=self.default_dpi, bbox_inches='tight')
            logger.info(f"网络指标仪表板已保存至: {save_path}")

        return fig

    def _calculate_node_sizes(self, graph: nx.Graph, metric: str) -> Dict[str, float]:
        """计算节点大小"""
        if metric == 'degree':
            values = dict(graph.degree())
        elif metric == 'betweenness' and self.model and self.model.centrality_analysis:
            values = self.model.centrality_analysis.betweenness_centrality
        elif metric == 'pagerank' and self.model and self.model.centrality_analysis:
            values = self.model.centrality_analysis.pagerank
        else:
            values = {node: 1 for node in graph.nodes()}

        # 标准化到指定范围
        if values:
            min_val, max_val = min(values.values()), max(values.values())
            if max_val > min_val:
                normalized = {node: (val - min_val) / (max_val - min_val)
                            for node, val in values.items()}
            else:
                normalized = {node: 0.5 for node in values.keys()}

            sizes = {node: self.node_size_range[0] + norm *
                    (self.node_size_range[1] - self.node_size_range[0])
                    for node, norm in normalized.items()}
        else:
            sizes = {node: self.node_size_range[0] for node in graph.nodes()}

        return sizes

    def _calculate_edge_weights(self, graph: nx.Graph, metric: str) -> Dict[Tuple[str, str], float]:
        """计算边权重"""
        weights = {}

        for u, v, data in graph.edges(data=True):
            if metric == 'strength':
                weight = data.get('strength', 1.0)
            elif metric == 'friction_heat':
                weight = data.get('friction_heat', 0.5)
            elif metric == 'escalation_potential':
                weight = data.get('escalation_potential', 0.3)
            else:
                weight = 1.0

            # 标准化到指定范围
            normalized_weight = self.edge_width_range[0] + weight * (self.edge_width_range[1] - self.edge_width_range[0])
            weights[(u, v)] = normalized_weight

        return weights

    def _get_node_colors(self, graph: nx.Graph, color_scheme: str) -> Dict[str, str]:
        """获取节点颜色"""
        colors = {}

        for node, data in graph.nodes(data=True):
            if color_scheme == 'domains':
                domains = data.get('domains', [])
                if domains:
                    primary_domain = domains[0]
                    colors[node] = self.color_schemes['domains'].get(primary_domain, '#808080')
                else:
                    colors[node] = '#808080'
            elif color_scheme == 'entity_types':
                entity_type = data.get('entity_type', '未知类型')
                colors[node] = self.color_schemes['entity_types'].get(entity_type, '#808080')
            else:
                colors[node] = '#808080'

        return colors

    def _add_legend(self, ax: plt.Axes, color_scheme: str):
        """添加图例"""
        if color_scheme in self.color_schemes:
            scheme = self.color_schemes[color_scheme]
            legend_elements = []

            for label, color in scheme.items():
                legend_elements.append(patches.Patch(color=color, label=label))

            ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

    def export_network_data(self, output_dir: str):
        """
        导出网络数据

        Args:
            output_dir: 输出目录
        """
        if self.model is None:
            raise ValueError("模型未初始化")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"导出网络数据到: {output_dir}")

        # 导出GraphML格式
        if self.model.main_network:
            graphml_path = output_path / "conflict_network.graphml"
            nx.write_graphml(self.model.main_network, graphml_path)

        # 导出边列表
        if self.model.main_network:
            edgelist_path = output_path / "conflict_network_edges.csv"
            edge_data = []
            for u, v, data in self.model.main_network.edges(data=True):
                edge_data.append({
                    'source': u,
                    'target': v,
                    'relation_type': data.get('relation_type', ''),
                    'strength': data.get('strength', 1.0),
                    'cross_domain': data.get('cross_domain', False)
                })
            pd.DataFrame(edge_data).to_csv(edgelist_path, index=False)

        # 导出节点数据
        if self.model.entities_df is not None:
            nodes_path = output_path / "conflict_network_nodes.csv"
            self.model.entities_df.to_csv(nodes_path, index=False)

        # 导出分析结果
        if hasattr(self.model, 'topology_metrics') and self.model.topology_metrics:
            results = {}

            # 拓扑指标
            results['topology_metrics'] = {
                'num_nodes': self.model.topology_metrics.num_nodes,
                'num_edges': self.model.topology_metrics.num_edges,
                'density': self.model.topology_metrics.density,
                'clustering_coefficient': self.model.topology_metrics.global_clustering,
                'avg_path_length': self.model.topology_metrics.avg_path_length
            }

            # 中心性结果
            if self.model.centrality_analysis:
                results['top_pagerank_nodes'] = self.model.centrality_analysis.centrality_rankings.get('pagerank', [])[:10]

            # 社团结果
            if self.model.community_structure:
                results['community_structure'] = {
                    'num_communities': self.model.community_structure.num_communities,
                    'modularity': self.model.community_structure.louvain_modularity
                }

            # 保存结果
            results_path = output_path / "analysis_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info("网络数据导出完成")

if __name__ == "__main__":
    # 测试可视化工具
    try:
        # 初始化模型
        model = ComprehensiveConflictNetworkModel()
        data_path = "D:/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
        model.load_data(data_path)

        # 运行分析
        results = model.run_comprehensive_analysis()

        # 初始化可视化工具
        viz_toolkit = NetworkVisualizationToolkit(model)

        # 创建输出目录
        output_dir = "D:/work/novellus/network_visualizations"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        print("=== 生成网络可视化 ===")

        # 1. 网络概览图
        fig1 = viz_toolkit.plot_network_overview(
            save_path=f"{output_dir}/network_overview.png",
            color_scheme='domains'
        )
        plt.close(fig1)

        # 2. 域子网络图
        domain_figs = viz_toolkit.plot_domain_networks(
            save_dir=f"{output_dir}/domain_networks"
        )
        for fig in domain_figs.values():
            plt.close(fig)

        # 3. 中心性热力图
        fig3 = viz_toolkit.plot_centrality_heatmap(
            save_path=f"{output_dir}/centrality_heatmap.png"
        )
        plt.close(fig3)

        # 4. 社团结构图
        fig4 = viz_toolkit.plot_community_structure(
            save_path=f"{output_dir}/community_structure.png"
        )
        plt.close(fig4)

        # 5. 冲突强度矩阵
        fig5 = viz_toolkit.plot_conflict_intensity_matrix(
            save_path=f"{output_dir}/intensity_matrix.png"
        )
        plt.close(fig5)

        # 6. 综合仪表板
        fig6 = viz_toolkit.plot_network_metrics_dashboard(
            save_path=f"{output_dir}/metrics_dashboard.png"
        )
        plt.close(fig6)

        # 7. 导出数据
        viz_toolkit.export_network_data(f"{output_dir}/exported_data")

        print("=== 可视化生成完成 ===")
        print(f"所有图表已保存到: {output_dir}")

    except Exception as e:
        logger.error(f"可视化测试失败: {e}")
        print(f"可视化过程中出现错误: {e}")
        import traceback
        traceback.print_exc()