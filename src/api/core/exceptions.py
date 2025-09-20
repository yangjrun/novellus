"""
Custom Exception Classes and Handlers for the API
"""

from typing import Optional, Dict, Any, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback
import uuid
import logging

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception class for API"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type: str = "APIError",
        details: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details
        self.headers = headers
        self.error_id = str(uuid.uuid4())
        super().__init__(self.message)


class ValidationException(APIException):
    """Exception for validation errors"""

    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="ValidationError",
            details=details
        )


class NotFoundException(APIException):
    """Exception for resource not found"""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="NotFound"
        )


class ConflictException(APIException):
    """Exception for resource conflicts"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_type="Conflict"
        )


class UnauthorizedException(APIException):
    """Exception for unauthorized access"""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(APIException):
    """Exception for forbidden access"""

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="Forbidden"
        )


class BadRequestException(APIException):
    """Exception for bad requests"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="BadRequest"
        )


class RateLimitException(APIException):
    """Exception for rate limit exceeded"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_type="RateLimit",
            headers=headers
        )


class ServiceUnavailableException(APIException):
    """Exception for service unavailable"""

    def __init__(self, message: str = "Service temporarily unavailable", retry_after: Optional[int] = None):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type="ServiceUnavailable",
            headers=headers
        )


class DatabaseException(APIException):
    """Exception for database errors"""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="DatabaseError"
        )


class ExternalServiceException(APIException):
    """Exception for external service errors"""

    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_type="ExternalServiceError"
        )


class PayloadTooLargeException(APIException):
    """Exception for payload too large"""

    def __init__(self, max_size: int):
        super().__init__(
            message=f"Payload too large. Maximum size is {max_size} bytes",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_type="PayloadTooLarge"
        )


class TimeoutException(APIException):
    """Exception for operation timeout"""

    def __init__(self, message: str = "Operation timed out"):
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_type="Timeout"
        )


def handle_api_exception(request: Request, exc: APIException) -> JSONResponse:
    """Handle API exceptions and return formatted response"""

    # Log the exception
    logger.error(
        f"API Exception: {exc.error_type} - {exc.message}",
        extra={
            "error_id": exc.error_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )

    # Create error response
    error_response = {
        "success": False,
        "message": exc.message,
        "error_type": exc.error_type,
        "error_id": exc.error_id,
        "timestamp": datetime.now().isoformat()
    }

    # Add details if available
    if exc.details:
        error_response["details"] = exc.details

    # Add request information in development mode
    from api.core.config import settings
    if settings.DEBUG:
        error_response["request"] = {
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params)
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers
    )


def handle_database_error(error: Exception) -> APIException:
    """Convert database errors to API exceptions"""

    error_message = str(error)

    # Check for specific database error patterns
    if "duplicate key" in error_message.lower():
        return ConflictException("Resource already exists")
    elif "foreign key" in error_message.lower():
        return BadRequestException("Referenced resource does not exist")
    elif "not found" in error_message.lower():
        return NotFoundException("Resource", None)
    elif "connection" in error_message.lower():
        return ServiceUnavailableException("Database connection failed")
    else:
        return DatabaseException(f"Database error: {error_message}")


def handle_validation_error(errors: List[Dict[str, Any]]) -> ValidationException:
    """Convert validation errors to API exception"""

    # Format validation errors
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "validation_error")
        })

    message = "Validation failed for one or more fields"
    return ValidationException(message, formatted_errors)


# Error response models for OpenAPI documentation
ERROR_RESPONSES = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Invalid request parameters",
                    "error_type": "BadRequest",
                    "error_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Unauthorized access",
                    "error_type": "Unauthorized",
                    "error_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Access forbidden",
                    "error_type": "Forbidden",
                    "error_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Resource not found",
                    "error_type": "NotFound",
                    "error_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    },
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation failed",
                    "error_type": "ValidationError",
                    "error_id": "123e4567-e89b-12d3-a456-426614174000",
                    "details": [
                        {
                            "field": "name",
                            "message": "Field is required",
                            "type": "missing"
                        }
                    ]
                }
            }
        }
    },
    429: {
        "description": "Too Many Requests",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Rate limit exceeded",
                    "error_type": "RateLimit",
                    "error_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Internal server error",
                    "error_type": "InternalError",
                    "error_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    }
}

class NotFoundError(APIException):
    """Exception for when a resource is not found"""
    
    def __init__(self, message: str = "Resource not found", resource_type: str = "resource", resource_id: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="NotFoundError",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ValidationError(APIException):
    """Exception for validation errors"""
    
    def __init__(self, message: str = "Validation failed", field: str = None, value: Any = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="ValidationError",
            details={"field": field, "value": value}
        )


class ConflictError(APIException):
    """Exception for resource conflicts"""
    
    def __init__(self, message: str = "Resource conflict", resource_type: str = "resource", conflict_reason: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_type="ConflictError",
            details={"resource_type": resource_type, "conflict_reason": conflict_reason}
        )


class AuthenticationError(APIException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="AuthenticationError"
        )


class AuthorizationError(APIException):
    """Exception for authorization errors"""
    
    def __init__(self, message: str = "Access denied", required_permission: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="AuthorizationError",
            details={"required_permission": required_permission}
        )


class ServiceUnavailableException(APIException):
    """Exception for when a service is unavailable"""
    
    def __init__(self, message: str = "Service temporarily unavailable", service: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type="ServiceUnavailableException",
            details={"service": service}
        )


class RateLimitExceededError(APIException):
    """Exception for rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_type="RateLimitExceededError",
            details={"retry_after": retry_after}
        )


class DatabaseError(APIException):
    """Exception for database errors"""
    
    def __init__(self, message: str = "Database error", operation: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="DatabaseError",
            details={"operation": operation}
        )
