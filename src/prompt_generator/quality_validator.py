"""
生成内容质量验证器
检查AI生成内容的一致性和质量
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    score: float  # 0-100分
    issues: List[Dict[str, Any]]
    warnings: List[str]
    suggestions: List[str]
    details: Dict[str, Any]


@dataclass
class ConsistencyCheck:
    """一致性检查项"""
    category: str  # worldbuilding/character/plot/style
    item: str
    expected: Any
    actual: Any
    severity: str  # critical/major/minor/warning
    message: str


class QualityValidator:
    """质量验证器"""

    # 评分权重
    SCORE_WEIGHTS = {
        "consistency": 0.35,  # 一致性
        "coherence": 0.25,    # 连贯性
        "creativity": 0.20,   # 创意性
        "engagement": 0.20    # 吸引力
    }

    # 严重级别分数扣减
    SEVERITY_PENALTY = {
        "critical": 20,
        "major": 10,
        "minor": 5,
        "warning": 2
    }

    def __init__(self, novel_context: Optional[Dict[str, Any]] = None):
        """
        初始化验证器

        Args:
            novel_context: 小说上下文信息
        """
        self.novel_context = novel_context or {}
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载验证规则"""
        return {
            "worldbuilding": [
                {
                    "rule": "no_modern_tech",
                    "pattern": r"(手机|电脑|互联网|汽车|飞机)",
                    "message": "发现现代科技元素，与世界观不符"
                },
                {
                    "rule": "law_chain_usage",
                    "pattern": r"使用.*法则链",
                    "check": self._check_law_chain_validity,
                    "message": "法则链使用需要符合设定"
                }
            ],
            "character": [
                {
                    "rule": "name_consistency",
                    "check": self._check_character_names,
                    "message": "角色名称必须一致"
                },
                {
                    "rule": "behavior_consistency",
                    "check": self._check_character_behavior,
                    "message": "角色行为需符合性格设定"
                }
            ],
            "plot": [
                {
                    "rule": "causal_logic",
                    "check": self._check_causality,
                    "message": "情节发展需要因果逻辑"
                },
                {
                    "rule": "conflict_progression",
                    "check": self._check_conflict_progression,
                    "message": "冲突发展需要合理"
                }
            ],
            "style": [
                {
                    "rule": "narrative_voice",
                    "check": self._check_narrative_voice,
                    "message": "叙事视角需要一致"
                },
                {
                    "rule": "tone_consistency",
                    "check": self._check_tone,
                    "message": "文风语调需要统一"
                }
            ]
        }

    async def validate_content(
        self,
        content: str,
        expected_context: Dict[str, Any],
        validation_level: str = "standard"
    ) -> ValidationResult:
        """
        验证生成内容

        Args:
            content: 生成的内容
            expected_context: 期望的上下文
            validation_level: 验证级别 (quick/standard/thorough)

        Returns:
            验证结果
        """
        issues = []
        warnings = []
        suggestions = []
        scores = {}

        # 1. 一致性检查
        consistency_checks = await self._check_consistency(content, expected_context)
        consistency_score = self._calculate_consistency_score(consistency_checks)
        scores["consistency"] = consistency_score

        for check in consistency_checks:
            if check.severity == "critical" or check.severity == "major":
                issues.append({
                    "type": check.category,
                    "severity": check.severity,
                    "message": check.message,
                    "item": check.item
                })
            else:
                warnings.append(check.message)

        # 2. 连贯性检查
        coherence_score = self._check_coherence(content)
        scores["coherence"] = coherence_score

        # 3. 创意性评估
        creativity_score = self._evaluate_creativity(content, expected_context)
        scores["creativity"] = creativity_score

        # 4. 吸引力评估
        engagement_score = self._evaluate_engagement(content)
        scores["engagement"] = engagement_score

        # 计算总分
        total_score = sum(
            score * self.SCORE_WEIGHTS[category]
            for category, score in scores.items()
        )

        # 生成建议
        if consistency_score < 70:
            suggestions.append("建议加强世界观和角色设定的一致性")
        if coherence_score < 70:
            suggestions.append("建议改善段落之间的逻辑连接")
        if creativity_score < 70:
            suggestions.append("可以增加更多创意元素和意外转折")
        if engagement_score < 70:
            suggestions.append("建议增强场景描写和情感渲染")

        # 判断是否通过验证
        is_valid = (
            len([i for i in issues if i["severity"] == "critical"]) == 0 and
            total_score >= 60
        )

        return ValidationResult(
            is_valid=is_valid,
            score=total_score,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions,
            details={
                "scores": scores,
                "content_length": len(content),
                "validation_level": validation_level,
                "timestamp": datetime.now().isoformat()
            }
        )

    async def _check_consistency(
        self,
        content: str,
        expected_context: Dict[str, Any]
    ) -> List[ConsistencyCheck]:
        """检查一致性"""
        checks = []

        # 世界观一致性
        for rule in self.validation_rules["worldbuilding"]:
            if "pattern" in rule:
                matches = re.findall(rule["pattern"], content)
                if matches:
                    checks.append(ConsistencyCheck(
                        category="worldbuilding",
                        item=rule["rule"],
                        expected="无现代元素",
                        actual=matches[0],
                        severity="major",
                        message=rule["message"]
                    ))

            if "check" in rule:
                result = rule["check"](content, expected_context)
                if result:
                    checks.extend(result)

        # 角色一致性
        if "characters" in expected_context:
            character_checks = self._check_character_consistency(
                content,
                expected_context["characters"]
            )
            checks.extend(character_checks)

        return checks

    def _check_character_consistency(
        self,
        content: str,
        expected_characters: List[Dict[str, Any]]
    ) -> List[ConsistencyCheck]:
        """检查角色一致性"""
        checks = []

        for character in expected_characters:
            name = character["name"]

            # 检查角色名称
            name_variations = self._find_name_variations(content, name)
            if name_variations:
                checks.append(ConsistencyCheck(
                    category="character",
                    item=f"角色名称_{name}",
                    expected=name,
                    actual=name_variations,
                    severity="minor",
                    message=f"角色{name}的名称出现变化"
                ))

            # 检查性格一致性
            if "personality" in character:
                personality_issues = self._check_personality_consistency(
                    content,
                    name,
                    character["personality"]
                )
                checks.extend(personality_issues)

        return checks

    def _find_name_variations(self, content: str, expected_name: str) -> List[str]:
        """查找名称变化"""
        variations = []

        # 查找相似但不同的名称
        # 这里简化处理，实际可以用更复杂的算法
        similar_pattern = expected_name[:-1] + r".{1,2}"
        matches = re.findall(similar_pattern, content)

        for match in matches:
            if match != expected_name and match not in variations:
                variations.append(match)

        return variations

    def _check_personality_consistency(
        self,
        content: str,
        character_name: str,
        personality: Dict[str, Any]
    ) -> List[ConsistencyCheck]:
        """检查性格一致性"""
        checks = []

        # 这里简化处理
        # 实际应该用NLP技术分析角色行为是否符合性格

        return checks

    def _check_law_chain_validity(
        self,
        content: str,
        context: Dict[str, Any]
    ) -> List[ConsistencyCheck]:
        """检查法则链使用有效性"""
        checks = []

        # 查找法则链使用
        chain_usage = re.findall(r"(\w+)链", content)

        valid_chains = [
            "命运", "因果", "时空", "生死", "混沌", "权柄",
            "名真", "记忆", "界域", "形质", "映象", "共鸣"
        ]

        for chain in chain_usage:
            if chain not in valid_chains:
                checks.append(ConsistencyCheck(
                    category="worldbuilding",
                    item="法则链",
                    expected=valid_chains,
                    actual=chain,
                    severity="major",
                    message=f"使用了不存在的法则链：{chain}链"
                ))

        return checks

    def _check_character_names(self, content: str, context: Dict[str, Any]) -> List[ConsistencyCheck]:
        """检查角色名称"""
        # 简化实现
        return []

    def _check_character_behavior(self, content: str, context: Dict[str, Any]) -> List[ConsistencyCheck]:
        """检查角色行为"""
        # 简化实现
        return []

    def _check_causality(self, content: str, context: Dict[str, Any]) -> List[ConsistencyCheck]:
        """检查因果逻辑"""
        # 简化实现
        return []

    def _check_conflict_progression(self, content: str, context: Dict[str, Any]) -> List[ConsistencyCheck]:
        """检查冲突发展"""
        # 简化实现
        return []

    def _check_narrative_voice(self, content: str, context: Dict[str, Any]) -> List[ConsistencyCheck]:
        """检查叙事视角"""
        # 简化实现
        return []

    def _check_tone(self, content: str, context: Dict[str, Any]) -> List[ConsistencyCheck]:
        """检查文风语调"""
        # 简化实现
        return []

    def _calculate_consistency_score(self, checks: List[ConsistencyCheck]) -> float:
        """计算一致性分数"""
        if not checks:
            return 100.0

        base_score = 100.0

        for check in checks:
            base_score -= self.SEVERITY_PENALTY.get(check.severity, 0)

        return max(0, base_score)

    def _check_coherence(self, content: str) -> float:
        """检查连贯性"""
        score = 80.0  # 基础分

        # 检查段落过渡
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            # 检查是否有过渡词
            transition_words = ["然而", "但是", "接着", "随后", "与此同时", "另一方面"]
            transition_count = sum(
                1 for word in transition_words
                if word in content
            )

            if transition_count > 0:
                score += min(10, transition_count * 2)

        # 检查时间线索
        time_markers = ["此时", "这时", "片刻后", "不久", "随即", "转瞬间"]
        time_count = sum(1 for marker in time_markers if marker in content)
        if time_count > 0:
            score += min(10, time_count * 2)

        return min(100, score)

    def _evaluate_creativity(self, content: str, context: Dict[str, Any]) -> float:
        """评估创意性"""
        score = 70.0  # 基础分

        # 检查独特描述
        unique_descriptions = [
            r"如\w{2,4}般",  # 比喻
            r"仿佛\w+",     # 类比
            r"宛\w+",       # 形容
        ]

        for pattern in unique_descriptions:
            if re.search(pattern, content):
                score += 5

        # 检查创意法则链组合
        if "法则链" in content:
            combinations = re.findall(r"(\w+链).*?(\w+链)", content)
            if combinations:
                score += min(15, len(combinations) * 5)

        return min(100, score)

    def _evaluate_engagement(self, content: str) -> float:
        """评估吸引力"""
        score = 75.0  # 基础分

        # 检查对话比例
        dialogue_lines = len(re.findall(r'".*?"', content))
        total_lines = len(content.split('\n'))

        if total_lines > 0:
            dialogue_ratio = dialogue_lines / total_lines
            if 0.2 <= dialogue_ratio <= 0.5:
                score += 10

        # 检查感官描写
        sensory_words = ["看", "听", "闻", "触", "尝", "感"]
        sensory_count = sum(1 for word in sensory_words if word in content)
        score += min(10, sensory_count * 2)

        # 检查情感词汇
        emotion_patterns = ["惊", "怒", "喜", "悲", "恐", "思"]
        emotion_count = sum(1 for pattern in emotion_patterns if pattern in content)
        score += min(5, emotion_count)

        return min(100, score)

    async def generate_correction_prompt(
        self,
        content: str,
        validation_result: ValidationResult
    ) -> str:
        """
        生成修正prompt

        Args:
            content: 原始内容
            validation_result: 验证结果

        Returns:
            修正prompt
        """
        issues_summary = "\n".join([
            f"- {issue['message']}"
            for issue in validation_result.issues
        ])

        suggestions_summary = "\n".join(validation_result.suggestions)

        correction_prompt = f"""请修正以下内容中的问题：

## 原始内容
{content[:500]}...

## 发现的问题
{issues_summary}

## 改进建议
{suggestions_summary}

请重新创作，确保：
1. 解决所有提到的问题
2. 保持原有剧情的主线
3. 改善整体质量和一致性
"""

        return correction_prompt

    def generate_quality_report(self, validation_results: List[ValidationResult]) -> str:
        """
        生成质量报告

        Args:
            validation_results: 验证结果列表

        Returns:
            质量报告文本
        """
        total_validations = len(validation_results)
        passed = sum(1 for r in validation_results if r.is_valid)
        average_score = sum(r.score for r in validation_results) / total_validations if total_validations > 0 else 0

        # 统计问题类型
        issue_stats = {}
        for result in validation_results:
            for issue in result.issues:
                issue_type = issue["type"]
                if issue_type not in issue_stats:
                    issue_stats[issue_type] = 0
                issue_stats[issue_type] += 1

        report = f"""# 内容质量验证报告

## 总体统计
- 验证次数：{total_validations}
- 通过次数：{passed}
- 通过率：{(passed/total_validations*100):.1f}%
- 平均得分：{average_score:.1f}/100

## 问题分布
"""
        for issue_type, count in issue_stats.items():
            report += f"- {issue_type}：{count}次\n"

        report += """
## 改进建议
1. 重点关注一致性问题，确保内容符合世界观设定
2. 加强角色塑造，保持行为的连贯性
3. 提升创意元素，增加阅读吸引力
"""

        return report