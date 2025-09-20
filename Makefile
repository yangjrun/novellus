# Novellus API Test Automation Makefile
# Provides convenient commands for running tests and development tasks

.PHONY: help test test-unit test-integration test-e2e test-performance test-security test-all
.PHONY: coverage lint format type-check deps deps-dev deps-test
.PHONY: docker-test docker-build docker-up docker-down
.PHONY: report clean setup

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project configuration
PROJECT_NAME := novellus-api
PYTHON := python3
PIP := pip3
PYTEST := pytest
VENV_NAME := venv
REPORTS_DIR := reports

help: ## Show this help message
	@echo "$(BLUE)Novellus API Test Automation$(NC)"
	@echo "=============================="
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
setup: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	./$(VENV_NAME)/bin/pip install --upgrade pip
	./$(VENV_NAME)/bin/pip install -e .[dev,test,performance]
	@echo "$(GREEN)✅ Development environment ready$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV_NAME)/bin/activate$(NC)"

deps: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install -e .

deps-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -e .[dev]

deps-test: ## Install test dependencies
	@echo "$(BLUE)Installing test dependencies...$(NC)"
	$(PIP) install -e .[test,performance]

# Code quality
lint: ## Run code linting
	@echo "$(BLUE)Running code linting...$(NC)"
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	isort --check-only --diff src/ tests/
	black --check src/ tests/
	@echo "$(GREEN)✅ Linting passed$(NC)"

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	isort src/ tests/
	black src/ tests/
	@echo "$(GREEN)✅ Code formatted$(NC)"

type-check: ## Run type checking
	@echo "$(BLUE)Running type checking...$(NC)"
	mypy src/ --ignore-missing-imports
	@echo "$(GREEN)✅ Type checking passed$(NC)"

# Testing
test: test-unit ## Run default tests (unit tests)

test-quick: ## Run quick tests for rapid feedback
	@echo "$(BLUE)Running quick tests...$(NC)"
	$(PYTHON) scripts/run_tests.py quick
	@echo "$(GREEN)✅ Quick tests completed$(NC)"

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) tests/unit/ \
		-v \
		--tb=short \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html:$(REPORTS_DIR)/htmlcov \
		--cov-report=xml:$(REPORTS_DIR)/coverage.xml \
		--junitxml=$(REPORTS_DIR)/unit-tests.xml \
		--html=$(REPORTS_DIR)/unit-tests.html \
		--self-contained-html
	@echo "$(GREEN)✅ Unit tests completed$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) tests/integration/ \
		-v \
		--tb=short \
		--junitxml=$(REPORTS_DIR)/integration-tests.xml \
		--html=$(REPORTS_DIR)/integration-tests.html \
		--self-contained-html
	@echo "$(GREEN)✅ Integration tests completed$(NC)"

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running end-to-end tests...$(NC)"
	$(PYTEST) tests/e2e/ \
		-v \
		--tb=short \
		--junitxml=$(REPORTS_DIR)/e2e-tests.xml \
		--html=$(REPORTS_DIR)/e2e-tests.html \
		--self-contained-html
	@echo "$(GREEN)✅ End-to-end tests completed$(NC)"

test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	$(PYTHON) scripts/run_tests.py performance
	@echo "$(GREEN)✅ Performance tests completed$(NC)"

test-security: ## Run security tests
	@echo "$(BLUE)Running security tests...$(NC)"
	$(PYTHON) scripts/run_tests.py security
	@echo "$(GREEN)✅ Security tests completed$(NC)"

test-load: ## Run load tests with Locust
	@echo "$(BLUE)Running load tests...$(NC)"
	locust -f tests/performance/locustfile.py \
		--host=http://localhost:8000 \
		--users=20 \
		--spawn-rate=2 \
		--run-time=2m \
		--headless \
		--html=$(REPORTS_DIR)/load-test-report.html \
		--csv=$(REPORTS_DIR)/load-test
	@echo "$(GREEN)✅ Load tests completed$(NC)"

test-all: ## Run all test types
	@echo "$(BLUE)Running comprehensive test suite...$(NC)"
	$(PYTHON) scripts/run_tests.py all
	@echo "$(GREEN)✅ All tests completed$(NC)"

test-parallel: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	$(PYTEST) tests/unit/ tests/integration/ \
		-v \
		--tb=short \
		-n auto \
		--cov=src \
		--cov-report=html:$(REPORTS_DIR)/htmlcov \
		--junitxml=$(REPORTS_DIR)/parallel-tests.xml
	@echo "$(GREEN)✅ Parallel tests completed$(NC)"

# Coverage analysis
coverage: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	$(PYTEST) tests/ \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html:$(REPORTS_DIR)/htmlcov \
		--cov-report=xml:$(REPORTS_DIR)/coverage.xml
	@echo "$(GREEN)✅ Coverage report generated$(NC)"
	@echo "$(YELLOW)Open $(REPORTS_DIR)/htmlcov/index.html to view report$(NC)"

coverage-open: coverage ## Generate and open coverage report
	@command -v open >/dev/null 2>&1 && open $(REPORTS_DIR)/htmlcov/index.html || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open $(REPORTS_DIR)/htmlcov/index.html || \
	echo "$(YELLOW)Open $(REPORTS_DIR)/htmlcov/index.html manually$(NC)"

