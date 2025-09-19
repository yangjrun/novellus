"""
跨域冲突网络可视化系统
实现交互式可视化、多层次展示、动态演化动画等功能
"""

import json
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
import logging
from pathlib import Path
import itertools
import math

# 可视化库
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    import plotly.io as pio
    import plotly.figure_factory as ff
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pyvis
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False

try:
    import dash
    from dash import dcc, html, Input, Output, State, callback
    import dash_cytoscape as cyto
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False

# 从分析器导入
from dynamic_conflict_analyzer import DynamicConflictAnalyzer, ConflictState, EscalationPath

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisualizationConfig:
    """可视化配置"""
    layout_algorithm: str = 'spring'  # spring, circular, hierarchical, force_directed
    node_size_factor: float = 10.0
    edge_width_factor: float = 2.0
    color_scheme: str = 'domain'  # domain, entity_type, conflict_intensity
    show_labels: bool = True
    interactive: bool = True
    animation_speed: float = 1.0

class NetworkVisualizer:
    """网络可视化器"""

    def __init__(self, analyzer: DynamicConflictAnalyzer):
        """初始化可视化器"""
        self.analyzer = analyzer
        self.config = VisualizationConfig()

        # 颜色配置
        self.domain_colors = {
            '人域域': '#FF6B6B',
            '天域域': '#4ECDC4',
            '灵域域': '#45B7D1',
            '荒域域': '#96CEB4'
        }

        self.entity_type_colors = {
            '核心资源': '#FFD93D',
            '法条制度': '#6BCF7F',
            '关键角色': '#DDA0DD',
            '推断实体': '#F4A261'
        }

        self.relation_type_colors = {
            '对立': '#FF4444',
            '竞争': '#FF8C42',
            '制约': '#FFA726',
            '依赖': '#66BB6A'
        }

        # 缓存的布局
        self.cached_layouts = {}

    def create_interactive_network_plot(self, graph: nx.Graph = None,
                                      config: VisualizationConfig = None) -> Any:
        """创建交互式网络图"""
        if not PLOTLY_AVAILABLE:
            logger.error("Plotly 不可用，无法创建交互式图表")
            return None

        if graph is None:
            graph = self.analyzer.main_network

        if config is None:
            config = self.config

        logger.info("创建交互式网络图...")

        # 计算布局
        pos = self._get_layout(graph, config.layout_algorithm)

        # 准备节点数据
        node_trace = self._create_node_trace(graph, pos, config)

        # 准备边数据
        edge_traces = self._create_edge_traces(graph, pos, config)

        # 创建图形
        fig = go.Figure(data=edge_traces + [node_trace])

        # 更新布局
        fig.update_layout(
            title="跨域冲突网络图",
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="拖拽节点进行交互，悬停查看详情",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color="#888", size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=800
        )

        return fig

    def _get_layout(self, graph: nx.Graph, algorithm: str) -> Dict[str, Tuple[float, float]]:
        """获取网络布局"""
        cache_key = f"{algorithm}_{graph.number_of_nodes()}_{graph.number_of_edges()}"

        if cache_key in self.cached_layouts:
            return self.cached_layouts[cache_key]

        logger.info(f"计算 {algorithm} 布局...")

        if algorithm == 'spring':
            pos = nx.spring_layout(graph, k=1, iterations=50)
        elif algorithm == 'circular':
            pos = nx.circular_layout(graph)
        elif algorithm == 'hierarchical':
            pos = self._hierarchical_layout(graph)
        elif algorithm == 'force_directed':
            pos = nx.fruchterman_reingold_layout(graph, iterations=100)
        else:
            pos = nx.spring_layout(graph)

        self.cached_layouts[cache_key] = pos
        return pos

    def _hierarchical_layout(self, graph: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """分层布局（按域分层）"""
        pos = {}

        # 按域分组节点
        domain_nodes = {}
        for node, data in graph.nodes(data=True):
            domains = data.get('domains', ['未知'])
            primary_domain = domains[0] if domains else '未知'

            if primary_domain not in domain_nodes:
                domain_nodes[primary_domain] = []
            domain_nodes[primary_domain].append(node)

        # 为每个域分配y坐标
        domain_list = list(domain_nodes.keys())
        n_domains = len(domain_list)

        for i, domain in enumerate(domain_list):
            y = i / max(n_domains - 1, 1)  # 垂直分布
            nodes = domain_nodes[domain]

            # 在该层内水平分布节点
            for j, node in enumerate(nodes):
                x = j / max(len(nodes) - 1, 1) if len(nodes) > 1 else 0.5
                pos[node] = (x, y)

        return pos

    def _create_node_trace(self, graph: nx.Graph, pos: Dict,
                          config: VisualizationConfig) -> go.Scatter:
        """创建节点轨迹"""
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []

        for node, data in graph.nodes(data=True):
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # 节点信息
            name = data.get('name', node)
            entity_type = data.get('entity_type', '未知')
            domains = ', '.join(data.get('domains', ['未知']))
            importance = data.get('importance', '中')

            # 悬停文本
            hover_text = f"<b>{name}</b><br>"
            hover_text += f"类型: {entity_type}<br>"
            hover_text += f"域: {domains}<br>"
            hover_text += f"重要性: {importance}"

            node_text.append(hover_text)

            # 节点颜色
            if config.color_scheme == 'domain':
                primary_domain = data.get('domains', ['未知'])[0]
                color = self.domain_colors.get(primary_domain, '#CCCCCC')
            elif config.color_scheme == 'entity_type':
                color = self.entity_type_colors.get(entity_type, '#CCCCCC')
            else:
                color = '#1f77b4'

            node_color.append(color)

            # 节点大小
            importance_weight = data.get('importance_weight', 1.0)
            size = max(10, importance_weight * config.node_size_factor)
            node_size.append(size)

        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text' if config.show_labels else 'markers',
            text=[data.get('name', node) for node, data in graph.nodes(data=True)],
            textposition="middle center",
            textfont=dict(size=8),
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            )
        )

    def _create_edge_traces(self, graph: nx.Graph, pos: Dict,
                           config: VisualizationConfig) -> List[go.Scatter]:
        """创建边轨迹"""
        edge_traces = []

        # 按关系类型分组边
        relation_edges = {}
        for source, target, data in graph.edges(data=True):
            relation_type = data.get('relation_type', '未知')
            if relation_type not in relation_edges:
                relation_edges[relation_type] = []
            relation_edges[relation_type].append((source, target, data))

        # 为每种关系类型创建轨迹
        for relation_type, edges in relation_edges.items():
            edge_x = []
            edge_y = []
            edge_info = []

            for source, target, data in edges:
                x0, y0 = pos[source]
                x1, y1 = pos[target]

                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

                # 边信息
                strength = data.get('strength', 1.0)
                info = f"{relation_type}: {strength:.2f}"
                edge_info.append(info)

            color = self.relation_type_colors.get(relation_type, '#888888')
            width = config.edge_width_factor

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=width, color=color),
                hoverinfo='none',
                mode='lines',
                name=relation_type,
                legendgroup=relation_type,
                showlegend=True
            )

            edge_traces.append(edge_trace)

        return edge_traces

    def create_multilayer_visualization(self) -> Any:
        """创建多层网络可视化"""
        if not PLOTLY_AVAILABLE:
            logger.error("Plotly 不可用")
            return None

        logger.info("创建多层网络可视化...")

        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['按域分层', '按实体类型分层', '按关系类型分层', '整体网络'],
            specs=[[{"type": "xy"}, {"type": "xy"}],
                   [{"type": "xy"}, {"type": "xy"}]]
        )

        # 域分层
        if self.analyzer.domain_networks:
            self._add_domain_subplots(fig, row=1, col=1)

        # 类型分层
        if self.analyzer.type_networks:
            self._add_type_subplots(fig, row=1, col=2)

        # 关系分层
        if self.analyzer.relation_networks:
            self._add_relation_subplots(fig, row=2, col=1)

        # 整体网络
        self._add_overall_network(fig, row=2, col=2)

        fig.update_layout(
            title="多层网络分析",
            height=800,
            showlegend=False
        )

        return fig

    def _add_domain_subplots(self, fig: go.Figure, row: int, col: int):
        """添加域分层子图"""
        # 选择最大的域网络进行展示
        largest_domain = max(self.analyzer.domain_networks.keys(),
                           key=lambda d: self.analyzer.domain_networks[d].number_of_nodes())

        domain_graph = self.analyzer.domain_networks[largest_domain]
        pos = nx.spring_layout(domain_graph, k=0.5)

        # 添加节点
        node_x = [pos[node][0] for node in domain_graph.nodes()]
        node_y = [pos[node][1] for node in domain_graph.nodes()]

        fig.add_trace(
            go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                marker=dict(size=8, color=self.domain_colors.get(largest_domain, '#1f77b4')),
                name=f'{largest_domain}',
                hoverinfo='skip'
            ),
            row=row, col=col
        )

        # 添加边
        edge_x, edge_y = [], []
        for edge in domain_graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        fig.add_trace(
            go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=1, color='#888'),
                hoverinfo='none',
                showlegend=False
            ),
            row=row, col=col
        )

    def _add_type_subplots(self, fig: go.Figure, row: int, col: int):
        """添加类型分层子图"""
        # 简化展示：显示各类型的节点数量
        type_counts = {}
        for type_name, type_graph in self.analyzer.type_networks.items():
            type_counts[type_name] = type_graph.number_of_nodes()

        if type_counts:
            types = list(type_counts.keys())
            counts = list(type_counts.values())
            colors = [self.entity_type_colors.get(t, '#CCCCCC') for t in types]

            fig.add_trace(
                go.Bar(
                    x=types, y=counts,
                    marker_color=colors,
                    name='实体类型分布',
                    showlegend=False
                ),
                row=row, col=col
            )

    def _add_relation_subplots(self, fig: go.Figure, row: int, col: int):
        """添加关系分层子图"""
        # 显示关系类型分布
        relation_counts = {}
        for relation_type, relation_graph in self.analyzer.relation_networks.items():
            relation_counts[relation_type] = relation_graph.number_of_edges()

        if relation_counts:
            relations = list(relation_counts.keys())
            counts = list(relation_counts.values())
            colors = [self.relation_type_colors.get(r, '#CCCCCC') for r in relations]

            fig.add_trace(
                go.Bar(
                    x=relations, y=counts,
                    marker_color=colors,
                    name='关系类型分布',
                    showlegend=False
                ),
                row=row, col=col
            )

    def _add_overall_network(self, fig: go.Figure, row: int, col: int):
        """添加整体网络子图"""
        graph = self.analyzer.main_network
        pos = nx.spring_layout(graph, k=0.3, iterations=20)

        # 简化展示：只显示重要节点
        important_nodes = []
        for node, data in graph.nodes(data=True):
            if data.get('importance_weight', 1.0) > 2.0:
                important_nodes.append(node)

        if len(important_nodes) > 50:
            important_nodes = important_nodes[:50]

        # 创建子图
        subgraph = graph.subgraph(important_nodes)
        sub_pos = {node: pos[node] for node in important_nodes if node in pos}

        # 添加节点
        node_x = [sub_pos[node][0] for node in subgraph.nodes() if node in sub_pos]
        node_y = [sub_pos[node][1] for node in subgraph.nodes() if node in sub_pos]

        fig.add_trace(
            go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                marker=dict(size=6, color='#1f77b4'),
                name='重要节点',
                hoverinfo='skip'
            ),
            row=row, col=col
        )

    def create_conflict_evolution_animation(self, escalation_paths: List[EscalationPath] = None) -> Any:
        """创建冲突演化动画"""
        if not PLOTLY_AVAILABLE:
            logger.error("Plotly 不可用")
            return None

        if escalation_paths is None:
            escalation_paths = self.analyzer.critical_paths[:5]  # 取前5条路径

        logger.info("创建冲突演化动画...")

        frames = []
        max_steps = max(len(path.path) for path in escalation_paths) if escalation_paths else 5

        for step in range(max_steps):
            frame_data = []

            for path_idx, path in enumerate(escalation_paths):
                if step < len(path.path):
                    # 当前步骤的状态
                    current_nodes = path.path[:step+1]

                    # 创建路径轨迹
                    path_trace = go.Scatter(
                        x=list(range(len(current_nodes))),
                        y=[path_idx] * len(current_nodes),
                        mode='lines+markers',
                        name=f'路径 {path_idx + 1}',
                        line=dict(color=px.colors.qualitative.Set1[path_idx % 10])
                    )

                    frame_data.append(path_trace)

            frames.append(go.Frame(data=frame_data, name=str(step)))

        # 创建初始图形
        fig = go.Figure(frames=frames)

        # 添加播放控件
        fig.update_layout(
            title="冲突升级路径演化",
            xaxis_title="演化步骤",
            yaxis_title="升级路径",
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(label="播放",
                             method="animate",
                             args=[None, {"frame": {"duration": 1000, "redraw": True},
                                         "fromcurrent": True}]),
                        dict(label="暂停",
                             method="animate",
                             args=[[None], {"frame": {"duration": 0, "redraw": False},
                                           "mode": "immediate",
                                           "transition": {"duration": 0}}])
                    ]
                )
            ]
        )

        return fig

    def create_metrics_dashboard(self) -> Any:
        """创建指标仪表盘"""
        if not PLOTLY_AVAILABLE:
            logger.error("Plotly 不可用")
            return None

        logger.info("创建指标仪表盘...")

        # 创建子图
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=[
                '网络密度', '平均路径长度', '聚类系数',
                '度分布', '中心性排名', '社群分布',
                '冲突强度分布', '稳定性指标', '升级风险'
            ],
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                [{"type": "xy"}, {"type": "xy"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "indicator"}, {"type": "indicator"}]
            ]
        )

        # 网络基础指标
        if self.analyzer.network_metrics:
            metrics = self.analyzer.network_metrics

            # 密度指示器
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=metrics.density,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "网络密度"},
                    gauge={'axis': {'range': [None, 1]},
                          'bar': {'color': "darkblue"},
                          'steps': [{'range': [0, 0.5], 'color': "lightgray"},
                                   {'range': [0.5, 1], 'color': "gray"}]}
                ),
                row=1, col=1
            )

            # 路径长度指示器
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=metrics.avg_path_length,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "平均路径长度"}
                ),
                row=1, col=2
            )

            # 聚类系数指示器
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=metrics.clustering_coefficient,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "聚类系数"}
                ),
                row=1, col=3
            )

        # 度分布
        self._add_degree_distribution_plot(fig, row=2, col=1)

        # 中心性排名
        self._add_centrality_ranking_plot(fig, row=2, col=2)

        # 社群分布
        self._add_community_distribution_plot(fig, row=2, col=3)

        # 冲突强度分布
        self._add_conflict_intensity_plot(fig, row=3, col=1)

        # 其他指标...

        fig.update_layout(
            title="网络分析仪表盘",
            height=900
        )

        return fig

    def _add_degree_distribution_plot(self, fig: go.Figure, row: int, col: int):
        """添加度分布图"""
        graph = self.analyzer.main_network
        degrees = [d for n, d in graph.degree()]

        fig.add_trace(
            go.Histogram(
                x=degrees,
                nbinsx=20,
                name='度分布',
                showlegend=False
            ),
            row=row, col=col
        )

    def _add_centrality_ranking_plot(self, fig: go.Figure, row: int, col: int):
        """添加中心性排名图"""
        if self.analyzer.centrality_metrics:
            centrality = self.analyzer.centrality_metrics.pagerank

            # 取前10个节点
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            nodes, values = zip(*top_nodes)

            # 获取节点名称
            graph = self.analyzer.main_network
            node_names = [graph.nodes[node].get('name', node) for node in nodes]

            fig.add_trace(
                go.Bar(
                    x=values,
                    y=node_names,
                    orientation='h',
                    name='PageRank',
                    showlegend=False
                ),
                row=row, col=col
            )

    def _add_community_distribution_plot(self, fig: go.Figure, row: int, col: int):
        """添加社群分布图"""
        if self.analyzer.community_structure:
            community_sizes = self.analyzer.community_structure.community_sizes

            fig.add_trace(
                go.Bar(
                    x=list(range(len(community_sizes))),
                    y=community_sizes,
                    name='社群大小',
                    showlegend=False
                ),
                row=row, col=col
            )

    def _add_conflict_intensity_plot(self, fig: go.Figure, row: int, col: int):
        """添加冲突强度分布图"""
        graph = self.analyzer.main_network
        conflict_intensities = []

        for source, target, data in graph.edges(data=True):
            relation_type = data.get('relation_type', '')
            strength = data.get('strength', 1.0)

            if relation_type in ['对立', '竞争']:
                conflict_intensities.append(strength)

        if conflict_intensities:
            fig.add_trace(
                go.Histogram(
                    x=conflict_intensities,
                    nbinsx=15,
                    name='冲突强度',
                    showlegend=False
                ),
                row=row, col=col
            )

    def export_visualization(self, fig: Any, filename: str, format: str = 'html'):
        """导出可视化结果"""
        if not PLOTLY_AVAILABLE:
            logger.error("Plotly 不可用")
            return

        output_path = Path(f"/d/work/novellus/output/{filename}.{format}")
        output_path.parent.mkdir(exist_ok=True)

        if format == 'html':
            fig.write_html(str(output_path))
        elif format == 'png':
            fig.write_image(str(output_path))
        elif format == 'pdf':
            fig.write_image(str(output_path))

        logger.info(f"可视化结果已导出到: {output_path}")

if __name__ == "__main__":
    # 测试可视化器
    from dynamic_conflict_analyzer import DynamicConflictAnalyzer

    analyzer = DynamicConflictAnalyzer()

    # 加载数据
    json_path = "/d/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
    analyzer.load_data(json_path=json_path)

    # 构建网络
    analyzer.build_main_network()
    analyzer.build_domain_networks()
    analyzer.build_type_networks()
    analyzer.build_relation_networks()

    # 分析
    analyzer.calculate_network_metrics()
    analyzer.calculate_centrality_metrics()
    analyzer.detect_communities_advanced()

    # 可视化
    visualizer = NetworkVisualizer(analyzer)

    # 创建交互式网络图
    network_fig = visualizer.create_interactive_network_plot()
    if network_fig:
        visualizer.export_visualization(network_fig, "interactive_network")

    # 创建多层可视化
    multilayer_fig = visualizer.create_multilayer_visualization()
    if multilayer_fig:
        visualizer.export_visualization(multilayer_fig, "multilayer_network")

    # 创建仪表盘
    dashboard_fig = visualizer.create_metrics_dashboard()
    if dashboard_fig:
        visualizer.export_visualization(dashboard_fig, "metrics_dashboard")

    print("可视化系统测试完成！")