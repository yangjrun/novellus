"""
Base Pydantic Schemas
Common schemas and base classes for API models
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Generic, TypeVar
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Generic type for pagination
T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(True, description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    }


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = Field(False, description="Operation failed")
    error: str = Field(..., description="Error type")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    error_id: Optional[str] = Field(None, description="Error tracking ID")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response model"""
    data: List[T] = Field(..., description="Page data")
    pagination: Dict[str, Any] = Field(..., description="Pagination metadata")
    total: int = Field(..., description="Total items count")
    pages: int = Field(..., description="Total pages count")

    @field_validator('pagination', mode='before')
    @classmethod
    def build_pagination(cls, v, info):
        """Build pagination metadata"""
        if not isinstance(v, dict):
            return {
                "page": 1,
                "page_size": len(info.data.get('data', [])) if info.data else 0,
                "has_next": False,
                "has_prev": False
            }
        return v


class SearchParams(BaseModel):
    """Search parameters"""
    query: str = Field(..., min_length=1, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    limit: int = Field(50, ge=1, le=200, description="Result limit")
    offset: int = Field(0, ge=0, description="Result offset")


class BulkOperationResponse(BaseResponse):
    """Bulk operation response"""
    processed: int = Field(..., description="Number of items processed")
    succeeded: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Error details for failed items")


class StatusEnum(str, Enum):
    """Common status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class PriorityEnum(int, Enum):
    """Priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    TRIVIAL = 5


class OperationTypeEnum(str, Enum):
    """Operation types for audit logging"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    IMPORT = "import"
    EXPORT = "export"


class TimestampedModel(BaseModel):
    """Model with timestamp fields"""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    }


class IDModel(BaseModel):
    """Model with ID field"""
    id: UUID = Field(..., description="Unique identifier")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class NamedModel(BaseModel):
    """Model with name and description"""
    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, max_length=2000, description="Description")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name is not empty"""
        if not v or v.isspace():
            raise ValueError('Name cannot be empty')
        return v.strip()


class MetadataModel(BaseModel):
    """Model with metadata field"""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags"""
        if v:
            return [tag.strip().lower() for tag in v if tag and not tag.isspace()]
        return []


class AuditedModel(TimestampedModel):
    """Model with audit fields"""
    created_by: Optional[str] = Field(None, description="Creator ID")
    updated_by: Optional[str] = Field(None, description="Last updater ID")
    version: int = Field(1, ge=1, description="Version number")


class SoftDeleteModel(BaseModel):
    """Model with soft delete support"""
    is_deleted: bool = Field(False, description="Soft delete flag")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp")
    deleted_by: Optional[str] = Field(None, description="Deleter ID")