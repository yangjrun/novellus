# 🧪 Novellus API Test Suite Documentation

This document provides comprehensive guidance for the Novellus API test automation suite, covering testing strategies, execution methods, and reporting capabilities.

## 📋 Overview

The Novellus API test suite is designed to ensure robust, reliable, and high-performance API functionality through comprehensive automated testing. The suite includes multiple testing layers from unit tests to load testing, with detailed reporting and CI/CD integration.

## 🏗️ Test Architecture

```
tests/
├── conftest.py              # Global test configuration and fixtures
├── unit/                    # Unit tests - isolated component testing
│   ├── test_health_check.py # Health check and basic functionality
│   ├── test_config.py       # Configuration management tests
│   ├── test_middleware.py   # Middleware functionality tests
│   └── test_api_*.py        # API endpoint unit tests
├── integration/             # Integration tests - multiple components
│   ├── test_database_integration.py # Database connectivity and operations
│   └── test_api_integration.py      # API integration workflows
├── e2e/                     # End-to-end tests - complete user workflows
│   └── test_api_workflows.py        # Complete API workflow testing
├── performance/             # Performance and load testing
│   ├── test_load_testing.py         # Performance benchmarks
│   └── locustfile.py                # Locust load testing scenarios
├── utils/                   # Test utilities and helpers
│   ├── test_reporter.py             # Comprehensive test reporting
│   └── test_runner.py               # Test orchestration and execution
└── fixtures/                # Test data and fixtures
```

## 🎯 Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Functions, classes, and modules
- **Characteristics**: Fast, reliable, no external dependencies
- **Coverage**: Aims for >90% code coverage

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and data flow
- **Scope**: Database operations, API integrations, service communication
- **Characteristics**: Moderate execution time, uses test databases
- **Coverage**: Critical integration points and data persistence

### End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows and business scenarios
- **Scope**: Full API workflows from request to response
- **Characteristics**: Slower execution, realistic user scenarios
- **Coverage**: Critical user journeys and cross-module workflows

### Performance Tests (`tests/performance/`)
- **Purpose**: Validate API performance, scalability, and resource usage
- **Scope**: Response times, throughput, memory usage, concurrent requests
- **Characteristics**: Resource-intensive, baseline establishment
- **Coverage**: Performance benchmarks and load testing scenarios

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python 3.10+ and required tools
python --version  # Should be 3.10+
pip install -e .[dev,test,performance]

# Optional: Install database tools for integration tests
# PostgreSQL, MongoDB, Redis
```

### Running Tests

#### Quick Tests (Fast Feedback)
```bash
# Using Make (recommended)
make test-quick

# Using Python script
python scripts/run_tests.py quick

# Using pytest directly
pytest tests/unit/ -m "not slow" --tb=short
```

#### Comprehensive Test Suite
```bash
# All test types
make test-all

# Individual test categories
make test-unit          # Unit tests with coverage
make test-integration   # Integration tests
make test-e2e          # End-to-end tests
make test-performance  # Performance tests
make test-security     # Security scans
```

#### Parallel Execution
```bash
# Run tests in parallel for faster execution
make test-parallel

# Specify number of workers
pytest tests/unit/ -n 4  # 4 parallel workers
```

## 📊 Test Configuration

### Environment Variables
```bash
# Test environment configuration
export ENVIRONMENT=testing
export DEBUG=True
export AUTH_ENABLED=False
export CACHE_ENABLED=False
export MONITORING_ENABLED=False

# Database configuration
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=test_novellus
export MONGODB_HOST=localhost
export MONGODB_PORT=27017
export MONGODB_DB=test_novellus
```

### Pytest Configuration
The test suite uses `pytest.ini` and `pyproject.toml` for configuration:

```ini
# Key pytest settings
[pytest]
testpaths = tests
python_files = test_*.py
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Tests that take more than 5 seconds
    database: Tests requiring database connection
```

## 🔍 Test Execution Examples

### Unit Tests with Coverage
```bash
# Generate comprehensive coverage report
pytest tests/unit/ \
    --cov=src \
    --cov-report=html:reports/htmlcov \
    --cov-report=xml:reports/coverage.xml \
    --cov-report=term-missing

# Open coverage report
open reports/htmlcov/index.html
```

### Integration Tests with Database
```bash
# Setup test databases
make db-setup

# Run integration tests
pytest tests/integration/ \
    --tb=short \
    --html=reports/integration-tests.html

# Cleanup
make db-teardown
```

### Performance Testing
```bash
# Run performance benchmarks
pytest tests/performance/ \
    --benchmark-json=reports/benchmark.json \
    --benchmark-histogram=reports/benchmark-histogram

# Run load tests with Locust
locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users=50 \
    --spawn-rate=5 \
    --run-time=5m \
    --headless \
    --html=reports/load-test-report.html
```

### Security Testing
```bash
# Static security analysis
bandit -r src/ -f json -o reports/bandit.json

# Dependency vulnerability scanning
safety check --json --output reports/safety.json

# Combined security testing
make test-security
```

## 📈 Test Reporting

### Automated Report Generation
The test suite generates multiple report formats:

```bash
# Generate comprehensive HTML report
python tests/utils/test_reporter.py \
    --input reports/ \
    --output reports/ \
    --format all

