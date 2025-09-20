"""
Projects API Endpoints
Handles project management operations
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from fastapi.responses import JSONResponse

from api.v1.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectStatsResponse,
    ProjectBatchCreateRequest,
    ProjectExportRequest,
    ProjectImportRequest,
    NovelListResponse
)
from api.v1.schemas.base import (
    BaseResponse,
    PaginationParams,
    BulkOperationResponse,
    ErrorResponse
)
from api.core.dependencies import (
    get_global_manager,
    get_current_user,
    require_auth
)
from api.core.exceptions import NotFoundError, ValidationError, ConflictError
from database.data_access import DatabaseError


router = APIRouter()


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    response_description="The created project"
)
async def create_project(
    request: ProjectCreateRequest,
    manager=Depends(get_global_manager),
    current_user=Depends(get_current_user)
):
    """
    Create a new novel project.

    - **name**: Unique project identifier
    - **title**: Display title for the project
    - **description**: Optional project description
    - **author**: Author name
    - **genre**: Genre classification
    - **metadata**: Additional project metadata
    - **tags**: Project tags for categorization
    """
    try:
        # Check if project name already exists
        existing = await manager.get_project_by_name(request.name)
        if existing:
            raise ConflictError(f"Project with name '{request.name}' already exists")

        # Create the project
        project_data = request.dict(exclude_unset=True)
        if current_user:
            project_data["created_by"] = current_user.id

        project = await manager.create_project(project_data)

        return ProjectResponse(
            **project.dict(),
            novel_count=0
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="List all projects",
    response_description="List of projects with pagination"
)
async def list_projects(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    author: Optional[str] = Query(None, description="Filter by author"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    manager=Depends(get_global_manager)
):
    """
    List all projects with optional filtering and pagination.

    Supports filtering by:
    - Status (active, paused, completed, archived)
    - Author name
    - Genre
    - Tags
    """
    try:
        # Build filter conditions
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if author:
            filters["author"] = author
        if genre:
            filters["genre"] = genre
        if tags:
            filters["tags"] = tags

        # Get projects with pagination
        projects = await manager.get_projects(
            filters=filters,
            offset=(pagination.page - 1) * pagination.page_size,
            limit=pagination.page_size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order
        )

        # Get total count
        total = await manager.count_projects(filters=filters)

        # Transform to response models
        project_responses = []
        for project in projects:
            novels = await manager.get_novels_by_project(project.id)
            project_responses.append(
                ProjectResponse(
                    **project.dict(),
                    novel_count=len(novels)
                )
            )

        return ProjectListResponse(
            success=True,
            projects=project_responses,
            total=total
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get project details",
    response_description="Detailed project information"
)
async def get_project(
    project_id: UUID,
    include_novels: bool = Query(True, description="Include novels in response"),
    include_stats: bool = Query(True, description="Include statistics"),
    manager=Depends(get_global_manager)
):
    """
    Get detailed information about a specific project.

    Includes:
    - Project metadata
    - Associated novels (optional)
    - Project statistics (optional)
    """
    try:
        project = await manager.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        response_data = project.dict()

        # Include novels if requested
        if include_novels:
            novels = await manager.get_novels_by_project(project_id)
            response_data["novels"] = [
                NovelResponse(**novel.dict()) for novel in novels
            ]
        else:
            response_data["novels"] = []

        # Include statistics if requested
        if include_stats:
            stats = await manager.get_project_statistics(project_id)
            response_data["statistics"] = stats
        else:
            response_data["statistics"] = {}

        return ProjectDetailResponse(**response_data)

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    response_description="Updated project information"
)
async def update_project(
    project_id: UUID,
    request: ProjectUpdateRequest,
    manager=Depends(get_global_manager),
    current_user=Depends(get_current_user)
):
    """
    Update an existing project's information.

    All fields are optional - only provided fields will be updated.
    """
    try:
        project = await manager.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        # Update only provided fields
        update_data = request.dict(exclude_unset=True)
        if current_user:
            update_data["updated_by"] = current_user.id

        updated_project = await manager.update_project(project_id, update_data)

        # Get novel count
        novels = await manager.get_novels_by_project(project_id)

        return ProjectResponse(
            **updated_project.dict(),
            novel_count=len(novels)
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete(
    "/{project_id}",
    response_model=BaseResponse,
    summary="Delete project",
    response_description="Deletion confirmation"
)
async def delete_project(
    project_id: UUID,
    force: bool = Query(False, description="Force delete even with content"),
    manager=Depends(get_global_manager),
    _=Depends(require_auth)
):
    """
    Delete a project and all associated data.

    **Warning**: This operation is irreversible and will delete:
    - All novels in the project
    - All content and worldbuilding data
    - All associated files and metadata

    Use `force=true` to delete projects with existing content.
    """
    try:
        project = await manager.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        # Check for existing content
        novels = await manager.get_novels_by_project(project_id)
        if novels and not force:
            raise ConflictError(
                f"Project has {len(novels)} novels. Use force=true to delete anyway."
            )

        # Delete the project
        await manager.delete_project(project_id)

        return BaseResponse(
            success=True,
            message=f"Project '{project.title}' deleted successfully"
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get(
    "/{project_id}/novels",
    response_model=NovelListResponse,
    summary="Get project novels",
    response_description="List of novels in the project"
)
async def get_project_novels(
    project_id: UUID,
    pagination: PaginationParams = Depends(),
    manager=Depends(get_global_manager)
):
    """
    Get all novels associated with a project.
    """
    try:
        project = await manager.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        novels = await manager.get_novels_by_project(
            project_id,
            offset=(pagination.page - 1) * pagination.page_size,
            limit=pagination.page_size
        )

        novel_responses = []
        for novel in novels:
            # Get chapter and word count
            stats = await manager.get_novel_statistics(novel.id)
            novel_responses.append(
                NovelResponse(
                    **novel.dict(),
                    chapter_count=stats.get("chapter_count", 0),
                    word_count=stats.get("word_count", 0)
                )
            )

        return NovelListResponse(
            success=True,
            novels=novel_responses,
            total=len(novels)
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get(
    "/{project_id}/statistics",
    response_model=ProjectStatsResponse,
    summary="Get project statistics",
    response_description="Project statistics and analytics"
)
async def get_project_statistics(
    project_id: UUID,
    manager=Depends(get_global_manager)
):
    """
    Get comprehensive statistics for a project.

    Includes:
    - Novel count and status distribution
    - Total word count
    - Chapter count
    - Character count
    - Worldbuilding elements count
    - Activity timeline
    """
    try:
        project = await manager.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        stats = await manager.get_project_statistics(project_id)

        return ProjectStatsResponse(
            success=True,
            project_id=project_id,
            statistics=stats
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post(
    "/batch",
    response_model=BulkOperationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple projects",
    response_description="Batch creation results"
)
async def create_projects_batch(
    request: ProjectBatchCreateRequest,
    manager=Depends(get_global_manager),
    _=Depends(require_auth)
):
    """
    Create multiple projects in a single operation.

    Useful for:
    - Importing projects from external sources
    - Setting up project templates
    - Bulk initialization
    """
    succeeded = 0
    failed = 0
    errors = []

    for project_data in request.projects:
        try:
            await manager.create_project(project_data.dict())
            succeeded += 1
        except Exception as e:
            failed += 1
            errors.append({
                "project": project_data.name,
                "error": str(e)
            })

    return BulkOperationResponse(
        success=succeeded > 0,
        message=f"Created {succeeded} projects, {failed} failed",
        processed=len(request.projects),
        succeeded=succeeded,
        failed=failed,
        errors=errors if errors else None
    )


@router.post(
    "/{project_id}/export",
    response_model=BaseResponse,
    summary="Export project data",
    response_description="Export operation result"
)
async def export_project(
    project_id: UUID,
    request: ProjectExportRequest,
    manager=Depends(get_global_manager)
):
    """
    Export project data in various formats.

    Options:
    - Include novels and their content
    - Include worldbuilding data
    - Export formats: JSON, YAML, XML
    """
    try:
        project = await manager.get_project(project_id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")

        # Perform export
        export_data = await manager.export_project(
            project_id,
            include_novels=request.include_novels,
            include_content=request.include_content,
            include_worldbuilding=request.include_worldbuilding,
            format=request.format
        )

        return JSONResponse(
            content={
                "success": True,
                "message": f"Project exported successfully",
                "data": export_data
            }
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post(
    "/import",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import project data",
    response_description="Import operation result"
)
async def import_project(
    request: ProjectImportRequest,
    manager=Depends(get_global_manager),
    _=Depends(require_auth)
):
    """
    Import project data from external source.

    Options:
    - Validate only: Check data without importing
    - Merge existing: Merge with existing projects
    """
    try:
        if request.validate_only:
            # Only validate the data
            validation_result = await manager.validate_import_data(request.data)
            return BaseResponse(
                success=validation_result["valid"],
                message="Validation " + ("successful" if validation_result["valid"] else "failed"),
                details=validation_result
            )

        # Perform import
        import_result = await manager.import_project(
            request.data,
            merge_existing=request.merge_existing
        )

        return BaseResponse(
            success=True,
            message=f"Project imported successfully",
            details=import_result
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Import validation error: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )