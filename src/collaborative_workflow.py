"""
人工AI协作创作工作流系统
支持用户手动与AI交互的创作模式
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import uuid
import asyncio
from pathlib import Path

from database.data_access import get_novel_manager
from prompt_generator.core import NovelPromptGenerator


class SessionStatus(Enum):
    """会话状态"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class ContentType(Enum):
    """内容类型"""
    SCENE = "scene"
    DIALOGUE = "dialogue"
    ACTION = "action"
    DESCRIPTION = "description"
    TRANSITION = "transition"
    CHAPTER_OPENING = "chapter_opening"
    CHAPTER_ENDING = "chapter_ending"
    BREAKTHROUGH = "breakthrough"


@dataclass
class PromptComponents:
    """Prompt组件"""
    system_prompt: str
    user_prompt: str
    suggested_max_tokens: int = 2000
    suggested_temperature: float = 0.8
    model_recommendation: str = "Claude 3.5 Sonnet"
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """分析结果"""
    # 基础质量指标
    length_analysis: Dict[str, Any]
    structure_analysis: Dict[str, Any]
    character_consistency: Dict[str, Any]
    world_consistency: Dict[str, Any]

    # 创作质量评估
    narrative_flow: Dict[str, Any]
    dialogue_quality: Dict[str, Any]
    scene_vividness: Dict[str, Any]
    emotional_impact: Dict[str, Any]

    # 法则链系统符合度
    law_chain_accuracy: Dict[str, Any]
    power_system_consistency: Dict[str, Any]

    # 改进建议
    strengths: List[str]
    weaknesses: List[str]
    specific_suggestions: List[str]
    prompt_optimization_tips: List[str]

    # 总体评分
    overall_score: float = 0.0
    recommendation: str = ""


@dataclass
class CreationSession:
    """创作会话"""
    session_id: str
    novel_id: str
    chapter_number: int
    created_at: datetime
    session_name: str = ""

    # Prompt相关
    original_prompt: Optional[PromptComponents] = None
    prompt_iterations: List[PromptComponents] = field(default_factory=list)

    # 内容相关
    generated_contents: List[str] = field(default_factory=list)
    user_ratings: List[int] = field(default_factory=list)
    analysis_results: List[AnalysisResult] = field(default_factory=list)

    # 最终结果
    final_content: Optional[str] = None
    session_notes: str = ""
    status: SessionStatus = SessionStatus.ACTIVE

    # 统计信息
    iteration_count: int = 0
    total_time_minutes: float = 0.0
    best_iteration_index: Optional[int] = None


