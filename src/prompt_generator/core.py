"""
核心Prompt生成器
将Novellus知识库转换为高质量的Claude创作prompt
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from uuid import UUID
import json
import logging
from dataclasses import dataclass, asdict

from database.data_access import get_novel_manager
from database.models import *
from .context_manager import ContextWindowManager
from .template_engine import PromptTemplateEngine

logger = logging.getLogger(__name__)


@dataclass
class PromptComponents:
    """Prompt组件"""
    system_prompt: str
    user_prompt: str
    context: Dict[str, Any]
    constraints: Dict[str, Any]
    style_guide: Dict[str, str]
    metadata: Dict[str, Any]


class NovelPromptGenerator:
    """小说创作Prompt生成器"""

    def __init__(self, novel_id: str):
        """
        初始化生成器

        Args:
            novel_id: 小说ID
        """
        self.novel_id = novel_id
        self.novel_manager = None
        self.context_manager = ContextWindowManager()
        self.template_engine = PromptTemplateEngine()
        self._initialized = False

    async def initialize(self):
        """异步初始化"""
        if not self._initialized:
            self.novel_manager = get_novel_manager(self.novel_id)
            await self._load_novel_data()
            self._initialized = True

    async def _load_novel_data(self):
        """加载小说基础数据"""
        # 获取小说信息
        self.novel_info = await self.novel_manager.get_novel()

        # 获取项目信息
        global_manager = get_global_manager()
        self.project = await global_manager.get_project(self.novel_info.project_id)

        # 预加载常用数据
        self.domains = await self.novel_manager.get_domains()
        self.law_chains = await self.novel_manager.get_law_chains()

        logger.info(f"Loaded novel data for: {self.novel_info.title}")

    async def generate_creation_prompt(
        self,
        chapter_number: int,
        scene_type: str = "narrative",
        focus_characters: Optional[List[str]] = None,
        target_length: int = 2000,
        style_params: Optional[Dict[str, Any]] = None,
        previous_chapters: Optional[List[int]] = None
    ) -> PromptComponents:
        """
        生成创作prompt

        Args:
            chapter_number: 章节号
            scene_type: 场景类型 (narrative/battle/dialogue/exposition/development)
            focus_characters: 焦点角色ID列表
            target_length: 目标字数
            style_params: 风格参数
            previous_chapters: 需要参考的前序章节列表

        Returns:
            结构化的prompt组件
        """
        if not self._initialized:
            await self.initialize()

        # 1. 收集世界观设定
        worldbuilding = await self._get_worldbuilding_context()

        # 2. 获取角色信息
        characters = await self._get_character_profiles(focus_characters or [])

        # 3. 提取法则链规则
        law_chains_context = await self._get_law_chains_context(scene_type)

        # 4. 获取前情提要
        previous_context = await self._get_previous_chapters_summary(
            chapter_number,
            previous_chapters
        )

        # 5. 构建冲突框架
        conflicts = await self._get_active_conflicts(chapter_number)

        # 6. 获取剧情钩子
        story_hooks = await self._get_relevant_story_hooks(scene_type, focus_characters)

        # 7. 构建各个prompt组件
        system_prompt = self._build_system_prompt(worldbuilding, law_chains_context)

        user_prompt = self._build_user_prompt(
            chapter_number=chapter_number,
            scene_type=scene_type,
            characters=characters,
            conflicts=conflicts,
            previous_context=previous_context,
            story_hooks=story_hooks
        )

        constraints = self._build_constraints(target_length, scene_type)

        style_guide = self._build_style_guide(style_params)

        # 8. 管理上下文窗口
        self.context_manager.add_context(system_prompt, priority=10)
        self.context_manager.add_context(user_prompt, priority=9)

        # 9. 构建元数据
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "novel_id": self.novel_id,
            "chapter_number": chapter_number,
            "scene_type": scene_type,
            "target_length": target_length,
            "context_tokens": self.context_manager.get_total_tokens()
        }

        return PromptComponents(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context={
                "worldbuilding": worldbuilding,
                "characters": characters,
                "law_chains": law_chains_context,
                "previous_context": previous_context,
                "conflicts": conflicts,
                "story_hooks": story_hooks
            },
            constraints=constraints,
            style_guide=style_guide,
            metadata=metadata
        )

    async def _get_worldbuilding_context(self) -> Dict[str, Any]:
        """获取世界观设定上下文"""
        context = {
            "novel_title": self.novel_info.title,
            "novel_description": self.novel_info.description,
            "author": self.project.author,
            "genre": self.project.genre,
            "domains": [],
            "core_concepts": {}
        }

        # 添加域信息
        for domain in self.domains:
            domain_info = {
                "name": domain.name,
                "type": domain.domain_type,
                "description": domain.description,
                "power_level": domain.power_level,
                "characteristics": domain.characteristics or {}
            }
            context["domains"].append(domain_info)

        # 添加核心概念
        context["core_concepts"] = {
            "法则链系统": "世界运行的基础规则，共12条基础法则链",
            "链疲劳": "使用法则链后的消耗状态",
            "污染度": "违背法则带来的负面影响",
            "因果债": "干涉命运和因果产生的代价",
            "九域": "世界的九个主要区域，各有独特文化和制度"
        }

        return context

    async def _get_character_profiles(self, character_ids: List[str]) -> List[Dict[str, Any]]:
        """获取角色档案"""
        profiles = []

        for char_id in character_ids:
            try:
                character = await self.novel_manager.get_character(char_id)

                # 获取角色的法则链掌握情况
                character_chains = []
                # 这里需要实际的查询，暂时模拟

                profile = {
                    "id": character.id,
                    "name": character.name,
                    "type": character.character_type,
                    "basic_info": character.basic_info or {},
                    "personality": character.personality or {},
                    "abilities": character.abilities or [],
                    "relationships": character.relationships or {},
                    "current_state": character.current_state or {},
                    "law_chains": character_chains,
                    "tags": character.tags
                }
                profiles.append(profile)

            except Exception as e:
                logger.warning(f"Failed to load character {char_id}: {e}")

        return profiles

    async def _get_law_chains_context(self, scene_type: str) -> Dict[str, Any]:
        """获取法则链上下文"""
        context = {
            "available_chains": [],
            "scene_relevant_chains": [],
            "combination_rules": [],
            "restrictions": []
        }

        # 获取所有法则链
        for chain in self.law_chains:
            chain_info = {
                "name": chain.name,
                "type": chain.chain_type,
                "description": chain.description,
                "power_level": chain.power_level,
                "rarity": chain.rarity,
                "effects": chain.effects or [],
                "cost": chain.cost or {}
            }
            context["available_chains"].append(chain_info)

            # 根据场景类型筛选相关法则链
            if scene_type == "battle" and chain.chain_type in ["offensive", "defensive"]:
                context["scene_relevant_chains"].append(chain.name)
            elif scene_type == "exploration" and chain.chain_type in ["spatial", "perception"]:
                context["scene_relevant_chains"].append(chain.name)

        # 添加组合规则
        context["combination_rules"] = [
            "命运链与因果链组合产生'宿命锁定'效果",
            "时空链与界域链组合产生'空间折叠'效果",
            "生死链与记忆链组合产生'灵魂烙印'效果"
        ]

        # 添加限制
        context["restrictions"] = [
            "每次使用法则链消耗链疲劳值",
            "违背法则会增加污染度",
            "过度使用可能导致法则反噬"
        ]

        return context

    async def _get_previous_chapters_summary(
        self,
        current_chapter: int,
        previous_chapters: Optional[List[int]] = None
    ) -> str:
        """获取前情提要"""
        if previous_chapters is None:
            # 默认获取前3章
            previous_chapters = list(range(max(1, current_chapter - 3), current_chapter))

        summaries = []

        for chapter_num in previous_chapters:
            try:
                # 查询章节内容
                segments = await self.novel_manager.get_chapter_segments(chapter_num)

                if segments:
                    # 提取关键信息
                    chapter_summary = f"第{chapter_num}章要点：\n"

                    # 获取主要事件
                    main_events = [s for s in segments if s.segment_type == "plot"]
                    if main_events:
                        chapter_summary += f"- 主要事件：{main_events[0].content[:100]}...\n"

                    # 获取角色发展
                    char_development = [s for s in segments if "character" in s.tags]
                    if char_development:
                        chapter_summary += f"- 角色发展：有重要角色成长\n"

                    summaries.append(chapter_summary)

            except Exception as e:
                logger.warning(f"Failed to get chapter {chapter_num} summary: {e}")

        return "\n".join(summaries) if summaries else "这是故事的开始。"

    async def _get_active_conflicts(self, chapter_number: int) -> List[Dict[str, Any]]:
        """获取活跃的冲突"""
        conflicts = []

        try:
            # 查询冲突矩阵
            query = """
                SELECT * FROM cross_domain_conflict_matrix
                WHERE novel_id = $1
                AND status = 'active'
                ORDER BY priority DESC, intensity DESC
                LIMIT 5
            """

            results = await self.novel_manager.fetch_query(query, self.novel_id)

            for row in results:
                conflict = {
                    "type": row["conflict_type"],
                    "domains": [row["domain_a"], row["domain_b"]],
                    "intensity": float(row["intensity"]),
                    "description": row.get("description", ""),
                    "key_roles": row.get("key_roles", []),
                    "trigger_conditions": row.get("trigger_laws", [])
                }
                conflicts.append(conflict)

        except Exception as e:
            logger.warning(f"Failed to get active conflicts: {e}")

        return conflicts

    async def _get_relevant_story_hooks(
        self,
        scene_type: str,
        focus_characters: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取相关的剧情钩子"""
        hooks = []

        try:
            # 查询剧情钩子
            query = """
                SELECT * FROM conflict_story_hooks
                WHERE novel_id = $1
                AND hook_type = $2
                AND overall_score >= 7.0
                ORDER BY priority_level DESC, overall_score DESC
                LIMIT 3
            """

            # 映射场景类型到钩子类型
            hook_type_map = {
                "battle": "combat",
                "dialogue": "character",
                "exposition": "worldbuilding",
                "development": "growth"
            }

            hook_type = hook_type_map.get(scene_type, "general")

            results = await self.novel_manager.fetch_query(query, self.novel_id, hook_type)

            for row in results:
                hook = {
                    "title": row["title"],
                    "description": row["description"],
                    "type": row["hook_type"],
                    "emotional_impact": float(row.get("emotional_impact", 0)),
                    "complexity": float(row.get("complexity", 0)),
                    "themes": row.get("moral_themes", [])
                }
                hooks.append(hook)

        except Exception as e:
            logger.warning(f"Failed to get story hooks: {e}")

        return hooks

    def _build_system_prompt(
        self,
        worldbuilding: Dict[str, Any],
        law_chains: Dict[str, Any]
    ) -> str:
        """构建系统提示词"""

        # 使用模板引擎
        template = self.template_engine.get_template("system_prompt")

        return template.format(
            novel_title=worldbuilding["novel_title"],
            novel_description=worldbuilding["novel_description"],
            author=worldbuilding["author"],
            genre=worldbuilding["genre"],
            domains=self._format_domains(worldbuilding["domains"]),
            core_concepts=self._format_core_concepts(worldbuilding["core_concepts"]),
            law_chains=self._format_law_chains(law_chains),
            creation_rules=self._get_creation_rules()
        )

    def _build_user_prompt(
        self,
        chapter_number: int,
        scene_type: str,
        characters: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        previous_context: str,
        story_hooks: List[Dict[str, Any]]
    ) -> str:
        """构建用户提示词"""

        # 获取场景模板
        template = self.template_engine.get_template(f"scene_{scene_type}")

        return template.format(
            chapter_number=chapter_number,
            scene_type=self._translate_scene_type(scene_type),
            previous_context=previous_context,
            characters=self._format_characters(characters),
            conflicts=self._format_conflicts(conflicts),
            story_hooks=self._format_story_hooks(story_hooks),
            scene_requirements=self._get_scene_requirements(scene_type)
        )

    def _build_constraints(self, target_length: int, scene_type: str) -> Dict[str, Any]:
        """构建约束条件"""

        constraints = {
            "word_count": {
                "target": target_length,
                "min": int(target_length * 0.8),
                "max": int(target_length * 1.2)
            },
            "content_requirements": self._get_content_requirements(scene_type),
            "forbidden_elements": self._get_forbidden_elements(),
            "consistency_checks": [
                "角色行为符合其性格设定",
                "法则链使用遵循世界观规则",
                "情节发展符合因果逻辑",
                "文化细节与域设定一致"
            ]
        }

        return constraints

    def _build_style_guide(self, style_params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """构建风格指南"""

        default_style = {
            "narrative_voice": "第三人称全知视角",
            "tone": "史诗奇幻，带有东方玄幻色彩",
            "pacing": "张弛有度，战斗紧凑，日常舒缓",
            "description_style": "细腻而富有画面感",
            "dialogue_style": "符合角色身份，古风与现代结合",
            "emotion_expression": "内心独白与外在表现并重"
        }

        if style_params:
            default_style.update(style_params)

        return default_style

    # =========================================================================
    # 格式化辅助方法
    # =========================================================================

    def _format_domains(self, domains: List[Dict[str, Any]]) -> str:
        """格式化域信息"""
        formatted = []
        for domain in domains:
            formatted.append(
                f"【{domain['name']}】\n"
                f"  类型：{domain['type']}\n"
                f"  描述：{domain['description']}\n"
                f"  力量等级：{domain['power_level']}/10"
            )
        return "\n\n".join(formatted)

    def _format_core_concepts(self, concepts: Dict[str, str]) -> str:
        """格式化核心概念"""
        formatted = []
        for concept, description in concepts.items():
            formatted.append(f"- {concept}：{description}")
        return "\n".join(formatted)

    def _format_law_chains(self, law_chains: Dict[str, Any]) -> str:
        """格式化法则链信息"""
        formatted = [
            "可用法则链：",
            "\n".join([f"  - {chain['name']}：{chain['description']}"
                      for chain in law_chains["available_chains"][:5]]),
            "\n场景相关法则链：",
            "  " + "、".join(law_chains["scene_relevant_chains"]),
            "\n组合规则：",
            "\n".join([f"  - {rule}" for rule in law_chains["combination_rules"][:3]])
        ]
        return "\n".join(formatted)

    def _format_characters(self, characters: List[Dict[str, Any]]) -> str:
        """格式化角色信息"""
        if not characters:
            return "本章无特定焦点角色"

        formatted = []
        for char in characters:
            char_info = [
                f"【{char['name']}】",
                f"  类型：{char['type']}",
                f"  性格：{char.get('personality', {}).get('traits', '未设定')}",
                f"  当前状态：{char.get('current_state', {}).get('condition', '正常')}",
                f"  能力：{', '.join(char.get('abilities', [])[:3]) if char.get('abilities') else '普通'}"
            ]
            formatted.append("\n".join(char_info))

        return "\n\n".join(formatted)

    def _format_conflicts(self, conflicts: List[Dict[str, Any]]) -> str:
        """格式化冲突信息"""
        if not conflicts:
            return "当前无主要冲突"

        formatted = []
        for conflict in conflicts[:3]:
            conf_info = [
                f"- {conflict['type']}冲突",
                f"  涉及：{' vs '.join(conflict['domains'])}",
                f"  强度：{conflict['intensity']}/5",
                f"  关键角色：{', '.join(conflict['key_roles'][:3]) if conflict['key_roles'] else '待定'}"
            ]
            formatted.append("\n".join(conf_info))

        return "\n\n".join(formatted)

    def _format_story_hooks(self, hooks: List[Dict[str, Any]]) -> str:
        """格式化剧情钩子"""
        if not hooks:
            return "可自由发挥剧情"

        formatted = []
        for hook in hooks:
            formatted.append(
                f"- 【{hook['title']}】{hook['description'][:100]}..."
            )

        return "\n".join(formatted)

    def _translate_scene_type(self, scene_type: str) -> str:
        """翻译场景类型"""
        translations = {
            "narrative": "叙事场景",
            "battle": "战斗场景",
            "dialogue": "对话场景",
            "exposition": "说明场景",
            "development": "发展场景"
        }
        return translations.get(scene_type, "一般场景")

    def _get_creation_rules(self) -> str:
        """获取创作规则"""
        return """
创作要求：
1. 严格遵守世界观设定，不得违背已建立的规则
2. 角色行为必须符合其性格和当前状态
3. 法则链的使用需要体现代价和限制
4. 冲突发展遵循因果逻辑，不能突兀
5. 保持叙事风格的一致性
6. 适当运用伏笔和悬念
7. 注意节奏控制，张弛有度
"""

    def _get_scene_requirements(self, scene_type: str) -> str:
        """获取场景要求"""
        requirements = {
            "battle": "重点描写战斗动作、法则链运用、战术策略",
            "dialogue": "注重对话的真实性、角色性格体现、信息传递",
            "exposition": "清晰介绍世界观设定、背景信息、文化细节",
            "development": "展现角色成长、关系变化、能力提升",
            "narrative": "平衡叙事节奏、推进主线剧情"
        }
        return requirements.get(scene_type, "自然推进故事")

    def _get_content_requirements(self, scene_type: str) -> List[str]:
        """获取内容要求"""
        base_requirements = [
            "包含环境描写",
            "有角色心理活动",
            "推进情节发展"
        ]

        scene_specific = {
            "battle": ["详细的战斗描写", "法则链效果展示", "战斗结果影响"],
            "dialogue": ["至少3轮对话", "体现角色关系", "信息交换"],
            "exposition": ["世界观介绍", "文化展示", "背景说明"],
            "development": ["能力或认知提升", "关系变化", "成长契机"]
        }

        return base_requirements + scene_specific.get(scene_type, [])

    def _get_forbidden_elements(self) -> List[str]:
        """获取禁止元素"""
        return [
            "现代科技产品（手机、电脑等）",
            "与世界观不符的西方魔法元素",
            "过于血腥暴力的描写",
            "不符合角色设定的OOC行为"
        ]

    async def export_prompt(self, components: PromptComponents) -> str:
        """
        导出完整的prompt

        Args:
            components: prompt组件

        Returns:
            格式化的完整prompt
        """
        full_prompt = f"""
# System Prompt
{components.system_prompt}

# User Prompt
{components.user_prompt}

# Constraints
{json.dumps(components.constraints, ensure_ascii=False, indent=2)}

# Style Guide
{json.dumps(components.style_guide, ensure_ascii=False, indent=2)}

# Metadata
{json.dumps(components.metadata, ensure_ascii=False, indent=2)}
"""

        return full_prompt

    async def save_prompt(
        self,
        components: PromptComponents,
        name: str,
        description: str = ""
    ) -> str:
        """
        保存prompt到数据库

        Args:
            components: prompt组件
            name: prompt名称
            description: 描述

        Returns:
            保存的prompt ID
        """
        # 这里需要实现保存到数据库的逻辑
        # 暂时返回模拟ID
        return f"prompt_{datetime.now().strftime('%Y%m%d%H%M%S')}"