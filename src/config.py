"""
Configuration settings for the MCP server.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class MCPConfig:
    """Configuration class for MCP server settings."""

    def __init__(self):
        self.server_name = os.getenv('MCP_SERVER_NAME', 'Novellus MCP Server')

        # Claude API configuration
        self.claude_api_key = os.getenv('CLAUDE_API_KEY', '')
        self.claude_model = os.getenv('CLAUDE_MODEL', 'claude-3-opus-20240229')
        self.claude_max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '4000'))
        self.claude_temperature = float(os.getenv('CLAUDE_TEMPERATURE', '0.8'))

        # Cost control configuration
        self.daily_cost_limit = float(os.getenv('DAILY_COST_LIMIT', '10.0'))
        self.monthly_cost_limit = float(os.getenv('MONTHLY_COST_LIMIT', '100.0'))

        # Rate limiting configuration
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '5'))
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))

        # PostgreSQL configuration
        self.postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.postgres_port = int(os.getenv('POSTGRES_PORT', '5432'))
        self.postgres_db = os.getenv('POSTGRES_DB', 'postgres')
        self.postgres_user = os.getenv('POSTGRES_USER', 'postgres')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD', '')

        # MongoDB configuration
        self.mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
        self.mongodb_port = int(os.getenv('MONGODB_PORT', '27017'))
        self.mongodb_db = os.getenv('MONGODB_DB', 'novellus')
        self.mongodb_user = os.getenv('MONGODB_USER', '')
        self.mongodb_password = os.getenv('MONGODB_PASSWORD', '')

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def postgres_async_url(self) -> str:
        """Get PostgreSQL async connection URL."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.mongodb_user and self.mongodb_password:
            return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}?authSource=admin"
        else:
            return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"

    @property
    def has_claude_api_key(self) -> bool:
        """Check if Claude API key is configured."""
        return bool(self.claude_api_key)

    @property
    def database_url(self) -> str:
        """Get database URL for SQLite or other databases."""
        return os.getenv('DATABASE_URL', 'sqlite:///./novellus.db')

# Global configuration instance
config = MCPConfig()