"""
Test configuration and fixtures
Shared test setup and utilities for the test suite
"""

import os
import sys
import asyncio
import pytest
import warnings
from pathlib import Path
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import AsyncMock, MagicMock

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Suppress warnings during tests
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

# Test environment variables
os.environ.update({
    "ENVIRONMENT": "testing",
    "DEBUG": "True",
    "AUTH_ENABLED": "False",
    "CACHE_ENABLED": "False",
    "MONITORING_ENABLED": "False",
    "POSTGRES_DB": "test_novellus",
    "MONGODB_DB": "test_novellus",
})

from api.main import app
from api.core.config import settings
from api.core.database import get_database_health


# Test configuration
class TestConfig:
    """Test configuration constants"""
    API_BASE_URL = f"http://testserver/api/v1"
    TIMEOUT = 30
    MAX_RETRIES = 3


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    """Create test FastAPI application"""
    # Override database settings for testing
    settings.POSTGRES_DB = "test_novellus"
    settings.MONGODB_DB = "test_novellus"
    return app


@pytest.fixture(scope="function")
def client(test_app) -> Generator[TestClient, None, None]:
    """Create test client for FastAPI application"""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(test_app) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async test client for FastAPI application"""
    async with httpx.AsyncClient(
        app=test_app,
        base_url="http://testserver",
        timeout=TestConfig.TIMEOUT
    ) as client:
        yield client


@pytest.fixture(scope="session")
def test_database_url():
    """Test database URL"""
    return "sqlite:///:memory:"


@pytest.fixture(scope="function")
def mock_postgres_db():
    """Mock PostgreSQL database"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables (would normally use Alembic migrations)
    # For now, we'll mock this
    return TestingSessionLocal


@pytest.fixture(scope="function")
def mock_mongodb():
    """Mock MongoDB database"""
    return MagicMock()


@pytest.fixture(scope="function")
def mock_redis():
    """Mock Redis cache"""
    return MagicMock()


@pytest.fixture(scope="function")
def mock_claude_client():
    """Mock Claude API client"""
    mock_client = AsyncMock()
    mock_client.messages.create.return_value = AsyncMock(
        content=[MagicMock(text="Mock Claude response")]
    )
    return mock_client


@pytest.fixture(scope="function")
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Novel Project",
        "description": "A test novel project for automated testing",
        "metadata": {
            "genre": "Science Fiction",
            "target_audience": "Adult",
            "estimated_length": 80000
        }
    }


@pytest.fixture(scope="function")
def sample_novel_data():
    """Sample novel data for testing"""
    return {
        "title": "Test Novel",
        "description": "A test novel for automated testing",
        "metadata": {
            "author": "Test Author",
            "genre": "Science Fiction",
            "target_word_count": 80000,
            "status": "planning"
        }
    }


@pytest.fixture(scope="function")
def sample_content_data():
    """Sample content data for testing"""
    return {
        "type": "chapter",
        "title": "Test Chapter",
        "content": "This is test content for automated testing.",
        "metadata": {
            "word_count": 50,
            "chapter_number": 1,
            "status": "draft"
        }
    }


@pytest.fixture(scope="function")
def sample_worldbuilding_data():
    """Sample worldbuilding data for testing"""
    return {
        "domain_name": "Test Domain",
        "domain_type": "technology",
        "description": "A test domain for automated testing",
        "law_chains": [
            {
                "name": "Test Law Chain",
                "description": "A test law chain",
                "rules": ["Rule 1", "Rule 2"]
            }
        ]
    }


@pytest.fixture(scope="function")
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture(scope="function")
def api_key_headers():
    """Mock API key headers"""
    return {"X-API-Key": "test-api-key"}


# Database health check fixture
@pytest.fixture(scope="function")
async def database_health():
    """Check database health status"""
    return await get_database_health()


# Performance testing fixtures
@pytest.fixture(scope="function")
def performance_config():
    """Performance test configuration"""
    return {
        "max_response_time": 1.0,  # seconds
        "max_memory_usage": 100 * 1024 * 1024,  # 100MB
        "concurrent_users": 10,
        "test_duration": 30,  # seconds
    }


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test"""
    yield
    # Add cleanup logic here if needed
    pass


# Custom markers for test organization
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "database: Tests requiring database")
    config.addinivalue_line("markers", "api: API endpoint tests")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    for item in items:
        # Add markers based on test location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)

        # Mark database tests
        if any(keyword in item.name.lower() for keyword in ["database", "db", "postgres", "mongo"]):
            item.add_marker(pytest.mark.database)

        # Mark API tests
        if any(keyword in item.name.lower() for keyword in ["api", "endpoint", "route"]):
            item.add_marker(pytest.mark.api)


# Test session hooks
def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    print("\n" + "="*50)
    print("🚀 Starting Novellus API Test Suite")
    print("="*50)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    print("\n" + "="*50)
    print(f"✅ Test Suite Complete - Exit Status: {exitstatus}")
    print("="*50)


# Async test utilities
async def wait_for_condition(condition_func, timeout=5, interval=0.1):
    """Wait for a condition to be true"""
    elapsed = 0
    while elapsed < timeout:
        if await condition_func():
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False


# Test utilities class
class TestUtils:
    """Utility functions for testing"""

    @staticmethod
    def assert_response_structure(response_data: Dict[str, Any], expected_keys: list):
        """Assert that response has expected structure"""
        for key in expected_keys:
            assert key in response_data, f"Missing key: {key}"

    @staticmethod
    def assert_error_response(response_data: Dict[str, Any]):
        """Assert that response is a valid error response"""
        assert "error" in response_data
        assert "message" in response_data

    @staticmethod
    def assert_success_response(response_data: Dict[str, Any]):
        """Assert that response is a valid success response"""
        assert "data" in response_data or "message" in response_data
        assert response_data.get("success", True)


# Export test utilities
@pytest.fixture(scope="session")
def test_utils():
    """Test utility functions"""
    return TestUtils