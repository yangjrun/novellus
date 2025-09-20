# Novellus RESTful API

A comprehensive RESTful API for the Novellus novel worldbuilding and content management system, replacing the MCP server with a modern FastAPI implementation.

## 🚀 Features

- **Project Management**: Create and manage multiple novel projects
- **Novel Organization**: Manage novels within projects with versioning
- **Content Management**: Batch-based content creation and segment management
- **Worldbuilding**: Domains, law chains, characters, and cultural frameworks
- **Conflict Analysis**: Cross-domain conflicts, story hooks, and network analysis
- **Collaborative Writing**: AI-assisted writing, prompt generation, and workflows
- **Search & Analytics**: Full-text search, statistics, and trend analysis
- **Administration**: Database management, health monitoring, and system metrics

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- MongoDB 4.4+ (optional)
- Redis (optional, for caching)

## 🔧 Installation

1. Install dependencies:
```bash
pip install -r requirements_api.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Initialize the database:
```bash
python -c "from src.database.database_init import initialize_database; import asyncio; asyncio.run(initialize_database())"
```

## 🏃 Running the API

### Development Mode
```bash
python run_api.py
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

### Production Mode
```bash
# Set environment to production
export ENVIRONMENT=production

# Run with gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧪 Testing

Run the API tests:
```bash
# Basic API test
python test_api.py

# Full test suite
pytest tests/ -v
```

## 📚 API Endpoints

### Core Endpoints
- `GET /` - Root (redirects to docs)
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /info` - API information

### Project Management (`/api/v1/projects`)
- `GET /` - List all projects
- `POST /` - Create new project
- `GET /{project_id}` - Get project details
- `PATCH /{project_id}` - Update project
- `DELETE /{project_id}` - Delete project
- `GET /{project_id}/novels` - List project novels
- `POST /{project_id}/novels` - Create novel in project
- `GET /{project_id}/statistics` - Get project statistics

### Novel Management (`/api/v1/novels`)
- `GET /` - List all novels
- `POST /` - Create new novel
- `GET /{novel_id}` - Get novel details
- `PATCH /{novel_id}` - Update novel
- `DELETE /{novel_id}` - Delete novel
- `GET /{novel_id}/statistics` - Get novel statistics

### Content Management (`/api/v1/content`)
- `POST /batches` - Create content batch
- `GET /batches` - List content batches
- `GET /batches/{batch_id}` - Get batch details
- `POST /batches/series` - Create batch series
- `GET /batches/{novel_id}/dashboard` - Get batch dashboard
- `POST /segments` - Create content segment
- `GET /segments` - List content segments
- `PATCH /segments/{segment_id}` - Update segment

### Worldbuilding (`/api/v1/worldbuilding`)
- `POST /domains` - Create domain
- `GET /domains` - List domains
- `GET /domains/{domain_id}` - Get domain details
- `POST /law-chains` - Create law chain
- `GET /law-chains` - List law chains
- `GET /law-chains/{chain_id}` - Get law chain details
- `POST /law-chains/analyze` - Analyze law chains
- `POST /characters` - Create character
- `GET /characters` - List characters
- `GET /characters/{character_id}` - Get character details

### Cultural Framework (`/api/v1/cultural`)
- `POST /frameworks` - Create cultural framework
- `GET /frameworks` - List cultural frameworks
- `POST /entities` - Create cultural entity
- `GET /entities` - List cultural entities
- `GET /entities/search` - Search cultural entities
- `POST /relations` - Create cultural relation
- `GET /relations/cross-domain` - Get cross-domain relations
- `POST /import` - Import cultural analysis
- `GET /statistics` - Get cultural statistics
- `GET /entity-network` - Get entity network

### Conflict Analysis (`/api/v1/conflicts`)
- `POST /import` - Import conflict data
- `GET /matrix` - Query conflict matrix
- `GET /entities` - Query conflict entities
- `GET /story-hooks` - Query story hooks
- `GET /network-analysis` - Query network analysis
- `GET /statistics` - Get conflict statistics

### Collaborative Writing (`/api/v1/collaborative`)
- `POST /workflow/start` - Start collaborative workflow
- `GET /workflow/{task_id}/status` - Get workflow status
- `POST /prompt/generate` - Generate writing prompt
- `POST /prompt/validate` - Validate generated content
- `POST /batch/create` - Create AI content batch
- `POST /enhance` - Enhance existing content
- `POST /analyze` - Analyze content
- `GET /templates` - Get writing templates
- `POST /feedback` - Submit feedback

### Search & Analytics (`/api/v1/search`)
- `GET /content` - Search novel content
- `GET /statistics/novel/{novel_id}` - Get novel statistics
- `GET /analytics/writing-progress` - Get writing progress
- `GET /analytics/content-distribution` - Get content distribution
- `GET /trending` - Get trending elements
- `GET /suggestions` - Get content suggestions

### Administration (`/api/v1/admin`)
- `GET /health` - System health check
- `POST /database/initialize` - Initialize database
- `GET /database/status` - Database status
- `POST /database/backup` - Backup database
- `POST /database/restore` - Restore database
- `POST /cache/clear` - Clear cache
- `GET /logs` - Get system logs
- `GET /metrics` - Get system metrics
- `POST /maintenance/mode` - Toggle maintenance mode
- `POST /test/connection` - Test external connections

## 🔒 Authentication

The API supports multiple authentication methods:

1. **API Key** (Header: `X-API-Key`)
2. **Bearer Token** (Header: `Authorization: Bearer <token>`)

Configure authentication in `.env`:
```env
AUTH_ENABLED=true
API_KEY_HEADER=X-API-Key
JWT_SECRET_KEY=your-secret-key
```

## ⚙️ Configuration

Key configuration options in `.env`:

```env
# Environment
ENVIRONMENT=development  # development, staging, production

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
AUTO_RELOAD=true

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=novellus

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT=100  # requests per minute

# Cache
CACHE_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📊 Monitoring

### Health Checks
- `/health` - Overall system health
- `/ready` - Service readiness
- `/api/v1/admin/health` - Detailed health status

### Metrics
- Prometheus metrics available at `/metrics` (when enabled)
- Custom metrics at `/api/v1/admin/metrics`

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Access logs with request IDs

## 🚨 Error Handling

The API uses standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_type": "ValidationError",
  "error_id": "uuid",
  "details": [
    {
      "field": "name",
      "message": "Field is required",
      "code": "missing"
    }
  ]
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `503` - Service Unavailable

## 🔄 Migration from MCP Server

This API is a complete replacement for the MCP server. Key differences:

1. **RESTful Design**: Standard HTTP methods and status codes
2. **OpenAPI Documentation**: Auto-generated, interactive docs
3. **Better Performance**: Async operations, connection pooling
4. **Standard Authentication**: JWT tokens, API keys
5. **Rate Limiting**: Built-in request throttling
6. **Monitoring**: Prometheus metrics, health checks

### Migration Steps:

1. Stop the MCP server
2. Install and configure the FastAPI server
3. Update client applications to use REST endpoints
4. Test all functionality
5. Monitor for any issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review the OpenAPI schema at `/openapi.json`