class ContentAnalyzer:
    """内容分析器"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _analyze_length(self, content: str) -> Dict[str, Any]:
        """分析内容长度"""
        words = content.split()
        sentences = content.split('。')
        paragraphs = content.split('\n\n')

        return {
            "character_count": len(content),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "avg_paragraph_length": len(words) / max(len(paragraphs), 1)
        }

    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """分析内容结构"""
        has_dialogue = '"' in content or '"' in content
        has_action = any(word in content for word in ['跃起', '出手', '攻击', '躲避', '施展'])
        has_description = any(word in content for word in ['天空', '大地', '景色', '环境'])

        # 段落类型分析
        paragraphs = content.split('\n\n')
        dialogue_paragraphs = sum(1 for p in paragraphs if '"' in p or '"' in p)
        action_paragraphs = sum(1 for p in paragraphs if any(w in p for w in ['跃起', '出手', '攻击']))

        return {
            "has_dialogue": has_dialogue,
            "has_action": has_action,
            "has_description": has_description,
            "dialogue_ratio": dialogue_paragraphs / max(len(paragraphs), 1),
            "action_ratio": action_paragraphs / max(len(paragraphs), 1),
            "paragraph_types": {
                "total": len(paragraphs),
                "dialogue": dialogue_paragraphs,
                "action": action_paragraphs,
                "mixed": len(paragraphs) - dialogue_paragraphs - action_paragraphs
            }
        }

    def _check_character_consistency(self, content: str, characters: List[str] = None) -> Dict[str, Any]:
        """检查角色一致性"""
        issues = []
        character_mentions = {}

        if characters:
            for char in characters:
                count = content.count(char)
                character_mentions[char] = count
                if count == 0:
                    issues.append(f"角色 {char} 未出现在内容中")

        return {
            "character_mentions": character_mentions,
            "consistency_issues": issues,
            "is_consistent": len(issues) == 0
        }

    def _check_world_consistency(self, content: str) -> Dict[str, Any]:
        """检查世界观一致性"""
        # 检查法则链相关术语
        law_chain_terms = ['法则链', '法则之力', '掌控者', '共鸣', '法则空间']
        power_terms = ['境界', '突破', '瓶颈', '感悟']

        found_terms = {
            "law_chain": [term for term in law_chain_terms if term in content],
            "power_system": [term for term in power_terms if term in content]
        }

        return {
            "found_world_terms": found_terms,
            "law_chain_mentioned": len(found_terms["law_chain"]) > 0,
            "power_system_mentioned": len(found_terms["power_system"]) > 0
        }

    def _evaluate_narrative_flow(self, content: str) -> Dict[str, Any]:
        """评估叙事流畅度"""
        # 检查过渡词
        transition_words = ['然而', '但是', '随后', '接着', '与此同时', '突然', '渐渐']
        transitions_found = sum(1 for word in transition_words if word in content)

        # 检查时间标记
        time_markers = ['片刻', '瞬间', '许久', '不久', '此时', '当下']
        time_markers_found = sum(1 for marker in time_markers if marker in content)

        return {
            "transition_count": transitions_found,
            "time_markers_count": time_markers_found,
            "flow_score": min((transitions_found + time_markers_found) / 10, 1.0),
            "has_good_flow": transitions_found >= 2
        }

    def _evaluate_dialogue(self, content: str) -> Dict[str, Any]:
        """评估对话质量"""
        import re

        # 提取对话
        dialogues = re.findall(r'[""](.*?)["""]', content)

        if not dialogues:
            return {
                "dialogue_count": 0,
                "avg_dialogue_length": 0,
                "quality_score": 0,
                "issues": ["无对话内容"]
            }

        avg_length = sum(len(d) for d in dialogues) / len(dialogues)

        # 检查对话多样性
        unique_starters = len(set(d.split('，')[0] if '，' in d else d[:10] for d in dialogues))
        diversity_score = unique_starters / len(dialogues)

        return {
            "dialogue_count": len(dialogues),
            "avg_dialogue_length": avg_length,
            "diversity_score": diversity_score,
            "quality_score": diversity_score * 0.7 + min(avg_length / 50, 1.0) * 0.3,
            "issues": []
        }

    def _evaluate_scene_description(self, content: str) -> Dict[str, Any]:
        """评估场景描写"""
        # 感官词汇
        visual_words = ['看见', '瞥见', '注视', '色彩', '光芒', '阴影', '明亮', '黑暗']
        auditory_words = ['听到', '声音', '轰鸣', '低语', '回响', '寂静']
        tactile_words = ['触摸', '感受', '冰冷', '温暖', '粗糙', '光滑']

        visual_count = sum(1 for word in visual_words if word in content)
        auditory_count = sum(1 for word in auditory_words if word in content)
        tactile_count = sum(1 for word in tactile_words if word in content)

        sensory_richness = (visual_count + auditory_count + tactile_count) / 15

        return {
            "visual_elements": visual_count,
            "auditory_elements": auditory_count,
            "tactile_elements": tactile_count,
            "sensory_richness_score": min(sensory_richness, 1.0),
            "is_vivid": sensory_richness > 0.3
        }

    def _evaluate_emotional_impact(self, content: str) -> Dict[str, Any]:
        """评估情感冲击力"""
        # 情感词汇
        emotion_words = {
            "positive": ['喜悦', '兴奋', '欣慰', '满足', '自豪', '希望'],
            "negative": ['愤怒', '悲伤', '绝望', '恐惧', '焦虑', '失望'],
            "intense": ['震撼', '惊骇', '狂喜', '崩溃', '疯狂', '极致']
        }

        emotion_counts = {}
        for category, words in emotion_words.items():
            emotion_counts[category] = sum(1 for word in words if word in content)

        total_emotions = sum(emotion_counts.values())
        intensity = emotion_counts.get("intense", 0) / max(total_emotions, 1)

        return {
            "emotion_counts": emotion_counts,
            "total_emotions": total_emotions,
            "emotional_intensity": intensity,
            "impact_score": min(total_emotions / 10, 1.0) * 0.7 + intensity * 0.3
        }

    def _check_law_chain_usage(self, content: str) -> Dict[str, Any]:
        """检查法则链系统使用"""
        # 法则链相关检查
        law_chains = ['时间', '空间', '生命', '死亡', '因果', '轮回', '创造', '毁灭', '平衡']
        mentioned_chains = [chain for chain in law_chains if chain in content and '法则' in content]

        # 检查法则链描述的准确性
        accuracy_issues = []
        if '时间法则' in content and '空间' not in content:
            accuracy_issues.append("时间法则通常与空间法则相关联")

        return {
            "mentioned_law_chains": mentioned_chains,
            "chain_count": len(mentioned_chains),
            "accuracy_issues": accuracy_issues,
            "usage_score": min(len(mentioned_chains) / 3, 1.0)
        }

    def _check_power_system(self, content: str) -> Dict[str, Any]:
        """检查力量体系一致性"""
        # 境界相关
        realms = ['凡人', '筑基', '金丹', '元婴', '化神', '合体', '渡劫', '大乘', '掌控者']
        mentioned_realms = [realm for realm in realms if realm in content]

        # 检查境界描述的逻辑性
        consistency_issues = []
        realm_indices = {realm: i for i, realm in enumerate(realms)}

        if len(mentioned_realms) > 1:
            indices = [realm_indices[r] for r in mentioned_realms]
            if max(indices) - min(indices) > 3:
                consistency_issues.append("境界跨度过大，可能存在逻辑问题")

        return {
            "mentioned_realms": mentioned_realms,
            "consistency_issues": consistency_issues,
            "is_consistent": len(consistency_issues) == 0
        }

    async def comprehensive_analysis(
        self,
        content: str,
        prompt_used: Optional[PromptComponents] = None,
        world_context: Dict = None,
        user_expectations: Dict = None,
        focus_characters: List[str] = None
    ) -> AnalysisResult:
        """全面分析生成内容"""

        # 执行各项分析
        length_analysis = self._analyze_length(content)
        structure_analysis = self._analyze_structure(content)
        character_consistency = self._check_character_consistency(content, focus_characters)
        world_consistency = self._check_world_consistency(content)
        narrative_flow = self._evaluate_narrative_flow(content)
        dialogue_quality = self._evaluate_dialogue(content)
        scene_vividness = self._evaluate_scene_description(content)
        emotional_impact = self._evaluate_emotional_impact(content)
        law_chain_accuracy = self._check_law_chain_usage(content)
        power_system_consistency = self._check_power_system(content)

        # 收集优点
        strengths = []
        if narrative_flow["has_good_flow"]:
            strengths.append("叙事流畅，过渡自然")
        if dialogue_quality.get("quality_score", 0) > 0.7:
            strengths.append("对话生动，富有个性")
        if scene_vividness["is_vivid"]:
            strengths.append("场景描写细腻，感官丰富")
        if law_chain_accuracy["chain_count"] > 0:
            strengths.append("法则链系统运用得当")

        # 收集缺点
        weaknesses = []
        if not narrative_flow["has_good_flow"]:
            weaknesses.append("叙事缺少过渡，显得生硬")
        if dialogue_quality.get("quality_score", 0) < 0.5:
            weaknesses.append("对话质量有待提升")
        if not scene_vividness["is_vivid"]:
            weaknesses.append("场景描写不够生动")
        if character_consistency["consistency_issues"]:
            weaknesses.extend(character_consistency["consistency_issues"])

        # 生成具体建议
        specific_suggestions = []
        if narrative_flow["transition_count"] < 2:
            specific_suggestions.append("增加过渡词和时间标记，让叙事更流畅")
        if dialogue_quality.get("dialogue_count", 0) < 3:
            specific_suggestions.append("适当增加对话，让角色更立体")
        if scene_vividness["sensory_richness_score"] < 0.3:
            specific_suggestions.append("加入更多感官描写，如视觉、听觉、触觉等")
        if law_chain_accuracy["chain_count"] == 0:
            specific_suggestions.append("考虑加入法则链相关的描述，增强世界观特色")

        # Prompt优化建议
        prompt_optimization_tips = []
        if length_analysis["word_count"] < 500:
            prompt_optimization_tips.append("在prompt中明确要求更详细的描写")
        if not dialogue_quality.get("dialogue_count"):
            prompt_optimization_tips.append("在prompt中要求包含角色对话")
        if not law_chain_accuracy["mentioned_law_chains"]:
            prompt_optimization_tips.append("在prompt中提醒AI关注法则链系统")

        # 计算总体评分
        scores = [
            narrative_flow.get("flow_score", 0) * 0.2,
            dialogue_quality.get("quality_score", 0) * 0.2,
            scene_vividness.get("sensory_richness_score", 0) * 0.15,
            emotional_impact.get("impact_score", 0) * 0.15,
            law_chain_accuracy.get("usage_score", 0) * 0.15,
            (1.0 if power_system_consistency["is_consistent"] else 0.5) * 0.15
        ]
        overall_score = sum(scores)

        # 生成推荐
        if overall_score > 0.8:
            recommendation = "优秀！可以直接使用或稍作润色"
        elif overall_score > 0.6:
            recommendation = "良好，建议根据具体建议进行优化"
        elif overall_score > 0.4:
            recommendation = "一般，需要较大幅度的改进"
        else:
            recommendation = "需要重新生成或大幅修改"

        return AnalysisResult(
            length_analysis=length_analysis,
            structure_analysis=structure_analysis,
            character_consistency=character_consistency,
            world_consistency=world_consistency,
            narrative_flow=narrative_flow,
            dialogue_quality=dialogue_quality,
            scene_vividness=scene_vividness,
            emotional_impact=emotional_impact,
            law_chain_accuracy=law_chain_accuracy,
            power_system_consistency=power_system_consistency,
            strengths=strengths,
            weaknesses=weaknesses,
            specific_suggestions=specific_suggestions,
            prompt_optimization_tips=prompt_optimization_tips,
            overall_score=overall_score,
            recommendation=recommendation
        )


