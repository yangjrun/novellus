"""
Batch Creation Manager for Novellus
批量创作管理器，支持并发创作和成本优化
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict

from prompt_generator.creation_workflow import CreationWorkflow, CreationResult
# from claude_client import CostController
from config import config

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """任务优先级"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchTask:
    """批量任务"""
    task_id: str
    novel_id: str
    chapter_number: int
    scene_type: str
    target_length: int
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[CreationResult] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "novel_id": self.novel_id,
            "chapter_number": self.chapter_number,
            "scene_type": self.scene_type,
            "target_length": self.target_length,
            "priority": self.priority.name,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class BatchStatistics:
    """批量统计"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    total_time: float = 0.0
    average_time_per_task: float = 0.0
    success_rate: float = 0.0
    average_validation_score: float = 0.0

    def update_from_result(self, result: CreationResult):
        """从结果更新统计"""
        if result.success:
            self.completed_tasks += 1
            self.total_tokens_used += result.total_tokens_used
            self.total_cost += result.metadata.get("cost", 0.0)
            self.total_time += result.time_elapsed

            # 更新平均分数
            if self.completed_tasks == 1:
                self.average_validation_score = result.validation_score
            else:
                self.average_validation_score = (
                    (self.average_validation_score * (self.completed_tasks - 1) + result.validation_score)
                    / self.completed_tasks
                )
        else:
            self.failed_tasks += 1

        # 更新成功率
        total_processed = self.completed_tasks + self.failed_tasks
        if total_processed > 0:
            self.success_rate = self.completed_tasks / total_processed
            self.average_time_per_task = self.total_time / total_processed

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "cancelled_tasks": self.cancelled_tasks,
            "total_tokens_used": self.total_tokens_used,
            "total_cost": round(self.total_cost, 4),
            "total_time": round(self.total_time, 2),
            "average_time_per_task": round(self.average_time_per_task, 2),
            "success_rate": round(self.success_rate, 2),
            "average_validation_score": round(self.average_validation_score, 2)
        }


class BatchCreationManager:
    """批量创作管理器"""

    def __init__(
        self,
        max_concurrent: int = 3,
        rate_limit: int = 5,  # 每分钟请求数
        use_real_api: bool = None,
        enable_cost_control: bool = True,
        enable_auto_retry: bool = True
    ):
        """初始化批量管理器

        Args:
            max_concurrent: 最大并发数
            rate_limit: 每分钟最大请求数
            use_real_api: 是否使用真实API
            enable_cost_control: 启用成本控制
            enable_auto_retry: 启用自动重试
        """
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.use_real_api = use_real_api if use_real_api is not None else config.has_claude_api_key
        self.enable_cost_control = enable_cost_control
        self.enable_auto_retry = enable_auto_retry

        # 工作流缓存
        self.workflows: Dict[str, CreationWorkflow] = {}

        # 任务队列
        self.task_queue: List[BatchTask] = []
        self.running_tasks: Dict[str, BatchTask] = {}
        self.completed_tasks: Dict[str, BatchTask] = {}

        # 统计信息
        self.statistics = BatchStatistics()

        # 成本控制
        if self.enable_cost_control and self.use_real_api:
            self.cost_controller = CostController(
                daily_limit=config.daily_cost_limit,
                monthly_limit=config.monthly_cost_limit
            )
        else:
            self.cost_controller = None

        # 并发控制
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = asyncio.Semaphore(rate_limit)
        self._rate_limit_reset_task = None

        # 状态
        self.is_running = False
        self.is_paused = False

    async def add_task(
        self,
        novel_id: str,
        chapter_number: int,
        scene_type: str = "narrative",
        target_length: int = 2000,
        priority: TaskPriority = TaskPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """添加任务到队列

        Args:
            novel_id: 小说ID
            chapter_number: 章节号
            scene_type: 场景类型
            target_length: 目标长度
            priority: 优先级
            metadata: 元数据

        Returns:
            任务ID
        """
        task_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.task_queue)}"

        task = BatchTask(
            task_id=task_id,
            novel_id=novel_id,
            chapter_number=chapter_number,
            scene_type=scene_type,
            target_length=target_length,
            priority=priority,
            metadata=metadata or {}
        )

        self.task_queue.append(task)
        self.statistics.total_tasks += 1

        # 按优先级排序
        self.task_queue.sort(key=lambda t: (t.priority.value, t.created_at))

        logger.info(f"Added task {task_id} to queue (Priority: {priority.name})")
        return task_id

    async def add_chapter_tasks(
        self,
        novel_id: str,
        chapter_number: int,
        scenes: List[Dict[str, Any]],
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> List[str]:
        """添加整章的任务

        Args:
            novel_id: 小说ID
            chapter_number: 章节号
            scenes: 场景配置列表
            priority: 优先级

        Returns:
            任务ID列表
        """
        task_ids = []
        for i, scene_config in enumerate(scenes):
            task_id = await self.add_task(
                novel_id=novel_id,
                chapter_number=chapter_number,
                scene_type=scene_config.get("type", "narrative"),
                target_length=scene_config.get("length", 2000),
                priority=priority,
                metadata={
                    "scene_number": i + 1,
                    "total_scenes": len(scenes),
                    **scene_config.get("metadata", {})
                }
            )
            task_ids.append(task_id)

        logger.info(f"Added {len(task_ids)} tasks for chapter {chapter_number}")
        return task_ids

    async def start(self):
        """启动批量处理"""
        if self.is_running:
            logger.warning("Batch manager is already running")
            return

        self.is_running = True
        self.is_paused = False
        logger.info("Starting batch creation manager")

        # 启动速率限制重置任务
        if not self._rate_limit_reset_task:
            self._rate_limit_reset_task = asyncio.create_task(self._reset_rate_limit())

        # 处理任务队列
        await self._process_queue()

    async def _process_queue(self):
        """处理任务队列"""
        while self.is_running:
            if self.is_paused:
                await asyncio.sleep(1)
                continue

            # 获取下一个任务
            if not self.task_queue:
                await asyncio.sleep(1)
                continue

            task = self.task_queue.pop(0)

            # 检查成本预算
            if self.cost_controller and self.use_real_api:
                # 估算成本
                estimated_cost = self._estimate_task_cost(task)
                budget_ok = await self.cost_controller.check_budget(estimated_cost)

                if not budget_ok:
                    logger.warning(f"Budget limit reached. Pausing task {task.task_id}")
                    task.status = TaskStatus.CANCELLED
                    task.error = "Budget limit exceeded"
                    self.completed_tasks[task.task_id] = task
                    self.statistics.cancelled_tasks += 1
                    continue

            # 执行任务
            async with self.semaphore:
                async with self.rate_limiter:
                    await self._execute_task(task)

    async def _execute_task(self, task: BatchTask):
        """执行单个任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self.running_tasks[task.task_id] = task

        try:
            # 获取或创建工作流
            workflow = await self._get_workflow(task.novel_id)

            # 创作场景
            logger.info(f"Executing task {task.task_id}: Chapter {task.chapter_number}, {task.scene_type}")

            result = await workflow.create_scene(
                chapter_number=task.chapter_number,
                scene_type=task.scene_type,
                target_length=task.target_length,
                metadata=task.metadata
            )

            task.result = result
            task.completed_at = datetime.now()

            if result.success:
                task.status = TaskStatus.COMPLETED
                logger.info(f"Task {task.task_id} completed successfully (Score: {result.validation_score})")

                # 记录实际成本
                if self.cost_controller and self.use_real_api:
                    actual_cost = result.metadata.get("cost", 0.0)
                    await self.cost_controller.record_usage(actual_cost)
            else:
                task.status = TaskStatus.FAILED
                task.error = result.metadata.get("error", "Unknown error")
                logger.error(f"Task {task.task_id} failed: {task.error}")

                # 自动重试
                if self.enable_auto_retry and task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    self.task_queue.append(task)
                    logger.info(f"Retrying task {task.task_id} (Attempt {task.retry_count}/{task.max_retries})")
                    return

            # 更新统计
            self.statistics.update_from_result(result)

        except Exception as e:
            logger.error(f"Task {task.task_id} failed with exception: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self.statistics.failed_tasks += 1

        finally:
            # 移动到完成列表
            del self.running_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task

    async def _get_workflow(self, novel_id: str) -> CreationWorkflow:
        """获取或创建工作流"""
        if novel_id not in self.workflows:
            self.workflows[novel_id] = CreationWorkflow(
                novel_id=novel_id,
                use_real_api=self.use_real_api
            )
            await self.workflows[novel_id].initialize()
        return self.workflows[novel_id]

    def _estimate_task_cost(self, task: BatchTask) -> float:
        """估算任务成本"""
        # 粗略估算：输入约1000 tokens，输出约target_length/4 tokens
        input_tokens = 1000
        output_tokens = task.target_length // 4

        # 使用Opus模型的价格
        input_cost = (input_tokens / 1_000_000) * 15.0
        output_cost = (output_tokens / 1_000_000) * 75.0

        return input_cost + output_cost

    async def _reset_rate_limit(self):
        """定期重置速率限制"""
        while self.is_running:
            await asyncio.sleep(60)  # 每分钟重置
            self.rate_limiter = asyncio.Semaphore(self.rate_limit)

    async def pause(self):
        """暂停处理"""
        self.is_paused = True
        logger.info("Batch creation manager paused")

    async def resume(self):
        """恢复处理"""
        self.is_paused = False
        logger.info("Batch creation manager resumed")

    async def stop(self):
        """停止处理"""
        self.is_running = False

        if self._rate_limit_reset_task:
            self._rate_limit_reset_task.cancel()
            self._rate_limit_reset_task = None

        logger.info("Batch creation manager stopped")

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "queue_size": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "statistics": self.statistics.to_dict(),
            "use_real_api": self.use_real_api,
            "cost_control_enabled": self.enable_cost_control
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 检查运行中的任务
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].to_dict()

        # 检查完成的任务
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            task_dict = task.to_dict()

            if task.result:
                task_dict["result"] = {
                    "success": task.result.success,
                    "validation_score": task.result.validation_score,
                    "tokens_used": task.result.total_tokens_used,
                    "time_elapsed": task.result.time_elapsed
                }

            return task_dict

        # 检查队列中的任务
        for task in self.task_queue:
            if task.task_id == task_id:
                return task.to_dict()

        return None

    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列信息"""
        # 按优先级分组
        priority_groups = defaultdict(list)
        for task in self.task_queue:
            priority_groups[task.priority.name].append(task.task_id)

        return {
            "total_queued": len(self.task_queue),
            "by_priority": {
                "HIGH": len(priority_groups["HIGH"]),
                "MEDIUM": len(priority_groups["MEDIUM"]),
                "LOW": len(priority_groups["LOW"])
            },
            "next_tasks": [t.task_id for t in self.task_queue[:5]]  # 下5个任务
        }

    async def wait_for_completion(self, timeout: Optional[float] = None):
        """等待所有任务完成

        Args:
            timeout: 超时时间（秒）
        """
        start_time = datetime.now()

        while len(self.task_queue) > 0 or len(self.running_tasks) > 0:
            if timeout:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= timeout:
                    logger.warning(f"Batch processing timeout after {timeout} seconds")
                    break

            await asyncio.sleep(1)

        logger.info("All tasks completed or timeout reached")

    def export_results(self, filepath: str):
        """导出结果到文件

        Args:
            filepath: 文件路径
        """
        export_data = {
            "export_time": datetime.now().isoformat(),
            "statistics": self.statistics.to_dict(),
            "completed_tasks": [
                {
                    **task.to_dict(),
                    "content": task.result.content if task.result and task.result.success else None
                }
                for task in self.completed_tasks.values()
            ],
            "failed_tasks": [
                task.to_dict()
                for task in self.completed_tasks.values()
                if task.status == TaskStatus.FAILED
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Results exported to {filepath}")

    def clear_completed(self):
        """清除已完成的任务"""
        self.completed_tasks.clear()
        logger.info("Cleared completed tasks")