"""
Content Management Endpoints
Handles content batches and segments
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body, Path, status

from database.models.core_models import (
    ContentBatch, ContentBatchCreate, ContentSegment, ContentSegmentCreate,
    BatchType, BatchStatus, SegmentType
)
from api.v1.schemas.responses import DataResponse, ListResponse, success_response
from api.core.database import get_novel_data_manager, get_batch_data_manager
from api.core.exceptions import NotFoundException, ValidationException, handle_database_error
from database.data_access import DatabaseError

router = APIRouter()


@router.post(
    "/batches",
    response_model=DataResponse[ContentBatch],
    status_code=status.HTTP_201_CREATED,
    summary="Create content batch",
    description="Create a new content batch for a novel"
)
async def create_content_batch(
    batch: ContentBatchCreate = Body(..., description="Batch details")
):
    """Create a new content batch"""
    try:
        novel_manager = get_novel_data_manager(str(batch.novel_id))

        # Get existing batches to determine next batch number
        existing_batches = await novel_manager.get_content_batches()
        next_batch_number = max([b.batch_number for b in existing_batches], default=0) + 1
        batch.batch_number = next_batch_number

        # Create the batch
        created_batch = await novel_manager.create_content_batch(batch)

        return DataResponse(
            success=True,
            message=f"Content batch '{created_batch.batch_name}' created successfully",
            data=created_batch
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/batches/{batch_id}",
    response_model=DataResponse[ContentBatch],
    summary="Get batch by ID",
    description="Retrieve a specific content batch"
)
async def get_content_batch(
    batch_id: UUID = Path(..., description="Batch UUID"),
    include_segments: bool = Query(False, description="Include segments")
):
    """Get a specific content batch"""
    try:
        # This would need implementation in the manager
        batch = await get_batch_details(batch_id)
        if not batch:
            raise NotFoundException("Content batch", str(batch_id))

        if include_segments:
            segments = await get_batch_segments(batch_id)
            batch.segments = segments

        return DataResponse(
            success=True,
            message="Content batch retrieved successfully",
            data=batch
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/batches",
    response_model=ListResponse[ContentBatch],
    summary="List content batches",
    description="List all content batches for a novel"
)
async def list_content_batches(
    novel_id: UUID = Query(..., description="Novel UUID"),
    batch_type: Optional[BatchType] = Query(None, description="Filter by batch type"),
    status: Optional[BatchStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """List content batches for a novel"""
    try:
        novel_manager = get_novel_data_manager(str(novel_id))
        batches = await novel_manager.get_content_batches()

        # Apply filters
        if batch_type:
            batches = [b for b in batches if b.batch_type == batch_type]
        if status:
            batches = [b for b in batches if b.status == status]

        # Apply pagination
        total = len(batches)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_batches = batches[start:end]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(paginated_batches)} batches",
            data=paginated_batches,
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.post(
    "/batches/series",
    response_model=DataResponse[List[ContentBatch]],
    status_code=status.HTTP_201_CREATED,
    summary="Create batch series",
    description="Create a series of related content batches"
)
async def create_batch_series(
    novel_id: UUID = Body(..., description="Novel UUID"),
    series_name: str = Body(..., description="Series name"),
    batch_type: BatchType = Body(..., description="Batch type"),
    batch_count: int = Body(..., ge=1, le=50, description="Number of batches"),
    description: Optional[str] = Body(None, description="Series description"),
    interval_days: int = Body(7, ge=1, description="Days between batches")
):
    """Create a series of content batches"""
    try:
        batch_manager = await get_batch_data_manager(str(novel_id))

        batches = await batch_manager.create_batch_series(
            series_name=series_name,
            batch_type=batch_type,
            batch_count=batch_count,
            description=description,
            interval_days=interval_days
        )

        return DataResponse(
            success=True,
            message=f"Batch series '{series_name}' with {batch_count} batches created successfully",
            data=batches
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/batches/{novel_id}/dashboard",
    response_model=DataResponse[dict],
    summary="Get batch dashboard",
    description="Get batch management dashboard for a novel"
)
async def get_batch_dashboard(
    novel_id: UUID = Path(..., description="Novel UUID")
):
    """Get batch management dashboard"""
    try:
        batch_manager = await get_batch_data_manager(str(novel_id))
        dashboard_data = await batch_manager.get_batch_dashboard()

        return DataResponse(
            success=True,
            message="Batch dashboard retrieved successfully",
            data=dashboard_data
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.post(
    "/segments",
    response_model=DataResponse[ContentSegment],
    status_code=status.HTTP_201_CREATED,
    summary="Create content segment",
    description="Create a new content segment in a batch"
)
async def create_content_segment(
    segment: ContentSegmentCreate = Body(..., description="Segment details")
):
    """Create a new content segment"""
    try:
        # Get the novel_id from batch (simplified - needs proper implementation)
        novel_manager = get_novel_data_manager("dummy")  # This needs the actual novel_id

        # Get existing segments to determine sequence
        existing_segments = await novel_manager.get_content_segments(str(segment.batch_id))
        segment.sequence_order = len(existing_segments) + 1

        # Create the segment
        created_segment = await novel_manager.create_content_segment(segment)

        return DataResponse(
            success=True,
            message=f"Content segment '{created_segment.title}' created successfully",
            data=created_segment
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/segments",
    response_model=ListResponse[ContentSegment],
    summary="List content segments",
    description="List content segments in a batch"
)
async def list_content_segments(
    batch_id: UUID = Query(..., description="Batch UUID"),
    segment_type: Optional[SegmentType] = Query(None, description="Filter by segment type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """List content segments in a batch"""
    try:
        # This needs proper implementation
        segments = await get_batch_segments(batch_id)

        # Apply filters
        if segment_type:
            segments = [s for s in segments if s.segment_type == segment_type]

        # Apply pagination
        total = len(segments)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_segments = segments[start:end]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(paginated_segments)} segments",
            data=paginated_segments,
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.patch(
    "/segments/{segment_id}",
    response_model=DataResponse[ContentSegment],
    summary="Update content segment",
    description="Update a content segment"
)
async def update_content_segment(
    segment_id: UUID = Path(..., description="Segment UUID"),
    update_data: dict = Body(..., description="Fields to update")
):
    """Update a content segment"""
    try:
        # This needs proper implementation
        segment = await update_segment(segment_id, update_data)
        if not segment:
            raise NotFoundException("Content segment", str(segment_id))

        return DataResponse(
            success=True,
            message="Content segment updated successfully",
            data=segment
        )

    except DatabaseError as e:
        raise handle_database_error(e)


# Helper functions (these would be implemented properly)
async def get_batch_details(batch_id: UUID):
    """Get batch details - placeholder"""
    pass

async def get_batch_segments(batch_id: UUID):
    """Get segments in a batch - placeholder"""
    pass

async def update_segment(segment_id: UUID, update_data: dict):
    """Update segment - placeholder"""
    pass