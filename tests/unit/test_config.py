"""
Unit tests for configuration management
Tests settings, environment variables, and configuration validation
"""

import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError


@pytest.mark.unit
class TestSettings:
    """Test application settings and configuration"""

    def test_default_settings(self):
        """Test default settings values"""
        from api.core.config import Settings

        settings = Settings()
        assert settings.APP_NAME == "Novellus API"
        assert settings.VERSION == "1.0.0"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.DEBUG is True

    def test_environment_override(self):
        """Test environment variable override"""
        from api.core.config import Settings

        with patch.dict(os.environ, {
            "APP_NAME": "Test API",
            "PORT": "9000",
            "DEBUG": "False"
        }):
            settings = Settings()
            assert settings.APP_NAME == "Test API"
            assert settings.PORT == 9000
            assert settings.DEBUG is False

    def test_postgres_url_generation(self):
        """Test PostgreSQL URL generation"""
        from api.core.config import Settings

        settings = Settings(
            POSTGRES_HOST="localhost",
            POSTGRES_PORT=5432,
            POSTGRES_DB="testdb",
            POSTGRES_USER="testuser",
            POSTGRES_PASSWORD="testpass"
        )

        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        assert settings.postgres_url == expected_url

    def test_postgres_async_url_generation(self):
        """Test PostgreSQL async URL generation"""
        from api.core.config import Settings

        settings = Settings(
            POSTGRES_HOST="localhost",
            POSTGRES_PORT=5432,
            POSTGRES_DB="testdb",
            POSTGRES_USER="testuser",
            POSTGRES_PASSWORD="testpass"
        )

        expected_url = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
        assert settings.postgres_async_url == expected_url

    def test_mongodb_url_generation_with_auth(self):
        """Test MongoDB URL generation with authentication"""
        from api.core.config import Settings

        settings = Settings(
            MONGODB_HOST="localhost",
            MONGODB_PORT=27017,
            MONGODB_DB="testdb",
            MONGODB_USER="testuser",
            MONGODB_PASSWORD="testpass"
        )

        expected_url = "mongodb://testuser:testpass@localhost:27017/testdb?authSource=admin"
        assert settings.mongodb_url == expected_url

    def test_mongodb_url_generation_without_auth(self):
        """Test MongoDB URL generation without authentication"""
        from api.core.config import Settings

        settings = Settings(
            MONGODB_HOST="localhost",
            MONGODB_PORT=27017,
            MONGODB_DB="testdb",
            MONGODB_USER="",
            MONGODB_PASSWORD=""
        )

        expected_url = "mongodb://localhost:27017/testdb"
        assert settings.mongodb_url == expected_url

    def test_redis_url_generation_with_password(self):
        """Test Redis URL generation with password"""
        from api.core.config import Settings

        settings = Settings(
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_DB=0,
            REDIS_PASSWORD="testpass"
        )

        expected_url = "redis://:testpass@localhost:6379/0"
        assert settings.redis_url == expected_url

    def test_redis_url_generation_without_password(self):
        """Test Redis URL generation without password"""
        from api.core.config import Settings

        settings = Settings(
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_DB=0,
            REDIS_PASSWORD=None
        )

        expected_url = "redis://localhost:6379/0"
        assert settings.redis_url == expected_url

    def test_environment_validation(self):
        """Test environment setting validation"""
        from api.core.config import Settings

        # Valid environments
        for env in ["development", "staging", "production"]:
            settings = Settings(ENVIRONMENT=env)
            assert settings.ENVIRONMENT == env

        # Invalid environment should raise ValidationError
        with pytest.raises(ValidationError):
            Settings(ENVIRONMENT="invalid")

    def test_cors_origins_parsing_from_string(self):
        """Test CORS origins parsing from comma-separated string"""
        from api.core.config import Settings

        origins_string = "http://localhost:3000,http://localhost:8000,https://example.com"
        settings = Settings(ALLOWED_ORIGINS=origins_string)

        expected_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "https://example.com"
        ]
        assert settings.ALLOWED_ORIGINS == expected_origins

    def test_cors_origins_parsing_from_list(self):
        """Test CORS origins parsing from list"""
        from api.core.config import Settings

        origins_list = ["http://localhost:3000", "http://localhost:8000"]
        settings = Settings(ALLOWED_ORIGINS=origins_list)
        assert settings.ALLOWED_ORIGINS == origins_list

    def test_trusted_hosts_parsing_from_string(self):
        """Test trusted hosts parsing from comma-separated string"""
        from api.core.config import Settings

        hosts_string = "localhost,127.0.0.1,example.com"
        settings = Settings(TRUSTED_HOSTS=hosts_string)

        expected_hosts = ["localhost", "127.0.0.1", "example.com"]
        assert settings.TRUSTED_HOSTS == expected_hosts

    def test_trusted_hosts_parsing_from_list(self):
        """Test trusted hosts parsing from list"""
        from api.core.config import Settings

        hosts_list = ["localhost", "127.0.0.1"]
        settings = Settings(TRUSTED_HOSTS=hosts_list)
        assert settings.TRUSTED_HOSTS == hosts_list


