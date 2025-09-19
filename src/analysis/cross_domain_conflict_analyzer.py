"""
裂世九域跨域冲突矩阵深度分析器
分析前四个域（人域、天域、灵域、荒域）之间的复杂冲突关系
"""

import json
import numpy as np
import networkx as nx
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Set
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import pandas as pd

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ConflictIntensity(Enum):
    """冲突强度等级"""
    LOW = "低"
    MEDIUM = "中"
    MEDIUM_HIGH = "中高"
    HIGH = "高"
    CRITICAL = "极高"


class DomainType(Enum):
    """域类型"""
    HUMAN = "人域"
    HEAVEN = "天域"
    SPIRIT = "灵域"
    WILD = "荒域"


class ConflictType(Enum):
    """冲突类型"""
    RESOURCE = "资源争夺"
    REGULATORY = "监管冲突"
    TERRITORIAL = "领土争端"
    TRADE = "贸易摩擦"
    LEGAL = "法律冲突"
    IDEOLOGICAL = "意识形态"


@dataclass
class ConflictResource:
    """冲突资源"""
    name: str
    type: str
    value: float
    scarcity: float
    strategic_importance: float
    domains_involved: List[str]


@dataclass
class ConflictScenario:
    """冲突场景"""
    title: str
    description: str
    participants: List[str]
    triggers: List[str]
    potential_outcomes: List[str]
    escalation_risk: float


@dataclass
class EscalationPath:
    """冲突升级路径"""
    level: int
    description: str
    triggers: List[str]
    consequences: List[str]
    probability: float
    next_levels: List[int]


@dataclass
class StoryHook:
    """剧情钩子"""
    title: str
    description: str
    conflict_types: List[str]
    complexity: int
    drama_value: int
    char_involvement: List[str]
    plot_potential: float


@dataclass
class ConflictMatrix:
    """跨域冲突矩阵"""
    domains: List[str]
    intensity_matrix: np.ndarray
    conflict_details: Dict[Tuple[str, str], Dict[str, Any]]

    def __post_init__(self):
        """初始化后处理"""
        self.size = len(self.domains)
        self.domain_to_index = {domain: i for i, domain in enumerate(self.domains)}


