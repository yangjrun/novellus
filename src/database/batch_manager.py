"""
文本批次管理系统
专门用于管理小说创作的分批次文本内容，支持渐进式内容管理
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum

from .data_access import get_global_manager, get_novel_manager, DatabaseError
from .models import *

logger = logging.getLogger(__name__)


class BatchPriority(int, Enum):
    """批次优先级枚举"""
    LOW = 1
    NORMAL = 3
    HIGH = 5
    URGENT = 7
    CRITICAL = 9


class BatchWorkflowStatus(str, Enum):
    """批次工作流状态"""
    DRAFT = "draft"
    OUTLINE = "outline"
    WRITING = "writing"
    REVIEW = "review"
    REVISION = "revision"
    COMPLETED = "completed"
    PUBLISHED = "published"


class ContentBatchManager:
    """内容批次管理器"""

    def __init__(self, novel_id: Union[str, UUID]):
        self.novel_id = str(novel_id)
        self.novel_manager = get_novel_manager(novel_id)

    async def create_batch_series(
        self,
        series_name: str,
        batch_type: BatchType,
        batch_count: int,
        description: Optional[str] = None,
        priority: int = BatchPriority.NORMAL,
        start_date: Optional[datetime] = None,
        interval_days: int = 7
    ) -> List[ContentBatch]:
        """创建批次系列（连续的多个批次）"""
        try:
            batches = []
            current_date = start_date or datetime.now()

            for i in range(batch_count):
                batch_name = f"{series_name}_第{i+1}批"
                batch_number = await self._get_next_batch_number()

                due_date = current_date + timedelta(days=interval_days * (i + 1))

                batch_data = ContentBatchCreate(
                    novel_id=UUID(self.novel_id),
                    batch_name=batch_name,
                    batch_number=batch_number,
                    batch_type=batch_type,
                    description=f"{description} - 第{i+1}批" if description else None,
                    priority=priority,
                    due_date=due_date,
                    metadata={
                        "series_name": series_name,
                        "series_index": i + 1,
                        "series_total": batch_count,
                        "workflow_status": BatchWorkflowStatus.DRAFT.value
                    }
                )

                batch = await self.novel_manager.create_content_batch(batch_data)
                batches.append(batch)

            logger.info(f"创建批次系列 '{series_name}'，共 {batch_count} 个批次")
            return batches

        except Exception as e:
            logger.error(f"创建批次系列失败: {e}")
            raise DatabaseError(f"创建批次系列失败: {e}")

    async def create_template_batch(
        self,
        template_name: str,
        batch_type: BatchType,
        segment_templates: List[Dict[str, Any]]
    ) -> ContentBatch:
        """创建模板批次（包含预定义的段落模板）"""
        try:
            batch_number = await self._get_next_batch_number()

            # 创建批次
            batch_data = ContentBatchCreate(
                novel_id=UUID(self.novel_id),
                batch_name=template_name,
                batch_number=batch_number,
                batch_type=batch_type,
                description=f"基于模板创建的批次",
                metadata={
                    "is_template": True,
                    "template_name": template_name,
                    "workflow_status": BatchWorkflowStatus.OUTLINE.value
                }
            )

            batch = await self.novel_manager.create_content_batch(batch_data)

            # 创建模板段落
            for i, template in enumerate(segment_templates):
                segment_data = ContentSegmentCreate(
                    batch_id=batch.id,
                    segment_type=SegmentType(template.get("type", "narrative")),
                    title=template.get("title", f"段落 {i+1}"),
                    content=template.get("content", "[待填写]"),
                    sequence_order=i + 1,
                    tags=template.get("tags", []),
                    metadata={
                        "is_template": True,
                        "template_notes": template.get("notes", "")
                    }
                )

                await self.novel_manager.create_content_segment(segment_data)

            logger.info(f"创建模板批次 '{template_name}'，包含 {len(segment_templates)} 个段落模板")
            return batch

        except Exception as e:
            logger.error(f"创建模板批次失败: {e}")
            raise DatabaseError(f"创建模板批次失败: {e}")

    async def get_batch_progress(self, batch_id: Union[str, UUID]) -> Dict[str, Any]:
        """获取批次进度信息"""
        try:
            batch = await self.novel_manager.pg_repo.get_content_batch_by_id(UUID(batch_id))
            if not batch:
                raise DatabaseError(f"批次不存在: {batch_id}")

            segments = await self.novel_manager.get_content_segments(batch_id)

            # 计算进度统计
            total_segments = len(segments)
            completed_segments = sum(1 for s in segments if s.status == SegmentStatus.APPROVED)
            draft_segments = sum(1 for s in segments if s.status == SegmentStatus.DRAFT)
            review_segments = sum(1 for s in segments if s.status == SegmentStatus.REVIEW)

            completion_rate = (completed_segments / total_segments * 100) if total_segments > 0 else 0

            # 计算预计完成时间
            estimated_completion = await self._estimate_completion_time(batch, segments)

            progress_info = {
                "batch_id": str(batch.id),
                "batch_name": batch.batch_name,
                "batch_type": batch.batch_type,
                "status": batch.status,
                "workflow_status": batch.metadata.get("workflow_status"),
                "word_count": batch.word_count,
                "progress": {
                    "total_segments": total_segments,
                    "completed_segments": completed_segments,
                    "draft_segments": draft_segments,
                    "review_segments": review_segments,
                    "completion_rate": round(completion_rate, 2)
                },
                "timeline": {
                    "created_at": batch.created_at.isoformat(),
                    "due_date": batch.due_date.isoformat() if batch.due_date else None,
                    "estimated_completion": estimated_completion,
                    "is_overdue": batch.due_date and datetime.now() > batch.due_date
                },
                "quality_metrics": await self._calculate_quality_metrics(segments)
            }

            return progress_info

        except Exception as e:
            logger.error(f"获取批次进度失败: {e}")
            raise DatabaseError(f"获取批次进度失败: {e}")

    async def get_batch_dashboard(self) -> Dict[str, Any]:
        """获取批次管理仪表板数据"""
        try:
            # 获取所有批次
            all_batches = await self.novel_manager.get_content_batches()

            # 按状态分组
            status_groups = {}
            for batch in all_batches:
                status = batch.status.value
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(batch)

            # 按类型分组
            type_groups = {}
            for batch in all_batches:
                batch_type = batch.batch_type.value
                if batch_type not in type_groups:
                    type_groups[batch_type] = []
                type_groups[batch_type].append(batch)

            # 计算总体统计
            total_batches = len(all_batches)
            total_word_count = sum(batch.word_count for batch in all_batches)
            completed_batches = len(status_groups.get("completed", []))
            overdue_batches = [
                batch for batch in all_batches
                if batch.due_date and datetime.now() > batch.due_date and batch.status != BatchStatus.COMPLETED
            ]

            # 获取近期活动
            recent_batches = sorted(
                all_batches,
                key=lambda x: x.updated_at,
                reverse=True
            )[:10]

            # 计算每日进度
            daily_progress = await self._calculate_daily_progress()

            dashboard_data = {
                "overview": {
                    "total_batches": total_batches,
                    "completed_batches": completed_batches,
                    "completion_rate": (completed_batches / total_batches * 100) if total_batches > 0 else 0,
                    "total_word_count": total_word_count,
                    "overdue_count": len(overdue_batches)
                },
                "status_distribution": {
                    status: len(batches) for status, batches in status_groups.items()
                },
                "type_distribution": {
                    batch_type: len(batches) for batch_type, batches in type_groups.items()
                },
                "recent_activity": [
                    {
                        "batch_id": str(batch.id),
                        "batch_name": batch.batch_name,
                        "batch_type": batch.batch_type.value,
                        "status": batch.status.value,
                        "updated_at": batch.updated_at.isoformat(),
                        "word_count": batch.word_count
                    }
                    for batch in recent_batches
                ],
                "overdue_batches": [
                    {
                        "batch_id": str(batch.id),
                        "batch_name": batch.batch_name,
                        "due_date": batch.due_date.isoformat(),
                        "days_overdue": (datetime.now() - batch.due_date).days
                    }
                    for batch in overdue_batches
                ],
                "daily_progress": daily_progress,
                "last_updated": datetime.now().isoformat()
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"获取批次仪表板失败: {e}")
            raise DatabaseError(f"获取批次仪表板失败: {e}")

    async def batch_workflow_transition(
        self,
        batch_id: Union[str, UUID],
        target_status: BatchWorkflowStatus,
        notes: Optional[str] = None
    ) -> ContentBatch:
        """批次工作流状态转换"""
        try:
            batch = await self.novel_manager.pg_repo.get_content_batch_by_id(UUID(batch_id))
            if not batch:
                raise DatabaseError(f"批次不存在: {batch_id}")

            current_workflow_status = batch.metadata.get("workflow_status", BatchWorkflowStatus.DRAFT.value)

            # 验证状态转换的合法性
            if not self._is_valid_transition(current_workflow_status, target_status.value):
                raise DatabaseError(f"无效的状态转换: {current_workflow_status} -> {target_status.value}")

            # 更新工作流状态
            new_metadata = batch.metadata.copy()
            new_metadata["workflow_status"] = target_status.value
            new_metadata["workflow_history"] = new_metadata.get("workflow_history", [])
            new_metadata["workflow_history"].append({
                "from_status": current_workflow_status,
                "to_status": target_status.value,
                "timestamp": datetime.now().isoformat(),
                "notes": notes
            })

            # 根据工作流状态更新批次状态
            batch_status_mapping = {
                BatchWorkflowStatus.DRAFT: BatchStatus.PLANNING,
                BatchWorkflowStatus.OUTLINE: BatchStatus.PLANNING,
                BatchWorkflowStatus.WRITING: BatchStatus.IN_PROGRESS,
                BatchWorkflowStatus.REVIEW: BatchStatus.IN_PROGRESS,
                BatchWorkflowStatus.REVISION: BatchStatus.IN_PROGRESS,
                BatchWorkflowStatus.COMPLETED: BatchStatus.COMPLETED,
                BatchWorkflowStatus.PUBLISHED: BatchStatus.COMPLETED
            }

            new_batch_status = batch_status_mapping.get(target_status)

            update_data = ContentBatchUpdate(
                status=new_batch_status,
                metadata=new_metadata,
                completed_at=datetime.now() if target_status == BatchWorkflowStatus.COMPLETED else None
            )

            updated_batch = await self.novel_manager.update_content_batch(batch_id, update_data)

            logger.info(f"批次工作流转换: {batch.batch_name} {current_workflow_status} -> {target_status.value}")
            return updated_batch

        except Exception as e:
            logger.error(f"批次工作流转换失败: {e}")
            raise DatabaseError(f"批次工作流转换失败: {e}")

    async def auto_schedule_batches(
        self,
        target_batches_per_week: int = 3,
        weeks_ahead: int = 4
    ) -> List[ContentBatch]:
        """自动调度批次计划"""
        try:
            # 获取所有未完成的批次
            pending_batches = await self.novel_manager.get_content_batches(
                status=BatchStatus.PLANNING
            )

            # 获取进行中的批次
            in_progress_batches = await self.novel_manager.get_content_batches(
                status=BatchStatus.IN_PROGRESS
            )

            # 计算当前工作负载
            current_workload = len(in_progress_batches)

            # 生成调度计划
            schedule_plan = []
            start_date = datetime.now()

            for week in range(weeks_ahead):
                week_start = start_date + timedelta(weeks=week)

                # 计算这一周可以安排的批次数量
                available_slots = max(0, target_batches_per_week - (current_workload if week == 0 else 0))

                # 为这一周安排批次
                week_batches = []
                for day in range(min(available_slots, len(pending_batches))):
                    if not pending_batches:
                        break

                    batch = pending_batches.pop(0)

                    # 设置截止日期
                    due_date = week_start + timedelta(days=day * 2)  # 每两天一个批次

                    # 更新批次
                    update_data = ContentBatchUpdate(
                        due_date=due_date,
                        priority=BatchPriority.NORMAL,
                        metadata={
                            **batch.metadata,
                            "auto_scheduled": True,
                            "scheduled_week": week + 1,
                            "schedule_timestamp": datetime.now().isoformat()
                        }
                    )

                    updated_batch = await self.novel_manager.update_content_batch(
                        batch.id, update_data
                    )
                    week_batches.append(updated_batch)

                schedule_plan.extend(week_batches)

            logger.info(f"自动调度完成，安排了 {len(schedule_plan)} 个批次")
            return schedule_plan

        except Exception as e:
            logger.error(f"自动调度批次失败: {e}")
            raise DatabaseError(f"自动调度批次失败: {e}")

    # =============================================================================
    # 私有辅助方法
    # =============================================================================

    async def _get_next_batch_number(self) -> int:
        """获取下一个批次编号"""
        batches = await self.novel_manager.get_content_batches()
        if not batches:
            return 1
        return max(batch.batch_number for batch in batches) + 1

    async def _estimate_completion_time(
        self,
        batch: ContentBatch,
        segments: List[ContentSegment]
    ) -> Optional[str]:
        """估算完成时间"""
        try:
            if batch.status == BatchStatus.COMPLETED:
                return None

            # 计算平均写作速度（基于历史数据）
            avg_words_per_day = await self._calculate_avg_writing_speed()
            if avg_words_per_day == 0:
                return None

            # 估算剩余工作量
            remaining_segments = [s for s in segments if s.status not in [SegmentStatus.APPROVED]]
            estimated_remaining_words = len(remaining_segments) * 200  # 假设每段平均200字

            # 计算预计天数
            estimated_days = estimated_remaining_words / avg_words_per_day
            estimated_completion = datetime.now() + timedelta(days=estimated_days)

            return estimated_completion.isoformat()

        except Exception:
            return None

    async def _calculate_avg_writing_speed(self) -> float:
        """计算平均写作速度"""
        try:
            # 这里可以基于历史数据计算，暂时返回固定值
            return 500.0  # 每天500字
        except Exception:
            return 0.0

    async def _calculate_quality_metrics(self, segments: List[ContentSegment]) -> Dict[str, Any]:
        """计算质量指标"""
        if not segments:
            return {}

        total_segments = len(segments)
        avg_word_count = sum(s.word_count for s in segments) / total_segments
        revision_rate = sum(s.revision_count for s in segments) / total_segments

        return {
            "avg_word_count_per_segment": round(avg_word_count, 2),
            "avg_revision_count": round(revision_rate, 2),
            "quality_score": min(100, max(0, 100 - revision_rate * 10))  # 简单的质量评分
        }

    async def _calculate_daily_progress(self) -> List[Dict[str, Any]]:
        """计算每日进度"""
        try:
            # 获取最近30天的进度数据
            progress_data = []
            for i in range(30):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")

                # 这里可以查询实际的每日进度数据
                # 暂时返回模拟数据
                progress_data.append({
                    "date": date_str,
                    "words_written": 200 + (i % 7) * 100,  # 模拟数据
                    "segments_completed": 1 + (i % 3),
                    "batches_completed": 1 if i % 7 == 0 else 0
                })

            return list(reversed(progress_data))

        except Exception:
            return []

    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        """验证工作流状态转换是否合法"""
        valid_transitions = {
            BatchWorkflowStatus.DRAFT.value: [
                BatchWorkflowStatus.OUTLINE.value,
                BatchWorkflowStatus.WRITING.value
            ],
            BatchWorkflowStatus.OUTLINE.value: [
                BatchWorkflowStatus.WRITING.value,
                BatchWorkflowStatus.DRAFT.value
            ],
            BatchWorkflowStatus.WRITING.value: [
                BatchWorkflowStatus.REVIEW.value,
                BatchWorkflowStatus.REVISION.value,
                BatchWorkflowStatus.COMPLETED.value
            ],
            BatchWorkflowStatus.REVIEW.value: [
                BatchWorkflowStatus.REVISION.value,
                BatchWorkflowStatus.COMPLETED.value
            ],
            BatchWorkflowStatus.REVISION.value: [
                BatchWorkflowStatus.WRITING.value,
                BatchWorkflowStatus.REVIEW.value,
                BatchWorkflowStatus.COMPLETED.value
            ],
            BatchWorkflowStatus.COMPLETED.value: [
                BatchWorkflowStatus.PUBLISHED.value,
                BatchWorkflowStatus.REVISION.value
            ],
            BatchWorkflowStatus.PUBLISHED.value: []
        }

        return to_status in valid_transitions.get(from_status, [])


# 便捷函数
async def get_batch_manager(novel_id: Union[str, UUID]) -> ContentBatchManager:
    """获取批次管理器"""
    return ContentBatchManager(novel_id)