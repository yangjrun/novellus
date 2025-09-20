#!/usr/bin/env python3
"""
FastAPI Server Startup Script
Handles environment setup and server initialization
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api.core.config import settings
from database.database_init import initialize_database


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_database():
    """Initialize database if needed"""
    logger.info("Checking database initialization...")
    try:
        result = await initialize_database()
        if result["overall_success"]:
            logger.info("Database initialized successfully")
        else:
            logger.warning(f"Database initialization incomplete: {result}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if settings.ENVIRONMENT == "production":
            sys.exit(1)


def run_development():
    """Run development server with auto-reload"""
    import uvicorn

    logger.info("Starting development server...")
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )


def run_production():
    """Run production server with multiple workers"""
    import uvicorn

    logger.info("Starting production server...")
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ACCESS_LOG_ENABLED,
        loop="uvloop",
        lifespan="on"
    )


def run_gunicorn():
    """Run with Gunicorn for production deployment"""
    import subprocess

    workers = settings.WORKERS
    bind = f"{settings.HOST}:{settings.PORT}"

    cmd = [
        "gunicorn",
        "api.main:app",
        "-w", str(workers),
        "-k", "uvicorn.workers.UvicornWorker",
        "--bind", bind,
        "--log-level", settings.LOG_LEVEL.lower(),
        "--access-logfile", "-" if settings.ACCESS_LOG_ENABLED else "/dev/null",
        "--error-logfile", "-",
        "--timeout", "120",
        "--graceful-timeout", "30",
        "--max-requests", "1000",
        "--max-requests-jitter", "50"
    ]

    logger.info(f"Starting Gunicorn with {workers} workers on {bind}")
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="Novellus FastAPI Server")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "gunicorn"],
        default="dev",
        help="Server mode (default: dev)"
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database before starting"
    )
    parser.add_argument(
        "--host",
        default=None,
        help=f"Host to bind (default: {settings.HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"Port to bind (default: {settings.PORT})"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help=f"Number of workers for production (default: {settings.WORKERS})"
    )

    args = parser.parse_args()

    # Override settings from command line
    if args.host:
        settings.HOST = args.host
    if args.port:
        settings.PORT = args.port
    if args.workers:
        settings.WORKERS = args.workers

    # Initialize database if requested
    if args.init_db:
        logger.info("Initializing database...")
        asyncio.run(setup_database())

    # Start server based on mode
    if args.mode == "dev":
        settings.ENVIRONMENT = "development"
        run_development()
    elif args.mode == "prod":
        settings.ENVIRONMENT = "production"
        run_production()
    elif args.mode == "gunicorn":
        settings.ENVIRONMENT = "production"
        run_gunicorn()


if __name__ == "__main__":
    main()