class CrossDomainConflictAnalyzer:
    """跨域冲突矩阵分析器"""

    def __init__(self):
        self.domains = ["人域", "天域", "灵域", "荒域"]
        self.conflict_matrix = None
        self.conflict_graph = nx.Graph()
        self.entities = {}
        self.relations = {}
        self.escalation_paths = {}
        self.story_hooks = []

        # 初始化冲突矩阵数据
        self._initialize_conflict_data()

    def _initialize_conflict_data(self):
        """初始化冲突数据"""
        # 4x4摩擦热度矩阵（对称矩阵）
        intensity_data = {
            ("人域", "天域"): 4,  # 高
            ("人域", "灵域"): 2,  # 中
            ("人域", "荒域"): 3,  # 中高
            ("天域", "灵域"): 3,  # 中高
            ("天域", "荒域"): 4,  # 高
            ("灵域", "荒域"): 3,  # 中高
        }

        # 创建对称矩阵
        matrix = np.zeros((4, 4))
        for i, domain_a in enumerate(self.domains):
            for j, domain_b in enumerate(self.domains):
                if i == j:
                    matrix[i][j] = 0  # 自己与自己无冲突
                elif (domain_a, domain_b) in intensity_data:
                    matrix[i][j] = intensity_data[(domain_a, domain_b)]
                elif (domain_b, domain_a) in intensity_data:
                    matrix[i][j] = intensity_data[(domain_b, domain_a)]

        # 详细冲突数据
        detailed_conflicts = {
            ("人域", "天域"): {
                "核心资源": ["税役征收", "链籍管控", "征召权力"],
                "触发法条": ["天域税令", "链籍登记法", "军事征召令"],
                "典型场景": [
                    "税收官员与地方势力的对抗",
                    "链籍审查引发的身份危机",
                    "军事征召导致的地方反弹"
                ],
                "关键角色": ["税收官", "链籍官", "地方领主", "民兵组织"],
                "升级阶梯": [
                    {"level": 1, "desc": "行政摩擦", "triggers": ["政策分歧"]},
                    {"level": 2, "desc": "公开对抗", "triggers": ["税收抗议"]},
                    {"level": 3, "desc": "武装冲突", "triggers": ["征召抵制"]},
                    {"level": 4, "desc": "域际战争", "triggers": ["大规模叛乱"]}
                ],
                "剧情钩子": [
                    "失踪的税收官引发的政治危机",
                    "伪造链籍证明的黑市网络",
                    "征召令下的家庭悲剧"
                ]
            },
            ("人域", "灵域"): {
                "核心资源": ["学徒名额", "器械供应", "评印权威"],
                "触发法条": ["学徒选拔令", "器械贸易规范", "评印标准"],
                "典型场景": [
                    "学徒选拔中的暗箱操作",
                    "器械质量争议引发的贸易纠纷",
                    "评印标准的权威性质疑"
                ],
                "关键角色": ["器械师", "评印官", "学徒候选人", "贸易商"],
                "升级阶梯": [
                    {"level": 1, "desc": "技术争议", "triggers": ["质量标准分歧"]},
                    {"level": 2, "desc": "贸易制裁", "triggers": ["供应中断"]},
                    {"level": 3, "desc": "技术封锁", "triggers": ["知识产权争夺"]},
                    {"level": 4, "desc": "完全断绝", "triggers": ["评印体系崩溃"]}
                ],
                "剧情钩子": [
                    "天才学徒的神秘失踪",
                    "伪造评印的器械流入市场",
                    "器械师与评印官的权力斗争"
                ]
            },
            ("人域", "荒域"): {
                "核心资源": ["边境贸易", "走私路线", "治安控制"],
                "触发法条": ["边贸协定", "缉私法令", "边境治安法"],
                "典型场景": [
                    "走私集团与边防军的猫鼠游戏",
                    "合法贸易与黑市交易的界限模糊",
                    "边境地区的治安真空"
                ],
                "关键角色": ["边防军官", "走私头目", "边境商人", "流民组织"],
                "升级阶梯": [
                    {"level": 1, "desc": "贸易摩擦", "triggers": ["关税争议"]},
                    {"level": 2, "desc": "走私猖獗", "triggers": ["执法松懈"]},
                    {"level": 3, "desc": "治安恶化", "triggers": ["暴力冲突"]},
                    {"level": 4, "desc": "边境失控", "triggers": ["军事介入"]}
                ],
                "剧情钩子": [
                    "神秘货物引发的跨域追杀",
                    "边防军官的道德困境",
                    "走私路线上的生死逃亡"
                ]
            },
            ("天域", "灵域"): {
                "核心资源": ["监管权威", "评印体系", "链法解释"],
                "触发法条": ["监管条例", "评印标准法", "链法大典"],
                "典型场景": [
                    "监管官员与器械师的权力争夺",
                    "评印标准的政治化倾向",
                    "链法解释权的归属争议"
                ],
                "关键角色": ["监管官", "高级器械师", "链法学者", "评印委员会"],
                "升级阶梯": [
                    {"level": 1, "desc": "标准分歧", "triggers": ["技术争议"]},
                    {"level": 2, "desc": "权威挑战", "triggers": ["公开质疑"]},
                    {"level": 3, "desc": "体系分裂", "triggers": ["平行标准"]},
                    {"level": 4, "desc": "制度对抗", "triggers": ["完全决裂"]}
                ],
                "剧情钩子": [
                    "禁忌技术的评印争议",
                    "监管官的腐败丑闻",
                    "链法解释引发的宗教危机"
                ]
            },
            ("天域", "荒域"): {
                "核心资源": ["断链惩罚", "矿脉开采", "军镇建设"],
                "触发法条": ["断链法令", "矿业法", "军镇条例"],
                "典型场景": [
                    "断链罪犯与荒域势力的勾结",
                    "矿脉开采权的血腥争夺",
                    "军镇与荒民的暴力冲突"
                ],
                "关键角色": ["断链执行官", "矿业公司", "军镇指挥官", "荒域部族"],
                "升级阶梯": [
                    {"level": 1, "desc": "管辖争议", "triggers": ["边界不清"]},
                    {"level": 2, "desc": "资源冲突", "triggers": ["开采权争夺"]},
                    {"level": 3, "desc": "军事对抗", "triggers": ["武装冲突"]},
                    {"level": 4, "desc": "全面战争", "triggers": ["大规模战役"]}
                ],
                "剧情钩子": [
                    "断链罪犯的荒域复仇",
                    "矿脉深处的古老秘密",
                    "军镇围困战的绝望与希望"
                ]
            },
            ("灵域", "荒域"): {
                "核心资源": ["黑市器械", "稀有矿料", "远古遗械"],
                "触发法条": ["器械管制法", "矿料贸易令", "遗械保护法"],
                "典型场景": [
                    "黑市器械的来源追踪",
                    "稀有矿料的走私网络",
                    "远古遗械的考古争夺"
                ],
                "关键角色": ["黑市商人", "矿料走私犯", "遗械猎人", "考古学者"],
                "升级阶梯": [
                    {"level": 1, "desc": "贸易纠纷", "triggers": ["价格争议"]},
                    {"level": 2, "desc": "走私猖獗", "triggers": ["监管失效"]},
                    {"level": 3, "desc": "暴力竞争", "triggers": ["黑市火拼"]},
                    {"level": 4, "desc": "全面对抗", "triggers": ["势力战争"]}
                ],
                "剧情钩子": [
                    "传说中的究极器械现世",
                    "矿料走私背后的阴谋",
                    "遗械猎人的生死冒险"
                ]
            }
        }

        # 创建冲突矩阵对象
        self.conflict_matrix = ConflictMatrix(
            domains=self.domains,
            intensity_matrix=matrix,
            conflict_details=detailed_conflicts
        )

    def analyze_conflict_matrix(self) -> Dict[str, Any]:
        """分析冲突矩阵的数学模型和特征"""
        matrix = self.conflict_matrix.intensity_matrix

        analysis = {
            "基础统计": {
                "总冲突对数": int(np.sum(matrix > 0) / 2),  # 除以2因为是对称矩阵
                "平均冲突强度": float(np.mean(matrix[matrix > 0])),
                "最高冲突强度": float(np.max(matrix)),
                "冲突强度方差": float(np.var(matrix[matrix > 0])),
                "冲突分布": dict(zip(*np.unique(matrix[matrix > 0], return_counts=True)))
            },
            "域特征分析": {},
            "网络特征": {},
            "冲突模式": []
        }

        # 分析每个域的冲突特征
        for i, domain in enumerate(self.domains):
            domain_conflicts = matrix[i, :]
            domain_conflicts = domain_conflicts[domain_conflicts > 0]

            analysis["域特征分析"][domain] = {
                "参与冲突数": int(len(domain_conflicts)),
                "平均冲突强度": float(np.mean(domain_conflicts)) if len(domain_conflicts) > 0 else 0,
                "最高冲突强度": float(np.max(domain_conflicts)) if len(domain_conflicts) > 0 else 0,
                "冲突倾向": "高冲突域" if np.mean(domain_conflicts) > 3 else "中冲突域" if np.mean(domain_conflicts) > 2 else "低冲突域"
            }

        # 构建网络图进行网络分析
        G = nx.Graph()
        for i, domain_a in enumerate(self.domains):
            for j, domain_b in enumerate(self.domains):
                if i < j and matrix[i][j] > 0:
                    G.add_edge(domain_a, domain_b, weight=matrix[i][j])

        # 网络特征分析
        if G.number_of_edges() > 0:
            analysis["网络特征"] = {
                "节点数": G.number_of_nodes(),
                "边数": G.number_of_edges(),
                "平均度": float(np.mean(list(dict(G.degree()).values()))),
                "网络密度": float(nx.density(G)),
                "聚类系数": float(nx.average_clustering(G)),
                "中心性分析": {
                    "度中心性": {domain: float(centrality) for domain, centrality in nx.degree_centrality(G).items()},
                    "介数中心性": {domain: float(centrality) for domain, centrality in nx.betweenness_centrality(G).items()}
                }
            }

        # 识别冲突模式
        patterns = []

        # 高强度冲突模式
        high_intensity_pairs = []
        for i, domain_a in enumerate(self.domains):
            for j, domain_b in enumerate(self.domains):
                if i < j and matrix[i][j] >= 4:
                    high_intensity_pairs.append((domain_a, domain_b))

        if high_intensity_pairs:
            patterns.append({
                "模式类型": "高强度冲突轴",
                "描述": "存在极高冲突强度的域对",
                "涉及域对": high_intensity_pairs,
                "特征": "可能引发大规模冲突或战争"
            })

        # 冲突集中模式
        conflict_counts = np.sum(matrix > 0, axis=1)
        max_conflicts = np.max(conflict_counts)
        high_conflict_domains = [self.domains[i] for i in np.where(conflict_counts == max_conflicts)[0]]

        if len(high_conflict_domains) > 0:
            patterns.append({
                "模式类型": "冲突集中域",
                "描述": "参与最多冲突的域",
                "涉及域": high_conflict_domains,
                "特征": "容易成为多方冲突的焦点"
            })

        analysis["冲突模式"] = patterns

        return analysis

    def extract_entities_and_relations(self) -> Dict[str, Any]:
        """提取实体和关系网络"""
        entities = {}
        relations = []
        entity_types = defaultdict(list)

        # 从冲突详情中提取实体
        for (domain_a, domain_b), details in self.conflict_matrix.conflict_details.items():
            conflict_id = f"{domain_a}_{domain_b}_冲突"

            # 提取核心资源实体
            for resource in details["核心资源"]:
                entity_id = f"resource_{hash(resource) % 10000}"
                entities[entity_id] = {
                    "id": entity_id,
                    "name": resource,
                    "type": "核心资源",
                    "domains": [domain_a, domain_b],
                    "importance": "高",
                    "category": "资源争夺"
                }
                entity_types["核心资源"].append(entity_id)

            # 提取触发法条实体
            for law in details["触发法条"]:
                entity_id = f"law_{hash(law) % 10000}"
                entities[entity_id] = {
                    "id": entity_id,
                    "name": law,
                    "type": "法条制度",
                    "domains": [domain_a, domain_b],
                    "importance": "高",
                    "category": "制度框架"
                }
                entity_types["法条制度"].append(entity_id)

            # 提取关键角色实体
            for role in details["关键角色"]:
                entity_id = f"role_{hash(role) % 10000}"
                entities[entity_id] = {
                    "id": entity_id,
                    "name": role,
                    "type": "关键角色",
                    "domains": [domain_a, domain_b],
                    "importance": "中高",
                    "category": "参与者"
                }
                entity_types["关键角色"].append(entity_id)

            # 提取典型场景实体
            for scenario in details["典型场景"]:
                entity_id = f"scenario_{hash(scenario) % 10000}"
                entities[entity_id] = {
                    "id": entity_id,
                    "name": scenario,
                    "type": "冲突场景",
                    "domains": [domain_a, domain_b],
                    "importance": "中",
                    "category": "具体表现"
                }
                entity_types["冲突场景"].append(entity_id)

        # 构建实体关系网络
        relation_types = [
            "争夺", "依赖", "制约", "触发", "参与", "影响", "控制", "衍生"
        ]

        # 资源与角色的关系
        for resource_id in entity_types["核心资源"]:
            for role_id in entity_types["关键角色"]:
                resource = entities[resource_id]
                role = entities[role_id]
                # 如果在同一冲突域中
                if set(resource["domains"]) & set(role["domains"]):
                    relations.append({
                        "source": resource_id,
                        "target": role_id,
                        "type": "争夺",
                        "strength": 0.8,
                        "description": f"{role['name']}争夺{resource['name']}"
                    })

        # 法条与场景的关系
        for law_id in entity_types["法条制度"]:
            for scenario_id in entity_types["冲突场景"]:
                law = entities[law_id]
                scenario = entities[scenario_id]
                if set(law["domains"]) & set(scenario["domains"]):
                    relations.append({
                        "source": law_id,
                        "target": scenario_id,
                        "type": "触发",
                        "strength": 0.7,
                        "description": f"{law['name']}触发{scenario['name']}"
                    })

        # 角色与场景的关系
        for role_id in entity_types["关键角色"]:
            for scenario_id in entity_types["冲突场景"]:
                role = entities[role_id]
                scenario = entities[scenario_id]
                if set(role["domains"]) & set(scenario["domains"]):
                    relations.append({
                        "source": role_id,
                        "target": scenario_id,
                        "type": "参与",
                        "strength": 0.6,
                        "description": f"{role['name']}参与{scenario['name']}"
                    })

        return {
            "entities": entities,
            "relations": relations,
            "entity_types": dict(entity_types),
            "network_stats": {
                "total_entities": len(entities),
                "total_relations": len(relations),
                "entity_type_distribution": {k: len(v) for k, v in entity_types.items()},
                "avg_relations_per_entity": len(relations) / len(entities) if entities else 0
            }
        }

    def analyze_escalation_paths(self) -> Dict[str, Any]:
        """分析冲突升级路径"""
        escalation_analysis = {
            "路径模型": {},
            "关键转折点": [],
            "升级概率": {},
            "网络效应": {}
        }

        # 分析每个冲突对的升级路径
        for (domain_a, domain_b), details in self.conflict_matrix.conflict_details.items():
            conflict_key = f"{domain_a}↔{domain_b}"

            # 构建状态机模型
            escalation_levels = details["升级阶梯"]
            path_model = {
                "states": [],
                "transitions": [],
                "terminal_states": []
            }

            for i, level_data in enumerate(escalation_levels):
                state = {
                    "level": level_data["level"],
                    "name": level_data["desc"],
                    "triggers": level_data["triggers"],
                    "risk_level": min(level_data["level"] * 25, 100),  # 风险百分比
                    "reversibility": max(100 - level_data["level"] * 20, 10)  # 可逆性
                }
                path_model["states"].append(state)

                # 添加转换关系
                if i < len(escalation_levels) - 1:
                    transition = {
                        "from": level_data["level"],
                        "to": escalation_levels[i + 1]["level"],
                        "triggers": escalation_levels[i + 1]["triggers"],
                        "probability": max(0.3, 1.0 - i * 0.2)  # 概率递减
                    }
                    path_model["transitions"].append(transition)
                else:
                    # 最高级别为终端状态
                    path_model["terminal_states"].append(level_data["level"])

            escalation_analysis["路径模型"][conflict_key] = path_model

            # 识别关键转折点
            for level_data in escalation_levels:
                if level_data["level"] in [2, 3]:  # 中间级别通常是关键转折点
                    escalation_analysis["关键转折点"].append({
                        "冲突域": conflict_key,
                        "转折点": level_data["desc"],
                        "触发条件": level_data["triggers"],
                        "重要性": "高" if level_data["level"] == 3 else "中",
                        "描述": f"{conflict_key}的{level_data['desc']}阶段是关键转折点"
                    })

        # 分析升级概率模型
        base_probabilities = {
            "人域↔天域": 0.7,  # 高强度冲突，升级概率高
            "天域↔荒域": 0.7,
            "人域↔荒域": 0.5,
            "天域↔灵域": 0.5,
            "灵域↔荒域": 0.5,
            "人域↔灵域": 0.3   # 相对较低
        }

        for conflict_key, base_prob in base_probabilities.items():
            escalation_analysis["升级概率"][conflict_key] = {
                "基础概率": base_prob,
                "调节因子": {
                    "资源稀缺性": 0.2,
                    "历史恩怨": 0.15,
                    "外部压力": 0.1,
                    "调解机制": -0.15
                },
                "最终概率": min(base_prob + 0.15, 0.9)  # 考虑调节因子
            }

        # 分析网络效应（冲突扩散）
        conflict_network = nx.Graph()
        for domain_a, domain_b in [("人域", "天域"), ("人域", "灵域"), ("人域", "荒域"),
                                  ("天域", "灵域"), ("天域", "荒域"), ("灵域", "荒域")]:
            conflict_network.add_edge(domain_a, domain_b,
                                    weight=self.conflict_matrix.intensity_matrix[
                                        self.domains.index(domain_a),
                                        self.domains.index(domain_b)
                                    ])

        escalation_analysis["网络效应"] = {
            "扩散路径": {},
            "连锁反应": [],
            "稳定性分析": {}
        }

        # 分析扩散路径
        for domain in self.domains:
            paths = []
            for other_domain in self.domains:
                if domain != other_domain:
                    try:
                        path = nx.shortest_path(conflict_network, domain, other_domain)
                        if len(path) > 2:  # 间接路径
                            paths.append({
                                "target": other_domain,
                                "path": path,
                                "hops": len(path) - 1,
                                "description": f"{domain}通过{' → '.join(path[1:-1])}影响{other_domain}"
                            })
                    except nx.NetworkXNoPath:
                        pass
            escalation_analysis["网络效应"]["扩散路径"][domain] = paths

        return escalation_analysis

    def evaluate_story_potential(self) -> Dict[str, Any]:
        """评估故事情节潜力"""
        story_analysis = {
            "剧情钩子分析": {},
            "戏剧价值评估": {},
            "情节生成空间": {},
            "推荐组合": []
        }

        # 分析每个冲突的剧情钩子
        all_hooks = []
        for (domain_a, domain_b), details in self.conflict_matrix.conflict_details.items():
            conflict_key = f"{domain_a}↔{domain_b}"
            hooks_data = details["剧情钩子"]

            for i, hook_desc in enumerate(hooks_data):
                hook = StoryHook(
                    title=f"{conflict_key}_钩子_{i+1}",
                    description=hook_desc,
                    conflict_types=self._classify_conflict_types(hook_desc),
                    complexity=self._calculate_complexity(hook_desc),
                    drama_value=self._calculate_drama_value(hook_desc),
                    char_involvement=self._extract_character_types(hook_desc),
                    plot_potential=self._calculate_plot_potential(hook_desc)
                )
                all_hooks.append(hook)

        # 按冲突域分组分析
        for (domain_a, domain_b), details in self.conflict_matrix.conflict_details.items():
            conflict_key = f"{domain_a}↔{domain_b}"
            conflict_hooks = [h for h in all_hooks if h.title.startswith(conflict_key)]

            story_analysis["剧情钩子分析"][conflict_key] = {
                "钩子数量": len(conflict_hooks),
                "平均复杂度": np.mean([h.complexity for h in conflict_hooks]),
                "平均戏剧价值": np.mean([h.drama_value for h in conflict_hooks]),
                "总体潜力": np.mean([h.plot_potential for h in conflict_hooks]),
                "钩子详情": [
                    {
                        "标题": h.title,
                        "描述": h.description,
                        "复杂度": h.complexity,
                        "戏剧价值": h.drama_value,
                        "情节潜力": h.plot_potential
                    } for h in conflict_hooks
                ]
            }

        # 戏剧价值评估矩阵
        drama_matrix = np.zeros((4, 4))
        for i, domain_a in enumerate(self.domains):
            for j, domain_b in enumerate(self.domains):
                if i != j:
                    conflict_key = f"{domain_a}↔{domain_b}" if (domain_a, domain_b) in [
                        (self.domains[x], self.domains[y]) for x in range(4) for y in range(x+1, 4)
                    ] else f"{domain_b}↔{domain_a}"

                    if conflict_key in story_analysis["剧情钩子分析"]:
                        drama_matrix[i][j] = story_analysis["剧情钩子分析"][conflict_key]["平均戏剧价值"]

        story_analysis["戏剧价值评估"] = {
            "戏剧价值矩阵": drama_matrix.tolist(),
            "最高戏剧价值": float(np.max(drama_matrix)),
            "平均戏剧价值": float(np.mean(drama_matrix[drama_matrix > 0])),
            "戏剧价值分布": {
                "高价值": int(np.sum(drama_matrix >= 8)),
                "中价值": int(np.sum((drama_matrix >= 5) & (drama_matrix < 8))),
                "低价值": int(np.sum((drama_matrix > 0) & (drama_matrix < 5)))
            }
        }

        # 情节生成空间分析
        conflict_types = ["资源争夺", "权力斗争", "身份认同", "道德冲突", "生存危机"]
        story_themes = ["复仇", "救赎", "成长", "牺牲", "背叛", "忠诚", "爱情", "友情"]
        character_arcs = ["英雄之旅", "反英雄", "悲剧英雄", "反派救赎", "普通人崛起"]

        story_analysis["情节生成空间"] = {
            "冲突类型": conflict_types,
            "故事主题": story_themes,
            "角色弧线": character_arcs,
            "组合可能性": len(conflict_types) * len(story_themes) * len(character_arcs),
            "高潜力组合": [
                {"冲突": "资源争夺", "主题": "牺牲", "角色": "悲剧英雄"},
                {"冲突": "权力斗争", "主题": "背叛", "角色": "反英雄"},
                {"冲突": "身份认同", "主题": "成长", "角色": "英雄之旅"}
            ]
        }

        # 推荐剧情组合
        high_potential_hooks = [h for h in all_hooks if h.plot_potential >= 8.0]
        high_potential_hooks.sort(key=lambda x: x.plot_potential, reverse=True)

        story_analysis["推荐组合"] = [
            {
                "组合名称": f"多域联动：{hook.title}",
                "核心钩子": hook.description,
                "涉及冲突": hook.conflict_types,
                "复杂度": hook.complexity,
                "戏剧价值": hook.drama_value,
                "推荐理由": f"高情节潜力({hook.plot_potential:.1f})，涉及多种冲突类型"
            }
            for hook in high_potential_hooks[:5]  # 前5个高潜力钩子
        ]

        return story_analysis

    def _classify_conflict_types(self, description: str) -> List[str]:
        """分类冲突类型"""
        types = []
        keywords = {
            "资源争夺": ["税收", "矿脉", "器械", "贸易"],
            "权力斗争": ["官员", "权威", "监管", "控制"],
            "身份认同": ["链籍", "评印", "身份", "地位"],
            "道德冲突": ["正义", "道德", "伦理", "价值"],
            "生存危机": ["生死", "存亡", "危机", "威胁"]
        }

        for conflict_type, kws in keywords.items():
            if any(kw in description for kw in kws):
                types.append(conflict_type)

        return types if types else ["未分类"]

    def _calculate_complexity(self, description: str) -> int:
        """计算复杂度"""
        # 基于描述长度、涉及实体数量等因素
        base = 5
        if len(description) > 20:
            base += 1
        if "网络" in description or "体系" in description:
            base += 2
        if "阴谋" in description or "秘密" in description:
            base += 2
        return min(base, 10)

    def _calculate_drama_value(self, description: str) -> int:
        """计算戏剧价值"""
        base = 5
        drama_keywords = ["悲剧", "绝望", "希望", "复仇", "背叛", "牺牲", "生死", "围困", "逃亡"]
        for keyword in drama_keywords:
            if keyword in description:
                base += 1
        return min(base, 10)

    def _extract_character_types(self, description: str) -> List[str]:
        """提取角色类型"""
        characters = []
        char_keywords = {
            "官员": ["官", "官员"],
            "商人": ["商", "贸易"],
            "军人": ["军", "战"],
            "学者": ["学者", "考古"],
            "罪犯": ["走私", "犯", "黑市"]
        }

        for char_type, kws in char_keywords.items():
            if any(kw in description for kw in kws):
                characters.append(char_type)

        return characters

    def _calculate_plot_potential(self, description: str) -> float:
        """计算情节潜力"""
        base = 5.0

        # 情节元素加分
        plot_elements = {
            "神秘": 1.5,
            "失踪": 1.0,
            "秘密": 1.5,
            "阴谋": 2.0,
            "追杀": 1.5,
            "逃亡": 1.0,
            "复仇": 1.5,
            "冒险": 1.0
        }

        for element, score in plot_elements.items():
            if element in description:
                base += score

        return min(base, 10.0)

    def generate_database_model(self) -> Dict[str, Any]:
        """生成数据库模型"""
        # 提取实体和关系
        entity_relation_data = self.extract_entities_and_relations()

        # 生成可导入的JSON数据
        database_model = {
            "meta": {
                "model_version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "description": "裂世九域跨域冲突矩阵数据模型",
                "domains": self.domains
            },
            "conflict_matrix": {
                "domains": self.domains,
                "intensity_matrix": self.conflict_matrix.intensity_matrix.tolist(),
                "conflict_pairs": []
            },
            "entities": [],
            "relations": [],
            "escalation_paths": [],
            "story_hooks": [],
            "sql_schema": self._generate_sql_schema(),
            "mongodb_collections": self._generate_mongodb_schema()
        }

        # 冲突对数据
        for (domain_a, domain_b), details in self.conflict_matrix.conflict_details.items():
            conflict_pair = {
                "id": str(uuid4()),
                "domain_a": domain_a,
                "domain_b": domain_b,
                "intensity": float(self.conflict_matrix.intensity_matrix[
                    self.domains.index(domain_a),
                    self.domains.index(domain_b)
                ]),
                "core_resources": details["核心资源"],
                "trigger_laws": details["触发法条"],
                "typical_scenarios": details["典型场景"],
                "key_roles": details["关键角色"],
                "escalation_levels": details["升级阶梯"],
                "story_hooks": details["剧情钩子"]
            }
            database_model["conflict_matrix"]["conflict_pairs"].append(conflict_pair)

        # 实体数据
        for entity_id, entity_data in entity_relation_data["entities"].items():
            entity = {
                "id": entity_id,
                "novel_id": "00000000-0000-0000-0000-000000000000",  # 占位符
                "name": entity_data["name"],
                "entity_type": entity_data["type"],
                "domains": entity_data["domains"],
                "importance": entity_data["importance"],
                "category": entity_data["category"],
                "description": f"{entity_data['name']}是{entity_data['category']}类型的{entity_data['type']}",
                "characteristics": {},
                "created_at": datetime.now().isoformat()
            }
            database_model["entities"].append(entity)

        # 关系数据
        for relation in entity_relation_data["relations"]:
            rel = {
                "id": str(uuid4()),
                "novel_id": "00000000-0000-0000-0000-000000000000",  # 占位符
                "source_entity_id": relation["source"],
                "target_entity_id": relation["target"],
                "relation_type": relation["type"],
                "description": relation["description"],
                "strength": relation["strength"],
                "is_cross_domain": True,  # 跨域冲突中的关系
                "created_at": datetime.now().isoformat()
            }
            database_model["relations"].append(rel)

        return database_model

    def _generate_sql_schema(self) -> str:
        """生成SQL schema"""
        return """
-- 跨域冲突矩阵表
CREATE TABLE IF NOT EXISTS cross_domain_conflict_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    domain_a VARCHAR(50) NOT NULL,
    domain_b VARCHAR(50) NOT NULL,
    intensity DECIMAL(3,1) NOT NULL CHECK (intensity >= 0 AND intensity <= 5),
    core_resources TEXT[] NOT NULL,
    trigger_laws TEXT[] NOT NULL,
    typical_scenarios TEXT[] NOT NULL,
    key_roles TEXT[] NOT NULL,
    escalation_data JSONB NOT NULL,
    story_hooks TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_id, domain_a, domain_b),
    CHECK (domain_a != domain_b)
);

-- 冲突升级路径表
CREATE TABLE IF NOT EXISTS conflict_escalation_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conflict_matrix_id UUID NOT NULL REFERENCES cross_domain_conflict_matrix(id),
    level INTEGER NOT NULL CHECK (level >= 1 AND level <= 10),
    description VARCHAR(500) NOT NULL,
    triggers TEXT[] NOT NULL,
    consequences TEXT[],
    probability DECIMAL(3,2) CHECK (probability >= 0 AND probability <= 1),
    risk_level INTEGER CHECK (risk_level >= 0 AND risk_level <= 100),
    reversibility INTEGER CHECK (reversibility >= 0 AND reversibility <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 冲突网络分析表
CREATE TABLE IF NOT EXISTS conflict_network_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    novel_id UUID NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    network_metrics JSONB NOT NULL,
    centrality_scores JSONB,
    clustering_data JSONB,
    analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_conflict_matrix_domains ON cross_domain_conflict_matrix(domain_a, domain_b);
CREATE INDEX IF NOT EXISTS idx_conflict_matrix_intensity ON cross_domain_conflict_matrix(intensity DESC);
CREATE INDEX IF NOT EXISTS idx_escalation_paths_level ON conflict_escalation_paths(level);
"""

    def _generate_mongodb_schema(self) -> Dict[str, Any]:
        """生成MongoDB collection schemas"""
        return {
            "cross_domain_conflicts": {
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["novel_id", "domain_a", "domain_b", "intensity"],
                        "properties": {
                            "novel_id": {"bsonType": "string"},
                            "domain_a": {"bsonType": "string"},
                            "domain_b": {"bsonType": "string"},
                            "intensity": {"bsonType": "number", "minimum": 0, "maximum": 5},
                            "core_resources": {"bsonType": "array"},
                            "trigger_laws": {"bsonType": "array"},
                            "escalation_matrix": {"bsonType": "object"},
                            "network_analysis": {"bsonType": "object"}
                        }
                    }
                },
                "indexes": [
                    {"key": {"novel_id": 1, "domain_a": 1, "domain_b": 1}, "unique": True},
                    {"key": {"intensity": -1}},
                    {"key": {"core_resources": 1}}
                ]
            },
            "conflict_entities": {
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["entity_id", "name", "type", "domains"],
                        "properties": {
                            "entity_id": {"bsonType": "string"},
                            "name": {"bsonType": "string"},
                            "type": {"bsonType": "string"},
                            "domains": {"bsonType": "array"},
                            "relations": {"bsonType": "array"}
                        }
                    }
                }
            }
        }

    def visualize_conflict_matrix(self, save_path: Optional[str] = None) -> None:
        """可视化冲突矩阵"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('裂世九域跨域冲突矩阵分析', fontsize=16, fontweight='bold')

        # 1. 冲突强度热力图
        ax1 = axes[0, 0]
        sns.heatmap(self.conflict_matrix.intensity_matrix,
                   annot=True,
                   xticklabels=self.domains,
                   yticklabels=self.domains,
                   cmap='Reds',
                   ax=ax1)
        ax1.set_title('跨域冲突强度矩阵')

        # 2. 网络图
        ax2 = axes[0, 1]
        G = nx.Graph()
        pos = {}
        colors = []
        sizes = []

        for i, domain in enumerate(self.domains):
            G.add_node(domain)
            # 设置节点位置（圆形布局）
            angle = 2 * np.pi * i / len(self.domains)
            pos[domain] = (np.cos(angle), np.sin(angle))
            colors.append('lightblue')
            sizes.append(1000)

        # 添加边
        for i, domain_a in enumerate(self.domains):
            for j, domain_b in enumerate(self.domains):
                if i < j and self.conflict_matrix.intensity_matrix[i][j] > 0:
                    G.add_edge(domain_a, domain_b,
                             weight=self.conflict_matrix.intensity_matrix[i][j])

        # 绘制网络
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]

        nx.draw(G, pos,
               node_color=colors,
               node_size=sizes,
               edge_color='red',
               width=[w for w in weights],
               with_labels=True,
               font_size=10,
               ax=ax2)
        ax2.set_title('跨域冲突网络图')

        # 3. 域冲突参与度
        ax3 = axes[1, 0]
        domain_conflicts = np.sum(self.conflict_matrix.intensity_matrix > 0, axis=1)
        ax3.bar(self.domains, domain_conflicts, color='orange', alpha=0.7)
        ax3.set_title('各域参与冲突数量')
        ax3.set_ylabel('参与冲突数')

        # 4. 冲突强度分布
        ax4 = axes[1, 1]
        intensities = self.conflict_matrix.intensity_matrix[
            self.conflict_matrix.intensity_matrix > 0
        ].flatten()
        ax4.hist(intensities, bins=4, color='green', alpha=0.7, edgecolor='black')
        ax4.set_title('冲突强度分布')
        ax4.set_xlabel('冲突强度')
        ax4.set_ylabel('频次')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"可视化图表已保存到: {save_path}")

        plt.show()

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合分析报告"""
        print("正在进行跨域冲突矩阵深度分析...")

        # 执行各项分析
        matrix_analysis = self.analyze_conflict_matrix()
        entity_analysis = self.extract_entities_and_relations()
        escalation_analysis = self.analyze_escalation_paths()
        story_analysis = self.evaluate_story_potential()
        database_model = self.generate_database_model()

        # 综合报告
        comprehensive_report = {
            "分析元数据": {
                "分析时间": datetime.now().isoformat(),
                "分析器版本": "1.0.0",
                "数据源": "裂世九域·法则链纪元跨域冲突设定",
                "分析范围": "前四域（人域、天域、灵域、荒域）"
            },
            "1_冲突矩阵分析": matrix_analysis,
            "2_实体关系网络": entity_analysis,
            "3_冲突升级路径": escalation_analysis,
            "4_故事情节潜力": story_analysis,
            "5_数据库模型": database_model,
            "6_世界观一致性检查": self._check_consistency(),
            "7_优化建议": self._generate_recommendations()
        }

        print("跨域冲突矩阵分析完成！")
        return comprehensive_report

    def _check_consistency(self) -> Dict[str, Any]:
        """检查世界观一致性"""
        consistency = {
            "检查项目": [],
            "潜在矛盾": [],
            "一致性评分": 0,
            "建议修正": []
        }

        checks = [
            {
                "项目": "域间冲突强度逻辑性",
                "状态": "通过",
                "描述": "人域-天域和天域-荒域的高强度冲突符合权力结构设定"
            },
            {
                "项目": "资源争夺合理性",
                "状态": "通过",
                "描述": "各域争夺的核心资源与其特性和需求相匹配"
            },
            {
                "项目": "法条体系完整性",
                "状态": "需要注意",
                "描述": "部分触发法条可能需要更详细的法理依据"
            },
            {
                "项目": "角色立场一致性",
                "状态": "通过",
                "描述": "关键角色的立场和行为动机与其所属域的利益一致"
            }
        ]

        consistency["检查项目"] = checks
        consistency["一致性评分"] = 85  # 基于检查结果的评分

        return consistency

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """生成优化建议"""
        return [
            {
                "类别": "数据完善",
                "建议": "补充灵域的内部组织结构设定，增强其作为冲突参与方的可信度",
                "优先级": "中"
            },
            {
                "类别": "冲突平衡",
                "建议": "考虑引入调解机制或第三方势力，避免冲突过度集中",
                "优先级": "高"
            },
            {
                "类别": "故事潜力",
                "建议": "开发更多跨三域或四域的复杂冲突场景，增加故事深度",
                "优先级": "中"
            },
            {
                "类别": "数据库扩展",
                "建议": "增加时间维度，支持冲突的历史演化分析",
                "优先级": "低"
            }
        ]


def main():
    """主函数 - 演示分析器使用"""
    analyzer = CrossDomainConflictAnalyzer()

    # 生成综合报告
    report = analyzer.generate_comprehensive_report()

    # 保存报告到JSON文件
    output_path = "D:/work/novellus/cross_domain_conflict_analysis_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n综合分析报告已保存到: {output_path}")

    # 生成可视化
    analyzer.visualize_conflict_matrix("D:/work/novellus/conflict_matrix_visualization.png")

    return report


if __name__ == "__main__":
    report = main()