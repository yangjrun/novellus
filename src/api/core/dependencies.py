"""
FastAPI Dependencies
Common dependencies for authentication, database access, and validation
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Annotated
import logging

from api.core.config import settings
from api.core.database import (
    get_global_data_manager,
    get_novel_data_manager,
    get_batch_data_manager,
    get_cultural_repo,
    get_law_chain_mgr
)

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)


async def get_global_manager():
    """Get global data manager dependency"""
    return await get_global_data_manager()


async def get_novel_manager(novel_id: str):
    """Get novel-specific data manager dependency"""
    return await get_novel_data_manager(novel_id)


async def get_batch_manager(novel_id: str):
    """Get batch manager dependency"""
    return await get_batch_data_manager(novel_id)


async def get_cultural_repository():
    """Get cultural framework repository dependency"""
    return await get_cultural_repo()


async def get_law_chain_manager():
    """Get law chain manager dependency"""
    return await get_law_chain_mgr()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> Optional[dict]:
    """
    Get current user from authorization token
    Returns None if authentication is disabled
    """
    if not settings.AUTH_ENABLED:
        return {"id": "anonymous", "username": "anonymous", "roles": ["user"]}
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Implement actual JWT token validation
    # For now, return a mock user
    return {
        "id": "user_123",
        "username": "test_user", 
        "roles": ["user"]
    }


async def require_auth(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """
    Require authentication - raises exception if user not authenticated
    """
    if not current_user or current_user.get("id") == "anonymous":
        if settings.AUTH_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
    
    return current_user


def require_role(required_role: str):
    """
    Create a dependency that requires a specific role
    """
    async def role_checker(
        current_user: Annotated[dict, Depends(require_auth)]
    ) -> dict:
        user_roles = current_user.get("roles", [])
        if required_role not in user_roles and "admin" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    
    return role_checker


# Common role dependencies
require_admin = require_role("admin")
require_editor = require_role("editor")
require_user = require_role("user")


async def validate_novel_id(novel_id: str) -> str:
    """
    Validate and return novel_id
    """
    if not novel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Novel ID is required"
        )
    
    # TODO: Add actual novel existence validation
    return novel_id


async def validate_project_id(project_id: str) -> str:
    """
    Validate and return project_id
    """
    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID is required"
        )
    
    # TODO: Add actual project existence validation
    return project_id
