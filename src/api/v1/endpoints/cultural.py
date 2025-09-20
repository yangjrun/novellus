"""
Cultural Framework Endpoints
Handles cultural frameworks, entities, and relations
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body, Path, status, UploadFile, File

from database.models.cultural_framework_models import (
    CulturalFramework, CulturalFrameworkCreate,
    CulturalEntity, CulturalEntityCreate,
    CulturalRelation, CulturalRelationCreate,
    DomainType, CulturalDimension, EntityType, RelationType
)
from api.v1.schemas.responses import DataResponse, ListResponse, ImportResponse
from api.core.database import get_cultural_repo
from api.core.exceptions import NotFoundException, ValidationException, handle_database_error
import json

router = APIRouter()


@router.post(
    "/frameworks",
    response_model=DataResponse[str],
    status_code=status.HTTP_201_CREATED,
    summary="Create cultural framework",
    description="Create a new cultural framework"
)
async def create_cultural_framework(
    framework: CulturalFrameworkCreate = Body(..., description="Framework details"),
    repo=Depends(get_cultural_repo)
):
    """Create a new cultural framework"""
    try:
        framework_id = await repo.create_cultural_framework(framework)

        return DataResponse(
            success=True,
            message=f"Cultural framework '{framework.title}' created successfully",
            data=str(framework_id)
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/frameworks",
    response_model=ListResponse[CulturalFramework],
    summary="List cultural frameworks",
    description="List all cultural frameworks for a novel"
)
async def list_cultural_frameworks(
    novel_id: UUID = Query(..., description="Novel UUID"),
    domain_type: Optional[DomainType] = Query(None, description="Filter by domain type"),
    dimension: Optional[CulturalDimension] = Query(None, description="Filter by dimension"),
    min_priority: Optional[int] = Query(None, ge=1, le=10, description="Minimum priority"),
    repo=Depends(get_cultural_repo)
):
    """List cultural frameworks"""
    try:
        frameworks = await repo.get_frameworks_by_novel(
            novel_id=novel_id,
            domain_type=domain_type,
            dimension=dimension
        )

        # Apply additional filters
        if min_priority:
            frameworks = [f for f in frameworks if f.priority >= min_priority]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(frameworks)} cultural frameworks",
            data=frameworks,
            total=len(frameworks)
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/entities",
    response_model=DataResponse[str],
    status_code=status.HTTP_201_CREATED,
    summary="Create cultural entity",
    description="Create a new cultural entity"
)
async def create_cultural_entity(
    entity: CulturalEntityCreate = Body(..., description="Entity details"),
    repo=Depends(get_cultural_repo)
):
    """Create a new cultural entity"""
    try:
        entity_id = await repo.create_cultural_entity(entity)

        return DataResponse(
            success=True,
            message=f"Cultural entity '{entity.name}' created successfully",
            data=str(entity_id)
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/entities",
    response_model=ListResponse[CulturalEntity],
    summary="List cultural entities",
    description="List cultural entities with filtering"
)
async def list_cultural_entities(
    novel_id: UUID = Query(..., description="Novel UUID"),
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    domain_type: Optional[DomainType] = Query(None, description="Filter by domain type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    repo=Depends(get_cultural_repo)
):
    """List cultural entities"""
    try:
        entities = await repo.get_entities_by_type(
            novel_id=novel_id,
            entity_type=entity_type,
            domain_type=domain_type
        )

        # Apply pagination
        total = len(entities)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_entities = entities[start:end]

        return ListResponse(
            success=True,
            message=f"Retrieved {len(paginated_entities)} cultural entities",
            data=paginated_entities,
            total=total,
            page=page,
            page_size=page_size,
            has_next=end < total
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/entities/search",
    response_model=DataResponse[dict],
    summary="Search cultural entities",
    description="Full-text search for cultural entities"
)
async def search_cultural_entities(
    novel_id: UUID = Query(..., description="Novel UUID"),
    query: str = Query(..., min_length=1, description="Search query"),
    entity_types: Optional[List[EntityType]] = Query(None, description="Filter by entity types"),
    domains: Optional[List[DomainType]] = Query(None, description="Filter by domains"),
    repo=Depends(get_cultural_repo)
):
    """Search cultural entities"""
    try:
        results = await repo.search_entities(
            novel_id=novel_id,
            search_query=query,
            entity_types=entity_types,
            domains=domains
        )

        return DataResponse(
            success=True,
            message=f"Found {len(results)} matching entities",
            data={"results": results, "count": len(results)}
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/relations",
    response_model=DataResponse[str],
    status_code=status.HTTP_201_CREATED,
    summary="Create cultural relation",
    description="Create a relation between cultural entities"
)
async def create_cultural_relation(
    relation: CulturalRelationCreate = Body(..., description="Relation details"),
    repo=Depends(get_cultural_repo)
):
    """Create a cultural relation"""
    try:
        relation_id = await repo.create_cultural_relation(relation)

        return DataResponse(
            success=True,
            message="Cultural relation created successfully",
            data=str(relation_id)
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/relations/cross-domain",
    response_model=DataResponse[List[dict]],
    summary="Get cross-domain relations",
    description="Get relations that cross domain boundaries"
)
async def get_cross_domain_relations(
    novel_id: UUID = Query(..., description="Novel UUID"),
    repo=Depends(get_cultural_repo)
):
    """Get cross-domain relations"""
    try:
        relations = await repo.get_cross_domain_relations(novel_id)

        return DataResponse(
            success=True,
            message=f"Found {len(relations)} cross-domain relations",
            data=relations
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/import",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import cultural analysis",
    description="Import cultural framework analysis from file"
)
async def import_cultural_analysis(
    novel_id: UUID = Body(..., description="Novel UUID"),
    file: UploadFile = File(..., description="Analysis file (JSON)"),
    task_name: str = Body("Cultural Framework Import", description="Import task name")
):
    """Import cultural framework analysis"""
    try:
        from database.cultural_batch_manager import CulturalDataBatchManager

        # Read and parse file
        content = await file.read()
        analysis_data = json.loads(content)

        # Get repository
        repo = await get_cultural_repo()
        batch_manager = CulturalDataBatchManager(repo)

        # Import data
        task_id = await batch_manager.import_cultural_framework_analysis(
            novel_id=novel_id,
            analysis_data=analysis_data,
            task_name=task_name
        )

        # Get statistics
        stats = batch_manager.get_processing_statistics()

        return ImportResponse(
            success=True,
            message="Cultural framework analysis import started",
            imported_count=stats.get("frameworks_imported", 0),
            details={
                "task_id": task_id,
                "statistics": stats
            }
        )

    except json.JSONDecodeError:
        raise ValidationException("Invalid JSON file")
    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/statistics",
    response_model=DataResponse[dict],
    summary="Get cultural statistics",
    description="Get cultural framework statistics for a novel"
)
async def get_cultural_statistics(
    novel_id: UUID = Query(..., description="Novel UUID"),
    repo=Depends(get_cultural_repo)
):
    """Get cultural framework statistics"""
    try:
        stats = await repo.get_novel_statistics(novel_id)

        return DataResponse(
            success=True,
            message="Cultural statistics retrieved successfully",
            data=stats
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/entity-network",
    response_model=DataResponse[dict],
    summary="Get entity network",
    description="Get the network of entity relationships"
)
async def get_entity_network(
    novel_id: UUID = Query(..., description="Novel UUID"),
    entity_types: Optional[List[EntityType]] = Query(None, description="Filter by entity types"),
    min_strength: float = Query(0.5, ge=0, le=1, description="Minimum relation strength"),
    repo=Depends(get_cultural_repo)
):
    """Get entity relationship network"""
    try:
        # Get entities and relations
        entities = await repo.get_entities_by_novel(novel_id)
        relations = await repo.get_relations_by_novel(novel_id)

        # Filter by entity types if specified
        if entity_types:
            entity_ids = {e.id for e in entities if e.entity_type in entity_types}
            entities = [e for e in entities if e.entity_type in entity_types]
            relations = [r for r in relations
                        if r.source_entity_id in entity_ids and r.target_entity_id in entity_ids]

        # Filter by relation strength
        relations = [r for r in relations if r.strength >= min_strength]

        # Build network structure
        network = {
            "nodes": [
                {
                    "id": str(e.id),
                    "name": e.name,
                    "type": e.entity_type.value,
                    "domain": e.domain_type.value if e.domain_type else None
                }
                for e in entities
            ],
            "edges": [
                {
                    "source": str(r.source_entity_id),
                    "target": str(r.target_entity_id),
                    "type": r.relation_type.value,
                    "strength": r.strength
                }
                for r in relations
            ],
            "statistics": {
                "node_count": len(entities),
                "edge_count": len(relations),
                "domains": list(set(e.domain_type.value for e in entities if e.domain_type))
            }
        }

        return DataResponse(
            success=True,
            message="Entity network retrieved successfully",
            data=network
        )

    except Exception as e:
        raise handle_database_error(e)