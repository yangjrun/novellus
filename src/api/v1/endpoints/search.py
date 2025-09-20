"""
Search and Analytics Endpoints
Handles content search, statistics, and analytics
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, Path, status

from api.v1.schemas.responses import DataResponse, ListResponse, StatisticsResponse
from api.core.database import get_novel_data_manager, get_cultural_repo
from api.core.exceptions import handle_database_error
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/content",
    response_model=DataResponse[dict],
    summary="Search novel content",
    description="Full-text search across all novel content"
)
async def search_content(
    novel_id: UUID = Query(..., description="Novel UUID"),
    query: str = Query(..., min_length=1, max_length=200, description="Search query"),
    content_types: Optional[List[str]] = Query(None, description="Content types to search"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Search novel content"""
    try:
        novel_manager = get_novel_data_manager(str(novel_id))

        # Perform search
        search_results = await novel_manager.search_content(
            query=query,
            content_types=content_types
        )

        # Format results
        formatted_results = {
            "query": query,
            "total_results": 0,
            "segments": [],
            "characters": [],
            "locations": [],
            "knowledge": []
        }

        # Process segments
        if "segments" in search_results:
            segments = search_results["segments"]
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            paginated_segments = segments[start:end]

            formatted_results["segments"] = [
                {
                    "id": str(s.id),
                    "title": s.title,
                    "content_preview": s.content[:200] + "..." if len(s.content) > 200 else s.content,
                    "word_count": s.word_count,
                    "tags": s.tags,
                    "relevance_score": getattr(s, 'relevance_score', 1.0)
                }
                for s in paginated_segments
            ]

        # Process characters
        if "characters" in search_results:
            formatted_results["characters"] = [
                {
                    "id": c.id,
                    "name": c.name,
                    "character_type": c.character_type,
                    "tags": c.tags
                }
                for c in search_results["characters"][:10]  # Limit to 10
            ]

        formatted_results["total_results"] = sum([
            len(search_results.get("segments", [])),
            len(search_results.get("characters", [])),
            len(search_results.get("locations", [])),
            len(search_results.get("knowledge", []))
        ])

        return DataResponse(
            success=True,
            message=f"Found {formatted_results['total_results']} results for '{query}'",
            data=formatted_results
        )

    except Exception as e:
        logger.error(f"Content search failed: {e}")
        raise handle_database_error(e)


