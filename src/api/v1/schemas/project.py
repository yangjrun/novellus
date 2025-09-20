"""
Project and Novel Schemas
Request/Response models for project and novel endpoints
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field

from api.v1.schemas.base import (
    BaseResponse,
    TimestampedModel,
    IDModel,
    NamedModel,
    MetadataModel,
    StatusEnum
)


# Enums
class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class NovelStatus(str, Enum):
    """Novel status enumeration"""
    PLANNING = "planning"
    WRITING = "writing"
    REVIEWING = "reviewing"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Request Models
class ProjectCreateRequest(NamedModel, MetadataModel):
    """Project creation request"""
    title: str = Field(..., min_length=1, max_length=500, description="Project title")
    author: Optional[str] = Field(None, max_length=255, description="Author name")
    genre: Optional[str] = Field(None, max_length=100, description="Genre")


class ProjectUpdateRequest(BaseModel):
    """Project update request"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    author: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    status: Optional[ProjectStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class NovelCreateRequest(NamedModel, MetadataModel):
    """Novel creation request"""
    project_id: UUID = Field(..., description="Parent project ID")
    title: str = Field(..., min_length=1, max_length=500, description="Novel title")
    volume_number: int = Field(1, ge=1, description="Volume number")


class NovelUpdateRequest(BaseModel):
    """Novel update request"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    volume_number: Optional[int] = Field(None, ge=1)
    status: Optional[NovelStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


# Response Models
class ProjectResponse(IDModel, NamedModel, MetadataModel, TimestampedModel):
    """Project response model"""
    title: str = Field(..., description="Project title")
    author: Optional[str] = Field(None, description="Author name")
    genre: Optional[str] = Field(None, description="Genre")
    status: ProjectStatus = Field(..., description="Project status")
    novel_count: int = Field(0, description="Number of novels")


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with novels"""
    novels: List['NovelResponse'] = Field(default_factory=list, description="Associated novels")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Project statistics")


class NovelResponse(IDModel, NamedModel, MetadataModel, TimestampedModel):
    """Novel response model"""
    project_id: UUID = Field(..., description="Parent project ID")
    title: str = Field(..., description="Novel title")
    volume_number: int = Field(..., description="Volume number")
    status: NovelStatus = Field(..., description="Novel status")
    chapter_count: int = Field(0, description="Number of chapters")
    word_count: int = Field(0, description="Total word count")


class NovelDetailResponse(NovelResponse):
    """Detailed novel response with statistics"""
    project: ProjectResponse = Field(..., description="Parent project")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Novel statistics")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activity")


class ProjectListResponse(BaseResponse):
    """Project list response"""
    projects: List[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total projects count")


class NovelListResponse(BaseResponse):
    """Novel list response"""
    novels: List[NovelResponse] = Field(..., description="List of novels")
    total: int = Field(..., description="Total novels count")


class ProjectStatsResponse(BaseResponse):
    """Project statistics response"""
    project_id: UUID = Field(..., description="Project ID")
    statistics: Dict[str, Any] = Field(..., description="Project statistics")


class NovelStatsResponse(BaseResponse):
    """Novel statistics response"""
    novel_id: UUID = Field(..., description="Novel ID")
    statistics: Dict[str, Any] = Field(..., description="Novel statistics")


# Batch operation schemas
class ProjectBatchCreateRequest(BaseModel):
    """Batch project creation request"""
    projects: List[ProjectCreateRequest] = Field(..., min_items=1, max_items=100)


class NovelBatchCreateRequest(BaseModel):
    """Batch novel creation request"""
    novels: List[NovelCreateRequest] = Field(..., min_items=1, max_items=100)


# Export/Import schemas
class ProjectExportRequest(BaseModel):
    """Project export request"""
    include_novels: bool = Field(True, description="Include novels in export")
    include_content: bool = Field(False, description="Include content in export")
    include_worldbuilding: bool = Field(False, description="Include worldbuilding data")
    format: str = Field("json", pattern="^(json|yaml|xml)$", description="Export format")


class ProjectImportRequest(BaseModel):
    """Project import request"""
    data: Dict[str, Any] = Field(..., description="Import data")
    merge_existing: bool = Field(False, description="Merge with existing data")
    validate_only: bool = Field(False, description="Only validate without importing")


# Update forward references
ProjectDetailResponse.update_forward_refs()
NovelDetailResponse.update_forward_refs()