# Available report formats:
# - HTML: Interactive web report
# - JSON: Machine-readable summary
# - XML: JUnit-compatible format
# - CSV: Performance metrics
```

### Report Types

#### Summary Report (`latest_summary.json`)
```json
{
  "summary": {
    "total_tests": 150,
    "passed": 142,
    "failed": 3,
    "skipped": 5,
    "success_rate_percent": 94.67,
    "total_duration_seconds": 45.2
  },
  "category_breakdown": {
    "unit": {"total": 80, "passed": 78, "failed": 2},
    "integration": {"total": 40, "passed": 39, "failed": 1},
    "e2e": {"total": 30, "passed": 25, "failed": 0, "skipped": 5}
  }
}
```

#### Performance Report
- Response time distributions (P50, P95, P99)
- Throughput metrics (requests per second)
- Resource usage (memory, CPU)
- Load testing results
- Performance trend analysis

## 🐳 Docker Testing

### Build and Run Tests in Docker
```bash
# Build test image
make docker-build

# Run all tests in Docker
make docker-test

# Use docker-compose for complete environment
make docker-up    # Start all services
make test-all     # Run tests
make docker-down  # Stop services
```

### Docker Test Environment
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: test_novellus
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow
The test suite integrates with GitHub Actions for automated testing:

```yaml
# .github/workflows/tests.yml
- Validates code on push/PR
- Runs comprehensive test suite
- Generates coverage reports
- Performs security scans
- Deploys test results to GitHub Pages
```

### Test Automation Features
- **Multi-Python Version Testing**: Tests against Python 3.10, 3.11, 3.12
- **Parallel Execution**: Optimized for CI performance
- **Artifact Management**: Preserves test reports and coverage data
- **PR Comments**: Automatic test result summaries on pull requests
- **Scheduled Testing**: Daily comprehensive test runs

## 🎯 Test Markers and Selection

### Available Test Markers
```bash
# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m "integration and database"  # Integration tests with DB
pytest -m "not slow"              # Skip slow tests
pytest -m "api and not performance"   # API tests excluding performance

# Combine markers for precise selection
pytest -m "(unit or integration) and not slow"
```

### Custom Test Selection
```bash
# Run tests by file pattern
pytest tests/unit/test_api_*.py

# Run tests by function name
pytest -k "test_create_project"

# Run failed tests from last run
pytest --lf

# Run tests until first failure
pytest -x
```

## 🛠️ Development Workflow

### Pre-commit Testing
```bash
# Set up pre-commit hooks
make install-hooks

# Manual pre-commit checks
make pre-commit  # Runs linting, type-checking, and unit tests
```

### Test-Driven Development (TDD)
```bash
# Watch mode for TDD
pytest tests/unit/ -f  # Re-run on file changes

# Quick feedback loop
make test-quick  # Fast unit tests for immediate feedback
```

### Debugging Tests
```bash
# Run with debugger
pytest tests/unit/test_api_projects.py::test_create_project --pdb

# Verbose output
pytest tests/unit/ -v -s  # Show print statements

# Capture and display stdout
pytest tests/unit/ --capture=no
```

## 📋 Performance Benchmarking

### Establishing Baselines
```bash
# Create performance baseline
python scripts/run_tests.py performance --performance-baseline

# Compare against baseline
pytest tests/performance/ --benchmark-compare=baseline.json
```

### Load Testing Scenarios
The Locust configuration supports multiple user behaviors:
- **APIUser**: General API interactions
- **HeavyAPIUser**: Resource-intensive operations
- **ReadOnlyUser**: Read-only operations
- **BurstUser**: Burst traffic patterns

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database status
make db-setup
docker ps  # Verify containers are running

# Reset test databases
make db-teardown
make db-setup
```

#### Import Errors
```bash
# Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Reinstall in development mode
pip install -e .[dev,test]
```

#### Test Discovery Issues
```bash
# Verify test structure
pytest --collect-only

# Check for syntax errors
python -m py_compile tests/unit/test_*.py
```

### Performance Issues
```bash
# Profile test execution
pytest tests/unit/ --durations=10  # Show 10 slowest tests

# Run with minimal output
pytest tests/unit/ -q  # Quiet mode

# Skip slow tests during development
pytest tests/unit/ -m "not slow"
```

## 📚 Best Practices

### Writing Tests
1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: `test_create_project_with_duplicate_name_should_return_409`
3. **Mock External Dependencies**: Use `@patch` for external services
4. **Test Edge Cases**: Invalid inputs, boundary conditions, error scenarios
5. **Keep Tests Independent**: Each test should be able to run in isolation

### Test Data Management
1. **Use Fixtures**: Leverage pytest fixtures for test data
2. **Factory Pattern**: Create data factories for complex objects
3. **Avoid Hardcoded Values**: Use constants or configuration
4. **Clean Up**: Ensure tests clean up after themselves

### Performance Testing
1. **Establish Baselines**: Record performance benchmarks
2. **Test Realistic Scenarios**: Use production-like data volumes
3. **Monitor Resource Usage**: Track memory and CPU consumption
4. **Set Performance Thresholds**: Define acceptable performance limits

## 🔗 Additional Resources

- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Locust Documentation](https://docs.locust.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## 📞 Support

For questions or issues with the test suite:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed error information
4. Include test output and environment details

---

**Happy Testing! 🚀**

Remember: Good tests are the foundation of reliable software. Invest time in writing comprehensive, maintainable tests that give you confidence in your code.