@router.get(
    "/statistics/novel/{novel_id}",
    response_model=StatisticsResponse,
    summary="Get novel statistics",
    description="Get comprehensive statistics for a novel"
)
async def get_novel_statistics(
    novel_id: UUID = Path(..., description="Novel UUID"),
    include_trends: bool = Query(False, description="Include trend data")
):
    """Get novel statistics"""
    try:
        novel_manager = get_novel_data_manager(str(novel_id))
        stats = await novel_manager.get_novel_statistics()

        # Add trend data if requested
        if include_trends:
            stats["trends"] = await calculate_trends(str(novel_id))

        return StatisticsResponse(
            success=True,
            message="Novel statistics retrieved successfully",
            statistics=stats,
            generated_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to get novel statistics: {e}")
        raise handle_database_error(e)


@router.get(
    "/analytics/writing-progress",
    response_model=DataResponse[dict],
    summary="Get writing progress analytics",
    description="Analyze writing progress and productivity"
)
async def get_writing_progress(
    novel_id: UUID = Query(..., description="Novel UUID"),
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days")
):
    """Get writing progress analytics"""
    try:
        novel_manager = get_novel_data_manager(str(novel_id))

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        # Get content created in period
        batches = await novel_manager.get_content_batches()
        recent_batches = [
            b for b in batches
            if b.created_at >= start_date
        ]

        # Calculate statistics
        total_words = sum(b.total_word_count for b in recent_batches if hasattr(b, 'total_word_count'))
        daily_average = total_words / period_days if period_days > 0 else 0

        progress_data = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": period_days
            },
            "content": {
                "batches_created": len(recent_batches),
                "total_words": total_words,
                "daily_average": daily_average
            },
            "productivity": {
                "most_productive_day": "Monday",  # Placeholder
                "peak_hours": "14:00-18:00",  # Placeholder
                "streak_days": 5  # Placeholder
            }
        }

        return DataResponse(
            success=True,
            message="Writing progress analytics retrieved",
            data=progress_data
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/analytics/content-distribution",
    response_model=DataResponse[dict],
    summary="Get content distribution",
    description="Analyze distribution of content types and categories"
)
async def get_content_distribution(
    novel_id: UUID = Query(..., description="Novel UUID")
):
    """Get content distribution analytics"""
    try:
        novel_manager = get_novel_data_manager(str(novel_id))

        # Get all content segments
        segments = await novel_manager.get_all_content_segments()

        # Calculate distribution
        distribution = {
            "by_type": {},
            "by_status": {},
            "by_tag": {},
            "word_count_ranges": {
                "0-500": 0,
                "500-1000": 0,
                "1000-2000": 0,
                "2000+": 0
            }
        }

        for segment in segments:
            # By type
            seg_type = segment.segment_type
            distribution["by_type"][seg_type] = distribution["by_type"].get(seg_type, 0) + 1

            # By status
            status = segment.status
            distribution["by_status"][status] = distribution["by_status"].get(status, 0) + 1

            # By word count range
            wc = segment.word_count
            if wc < 500:
                distribution["word_count_ranges"]["0-500"] += 1
            elif wc < 1000:
                distribution["word_count_ranges"]["500-1000"] += 1
            elif wc < 2000:
                distribution["word_count_ranges"]["1000-2000"] += 1
            else:
                distribution["word_count_ranges"]["2000+"] += 1

            # By tags
            for tag in segment.tags:
                distribution["by_tag"][tag] = distribution["by_tag"].get(tag, 0) + 1

        return DataResponse(
            success=True,
            message="Content distribution analysis completed",
            data=distribution
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/trending",
    response_model=DataResponse[dict],
    summary="Get trending elements",
    description="Identify trending characters, themes, and topics"
)
async def get_trending_elements(
    novel_id: UUID = Query(..., description="Novel UUID"),
    period_days: int = Query(7, ge=1, le=90, description="Trending period in days"),
    limit: int = Query(10, ge=1, le=50, description="Number of items per category")
):
    """Get trending elements in the novel"""
    try:
        # This would analyze recent content to find trending elements
        # Placeholder implementation
        trending = {
            "characters": [
                {"name": "Protagonist", "mentions": 45, "trend": "+15%"},
                {"name": "Antagonist", "mentions": 32, "trend": "+8%"}
            ][:limit],
            "themes": [
                {"theme": "Conflict", "occurrences": 28, "trend": "+12%"},
                {"theme": "Discovery", "occurrences": 19, "trend": "+5%"}
            ][:limit],
            "locations": [
                {"location": "Capital City", "mentions": 21, "trend": "+10%"},
                {"location": "Ancient Temple", "mentions": 15, "trend": "+7%"}
            ][:limit],
            "period": {
                "start": (datetime.now() - timedelta(days=period_days)).isoformat(),
                "end": datetime.now().isoformat()
            }
        }

        return DataResponse(
            success=True,
            message="Trending elements retrieved",
            data=trending
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/suggestions",
    response_model=DataResponse[List[dict]],
    summary="Get content suggestions",
    description="Get AI-powered content suggestions based on analysis"
)
async def get_content_suggestions(
    novel_id: UUID = Query(..., description="Novel UUID"),
    suggestion_type: str = Query("plot", description="Type of suggestions"),
    count: int = Query(5, ge=1, le=20, description="Number of suggestions")
):
    """Get content suggestions"""
    try:
        # This would use AI to generate suggestions based on content analysis
        # Placeholder implementation
        suggestions = []

        if suggestion_type == "plot":
            suggestions = [
                {
                    "type": "plot_twist",
                    "suggestion": "Reveal hidden connection between two characters",
                    "confidence": 0.85,
                    "reasoning": "Based on established relationships and foreshadowing"
                },
                {
                    "type": "conflict_escalation",
                    "suggestion": "Introduce external threat to unite opposing factions",
                    "confidence": 0.78,
                    "reasoning": "Current conflict patterns suggest need for escalation"
                }
            ]
        elif suggestion_type == "character":
            suggestions = [
                {
                    "type": "character_development",
                    "suggestion": "Explore protagonist's backstory through flashback",
                    "confidence": 0.82,
                    "reasoning": "Character lacks depth in current narrative"
                }
            ]
        elif suggestion_type == "worldbuilding":
            suggestions = [
                {
                    "type": "world_expansion",
                    "suggestion": "Develop the economic system of the Northern Realm",
                    "confidence": 0.75,
                    "reasoning": "Referenced but not fully explained in current content"
                }
            ]

        return DataResponse(
            success=True,
            message=f"Generated {len(suggestions[:count])} {suggestion_type} suggestions",
            data=suggestions[:count]
        )

    except Exception as e:
        raise handle_database_error(e)


# Helper function
async def calculate_trends(novel_id: str) -> dict:
    """Calculate trend data for the novel"""
    # Placeholder implementation
    return {
        "word_count_trend": "+12.5%",
        "productivity_trend": "increasing",
        "quality_score_trend": "stable",
        "period": "last_30_days"
    }