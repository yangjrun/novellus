"""
MCP Prompt生成工具
提供小说创作prompt生成的MCP接口
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from prompt_generator import (
    NovelPromptGenerator,
    ContextWindowManager,
    PromptTemplateEngine,
    QualityValidator,
    CreationWorkflow
)

logger = logging.getLogger(__name__)


def register_prompt_tools(mcp):
    """注册prompt生成工具到MCP服务器"""

    # 存储活跃的生成器实例
    generators = {}
    workflows = {}

    @mcp.tool()
    async def generate_creation_prompt(
        novel_id: str,
        chapter_number: int,
        scene_type: str = "narrative",
        focus_characters: str = "",
        target_length: int = 2000,
        style: str = "default",
        include_previous_chapters: bool = True
    ) -> str:
        """
        生成小说创作prompt

        Args:
            novel_id: 小说ID
            chapter_number: 章节号
            scene_type: 场景类型 (narrative/battle/dialogue/exposition/development)
            focus_characters: 焦点角色ID列表（逗号分隔）
            target_length: 目标字数
            style: 创作风格 (default/dramatic/poetic/concise)
            include_previous_chapters: 是否包含前序章节总结

        Returns:
            生成的prompt JSON
        """
        try:
            # 获取或创建生成器
            if novel_id not in generators:
                generators[novel_id] = NovelPromptGenerator(novel_id)
                await generators[novel_id].initialize()

            generator = generators[novel_id]

            # 处理角色列表
            character_list = [c.strip() for c in focus_characters.split(",") if c.strip()]

            # 处理前序章节
            previous_chapters = None
            if include_previous_chapters and chapter_number > 1:
                previous_chapters = list(range(max(1, chapter_number - 3), chapter_number))

            # 生成风格参数
            style_params = None
            if style != "default":
                style_map = {
                    "dramatic": {
                        "tone": "戏剧性强烈，冲突激烈",
                        "pacing": "快节奏，紧张刺激",
                        "description_style": "动感强烈，画面冲击力强"
                    },
                    "poetic": {
                        "tone": "诗意盎然，意境深远",
                        "pacing": "舒缓优雅",
                        "description_style": "细腻唯美，富有诗意"
                    },
                    "concise": {
                        "tone": "简洁明快",
                        "pacing": "节奏明快",
                        "description_style": "简洁有力，直击要点"
                    }
                }
                style_params = style_map.get(style)

            # 生成prompt
            components = await generator.generate_creation_prompt(
                chapter_number=chapter_number,
                scene_type=scene_type,
                focus_characters=character_list,
                target_length=target_length,
                style_params=style_params,
                previous_chapters=previous_chapters
            )

            # 导出为JSON格式
            result = {
                "success": True,
                "prompt": {
                    "system": components.system_prompt,
                    "user": components.user_prompt,
                    "constraints": components.constraints,
                    "style_guide": components.style_guide
                },
                "context": {
                    "worldbuilding_included": bool(components.context.get("worldbuilding")),
                    "characters_count": len(components.context.get("characters", [])),
                    "conflicts_count": len(components.context.get("conflicts", [])),
                    "story_hooks_count": len(components.context.get("story_hooks", []))
                },
                "metadata": components.metadata,
                "usage": {
                    "estimated_tokens": components.metadata.get("context_tokens", 0)
                }
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Prompt generation failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def validate_generated_content(
        novel_id: str,
        content: str,
        chapter_number: int,
        scene_type: str = "narrative"
    ) -> str:
        """
        验证AI生成内容的质量和一致性

        Args:
            novel_id: 小说ID
            content: 生成的内容
            chapter_number: 章节号
            scene_type: 场景类型

        Returns:
            验证报告JSON
        """
        try:
            # 获取生成器以获取上下文
            if novel_id not in generators:
                generators[novel_id] = NovelPromptGenerator(novel_id)
                await generators[novel_id].initialize()

            generator = generators[novel_id]

            # 创建验证器
            validator = QualityValidator()

            # 获取期望的上下文
            components = await generator.generate_creation_prompt(
                chapter_number=chapter_number,
                scene_type=scene_type,
                target_length=len(content)
            )

            # 执行验证
            validation_result = await validator.validate_content(
                content=content,
                expected_context=components.context,
                validation_level="thorough"
            )

            # 生成修正建议
            correction_prompt = None
            if not validation_result.is_valid:
                correction_prompt = await validator.generate_correction_prompt(
                    content,
                    validation_result
                )

            result = {
                "success": True,
                "validation": {
                    "is_valid": validation_result.is_valid,
                    "score": validation_result.score,
                    "grade": self._get_grade(validation_result.score)
                },
                "issues": validation_result.issues,
                "warnings": validation_result.warnings,
                "suggestions": validation_result.suggestions,
                "scores": validation_result.details.get("scores", {}),
                "correction_prompt": correction_prompt
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def create_scene_with_ai(
        novel_id: str,
        chapter_number: int,
        scene_type: str = "narrative",
        target_length: int = 2000,
        auto_validate: bool = True,
        save_to_db: bool = False,
        batch_id: str = "",
        use_real_api: bool = None
    ) -> str:
        """
        使用AI完整创作一个场景（需要配置Claude API）

        Args:
            novel_id: 小说ID
            chapter_number: 章节号
            scene_type: 场景类型
            target_length: 目标字数
            auto_validate: 是否自动验证和修正
            save_to_db: 是否保存到数据库
            batch_id: 批次ID（保存时需要）
            use_real_api: 是否使用真实API（None时根据配置自动判断）

        Returns:
            创作结果JSON
        """
        try:
            # 获取或创建工作流
            workflow_key = f"{novel_id}_{'real' if use_real_api else 'mock'}"
            if workflow_key not in workflows:
                workflows[workflow_key] = CreationWorkflow(novel_id, use_real_api=use_real_api)
                await workflows[workflow_key].initialize()

            workflow = workflows[workflow_key]

            # 创作场景
            result = await workflow.create_scene(
                chapter_number=chapter_number,
                scene_type=scene_type,
                target_length=target_length
            )

            # 保存到数据库
            saved_id = None
            if save_to_db and result.success and batch_id:
                try:
                    saved_id = await workflow.save_to_database(result, batch_id)
                except Exception as e:
                    logger.warning(f"Failed to save to database: {e}")

            response_data = {
                "success": result.success,
                "content": result.content,
                "validation_score": result.validation_score,
                "iterations": result.iterations,
                "tokens_used": result.total_tokens_used,
                "time_elapsed": result.time_elapsed,
                "saved_id": saved_id,
                "metadata": result.metadata
            }

            # 添加API使用信息
            if workflow.use_real_api:
                response_data["api_info"] = {
                    "used_real_api": True,
                    "model": result.metadata.get("model", "unknown"),
                    "cost": result.metadata.get("cost", 0.0),
                    "cost_formatted": f"${result.metadata.get('cost', 0.0):.4f}"
                }
            else:
                response_data["api_info"] = {
                    "used_real_api": False,
                    "model": "mock",
                    "cost": 0.0
                }

            return json.dumps(response_data, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Scene creation failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def get_context_usage(novel_id: str) -> str:
        """
        获取当前上下文窗口使用情况

        Args:
            novel_id: 小说ID

        Returns:
            上下文使用统计JSON
        """
        try:
            if novel_id not in generators:
                return json.dumps({
                    "success": False,
                    "message": "No active generator for this novel"
                }, ensure_ascii=False, indent=2)

            generator = generators[novel_id]
            context_manager = generator.context_manager

            summary = context_manager.get_context_summary()

            return json.dumps({
                "success": True,
                "usage": {
                    "total_tokens": summary["total_tokens"],
                    "max_tokens": summary["max_tokens"],
                    "usage_percentage": f"{summary['usage_percentage']:.1f}%",
                    "remaining_tokens": context_manager.estimate_remaining_space()
                },
                "items": summary["items_count"],
                "categories": summary["categories"],
                "priority_distribution": summary["priority_distribution"]
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Failed to get context usage: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def manage_prompt_templates(
        action: str,
        template_name: str = "",
        template_content: str = "",
        filepath: str = ""
    ) -> str:
        """
        管理prompt模板

        Args:
            action: 操作类型 (list/add/get/preview/export/import)
            template_name: 模板名称
            template_content: 模板内容
            filepath: 文件路径（导入/导出用）

        Returns:
            操作结果JSON
        """
        try:
            engine = PromptTemplateEngine()

            if action == "list":
                templates = engine.list_templates()
                return json.dumps({
                    "success": True,
                    "templates": templates
                }, ensure_ascii=False, indent=2)

            elif action == "add":
                if not template_name or not template_content:
                    return json.dumps({
                        "success": False,
                        "message": "Template name and content are required"
                    }, ensure_ascii=False, indent=2)

                engine.add_custom_template(template_name, template_content)
                return json.dumps({
                    "success": True,
                    "message": f"Template '{template_name}' added successfully"
                }, ensure_ascii=False, indent=2)

            elif action == "get":
                if not template_name:
                    return json.dumps({
                        "success": False,
                        "message": "Template name is required"
                    }, ensure_ascii=False, indent=2)

                template = engine.get_template(template_name)
                variables = engine.get_template_variables(template_name)

                return json.dumps({
                    "success": True,
                    "template": template,
                    "variables": variables
                }, ensure_ascii=False, indent=2)

            elif action == "preview":
                if not template_name:
                    return json.dumps({
                        "success": False,
                        "message": "Template name is required"
                    }, ensure_ascii=False, indent=2)

                preview = engine.preview_template(template_name)
                return json.dumps({
                    "success": True,
                    "preview": preview
                }, ensure_ascii=False, indent=2)

            elif action == "export":
                if not filepath:
                    filepath = f"templates_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

                engine.export_templates(filepath)
                return json.dumps({
                    "success": True,
                    "message": f"Templates exported to {filepath}"
                }, ensure_ascii=False, indent=2)

            elif action == "import":
                if not filepath:
                    return json.dumps({
                        "success": False,
                        "message": "Filepath is required for import"
                    }, ensure_ascii=False, indent=2)

                engine.import_templates(filepath)
                return json.dumps({
                    "success": True,
                    "message": f"Templates imported from {filepath}"
                }, ensure_ascii=False, indent=2)

            else:
                return json.dumps({
                    "success": False,
                    "message": f"Unknown action: {action}"
                }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Template management failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def get_workflow_statistics(novel_id: str) -> str:
        """
        获取创作工作流统计信息

        Args:
            novel_id: 小说ID

        Returns:
            工作流统计JSON
        """
        try:
            if novel_id not in workflows:
                return json.dumps({
                    "success": False,
                    "message": "No active workflow for this novel"
                }, ensure_ascii=False, indent=2)

            workflow = workflows[novel_id]
            stats = workflow.get_workflow_statistics()

            return json.dumps({
                "success": True,
                "statistics": stats
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    def _get_grade(score: float) -> str:
        """将分数转换为等级"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"

    logger.info("Prompt generation tools registered successfully")