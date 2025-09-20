"""
API Configuration Settings
Centralized configuration management for the FastAPI application
"""

import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """

    # Application Settings
    APP_NAME: str = "Novellus API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    AUTO_RELOAD: bool = True
    LOG_LEVEL: str = "INFO"
    ACCESS_LOG_ENABLED: bool = True

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    TRUSTED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database Settings (from existing config)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""

    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB: str = "novellus"
    MONGODB_USER: str = ""
    MONGODB_PASSWORD: str = ""

    # Redis Cache Settings
    CACHE_ENABLED: bool = False
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 300  # 5 minutes default

    # Authentication Settings
    AUTH_ENABLED: bool = False
    API_KEY_HEADER: str = "X-API-Key"
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT: int = 100  # requests per minute
    RATE_LIMIT_BURST: int = 10  # burst capacity

    # Claude API Settings (from existing config)
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-opus-20240229"
    CLAUDE_MAX_TOKENS: int = 4000
    CLAUDE_TEMPERATURE: float = 0.8

    # Cost Control Settings
    DAILY_COST_LIMIT: float = 10.0
    MONTHLY_COST_LIMIT: float = 100.0
    MAX_REQUESTS_PER_MINUTE: int = 5
    MAX_CONCURRENT_REQUESTS: int = 3

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [".json", ".txt", ".md", ".csv"]

    # Monitoring Settings
    MONITORING_ENABLED: bool = False
    METRICS_ENDPOINT: str = "/metrics"
    SENTRY_DSN: Optional[str] = None

    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # API Documentation Settings
    DOCS_ENABLED: bool = True
    REDOC_ENABLED: bool = True
    OPENAPI_ENABLED: bool = True

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def postgres_async_url(self) -> str:
        """Get PostgreSQL async connection URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL"""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}?authSource=admin"
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting"""
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, v):
        """Parse trusted hosts from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Use this function to get settings throughout the application
    """
    return Settings()


# Global settings instance
settings = get_settings()


# Environment-specific configurations
def configure_for_environment():
    """Apply environment-specific configurations"""
    if settings.ENVIRONMENT == "production":
        # Production settings
        settings.DEBUG = False
        settings.AUTO_RELOAD = False
        settings.LOG_LEVEL = "WARNING"
        settings.DOCS_ENABLED = False
        settings.AUTH_ENABLED = True
        settings.RATE_LIMIT_ENABLED = True

    elif settings.ENVIRONMENT == "staging":
        # Staging settings
        settings.DEBUG = False
        settings.AUTO_RELOAD = False
        settings.LOG_LEVEL = "INFO"
        settings.AUTH_ENABLED = True

    else:  # development
        # Development settings (already set as defaults)
        pass


# Apply environment configuration
configure_for_environment()