"""
Conflict Analysis Endpoints
Handles conflict matrices, entities, story hooks, and network analysis
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body, Path, status

from api.v1.schemas.responses import DataResponse, ListResponse, ImportResponse, StatisticsResponse
from api.core.database import get_novel_data_manager
from api.core.exceptions import NotFoundException, handle_database_error
from database.conflict_data_importer import ConflictDataImporter, ImportConfig
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/import",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import conflict analysis data",
    description="Import cross-domain conflict analysis data"
)
async def import_conflict_data(
    project_id: UUID = Body("29c170c5-4a3e-4829-a242-74c1acb96453", description="Project UUID"),
    novel_id: UUID = Body("e1fd1aa4-bde2-4c76-8cee-334e54fa47d1", description="Novel UUID"),
    clear_existing: bool = Body(False, description="Clear existing conflict data"),
    validate_integrity: bool = Body(True, description="Validate data integrity")
):
    """Import conflict analysis data"""
    try:
        config = ImportConfig(
            project_id=str(project_id),
            novel_id=str(novel_id),
            clear_existing_data=clear_existing,
            validate_data_integrity=validate_integrity
        )

        importer = ConflictDataImporter(config)
        result = await importer.run_import()

        return ImportResponse(
            success=result.get("success", False),
            message=result.get("message", "Import completed"),
            imported_count=result.get("imported", {}).get("total", 0),
            error_count=len(result.get("errors", [])),
            details=result
        )

    except Exception as e:
        logger.error(f"Conflict data import failed: {e}")
        raise handle_database_error(e)


@router.get(
    "/matrix",
    response_model=ListResponse[dict],
    summary="Query conflict matrix",
    description="Query cross-domain conflict matrix data"
)
async def query_conflict_matrix(
    novel_id: UUID = Query("e1fd1aa4-bde2-4c76-8cee-334e54fa47d1", description="Novel UUID"),
    domain_a: Optional[str] = Query(None, description="Domain A name"),
    domain_b: Optional[str] = Query(None, description="Domain B name"),
    min_intensity: float = Query(0.0, ge=0, le=5, description="Minimum conflict intensity"),
    max_intensity: float = Query(5.0, ge=0, le=5, description="Maximum conflict intensity"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Query conflict matrix data"""
    try:
        manager = get_novel_data_manager(str(novel_id))

        # Build query conditions
        conditions = ["novel_id = $1", "intensity BETWEEN $2 AND $3"]
        params = [str(novel_id), min_intensity, max_intensity]

        if domain_a:
            conditions.append("(domain_a = $4 OR domain_b = $4)")
            params.append(domain_a)

        if domain_b and domain_a != domain_b:
            param_idx = len(params) + 1
            conditions.append(f"(domain_a = ${param_idx} OR domain_b = ${param_idx})")
            params.append(domain_b)

        # Add pagination
        offset = (page - 1) * page_size
        query = f"""
            SELECT id, matrix_name, domain_a, domain_b, intensity, conflict_type,
                   risk_level, status, priority, core_resources, trigger_laws,
                   typical_scenarios, key_roles, created_at, updated_at
            FROM cross_domain_conflict_matrix
            WHERE {' AND '.join(conditions)}
            ORDER BY intensity DESC, priority DESC
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """
        params.extend([page_size, offset])

        results = await manager.fetch_query(query, *params)

        # Convert to dict format
        conflicts = []
        for row in results:
            conflict = dict(row)
            conflict['id'] = str(conflict['id'])
            conflict['created_at'] = conflict['created_at'].isoformat()
            conflict['updated_at'] = conflict['updated_at'].isoformat()
            conflicts.append(conflict)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count
            FROM cross_domain_conflict_matrix
            WHERE {' AND '.join(conditions[:len(conditions)])}
        """
        count_result = await manager.fetch_query(count_query, *params[:-2])
        total = count_result[0]['count'] if count_result else 0

        return ListResponse(
            success=True,
            message=f"Retrieved {len(conflicts)} conflict matrices",
            data=conflicts,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total
        )

    except Exception as e:
        logger.error(f"Conflict matrix query failed: {e}")
        raise handle_database_error(e)


@router.get(
    "/entities",
    response_model=ListResponse[dict],
    summary="Query conflict entities",
    description="Query conflict entities data"
)
async def query_conflict_entities(
    novel_id: UUID = Query("e1fd1aa4-bde2-4c76-8cee-334e54fa47d1", description="Novel UUID"),
    entity_type: Optional[str] = Query(None, description="Entity type"),
    domain: Optional[str] = Query(None, description="Related domain"),
    min_strategic_value: float = Query(0.0, ge=0, description="Minimum strategic value"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page")
):
    """Query conflict entities"""
    try:
        manager = get_novel_data_manager(str(novel_id))

        # Build query
        conditions = ["novel_id = $1", "strategic_value >= $2"]
        params = [str(novel_id), min_strategic_value]

        if entity_type:
            conditions.append("entity_type = $3")
            params.append(entity_type)

        if domain:
            param_idx = len(params) + 1
            conditions.append(f"(primary_domain = ${param_idx} OR ${param_idx} = ANY(involved_domains))")
            params.append(domain)

        offset = (page - 1) * page_size
        query = f"""
            SELECT id, name, entity_type, entity_subtype, primary_domain,
                   involved_domains, description, strategic_value, economic_value,
                   symbolic_value, scarcity_level, conflict_roles, dispute_intensity,
                   confidence_score, validation_status, tags, created_at
            FROM conflict_entities
            WHERE {' AND '.join(conditions)}
            ORDER BY strategic_value DESC, dispute_intensity DESC
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """
        params.extend([page_size, offset])

        results = await manager.fetch_query(query, *params)

        # Convert results
        entities = []
        for row in results:
            entity = dict(row)
            entity['id'] = str(entity['id'])
            entity['created_at'] = entity['created_at'].isoformat()
            entities.append(entity)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count
            FROM conflict_entities
            WHERE {' AND '.join(conditions)}
        """
        count_result = await manager.fetch_query(count_query, *params[:-2])
        total = count_result[0]['count'] if count_result else 0

        return ListResponse(
            success=True,
            message=f"Retrieved {len(entities)} conflict entities",
            data=entities,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total
        )

    except Exception as e:
        logger.error(f"Conflict entities query failed: {e}")
        raise handle_database_error(e)