class CreationSessionManager:
    """创作会话管理器"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.sessions: Dict[str, CreationSession] = {}
        self.session_storage_path = Path("creation_sessions")
        self.session_storage_path.mkdir(exist_ok=True)

    async def create_session(
        self,
        novel_id: str,
        chapter_number: int,
        session_name: str = ""
    ) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())

        if not session_name:
            session_name = f"第{chapter_number}章创作会话_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = CreationSession(
            session_id=session_id,
            novel_id=novel_id,
            chapter_number=chapter_number,
            created_at=datetime.now(),
            session_name=session_name
        )

        self.sessions[session_id] = session
        await self._save_session(session)

        return session_id

    async def add_content_iteration(
        self,
        session_id: str,
        content: str,
        user_rating: int,
        analysis: AnalysisResult,
        prompt_used: Optional[PromptComponents] = None
    ):
        """添加内容迭代"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.generated_contents.append(content)
        session.user_ratings.append(user_rating)
        session.analysis_results.append(analysis)

        if prompt_used:
            session.prompt_iterations.append(prompt_used)

        session.iteration_count += 1

        # 更新最佳迭代
        if user_rating >= 8 or (session.best_iteration_index is None):
            if session.best_iteration_index is None or user_rating > session.user_ratings[session.best_iteration_index]:
                session.best_iteration_index = len(session.user_ratings) - 1

        await self._save_session(session)

    async def get_session(self, session_id: str) -> Optional[CreationSession]:
        """获取会话"""
        if session_id in self.sessions:
            return self.sessions[session_id]

        # 尝试从存储加载
        session_file = self.session_storage_path / f"{session_id}.json"
        if session_file.exists():
            return await self._load_session(session_id)

        return None

    async def update_session_status(
        self,
        session_id: str,
        status: SessionStatus,
        final_content: Optional[str] = None,
        notes: str = ""
    ):
        """更新会话状态"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.status = status

        if final_content:
            session.final_content = final_content

        if notes:
            session.session_notes = notes

        if status == SessionStatus.COMPLETED:
            session.total_time_minutes = (
                datetime.now() - session.created_at
            ).total_seconds() / 60

        await self._save_session(session)

    async def get_session_statistics(self, session_id: str) -> Dict:
        """获取会话统计"""
        session = await self.get_session(session_id)
        if not session:
            return {}

        stats = {
            "session_id": session.session_id,
            "session_name": session.session_name,
            "novel_id": session.novel_id,
            "chapter_number": session.chapter_number,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "iteration_count": session.iteration_count,
            "total_time_minutes": session.total_time_minutes,
            "average_rating": sum(session.user_ratings) / len(session.user_ratings) if session.user_ratings else 0,
            "best_rating": max(session.user_ratings) if session.user_ratings else 0,
            "best_iteration_index": session.best_iteration_index,
            "has_final_content": session.final_content is not None,
            "overall_scores": [r.overall_score for r in session.analysis_results],
            "improvement_trend": self._calculate_improvement_trend(session)
        }

        return stats

    def _calculate_improvement_trend(self, session: CreationSession) -> str:
        """计算改进趋势"""
        if len(session.user_ratings) < 2:
            return "insufficient_data"

        # 比较前半部分和后半部分的平均评分
        mid = len(session.user_ratings) // 2
        first_half_avg = sum(session.user_ratings[:mid]) / mid
        second_half_avg = sum(session.user_ratings[mid:]) / (len(session.user_ratings) - mid)

        if second_half_avg > first_half_avg + 0.5:
            return "improving"
        elif second_half_avg < first_half_avg - 0.5:
            return "declining"
        else:
            return "stable"

    async def _save_session(self, session: CreationSession):
        """保存会话到文件"""
        session_file = self.session_storage_path / f"{session.session_id}.json"

        # 转换为可序列化格式
        session_data = {
            "session_id": session.session_id,
            "novel_id": session.novel_id,
            "chapter_number": session.chapter_number,
            "created_at": session.created_at.isoformat(),
            "session_name": session.session_name,
            "status": session.status.value,
            "iteration_count": session.iteration_count,
            "total_time_minutes": session.total_time_minutes,
            "best_iteration_index": session.best_iteration_index,
            "generated_contents": session.generated_contents,
            "user_ratings": session.user_ratings,
            "final_content": session.final_content,
            "session_notes": session.session_notes
        }

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    async def _load_session(self, session_id: str) -> Optional[CreationSession]:
        """从文件加载会话"""
        session_file = self.session_storage_path / f"{session_id}.json"

        if not session_file.exists():
            return None

        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 重建会话对象
        session = CreationSession(
            session_id=data["session_id"],
            novel_id=data["novel_id"],
            chapter_number=data["chapter_number"],
            created_at=datetime.fromisoformat(data["created_at"]),
            session_name=data["session_name"],
            status=SessionStatus(data["status"]),
            iteration_count=data["iteration_count"],
            total_time_minutes=data["total_time_minutes"],
            best_iteration_index=data["best_iteration_index"],
            generated_contents=data["generated_contents"],
            user_ratings=data["user_ratings"],
            final_content=data["final_content"],
            session_notes=data["session_notes"]
        )

        self.sessions[session_id] = session
        return session


class UserInteractionInterface:
    """用户交互界面"""

    def format_prompt_for_display(self, prompt_components: PromptComponents) -> str:
        """格式化prompt供用户复制"""
        divider = "=" * 50

        formatted = f"""
{divider}
Novellus 创作提示词
{divider}

