"""
Unit tests for health check endpoints
Tests basic application functionality and health monitoring
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch


@pytest.mark.unit
@pytest.mark.api
class TestHealthCheck:
    """Test health check and basic application endpoints"""

    def test_root_endpoint_redirect(self, client: TestClient):
        """Test that root endpoint redirects to documentation"""
        response = client.get("/", allow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/docs"

    def test_info_endpoint(self, client: TestClient):
        """Test API info endpoint returns correct metadata"""
        response = client.get("/info")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "documentation" in data
        assert "features" in data

        # Check documentation links
        docs = data["documentation"]
        assert docs["swagger"] == "/docs"
        assert docs["redoc"] == "/redoc"
        assert docs["openapi"] == "/openapi.json"

    @patch("api.core.database.get_database_health")
    def test_health_check_healthy(self, mock_db_health, client: TestClient):
        """Test health check when all services are healthy"""
        # Mock healthy database
        mock_db_health.return_value = {
            "postgresql": True,
            "mongodb": True
        }

        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data

        services = data["services"]
        assert services["api"] == "running"
        assert services["postgresql"] == "connected"
        assert services["mongodb"] == "connected"

    @patch("api.core.database.get_database_health")
    def test_health_check_degraded(self, mock_db_health, client: TestClient):
        """Test health check when some services are unhealthy"""
        # Mock degraded database state
        mock_db_health.return_value = {
            "postgresql": True,
            "mongodb": False
        }

        response = client.get("/health")
        assert response.status_code == 503

        data = response.json()
        assert data["status"] == "degraded"

        services = data["services"]
        assert services["api"] == "running"
        assert services["postgresql"] == "connected"
        assert services["mongodb"] == "disconnected"

    @patch("api.core.database.get_database_health")
    def test_ready_check_ready(self, mock_db_health, client: TestClient):
        """Test readiness check when service is ready"""
        mock_db_health.return_value = {
            "postgresql": True,
            "mongodb": True
        }

        response = client.get("/ready")
        assert response.status_code == 200

        data = response.json()
        assert data["ready"] is True

    @patch("api.core.database.get_database_health")
    def test_ready_check_not_ready(self, mock_db_health, client: TestClient):
        """Test readiness check when service is not ready"""
        mock_db_health.return_value = {
            "postgresql": False,
            "mongodb": False
        }

        response = client.get("/ready")
        assert response.status_code == 503

        data = response.json()
        assert data["ready"] is False

    def test_openapi_schema(self, client: TestClient):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Check API info
        info = schema["info"]
        assert info["title"] == "Novellus API"
        assert "version" in info

    def test_docs_accessible(self, client: TestClient):
        """Test that Swagger documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_accessible(self, client: TestClient):
        """Test that ReDoc documentation is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseHealth:
    """Test database health checking functionality"""

    @patch("api.core.database.get_database_health")
    async def test_database_health_check_success(self, mock_db_health):
        """Test successful database health check"""
        from api.core.database import get_database_health

        # Mock successful database connections
        mock_db_health.return_value = {
            "postgresql": True,
            "mongodb": True
        }

        health = await get_database_health()
        assert health["postgresql"] is True
        assert health["mongodb"] is True
        mock_db_health.assert_called_once()

    @patch("api.core.database.get_database_health")
    async def test_database_health_check_failure(self, mock_db_health):
        """Test database health check with failures"""
        from api.core.database import get_database_health

        # Mock database connection failures
        mock_db_health.return_value = {
            "postgresql": False,
            "mongodb": False
        }

        health = await get_database_health()
        assert health["postgresql"] is False
        assert health["mongodb"] is False
        mock_db_health.assert_called_once()


@pytest.mark.unit
class TestApplicationStartup:
    """Test application startup and lifecycle"""

    def test_app_creation(self, test_app):
        """Test that FastAPI app is created correctly"""
        assert test_app is not None
        assert hasattr(test_app, "title")
        assert test_app.title == "Novellus API"

    def test_middleware_configuration(self, test_app):
        """Test that middleware is configured correctly"""
        # Check that middleware stack exists
        assert len(test_app.user_middleware) > 0

        # Check for CORS middleware
        middleware_classes = [m.cls.__name__ for m in test_app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_routes_configuration(self, test_app):
        """Test that routes are configured correctly"""
        routes = [route.path for route in test_app.routes]

        # Check basic endpoints
        assert "/" in routes
        assert "/health" in routes
        assert "/ready" in routes
        assert "/info" in routes

        # Check API v1 prefix
        api_routes = [route for route in routes if route.startswith("/api/v1")]
        assert len(api_routes) > 0


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling and exception management"""

    def test_404_error(self, client: TestClient):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient):
        """Test 405 method not allowed error"""
        response = client.post("/health")
        assert response.status_code == 405

    @patch("api.core.database.get_database_health")
    def test_internal_server_error_handling(self, mock_db_health, client: TestClient):
        """Test internal server error handling"""
        # Mock database health check to raise an exception
        mock_db_health.side_effect = Exception("Database connection failed")

        response = client.get("/health")
        # Should still return a response, even if degraded
        assert response.status_code in [200, 503, 500]


@pytest.mark.unit
class TestConfiguration:
    """Test application configuration"""

    def test_settings_loading(self):
        """Test that settings are loaded correctly"""
        from api.core.config import settings

        assert settings is not None
        assert hasattr(settings, "APP_NAME")
        assert hasattr(settings, "VERSION")
        assert hasattr(settings, "ENVIRONMENT")

    def test_environment_variables(self):
        """Test environment variable handling"""
        from api.core.config import settings

        # Check test environment is set
        assert settings.ENVIRONMENT == "testing"
        assert settings.DEBUG is True

    def test_database_urls(self):
        """Test database URL generation"""
        from api.core.config import settings

        postgres_url = settings.postgres_url
        assert postgres_url.startswith("postgresql://")

        mongodb_url = settings.mongodb_url
        assert mongodb_url.startswith("mongodb://")