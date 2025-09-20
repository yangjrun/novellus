"""
MCP人工协作创作工具
提供用户手动与AI交互的创作模式工具
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from uuid import UUID

from .collaborative_workflow import (
    HumanAICollaborativeWorkflow,
    CreationSessionManager,
    ContentAnalyzer,
    UserInteractionInterface,
    SessionStatus,
    ContentType,
    PromptComponents
)
from .database.data_access import get_novel_manager

logger = logging.getLogger(__name__)


def register_collaborative_tools(mcp):
    """注册人工协作工具到MCP服务器"""

    # 存储活跃的工作流实例
    workflows = {}
    session_managers = {}

    @mcp.tool()
    async def start_writing_session(
        novel_id: str,
        chapter_number: int,
        session_name: str = ""
    ) -> str:
        """
        开始新的创作会话

        Args:
            novel_id: 小说ID
            chapter_number: 章节编号
            session_name: 会话名称（可选）

        Returns:
            包含会话ID和初始信息的JSON
        """
        try:
            # 获取或创建会话管理器
            if novel_id not in session_managers:
                novel_manager = get_novel_manager(novel_id)
                session_managers[novel_id] = CreationSessionManager(novel_manager)

            session_manager = session_managers[novel_id]

            # 创建新会话
            session_id = await session_manager.create_session(
                novel_id=novel_id,
                chapter_number=chapter_number,
                session_name=session_name
            )

            return json.dumps({
                "success": True,
                "message": "创作会话已启动",
                "session": {
                    "session_id": session_id,
                    "novel_id": novel_id,
                    "chapter_number": chapter_number,
                    "session_name": session_name or f"第{chapter_number}章创作会话",
                    "created_at": datetime.now().isoformat(),
                    "status": "active"
                },
                "instructions": [
                    "1. 使用 generate_writing_prompt 生成创作提示词",
                    "2. 将提示词复制到Claude客户端获得创作内容",
                    "3. 使用 analyze_generated_content 分析生成的内容",
                    "4. 根据分析结果使用 optimize_prompt_based_on_feedback 优化提示词",
                    "5. 满意后使用 save_final_content 保存最终内容"
                ]
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "创建创作会话失败"
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def generate_writing_prompt(
        novel_id: str,
        chapter_number: int,
        scene_type: str = "narrative",
        focus_characters: str = "",
        target_length: int = 2000,
        style: str = "default",
        special_requirements: str = ""
    ) -> str:
        """
        生成小说创作prompt供用户使用

        Args:
            novel_id: 小说ID
            chapter_number: 章节编号
            scene_type: 场景类型 (narrative/dialogue/action/description/transition/breakthrough)
            focus_characters: 焦点角色（逗号分隔）
            target_length: 目标字数
            style: 创作风格 (default/dramatic/poetic/concise)
            special_requirements: 特殊要求

        Returns:
            格式化的prompt，用户可直接复制到Claude客户端
        """
        try:
            # 获取或创建工作流
            if novel_id not in workflows:
                novel_manager = get_novel_manager(novel_id)
                workflows[novel_id] = HumanAICollaborativeWorkflow(novel_id, novel_manager)

            workflow = workflows[novel_id]

            # 处理角色列表
            character_list = [c.strip() for c in focus_characters.split(",") if c.strip()]

            # 处理风格参数
            style_preferences = {}
            if style != "default":
                style_map = {
                    "dramatic": {
                        "temperature": 0.85,
                        "notes": "戏剧性强烈，冲突激烈，节奏紧张，情绪起伏大"
                    },
                    "poetic": {
                        "temperature": 0.9,
                        "notes": "诗意盎然，意境深远，语言优美，富有韵律感"
                    },
                    "concise": {
                        "temperature": 0.7,
                        "notes": "简洁明快，直击要点，避免冗长描述"
                    }
                }
                style_preferences = style_map.get(style, {})

            if special_requirements:
                style_preferences["special_requirements"] = special_requirements

            # 生成prompt
            formatted_prompt, prompt_components = await workflow.generate_prompt_for_user(
                chapter_number=chapter_number,
                scene_type=scene_type,
                focus_characters=character_list,
                target_length=target_length,
                style_preferences=style_preferences
            )

            # 返回结果
            return json.dumps({
                "success": True,
                "message": "创作提示词生成成功",
                "prompt": {
                    "formatted_text": formatted_prompt,
                    "copyable_prompt": f"{prompt_components.system_prompt}\n\n{prompt_components.user_prompt}",
                    "components": {
                        "system": prompt_components.system_prompt,
                        "user": prompt_components.user_prompt
                    }
                },
                "parameters": {
                    "suggested_max_tokens": prompt_components.suggested_max_tokens,
                    "suggested_temperature": prompt_components.suggested_temperature,
                    "model_recommendation": prompt_components.model_recommendation
                },
                "metadata": {
                    "chapter_number": chapter_number,
                    "scene_type": scene_type,
                    "focus_characters": character_list,
                    "target_length": target_length,
                    "style": style
                },
                "usage_tips": [
                    "1. 复制 copyable_prompt 到Claude客户端",
                    "2. 设置温度参数为建议值",
                    "3. 设置最大token数为建议值",
                    "4. 生成内容后复制回来进行分析"
                ]
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"生成创作提示词失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "生成创作提示词失败"
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def analyze_generated_content(
        novel_id: str,
        session_id: str,
        generated_content: str,
        user_rating: int = 5,
        content_type: str = "scene"
    ) -> str:
        """
        分析用户提供的AI生成内容

        Args:
            novel_id: 小说ID
            session_id: 会话ID
            generated_content: AI生成的内容
            user_rating: 用户满意度评分 (1-10)
            content_type: 内容类型

        Returns:
            详细的分析报告和改进建议
        """
        try:
            # 获取工作流
            if novel_id not in workflows:
                novel_manager = get_novel_manager(novel_id)
                workflows[novel_id] = HumanAICollaborativeWorkflow(novel_id, novel_manager)

            workflow = workflows[novel_id]

            # 执行分析
            formatted_report, analysis = await workflow.analyze_user_content(
                session_id=session_id,
                generated_content=generated_content,
                user_satisfaction=user_rating
            )

            # 生成改进建议
            suggestions = await workflow.suggest_improvements(
                session_id=session_id,
                analysis_result=analysis
            )

            return json.dumps({
                "success": True,
                "message": "内容分析完成",
                "analysis": {
                    "overall_score": analysis.overall_score,
                    "recommendation": analysis.recommendation,
                    "formatted_report": formatted_report
                },
                "quality_metrics": {
                    "narrative_flow": analysis.narrative_flow.get("flow_score", 0),
                    "dialogue_quality": analysis.dialogue_quality.get("quality_score", 0),
                    "scene_vividness": analysis.scene_vividness.get("sensory_richness_score", 0),
                    "emotional_impact": analysis.emotional_impact.get("impact_score", 0),
                    "law_chain_accuracy": analysis.law_chain_accuracy.get("usage_score", 0)
                },
                "content_stats": {
                    "character_count": analysis.length_analysis["character_count"],
                    "word_count": analysis.length_analysis["word_count"],
                    "paragraph_count": analysis.length_analysis["paragraph_count"],
                    "dialogue_count": analysis.dialogue_quality.get("dialogue_count", 0)
                },
                "strengths": analysis.strengths,
                "weaknesses": analysis.weaknesses,
                "suggestions": {
                    "content_improvements": suggestions["content_improvements"],
                    "prompt_improvements": suggestions["prompt_improvements"],
                    "next_steps": suggestions["next_steps"]
                },
                "user_rating": user_rating
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "内容分析失败"
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def optimize_prompt_based_on_feedback(
        session_id: str,
        issues_found: str,
        desired_improvements: str
    ) -> str:
        """
        基于用户反馈优化prompt

        Args:
            session_id: 会话ID
            issues_found: 发现的问题（逗号分隔）
            desired_improvements: 期望的改进（逗号分隔）

        Returns:
            改进后的prompt
        """
        try:
            # 查找会话对应的工作流
            workflow = None
            novel_id = None

            for nid, mgr in session_managers.items():
                session = await mgr.get_session(session_id)
                if session:
                    novel_id = nid
                    break

            if not novel_id:
                return json.dumps({
                    "success": False,
                    "message": "未找到对应的创作会话"
                }, ensure_ascii=False, indent=2)

            if novel_id not in workflows:
                novel_manager = get_novel_manager(novel_id)
                workflows[novel_id] = HumanAICollaborativeWorkflow(novel_id, novel_manager)

            workflow = workflows[novel_id]

            # 获取会话信息
            session_manager = session_managers[novel_id]
            session = await session_manager.get_session(session_id)

            if not session or not session.original_prompt:
                return json.dumps({
                    "success": False,
                    "message": "会话中没有原始prompt信息"
                }, ensure_ascii=False, indent=2)

            # 处理反馈
            issues_list = [issue.strip() for issue in issues_found.split(",") if issue.strip()]
            improvements_list = [imp.strip() for imp in desired_improvements.split(",") if imp.strip()]

            # 优化prompt
            formatted_prompt, optimized_components = await workflow.optimize_prompt_iteration(
                session_id=session_id,
                original_prompt=session.original_prompt,
                issues_found=issues_list,
                desired_improvements=improvements_list
            )

            return json.dumps({
                "success": True,
                "message": "Prompt优化成功",
                "optimized_prompt": {
                    "formatted_text": formatted_prompt,
                    "copyable_prompt": f"{optimized_components.system_prompt}\n\n{optimized_components.user_prompt}",
                    "components": {
                        "system": optimized_components.system_prompt,
                        "user": optimized_components.user_prompt
                    }
                },
                "parameters": {
                    "suggested_max_tokens": optimized_components.suggested_max_tokens,
                    "suggested_temperature": optimized_components.suggested_temperature,
                    "model_recommendation": optimized_components.model_recommendation
                },
                "optimization_notes": [
                    f"根据 {len(issues_list)} 个问题进行了优化",
                    f"应用了 {len(improvements_list)} 个改进建议",
                    "温度参数已根据需求调整"
                ]
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"优化prompt失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "优化prompt失败"
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def get_session_history(session_id: str) -> str:
        """
        获取创作会话历史

        Args:
            session_id: 会话ID

        Returns:
            会话历史记录
        """
        try:
            # 查找会话
            session = None
            session_manager = None

            for novel_id, mgr in session_managers.items():
                s = await mgr.get_session(session_id)
                if s:
                    session = s
                    session_manager = mgr
                    break

            if not session:
                return json.dumps({
                    "success": False,
                    "message": "未找到指定会话"
                }, ensure_ascii=False, indent=2)

            # 获取会话统计
            stats = await session_manager.get_session_statistics(session_id)

            # 构建历史记录
            history = {
                "session_info": {
                    "session_id": session.session_id,
                    "novel_id": session.novel_id,
                    "chapter_number": session.chapter_number,
                    "session_name": session.session_name,
                    "status": session.status.value,
                    "created_at": session.created_at.isoformat()
                },
                "statistics": stats,
                "iterations": []
            }

            # 添加每次迭代的信息
            for i, (content, rating, analysis) in enumerate(
                zip(session.generated_contents, session.user_ratings, session.analysis_results)
            ):
                iteration = {
                    "index": i + 1,
                    "user_rating": rating,
                    "overall_score": analysis.overall_score,
                    "content_preview": content[:200] + "..." if len(content) > 200 else content,
                    "strengths": analysis.strengths[:2],  # 只显示前两个优点
                    "weaknesses": analysis.weaknesses[:2]  # 只显示前两个缺点
                }
                history["iterations"].append(iteration)

            # 添加最终内容信息
            if session.final_content:
                history["final_content"] = {
                    "saved": True,
                    "preview": session.final_content[:300] + "..." if len(session.final_content) > 300 else session.final_content,
                    "notes": session.session_notes
                }
            else:
                history["final_content"] = {
                    "saved": False
                }

            return json.dumps({
                "success": True,
                "message": "获取会话历史成功",
                "history": history
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"获取会话历史失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "获取会话历史失败"
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def save_final_content(
        session_id: str,
        final_content: str,
        content_metadata: str = "{}"
    ) -> str:
        """
        保存最终确定的内容

        Args:
            session_id: 会话ID
            final_content: 最终内容
            content_metadata: 内容元数据（JSON字符串）

        Returns:
            保存结果
        """
        try:
            # 查找会话
            session_manager = None
            novel_id = None

            for nid, mgr in session_managers.items():
                session = await mgr.get_session(session_id)
                if session:
                    session_manager = mgr
                    novel_id = nid
                    break

            if not session_manager:
                return json.dumps({
                    "success": False,
                    "message": "未找到指定会话"
                }, ensure_ascii=False, indent=2)

            # 解析元数据
            try:
                metadata = json.loads(content_metadata)
            except:
                metadata = {}

            # 生成会话笔记
            notes = f"用户满意度: {metadata.get('user_satisfaction', 'N/A')}/10\n"
            notes += f"迭代次数: {metadata.get('version', 'N/A')}\n"
            if "comments" in metadata:
                notes += f"备注: {metadata['comments']}"

            # 更新会话状态
            await session_manager.update_session_status(
                session_id=session_id,
                status=SessionStatus.COMPLETED,
                final_content=final_content,
                notes=notes
            )

            # 保存到数据库（如果需要）
            saved_to_db = False
            segment_id = None

            if metadata.get("save_to_database", False):
                try:
                    novel_manager = get_novel_manager(novel_id)
                    session = await session_manager.get_session(session_id)

                    # 创建内容段落
                    from .database.models.content_models import ContentSegmentCreate, SegmentType

                    segment_data = ContentSegmentCreate(
                        batch_id=UUID(metadata.get("batch_id")) if metadata.get("batch_id") else None,
                        segment_type=SegmentType(metadata.get("segment_type", "narrative")),
                        title=f"第{session.chapter_number}章 - {metadata.get('title', '未命名段落')}",
                        content=final_content,
                        sequence_order=metadata.get("sequence_order", 1),
                        tags=metadata.get("tags", [])
                    )

                    segment = await novel_manager.create_content_segment(segment_data)
                    saved_to_db = True
                    segment_id = str(segment.id)
                except Exception as e:
                    logger.warning(f"保存到数据库失败: {e}")

            # 获取最终统计
            final_stats = await session_manager.get_session_statistics(session_id)

            return json.dumps({
                "success": True,
                "message": "内容保存成功",
                "saved": {
                    "session_id": session_id,
                    "final_content_length": len(final_content),
                    "saved_to_database": saved_to_db,
                    "segment_id": segment_id
                },
                "session_summary": {
                    "total_iterations": final_stats["iteration_count"],
                    "total_time_minutes": final_stats["total_time_minutes"],
                    "average_rating": final_stats["average_rating"],
                    "best_rating": final_stats["best_rating"],
                    "improvement_trend": final_stats["improvement_trend"]
                },
                "metadata": metadata
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"保存内容失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "保存内容失败"
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def compare_iterations(
        session_id: str,
        iteration_a: int,
        iteration_b: int
    ) -> str:
        """
        比较两次迭代的内容

        Args:
            session_id: 会话ID
            iteration_a: 第一个迭代索引（从1开始）
            iteration_b: 第二个迭代索引（从1开始）

        Returns:
            比较结果
        """
        try:
            # 查找会话
            session = None
            for novel_id, mgr in session_managers.items():
                s = await mgr.get_session(session_id)
                if s:
                    session = s
                    break

            if not session:
                return json.dumps({
                    "success": False,
                    "message": "未找到指定会话"
                }, ensure_ascii=False, indent=2)

            # 验证迭代索引
            max_iterations = len(session.generated_contents)
            if iteration_a < 1 or iteration_a > max_iterations:
                return json.dumps({
                    "success": False,
                    "message": f"迭代A索引无效，应在1到{max_iterations}之间"
                }, ensure_ascii=False, indent=2)

            if iteration_b < 1 or iteration_b > max_iterations:
                return json.dumps({
                    "success": False,
                    "message": f"迭代B索引无效，应在1到{max_iterations}之间"
                }, ensure_ascii=False, indent=2)

            # 获取两次迭代的数据
            idx_a = iteration_a - 1
            idx_b = iteration_b - 1

            content_a = session.generated_contents[idx_a]
            content_b = session.generated_contents[idx_b]
            analysis_a = session.analysis_results[idx_a]
            analysis_b = session.analysis_results[idx_b]
            rating_a = session.user_ratings[idx_a]
            rating_b = session.user_ratings[idx_b]

            # 计算改进情况
            score_improvement = analysis_b.overall_score - analysis_a.overall_score
            rating_improvement = rating_b - rating_a

            # 内容变化
            length_change = len(content_b) - len(content_a)

            comparison = {
                "iteration_a": {
                    "index": iteration_a,
                    "overall_score": analysis_a.overall_score,
                    "user_rating": rating_a,
                    "character_count": len(content_a),
                    "strengths": analysis_a.strengths,
                    "weaknesses": analysis_a.weaknesses
                },
                "iteration_b": {
                    "index": iteration_b,
                    "overall_score": analysis_b.overall_score,
                    "user_rating": rating_b,
                    "character_count": len(content_b),
                    "strengths": analysis_b.strengths,
                    "weaknesses": analysis_b.weaknesses
                },
                "improvements": {
                    "score_change": score_improvement,
                    "score_change_percentage": f"{score_improvement * 100:+.1f}%",
                    "rating_change": rating_improvement,
                    "length_change": length_change,
                    "length_change_percentage": f"{(length_change / len(content_a) * 100):+.1f}%" if content_a else "N/A"
                },
                "quality_comparison": {
                    "narrative_flow": {
                        "a": analysis_a.narrative_flow.get("flow_score", 0),
                        "b": analysis_b.narrative_flow.get("flow_score", 0),
                        "improved": analysis_b.narrative_flow.get("flow_score", 0) > analysis_a.narrative_flow.get("flow_score", 0)
                    },
                    "dialogue_quality": {
                        "a": analysis_a.dialogue_quality.get("quality_score", 0),
                        "b": analysis_b.dialogue_quality.get("quality_score", 0),
                        "improved": analysis_b.dialogue_quality.get("quality_score", 0) > analysis_a.dialogue_quality.get("quality_score", 0)
                    },
                    "scene_vividness": {
                        "a": analysis_a.scene_vividness.get("sensory_richness_score", 0),
                        "b": analysis_b.scene_vividness.get("sensory_richness_score", 0),
                        "improved": analysis_b.scene_vividness.get("sensory_richness_score", 0) > analysis_a.scene_vividness.get("sensory_richness_score", 0)
                    }
                },
                "recommendation": "迭代B更优" if score_improvement > 0 else ("迭代A更优" if score_improvement < 0 else "两者相当")
            }

            return json.dumps({
                "success": True,
                "message": "迭代比较完成",
                "comparison": comparison
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"比较迭代失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "比较迭代失败"
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def get_active_sessions(novel_id: str) -> str:
        """
        获取小说的所有活跃创作会话

        Args:
            novel_id: 小说ID

        Returns:
            活跃会话列表
        """
        try:
            if novel_id not in session_managers:
                return json.dumps({
                    "success": True,
                    "message": "该小说暂无创作会话",
                    "sessions": []
                }, ensure_ascii=False, indent=2)

            session_manager = session_managers[novel_id]

            # 获取所有会话
            active_sessions = []
            for session_id, session in session_manager.sessions.items():
                if session.status == SessionStatus.ACTIVE:
                    stats = await session_manager.get_session_statistics(session_id)
                    active_sessions.append({
                        "session_id": session_id,
                        "session_name": session.session_name,
                        "chapter_number": session.chapter_number,
                        "created_at": session.created_at.isoformat(),
                        "iteration_count": stats["iteration_count"],
                        "average_rating": stats["average_rating"],
                        "status": session.status.value
                    })

            return json.dumps({
                "success": True,
                "message": f"找到 {len(active_sessions)} 个活跃会话",
                "sessions": active_sessions
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"获取活跃会话失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "获取活跃会话失败"
            }, ensure_ascii=False, indent=2)

    logger.info("人工协作创作工具注册成功")