【系统提示词 / System Prompt】
{'-' * 40}
{prompt_components.system_prompt}

【用户提示词 / User Prompt】
{'-' * 40}
{prompt_components.user_prompt}

【参数建议 / Suggested Parameters】
{'-' * 40}
• 最大Token数: {prompt_components.suggested_max_tokens}
• 温度参数: {prompt_components.suggested_temperature}
• 推荐模型: {prompt_components.model_recommendation}

【使用说明 / Instructions】
{'-' * 40}
1. 将【系统提示词】复制到Claude的System字段（如果可用）
2. 将【用户提示词】复制到对话框
3. 按照参数建议设置AI参数
4. 生成内容后，将结果返回给Novellus进行分析

【快速复制区】
{'-' * 40}
完整提示词（可直接粘贴）:

{prompt_components.system_prompt}

{prompt_components.user_prompt}
{divider}
"""
        return formatted

    def format_analysis_report(self, analysis: AnalysisResult) -> str:
        """格式化分析报告"""
        divider = "=" * 50
        sub_divider = "-" * 40

        # 生成星级评分
        stars = "★" * int(analysis.overall_score * 5) + "☆" * (5 - int(analysis.overall_score * 5))

        report = f"""
{divider}
Novellus 内容分析报告
{divider}

【总体评分】 {stars} ({analysis.overall_score:.2f}/1.00)
【推荐建议】 {analysis.recommendation}

