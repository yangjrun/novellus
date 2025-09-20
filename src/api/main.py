#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Novellus FastAPI Application
RESTful API service for novel worldbuilding and content management
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.config import settings
from api.core.exceptions import APIException, handle_api_exception
from api.core.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    AuthenticationMiddleware,
    RequestValidationMiddleware
)
from api.core.database import init_database, close_database
from api.v1.router import api_v1_router

# API metadata
API_METADATA = {
    "title": "Novellus API",
    "description": """
    ## Novellus - Novel Worldbuilding & Content Management API

    A comprehensive RESTful API for managing novel projects, worldbuilding elements,
    content creation workflows, and collaborative writing features.

    ### Features
    - 📚 **Project Management**: Create and manage multiple novel projects
    - 🌍 **Worldbuilding**: Define domains, law chains, cultural frameworks
    - ✍️ **Content Creation**: Batch management, content segments, collaborative workflows
    - 🔄 **Conflict Analysis**: Cross-domain conflicts, network analysis, story hooks
    - 🤖 **AI Integration**: Prompt generation, content analysis, optimization
    - 📊 **Analytics**: Statistics, search, and reporting capabilities

    ### API Versioning
    - Current version: v1
    - Base URL: `/api/v1`

    ### Authentication
    - API Key authentication (when enabled)
    - Bearer token support for user sessions

    ### Rate Limiting
    - Default: 100 requests per minute
    - Burst: 10 concurrent requests
    """,
    "version": "1.0.0",
    "contact": {
        "name": "Novellus Team",
        "email": "support@novellus.io"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager
    Handles startup and shutdown events
    """
    # Startup
    print("Starting Novellus API Server...")

    # Initialize database connections
    try:
        await init_database()
        print("Database connections established")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Continue anyway for development, but log the error

    # Initialize cache if configured
    if settings.CACHE_ENABLED:
        from api.core.cache import init_cache
        await init_cache()
        print("Cache initialized")

    # Initialize monitoring
    if settings.MONITORING_ENABLED:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
        print("Monitoring enabled at /metrics")

    print(f"API ready at http://{settings.HOST}:{settings.PORT}")
    print(f"Documentation available at http://{settings.HOST}:{settings.PORT}/docs")

    yield

    # Shutdown
    print("Shutting down Novellus API Server...")

    # Close database connections
    await close_database()
    print("Database connections closed")

    # Close cache connections
    if settings.CACHE_ENABLED:
        from api.core.cache import close_cache
        await close_cache()
        print("Cache closed")

    print("Server shutdown complete")


# Create FastAPI application
app = FastAPI(
    **API_METADATA,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware for security
if settings.TRUSTED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS
    )

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limit=settings.RATE_LIMIT)
app.add_middleware(RequestValidationMiddleware)

# Add authentication middleware if enabled
if settings.AUTH_ENABLED:
    app.add_middleware(AuthenticationMiddleware)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - redirects to documentation"""
    return RedirectResponse(url="/docs")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns server status and database connectivity
    """
    from api.core.database import get_database_health

    db_health = await get_database_health()

    health_status = {
        "status": "healthy" if all(db_health.values()) else "degraded",
        "version": API_METADATA["version"],
        "services": {
            "api": "running",
            "postgresql": "connected" if db_health.get("postgresql") else "disconnected",
            "mongodb": "connected" if db_health.get("mongodb") else "disconnected",
            "cache": "connected" if settings.CACHE_ENABLED else "disabled"
        }
    }

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


# Ready check endpoint
@app.get("/ready", tags=["Health"])
async def ready_check():
    """
    Readiness check endpoint
    Returns whether the service is ready to accept requests
    """
    from api.core.database import get_database_health

    db_health = await get_database_health()
    is_ready = all(db_health.values())

    return JSONResponse(
        content={"ready": is_ready},
        status_code=200 if is_ready else 503
    )


# API info endpoint
@app.get("/info", tags=["Info"])
async def api_info():
    """
    API information endpoint
    Returns API metadata and configuration info
    """
    return {
        "name": API_METADATA["title"],
        "version": API_METADATA["version"],
        "description": "Novellus API - Novel Worldbuilding & Content Management",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "features": {
            "authentication": settings.AUTH_ENABLED,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "caching": settings.CACHE_ENABLED,
            "monitoring": settings.MONITORING_ENABLED
        }
    }


# Include API v1 router
app.include_router(
    api_v1_router,
    prefix="/api/v1",
    tags=["API v1"]
)


# Global exception handler
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle API exceptions"""
    return handle_api_exception(request, exc)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    import traceback
    from uuid import uuid4

    # Log the error
    error_id = str(uuid4())
    traceback_str = traceback.format_exc()

    # In production, don't expose internal errors
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_id": error_id,
                "message": "An unexpected error occurred"
            }
        )

    # In development, include more details
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_id": error_id,
            "message": str(exc),
            "type": exc.__class__.__name__,
            "traceback": traceback_str.split('\n')
        }
    )


def run_server():
    """Run the FastAPI server"""
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.AUTO_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ACCESS_LOG_ENABLED,
        workers=settings.WORKERS if not settings.AUTO_RELOAD else 1
    )


if __name__ == "__main__":
    run_server()