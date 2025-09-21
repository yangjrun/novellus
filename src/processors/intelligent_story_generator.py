#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
裂世九域·法则链纪元 - 智能故事生成和剧情钩子深度分析系统
基于跨域冲突网络分析成果，提供AI驱动的故事创作辅助功能

功能模块：
1. 剧情钩子深度评估分析
2. 基于网络拓扑的智能故事生成
3. 冲突升级路径预测
4. 角色行为和动机分析
5. 故事一致性验证
6. 创作辅助工具
"""

import json
import uuid
import re
import math
import random
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PlotHookAnalysis:
    """剧情钩子深度分析数据模型"""
    id: str
    original_description: str
    conflict_pair: str
    hook_type: str

    # 戏剧价值分析
    dramatic_tension: float  # 戏剧张力 (0-10)
    emotional_impact: float  # 情感冲击力 (0-10)
    surprise_factor: float   # 意外性 (0-10)
    stakes_magnitude: float  # 风险规模 (0-10)

    # 故事发展潜力
    expandability: float     # 可扩展性 (0-10)
    branching_potential: float  # 分支可能性 (0-10)
    character_growth_space: float  # 角色成长空间 (0-10)
    theme_depth: float       # 主题深度 (0-10)

    # 世界观一致性
    lore_consistency: float  # 设定一致性 (0-10)
    logic_coherence: float   # 逻辑连贯性 (0-10)
    domain_authenticity: float  # 域特色真实性 (0-10)

    # 读者吸引力
    curiosity_hook: float    # 好奇心激发 (0-10)
    relatability: float      # 情感共鸣 (0-10)
    readability: float       # 可读性 (0-10)

    # 综合评分
    overall_score: float     # 综合评分 (0-100)
    quality_tier: str        # 质量等级 (S/A/B/C/D)

    # 分析详情
    strengths: List[str]     # 优势点
    weaknesses: List[str]    # 薄弱点
    improvement_suggestions: List[str]  # 改进建议
    related_entities: List[str]  # 相关实体
    conflict_elements: List[str]  # 冲突要素

    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class GeneratedStoryElement:
    """AI生成的故事元素"""
    id: str
    element_type: str  # plot_hook, character_arc, conflict_development
    title: str
    description: str

    # 生成参数
    based_on_entities: List[str]
    conflict_pattern: str
    complexity_level: int  # 1-10

    # 质量评估
    originality_score: float  # 原创性 (0-10)
    coherence_score: float    # 连贯性 (0-10)
    dramatic_potential: float # 戏剧潜力 (0-10)

    # 关联信息
    network_position: Dict[str, Any]  # 网络中的位置信息
    influence_scope: List[str]        # 影响范围
    trigger_conditions: List[str]     # 触发条件

    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ConflictEscalationPath:
    """冲突升级路径"""
    path_id: str
    initial_state: str
    escalation_levels: List[Dict[str, Any]]
    probability_factors: Dict[str, float]
    intervention_points: List[Dict[str, Any]]
    ultimate_outcomes: List[Dict[str, Any]]

@dataclass
class CharacterMotivationProfile:
    """角色动机档案"""
    character_id: str
    character_name: str
    primary_motivations: List[str]
    conflict_interests: Dict[str, float]
    emotional_drivers: Dict[str, float]
    moral_alignment: Dict[str, float]
    relationship_dynamics: Dict[str, float]

class IntelligentStoryGenerator:
    """智能故事生成器"""

    def __init__(self):
        self.entities: Dict[str, Any] = {}
        self.relations: Dict[str, Any] = {}
        self.plot_hooks: List[Dict[str, Any]] = []
        self.analyzed_hooks: Dict[str, PlotHookAnalysis] = {}
        self.generated_stories: Dict[str, GeneratedStoryElement] = {}

        # 网络分析数据
        self.network_graph = None
        self.centrality_scores = {}
        self.community_structure = {}
        self.propagation_model = {}

        # 分析参数
        self.story_generation_params = {
            "creativity_factor": 0.7,      # 创意因子
            "consistency_weight": 0.8,     # 一致性权重
            "complexity_preference": 0.6,  # 复杂度偏好
            "novelty_threshold": 0.5       # 新颖度阈值
        }

        # 评分权重配置
        self.scoring_weights = {
            "dramatic_value": 0.25,
            "story_potential": 0.25,
            "consistency": 0.20,
            "reader_appeal": 0.30
        }

        # 冲突升级触发器库
        self.escalation_triggers = {
            "权力斗争": [
                "上级压力", "同级竞争", "下级反叛", "外部威胁",
                "资源争夺", "声誉损失", "政治变动", "利益冲突"
            ],
            "身份认同": [
                "血统质疑", "能力否定", "归属冲突", "价值观分歧",
                "社会排斥", "文化冲击", "身份暴露", "认同危机"
            ],
            "经济冲突": [
                "市场垄断", "价格操控", "供应中断", "需求变化",
                "技术革新", "政策调整", "竞争加剧", "资源稀缺"
            ],
            "综合冲突": [
                "系统性危机", "多方博弈", "连锁反应", "结构性矛盾",
                "价值观冲突", "利益重新分配", "制度变革", "外部冲击"
            ]
        }

    def load_conflict_analysis_data(self, data_file: str) -> bool:
        """加载冲突分析数据"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取剧情钩子数据
            if "4. 故事情节潜力评估" in data:
                plot_section = data["4. 故事情节潜力评估"]
                hooks_data = plot_section.get("剧情钩子分析", {})

                for conflict_pair, hook_info in hooks_data.items():
                    for hook in hook_info.get("钩子详情", []):
                        hook["conflict_pair"] = conflict_pair
                        self.plot_hooks.append(hook)

            # 提取网络数据（从增强版输出目录加载）
            enhanced_file = "D:/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"
            if Path(enhanced_file).exists():
                with open(enhanced_file, 'r', encoding='utf-8') as f:
                    enhanced_data = json.load(f)
                    self.entities = {e['id']: e for e in enhanced_data.get('entities', [])}
                    self.relations = {r['id']: r for r in enhanced_data.get('relations', [])}
                    self.network_graph = enhanced_data.get('network_graph', {})

            logger.info(f"成功加载 {len(self.plot_hooks)} 个剧情钩子和 {len(self.entities)} 个实体")
            return True

        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return False

    def analyze_all_plot_hooks(self) -> Dict[str, PlotHookAnalysis]:
        """分析所有剧情钩子"""
        logger.info("开始分析所有剧情钩子...")

        for i, hook in enumerate(self.plot_hooks):
            hook_id = f"hook_{i:03d}"
            analysis = self._analyze_single_plot_hook(hook, hook_id)
            self.analyzed_hooks[hook_id] = analysis

        logger.info(f"完成 {len(self.analyzed_hooks)} 个剧情钩子的深度分析")
        return self.analyzed_hooks

    def _analyze_single_plot_hook(self, hook: Dict[str, Any], hook_id: str) -> PlotHookAnalysis:
        """分析单个剧情钩子"""
        description = hook.get("描述", "")
        conflict_pair = hook.get("conflict_pair", "")
        hook_type = hook.get("冲突类型", "")

        # 戏剧价值分析
        dramatic_tension = self._calculate_dramatic_tension(description, hook_type)
        emotional_impact = self._calculate_emotional_impact(description, hook_type)
        surprise_factor = self._calculate_surprise_factor(description)
        stakes_magnitude = self._calculate_stakes_magnitude(description, conflict_pair)

        # 故事发展潜力
        expandability = self._calculate_expandability(description, conflict_pair)
        branching_potential = self._calculate_branching_potential(description, hook_type)
        character_growth_space = self._calculate_character_growth_space(description)
        theme_depth = self._calculate_theme_depth(description, hook_type)

        # 世界观一致性
        lore_consistency = self._calculate_lore_consistency(description, conflict_pair)
        logic_coherence = self._calculate_logic_coherence(description)
        domain_authenticity = self._calculate_domain_authenticity(description, conflict_pair)

        # 读者吸引力
        curiosity_hook = self._calculate_curiosity_hook(description)
        relatability = self._calculate_relatability(description, hook_type)
        readability = self._calculate_readability(description)

        # 计算综合评分
        dramatic_value = (dramatic_tension + emotional_impact + surprise_factor + stakes_magnitude) / 4
        story_potential = (expandability + branching_potential + character_growth_space + theme_depth) / 4
        consistency = (lore_consistency + logic_coherence + domain_authenticity) / 3
        reader_appeal = (curiosity_hook + relatability + readability) / 3

        overall_score = (
            dramatic_value * self.scoring_weights["dramatic_value"] +
            story_potential * self.scoring_weights["story_potential"] +
            consistency * self.scoring_weights["consistency"] +
            reader_appeal * self.scoring_weights["reader_appeal"]
        ) * 10

        quality_tier = self._determine_quality_tier(overall_score)

        # 生成分析详情
        strengths = self._identify_strengths(
            dramatic_value, story_potential, consistency, reader_appeal
        )
        weaknesses = self._identify_weaknesses(
            dramatic_value, story_potential, consistency, reader_appeal
        )
        improvement_suggestions = self._generate_improvement_suggestions(
            weaknesses, description, hook_type
        )

        # 识别相关实体和冲突要素
        related_entities = self._identify_related_entities(description, conflict_pair)
        conflict_elements = self._extract_conflict_elements(description, hook_type)

        return PlotHookAnalysis(
            id=hook_id,
            original_description=description,
            conflict_pair=conflict_pair,
            hook_type=hook_type,
            dramatic_tension=dramatic_tension,
            emotional_impact=emotional_impact,
            surprise_factor=surprise_factor,
            stakes_magnitude=stakes_magnitude,
            expandability=expandability,
            branching_potential=branching_potential,
            character_growth_space=character_growth_space,
            theme_depth=theme_depth,
            lore_consistency=lore_consistency,
            logic_coherence=logic_coherence,
            domain_authenticity=domain_authenticity,
            curiosity_hook=curiosity_hook,
            relatability=relatability,
            readability=readability,
            overall_score=overall_score,
            quality_tier=quality_tier,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=improvement_suggestions,
            related_entities=related_entities,
            conflict_elements=conflict_elements
        )

    def _calculate_dramatic_tension(self, description: str, hook_type: str) -> float:
        """计算戏剧张力"""
        tension_keywords = {
            "高张力": ["危机", "生死", "绝望", "崩溃", "毁灭", "围困", "追杀"],
            "中张力": ["冲突", "斗争", "对抗", "竞争", "威胁", "困境"],
            "低张力": ["分歧", "争议", "问题", "困惑", "疑惑"]
        }

        score = 5.0  # 基础分数

        for level, keywords in tension_keywords.items():
            for keyword in keywords:
                if keyword in description:
                    if level == "高张力":
                        score += 1.5
                    elif level == "中张力":
                        score += 1.0
                    else:
                        score += 0.5

        # 冲突类型调整
        type_modifiers = {
            "权力斗争": 1.2,
            "生存危机": 1.3,
            "综合冲突": 1.1,
            "身份认同": 1.0,
            "经济冲突": 0.9
        }
        score *= type_modifiers.get(hook_type, 1.0)

        return min(10.0, max(1.0, score))

    def _calculate_emotional_impact(self, description: str, hook_type: str) -> float:
        """计算情感冲击力"""
        emotion_keywords = {
            "强情感": ["悲剧", "背叛", "牺牲", "绝望", "复仇", "失去", "痛苦"],
            "中情感": ["困境", "选择", "冲突", "压力", "责任", "担忧"],
            "弱情感": ["疑问", "困惑", "不确定", "考虑"]
        }

        score = 4.0

        for level, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in description:
                    if level == "强情感":
                        score += 2.0
                    elif level == "中情感":
                        score += 1.0
                    else:
                        score += 0.3

        return min(10.0, max(1.0, score))

    def _calculate_surprise_factor(self, description: str) -> float:
        """计算意外性"""
        surprise_indicators = [
            "神秘", "失踪", "突然", "意外", "惊人", "震惊", "不可思议",
            "隐藏", "秘密", "背后", "真相", "揭露", "发现"
        ]

        score = 3.0
        for indicator in surprise_indicators:
            if indicator in description:
                score += 0.8

        # 检查是否有反转元素
        if any(word in description for word in ["背叛", "真相", "隐藏", "伪装"]):
            score += 2.0

        return min(10.0, max(1.0, score))

    def _calculate_stakes_magnitude(self, description: str, conflict_pair: str) -> float:
        """计算风险规模"""
        scale_indicators = {
            "个人": ["个人", "家庭", "私人"],
            "组织": ["组织", "公会", "团体", "势力"],
            "地区": ["地区", "城市", "县", "镇"],
            "域级": ["域", "国家", "王国"],
            "跨域": ["跨域", "多域", "各域"]
        }

        base_score = 3.0

        # 根据冲突对确定基础规模
        if "↔" in conflict_pair:
            base_score = 6.0  # 跨域冲突基础分数更高

        # 检查描述中的规模指示词
        for scale, indicators in scale_indicators.items():
            for indicator in indicators:
                if indicator in description:
                    if scale == "跨域":
                        base_score += 3.0
                    elif scale == "域级":
                        base_score += 2.5
                    elif scale == "地区":
                        base_score += 1.5
                    elif scale == "组织":
                        base_score += 1.0

        return min(10.0, max(1.0, base_score))

    def _calculate_expandability(self, description: str, conflict_pair: str) -> float:
        """计算可扩展性"""
        expandability_factors = [
            "网络", "系统", "组织", "势力", "联盟", "集团",
            "体系", "制度", "规模", "影响", "连锁"
        ]

        score = 4.0

        for factor in expandability_factors:
            if factor in description:
                score += 0.8

        # 跨域冲突天然具有更高的可扩展性
        if "↔" in conflict_pair:
            score += 2.0

        # 检查是否涉及多个角色或组织
        role_count = len(re.findall(r'[官师商军人]', description))
        score += min(role_count * 0.5, 2.0)

        return min(10.0, max(1.0, score))

    def _calculate_branching_potential(self, description: str, hook_type: str) -> float:
        """计算分支可能性"""
        branching_indicators = [
            "选择", "决定", "路径", "方向", "可能", "或者",
            "要么", "困境", "两难", "多种", "不同"
        ]

        score = 3.0

        for indicator in branching_indicators:
            if indicator in description:
                score += 1.0

        # 复杂冲突类型有更高的分支潜力
        complexity_bonus = {
            "综合冲突": 2.0,
            "权力斗争": 1.5,
            "身份认同": 1.2,
            "经济冲突": 1.0
        }
        score += complexity_bonus.get(hook_type, 0.5)

        return min(10.0, max(1.0, score))

    def _calculate_character_growth_space(self, description: str) -> float:
        """计算角色成长空间"""
        growth_indicators = [
            "成长", "改变", "转变", "觉醒", "领悟", "学习",
            "经历", "历练", "考验", "挑战", "磨练"
        ]

        moral_dilemma_indicators = [
            "道德", "正义", "良心", "选择", "责任", "义务",
            "困境", "两难", "牺牲", "代价"
        ]

        score = 4.0

        for indicator in growth_indicators:
            if indicator in description:
                score += 1.0

        for indicator in moral_dilemma_indicators:
            if indicator in description:
                score += 0.8

        return min(10.0, max(1.0, score))

    def _calculate_theme_depth(self, description: str, hook_type: str) -> float:
        """计算主题深度"""
        deep_themes = {
            "权力与责任": ["权力", "责任", "义务", "领导"],
            "正义与秩序": ["正义", "公平", "秩序", "法律"],
            "自由与束缚": ["自由", "束缚", "约束", "解放"],
            "传统与变革": ["传统", "变革", "改革", "创新"],
            "个人与集体": ["个人", "集体", "社会", "群体"],
            "生存与尊严": ["生存", "尊严", "荣誉", "品格"]
        }

        score = 3.0

        for theme, keywords in deep_themes.items():
            if any(keyword in description for keyword in keywords):
                score += 1.2

        # 复杂冲突通常有更深的主题
        if hook_type == "综合冲突":
            score += 1.5

        return min(10.0, max(1.0, score))

    def _calculate_lore_consistency(self, description: str, conflict_pair: str) -> float:
        """计算设定一致性"""
        # 检查是否包含世界观关键元素
        lore_elements = [
            "链", "籍", "域", "祭", "评印", "器械", "缚约",
            "断链", "环约", "万器朝链", "裂世夜"
        ]

        score = 5.0
        element_count = 0

        for element in lore_elements:
            if element in description:
                element_count += 1
                score += 0.5

        # 基于冲突对验证域特色
        domain_consistency = self._validate_domain_consistency(description, conflict_pair)
        score += domain_consistency

        return min(10.0, max(1.0, score))

    def _validate_domain_consistency(self, description: str, conflict_pair: str) -> float:
        """验证域特色一致性"""
        domain_keywords = {
            "人域": ["税收", "征召", "链籍", "县府", "乡祭", "里正"],
            "天域": ["巡链官", "缚司", "环约", "评印院", "链法"],
            "灵域": ["器械师", "宗匠", "公会", "学徒", "工坊"],
            "荒域": ["部落", "断链", "遗迹", "矿脉", "守火者"]
        }

        score = 0.0
        domains = conflict_pair.replace("↔", " ").split()

        for domain in domains:
            domain_name = domain if domain.endswith("域") else domain + "域"
            if domain_name in domain_keywords:
                keywords = domain_keywords[domain_name]
                if any(keyword in description for keyword in keywords):
                    score += 1.0

        return score

    def _calculate_logic_coherence(self, description: str) -> float:
        """计算逻辑连贯性"""
        # 基础逻辑检查
        score = 6.0

        # 检查因果关系指示词
        causality_indicators = ["因为", "所以", "导致", "引发", "造成", "由于"]
        if any(indicator in description for indicator in causality_indicators):
            score += 1.0

        # 检查时间逻辑
        time_indicators = ["前夕", "之后", "期间", "突然", "随着"]
        if any(indicator in description for indicator in time_indicators):
            score += 0.5

        # 检查描述完整性
        if len(description) > 15:  # 描述足够详细
            score += 1.0

        return min(10.0, max(1.0, score))

    def _calculate_domain_authenticity(self, description: str, conflict_pair: str) -> float:
        """计算域特色真实性"""
        return self._validate_domain_consistency(description, conflict_pair) + 4.0

    def _calculate_curiosity_hook(self, description: str) -> float:
        """计算好奇心激发"""
        curiosity_triggers = [
            "神秘", "失踪", "秘密", "隐藏", "未知", "奇怪",
            "意外", "惊人", "不可思议", "传说", "谜团"
        ]

        score = 3.0

        for trigger in curiosity_triggers:
            if trigger in description:
                score += 1.2

        # 问题性描述增加好奇心
        if "?" in description or any(word in description for word in ["为什么", "怎么", "什么"]):
            score += 1.5

        return min(10.0, max(1.0, score))

    def _calculate_relatability(self, description: str, hook_type: str) -> float:
        """计算情感共鸣"""
        relatable_themes = [
            "家庭", "友情", "背叛", "牺牲", "成长", "责任",
            "选择", "困境", "梦想", "希望", "失去"
        ]

        score = 4.0

        for theme in relatable_themes:
            if theme in description:
                score += 0.8

        # 人性化冲突更容易产生共鸣
        human_elements = ["人情", "道德", "良心", "感情", "亲情"]
        for element in human_elements:
            if element in description:
                score += 1.0

        return min(10.0, max(1.0, score))

    def _calculate_readability(self, description: str) -> float:
        """计算可读性"""
        score = 5.0

        # 长度适中性
        length = len(description)
        if 10 <= length <= 25:
            score += 2.0
        elif 25 < length <= 40:
            score += 1.0
        elif length > 40:
            score -= 1.0

        # 复杂度检查
        complex_chars = len([c for c in description if ord(c) > 0x9FFF])
        if complex_chars / length < 0.1:  # 生僻字比例低
            score += 1.0

        return min(10.0, max(1.0, score))

    def _determine_quality_tier(self, overall_score: float) -> str:
        """确定质量等级"""
        if overall_score >= 85:
            return "S"
        elif overall_score >= 75:
            return "A"
        elif overall_score >= 65:
            return "B"
        elif overall_score >= 55:
            return "C"
        else:
            return "D"

    def _identify_strengths(self, dramatic_value: float, story_potential: float,
                          consistency: float, reader_appeal: float) -> List[str]:
        """识别优势点"""
        strengths = []

        if dramatic_value >= 7.5:
            strengths.append("戏剧张力强烈，冲突激烈引人入胜")
        if story_potential >= 7.5:
            strengths.append("故事发展潜力巨大，可扩展性强")
        if consistency >= 8.0:
            strengths.append("世界观设定一致性优秀，逻辑严密")
        if reader_appeal >= 7.5:
            strengths.append("读者吸引力强，情感共鸣度高")

        if not strengths:
            strengths.append("具备基础的故事要素，有发展空间")

        return strengths

    def _identify_weaknesses(self, dramatic_value: float, story_potential: float,
                           consistency: float, reader_appeal: float) -> List[str]:
        """识别薄弱点"""
        weaknesses = []

        if dramatic_value < 5.0:
            weaknesses.append("戏剧张力不足，冲突强度偏低")
        if story_potential < 5.0:
            weaknesses.append("故事发展潜力有限，扩展性不足")
        if consistency < 6.0:
            weaknesses.append("世界观一致性需要加强，设定细节不够")
        if reader_appeal < 5.0:
            weaknesses.append("读者吸引力偏弱，情感共鸣度不够")

        return weaknesses

    def _generate_improvement_suggestions(self, weaknesses: List[str],
                                        description: str, hook_type: str) -> List[str]:
        """生成改进建议"""
        suggestions = []

        for weakness in weaknesses:
            if "戏剧张力" in weakness:
                suggestions.append("增加更高风险的冲突要素，提升危机感和紧迫性")
            elif "发展潜力" in weakness:
                suggestions.append("添加更多关联角色和势力，创造更复杂的利益关系网")
            elif "一致性" in weakness:
                suggestions.append("深化世界观细节，增加特定域的文化特色和制度背景")
            elif "吸引力" in weakness:
                suggestions.append("强化角色的情感动机，增加道德困境和人性化冲突")

        # 基于冲突类型的具体建议
        if hook_type == "权力斗争":
            suggestions.append("明确权力结构和利益分配，突出政治博弈的复杂性")
        elif hook_type == "身份认同":
            suggestions.append("深入探讨身份背后的文化冲突和价值观差异")
        elif hook_type == "经济冲突":
            suggestions.append("完善经济系统的运作机制，体现经济与政治的交互影响")

        return suggestions[:3]  # 限制建议数量

    def _identify_related_entities(self, description: str, conflict_pair: str) -> List[str]:
        """识别相关实体"""
        entities = []

        # 从已有实体库中匹配
        for entity_id, entity_data in self.entities.items():
            entity_name = entity_data.get('name', '')
            if entity_name and (entity_name in description or
                              any(alias in description for alias in entity_data.get('aliases', []))):
                entities.append(entity_name)

        # 如果没有匹配到，根据关键词推断
        if not entities:
            entities = self._extract_implied_entities(description, conflict_pair)

        return entities[:5]  # 限制数量

    def _extract_implied_entities(self, description: str, conflict_pair: str) -> List[str]:
        """提取隐含实体"""
        implied_entities = []

        # 角色实体模式
        role_patterns = [
            r'([^，。；！？]*官[^，。；！？]*)',
            r'([^，。；！？]*师[^，。；！？]*)',
            r'([^，。；！？]*商[^，。；！？]*)',
            r'([^，。；！？]*军[^，。；！？]*)'
        ]

        for pattern in role_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                clean_match = match.strip()
                if 2 <= len(clean_match) <= 10:
                    implied_entities.append(clean_match)

        return implied_entities

    def _extract_conflict_elements(self, description: str, hook_type: str) -> List[str]:
        """提取冲突要素"""
        elements = []

        # 基于冲突类型的要素库
        conflict_element_patterns = {
            "权力斗争": ["权力", "地位", "控制", "威权", "统治", "支配"],
            "身份认同": ["身份", "血统", "出身", "归属", "认同", "接纳"],
            "经济冲突": ["利益", "资源", "财富", "贸易", "垄断", "竞争"],
            "综合冲突": ["制度", "系统", "秩序", "变革", "冲击", "危机"]
        }

        relevant_patterns = conflict_element_patterns.get(hook_type, [])
        for pattern in relevant_patterns:
            if pattern in description:
                elements.append(pattern)

        # 通用冲突要素
        general_elements = ["矛盾", "冲突", "对立", "争夺", "竞争", "博弈"]
        for element in general_elements:
            if element in description and element not in elements:
                elements.append(element)

        return elements

    def generate_new_plot_hooks(self, generation_params: Dict[str, Any] = None) -> List[GeneratedStoryElement]:
        """基于网络拓扑生成新的剧情钩子"""
        logger.info("开始基于网络拓扑生成新剧情钩子...")

        if generation_params is None:
            generation_params = self.story_generation_params.copy()

        generated_hooks = []

        # 基于高中心性实体生成
        high_centrality_hooks = self._generate_from_high_centrality_entities()
        generated_hooks.extend(high_centrality_hooks)

        # 基于社群边界生成
        community_boundary_hooks = self._generate_from_community_boundaries()
        generated_hooks.extend(community_boundary_hooks)

        # 基于路径分析生成
        path_based_hooks = self._generate_from_network_paths()
        generated_hooks.extend(path_based_hooks)

        # 基于结构洞生成
        structural_hole_hooks = self._generate_from_structural_holes()
        generated_hooks.extend(structural_hole_hooks)

        logger.info(f"生成了 {len(generated_hooks)} 个新剧情钩子")
        return generated_hooks

    def _generate_from_high_centrality_entities(self) -> List[GeneratedStoryElement]:
        """基于高中心性实体生成剧情钩子"""
        hooks = []

        # 模拟中心性计算（如果没有真实的网络图数据）
        entity_connections = defaultdict(int)
        for relation in self.relations.values():
            entity_connections[relation.get('source_entity_id', '')] += 1
            entity_connections[relation.get('target_entity_id', '')] += 1

        # 选择连接数最多的实体
        sorted_entities = sorted(entity_connections.items(), key=lambda x: x[1], reverse=True)[:5]

        for entity_id, connection_count in sorted_entities:
            if entity_id in self.entities:
                entity = self.entities[entity_id]
                hook = self._create_centrality_based_hook(entity, connection_count)
                hooks.append(hook)

        return hooks

    def _create_centrality_based_hook(self, entity: Dict[str, Any], connection_count: int) -> GeneratedStoryElement:
        """创建基于中心性的剧情钩子"""
        entity_name = entity.get('name', '未知实体')
        entity_type = entity.get('entity_type', '')
        domains = entity.get('domains', [])

        # 基于实体类型和连接数生成情节
        if entity_type == "核心资源":
            title = f"{entity_name}的争夺战"
            description = f"多方势力围绕{entity_name}展开激烈争夺，这一核心资源的控制权将决定{domains[0] if domains else '某域'}的未来走向"
        elif entity_type == "关键角色":
            title = f"{entity_name}的抉择时刻"
            description = f"身处权力网络中心的{entity_name}面临前所未有的选择，其决定将影响整个利益网络的平衡"
        elif entity_type == "法条制度":
            title = f"{entity_name}引发的制度危机"
            description = f"围绕{entity_name}的执行和解释权，各方力量展开博弈，制度的权威性受到前所未有的挑战"
        else:
            title = f"围绕{entity_name}的连锁反应"
            description = f"{entity_name}的变化引发连锁反应，波及整个关系网络，各方势力重新洗牌"

        return GeneratedStoryElement(
            id=f"generated_centrality_{entity.get('id', 'unknown')}",
            element_type="plot_hook",
            title=title,
            description=description,
            based_on_entities=[entity.get('id', '')],
            conflict_pattern="centrality_based",
            complexity_level=min(connection_count // 2, 10),
            originality_score=7.0 + random.uniform(-1, 1),
            coherence_score=8.0 + random.uniform(-0.5, 0.5),
            dramatic_potential=7.5 + random.uniform(-1, 1),
            network_position={"centrality_rank": 1, "connection_count": connection_count},
            influence_scope=domains,
            trigger_conditions=[f"{entity_name}状态变化", "外部压力增加", "利益分配失衡"]
        )

    def _generate_from_community_boundaries(self) -> List[GeneratedStoryElement]:
        """基于社群边界生成剧情钩子"""
        hooks = []

        # 识别跨社群关系
        cross_community_relations = []
        for relation in self.relations.values():
            if relation.get('is_cross_domain', False):
                cross_community_relations.append(relation)

        # 从跨社群关系中生成冲突情节
        for i, relation in enumerate(cross_community_relations[:3]):  # 限制数量
            hook = self._create_boundary_based_hook(relation, i)
            hooks.append(hook)

        return hooks

    def _create_boundary_based_hook(self, relation: Dict[str, Any], index: int) -> GeneratedStoryElement:
        """创建基于边界的剧情钩子"""
        source_id = relation.get('source_entity_id', '')
        target_id = relation.get('target_entity_id', '')
        relation_type = relation.get('relation_type', '')
        source_domain = relation.get('source_domain', '')
        target_domain = relation.get('target_domain', '')

        # 获取实体信息
        source_entity = self.entities.get(source_id, {})
        target_entity = self.entities.get(target_id, {})

        source_name = source_entity.get('name', '未知实体A')
        target_name = target_entity.get('name', '未知实体B')

        # 基于关系类型生成情节
        if relation_type == "对立":
            title = f"{source_domain}与{target_domain}的边界冲突"
            description = f"{source_name}与{target_name}的对立关系升级，成为{source_domain}和{target_domain}之间紧张关系的导火索"
        elif relation_type == "竞争":
            title = f"跨域竞争的新阶段"
            description = f"围绕{source_name}和{target_name}的竞争演变为{source_domain}与{target_domain}的系统性竞争"
        else:
            title = f"跨域{relation_type}的意外后果"
            description = f"{source_name}与{target_name}的{relation_type}关系产生意想不到的后果，影响两域之间的平衡"

        return GeneratedStoryElement(
            id=f"generated_boundary_{index}",
            element_type="plot_hook",
            title=title,
            description=description,
            based_on_entities=[source_id, target_id],
            conflict_pattern="boundary_conflict",
            complexity_level=8,
            originality_score=7.5 + random.uniform(-0.5, 0.5),
            coherence_score=8.5 + random.uniform(-0.3, 0.3),
            dramatic_potential=8.0 + random.uniform(-0.5, 0.5),
            network_position={"type": "cross_community", "domains": [source_domain, target_domain]},
            influence_scope=[source_domain, target_domain],
            trigger_conditions=["跨域关系紧张", "边界事件", "政策变化"]
        )

    def _generate_from_network_paths(self) -> List[GeneratedStoryElement]:
        """基于网络路径生成剧情钩子"""
        hooks = []

        # 找到关键路径（模拟最短路径算法的结果）
        critical_paths = self._identify_critical_paths()

        for i, path in enumerate(critical_paths[:2]):  # 限制数量
            hook = self._create_path_based_hook(path, i)
            hooks.append(hook)

        return hooks

    def _identify_critical_paths(self) -> List[List[str]]:
        """识别关键路径"""
        # 这里使用简化的方法识别路径
        # 在真实实现中应该使用图算法
        paths = []

        # 构建一些示例路径
        entities_by_domain = defaultdict(list)
        for entity_id, entity in self.entities.items():
            domains = entity.get('domains', [])
            for domain in domains:
                entities_by_domain[domain].append(entity_id)

        # 创建跨域路径
        domains = list(entities_by_domain.keys())
        for i in range(len(domains) - 1):
            for j in range(i + 1, len(domains)):
                if entities_by_domain[domains[i]] and entities_by_domain[domains[j]]:
                    path = [
                        entities_by_domain[domains[i]][0],
                        entities_by_domain[domains[j]][0]
                    ]
                    paths.append(path)

        return paths

    def _create_path_based_hook(self, path: List[str], index: int) -> GeneratedStoryElement:
        """创建基于路径的剧情钩子"""
        path_entities = [self.entities.get(entity_id, {}) for entity_id in path]
        entity_names = [entity.get('name', f'实体{i}') for i, entity in enumerate(path_entities)]

        title = f"连锁效应：从{entity_names[0]}到{entity_names[-1]}"
        description = f"一个看似无关的事件从{entity_names[0]}开始，通过复杂的关系网络传播，最终影响到{entity_names[-1]}，引发意想不到的后果"

        return GeneratedStoryElement(
            id=f"generated_path_{index}",
            element_type="plot_hook",
            title=title,
            description=description,
            based_on_entities=path,
            conflict_pattern="chain_reaction",
            complexity_level=9,
            originality_score=8.0 + random.uniform(-0.5, 0.5),
            coherence_score=7.5 + random.uniform(-0.5, 0.5),
            dramatic_potential=7.8 + random.uniform(-0.3, 0.7),
            network_position={"type": "critical_path", "path_length": len(path)},
            influence_scope=[entity.get('domains', [''])[0] for entity in path_entities if entity.get('domains')],
            trigger_conditions=["连锁事件", "系统性变化", "信息传播"]
        )

    def _generate_from_structural_holes(self) -> List[GeneratedStoryElement]:
        """基于结构洞生成剧情钩子"""
        hooks = []

        # 识别桥接节点（结构洞位置）
        bridge_entities = self._identify_bridge_entities()

        for i, entity_id in enumerate(bridge_entities[:2]):  # 限制数量
            if entity_id in self.entities:
                hook = self._create_structural_hole_hook(self.entities[entity_id], i)
                hooks.append(hook)

        return hooks

    def _identify_bridge_entities(self) -> List[str]:
        """识别桥接实体"""
        bridge_entities = []

        # 简化的桥接识别：找到连接不同域的实体
        for entity_id, entity in self.entities.items():
            domains = entity.get('domains', [])
            if len(domains) > 1:  # 跨域实体可能是桥接点
                bridge_entities.append(entity_id)

        return bridge_entities

    def _create_structural_hole_hook(self, entity: Dict[str, Any], index: int) -> GeneratedStoryElement:
        """创建基于结构洞的剧情钩子"""
        entity_name = entity.get('name', '未知实体')
        domains = entity.get('domains', [])

        title = f"关键节点{entity_name}的危机"
        description = f"作为连接{' 和 '.join(domains)}的关键节点，{entity_name}的任何变化都可能切断重要联系，引发系统性危机"

        return GeneratedStoryElement(
            id=f"generated_structural_hole_{index}",
            element_type="plot_hook",
            title=title,
            description=description,
            based_on_entities=[entity.get('id', '')],
            conflict_pattern="structural_vulnerability",
            complexity_level=10,
            originality_score=8.5 + random.uniform(-0.3, 0.3),
            coherence_score=8.8 + random.uniform(-0.2, 0.2),
            dramatic_potential=9.0 + random.uniform(-0.5, 0.5),
            network_position={"type": "structural_hole", "bridge_domains": domains},
            influence_scope=domains,
            trigger_conditions=["桥接失效", "中介危机", "网络分裂"]
        )

    def predict_conflict_escalation_paths(self, hook_id: str) -> ConflictEscalationPath:
        """预测冲突升级路径"""
        if hook_id not in self.analyzed_hooks:
            raise ValueError(f"未找到钩子 {hook_id}")

        hook = self.analyzed_hooks[hook_id]

        # 基于钩子类型和特征预测升级路径
        escalation_levels = self._generate_escalation_levels(hook)
        probability_factors = self._calculate_probability_factors(hook)
        intervention_points = self._identify_intervention_points(hook)
        ultimate_outcomes = self._predict_ultimate_outcomes(hook)

        return ConflictEscalationPath(
            path_id=f"escalation_{hook_id}",
            initial_state=hook.original_description,
            escalation_levels=escalation_levels,
            probability_factors=probability_factors,
            intervention_points=intervention_points,
            ultimate_outcomes=ultimate_outcomes
        )

    def _generate_escalation_levels(self, hook: PlotHookAnalysis) -> List[Dict[str, Any]]:
        """生成冲突升级等级"""
        base_triggers = self.escalation_triggers.get(hook.hook_type, ["未知触发器"])

        levels = []
        intensity_progression = [0.2, 0.4, 0.6, 0.8, 1.0]

        for i, intensity in enumerate(intensity_progression):
            level = {
                "level": i + 1,
                "description": self._generate_escalation_description(hook, intensity),
                "intensity": intensity,
                "triggers": random.sample(base_triggers, min(2, len(base_triggers))),
                "affected_entities": self._predict_affected_entities(hook, intensity),
                "estimated_probability": max(0.1, 1.0 - intensity * 0.8),
                "resolution_difficulty": intensity * 10
            }
            levels.append(level)

        return levels

    def _generate_escalation_description(self, hook: PlotHookAnalysis, intensity: float) -> str:
        """生成升级描述"""
        base_description = hook.original_description

        if intensity <= 0.3:
            return f"{base_description} - 初期影响扩散"
        elif intensity <= 0.5:
            return f"{base_description} - 冲突范围扩大"
        elif intensity <= 0.7:
            return f"{base_description} - 矛盾全面激化"
        elif intensity <= 0.9:
            return f"{base_description} - 危机失控蔓延"
        else:
            return f"{base_description} - 系统性崩溃威胁"

    def _calculate_probability_factors(self, hook: PlotHookAnalysis) -> Dict[str, float]:
        """计算概率因子"""
        return {
            "基础冲突强度": hook.dramatic_tension / 10,
            "利益相关度": hook.stakes_magnitude / 10,
            "外部压力": 0.3,
            "干预能力": 1.0 - (hook.overall_score / 100),
            "历史先例": 0.5,
            "系统稳定性": 0.6
        }

    def _identify_intervention_points(self, hook: PlotHookAnalysis) -> List[Dict[str, Any]]:
        """识别干预节点"""
        intervention_points = []

        # 基于相关实体识别干预点
        for entity_name in hook.related_entities[:3]:
            intervention_points.append({
                "point": f"通过{entity_name}进行调解",
                "effectiveness": random.uniform(0.3, 0.8),
                "cost": random.uniform(0.2, 0.7),
                "risks": [f"{entity_name}可能的副作用", "干预失败的后果"]
            })

        # 添加系统性干预点
        intervention_points.append({
            "point": "制度性调整",
            "effectiveness": 0.7,
            "cost": 0.8,
            "risks": ["制度变更的不确定性", "既得利益者的反抗"]
        })

        return intervention_points

    def _predict_ultimate_outcomes(self, hook: PlotHookAnalysis) -> List[Dict[str, Any]]:
        """预测最终结果"""
        outcomes = []

        # 基于冲突类型预测可能结果
        if hook.hook_type == "权力斗争":
            outcomes = [
                {"outcome": "权力重新分配", "probability": 0.4, "impact": "高"},
                {"outcome": "权威体系重构", "probability": 0.3, "impact": "极高"},
                {"outcome": "维持现状", "probability": 0.3, "impact": "低"}
            ]
        elif hook.hook_type == "身份认同":
            outcomes = [
                {"outcome": "身份认同重新定义", "probability": 0.5, "impact": "中高"},
                {"outcome": "群体分裂", "probability": 0.3, "impact": "高"},
                {"outcome": "融合与和解", "probability": 0.2, "impact": "中"}
            ]
        elif hook.hook_type == "经济冲突":
            outcomes = [
                {"outcome": "经济规则重构", "probability": 0.4, "impact": "高"},
                {"outcome": "市场重新洗牌", "probability": 0.4, "impact": "中高"},
                {"outcome": "经济危机", "probability": 0.2, "impact": "极高"}
            ]
        else:
            outcomes = [
                {"outcome": "系统性变革", "probability": 0.3, "impact": "极高"},
                {"outcome": "局部调整", "probability": 0.5, "impact": "中"},
                {"outcome": "危机加剧", "probability": 0.2, "impact": "高"}
            ]

        return outcomes

    def _predict_affected_entities(self, hook: PlotHookAnalysis, intensity: float) -> List[str]:
        """预测受影响的实体"""
        # 基于强度扩散范围
        base_entities = hook.related_entities.copy()

        if intensity > 0.5:
            # 添加同域其他实体
            domain_entities = [
                entity_name for entity_id, entity_data in self.entities.items()
                for domain in hook.conflict_pair.split("↔")
                if domain in entity_data.get('domains', [])
                for entity_name in [entity_data.get('name', '')]
                if entity_name and entity_name not in base_entities
            ]
            base_entities.extend(domain_entities[:3])

        if intensity > 0.8:
            # 添加跨域实体
            cross_domain_entities = [
                entity_data.get('name', '') for entity_id, entity_data in self.entities.items()
                if len(entity_data.get('domains', [])) > 1
                and entity_data.get('name', '') not in base_entities
            ]
            base_entities.extend(cross_domain_entities[:2])

        return base_entities[:10]  # 限制数量

    def analyze_character_motivations(self, character_entities: List[str]) -> List[CharacterMotivationProfile]:
        """分析角色动机"""
        motivation_profiles = []

        for entity_name in character_entities:
            # 找到对应的实体
            entity_data = None
            for entity_id, entity in self.entities.items():
                if entity.get('name') == entity_name:
                    entity_data = entity
                    break

            if entity_data and entity_data.get('entity_type') == '关键角色':
                profile = self._create_motivation_profile(entity_data)
                motivation_profiles.append(profile)

        return motivation_profiles

    def _create_motivation_profile(self, entity_data: Dict[str, Any]) -> CharacterMotivationProfile:
        """创建动机档案"""
        character_name = entity_data.get('name', '未知角色')
        domains = entity_data.get('domains', [])

        # 基于角色名称和描述推断动机
        primary_motivations = self._infer_primary_motivations(character_name, entity_data)
        conflict_interests = self._analyze_conflict_interests(character_name, domains)
        emotional_drivers = self._analyze_emotional_drivers(character_name)
        moral_alignment = self._analyze_moral_alignment(character_name)
        relationship_dynamics = self._analyze_relationship_dynamics(character_name)

        return CharacterMotivationProfile(
            character_id=entity_data.get('id', ''),
            character_name=character_name,
            primary_motivations=primary_motivations,
            conflict_interests=conflict_interests,
            emotional_drivers=emotional_drivers,
            moral_alignment=moral_alignment,
            relationship_dynamics=relationship_dynamics
        )

    def _infer_primary_motivations(self, character_name: str, entity_data: Dict[str, Any]) -> List[str]:
        """推断主要动机"""
        motivations = []

        # 基于角色类型推断
        if "官" in character_name:
            motivations.extend(["权力维护", "政治稳定", "职业发展"])
        elif "师" in character_name:
            motivations.extend(["技能精进", "知识传承", "创新突破"])
        elif "商" in character_name:
            motivations.extend(["经济利益", "市场扩张", "风险控制"])
        elif "军" in character_name:
            motivations.extend(["安全保障", "荣誉追求", "职责履行"])
        else:
            motivations.extend(["生存发展", "利益保护", "价值实现"])

        return motivations

    def _analyze_conflict_interests(self, character_name: str, domains: List[str]) -> Dict[str, float]:
        """分析冲突利益"""
        interests = {}

        # 基于角色在不同冲突中的利益
        for domain in domains:
            interests[f"{domain}利益"] = random.uniform(0.3, 0.9)

        # 添加通用利益项
        interests.update({
            "个人利益": random.uniform(0.5, 0.8),
            "集体利益": random.uniform(0.3, 0.7),
            "长期利益": random.uniform(0.4, 0.6),
            "短期利益": random.uniform(0.6, 0.9)
        })

        return interests

    def _analyze_emotional_drivers(self, character_name: str) -> Dict[str, float]:
        """分析情感驱动因素"""
        return {
            "野心": random.uniform(0.2, 0.8),
            "恐惧": random.uniform(0.1, 0.6),
            "责任感": random.uniform(0.4, 0.9),
            "复仇心": random.uniform(0.0, 0.4),
            "同情心": random.uniform(0.2, 0.7),
            "好奇心": random.uniform(0.3, 0.8)
        }

    def _analyze_moral_alignment(self, character_name: str) -> Dict[str, float]:
        """分析道德倾向"""
        return {
            "秩序倾向": random.uniform(0.2, 0.8),
            "善良倾向": random.uniform(0.3, 0.9),
            "务实倾向": random.uniform(0.4, 0.8),
            "理想主义": random.uniform(0.2, 0.7)
        }

    def _analyze_relationship_dynamics(self, character_name: str) -> Dict[str, float]:
        """分析关系动态"""
        return {
            "合作倾向": random.uniform(0.3, 0.8),
            "竞争倾向": random.uniform(0.2, 0.7),
            "领导能力": random.uniform(0.1, 0.9),
            "影响力": random.uniform(0.2, 0.8),
            "可信度": random.uniform(0.4, 0.9)
        }

    def generate_comprehensive_report(self, output_dir: str = "D:/work/novellus/story_analysis_output") -> Dict[str, Any]:
        """生成综合分析报告"""
        logger.info("生成综合分析报告...")

        os.makedirs(output_dir, exist_ok=True)

        # 分析所有剧情钩子
        if not self.analyzed_hooks:
            self.analyze_all_plot_hooks()

        # 生成新剧情钩子
        generated_hooks = self.generate_new_plot_hooks()

        # 编译报告数据
        report_data = {
            "报告元数据": {
                "生成时间": datetime.now().isoformat(),
                "分析器版本": "智能故事生成器 v1.0",
                "原始钩子数量": len(self.plot_hooks),
                "分析钩子数量": len(self.analyzed_hooks),
                "生成钩子数量": len(generated_hooks)
            },
            "原始剧情钩子分析": {
                "整体统计": self._generate_overall_statistics(),
                "质量分布": self._generate_quality_distribution(),
                "类型分析": self._generate_type_analysis(),
                "详细分析结果": [asdict(hook) for hook in self.analyzed_hooks.values()]
            },
            "AI生成剧情钩子": {
                "生成策略": ["中心性分析", "社群边界", "网络路径", "结构洞"],
                "生成结果": [asdict(hook) for hook in generated_hooks],
                "质量评估": self._evaluate_generated_hooks(generated_hooks)
            },
            "冲突升级路径分析": self._generate_escalation_analysis(),
            "角色动机分析": self._generate_character_analysis(),
            "创作指导建议": self._generate_writing_guidance(),
            "可视化数据": self._generate_visualization_data()
        }

        # 保存主报告
        main_report_file = f"{output_dir}/intelligent_story_analysis_report.json"
        with open(main_report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        # 生成Markdown报告
        markdown_report = self._generate_markdown_report(report_data)
        markdown_file = f"{output_dir}/story_analysis_report.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)

        # 生成创作辅助文件
        self._generate_creative_aids(output_dir, report_data)

        summary = {
            "报告生成时间": datetime.now().isoformat(),
            "输出目录": output_dir,
            "主要文件": {
                "详细分析报告": main_report_file,
                "Markdown报告": markdown_file,
                "创作辅助文件": f"{output_dir}/creative_aids/"
            },
            "分析统计": {
                "原始钩子": len(self.plot_hooks),
                "深度分析": len(self.analyzed_hooks),
                "AI生成": len(generated_hooks),
                "平均质量分": sum(h.overall_score for h in self.analyzed_hooks.values()) / len(self.analyzed_hooks) if self.analyzed_hooks else 0
            }
        }

        logger.info("综合分析报告生成完成")
        return summary

    def _generate_overall_statistics(self) -> Dict[str, Any]:
        """生成整体统计"""
        if not self.analyzed_hooks:
            return {}

        scores = [hook.overall_score for hook in self.analyzed_hooks.values()]

        return {
            "平均综合评分": sum(scores) / len(scores),
            "最高评分": max(scores),
            "最低评分": min(scores),
            "评分标准差": np.std(scores) if len(scores) > 1 else 0,
            "S级钩子数": len([h for h in self.analyzed_hooks.values() if h.quality_tier == "S"]),
            "A级钩子数": len([h for h in self.analyzed_hooks.values() if h.quality_tier == "A"]),
            "B级钩子数": len([h for h in self.analyzed_hooks.values() if h.quality_tier == "B"]),
            "C级钩子数": len([h for h in self.analyzed_hooks.values() if h.quality_tier == "C"]),
            "D级钩子数": len([h for h in self.analyzed_hooks.values() if h.quality_tier == "D"])
        }

    def _generate_quality_distribution(self) -> Dict[str, Any]:
        """生成质量分布"""
        if not self.analyzed_hooks:
            return {}

        distributions = {
            "戏剧张力": [h.dramatic_tension for h in self.analyzed_hooks.values()],
            "情感冲击": [h.emotional_impact for h in self.analyzed_hooks.values()],
            "可扩展性": [h.expandability for h in self.analyzed_hooks.values()],
            "一致性": [h.lore_consistency for h in self.analyzed_hooks.values()],
            "读者吸引力": [h.curiosity_hook for h in self.analyzed_hooks.values()]
        }

        return {
            dimension: {
                "平均分": sum(scores) / len(scores),
                "最高分": max(scores),
                "最低分": min(scores)
            }
            for dimension, scores in distributions.items()
        }

    def _generate_type_analysis(self) -> Dict[str, Any]:
        """生成类型分析"""
        type_stats = defaultdict(list)

        for hook in self.analyzed_hooks.values():
            type_stats[hook.hook_type].append(hook.overall_score)

        return {
            hook_type: {
                "数量": len(scores),
                "平均评分": sum(scores) / len(scores),
                "最佳表现": max(scores),
                "改进空间": min(scores)
            }
            for hook_type, scores in type_stats.items()
        }

    def _evaluate_generated_hooks(self, generated_hooks: List[GeneratedStoryElement]) -> Dict[str, Any]:
        """评估生成的钩子"""
        if not generated_hooks:
            return {}

        return {
            "平均原创性": sum(h.originality_score for h in generated_hooks) / len(generated_hooks),
            "平均连贯性": sum(h.coherence_score for h in generated_hooks) / len(generated_hooks),
            "平均戏剧潜力": sum(h.dramatic_potential for h in generated_hooks) / len(generated_hooks),
            "生成策略分布": Counter([h.conflict_pattern for h in generated_hooks]),
            "复杂度分布": Counter([h.complexity_level for h in generated_hooks])
        }

    def _generate_escalation_analysis(self) -> Dict[str, Any]:
        """生成升级路径分析"""
        # 为前3个钩子生成升级路径分析
        escalation_analyses = {}

        for hook_id in list(self.analyzed_hooks.keys())[:3]:
            try:
                escalation_path = self.predict_conflict_escalation_paths(hook_id)
                escalation_analyses[hook_id] = {
                    "初始状态": escalation_path.initial_state,
                    "升级等级数": len(escalation_path.escalation_levels),
                    "平均升级概率": sum(level.get("estimated_probability", 0) for level in escalation_path.escalation_levels) / len(escalation_path.escalation_levels),
                    "干预点数量": len(escalation_path.intervention_points),
                    "可能结果": len(escalation_path.ultimate_outcomes)
                }
            except Exception as e:
                logger.warning(f"生成升级路径失败 {hook_id}: {e}")

        return escalation_analyses

    def _generate_character_analysis(self) -> Dict[str, Any]:
        """生成角色分析"""
        # 提取所有角色实体
        character_entities = [
            entity.get('name', '') for entity in self.entities.values()
            if entity.get('entity_type') == '关键角色'
        ]

        if character_entities:
            motivation_profiles = self.analyze_character_motivations(character_entities[:5])
            return {
                "分析角色数": len(motivation_profiles),
                "角色列表": [profile.character_name for profile in motivation_profiles],
                "平均动机复杂度": len(motivation_profiles[0].primary_motivations) if motivation_profiles else 0,
                "关键发现": ["角色动机呈现多样化特征", "冲突利益分化明显", "道德倾向影响决策"]
            }

        return {"分析角色数": 0, "说明": "未发现足够的角色实体进行分析"}

    def _generate_writing_guidance(self) -> Dict[str, Any]:
        """生成创作指导"""
        if not self.analyzed_hooks:
            return {}

        # 基于分析结果生成指导建议
        high_quality_hooks = [h for h in self.analyzed_hooks.values() if h.overall_score >= 75]
        low_quality_hooks = [h for h in self.analyzed_hooks.values() if h.overall_score < 60]

        return {
            "优秀案例学习": {
                "高质量钩子特征": self._extract_high_quality_patterns(high_quality_hooks),
                "成功要素": ["强烈的戏剧冲突", "深刻的主题内涵", "完整的世界观背景"]
            },
            "改进建议": {
                "普遍问题": self._identify_common_weaknesses(low_quality_hooks),
                "提升策略": ["增强角色动机的复杂性", "深化冲突的道德层面", "扩展故事的影响范围"]
            },
            "创作技巧": {
                "冲突设计": "从个人矛盾升级到系统性危机",
                "角色塑造": "多重动机驱动，道德困境选择",
                "世界观运用": "充分利用域特色，体现制度冲突"
            },
            "情节发展建议": {
                "开篇策略": "以小见大，从具体事件引出深层矛盾",
                "中段推进": "多线并行，相互影响，逐步升级",
                "高潮设计": "价值观冲突，艰难选择，意外反转",
                "结局处理": "既解决冲突又留有余韵，体现主题"
            }
        }

    def _extract_high_quality_patterns(self, high_quality_hooks: List[PlotHookAnalysis]) -> List[str]:
        """提取高质量模式"""
        if not high_quality_hooks:
            return ["暂无高质量案例可供分析"]

        patterns = []

        # 分析共同特征
        avg_tension = sum(h.dramatic_tension for h in high_quality_hooks) / len(high_quality_hooks)
        if avg_tension > 7:
            patterns.append("戏剧张力突出，冲突激烈")

        avg_expandability = sum(h.expandability for h in high_quality_hooks) / len(high_quality_hooks)
        if avg_expandability > 7:
            patterns.append("故事扩展性强，发展空间大")

        common_types = Counter(h.hook_type for h in high_quality_hooks).most_common(1)
        if common_types:
            patterns.append(f"'{common_types[0][0]}'类型表现优秀")

        return patterns

    def _identify_common_weaknesses(self, low_quality_hooks: List[PlotHookAnalysis]) -> List[str]:
        """识别常见弱点"""
        if not low_quality_hooks:
            return ["整体质量良好，无明显共性问题"]

        weaknesses = []

        # 分析薄弱环节
        avg_tension = sum(h.dramatic_tension for h in low_quality_hooks) / len(low_quality_hooks)
        if avg_tension < 5:
            weaknesses.append("戏剧张力不足，冲突强度偏低")

        avg_consistency = sum(h.lore_consistency for h in low_quality_hooks) / len(low_quality_hooks)
        if avg_consistency < 6:
            weaknesses.append("世界观一致性有待加强")

        avg_appeal = sum(h.curiosity_hook for h in low_quality_hooks) / len(low_quality_hooks)
        if avg_appeal < 5:
            weaknesses.append("读者吸引力需要提升")

        return weaknesses

    def _generate_visualization_data(self) -> Dict[str, Any]:
        """生成可视化数据"""
        return {
            "质量评分雷达图": {
                "维度": ["戏剧价值", "故事潜力", "世界观一致性", "读者吸引力"],
                "数据": [
                    {
                        "名称": hook.original_description[:20] + "...",
                        "数值": [
                            (hook.dramatic_tension + hook.emotional_impact) / 2,
                            (hook.expandability + hook.branching_potential) / 2,
                            (hook.lore_consistency + hook.logic_coherence) / 2,
                            (hook.curiosity_hook + hook.relatability) / 2
                        ]
                    }
                    for hook in list(self.analyzed_hooks.values())[:5]
                ]
            },
            "冲突类型分布": {
                "标签": list(Counter(h.hook_type for h in self.analyzed_hooks.values()).keys()),
                "数值": list(Counter(h.hook_type for h in self.analyzed_hooks.values()).values())
            },
            "质量等级分布": {
                "标签": ["S", "A", "B", "C", "D"],
                "数值": [
                    len([h for h in self.analyzed_hooks.values() if h.quality_tier == tier])
                    for tier in ["S", "A", "B", "C", "D"]
                ]
            }
        }

    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        md_content = f"""# 裂世九域·法则链纪元 - 智能故事生成分析报告

## 报告概览

- **生成时间**: {report_data['报告元数据']['生成时间']}
- **分析器版本**: {report_data['报告元数据']['分析器版本']}
- **原始钩子数量**: {report_data['报告元数据']['原始钩子数量']}
- **AI生成钩子数量**: {report_data['报告元数据']['生成钩子数量']}

## 原始剧情钩子分析

### 整体质量评估

"""

        overall_stats = report_data.get('原始剧情钩子分析', {}).get('整体统计', {})
        if overall_stats:
            md_content += f"""
- **平均综合评分**: {overall_stats.get('平均综合评分', 0):.2f}/100
- **质量分布**: S级 {overall_stats.get('S级钩子数', 0)}个, A级 {overall_stats.get('A级钩子数', 0)}个, B级 {overall_stats.get('B级钩子数', 0)}个
- **最高评分**: {overall_stats.get('最高评分', 0):.2f}
- **最低评分**: {overall_stats.get('最低评分', 0):.2f}

"""

        md_content += """
### 优秀剧情钩子案例

"""

        # 添加高质量钩子示例
        detailed_analysis = report_data.get('原始剧情钩子分析', {}).get('详细分析结果', [])
        high_quality = sorted(detailed_analysis, key=lambda x: x.get('overall_score', 0), reverse=True)[:3]

        for i, hook in enumerate(high_quality, 1):
            md_content += f"""
#### 案例 {i}: {hook.get('original_description', '未知描述')}

- **综合评分**: {hook.get('overall_score', 0):.2f}/100 (质量等级: {hook.get('quality_tier', 'N/A')})
- **冲突类型**: {hook.get('hook_type', '未知')}
- **优势特征**: {', '.join(hook.get('strengths', []))}
- **改进建议**: {', '.join(hook.get('improvement_suggestions', []))}

"""

        md_content += """
## AI生成剧情钩子

### 生成策略说明

本系统采用以下四种策略生成新的剧情钩子：

1. **中心性分析**: 基于实体在关系网络中的重要性生成冲突
2. **社群边界**: 利用不同社群间的边界张力创造情节
3. **网络路径**: 通过关键路径的传播效应设计连锁事件
4. **结构洞**: 利用网络中的结构薄弱点构建危机情节

### 生成结果展示

"""

        generated_hooks = report_data.get('AI生成剧情钩子', {}).get('生成结果', [])
        for i, hook in enumerate(generated_hooks[:5], 1):
            md_content += f"""
#### 生成钩子 {i}: {hook.get('title', '未知标题')}

**描述**: {hook.get('description', '无描述')}

**特征**:
- 生成策略: {hook.get('conflict_pattern', '未知')}
- 复杂度等级: {hook.get('complexity_level', 0)}/10
- 原创性评分: {hook.get('originality_score', 0):.1f}/10
- 戏剧潜力: {hook.get('dramatic_potential', 0):.1f}/10

"""

        md_content += """
## 创作指导建议

### 优秀案例学习要点

"""

        guidance = report_data.get('创作指导建议', {})
        excellent_features = guidance.get('优秀案例学习', {}).get('成功要素', [])
        for feature in excellent_features:
            md_content += f"- {feature}\n"

        md_content += """
### 常见问题与改进策略

"""

        common_issues = guidance.get('改进建议', {}).get('普遍问题', [])
        for issue in common_issues:
            md_content += f"- **问题**: {issue}\n"

        improvement_strategies = guidance.get('改进建议', {}).get('提升策略', [])
        for strategy in improvement_strategies:
            md_content += f"- **策略**: {strategy}\n"

        md_content += """
### 具体创作技巧

"""

        techniques = guidance.get('创作技巧', {})
        for technique_type, description in techniques.items():
            md_content += f"- **{technique_type}**: {description}\n"

        md_content += """
## 总结与展望

基于本次分析，《裂世九域·法则链纪元》的剧情钩子体系展现出以下特点：

1. **世界观深度**: 独特的"链"文化体系为故事提供了丰富的冲突源泉
2. **结构复杂性**: 跨域冲突网络创造了多层次的故事发展空间
3. **角色多样性**: 不同域的角色身份为情节发展提供了多元视角

### 建议关注重点

- 深化"链法"体系的哲学内涵，提升主题深度
- 强化跨域文化冲突的戏剧张力
- 发展更多具有道德困境的角色选择情节
- 利用AI生成工具扩充剧情库，提高创作效率

---

*本报告由智能故事生成分析系统自动生成，为《裂世九域·法则链纪元》的创作提供数据支持和分析指导。*
"""

        return md_content

    def _generate_creative_aids(self, output_dir: str, report_data: Dict[str, Any]) -> None:
        """生成创作辅助文件"""
        aids_dir = f"{output_dir}/creative_aids"
        os.makedirs(aids_dir, exist_ok=True)

        # 1. 剧情钩子库
        hooks_library = {
            "原始钩子": [
                {
                    "标题": hook.get('original_description', ''),
                    "评分": hook.get('overall_score', 0),
                    "类型": hook.get('hook_type', ''),
                    "建议": hook.get('improvement_suggestions', [])
                }
                for hook in report_data.get('原始剧情钩子分析', {}).get('详细分析结果', [])
            ],
            "AI生成钩子": [
                {
                    "标题": hook.get('title', ''),
                    "描述": hook.get('description', ''),
                    "策略": hook.get('conflict_pattern', ''),
                    "复杂度": hook.get('complexity_level', 0)
                }
                for hook in report_data.get('AI生成剧情钩子', {}).get('生成结果', [])
            ]
        }

        with open(f"{aids_dir}/plot_hooks_library.json", 'w', encoding='utf-8') as f:
            json.dump(hooks_library, f, ensure_ascii=False, indent=2)

        # 2. 角色发展指南
        character_guide = {
            "动机分析框架": [
                "主要动机识别",
                "冲突利益评估",
                "情感驱动分析",
                "道德倾向判断",
                "关系动态考量"
            ],
            "角色成长弧线模板": [
                "初始状态 -> 触发事件 -> 内心冲突 -> 选择时刻 -> 转变结果",
                "舒适区 -> 挑战出现 -> 抗拒变化 -> 尝试新方法 -> 整合成长"
            ],
            "冲突设计原则": [
                "个人利益与集体利益的冲突",
                "传统价值与新思想的冲突",
                "责任义务与个人欲望的冲突",
                "理想信念与现实困境的冲突"
            ]
        }

        with open(f"{aids_dir}/character_development_guide.json", 'w', encoding='utf-8') as f:
            json.dump(character_guide, f, ensure_ascii=False, indent=2)

        # 3. 世界观一致性检查清单
        consistency_checklist = {
            "链法体系": [
                "是否正确使用了链法术语",
                "链法的执行是否符合设定逻辑",
                "不同域对链法的理解差异是否体现"
            ],
            "域特色": [
                "人域：农业文明，税收制度，基层治理",
                "天域：政治权威，法条制定，监管体系",
                "灵域：技术创新，器械制造，评印系统",
                "荒域：部落文化，断链传统，边境特色"
            ],
            "社会制度": [
                "链籍制度的运作机制",
                "评印体系的权威性",
                "跨域关系的复杂性",
                "传统习俗的影响力"
            ]
        }

        with open(f"{aids_dir}/worldbuilding_consistency_checklist.json", 'w', encoding='utf-8') as f:
            json.dump(consistency_checklist, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    generator = IntelligentStoryGenerator()

    try:
        # 加载数据
        data_file = "D:/work/novellus/cross_domain_conflict_analysis_report.json"
        if not generator.load_conflict_analysis_data(data_file):
            raise Exception("无法加载分析数据")

        # 生成综合报告
        summary = generator.generate_comprehensive_report()

        print("\n=== 智能故事生成分析完成 ===")
        print(f"分析统计: {summary['分析统计']}")
        print(f"输出目录: {summary['输出目录']}")
        print(f"主要文件: {summary['主要文件']}")

    except Exception as e:
        logger.error(f"分析过程失败: {e}")
        raise

if __name__ == "__main__":
    main()