{sub_divider}
【质量指标】
{sub_divider}
• 叙事流畅度: {self._score_to_bar(analysis.narrative_flow.get('flow_score', 0))}
• 对话质量: {self._score_to_bar(analysis.dialogue_quality.get('quality_score', 0))}
• 场景生动性: {self._score_to_bar(analysis.scene_vividness.get('sensory_richness_score', 0))}
• 情感冲击力: {self._score_to_bar(analysis.emotional_impact.get('impact_score', 0))}
• 法则链准确性: {self._score_to_bar(analysis.law_chain_accuracy.get('usage_score', 0))}

{sub_divider}
【内容统计】
{sub_divider}
• 总字数: {analysis.length_analysis['character_count']} 字
• 段落数: {analysis.length_analysis['paragraph_count']} 段
• 对话数: {analysis.dialogue_quality.get('dialogue_count', 0)} 处
• 法则链提及: {', '.join(analysis.law_chain_accuracy['mentioned_law_chains']) if analysis.law_chain_accuracy['mentioned_law_chains'] else '无'}

{sub_divider}
【优点】 ✓
{sub_divider}
"""
        for strength in analysis.strengths:
            report += f"• {strength}\n"

        report += f"""
{sub_divider}
【待改进】 ⚠
{sub_divider}
"""
        for weakness in analysis.weaknesses:
            report += f"• {weakness}\n"

        report += f"""
{sub_divider}
【具体建议】 💡
{sub_divider}
"""
        for i, suggestion in enumerate(analysis.specific_suggestions, 1):
            report += f"{i}. {suggestion}\n"

        if analysis.prompt_optimization_tips:
            report += f"""
{sub_divider}
【Prompt优化建议】 🔧
{sub_divider}
"""
            for tip in analysis.prompt_optimization_tips:
                report += f"• {tip}\n"

        report += f"""
{divider}
"""
        return report

    def _score_to_bar(self, score: float) -> str:
        """将分数转换为进度条"""
        filled = int(score * 10)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        return f"{bar} {score:.1%}"

    def format_session_summary(self, stats: Dict) -> str:
        """格式化会话摘要"""
        divider = "=" * 50

        summary = f"""
{divider}
创作会话摘要
{divider}

