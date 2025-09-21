# Project Structure Guide

## Overview

Novellus is an AI-powered storytelling and worldbuilding platform with a clean, organized project structure following modern Python development practices.

## Directory Structure

```
novellus/
├── docs/                          # Documentation
│   ├── api/                       # API documentation
│   ├── development/               # Development guides
│   └── reports/                   # Analysis and status reports
├── src/                           # Main source code
│   ├── api/                       # FastAPI application
│   ├── analysis/                  # Conflict analysis modules
│   ├── database/                  # Database management
│   ├── ai/                        # AI integration
│   ├── etl/                       # Data processing
│   ├── entrypoints/               # Application entry points
│   ├── processors/                # Content processors
│   └── tools/                     # Utility tools
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── e2e/                       # End-to-end tests
│   ├── performance/               # Performance tests
│   └── fixtures/                  # Test data
├── scripts/                       # Utility scripts
│   ├── database_setup/            # Database initialization
│   ├── demos/                     # Demo applications
│   └── utils/                     # Utility scripts
├── config/                        # Configuration files
├── docker/                        # Docker configurations
└── examples/                      # Usage examples
```

## Key Components

### Source Code (`src/`)

#### API Layer (`src/api/`)
- **Purpose**: FastAPI web application with RESTful endpoints
- **Key Files**:
  - `main.py`: Application bootstrap and configuration
  - `core/`: Infrastructure (config, database, middleware)
  - `v1/`: API version 1 endpoints

#### Analysis Layer (`src/analysis/`)
- **Purpose**: Conflict analysis and cultural framework processing
- **Features**: Multi-domain conflict detection, network analysis, cultural modeling

#### Database Layer (`src/database/`)
- **Purpose**: Data access and management
- **Supports**: PostgreSQL (primary), MongoDB (documents)
- **Features**: Connection pooling, migrations, repository pattern

#### AI Integration (`src/ai/`)
- **Purpose**: Claude API integration and prompt management
- **Features**: Cost tracking, response caching, intelligent content generation

### Scripts (`scripts/`)

#### Database Setup (`scripts/database_setup/`)
- Database initialization scripts
- Migration utilities
- Data import tools

#### Demos (`scripts/demos/`)
- Example applications
- Feature demonstrations
- Testing scenarios

#### Utils (`scripts/utils/`)
- Maintenance scripts
- Data verification tools
- Analysis utilities

### Documentation (`docs/`)

#### API Documentation (`docs/api/`)
- API endpoint documentation
- Schema definitions
- Integration guides

#### Development (`docs/development/`)
- Setup instructions
- Architecture guides
- Testing documentation

#### Reports (`docs/reports/`)
- Analysis reports
- Status updates
- Performance assessments

## Development Workflow

### Dependencies
All dependencies are managed through `pyproject.toml` with optional dependency groups:
- **dev**: Development tools (testing, linting)
- **test**: Testing frameworks and utilities
- **performance**: Performance testing tools

### Testing
```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m performance
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/
```

### API Development
```bash
# Start development server
python src/entrypoints/run_api.py

# Start production server
python src/entrypoints/start_api.py
```

## Configuration

### Environment Variables
- `MCP_SERVER_NAME`: Server identification
- `DATABASE_URL`: PostgreSQL connection string
- `MONGODB_URL`: MongoDB connection string
- `ANTHROPIC_API_KEY`: Claude API access

### Configuration Files
- `pyproject.toml`: Project metadata and dependencies
- `docker-compose.api.yml`: API service configuration
- `config/ai_models_config.yaml`: AI model settings

## Best Practices

### File Organization
1. **Domain-driven structure**: Related functionality grouped together
2. **Clear separation**: API, business logic, and data access layers
3. **Consistent naming**: Descriptive, standardized file names

### Development
1. **Test-driven**: Write tests for new functionality
2. **Type hints**: Use Python type annotations
3. **Documentation**: Keep docs updated with code changes

### Deployment
1. **Environment isolation**: Use virtual environments
2. **Configuration management**: Environment-specific settings
3. **Monitoring**: Prometheus metrics and logging

## Migration Notes

This structure was reorganized from a flat file structure to improve:
- **Discoverability**: Easier to find related code
- **Maintainability**: Clear boundaries between components
- **Scalability**: Room for growth without clutter
- **Onboarding**: New developers can navigate quickly

For legacy file locations, see git history or contact the development team.