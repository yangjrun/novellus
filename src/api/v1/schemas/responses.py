"""
Common Response Schemas for API v1
Standardized response models for consistent API responses
"""

from typing import Generic, TypeVar, Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

# Generic type for data payload
T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message about the operation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class DataResponse(BaseResponse, GenericModel, Generic[T]):
    """Generic response model with data payload"""
    data: T = Field(..., description="Response data payload")


class ListResponse(BaseResponse, GenericModel, Generic[T]):
    """Response model for list/collection endpoints"""
    data: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of items per page")
    has_next: Optional[bool] = Field(None, description="Whether there are more pages")


class ErrorDetail(BaseModel):
    """Error detail information"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Main error message")
    error_type: str = Field(..., description="Type of error")
    error_id: Optional[str] = Field(None, description="Unique error identifier for tracking")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StatusResponse(BaseResponse):
    """Response for status/health check endpoints"""
    status: str = Field(..., description="Service status")
    services: Dict[str, str] = Field(default_factory=dict, description="Status of dependent services")
    version: Optional[str] = Field(None, description="API version")


class BatchOperationResult(BaseModel):
    """Result of a batch operation on a single item"""
    id: str = Field(..., description="Item identifier")
    success: bool = Field(..., description="Whether the operation succeeded for this item")
    message: Optional[str] = Field(None, description="Operation message")
    error: Optional[str] = Field(None, description="Error message if failed")


class BatchResponse(BaseResponse):
    """Response for batch operations"""
    results: List[BatchOperationResult] = Field(..., description="Results for each item")
    total_success: int = Field(..., description="Number of successful operations")
    total_failed: int = Field(..., description="Number of failed operations")


class PaginationParams(BaseModel):
    """Pagination request parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order")


class SearchParams(BaseModel):
    """Search request parameters"""
    query: str = Field(..., min_length=1, description="Search query")
    search_fields: Optional[List[str]] = Field(None, description="Fields to search in")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    pagination: Optional[PaginationParams] = Field(None, description="Pagination parameters")


class StatisticsResponse(BaseResponse):
    """Response for statistics endpoints"""
    statistics: Dict[str, Any] = Field(..., description="Statistical data")
    period: Optional[str] = Field(None, description="Time period for statistics")
    generated_at: datetime = Field(default_factory=datetime.now, description="When statistics were generated")


class ImportResponse(BaseResponse):
    """Response for data import operations"""
    imported_count: int = Field(..., description="Number of items imported")
    skipped_count: int = Field(0, description="Number of items skipped")
    error_count: int = Field(0, description="Number of errors")
    warnings: Optional[List[str]] = Field(None, description="Warning messages")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional import details")


class ExportResponse(BaseResponse):
    """Response for data export operations"""
    export_format: str = Field(..., description="Format of exported data")
    file_url: Optional[str] = Field(None, description="URL to download exported file")
    data: Optional[Any] = Field(None, description="Inline exported data (for small exports)")
    record_count: int = Field(..., description="Number of records exported")


class TaskResponse(BaseResponse):
    """Response for async task operations"""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Task progress percentage")
    result: Optional[Any] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="When task started")
    completed_at: Optional[datetime] = Field(None, description="When task completed")


class ValidationResponse(BaseResponse):
    """Response for validation operations"""
    is_valid: bool = Field(..., description="Whether the data is valid")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Validation errors")
    warnings: Optional[List[str]] = Field(None, description="Validation warnings")


# Commonly used response instances
def success_response(message: str = "Operation successful", **kwargs) -> BaseResponse:
    """Create a success response"""
    return BaseResponse(success=True, message=message, **kwargs)


def error_response(message: str, error_type: str = "Error", **kwargs) -> ErrorResponse:
    """Create an error response"""
    return ErrorResponse(
        success=False,
        message=message,
        error_type=error_type,
        **kwargs
    )


def data_response(data: Any, message: str = "Data retrieved successfully", **kwargs) -> DataResponse:
    """Create a data response"""
    return DataResponse(
        success=True,
        message=message,
        data=data,
        **kwargs
    )


def list_response(
    data: List[Any],
    total: int,
    message: str = "Data retrieved successfully",
    **kwargs
) -> ListResponse:
    """Create a list response"""
    return ListResponse(
        success=True,
        message=message,
        data=data,
        total=total,
        **kwargs
    )