会话名称: {stats['session_name']}
状态: {stats['status']}
创建时间: {stats['created_at']}
迭代次数: {stats['iteration_count']}
总用时: {stats['total_time_minutes']:.1f} 分钟

平均评分: {stats['average_rating']:.1f}/10
最高评分: {stats['best_rating']}/10
最佳版本: 第 {(stats['best_iteration_index'] + 1) if stats['best_iteration_index'] is not None else '无'} 次迭代

改进趋势: {self._translate_trend(stats['improvement_trend'])}
已保存最终稿: {'是' if stats['has_final_content'] else '否'}

{divider}
"""
        return summary

    def _translate_trend(self, trend: str) -> str:
        """翻译趋势"""
        translations = {
            "improving": "📈 持续改进",
            "declining": "📉 有所下降",
            "stable": "➡️ 保持稳定",
            "insufficient_data": "📊 数据不足"
        }
        return translations.get(trend, trend)


class HumanAICollaborativeWorkflow:
    """人工AI协作创作工作流"""

    def __init__(self, novel_id: str, db_manager=None):
        self.novel_id = novel_id
        self.db_manager = db_manager or get_novel_manager(novel_id)
        self.prompt_generator = NovelPromptGenerator(novel_id)
        self.content_analyzer = ContentAnalyzer(self.db_manager)
        self.session_manager = CreationSessionManager(self.db_manager)
        self.ui_interface = UserInteractionInterface()

    async def generate_prompt_for_user(
        self,
        chapter_number: int,
        scene_type: str,
        focus_characters: List[str],
        target_length: int = 2000,
        style_preferences: Dict = None
    ) -> Tuple[str, PromptComponents]:
        """为用户生成结构化prompt"""

        # 获取章节和角色信息
        # TODO: 实现从数据库获取章节和角色信息
        chapter_info = {
            "number": chapter_number,
            "summary": f"第{chapter_number}章内容摘要"
        }
        character_details = []
        for char_name in focus_characters:
            character_details.append({
                "name": char_name,
                "description": f"{char_name}的描述信息"
            })

        # 生成系统提示词
        system_prompt = await self._generate_system_prompt(
            scene_type=scene_type,
            chapter_context=chapter_info,
            characters=character_details,
            style_preferences=style_preferences
        )

        # 生成用户提示词
        user_prompt = await self._generate_user_prompt(
            chapter_number=chapter_number,
            scene_type=scene_type,
            focus_characters=focus_characters,
            target_length=target_length,
            chapter_context=chapter_info
        )

        # 设置参数建议
        temperature = style_preferences.get("temperature", 0.8) if style_preferences else 0.8

        prompt_components = PromptComponents(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            suggested_max_tokens=int(target_length * 1.5),
            suggested_temperature=temperature,
            metadata={
                "chapter_number": chapter_number,
                "scene_type": scene_type,
                "focus_characters": focus_characters
            }
        )

        # 格式化供显示
        formatted_prompt = self.ui_interface.format_prompt_for_display(prompt_components)

        return formatted_prompt, prompt_components

    async def analyze_user_content(
        self,
        session_id: str,
        generated_content: str,
        user_satisfaction: int = None,
        prompt_used: Optional[PromptComponents] = None
    ) -> Tuple[str, AnalysisResult]:
        """分析用户提供的生成内容"""

        # 获取会话信息
        session = await self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 获取相关上下文
        # TODO: 实现从数据库获取小说和章节信息
        novel_info = {
            "id": session.novel_id,
            "title": "小说标题"
        }
        chapter_info = {
            "number": session.chapter_number,
            "summary": f"第{session.chapter_number}章内容摘要"
        }

        # 提取焦点角色
        focus_characters = []
        if prompt_used and prompt_used.metadata:
            focus_characters = prompt_used.metadata.get("focus_characters", [])

        # 执行内容分析
        analysis = await self.content_analyzer.comprehensive_analysis(
            content=generated_content,
            prompt_used=prompt_used,
            world_context={
                "novel_info": novel_info,
                "chapter_info": chapter_info
            },
            focus_characters=focus_characters
        )

        # 添加到会话
        await self.session_manager.add_content_iteration(
            session_id=session_id,
            content=generated_content,
            user_rating=user_satisfaction or 5,
            analysis=analysis,
            prompt_used=prompt_used
        )

        # 格式化分析报告
        formatted_report = self.ui_interface.format_analysis_report(analysis)

        return formatted_report, analysis

    async def suggest_improvements(
        self,
        session_id: str,
        analysis_result: AnalysisResult,
        user_feedback: str = ""
    ) -> Dict[str, Any]:
        """提供改进建议"""

        suggestions = {
            "prompt_improvements": [],
            "content_improvements": [],
            "next_steps": []
        }

        # 基于分析结果生成prompt改进建议
        if analysis_result.overall_score < 0.6:
            suggestions["prompt_improvements"].append(
                "考虑在prompt中加入更具体的要求，如具体的场景细节、情感基调等"
            )

        if not analysis_result.law_chain_accuracy["mentioned_law_chains"]:
            suggestions["prompt_improvements"].append(
                "在prompt中明确提及需要展现的法则链元素"
            )

        if analysis_result.dialogue_quality.get("dialogue_count", 0) < 2:
            suggestions["prompt_improvements"].append(
                "要求AI包含至少3-4处角色对话，展现角色性格"
            )

        # 内容改进建议
        suggestions["content_improvements"].extend(analysis_result.specific_suggestions)

        # 下一步建议
        if analysis_result.overall_score > 0.8:
            suggestions["next_steps"].append("内容质量优秀，可以保存为最终版本")
        elif analysis_result.overall_score > 0.6:
            suggestions["next_steps"].append("根据具体建议微调prompt后重新生成")
        else:
            suggestions["next_steps"].append("建议重新设计prompt，加入更多具体要求")

        # 如果有用户反馈，生成针对性建议
        if user_feedback:
            suggestions["targeted_suggestions"] = await self._generate_targeted_suggestions(
                user_feedback,
                analysis_result
            )

        return suggestions

    async def optimize_prompt_iteration(
        self,
        session_id: str,
        original_prompt: PromptComponents,
        issues_found: List[str],
        desired_improvements: List[str]
    ) -> Tuple[str, PromptComponents]:
        """基于反馈优化prompt"""

        # 分析问题
        optimization_focus = self._analyze_optimization_needs(
            issues_found,
            desired_improvements
        )

        # 修改系统提示词
        optimized_system = original_prompt.system_prompt
        for focus in optimization_focus["system_additions"]:
            optimized_system += f"\n\n{focus}"

        # 修改用户提示词
        optimized_user = original_prompt.user_prompt
        for focus in optimization_focus["user_additions"]:
            optimized_user += f"\n\n{focus}"

        # 调整参数
        new_temperature = original_prompt.suggested_temperature
        if "更有创意" in str(desired_improvements):
            new_temperature = min(new_temperature + 0.1, 1.0)
        elif "更准确" in str(desired_improvements):
            new_temperature = max(new_temperature - 0.1, 0.5)

        optimized_prompt = PromptComponents(
            system_prompt=optimized_system,
            user_prompt=optimized_user,
            suggested_max_tokens=original_prompt.suggested_max_tokens,
            suggested_temperature=new_temperature,
            metadata=original_prompt.metadata
        )

        formatted = self.ui_interface.format_prompt_for_display(optimized_prompt)

        return formatted, optimized_prompt

    async def _generate_system_prompt(
        self,
        scene_type: str,
        chapter_context: Dict,
        characters: List[Dict],
        style_preferences: Dict = None
    ) -> str:
        """生成系统提示词"""

        system_prompt = f"""你是一位专业的玄幻小说创作助手，擅长创作富有东方玄幻色彩的修仙小说。

