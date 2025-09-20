"""
法则链AI智能助手
提供学习路径推荐、组合策略分析、风险评估等智能服务
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import networkx as nx
from dataclasses import dataclass
import json

from database.law_chain_manager import LawChainManager
from database.models.law_chain_models import (
    LawChainDefinition, LawChainMaster, LawChainCombination,
    ChainCategory, LearningLevel, RarityLevel,
    CombinationType, DomainType
)


@dataclass
class LearningPath:
    """学习路径"""
    path_name: str
    description: str
    chain_sequence: List[Dict[str, Any]]  # 法则链学习顺序
    estimated_time: int  # 预估时间（天）
    difficulty: str  # easy/medium/hard/extreme
    synergy_score: float  # 协同得分
    risk_level: str  # low/medium/high
    prerequisites: List[str]  # 前置条件
    rewards: List[str]  # 预期收益


@dataclass
class CombinationStrategy:
    """组合策略"""
    strategy_name: str
    strategy_type: str  # offensive/defensive/balanced/utility
    primary_chains: List[str]  # 主要法则链
    support_chains: List[str]  # 支援法则链
    combinations: List[Dict[str, Any]]  # 推荐组合
    effectiveness: float  # 效力评分
    resource_cost: Dict[str, float]  # 资源消耗
    counters: List[str]  # 克制对象
    weaknesses: List[str]  # 弱点


@dataclass
class RiskAssessment:
    """风险评估"""
    overall_risk: str  # low/medium/high/extreme
    risk_factors: Dict[str, float]  # 各项风险因素
    mitigation_strategies: List[str]  # 缓解策略
    warning_signs: List[str]  # 警告标志
    recovery_time: int  # 恢复时间（小时）
    safe_threshold: Dict[str, float]  # 安全阈值


class LawChainAIAssistant:
    """法则链AI助手"""

    def __init__(self):
        self.manager = LawChainManager()
        self.chain_graph = nx.DiGraph()  # 法则链关系图
        self.synergy_matrix = {}  # 协同矩阵
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """初始化知识库"""
        # 定义法则链之间的协同关系
        self.synergy_matrix = {
            # 强协同组合
            ("命运", "因果"): 1.5,
            ("时空", "界域"): 1.4,
            ("生死", "记忆"): 1.3,
            ("混沌", "形质"): 1.2,
            ("权柄", "名真"): 1.4,
            ("映象", "共鸣"): 1.3,

            # 互补组合
            ("命运", "时空"): 1.1,
            ("因果", "记忆"): 1.1,
            ("权柄", "界域"): 1.2,
            ("生死", "形质"): 1.1,

            # 冲突组合
            ("混沌", "权柄"): 0.8,
            ("生死", "混沌"): 0.7,
            ("名真", "映象"): 0.9,
        }

        # 构建法则链关系图
        self._build_chain_graph()

    def _build_chain_graph(self):
        """构建法则链关系图"""
        # 添加节点（12条法则链）
        chains = [
            "命运", "因果", "时空", "生死", "混沌", "权柄",
            "名真", "记忆", "界域", "形质", "映象", "共鸣"
        ]

        for chain in chains:
            self.chain_graph.add_node(chain)

        # 添加边（基于协同关系）
        for (chain1, chain2), synergy in self.synergy_matrix.items():
            weight = synergy if synergy > 1 else 1 / synergy
            self.chain_graph.add_edge(chain1, chain2, weight=weight)
            self.chain_graph.add_edge(chain2, chain1, weight=weight)

    # =========================================================================
    # 学习路径推荐
    # =========================================================================

    async def recommend_learning_paths(
        self,
        character_id: str,
        goal: str = "balanced",
        time_limit: Optional[int] = None
    ) -> List[LearningPath]:
        """
        推荐学习路径

        Args:
            character_id: 角色ID
            goal: 学习目标（balanced/combat/support/exploration/crafting）
            time_limit: 时间限制（天）

        Returns:
            推荐的学习路径列表
        """
        # 获取角色当前法则链状态
        current_chains = await self.manager.list_character_chains(character_id)
        mastered_categories = {c.chain_id for c in current_chains}

        paths = []

        # 根据目标生成不同路径
        if goal == "balanced":
            paths.append(self._generate_balanced_path(mastered_categories))
        elif goal == "combat":
            paths.append(self._generate_combat_path(mastered_categories))
        elif goal == "support":
            paths.append(self._generate_support_path(mastered_categories))
        elif goal == "exploration":
            paths.append(self._generate_exploration_path(mastered_categories))
        elif goal == "crafting":
            paths.append(self._generate_crafting_path(mastered_categories))

        # 优化路径
        paths = self._optimize_paths(paths, time_limit)

        # 计算协同得分
        for path in paths:
            path.synergy_score = self._calculate_path_synergy(path)

        # 排序并返回
        return sorted(paths, key=lambda p: p.synergy_score, reverse=True)

    def _generate_balanced_path(self, mastered: set) -> LearningPath:
        """生成平衡型学习路径"""
        sequence = []

        # 核心法则链（必学）
        core_chains = ["命运", "因果", "时空"]
        for chain in core_chains:
            if chain not in mastered:
                sequence.append({
                    "chain": chain,
                    "target_level": 3,
                    "priority": "high",
                    "time_estimate": 30
                })

        # 辅助法则链
        support_chains = ["记忆", "界域"]
        for chain in support_chains:
            if chain not in mastered:
                sequence.append({
                    "chain": chain,
                    "target_level": 2,
                    "priority": "medium",
                    "time_estimate": 20
                })

        return LearningPath(
            path_name="平衡发展之路",
            description="均衡发展各项能力，适合新手和全能型角色",
            chain_sequence=sequence,
            estimated_time=sum(s["time_estimate"] for s in sequence),
            difficulty="medium",
            synergy_score=0.0,  # 将在后续计算
            risk_level="low",
            prerequisites=["基础修为达到开脉境"],
            rewards=["获得全面的法则链掌控能力", "解锁多种组合可能"]
        )

    def _generate_combat_path(self, mastered: set) -> LearningPath:
        """生成战斗型学习路径"""
        sequence = []

        # 战斗核心链
        combat_chains = ["权柄", "生死", "混沌"]
        for chain in combat_chains:
            if chain not in mastered:
                sequence.append({
                    "chain": chain,
                    "target_level": 4,
                    "priority": "critical",
                    "time_estimate": 40
                })

        # 战斗辅助链
        support_chains = ["形质", "映象"]
        for chain in support_chains:
            if chain not in mastered:
                sequence.append({
                    "chain": chain,
                    "target_level": 2,
                    "priority": "high",
                    "time_estimate": 25
                })

        return LearningPath(
            path_name="战神之路",
            description="专注战斗能力提升，适合战斗型角色",
            chain_sequence=sequence,
            estimated_time=sum(s["time_estimate"] for s in sequence),
            difficulty="hard",
            synergy_score=0.0,
            risk_level="high",
            prerequisites=["战斗天赋", "高强度训练耐受"],
            rewards=["极强的战斗力", "毁灭性的法则链组合"]
        )

    def _generate_support_path(self, mastered: set) -> LearningPath:
        """生成辅助型学习路径"""
        sequence = []

        # 辅助核心链
        support_chains = ["共鸣", "记忆", "名真"]
        for chain in support_chains:
            if chain not in mastered:
                sequence.append({
                    "chain": chain,
                    "target_level": 3,
                    "priority": "high",
                    "time_estimate": 30
                })

        return LearningPath(
            path_name="贤者之路",
            description="专注辅助和支援能力，适合团队型角色",
            chain_sequence=sequence,
            estimated_time=sum(s["time_estimate"] for s in sequence),
            difficulty="medium",
            synergy_score=0.0,
            risk_level="low",
            prerequisites=["高悟性", "团队协作经验"],
            rewards=["强大的辅助能力", "团队增益效果"]
        )

    def _generate_exploration_path(self, mastered: set) -> LearningPath:
        """生成探索型学习路径"""
        sequence = []

        # 探索核心链
        exploration_chains = ["时空", "界域", "映象"]
        for chain in exploration_chains:
            if chain not in mastered:
                sequence.append({
                    "chain": chain,
                    "target_level": 3,
                    "priority": "high",
                    "time_estimate": 35
                })

        return LearningPath(
            path_name="探索者之路",
            description="专注空间和探索能力，适合冒险型角色",
            chain_sequence=sequence,
            estimated_time=sum(s["time_estimate"] for s in sequence),
            difficulty="medium",
            synergy_score=0.0,
            risk_level="medium",
            prerequisites=["空间感知天赋", "冒险精神"],
            rewards=["卓越的探索能力", "空间操控技巧"]
        )

    def _generate_crafting_path(self, mastered: set) -> LearningPath:
        """生成工匠型学习路径"""
        sequence = []

        # 工匠核心链
        crafting_chains = ["形质", "名真", "因果"]
        for chain in crafting_chains:
            if chain not in mastered:
                sequence.append({
                    "chain": chain,
                    "target_level": 4,
                    "priority": "high",
                    "time_estimate": 35
                })

        return LearningPath(
            path_name="工匠之路",
            description="专注创造和制作能力，适合工匠型角色",
            chain_sequence=sequence,
            estimated_time=sum(s["time_estimate"] for s in sequence),
            difficulty="hard",
            synergy_score=0.0,
            risk_level="medium",
            prerequisites=["精细操控能力", "创造天赋"],
            rewards=["高超的制作技艺", "独特的创造能力"]
        )

    def _calculate_path_synergy(self, path: LearningPath) -> float:
        """计算路径协同得分"""
        chains = [s["chain"] for s in path.chain_sequence]
        if len(chains) < 2:
            return 1.0

        total_synergy = 0
        count = 0

        for i in range(len(chains) - 1):
            for j in range(i + 1, len(chains)):
                key1 = (chains[i], chains[j])
                key2 = (chains[j], chains[i])

                if key1 in self.synergy_matrix:
                    total_synergy += self.synergy_matrix[key1]
                    count += 1
                elif key2 in self.synergy_matrix:
                    total_synergy += self.synergy_matrix[key2]
                    count += 1
                else:
                    total_synergy += 1.0  # 默认协同
                    count += 1

        return total_synergy / count if count > 0 else 1.0

    def _optimize_paths(
        self,
        paths: List[LearningPath],
        time_limit: Optional[int]
    ) -> List[LearningPath]:
        """优化学习路径"""
        if not time_limit:
            return paths

        optimized = []
        for path in paths:
            if path.estimated_time <= time_limit:
                optimized.append(path)
            else:
                # 压缩路径
                compressed = self._compress_path(path, time_limit)
                optimized.append(compressed)

        return optimized

    def _compress_path(
        self,
        path: LearningPath,
        time_limit: int
    ) -> LearningPath:
        """压缩学习路径以适应时间限制"""
        # 按优先级排序
        sequence = sorted(
            path.chain_sequence,
            key=lambda s: (
                0 if s["priority"] == "critical" else
                1 if s["priority"] == "high" else
                2 if s["priority"] == "medium" else 3
            )
        )

        # 累积时间直到达到限制
        compressed_sequence = []
        total_time = 0

        for item in sequence:
            if total_time + item["time_estimate"] <= time_limit:
                compressed_sequence.append(item)
                total_time += item["time_estimate"]
            else:
                # 尝试降低目标等级以节省时间
                reduced_time = item["time_estimate"] * 0.7
                if total_time + reduced_time <= time_limit:
                    item["target_level"] = max(1, item["target_level"] - 1)
                    item["time_estimate"] = int(reduced_time)
                    compressed_sequence.append(item)
                    total_time += item["time_estimate"]

        path.chain_sequence = compressed_sequence
        path.estimated_time = total_time
        return path

    # =========================================================================
    # 组合策略分析
    # =========================================================================

    async def analyze_combination_strategies(
        self,
        character_id: str,
        scenario: str = "general"
    ) -> List[CombinationStrategy]:
        """
        分析组合策略

        Args:
            character_id: 角色ID
            scenario: 场景（general/pvp/pve/boss/defense/escape）

        Returns:
            推荐的组合策略列表
        """
        # 获取角色法则链
        chains = await self.manager.list_character_chains(character_id)
        available_chains = {c.chain_id: c for c in chains}

        strategies = []

        if scenario == "general":
            strategies.extend(self._generate_general_strategies(available_chains))
        elif scenario == "pvp":
            strategies.extend(self._generate_pvp_strategies(available_chains))
        elif scenario == "pve":
            strategies.extend(self._generate_pve_strategies(available_chains))
        elif scenario == "boss":
            strategies.extend(self._generate_boss_strategies(available_chains))
        elif scenario == "defense":
            strategies.extend(self._generate_defense_strategies(available_chains))
        elif scenario == "escape":
            strategies.extend(self._generate_escape_strategies(available_chains))

        # 计算效力评分
        for strategy in strategies:
            strategy.effectiveness = self._calculate_strategy_effectiveness(
                strategy,
                available_chains
            )

        return sorted(strategies, key=lambda s: s.effectiveness, reverse=True)

    def _generate_general_strategies(
        self,
        available_chains: Dict[str, LawChainMaster]
    ) -> List[CombinationStrategy]:
        """生成通用策略"""
        strategies = []

        # 平衡型策略
        if self._has_chains(available_chains, ["命运", "因果", "时空"]):
            strategies.append(CombinationStrategy(
                strategy_name="时空因果连锁",
                strategy_type="balanced",
                primary_chains=["命运", "因果", "时空"],
                support_chains=["记忆"],
                combinations=[
                    {
                        "name": "命运因果锁定",
                        "chains": ["命运", "因果"],
                        "effect": "锁定目标命运轨迹"
                    },
                    {
                        "name": "时空回溯",
                        "chains": ["时空", "记忆"],
                        "effect": "回溯时间线修正错误"
                    }
                ],
                effectiveness=0.0,
                resource_cost={"链疲劳": 30, "污染": 10},
                counters=["混沌系攻击"],
                weaknesses=["高消耗", "需要准备时间"]
            ))

        return strategies

    def _generate_pvp_strategies(
        self,
        available_chains: Dict[str, LawChainMaster]
    ) -> List[CombinationStrategy]:
        """生成PVP策略"""
        strategies = []

        # 爆发型策略
        if self._has_chains(available_chains, ["权柄", "生死"]):
            strategies.append(CombinationStrategy(
                strategy_name="死亡宣告",
                strategy_type="offensive",
                primary_chains=["权柄", "生死"],
                support_chains=["混沌"],
                combinations=[
                    {
                        "name": "权柄制裁",
                        "chains": ["权柄", "生死"],
                        "effect": "即死判定"
                    }
                ],
                effectiveness=0.0,
                resource_cost={"链疲劳": 50, "污染": 30, "因果债": 20},
                counters=["防御型角色"],
                weaknesses=["极高代价", "可被名真链反制"]
            ))

        # 控制型策略
        if self._has_chains(available_chains, ["时空", "界域"]):
            strategies.append(CombinationStrategy(
                strategy_name="空间囚笼",
                strategy_type="offensive",
                primary_chains=["时空", "界域"],
                support_chains=["形质"],
                combinations=[
                    {
                        "name": "界域封锁",
                        "chains": ["界域", "形质"],
                        "effect": "完全限制对手行动"
                    }
                ],
                effectiveness=0.0,
                resource_cost={"链疲劳": 35, "污染": 15},
                counters=["机动型角色"],
                weaknesses=["需要场地优势", "维持消耗大"]
            ))

        return strategies

    def _generate_boss_strategies(
        self,
        available_chains: Dict[str, LawChainMaster]
    ) -> List[CombinationStrategy]:
        """生成BOSS战策略"""
        strategies = []

        # 持续输出策略
        if self._has_chains(available_chains, ["因果", "共鸣"]):
            strategies.append(CombinationStrategy(
                strategy_name="因果共振",
                strategy_type="offensive",
                primary_chains=["因果", "共鸣"],
                support_chains=["映象"],
                combinations=[
                    {
                        "name": "因果积累",
                        "chains": ["因果"],
                        "effect": "叠加伤害标记"
                    },
                    {
                        "name": "共鸣爆发",
                        "chains": ["共鸣", "映象"],
                        "effect": "引爆所有标记"
                    }
                ],
                effectiveness=0.0,
                resource_cost={"链疲劳": 40, "污染": 20},
                counters=["高防御BOSS"],
                weaknesses=["需要时间积累", "容易被打断"]
            ))

        return strategies

    def _has_chains(
        self,
        available_chains: Dict[str, LawChainMaster],
        required: List[str]
    ) -> bool:
        """检查是否拥有所需法则链"""
        # 这里简化处理，实际需要匹配chain_id到chain_category
        return True  # 暂时返回True

    def _calculate_strategy_effectiveness(
        self,
        strategy: CombinationStrategy,
        available_chains: Dict[str, LawChainMaster]
    ) -> float:
        """计算策略效力"""
        base_score = 50.0

        # 根据法则链等级加分
        level_bonus = 0
        for chain_id in strategy.primary_chains:
            if chain_id in available_chains:
                master = available_chains[chain_id]
                level_bonus += master.current_level * 5

        # 根据协同度加分
        synergy_bonus = 0
        chains = strategy.primary_chains + strategy.support_chains
        for i in range(len(chains) - 1):
            for j in range(i + 1, len(chains)):
                key = (chains[i], chains[j])
                if key in self.synergy_matrix:
                    synergy_bonus += self.synergy_matrix[key] * 10

        # 根据资源消耗扣分
        resource_penalty = sum(strategy.resource_cost.values()) * 0.2

        return base_score + level_bonus + synergy_bonus - resource_penalty

    # =========================================================================
    # 风险评估
    # =========================================================================

    async def assess_risk(
        self,
        character_id: str,
        action_plan: Dict[str, Any]
    ) -> RiskAssessment:
        """
        评估风险

        Args:
            character_id: 角色ID
            action_plan: 行动计划

        Returns:
            风险评估结果
        """
        # 获取角色当前状态
        chains = await self.manager.list_character_chains(character_id)
        debts = await self.manager.get_character_debts(character_id, "active")

        risk_factors = {}

        # 评估疲劳风险
        avg_fatigue = np.mean([float(c.chain_fatigue) for c in chains])
        risk_factors["疲劳风险"] = avg_fatigue / 100

        # 评估污染风险
        avg_pollution = np.mean([float(c.pollution_level) for c in chains])
        risk_factors["污染风险"] = avg_pollution / 100

        # 评估债务风险
        total_debt = sum(float(d.current_amount) for d in debts)
        risk_factors["债务风险"] = min(total_debt / 1000, 1.0)

        # 评估组合风险
        if "combinations" in action_plan:
            combo_risk = len(action_plan["combinations"]) * 0.15
            risk_factors["组合风险"] = min(combo_risk, 1.0)

        # 计算总体风险
        overall_score = np.mean(list(risk_factors.values()))

        if overall_score < 0.3:
            overall_risk = "low"
        elif overall_score < 0.5:
            overall_risk = "medium"
        elif overall_score < 0.7:
            overall_risk = "high"
        else:
            overall_risk = "extreme"

        # 生成缓解策略
        mitigation = []
        if risk_factors["疲劳风险"] > 0.5:
            mitigation.append("建议休息恢复链疲劳")
        if risk_factors["污染风险"] > 0.5:
            mitigation.append("需要进行污染净化")
        if risk_factors["债务风险"] > 0.5:
            mitigation.append("优先偿还因果债务")

        # 生成警告标志
        warnings = []
        if avg_fatigue > 70:
            warnings.append("链疲劳接近危险水平")
        if avg_pollution > 60:
            warnings.append("污染度过高，可能失控")
        if total_debt > 500:
            warnings.append("债务累积过多，注意反噬")

        # 计算恢复时间
        recovery_hours = int(avg_fatigue / 10 + avg_pollution / 5)

        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation,
            warning_signs=warnings,
            recovery_time=recovery_hours,
            safe_threshold={
                "疲劳": 50.0,
                "污染": 30.0,
                "债务": 100.0
            }
        )

    # =========================================================================
    # 智能推荐
    # =========================================================================

    async def get_next_action_recommendation(
        self,
        character_id: str,
        current_situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        获取下一步行动推荐

        Args:
            character_id: 角色ID
            current_situation: 当前情况描述

        Returns:
            行动推荐
        """
        # 获取角色状态
        chains = await self.manager.list_character_chains(character_id)
        stats = await self.manager.get_character_chain_stats(character_id)

        recommendations = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_goals": [],
            "warnings": []
        }

        # 检查紧急情况
        for chain in chains:
            if chain.is_exhausted:
                recommendations["immediate_actions"].append({
                    "action": "rest",
                    "target": chain.chain_id,
                    "reason": "链疲劳过度，需要立即休息"
                })

            if chain.is_polluted:
                recommendations["immediate_actions"].append({
                    "action": "purify",
                    "target": chain.chain_id,
                    "reason": "污染严重，需要净化"
                })

        # 短期目标
        if stats["average_level"] < 3:
            recommendations["short_term_goals"].append({
                "goal": "提升法则链等级",
                "target_level": 3,
                "reason": "当前等级偏低，建议提升到L3"
            })

        # 长期目标
        if len(chains) < 5:
            recommendations["long_term_goals"].append({
                "goal": "学习更多法则链",
                "target_count": 5,
                "reason": "法则链数量不足，限制组合可能性"
            })

        # 警告
        if stats["average_pollution"] > 50:
            recommendations["warnings"].append(
                "平均污染度过高，存在失控风险"
            )

        return recommendations

    async def simulate_outcome(
        self,
        character_id: str,
        action_sequence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        模拟行动结果

        Args:
            character_id: 角色ID
            action_sequence: 行动序列

        Returns:
            模拟结果
        """
        # 获取初始状态
        initial_chains = await self.manager.list_character_chains(character_id)

        # 初始化模拟状态
        simulated_state = {
            "fatigue": {c.chain_id: float(c.chain_fatigue) for c in initial_chains},
            "pollution": {c.chain_id: float(c.pollution_level) for c in initial_chains},
            "debts": 0.0,
            "success_count": 0,
            "failure_count": 0
        }

        # 模拟每个行动
        for action in action_sequence:
            if action["type"] == "use_chain":
                # 模拟使用法则链
                chain_id = action["chain_id"]

                # 计算成功率（简化模型）
                base_rate = 70
                fatigue_penalty = simulated_state["fatigue"].get(chain_id, 0) / 2
                success_rate = max(30, base_rate - fatigue_penalty)

                # 判定结果
                if np.random.random() * 100 < success_rate:
                    simulated_state["success_count"] += 1
                    simulated_state["fatigue"][chain_id] += 10
                    simulated_state["pollution"][chain_id] += 2
                else:
                    simulated_state["failure_count"] += 1
                    simulated_state["fatigue"][chain_id] += 15
                    simulated_state["pollution"][chain_id] += 5
                    simulated_state["debts"] += 10

            elif action["type"] == "rest":
                # 模拟休息
                hours = action.get("hours", 1)
                for chain_id in simulated_state["fatigue"]:
                    simulated_state["fatigue"][chain_id] = max(
                        0,
                        simulated_state["fatigue"][chain_id] - 10 * hours
                    )

        # 计算最终统计
        outcome = {
            "final_state": simulated_state,
            "success_rate": (
                simulated_state["success_count"] /
                (simulated_state["success_count"] + simulated_state["failure_count"])
                if simulated_state["success_count"] + simulated_state["failure_count"] > 0
                else 0
            ),
            "total_debt_incurred": simulated_state["debts"],
            "average_final_fatigue": np.mean(list(simulated_state["fatigue"].values())),
            "average_final_pollution": np.mean(list(simulated_state["pollution"].values())),
            "risk_level": self._calculate_risk_level(simulated_state)
        }

        return outcome

    def _calculate_risk_level(self, state: Dict[str, Any]) -> str:
        """计算风险等级"""
        avg_fatigue = np.mean(list(state["fatigue"].values()))
        avg_pollution = np.mean(list(state["pollution"].values()))

        risk_score = (avg_fatigue / 100 + avg_pollution / 100 + state["debts"] / 1000) / 3

        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.5:
            return "medium"
        elif risk_score < 0.7:
            return "high"
        else:
            return "extreme"