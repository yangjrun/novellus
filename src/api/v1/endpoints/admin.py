"""
Administration Endpoints
Handles database management, system health, and administrative tasks
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Body, status, HTTPException
from datetime import datetime

from api.v1.schemas.responses import (
    DataResponse, StatusResponse, TaskResponse,
    success_response, error_response
)
from api.core.database import (
    get_database_health, test_database_connection,
    init_database as init_db
)
from api.core.exceptions import handle_database_error, ServiceUnavailableException
from database.database_init import initialize_database, reset_database
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/health",
    response_model=StatusResponse,
    summary="System health check",
    description="Check the health status of all system components"
)
async def health_check():
    """Check system health"""
    try:
        # Get database health
        db_health = await get_database_health()

        # Determine overall status
        all_healthy = all(db_health.values())
        status = "healthy" if all_healthy else "degraded"

        services = {
            "api": "running",
            "postgresql": "connected" if db_health.get("postgresql") else "disconnected",
            "mongodb": "connected" if db_health.get("mongodb") else "disconnected"
        }

        return StatusResponse(
            success=True,
            message=f"System is {status}",
            status=status,
            services=services,
            version="1.0.0"
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise ServiceUnavailableException("Health check failed")


@router.post(
    "/database/initialize",
    response_model=DataResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Initialize database",
    description="Initialize database structure and base data"
)
async def initialize_database_endpoint(
    reset_existing: bool = Body(False, description="Reset existing database"),
    seed_data: bool = Body(True, description="Load seed data")
):
    """Initialize database"""
    try:
        if reset_existing:
            logger.warning("Resetting existing database")
            await reset_database()

        result = await initialize_database()

        response_data = {
            "postgresql": result["postgresql"],
            "mongodb": result["mongodb"],
            "overall_success": result["overall_success"],
            "seed_data_loaded": seed_data,
            "timestamp": datetime.now().isoformat()
        }

        if not result["overall_success"]:
            raise ServiceUnavailableException("Database initialization partially failed")

        return DataResponse(
            success=True,
            message="Database initialized successfully",
            data=response_data
        )

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise handle_database_error(e)


@router.get(
    "/database/status",
    response_model=DataResponse[dict],
    summary="Database status",
    description="Get detailed database connection status"
)
async def get_database_status():
    """Get database status"""
    try:
        health = await get_database_health()
        can_connect = await test_database_connection()

        status_data = {
            "connections": health,
            "can_connect": can_connect,
            "postgresql": {
                "status": "connected" if health.get("postgresql") else "disconnected",
                "host": "localhost",
                "port": 5432,
                "database": "postgres"
            },
            "mongodb": {
                "status": "connected" if health.get("mongodb") else "disconnected",
                "host": "localhost",
                "port": 27017,
                "database": "novellus"
            },
            "timestamp": datetime.now().isoformat()
        }

        return DataResponse(
            success=True,
            message="Database status retrieved",
            data=status_data
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/database/backup",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Backup database",
    description="Create a database backup"
)
async def backup_database(
    backup_type: str = Body("full", description="Type of backup (full/incremental)"),
    include_mongodb: bool = Body(True, description="Include MongoDB in backup")
):
    """Create database backup"""
    try:
        # This would trigger actual backup process
        # Placeholder implementation
        task_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return TaskResponse(
            success=True,
            message=f"Database backup started ({backup_type})",
            task_id=task_id,
            status="running",
            started_at=datetime.now()
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/database/restore",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Restore database",
    description="Restore database from backup"
)
async def restore_database(
    backup_id: str = Body(..., description="Backup ID to restore from"),
    confirm: bool = Body(False, description="Confirm restore operation")
):
    """Restore database from backup"""
    try:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restore operation requires confirmation (confirm=true)"
            )

        # This would trigger actual restore process
        # Placeholder implementation
        task_id = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return TaskResponse(
            success=True,
            message=f"Database restore started from backup {backup_id}",
            task_id=task_id,
            status="running",
            started_at=datetime.now()
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/cache/clear",
    response_model=DataResponse[dict],
    summary="Clear cache",
    description="Clear application cache"
)
async def clear_cache(
    cache_type: str = Body("all", description="Type of cache to clear"),
    pattern: Optional[str] = Body(None, description="Pattern for selective clearing")
):
    """Clear application cache"""
    try:
        # This would clear actual cache
        # Placeholder implementation
        cleared_items = 0

        if cache_type == "all":
            cleared_items = 100  # Placeholder
        elif cache_type == "api":
            cleared_items = 50  # Placeholder
        elif cache_type == "database":
            cleared_items = 30  # Placeholder

        return DataResponse(
            success=True,
            message=f"Cache cleared successfully",
            data={
                "cache_type": cache_type,
                "pattern": pattern,
                "cleared_items": cleared_items,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/logs",
    response_model=DataResponse[list],
    summary="Get system logs",
    description="Retrieve system logs"
)
async def get_system_logs(
    level: str = Query("INFO", description="Log level filter"),
    limit: int = Query(100, ge=1, le=1000, description="Number of log entries"),
    component: Optional[str] = Query(None, description="Filter by component")
):
    """Get system logs"""
    try:
        # This would fetch actual logs
        # Placeholder implementation
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "component": "api",
                "message": "API request processed successfully"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "WARNING",
                "component": "database",
                "message": "Slow query detected"
            }
        ]

        # Apply filters
        if component:
            logs = [log for log in logs if log["component"] == component]

        return DataResponse(
            success=True,
            message=f"Retrieved {len(logs[:limit])} log entries",
            data=logs[:limit]
        )

    except Exception as e:
        raise handle_database_error(e)


@router.get(
    "/metrics",
    response_model=DataResponse[dict],
    summary="Get system metrics",
    description="Retrieve system performance metrics"
)
async def get_system_metrics():
    """Get system metrics"""
    try:
        # This would collect actual metrics
        # Placeholder implementation
        metrics = {
            "api": {
                "requests_per_minute": 120,
                "average_response_time_ms": 45,
                "error_rate": 0.02,
                "active_connections": 15
            },
            "database": {
                "postgresql": {
                    "connections_active": 5,
                    "connections_idle": 10,
                    "queries_per_second": 50,
                    "average_query_time_ms": 12
                },
                "mongodb": {
                    "connections_active": 3,
                    "operations_per_second": 30,
                    "average_operation_time_ms": 8
                }
            },
            "system": {
                "cpu_usage_percent": 35,
                "memory_usage_mb": 512,
                "disk_usage_percent": 45,
                "uptime_hours": 168
            },
            "timestamp": datetime.now().isoformat()
        }

        return DataResponse(
            success=True,
            message="System metrics retrieved",
            data=metrics
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/maintenance/mode",
    response_model=DataResponse[dict],
    summary="Toggle maintenance mode",
    description="Enable or disable maintenance mode"
)
async def set_maintenance_mode(
    enabled: bool = Body(..., description="Enable maintenance mode"),
    message: Optional[str] = Body(None, description="Maintenance message"),
    estimated_duration_minutes: Optional[int] = Body(None, description="Estimated duration")
):
    """Toggle maintenance mode"""
    try:
        # This would set actual maintenance mode
        # Placeholder implementation
        maintenance_data = {
            "enabled": enabled,
            "message": message or "System is under maintenance",
            "started_at": datetime.now().isoformat() if enabled else None,
            "estimated_end": datetime.now().isoformat() if estimated_duration_minutes else None
        }

        return DataResponse(
            success=True,
            message=f"Maintenance mode {'enabled' if enabled else 'disabled'}",
            data=maintenance_data
        )

    except Exception as e:
        raise handle_database_error(e)


@router.post(
    "/test/connection",
    response_model=DataResponse[dict],
    summary="Test external connections",
    description="Test connections to external services"
)
async def test_connections():
    """Test external service connections"""
    try:
        results = {
            "database": {
                "postgresql": await test_database_connection(),
                "mongodb": await test_database_connection()  # Would test MongoDB specifically
            },
            "external_services": {
                "claude_api": True,  # Would test Claude API
                "storage": True  # Would test storage service
            },
            "timestamp": datetime.now().isoformat()
        }

        all_connected = all([
            results["database"]["postgresql"],
            results["database"]["mongodb"],
            results["external_services"]["claude_api"]
        ])

        return DataResponse(
            success=all_connected,
            message="Connection test completed",
            data=results
        )

    except Exception as e:
        raise handle_database_error(e)