@router.get(
    "/story-hooks",
    response_model=ListResponse[dict],
    summary="Query story hooks",
    description="Query conflict story hooks"
)
async def query_story_hooks(
    novel_id: UUID = Query("e1fd1aa4-bde2-4c76-8cee-334e54fa47d1", description="Novel UUID"),
    hook_type: Optional[str] = Query(None, description="Hook type"),
    min_score: float = Query(5.0, ge=0, le=10, description="Minimum overall score"),
    is_ai_generated: Optional[bool] = Query(None, description="Filter by AI-generated status"),
    domains: Optional[List[str]] = Query(None, description="Filter by involved domains"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page")
):
    """Query story hooks"""
    try:
        manager = get_novel_data_manager(str(novel_id))

        # Build query
        conditions = ["novel_id = $1", "overall_score >= $2"]
        params = [str(novel_id), min_score]

        if hook_type:
            conditions.append("hook_type = $3")
            params.append(hook_type)

        if is_ai_generated is not None:
            param_idx = len(params) + 1
            conditions.append(f"is_ai_generated = ${param_idx}")
            params.append(is_ai_generated)

        if domains:
            param_idx = len(params) + 1
            conditions.append(f"domains_involved && ${param_idx}")
            params.append(domains)

        offset = (page - 1) * page_size
        query = f"""
            SELECT id, title, description, hook_type, hook_subtype,
                   domains_involved, main_characters, moral_themes,
                   inciting_incident, originality, complexity, emotional_impact,
                   plot_integration, overall_score, priority_level,
                   is_ai_generated, generation_method, human_validation_status,
                   usage_count, tags, created_at
            FROM conflict_story_hooks
            WHERE {' AND '.join(conditions)}
            ORDER BY overall_score DESC, priority_level DESC
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """
        params.extend([page_size, offset])

        results = await manager.fetch_query(query, *params)

        # Convert results
        hooks = []
        for row in results:
            hook = dict(row)
            hook['id'] = str(hook['id'])
            hook['created_at'] = hook['created_at'].isoformat()
            hooks.append(hook)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count
            FROM conflict_story_hooks
            WHERE {' AND '.join(conditions)}
        """
        count_result = await manager.fetch_query(count_query, *params[:-2])
        total = count_result[0]['count'] if count_result else 0

        return ListResponse(
            success=True,
            message=f"Retrieved {len(hooks)} story hooks",
            data=hooks,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total
        )

    except Exception as e:
        logger.error(f"Story hooks query failed: {e}")
        raise handle_database_error(e)


@router.get(
    "/network-analysis",
    response_model=ListResponse[dict],
    summary="Query network analysis",
    description="Query conflict network analysis results"
)
async def query_network_analysis(
    novel_id: UUID = Query("e1fd1aa4-bde2-4c76-8cee-334e54fa47d1", description="Novel UUID"),
    analysis_type: Optional[str] = Query(None, description="Analysis type"),
    min_confidence: float = Query(0.5, ge=0, le=1, description="Minimum confidence score")
):
    """Query network analysis results"""
    try:
        manager = get_novel_data_manager(str(novel_id))

        conditions = ["novel_id = $1", "analysis_confidence >= $2"]
        params = [str(novel_id), min_confidence]

        if analysis_type:
            conditions.append("analysis_type = $3")
            params.append(analysis_type)

        query = f"""
            SELECT id, analysis_type, network_type, node_count, edge_count,
                   network_density, average_clustering_coefficient,
                   average_path_length, diameter, modularity,
                   community_count, analysis_confidence, results,
                   analysis_date, created_at
            FROM network_analysis_results
            WHERE {' AND '.join(conditions)}
            ORDER BY analysis_date DESC, analysis_confidence DESC
        """

        results = await manager.fetch_query(query, *params)

        # Convert results
        analyses = []
        for row in results:
            analysis = dict(row)
            analysis['id'] = str(analysis['id'])
            analysis['analysis_date'] = analysis['analysis_date'].isoformat()
            analysis['created_at'] = analysis['created_at'].isoformat()
            if analysis['results']:
                analysis['results'] = json.loads(analysis['results'])
            analyses.append(analysis)

        return ListResponse(
            success=True,
            message=f"Retrieved {len(analyses)} network analyses",
            data=analyses,
            total=len(analyses)
        )

    except Exception as e:
        logger.error(f"Network analysis query failed: {e}")
        raise handle_database_error(e)


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Get conflict statistics",
    description="Get comprehensive conflict analysis statistics"
)
async def get_conflict_statistics(
    novel_id: UUID = Query("e1fd1aa4-bde2-4c76-8cee-334e54fa47d1", description="Novel UUID")
):
    """Get conflict analysis statistics"""
    try:
        manager = get_novel_data_manager(str(novel_id))

        # Query various statistics
        stats_queries = {
            "conflict_matrices": """
                SELECT COUNT(*) as count, AVG(intensity) as avg_intensity
                FROM cross_domain_conflict_matrix WHERE novel_id = $1
            """,
            "conflict_entities": """
                SELECT COUNT(*) as count, entity_type, AVG(strategic_value) as avg_value
                FROM conflict_entities WHERE novel_id = $1 GROUP BY entity_type
            """,
            "story_hooks": """
                SELECT COUNT(*) as count, hook_type, AVG(overall_score) as avg_score,
                       COUNT(CASE WHEN is_ai_generated THEN 1 END) as ai_generated_count
                FROM conflict_story_hooks WHERE novel_id = $1 GROUP BY hook_type
            """,
            "domain_participation": """
                WITH domain_conflicts AS (
                    SELECT domain_a as domain, intensity FROM cross_domain_conflict_matrix WHERE novel_id = $1
                    UNION ALL
                    SELECT domain_b as domain, intensity FROM cross_domain_conflict_matrix WHERE novel_id = $1
                )
                SELECT domain, COUNT(*) as conflict_count, AVG(intensity) as avg_intensity
                FROM domain_conflicts
                GROUP BY domain
                ORDER BY avg_intensity DESC
            """
        }

        statistics = {}
        for stat_name, query in stats_queries.items():
            results = await manager.fetch_query(query, str(novel_id))

            if stat_name in ["conflict_entities", "story_hooks"]:
                statistics[stat_name] = [dict(row) for row in results]
            elif stat_name == "domain_participation":
                statistics[stat_name] = [dict(row) for row in results]
            else:
                statistics[stat_name] = dict(results[0]) if results else {"count": 0}

        return StatisticsResponse(
            success=True,
            message="Conflict statistics retrieved successfully",
            statistics=statistics,
            generated_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Conflict statistics query failed: {e}")
        raise handle_database_error(e)