# Database management
db-setup: ## Setup test databases
	@echo "$(BLUE)Setting up test databases...$(NC)"
	-docker run --name test-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=test_novellus -p 5432:5432 -d postgres:15
	-docker run --name test-mongodb -p 27017:27017 -d mongo:7.0
	@echo "$(GREEN)✅ Test databases started$(NC)"

db-teardown: ## Teardown test databases
	@echo "$(BLUE)Tearing down test databases...$(NC)"
	-docker stop test-postgres test-mongodb
	-docker rm test-postgres test-mongodb
	@echo "$(GREEN)✅ Test databases stopped$(NC)"

# Docker operations
docker-build: ## Build Docker test image
	@echo "$(BLUE)Building Docker test image...$(NC)"
	docker build -f Dockerfile.test -t $(PROJECT_NAME)-test .
	@echo "$(GREEN)✅ Docker image built$(NC)"

docker-test: docker-build ## Run tests in Docker
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	docker run --rm -v $(PWD)/$(REPORTS_DIR):/app/$(REPORTS_DIR) $(PROJECT_NAME)-test
	@echo "$(GREEN)✅ Docker tests completed$(NC)"

docker-up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting services with docker-compose...$(NC)"
	docker-compose -f docker-compose.test.yml up -d
	@echo "$(GREEN)✅ Services started$(NC)"

docker-down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose -f docker-compose.test.yml down
	@echo "$(GREEN)✅ Services stopped$(NC)"

# API server management
server-start: ## Start API server for testing
	@echo "$(BLUE)Starting API server...$(NC)"
	cd src && $(PYTHON) -m api.main &
	@echo "$(GREEN)✅ API server started at http://localhost:8000$(NC)"

server-stop: ## Stop API server
	@echo "$(BLUE)Stopping API server...$(NC)"
	pkill -f "python -m api.main" || true
	@echo "$(GREEN)✅ API server stopped$(NC)"

# Reporting
report: ## Generate comprehensive test report
	@echo "$(BLUE)Generating comprehensive test report...$(NC)"
	$(PYTHON) tests/utils/test_reporter.py --input $(REPORTS_DIR) --output $(REPORTS_DIR) --format all
	@echo "$(GREEN)✅ Report generated$(NC)"
	@echo "$(YELLOW)Open $(REPORTS_DIR)/latest_report.html to view$(NC)"

report-open: report ## Generate and open test report
	@command -v open >/dev/null 2>&1 && open $(REPORTS_DIR)/latest_report.html || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open $(REPORTS_DIR)/latest_report.html || \
	echo "$(YELLOW)Open $(REPORTS_DIR)/latest_report.html manually$(NC)"

# Benchmarking
benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	$(PYTEST) tests/performance/ \
		--benchmark-only \
		--benchmark-json=$(REPORTS_DIR)/benchmark.json \
		--benchmark-histogram=$(REPORTS_DIR)/benchmark-histogram
	@echo "$(GREEN)✅ Benchmarks completed$(NC)"

# Cleanup
clean: ## Clean generated files and caches
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	rm -rf $(REPORTS_DIR)/*
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf **/__pycache__/
	rm -rf **/*.pyc
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

clean-all: clean ## Clean everything including virtual environment
	@echo "$(BLUE)Cleaning everything...$(NC)"
	rm -rf $(VENV_NAME)/
	@echo "$(GREEN)✅ Full cleanup completed$(NC)"

# CI/CD helpers
ci-test: ## Run tests in CI mode
	@echo "$(BLUE)Running tests in CI mode...$(NC)"
	$(PYTEST) tests/ \
		-v \
		--tb=short \
		--strict-markers \
		--cov=src \
		--cov-report=xml:$(REPORTS_DIR)/coverage.xml \
		--cov-report=term \
		--junitxml=$(REPORTS_DIR)/test-results.xml

pre-commit: lint type-check test-unit ## Run pre-commit checks
	@echo "$(GREEN)✅ Pre-commit checks passed$(NC)"

# Development helpers
dev-setup: setup db-setup ## Complete development setup
	@echo "$(GREEN)✅ Development environment fully configured$(NC)"

dev-test: test-unit test-integration ## Run development tests
	@echo "$(GREEN)✅ Development tests completed$(NC)"

watch-tests: ## Watch for changes and run tests
	@echo "$(BLUE)Watching for changes...$(NC)"
	$(PYTEST) tests/unit/ \
		-v \
		--tb=short \
		-f

# Environment information
info: ## Show environment information
	@echo "$(BLUE)Environment Information$(NC)"
	@echo "======================="
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Pytest: $(shell $(PYTEST) --version)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Reports: $(REPORTS_DIR)/"
	@echo ""
	@echo "$(BLUE)Available test commands:$(NC)"
	@echo "  make test-quick     - Quick unit tests"
	@echo "  make test-unit      - Unit tests with coverage"
	@echo "  make test-integration - Integration tests"
	@echo "  make test-e2e       - End-to-end tests"
	@echo "  make test-performance - Performance tests"
	@echo "  make test-all       - All test types"

# Install pre-commit hooks
install-hooks: ## Install git pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✅ Pre-commit hooks installed$(NC)"