"""
AI小说创作工作流
完整的创作流程管理
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json
import logging

from .core import NovelPromptGenerator, PromptComponents
from .quality_validator import QualityValidator, ValidationResult
from claude_client import ClaudeClient, CreationMetrics
from config import config

logger = logging.getLogger(__name__)


@dataclass
class CreationTask:
    """创作任务"""
    task_id: str
    novel_id: str
    chapter_number: int
    scene_type: str
    target_length: int
    status: str  # pending/generating/validating/completed/failed
    created_at: datetime
    prompt_components: Optional[PromptComponents] = None
    generated_content: Optional[str] = None
    validation_result: Optional[ValidationResult] = None
    final_content: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class CreationResult:
    """创作结果"""
    success: bool
    content: Optional[str]
    prompt_used: Optional[str]
    validation_score: float
    iterations: int
    total_tokens_used: int
    time_elapsed: float
    metadata: Dict[str, Any]


class CreationWorkflow:
    """创作工作流"""

    MAX_RETRIES = 3
    MAX_ITERATIONS = 5

    def __init__(
        self,
        novel_id: str,
        claude_api: Optional[Callable] = None,
        use_real_api: bool = None
    ):
        """
        初始化工作流

        Args:
            novel_id: 小说ID
            claude_api: Claude API调用函数（已弃用，保留以兼容）
            use_real_api: 是否使用真实API（None时根据配置自动判断）
        """
        self.novel_id = novel_id
        self.prompt_generator = NovelPromptGenerator(novel_id)
        self.validator = QualityValidator()
        self.tasks = {}
        self.results = {}

        # 初始化Claude客户端
        if use_real_api is None:
            use_real_api = config.has_claude_api_key

        if use_real_api and config.has_claude_api_key:
            self.claude_client = ClaudeClient(
                api_key=config.claude_api_key,
                model=config.claude_model
            )
            self.cost_controller = None  # 成本控制暂时在Claude客户端内部处理
            self.use_real_api = True
            logger.info("Using real Claude API for content creation")
        else:
            self.claude_client = None
            self.cost_controller = None
            self.use_real_api = False
            self.claude_api = claude_api or self._mock_claude_api
            logger.info("Using mock API for content creation")

    async def initialize(self):
        """初始化工作流"""
        await self.prompt_generator.initialize()
        logger.info(f"Initialized creation workflow for novel {self.novel_id}")

    async def create_chapter(
        self,
        chapter_number: int,
        scenes: List[Dict[str, Any]],
        batch_mode: bool = False
    ) -> Dict[str, Any]:
        """
        创作一个完整章节

        Args:
            chapter_number: 章节号
            scenes: 场景列表 [{"type": "narrative", "length": 2000, ...}]
            batch_mode: 是否批量模式

        Returns:
            章节创作结果
        """
        chapter_content = []
        chapter_results = []
        total_tokens = 0
        start_time = datetime.now()

        logger.info(f"Starting chapter {chapter_number} creation with {len(scenes)} scenes")

        for i, scene_config in enumerate(scenes):
            scene_number = i + 1

            # 创作场景
            result = await self.create_scene(
                chapter_number=chapter_number,
                scene_type=scene_config.get("type", "narrative"),
                target_length=scene_config.get("length", 2000),
                focus_characters=scene_config.get("characters"),
                previous_content="\n\n".join(chapter_content) if chapter_content else None,
                metadata={
                    "scene_number": scene_number,
                    "total_scenes": len(scenes)
                }
            )

            if result.success:
                chapter_content.append(result.content)
                chapter_results.append(result)
                total_tokens += result.total_tokens_used
            else:
                logger.error(f"Failed to create scene {scene_number}")
                if not batch_mode:
                    # 非批量模式下，单个场景失败则停止
                    break

        # 计算总体统计
        time_elapsed = (datetime.now() - start_time).total_seconds()
        success_rate = sum(1 for r in chapter_results if r.success) / len(scenes) if scenes else 0

        return {
            "success": success_rate > 0.8,  # 80%以上成功则认为章节创作成功
            "chapter_number": chapter_number,
            "content": "\n\n---\n\n".join(chapter_content),
            "scenes_created": len(chapter_content),
            "total_scenes": len(scenes),
            "success_rate": success_rate,
            "total_tokens": total_tokens,
            "time_elapsed": time_elapsed,
            "individual_results": chapter_results
        }

    async def create_scene(
        self,
        chapter_number: int,
        scene_type: str = "narrative",
        target_length: int = 2000,
        focus_characters: Optional[List[str]] = None,
        previous_content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CreationResult:
        """
        创作单个场景

        Args:
            chapter_number: 章节号
            scene_type: 场景类型
            target_length: 目标长度
            focus_characters: 焦点角色
            previous_content: 前序内容
            metadata: 元数据

        Returns:
            创作结果
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{chapter_number}_{scene_type}"
        start_time = datetime.now()

        # 创建任务
        task = CreationTask(
            task_id=task_id,
            novel_id=self.novel_id,
            chapter_number=chapter_number,
            scene_type=scene_type,
            target_length=target_length,
            status="pending",
            created_at=start_time,
            metadata=metadata or {}
        )

        self.tasks[task_id] = task

        try:
            # 1. 生成prompt
            task.status = "generating"
            prompt_components = await self.prompt_generator.generate_creation_prompt(
                chapter_number=chapter_number,
                scene_type=scene_type,
                focus_characters=focus_characters,
                target_length=target_length,
                previous_chapters=None  # 可以根据需要传入
            )
            task.prompt_components = prompt_components

            # 2. 调用Claude API生成内容
            if self.use_real_api:
                content, iterations, tokens_used, cost = await self._generate_with_validation_real(
                    prompt_components,
                    target_length
                )
            else:
                content, iterations, tokens_used = await self._generate_with_validation(
                    prompt_components,
                    target_length
                )
                cost = 0.0

            task.generated_content = content

            # 3. 最终验证
            task.status = "validating"
            final_validation = await self.validator.validate_content(
                content,
                prompt_components.context,
                validation_level="thorough"
            )
            task.validation_result = final_validation

            # 4. 如果验证失败，尝试自动修正
            if not final_validation.is_valid and iterations < self.MAX_ITERATIONS:
                content = await self._auto_correct(content, final_validation)
                # 重新验证
                final_validation = await self.validator.validate_content(
                    content,
                    prompt_components.context,
                    validation_level="standard"
                )

            task.final_content = content
            task.status = "completed"

            # 计算统计
            time_elapsed = (datetime.now() - start_time).total_seconds()

            result = CreationResult(
                success=True,
                content=content,
                prompt_used=await self.prompt_generator.export_prompt(prompt_components),
                validation_score=final_validation.score,
                iterations=iterations,
                total_tokens_used=tokens_used,
                time_elapsed=time_elapsed,
                metadata={
                    "task_id": task_id,
                    "validation_details": final_validation.details,
                    "cost": cost if self.use_real_api else 0.0,
                    "model": config.claude_model if self.use_real_api else "mock",
                    **(metadata or {})
                }
            )

            self.results[task_id] = result
            return result

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            logger.error(f"Scene creation failed: {e}")

            return CreationResult(
                success=False,
                content=None,
                prompt_used=None,
                validation_score=0,
                iterations=0,
                total_tokens_used=0,
                time_elapsed=(datetime.now() - start_time).total_seconds(),
                metadata={"error": str(e)}
            )

    async def _generate_with_validation(
        self,
        prompt_components: PromptComponents,
        target_length: int
    ) -> Tuple[str, int, int]:
        """
        生成内容并进行验证循环（模拟API）

        Args:
            prompt_components: prompt组件
            target_length: 目标长度

        Returns:
            (内容, 迭代次数, token使用量)
        """
        content = None
        iterations = 0
        total_tokens = 0

        while iterations < self.MAX_ITERATIONS:
            iterations += 1

            # 调用Claude API
            response = await self.claude_api(
                system_prompt=prompt_components.system_prompt,
                user_prompt=prompt_components.user_prompt,
                max_tokens=target_length * 2  # 留出余量
            )

            content = response.get("content", "")
            tokens_used = response.get("tokens_used", 0)
            total_tokens += tokens_used

            # 快速验证
            validation = await self.validator.validate_content(
                content,
                prompt_components.context,
                validation_level="quick"
            )

            if validation.is_valid or validation.score >= 75:
                break

            # 如果验证失败，生成修正prompt
            if iterations < self.MAX_ITERATIONS:
                correction_prompt = await self.validator.generate_correction_prompt(
                    content,
                    validation
                )
                prompt_components.user_prompt = correction_prompt

        return content, iterations, total_tokens

    async def _generate_with_validation_real(
        self,
        prompt_components: PromptComponents,
        target_length: int
    ) -> Tuple[str, int, int, float]:
        """
        使用真实Claude API生成内容并进行验证循环

        Args:
            prompt_components: prompt组件
            target_length: 目标长度

        Returns:
            (内容, 迭代次数, token使用量, 成本)
        """
        content = None
        iterations = 0
        total_tokens = 0
        total_cost = 0.0

        # 组合完整prompt
        full_prompt = await self.prompt_generator.export_prompt(prompt_components)

        while iterations < self.MAX_ITERATIONS:
            iterations += 1

            # 调用真实Claude API
            try:
                api_response = await self.claude_client.create_content(
                    system_prompt=prompt_components.system_prompt,
                    user_prompt=prompt_components.user_prompt,
                    max_tokens=min(target_length * 2, config.claude_max_tokens),
                    temperature=config.claude_temperature
                )

                content = api_response["content"]
                total_tokens += api_response["usage"]["total_tokens"]
                total_cost += api_response["cost"]

                # 快速验证
                validation = await self.validator.validate_content(
                    content,
                    prompt_components.context,
                    validation_level="quick"
                )

                if validation.is_valid or validation.score >= 75:
                    break

                # 如果验证失败，生成修正prompt
                if iterations < self.MAX_ITERATIONS:
                    correction_prompt = await self.validator.generate_correction_prompt(
                        content,
                        validation
                    )
                    prompt_components.user_prompt = correction_prompt

            except Exception as e:
                logger.error(f"API call failed on iteration {iterations}: {str(e)}")
                if iterations >= self.MAX_RETRIES:
                    raise
                await asyncio.sleep(2 ** iterations)  # 指数退避

        return content, iterations, total_tokens, total_cost

    async def _auto_correct(
        self,
        content: str,
        validation_result: ValidationResult
    ) -> str:
        """
        自动修正内容

        Args:
            content: 原始内容
            validation_result: 验证结果

        Returns:
            修正后的内容
        """
        correction_prompt = await self.validator.generate_correction_prompt(
            content,
            validation_result
        )

        if self.use_real_api:
            # 使用真实API
            try:
                api_response = await self.claude_client.create_content(
                    system_prompt="你是一位专业的文本编辑，请根据要求修正内容。保持原有风格和语调。",
                    user_prompt=correction_prompt,
                    max_tokens=len(content) * 2,
                    temperature=0.5  # 使用较低温度以获得更稳定的修正
                )
                return api_response.content
            except Exception as e:
                logger.error(f"Auto-correction failed: {str(e)}")
                return content
        else:
            # 使用模拟API
            response = await self.claude_api(
                system_prompt="你是一位专业的文本编辑，请根据要求修正内容。",
                user_prompt=correction_prompt,
                max_tokens=len(content) * 2
            )
            return response.get("content", content)  # 如果修正失败，返回原内容

    async def _mock_claude_api(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        模拟Claude API（用于测试）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_tokens: 最大token数

        Returns:
            模拟响应
        """
        # 模拟延迟
        await asyncio.sleep(1)

        # 生成模拟内容
        mock_content = f"""林潜缓缓睁开双眼，眼中闪过一丝精光。

经过三日的闭关，他终于成功将命运链与因果链初步融合，这种前所未有的尝试让他的实力有了质的飞跃。

"命运与因果相连，万物皆有定数，却又充满变数。"林潜喃喃自语，感受着体内两条法则链交织产生的奇妙力量。

就在此时，房门外传来急促的敲门声。

"林公子，大事不好了！"管事的声音透着焦急，"炎家的人已经包围了我们的宅院，说是要讨个说法！"

林潜眉头微皱。炎家，天炎域三大世家之一，其少主炎无极前日在坊市与他发生冲突，被他以因果链反噬其攻击，导致受了不轻的内伤。

"看来这场麻烦是躲不过了。"林潜站起身来，体内的法则链微微震动，随时准备应对即将到来的冲突。

他推开房门，只见院中已经聚集了数十名炎家护卫，为首的正是炎家二长老炎烈。

"林潜，你伤我炎家少主，今日必须给个交代！"炎烈声如洪钟，身上的火属性法则链散发着灼热的气息。

林潜不卑不亢地回应道："炎长老，事情的经过想必您已经清楚。是令公子先动手，我不过是正当防卫。"

"巧言令色！"炎烈冷哼一声，"不管如何，伤了我炎家的人，就要付出代价！"

话音未落，炎烈身上的权柄链猛然展开，一股强大的威压向林潜压来。

林潜不慌不忙，命运链悄然运转，将这股威压引向虚无。同时，因果链在暗中布置，每一个炎家护卫的攻击都可能成为反噬他们自己的因果。

"有意思，小小年纪竟然掌握了两条法则链。"炎烈眼中闪过一丝惊讶，"不过，在绝对的实力面前，一切技巧都是徒劳！"

炎烈正要全力出手，突然天空中传来一声清啸。

"炎烈，在我灵器坊的地盘上动手，是不是太不把我们放在眼里了？"

一道身影从天而降，正是灵器坊的首席器械师墨云山。他的形质链在周围凝聚出无数兵器虚影，每一件都散发着凌厉的气息。

局势瞬间变得更加复杂起来..."""

        return {
            "content": mock_content,
            "tokens_used": len(mock_content) // 4,  # 粗略估算
            "model": "claude-3-opus-simulated",
            "finish_reason": "stop"
        }

    async def save_to_database(
        self,
        result: CreationResult,
        batch_id: str
    ) -> str:
        """
        保存创作结果到数据库

        Args:
            result: 创作结果
            batch_id: 批次ID

        Returns:
            保存的段落ID
        """
        if not result.success or not result.content:
            raise ValueError("Cannot save failed creation result")

        # 创建内容段落
        segment_data = ContentSegmentCreate(
            batch_id=batch_id,
            segment_type=SegmentType.narrative,
            title=f"第{result.metadata.get('chapter_number')}章-场景{result.metadata.get('scene_number', 1)}",
            content=result.content,
            sequence_order=result.metadata.get('scene_number', 1),
            tags=["ai_generated", f"score_{int(result.validation_score)}"]
        )

        # 这里需要调用实际的数据库保存方法
        # segment = await novel_manager.create_content_segment(segment_data)
        # return str(segment.id)

        # 暂时返回模拟ID
        return f"segment_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "status": task.status,
            "chapter_number": task.chapter_number,
            "scene_type": task.scene_type,
            "created_at": task.created_at.isoformat(),
            "has_content": task.final_content is not None,
            "validation_score": task.validation_result.score if task.validation_result else None,
            "error": task.error_message
        }

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        获取工作流统计信息

        Returns:
            统计信息
        """
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed_tasks = sum(1 for t in self.tasks.values() if t.status == "failed")

        total_tokens = sum(r.total_tokens_used for r in self.results.values())
        average_score = (
            sum(r.validation_score for r in self.results.values()) / len(self.results)
            if self.results else 0
        )

        stats = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "total_tokens_used": total_tokens,
            "average_validation_score": average_score,
            "active_tasks": sum(1 for t in self.tasks.values() if t.status in ["pending", "generating", "validating"])
        }

        # 如果使用真实API，添加成本统计
        if self.use_real_api and self.claude_client:
            api_metrics = self.claude_client.get_metrics_summary()
            stats["api_metrics"] = api_metrics
            stats["total_cost"] = api_metrics.get("total_cost", 0.0)

            # 添加预算使用情况
            if self.cost_controller:
                try:
                    usage_stats = asyncio.run(self.cost_controller.get_usage_stats())
                    stats["budget_usage"] = usage_stats
                except:
                    pass

        return stats

    async def batch_create(
        self,
        creation_plan: List[Dict[str, Any]],
        parallel: bool = True,
        max_concurrent: int = 3
    ) -> List[CreationResult]:
        """
        批量创作

        Args:
            creation_plan: 创作计划列表
            parallel: 是否并行处理
            max_concurrent: 最大并发数

        Returns:
            创作结果列表
        """
        results = []

        if parallel:
            # 并行处理
            semaphore = asyncio.Semaphore(max_concurrent)

            async def create_with_semaphore(plan):
                async with semaphore:
                    return await self.create_scene(**plan)

            tasks = [create_with_semaphore(plan) for plan in creation_plan]
            results = await asyncio.gather(*tasks)
        else:
            # 串行处理
            for plan in creation_plan:
                result = await self.create_scene(**plan)
                results.append(result)

        return results

    def export_workflow_data(self, filepath: str):
        """
        导出工作流数据

        Args:
            filepath: 文件路径
        """
        export_data = {
            "workflow_id": self.novel_id,
            "statistics": self.get_workflow_statistics(),
            "tasks": [
                {
                    "task_id": task.task_id,
                    "chapter": task.chapter_number,
                    "scene_type": task.scene_type,
                    "status": task.status,
                    "validation_score": task.validation_result.score if task.validation_result else None
                }
                for task in self.tasks.values()
            ],
            "exported_at": datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)