"""
核心数据模型 - 项目、小说、批次和内容段落
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator


class ProjectStatus(str, Enum):
    """项目状态枚举"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class NovelStatus(str, Enum):
    """小说状态枚举"""
    PLANNING = "planning"
    WRITING = "writing"
    REVIEWING = "reviewing"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BatchType(str, Enum):
    """批次类型枚举"""
    WORLDBUILDING = "worldbuilding"
    CHARACTERS = "characters"
    PLOT = "plot"
    SCENES = "scenes"
    DIALOGUE = "dialogue"
    REVISION = "revision"


class BatchStatus(str, Enum):
    """批次状态枚举"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class SegmentType(str, Enum):
    """段落类型枚举"""
    NARRATIVE = "narrative"
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"
    ACTION = "action"
    THOUGHT = "thought"
    FLASHBACK = "flashback"


class SegmentStatus(str, Enum):
    """段落状态枚举"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"


class BaseModelWithTimestamp(BaseModel):
    """带时间戳的基础模型"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Project(BaseModelWithTimestamp):
    """项目模型"""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255, description="项目唯一名称")
    title: str = Field(..., min_length=1, max_length=500, description="项目标题")
    description: Optional[str] = Field(None, description="项目描述")
    author: Optional[str] = Field(None, max_length=255, description="作者")
    genre: Optional[str] = Field(None, max_length=100, description="题材类型")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, description="项目状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('项目名称不能为空')
        return v.strip()

    @validator('title')
    def validate_title(cls, v):
        if not v or v.isspace():
            raise ValueError('项目标题不能为空')
        return v.strip()


class Novel(BaseModelWithTimestamp):
    """小说模型"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID = Field(..., description="关联的项目ID")
    name: str = Field(..., min_length=1, max_length=255, description="小说唯一名称")
    title: str = Field(..., min_length=1, max_length=500, description="小说标题")
    description: Optional[str] = Field(None, description="小说描述")
    volume_number: int = Field(default=1, ge=1, description="卷号")
    status: NovelStatus = Field(default=NovelStatus.PLANNING, description="小说状态")
    word_count: int = Field(default=0, ge=0, description="总字数")
    chapter_count: int = Field(default=0, ge=0, description="章节数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('小说名称不能为空')
        return v.strip()

    @validator('title')
    def validate_title(cls, v):
        if not v or v.isspace():
            raise ValueError('小说标题不能为空')
        return v.strip()


class ContentBatch(BaseModelWithTimestamp):
    """内容批次模型"""
    id: UUID = Field(default_factory=uuid4)
    novel_id: UUID = Field(..., description="关联的小说ID")
    batch_name: str = Field(..., min_length=1, max_length=255, description="批次名称")
    batch_number: int = Field(..., ge=1, description="批次编号")
    batch_type: BatchType = Field(..., description="批次类型")
    description: Optional[str] = Field(None, description="批次描述")
    word_count: int = Field(default=0, ge=0, description="批次字数")
    status: BatchStatus = Field(default=BatchStatus.PLANNING, description="批次状态")
    priority: int = Field(default=0, description="优先级")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    @validator('batch_name')
    def validate_batch_name(cls, v):
        if not v or v.isspace():
            raise ValueError('批次名称不能为空')
        return v.strip()

    @validator('completed_at')
    def validate_completed_at(cls, v, values):
        if v and values.get('status') != BatchStatus.COMPLETED:
            raise ValueError('只有已完成的批次才能设置完成时间')
        return v


class ContentSegment(BaseModelWithTimestamp):
    """内容段落模型"""
    id: UUID = Field(default_factory=uuid4)
    batch_id: UUID = Field(..., description="关联的批次ID")
    segment_type: SegmentType = Field(..., description="段落类型")
    title: Optional[str] = Field(None, max_length=500, description="段落标题")
    content: str = Field(..., min_length=1, description="段落内容")
    word_count: int = Field(default=0, ge=0, description="字数")
    sequence_order: int = Field(..., ge=1, description="序列顺序")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    emotions: List[str] = Field(default_factory=list, description="情感标签")
    characters: List[UUID] = Field(default_factory=list, description="涉及角色ID列表")
    locations: List[UUID] = Field(default_factory=list, description="涉及地点ID列表")
    status: SegmentStatus = Field(default=SegmentStatus.DRAFT, description="段落状态")
    revision_count: int = Field(default=0, ge=0, description="修订次数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    @validator('content')
    def validate_content(cls, v):
        if not v or v.isspace():
            raise ValueError('段落内容不能为空')
        return v.strip()

    @validator('word_count', always=True)
    def calculate_word_count(cls, v, values):
        content = values.get('content', '')
        if content:
            # 计算中文字符数（去除空白字符）
            import re
            clean_content = re.sub(r'\s+', '', content)
            return len(clean_content)
        return 0

    @validator('tags')
    def validate_tags(cls, v):
        # 去除空标签和重复标签
        return list(set(tag.strip() for tag in v if tag and tag.strip()))

    @validator('emotions')
    def validate_emotions(cls, v):
        # 去除空情感标签和重复标签
        return list(set(emotion.strip() for emotion in v if emotion and emotion.strip()))


# 创建模型的请求/响应类型
class ProjectCreate(BaseModel):
    """创建项目请求模型"""
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    """更新项目请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    status: Optional[ProjectStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class NovelCreate(BaseModel):
    """创建小说请求模型"""
    project_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    volume_number: int = Field(default=1, ge=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NovelUpdate(BaseModel):
    """更新小说请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    volume_number: Optional[int] = Field(None, ge=1)
    status: Optional[NovelStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentBatchCreate(BaseModel):
    """创建内容批次请求模型"""
    novel_id: UUID
    batch_name: str = Field(..., min_length=1, max_length=255)
    batch_number: int = Field(..., ge=1)
    batch_type: BatchType
    description: Optional[str] = None
    priority: int = Field(default=0)
    due_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentBatchUpdate(BaseModel):
    """更新内容批次请求模型"""
    batch_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[BatchStatus] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentSegmentCreate(BaseModel):
    """创建内容段落请求模型"""
    batch_id: UUID
    segment_type: SegmentType
    title: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    sequence_order: int = Field(..., ge=1)
    tags: List[str] = Field(default_factory=list)
    emotions: List[str] = Field(default_factory=list)
    characters: List[UUID] = Field(default_factory=list)
    locations: List[UUID] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentSegmentUpdate(BaseModel):
    """更新内容段落请求模型"""
    segment_type: Optional[SegmentType] = None
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    sequence_order: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    emotions: Optional[List[str]] = None
    characters: Optional[List[UUID]] = None
    locations: Optional[List[UUID]] = None
    status: Optional[SegmentStatus] = None
    metadata: Optional[Dict[str, Any]] = None