@pytest.mark.unit
class TestEnvironmentConfiguration:
    """Test environment-specific configuration"""

    def test_development_environment_config(self):
        """Test development environment configuration"""
        from api.core.config import Settings

        settings = Settings(ENVIRONMENT="development")
        settings.DEBUG = True
        settings.AUTO_RELOAD = True
        settings.LOG_LEVEL = "INFO"
        settings.DOCS_ENABLED = True

        assert settings.DEBUG is True
        assert settings.AUTO_RELOAD is True
        assert settings.LOG_LEVEL == "INFO"
        assert settings.DOCS_ENABLED is True

    def test_production_environment_config(self):
        """Test production environment configuration"""
        from api.core.config import Settings, configure_for_environment

        # Create settings with production environment
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            settings = Settings()
            # Apply production configuration
            if settings.ENVIRONMENT == "production":
                settings.DEBUG = False
                settings.AUTO_RELOAD = False
                settings.LOG_LEVEL = "WARNING"
                settings.DOCS_ENABLED = False
                settings.AUTH_ENABLED = True
                settings.RATE_LIMIT_ENABLED = True

            assert settings.DEBUG is False
            assert settings.AUTO_RELOAD is False
            assert settings.LOG_LEVEL == "WARNING"
            assert settings.DOCS_ENABLED is False
            assert settings.AUTH_ENABLED is True
            assert settings.RATE_LIMIT_ENABLED is True

    def test_staging_environment_config(self):
        """Test staging environment configuration"""
        from api.core.config import Settings

        # Create settings with staging environment
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            settings = Settings()
            # Apply staging configuration
            if settings.ENVIRONMENT == "staging":
                settings.DEBUG = False
                settings.AUTO_RELOAD = False
                settings.LOG_LEVEL = "INFO"
                settings.AUTH_ENABLED = True

            assert settings.DEBUG is False
            assert settings.AUTO_RELOAD is False
            assert settings.LOG_LEVEL == "INFO"
            assert settings.AUTH_ENABLED is True


@pytest.mark.unit
class TestConfigurationCaching:
    """Test configuration caching and singleton behavior"""

    def test_settings_caching(self):
        """Test that get_settings returns cached instance"""
        from api.core.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same instance due to lru_cache
        assert settings1 is settings2

    def test_global_settings_instance(self):
        """Test global settings instance"""
        from api.core.config import settings, get_settings

        # Global instance should be same as cached function result
        cached_settings = get_settings()
        assert settings.APP_NAME == cached_settings.APP_NAME
        assert settings.VERSION == cached_settings.VERSION


@pytest.mark.unit
class TestSecurityConfiguration:
    """Test security-related configuration"""

    def test_jwt_configuration(self):
        """Test JWT configuration"""
        from api.core.config import Settings

        settings = Settings(
            JWT_SECRET_KEY="test-secret-key",
            JWT_ALGORITHM="HS256",
            JWT_EXPIRATION_MINUTES=60
        )

        assert settings.JWT_SECRET_KEY == "test-secret-key"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRATION_MINUTES == 60

    def test_api_key_configuration(self):
        """Test API key configuration"""
        from api.core.config import Settings

        settings = Settings(
            AUTH_ENABLED=True,
            API_KEY_HEADER="X-API-Key"
        )

        assert settings.AUTH_ENABLED is True
        assert settings.API_KEY_HEADER == "X-API-Key"

    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration"""
        from api.core.config import Settings

        settings = Settings(
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT=100,
            RATE_LIMIT_BURST=10
        )

        assert settings.RATE_LIMIT_ENABLED is True
        assert settings.RATE_LIMIT == 100
        assert settings.RATE_LIMIT_BURST == 10


@pytest.mark.unit
class TestFeatureFlags:
    """Test feature flag configuration"""

    def test_cache_feature_flag(self):
        """Test cache enable/disable"""
        from api.core.config import Settings

        # Cache enabled
        settings = Settings(CACHE_ENABLED=True)
        assert settings.CACHE_ENABLED is True

        # Cache disabled
        settings = Settings(CACHE_ENABLED=False)
        assert settings.CACHE_ENABLED is False

    def test_monitoring_feature_flag(self):
        """Test monitoring enable/disable"""
        from api.core.config import Settings

        # Monitoring enabled
        settings = Settings(MONITORING_ENABLED=True)
        assert settings.MONITORING_ENABLED is True

        # Monitoring disabled
        settings = Settings(MONITORING_ENABLED=False)
        assert settings.MONITORING_ENABLED is False

    def test_documentation_feature_flags(self):
        """Test documentation feature flags"""
        from api.core.config import Settings

        settings = Settings(
            DOCS_ENABLED=True,
            REDOC_ENABLED=True,
            OPENAPI_ENABLED=True
        )

        assert settings.DOCS_ENABLED is True
        assert settings.REDOC_ENABLED is True
        assert settings.OPENAPI_ENABLED is True


@pytest.mark.unit
class TestClaudeConfiguration:
    """Test Claude API configuration"""

    def test_claude_api_settings(self):
        """Test Claude API configuration"""
        from api.core.config import Settings

        settings = Settings(
            CLAUDE_API_KEY="test-api-key",
            CLAUDE_MODEL="claude-3-opus-20240229",
            CLAUDE_MAX_TOKENS=4000,
            CLAUDE_TEMPERATURE=0.8
        )

        assert settings.CLAUDE_API_KEY == "test-api-key"
        assert settings.CLAUDE_MODEL == "claude-3-opus-20240229"
        assert settings.CLAUDE_MAX_TOKENS == 4000
        assert settings.CLAUDE_TEMPERATURE == 0.8

    def test_cost_control_settings(self):
        """Test cost control configuration"""
        from api.core.config import Settings

        settings = Settings(
            DAILY_COST_LIMIT=10.0,
            MONTHLY_COST_LIMIT=100.0,
            MAX_REQUESTS_PER_MINUTE=5,
            MAX_CONCURRENT_REQUESTS=3
        )

        assert settings.DAILY_COST_LIMIT == 10.0
        assert settings.MONTHLY_COST_LIMIT == 100.0
        assert settings.MAX_REQUESTS_PER_MINUTE == 5
        assert settings.MAX_CONCURRENT_REQUESTS == 3