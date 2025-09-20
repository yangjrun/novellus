"""
API v1 Router
Main router that combines all v1 endpoints
"""

from fastapi import APIRouter

from api.v1.endpoints import (
    projects,
    novels,
    content,
    worldbuilding,
    cultural,
    conflicts,
    collaborative,
    search,
    admin
)

# Create main v1 router
api_v1_router = APIRouter()

# Include all endpoint routers
api_v1_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"]
)

api_v1_router.include_router(
    novels.router,
    prefix="/novels",
    tags=["Novels"]
)

api_v1_router.include_router(
    content.router,
    prefix="/content",
    tags=["Content Management"]
)

api_v1_router.include_router(
    worldbuilding.router,
    prefix="/worldbuilding",
    tags=["Worldbuilding"]
)

api_v1_router.include_router(
    cultural.router,
    prefix="/cultural",
    tags=["Cultural Framework"]
)

api_v1_router.include_router(
    conflicts.router,
    prefix="/conflicts",
    tags=["Conflict Analysis"]
)

api_v1_router.include_router(
    collaborative.router,
    prefix="/collaborative",
    tags=["Collaborative Writing"]
)

api_v1_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search & Analytics"]
)

api_v1_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administration"]
)