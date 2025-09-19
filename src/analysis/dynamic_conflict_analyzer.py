"""
动态冲突网络分析器
实现时间序列分析、冲突升级建模、马尔可夫链分析等功能
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
from scipy.stats import poisson, expon
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# 时间序列分析
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller
except ImportError:
    ARIMA = seasonal_decompose = adfuller = None

# 马尔可夫链
try:
    import networkx.algorithms.markov as markov
except ImportError:
    markov = None

# 可视化
import matplotlib.pyplot as plt
import seaborn as sns

# 从基础分析器导入
from advanced_network_analyzer import AdvancedNetworkAnalyzer, ConflictPath

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConflictState:
    """冲突状态"""
    state_id: str
    entities_involved: List[str]
    conflict_intensity: float
    domains_affected: List[str]
    stability_score: float
    transition_probabilities: Dict[str, float]

@dataclass
class EscalationPath:
    """升级路径"""
    path_id: str
    states: List[ConflictState]
    trigger_events: List[str]
    escalation_probability: float
    time_to_escalation: float
    mitigation_strategies: List[str]

@dataclass
class ConflictDynamics:
    """冲突动态特征"""
    states: List[ConflictState]
    transition_matrix: np.ndarray
    steady_state: np.ndarray
    escalation_paths: List[EscalationPath]
    critical_transitions: List[Tuple[str, str, float]]

@dataclass
class TimeSeriesFeatures:
    """时间序列特征"""
    trend: str  # 'increasing', 'decreasing', 'stable'
    seasonality: bool
    periodicity: Optional[float]
    volatility: float
    stationarity: bool
    forecast: np.ndarray

class DynamicConflictAnalyzer(AdvancedNetworkAnalyzer):
    """动态冲突分析器"""

    def __init__(self, data_path: str = None):
        """初始化动态分析器"""
        super().__init__(data_path)

        # 动态分析结果
        self.conflict_dynamics = None
        self.escalation_model = None
        self.time_series_features = None

        # 动态参数
        self.conflict_states = {}
        self.state_transitions = defaultdict(list)

        # 时间窗口设置
        self.time_windows = [1, 7, 30, 90, 365]  # 天数

    def build_conflict_state_model(self, graph: nx.Graph = None) -> ConflictDynamics:
        """构建冲突状态模型"""
        if graph is None:
            graph = self.main_network

        logger.info("构建冲突状态模型...")

        # 识别基础冲突状态
        base_states = self._identify_base_conflict_states(graph)

        # 构建状态转换矩阵
        transition_matrix = self._build_transition_matrix(base_states)

        # 计算稳态分布
        steady_state = self._calculate_steady_state(transition_matrix)

        # 识别升级路径
        escalation_paths = self._identify_escalation_paths(base_states, transition_matrix)

        # 识别关键转换
        critical_transitions = self._identify_critical_transitions(base_states, transition_matrix)

        dynamics = ConflictDynamics(
            states=base_states,
            transition_matrix=transition_matrix,
            steady_state=steady_state,
            escalation_paths=escalation_paths,
            critical_transitions=critical_transitions
        )

        self.conflict_dynamics = dynamics
        logger.info(f"冲突状态模型构建完成: {len(base_states)}个状态, {len(escalation_paths)}条升级路径")

        return dynamics

    def _identify_base_conflict_states(self, graph: nx.Graph) -> List[ConflictState]:
        """识别基础冲突状态"""
        states = []

        # 基于社群结构定义状态
        if self.community_structure:
            communities = self.community_structure.communities

            for comm_id, nodes in communities.items():
                # 计算社群内冲突强度
                subgraph = graph.subgraph(nodes)
                conflict_intensity = self._calculate_community_conflict_intensity(subgraph)

                # 获取涉及的域
                domains_affected = set()
                for node in nodes:
                    if node in graph.nodes:
                        domains_affected.update(graph.nodes[node].get('domains', []))

                # 计算稳定性分数
                stability_score = self._calculate_stability_score(subgraph)

                state = ConflictState(
                    state_id=f"community_{comm_id}",
                    entities_involved=nodes,
                    conflict_intensity=conflict_intensity,
                    domains_affected=list(domains_affected),
                    stability_score=stability_score,
                    transition_probabilities={}
                )

                states.append(state)

        # 添加跨域冲突状态
        cross_domain_states = self._identify_cross_domain_states(graph)
        states.extend(cross_domain_states)

        return states

    def _calculate_community_conflict_intensity(self, subgraph: nx.Graph) -> float:
        """计算社群内冲突强度"""
        if subgraph.number_of_edges() == 0:
            return 0.0

        conflict_edges = 0
        total_strength = 0.0

        for source, target, data in subgraph.edges(data=True):
            relation_type = data.get('relation_type', '')
            strength = data.get('strength', 1.0)

            if relation_type in ['对立', '竞争']:
                conflict_edges += 1
                total_strength += strength * 2  # 冲突关系权重更高
            elif relation_type == '制约':
                conflict_edges += 0.5
                total_strength += strength

        # 标准化
        max_possible_conflicts = subgraph.number_of_edges()
        if max_possible_conflicts > 0:
            conflict_ratio = conflict_edges / max_possible_conflicts
            avg_strength = total_strength / max_possible_conflicts
            return min(1.0, conflict_ratio * avg_strength)

        return 0.0

    def _calculate_stability_score(self, subgraph: nx.Graph) -> float:
        """计算稳定性分数"""
        if subgraph.number_of_nodes() < 2:
            return 1.0

        # 因素1: 内部连接密度
        density = nx.density(subgraph)

        # 因素2: 聚类系数
        clustering = nx.average_clustering(subgraph)

        # 因素3: 依赖关系比例
        dependency_ratio = 0.0
        if subgraph.number_of_edges() > 0:
            dependency_edges = sum(1 for _, _, data in subgraph.edges(data=True)
                                 if data.get('relation_type') == '依赖')
            dependency_ratio = dependency_edges / subgraph.number_of_edges()

        # 综合稳定性分数
        stability = (density * 0.4 + clustering * 0.3 + dependency_ratio * 0.3)

        return min(1.0, stability)

    def _identify_cross_domain_states(self, graph: nx.Graph) -> List[ConflictState]:
        """识别跨域冲突状态"""
        cross_states = []

        # 获取所有域
        domains = set()
        for node, data in graph.nodes(data=True):
            domains.update(data.get('domains', []))

        # 分析每对域之间的冲突状态
        for domain1, domain2 in itertools.combinations(domains, 2):
            # 找到连接两个域的边
            cross_edges = []
            entities_involved = set()

            for source, target, data in graph.edges(data=True):
                source_domains = graph.nodes[source].get('domains', [])
                target_domains = graph.nodes[target].get('domains', [])

                if domain1 in source_domains and domain2 in target_domains:
                    cross_edges.append((source, target, data))
                    entities_involved.update([source, target])
                elif domain2 in source_domains and domain1 in target_domains:
                    cross_edges.append((source, target, data))
                    entities_involved.update([source, target])

            if cross_edges:
                # 计算跨域冲突强度
                conflict_intensity = 0.0
                for source, target, data in cross_edges:
                    relation_type = data.get('relation_type', '')
                    strength = data.get('strength', 1.0)

                    if relation_type in ['对立', '竞争']:
                        conflict_intensity += strength * 2
                    elif relation_type == '制约':
                        conflict_intensity += strength

                conflict_intensity = min(1.0, conflict_intensity / len(cross_edges))

                # 跨域状态通常不稳定
                stability_score = 0.3

                state = ConflictState(
                    state_id=f"cross_domain_{domain1}_{domain2}",
                    entities_involved=list(entities_involved),
                    conflict_intensity=conflict_intensity,
                    domains_affected=[domain1, domain2],
                    stability_score=stability_score,
                    transition_probabilities={}
                )

                cross_states.append(state)

        return cross_states

    def _build_transition_matrix(self, states: List[ConflictState]) -> np.ndarray:
        """构建状态转换矩阵"""
        n_states = len(states)
        transition_matrix = np.zeros((n_states, n_states))

        for i, state_i in enumerate(states):
            for j, state_j in enumerate(states):
                if i != j:
                    # 计算从状态i到状态j的转换概率
                    transition_prob = self._calculate_transition_probability(state_i, state_j)
                    transition_matrix[i, j] = transition_prob

        # 确保每行和为1（添加自循环）
        for i in range(n_states):
            row_sum = transition_matrix[i, :].sum()
            if row_sum < 1.0:
                transition_matrix[i, i] = 1.0 - row_sum
            elif row_sum > 1.0:
                # 标准化
                transition_matrix[i, :] = transition_matrix[i, :] / row_sum

        return transition_matrix

    def _calculate_transition_probability(self, state_from: ConflictState, state_to: ConflictState) -> float:
        """计算状态转换概率"""
        # 基础转换概率
        base_prob = 0.01

        # 因素1: 冲突强度差异
        intensity_diff = abs(state_to.conflict_intensity - state_from.conflict_intensity)
        intensity_factor = 1.0 - intensity_diff  # 强度相近的状态更容易转换

        # 因素2: 稳定性影响
        stability_factor = 1.0 - state_from.stability_score  # 不稳定的状态更容易转换

        # 因素3: 共同实体数量
        common_entities = set(state_from.entities_involved) & set(state_to.entities_involved)
        entity_overlap = len(common_entities) / max(len(state_from.entities_involved), 1)

        # 因素4: 域重叠
        common_domains = set(state_from.domains_affected) & set(state_to.domains_affected)
        domain_overlap = len(common_domains) / max(len(state_from.domains_affected), 1)

        # 综合转换概率
        transition_prob = base_prob * (
            intensity_factor * 0.3 +
            stability_factor * 0.3 +
            entity_overlap * 0.2 +
            domain_overlap * 0.2
        )

        return min(0.5, transition_prob)  # 限制最大转换概率

    def _calculate_steady_state(self, transition_matrix: np.ndarray) -> np.ndarray:
        """计算稳态分布"""
        try:
            # 计算转换矩阵的特征向量
            eigenvalues, eigenvectors = np.linalg.eig(transition_matrix.T)

            # 找到特征值为1的特征向量
            steady_state_idx = np.argmax(np.real(eigenvalues))
            steady_state = np.real(eigenvectors[:, steady_state_idx])

            # 标准化
            steady_state = steady_state / steady_state.sum()

            return np.abs(steady_state)

        except Exception as e:
            logger.warning(f"稳态分布计算失败: {e}")
            # 返回均匀分布
            n = transition_matrix.shape[0]
            return np.ones(n) / n

    def _identify_escalation_paths(self, states: List[ConflictState],
                                 transition_matrix: np.ndarray) -> List[EscalationPath]:
        """识别升级路径"""
        escalation_paths = []

        # 按冲突强度排序状态
        sorted_states = sorted(enumerate(states), key=lambda x: x[1].conflict_intensity)

        # 识别从低强度到高强度的路径
        for i, (low_idx, low_state) in enumerate(sorted_states[:-1]):
            for j, (high_idx, high_state) in enumerate(sorted_states[i+1:], i+1):
                if high_state.conflict_intensity > low_state.conflict_intensity + 0.2:
                    # 寻找升级路径
                    path = self._find_escalation_path(low_idx, high_idx, states, transition_matrix)

                    if path:
                        # 计算升级概率
                        escalation_prob = self._calculate_escalation_probability(path, transition_matrix)

                        # 估计升级时间
                        time_to_escalation = self._estimate_escalation_time(path, transition_matrix)

                        # 生成缓解策略
                        mitigation_strategies = self._generate_mitigation_strategies(path, states)

                        escalation_path = EscalationPath(
                            path_id=f"escalation_{low_idx}_to_{high_idx}",
                            states=[states[idx] for idx in path],
                            trigger_events=self._identify_trigger_events(path, states),
                            escalation_probability=escalation_prob,
                            time_to_escalation=time_to_escalation,
                            mitigation_strategies=mitigation_strategies
                        )

                        escalation_paths.append(escalation_path)

        # 按升级概率排序
        escalation_paths.sort(key=lambda x: x.escalation_probability, reverse=True)

        return escalation_paths[:20]  # 返回前20条最可能的升级路径

    def _find_escalation_path(self, start_idx: int, end_idx: int,
                            states: List[ConflictState],
                            transition_matrix: np.ndarray) -> Optional[List[int]]:
        """寻找升级路径"""
        # 使用Dijkstra算法寻找最短路径
        import heapq

        n_states = len(states)
        distances = [float('inf')] * n_states
        distances[start_idx] = 0
        previous = [-1] * n_states
        visited = [False] * n_states

        heap = [(0, start_idx)]

        while heap:
            current_dist, current_idx = heapq.heappop(heap)

            if visited[current_idx]:
                continue

            visited[current_idx] = True

            if current_idx == end_idx:
                # 重构路径
                path = []
                idx = end_idx
                while idx != -1:
                    path.append(idx)
                    idx = previous[idx]
                return path[::-1]

            # 检查邻居
            for next_idx in range(n_states):
                if not visited[next_idx] and transition_matrix[current_idx, next_idx] > 0:
                    # 距离为负对数概率
                    edge_weight = -np.log(transition_matrix[current_idx, next_idx])
                    new_dist = current_dist + edge_weight

                    if new_dist < distances[next_idx]:
                        distances[next_idx] = new_dist
                        previous[next_idx] = current_idx
                        heapq.heappush(heap, (new_dist, next_idx))

        return None

    def _calculate_escalation_probability(self, path: List[int],
                                        transition_matrix: np.ndarray) -> float:
        """计算升级概率"""
        if len(path) < 2:
            return 0.0

        # 路径概率为各步转换概率的乘积
        path_prob = 1.0
        for i in range(len(path) - 1):
            path_prob *= transition_matrix[path[i], path[i + 1]]

        return path_prob

    def _estimate_escalation_time(self, path: List[int],
                                transition_matrix: np.ndarray) -> float:
        """估计升级时间"""
        if len(path) < 2:
            return 0.0

        # 基于转换概率估计期望等待时间
        total_time = 0.0
        for i in range(len(path) - 1):
            transition_prob = transition_matrix[path[i], path[i + 1]]
            if transition_prob > 0:
                # 期望等待时间为1/概率（假设泊松过程）
                waiting_time = 1.0 / transition_prob
                total_time += waiting_time

        return total_time

    def _generate_mitigation_strategies(self, path: List[int],
                                      states: List[ConflictState]) -> List[str]:
        """生成缓解策略"""
        strategies = []

        # 分析路径中的关键状态
        for state_idx in path:
            state = states[state_idx]

            # 基于冲突强度的策略
            if state.conflict_intensity > 0.7:
                strategies.append(f"优先处理高强度冲突实体: {', '.join(state.entities_involved[:3])}")

            # 基于稳定性的策略
            if state.stability_score < 0.5:
                strategies.append(f"加强{', '.join(state.domains_affected)}域的稳定性建设")

            # 基于涉及域的策略
            if len(state.domains_affected) > 2:
                strategies.append("建立跨域协调机制，减少多域冲突")

        # 去重并限制数量
        unique_strategies = list(set(strategies))
        return unique_strategies[:5]

    def _identify_trigger_events(self, path: List[int],
                               states: List[ConflictState]) -> List[str]:
        """识别触发事件"""
        trigger_events = []

        for i, state_idx in enumerate(path):
            state = states[state_idx]

            # 基于状态特征推断可能的触发事件
            if state.conflict_intensity > 0.6:
                trigger_events.append(f"阶段{i+1}: 核心冲突实体激活")

            if len(state.domains_affected) > len(states[path[0]].domains_affected):
                trigger_events.append(f"阶段{i+1}: 冲突扩散到新域")

            if state.stability_score < 0.3:
                trigger_events.append(f"阶段{i+1}: 系统稳定性崩溃")

        return trigger_events

    def _identify_critical_transitions(self, states: List[ConflictState],
                                     transition_matrix: np.ndarray) -> List[Tuple[str, str, float]]:
        """识别关键转换"""
        critical_transitions = []

        # 找到高概率转换
        for i in range(len(states)):
            for j in range(len(states)):
                if i != j and transition_matrix[i, j] > 0.1:  # 阈值可调
                    transition_prob = transition_matrix[i, j]
                    from_state = states[i].state_id
                    to_state = states[j].state_id

                    critical_transitions.append((from_state, to_state, transition_prob))

        # 按概率排序
        critical_transitions.sort(key=lambda x: x[2], reverse=True)

        return critical_transitions[:10]

    def analyze_temporal_patterns(self, conflict_events: List[Dict] = None) -> TimeSeriesFeatures:
        """分析时间模式"""
        logger.info("分析冲突时间模式...")

        if conflict_events is None:
            # 生成模拟时间序列数据
            conflict_events = self._generate_simulated_time_series()

        # 转换为时间序列
        df = pd.DataFrame(conflict_events)
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # 基础统计
        if 'intensity' not in df.columns:
            df['intensity'] = np.random.uniform(0, 1, len(df))

        time_series = df['intensity']

        # 趋势分析
        trend = self._analyze_trend(time_series)

        # 季节性分析
        seasonality, periodicity = self._analyze_seasonality(time_series)

        # 波动性分析
        volatility = time_series.std()

        # 平稳性检验
        stationarity = self._test_stationarity(time_series)

        # 预测
        forecast = self._forecast_time_series(time_series)

        features = TimeSeriesFeatures(
            trend=trend,
            seasonality=seasonality,
            periodicity=periodicity,
            volatility=volatility,
            stationarity=stationarity,
            forecast=forecast
        )

        self.time_series_features = features
        logger.info(f"时间模式分析完成: 趋势={trend}, 季节性={seasonality}")

        return features

    def _generate_simulated_time_series(self, n_points: int = 365) -> List[Dict]:
        """生成模拟时间序列数据"""
        events = []
        base_intensity = 0.3

        for i in range(n_points):
            # 添加趋势
            trend_component = 0.001 * i

            # 添加季节性
            seasonal_component = 0.1 * np.sin(2 * np.pi * i / 30)  # 30天周期

            # 添加随机扰动
            noise = np.random.normal(0, 0.05)

            intensity = base_intensity + trend_component + seasonal_component + noise
            intensity = max(0, min(1, intensity))  # 限制在[0,1]

            events.append({
                'day': i,
                'intensity': intensity,
                'events_count': np.random.poisson(intensity * 10)
            })

        return events

    def _analyze_trend(self, time_series: pd.Series) -> str:
        """分析趋势"""
        # 简单线性回归
        x = np.arange(len(time_series))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, time_series.values)

        if p_value < 0.05:  # 显著性检验
            if slope > 0.001:
                return 'increasing'
            elif slope < -0.001:
                return 'decreasing'

        return 'stable'

    def _analyze_seasonality(self, time_series: pd.Series) -> Tuple[bool, Optional[float]]:
        """分析季节性"""
        try:
            if seasonal_decompose and len(time_series) >= 24:
                # 季节性分解
                decomposition = seasonal_decompose(time_series, model='additive', period=30)
                seasonal_component = decomposition.seasonal

                # 检验季节性强度
                seasonal_strength = seasonal_component.std() / time_series.std()

                if seasonal_strength > 0.1:
                    return True, 30.0

            # 简单的周期性检验
            autocorr = [time_series.autocorr(lag=lag) for lag in range(1, min(50, len(time_series)//2))]

            # 寻找显著的自相关
            significant_lags = [i+1 for i, corr in enumerate(autocorr) if abs(corr) > 0.3]

            if significant_lags:
                return True, float(significant_lags[0])

        except Exception as e:
            logger.warning(f"季节性分析失败: {e}")

        return False, None

    def _test_stationarity(self, time_series: pd.Series) -> bool:
        """检验平稳性"""
        try:
            if adfuller:
                result = adfuller(time_series.dropna())
                p_value = result[1]
                return p_value < 0.05  # 拒绝原假设，序列平稳

            # 简单的平稳性检验
            # 检查均值和方差的稳定性
            half_point = len(time_series) // 2
            first_half = time_series.iloc[:half_point]
            second_half = time_series.iloc[half_point:]

            mean_diff = abs(first_half.mean() - second_half.mean())
            var_diff = abs(first_half.var() - second_half.var())

            # 如果均值和方差差异较小，认为是平稳的
            return mean_diff < 0.1 and var_diff < 0.1

        except Exception as e:
            logger.warning(f"平稳性检验失败: {e}")
            return False

    def _forecast_time_series(self, time_series: pd.Series, periods: int = 30) -> np.ndarray:
        """时间序列预测"""
        try:
            if ARIMA and len(time_series) >= 50:
                # ARIMA模型预测
                model = ARIMA(time_series, order=(1, 1, 1))
                fitted_model = model.fit()
                forecast = fitted_model.forecast(steps=periods)
                return forecast.values

            # 简单的移动平均预测
            window_size = min(7, len(time_series) // 4)
            recent_values = time_series.tail(window_size)
            forecast_value = recent_values.mean()

            # 添加随机波动
            noise = np.random.normal(0, recent_values.std() * 0.1, periods)
            forecast = np.full(periods, forecast_value) + noise

            return forecast

        except Exception as e:
            logger.warning(f"时间序列预测失败: {e}")
            # 返回最后一个值的重复
            last_value = time_series.iloc[-1]
            return np.full(periods, last_value)

if __name__ == "__main__":
    # 测试动态分析器
    analyzer = DynamicConflictAnalyzer()

    # 加载数据
    json_path = "/d/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
    analyzer.load_data(json_path=json_path)

    # 构建网络
    analyzer.build_main_network()
    analyzer.detect_communities_advanced()

    # 动态分析
    dynamics = analyzer.build_conflict_state_model()
    time_features = analyzer.analyze_temporal_patterns()

    print("动态冲突分析完成！")
    print(f"识别冲突状态: {len(dynamics.states)} 个")
    print(f"升级路径: {len(dynamics.escalation_paths)} 条")
    print(f"关键转换: {len(dynamics.critical_transitions)} 个")
    print(f"时间趋势: {time_features.trend}")
    print(f"季节性: {time_features.seasonality}")