【世界观设定】
这是一个以"法则链"为核心力量体系的玄幻世界。修炼者通过感悟和掌控不同的法则链来提升实力。
主要法则链包括：时间、空间、生命、死亡、因果、轮回、创造、毁灭、平衡。

【场景类型】
当前需要创作的是：{scene_type}类型的场景

【写作风格要求】
- 语言优美流畅，富有画面感
- 注重细节描写和氛围营造
- 人物对话要符合角色性格
- 动作描写要有张力和节奏感
- 适当运用比喻、排比等修辞手法"""

        if style_preferences:
            style_notes = style_preferences.get("notes", "")
            if style_notes:
                system_prompt += f"\n\n【特殊风格要求】\n{style_notes}"

        if characters:
            system_prompt += "\n\n【重点角色信息】"
            for char in characters[:3]:  # 最多列出3个角色
                system_prompt += f"\n- {char.get('name', '未知')}: {char.get('description', '无描述')}"

        return system_prompt

    async def _generate_user_prompt(
        self,
        chapter_number: int,
        scene_type: str,
        focus_characters: List[str],
        target_length: int,
        chapter_context: Dict = None
    ) -> str:
        """生成用户提示词"""

        user_prompt = f"""请为第{chapter_number}章创作一个{scene_type}场景。

