#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Novellus API Server Launcher
Run the FastAPI application with proper configuration
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Main entry point for running the API server"""
    import uvicorn
    from api.core.config import settings

    print("=" * 60)
    print("🚀 Starting Novellus RESTful API Server")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"Auto-reload: {settings.AUTO_RELOAD}")
    print(f"Workers: {settings.WORKERS if not settings.AUTO_RELOAD else 1}")
    print("=" * 60)

    # Run the server
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.AUTO_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ACCESS_LOG_ENABLED,
        workers=settings.WORKERS if not settings.AUTO_RELOAD else 1
    )


if __name__ == "__main__":
    main()