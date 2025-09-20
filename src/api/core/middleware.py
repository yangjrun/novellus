"""
Custom Middleware Components
Handles cross-cutting concerns like authentication, rate limiting, logging, etc.
"""

import time
import json
import uuid
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.core.config import settings
from api.core.cache import get_cache_client


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request {request_id} failed: {str(e)}")
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # Log response
        logger.info(
            f"Response {request_id}: {response.status_code} "
            f"({process_time:.3f}s)"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    """

    def __init__(
        self,
        app: ASGIApp,
        rate_limit: int = 100,  # requests per minute
        burst_size: int = 10,    # burst capacity
        use_cache: bool = True   # use Redis if available
    ):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.burst_size = burst_size
        self.use_cache = use_cache
        self.local_storage = defaultdict(list)  # fallback for no cache

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        allowed, remaining = await self._check_rate_limit(client_id)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.rate_limit}/minute",
                    "retry_after": 60
                },
                headers={
                    "X-RateLimit-Limit": str(self.rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get from API key or auth
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"

        # Fallback to IP address
        if request.client:
            return f"ip:{request.client.host}"

        return "anonymous"

    async def _check_rate_limit(self, client_id: str) -> tuple[bool, int]:
        """Check if client has exceeded rate limit"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        if self.use_cache and settings.CACHE_ENABLED:
            # Use Redis for distributed rate limiting
            cache = get_cache_client()
            if cache:
                key = f"rate_limit:{client_id}"
                try:
                    # Implement sliding window in Redis
                    pipe = cache.pipeline()
                    pipe.zremrangebyscore(key, 0, minute_ago.timestamp())
                    pipe.zadd(key, {str(uuid.uuid4()): now.timestamp()})
                    pipe.zcount(key, minute_ago.timestamp(), now.timestamp())
                    pipe.expire(key, 120)
                    results = await pipe.execute()

                    request_count = results[2]
                    remaining = max(0, self.rate_limit - request_count)

                    return request_count <= self.rate_limit, remaining
                except Exception as e:
                    logger.error(f"Redis rate limit error: {e}")
                    # Fall through to local storage

        # Use local storage (not distributed)
        requests = self.local_storage[client_id]

        # Remove old requests
        requests = [req_time for req_time in requests if req_time > minute_ago]

        # Add current request
        requests.append(now)
        self.local_storage[client_id] = requests

        remaining = max(0, self.rate_limit - len(requests))
        return len(requests) <= self.rate_limit, remaining


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for API key and JWT validation
    """

    EXEMPT_PATHS = [
        "/",
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics"
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Skip if auth is disabled
        if not settings.AUTH_ENABLED:
            return await call_next(request)

        # Check for API key
        api_key = request.headers.get(settings.API_KEY_HEADER)
        if api_key:
            if await self._validate_api_key(api_key):
                request.state.authenticated = True
                return await call_next(request)

        # Check for Bearer token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            user_info = await self._validate_jwt_token(token)
            if user_info:
                request.state.authenticated = True
                request.state.user_id = user_info.get("user_id")
                request.state.user = user_info
                return await call_next(request)

        # No valid authentication
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Unauthorized",
                "message": "Valid authentication required"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    async def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        # Implement API key validation logic
        # This could check against database or configuration
        valid_keys = settings.get("API_KEYS", [])
        return api_key in valid_keys

    async def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user info"""
        try:
            import jwt

            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.now():
                return None

            return payload

        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return None


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request validation and sanitization
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Validate content type for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")

            # Check if JSON is expected
            if request.url.path.startswith("/api/") and not content_type.startswith("application/json"):
                if not content_type.startswith("multipart/form-data"):
                    return JSONResponse(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        content={
                            "error": "Unsupported Media Type",
                            "message": "Content-Type must be application/json"
                        }
                    )

        # Validate request size
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                size = int(content_length)
                if size > settings.MAX_UPLOAD_SIZE:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": "Request Entity Too Large",
                            "message": f"Request size exceeds maximum of {settings.MAX_UPLOAD_SIZE} bytes"
                        }
                    )
            except ValueError:
                pass

        # Process request
        return await call_next(request)


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with more control
    """

    def __init__(
        self,
        app: ASGIApp,
        allow_origins: list = None,
        allow_methods: list = None,
        allow_headers: list = None,
        expose_headers: list = None,
        allow_credentials: bool = True,
        max_age: int = 3600
    ):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
        self.expose_headers = expose_headers or []
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Handle preflight requests
        if request.method == "OPTIONS":
            return self._preflight_response(request)

        # Process request
        response = await call_next(request)

        # Add CORS headers
        origin = request.headers.get("Origin")
        if origin and self._is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            if self.expose_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        return response

    def _preflight_response(self, request: Request) -> Response:
        """Handle CORS preflight requests"""
        headers = {}

        origin = request.headers.get("Origin")
        if origin and self._is_allowed_origin(origin):
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            headers["Access-Control-Max-Age"] = str(self.max_age)

            if self.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"

        return Response(status_code=200, headers=headers)

    def _is_allowed_origin(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if "*" in self.allow_origins:
            return True
        return origin in self.allow_origins


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Response compression middleware
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if client accepts compression
        accept_encoding = request.headers.get("Accept-Encoding", "")

        # Process request
        response = await call_next(request)

        # Skip compression for small responses or already compressed
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) < 1000:
            return response

        if response.headers.get("Content-Encoding"):
            return response

        # Apply gzip compression if accepted
        if "gzip" in accept_encoding:
            # Note: Actual compression would be handled by GZipMiddleware
            # This is just for demonstration
            response.headers["Vary"] = "Accept-Encoding"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to responses
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        if settings.ENVIRONMENT == "production":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            )

        return response