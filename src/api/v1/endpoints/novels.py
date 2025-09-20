"""
Novel Management Endpoints
Handles CRUD operations for novels within projects
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body, Path, status

from database.models.core_models import Novel, NovelCreate, NovelUpdate, NovelStatus
from api.v1.schemas.responses import DataResponse, ListResponse, success_response
from api.core.database import get_global_data_manager, get_novel_data_manager
from api.core.exceptions import NotFoundException, ConflictException, handle_database_error
from database.data_access import DatabaseError

router = APIRouter()


@router.get(
    "/",
    response_model=ListResponse[Novel],
    summary="List all novels",
    description="Retrieve a list of all novels across all projects"
)
async def list_novels(
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    status: Optional[NovelStatus] = Query(None, description="Filter by novel status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    manager=Depends(get_global_data_manager)
):
    """Get all novels with optional filtering"""
    try:
        if project_id:
            novels = await manager.get_novels_by_project(project_id)
        else:
            # Get all novels (would need to implement this method)
            novels = await manager.get_all_novels()

        # Apply filtering
        if status:
            novels = [n for n in novels if n.status == status]

        # Apply pagination
        total = len(novels)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_novels = novels[start:end]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(paginated_novels)} novels",
            data=paginated_novels,
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.post(
    "/",
    response_model=DataResponse[Novel],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new novel",
    description="Create a new novel in a project"
)
async def create_novel(
    novel: NovelCreate = Body(..., description="Novel details"),
    manager=Depends(get_global_data_manager)
):
    """Create a new novel"""
    try:
        # Check if project exists
        project = await manager.get_project(novel.project_id)
        if not project:
            raise NotFoundException("Project", str(novel.project_id))

        # Check for duplicate novel name
        existing_novels = await manager.get_novels_by_project(novel.project_id)
        if any(n.name == novel.name for n in existing_novels):
            raise ConflictException(f"Novel with name '{novel.name}' already exists in project")

        # Create the novel
        created_novel = await manager.create_novel(novel)

        return DataResponse(
            success=True,
            message=f"Novel '{created_novel.title}' created successfully",
            data=created_novel
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/{novel_id}",
    response_model=DataResponse[Novel],
    summary="Get novel by ID",
    description="Retrieve detailed information about a specific novel"
)
async def get_novel(
    novel_id: UUID = Path(..., description="Novel UUID"),
    include_stats: bool = Query(False, description="Include statistics"),
    manager=Depends(get_global_data_manager)
):
    """Get a specific novel by ID"""
    try:
        novel = await manager.get_novel(novel_id)
        if not novel:
            raise NotFoundException("Novel", str(novel_id))

        if include_stats:
            novel_manager = get_novel_manager(str(novel_id))
            stats = await novel_manager.get_novel_statistics()
            novel.statistics = stats

        return DataResponse(
            success=True,
            message="Novel retrieved successfully",
            data=novel
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.patch(
    "/{novel_id}",
    response_model=DataResponse[Novel],
    summary="Update novel",
    description="Update novel details"
)
async def update_novel(
    novel_id: UUID = Path(..., description="Novel UUID"),
    update_data: NovelUpdate = Body(..., description="Fields to update"),
    manager=Depends(get_global_data_manager)
):
    """Update a novel"""
    try:
        # Check if novel exists
        novel = await manager.get_novel(novel_id)
        if not novel:
            raise NotFoundException("Novel", str(novel_id))

        # Update the novel
        updated_novel = await manager.update_novel(novel_id, update_data)

        return DataResponse(
            success=True,
            message="Novel updated successfully",
            data=updated_novel
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.delete(
    "/{novel_id}",
    response_model=DataResponse[dict],
    summary="Delete novel",
    description="Delete a novel and all associated content"
)
async def delete_novel(
    novel_id: UUID = Path(..., description="Novel UUID"),
    cascade: bool = Query(False, description="Delete all associated content"),
    manager=Depends(get_global_data_manager)
):
    """Delete a novel"""
    try:
        # Check if novel exists
        novel = await manager.get_novel(novel_id)
        if not novel:
            raise NotFoundException("Novel", str(novel_id))

        # Check for associated content
        novel_manager = get_novel_manager(str(novel_id))
        batches = await novel_manager.get_content_batches()
        if batches and not cascade:
            raise ConflictException(
                f"Novel has {len(batches)} content batches. "
                "Use cascade=true to delete all associated data."
            )

        # Delete the novel
        await manager.delete_novel(novel_id, cascade=cascade)

        return DataResponse(
            success=True,
            message=f"Novel '{novel.title}' deleted successfully",
            data={"novel_id": str(novel_id), "deleted_at": datetime.now().isoformat()}
        )

    except DatabaseError as e:
        raise handle_database_error(e)


@router.get(
    "/{novel_id}/statistics",
    response_model=DataResponse[dict],
    summary="Get novel statistics",
    description="Get comprehensive statistics for a novel"
)
async def get_novel_statistics(
    novel_id: UUID = Path(..., description="Novel UUID")
):
    """Get statistics for a novel"""
    try:
        novel_manager = get_novel_manager(str(novel_id))
        stats = await novel_manager.get_novel_statistics()

        return DataResponse(
            success=True,
            message="Novel statistics retrieved successfully",
            data=stats
        )

    except DatabaseError as e:
        raise handle_database_error(e)