【场景要求】
- 重点角色：{', '.join(focus_characters)}
- 目标字数：约{target_length}字
- 场景类型：{scene_type}

【内容要求】
1. 场景要有明确的开始、发展和结尾
2. 突出展现角色的性格特点
3. 适当加入法则链相关的描述
4. 包含至少2-3处精彩的对话
5. 注意与前文的连贯性"""

        if chapter_context:
            if "summary" in chapter_context:
                user_prompt += f"\n\n【章节背景】\n{chapter_context['summary']}"

        user_prompt += "\n\n请开始创作："

        return user_prompt

    def _analyze_optimization_needs(
        self,
        issues_found: List[str],
        desired_improvements: List[str]
    ) -> Dict[str, List[str]]:
        """分析优化需求"""

        system_additions = []
        user_additions = []

        # 分析问题并生成优化
        all_feedback = issues_found + desired_improvements
        feedback_text = " ".join(all_feedback)

        if "对话" in feedback_text:
            user_additions.append("【特别强调】请确保包含3-5处生动的角色对话，展现人物性格")

        if "法则" in feedback_text or "力量体系" in feedback_text:
            system_additions.append("【法则链描写指导】描写法则链时要具体展现其表现形式、威能和修炼者的感悟过程")

        if "场景" in feedback_text or "描写" in feedback_text:
            user_additions.append("【场景要求】请加入丰富的感官描写（视觉、听觉、触觉等），让场景更加生动立体")

        if "节奏" in feedback_text or "紧张" in feedback_text:
            system_additions.append("【节奏控制】注意通过短句营造紧张感，长句展现宏大场面，张弛有度")

        if "情感" in feedback_text:
            user_additions.append("【情感要求】深入刻画角色的内心活动和情感变化，让读者产生共鸣")

        return {
            "system_additions": system_additions,
            "user_additions": user_additions
        }

    async def _generate_targeted_suggestions(
        self,
        user_feedback: str,
        analysis_result: AnalysisResult
    ) -> List[str]:
        """生成针对性建议"""

        suggestions = []

        # 根据用户反馈生成建议
        if "太短" in user_feedback:
            suggestions.append("增加场景细节描写和人物心理活动")
            suggestions.append("可以加入更多的环境描写和氛围渲染")

        if "不够精彩" in user_feedback:
            suggestions.append("增加冲突和转折，提升戏剧张力")
            suggestions.append("加入意外元素或反转，增强吸引力")

        if "角色" in user_feedback:
            suggestions.append("深化角色性格刻画，通过细节展现人物特点")
            suggestions.append("增加角色独特的语言风格和行为模式")

        return suggestions


# 导出主要类
__all__ = [
    'HumanAICollaborativeWorkflow',
    'CreationSessionManager',
    'ContentAnalyzer',
    'UserInteractionInterface',
    'PromptComponents',
    'AnalysisResult',
    'CreationSession',
    'SessionStatus',
    'ContentType'
]