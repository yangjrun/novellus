# Novellus FastAPI Architecture

## Overview

The Novellus FastAPI service provides a RESTful API interface for the novel worldbuilding and content management system, converting the existing MCP server functionality into a scalable web service.

## Architecture Components

### 1. Core Structure

```
src/api/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Configuration management
│   ├── middleware.py      # Custom middleware components
│   ├── dependencies.py    # Dependency injection
│   ├── exceptions.py      # Exception handling
│   ├── database.py        # Database connections
│   ├── cache.py           # Redis cache management
│   └── security.py        # Authentication & authorization
├── v1/
│   ├── router.py          # API v1 main router
│   ├── endpoints/         # API endpoint modules
│   │   ├── projects.py    # Project management
│   │   ├── novels.py      # Novel operations
│   │   ├── content.py     # Content management
│   │   ├── worldbuilding.py # Worldbuilding elements
│   │   ├── cultural.py    # Cultural framework
│   │   ├── conflicts.py   # Conflict analysis
│   │   ├── collaborative.py # Collaborative writing
│   │   ├── search.py      # Search & analytics
│   │   └── admin.py       # Administration
│   └── schemas/           # Pydantic models
│       ├── base.py        # Base schemas
│       ├── project.py     # Project/Novel models
│       ├── content.py     # Content models
│       └── ...           # Other domain models
```

## API Design Principles

### RESTful Resource Design

| Resource | Endpoint Pattern | Operations |
|----------|-----------------|------------|
| Projects | `/api/v1/projects` | CRUD, List, Search |
| Novels | `/api/v1/novels` | CRUD, List, Statistics |
| Content | `/api/v1/content` | Batch management, Segments |
| Worldbuilding | `/api/v1/worldbuilding` | Domains, Law chains, Characters |
| Cultural | `/api/v1/cultural` | Frameworks, Entities, Relations |
| Conflicts | `/api/v1/conflicts` | Matrix, Entities, Hooks, Network |
| Collaborative | `/api/v1/collaborative` | Sessions, Prompts, Analysis |
| Search | `/api/v1/search` | Full-text, Filters, Analytics |

### HTTP Method Mapping

- **GET**: Retrieve resources
- **POST**: Create new resources
- **PUT**: Full update of resources
- **PATCH**: Partial update of resources
- **DELETE**: Remove resources
- **OPTIONS**: CORS preflight

### Status Code Standards

- **200 OK**: Successful GET/PUT/PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Validation errors
- **401 Unauthorized**: Missing/invalid auth
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server errors

## Key Features

### 1. Middleware Stack

```python
# Applied in order:
1. SecurityHeadersMiddleware    # Security headers
2. RequestLoggingMiddleware     # Request/response logging
3. RateLimitMiddleware          # Rate limiting (100 req/min default)
4. AuthenticationMiddleware     # API key/JWT validation
5. RequestValidationMiddleware  # Request validation
6. CORSMiddleware              # CORS handling
7. GZipMiddleware              # Response compression
```

### 2. Authentication & Authorization

**Supported Methods:**
- API Key authentication (header: `X-API-Key`)
- JWT Bearer tokens
- Optional authentication (configurable)

**Authorization Levels:**
- Public endpoints (health, docs)
- Authenticated endpoints
- Admin-only endpoints

### 3. Rate Limiting

**Default Configuration:**
- 100 requests per minute per client
- 10 request burst capacity
- Sliding window algorithm
- Redis-backed for distributed systems

### 4. Caching Strategy

**Cache Layers:**
- Redis cache for frequently accessed data
- 5-minute TTL default
- Cache invalidation on updates
- Optional in-memory fallback

### 5. Response Format

**Standard Success Response:**
```json
{
  "success": true,
  "message": "Operation completed",
  "data": {...},
  "timestamp": "2024-01-20T10:30:00Z"
}
```

**Standard Error Response:**
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Detailed error message",
  "details": {...},
  "error_id": "uuid-for-tracking"
}
```

**Paginated Response:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Performance Optimizations

### 1. Database Connection Pooling
- PostgreSQL: AsyncPG with connection pool
- MongoDB: Motor with connection pool
- Configurable pool sizes

### 2. Async/Await Throughout
- All database operations are async
- Non-blocking I/O operations
- Concurrent request handling

### 3. Response Compression
- Automatic gzip compression
- Configurable minimum size threshold
- Client negotiation via Accept-Encoding

### 4. Query Optimization
- Indexed database fields
- Pagination for large datasets
- Selective field loading

## Deployment Options

### 1. Development Mode
```bash
# Auto-reload enabled
python start_api.py --mode dev
```

### 2. Production Mode
```bash
# Multiple workers, no reload
python start_api.py --mode prod --workers 4
```

### 3. Docker Deployment
```bash
# Full stack with databases
docker-compose -f docker-compose.api.yml up
```

### 4. Kubernetes Deployment
```yaml
# Horizontal pod autoscaling
# Service mesh integration
# ConfigMap for configuration
# Secret for credentials
```

## Monitoring & Observability

### 1. Health Checks
- `/health`: Overall system health
- `/ready`: Readiness probe
- Database connectivity checks

### 2. Metrics Endpoint
- `/metrics`: Prometheus metrics
- Request counts and latencies
- Error rates and types
- Resource utilization

### 3. Logging
- Structured JSON logging
- Request ID tracking
- Error correlation
- Log levels: DEBUG, INFO, WARNING, ERROR

### 4. Distributed Tracing
- OpenTelemetry support (optional)
- Request flow visualization
- Performance bottleneck identification

## API Documentation

### 1. Interactive Documentation
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

### 2. Documentation Features
- Try-it-out functionality
- Request/response examples
- Schema definitions
- Authentication testing

## Security Considerations

### 1. Input Validation
- Pydantic model validation
- SQL injection prevention
- XSS protection
- File upload restrictions

### 2. Security Headers
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Content-Security-Policy

### 3. Rate Limiting
- Per-client limits
- Distributed rate limiting
- Customizable thresholds

### 4. HTTPS Enforcement
- TLS/SSL in production
- HSTS headers
- Certificate validation

## Migration from MCP Server

### Endpoint Mapping

| MCP Tool | FastAPI Endpoint |
|----------|-----------------|
| `test_mcp_connection` | `GET /health` |
| `initialize_database_tool` | `POST /api/v1/admin/database/init` |
| `create_project` | `POST /api/v1/projects` |
| `create_novel` | `POST /api/v1/novels` |
| `list_projects` | `GET /api/v1/projects` |
| `create_content_batch` | `POST /api/v1/content/batches` |
| `create_domain` | `POST /api/v1/worldbuilding/domains` |
| `create_law_chain` | `POST /api/v1/worldbuilding/law-chains` |
| `create_character` | `POST /api/v1/worldbuilding/characters` |
| `create_cultural_framework` | `POST /api/v1/cultural/frameworks` |
| `import_conflict_analysis_data` | `POST /api/v1/conflicts/import` |
| `search_novel_content` | `POST /api/v1/search/content` |

### Data Format Changes
- All UUIDs returned as strings
- Timestamps in ISO 8601 format
- Enums as strings
- Binary data as base64

## Testing Strategy

### 1. Unit Tests
```bash
pytest tests/unit/ --cov=api
```

### 2. Integration Tests
```bash
pytest tests/integration/ --db-test
```

### 3. Load Testing
```bash
locust -f tests/load/locustfile.py
```

### 4. API Contract Testing
```bash
schemathesis run --base-url http://localhost:8000 openapi.json
```

## Configuration Management

### Environment Variables
```env
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=novellus
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret

# Cache
CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# Authentication
AUTH_ENABLED=false
JWT_SECRET_KEY=your-secret-key

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT=100
```

## Scaling Considerations

### Horizontal Scaling
- Stateless application design
- Shared cache (Redis)
- Database connection pooling
- Load balancer compatible

### Vertical Scaling
- Configurable worker processes
- Memory optimization
- CPU utilization monitoring
- Resource limits

### Database Scaling
- Read replicas for queries
- Write master for mutations
- Connection pooling
- Query optimization

## Maintenance & Operations

### Database Migrations
```bash
alembic upgrade head
```

### Backup & Recovery
- Automated database backups
- Point-in-time recovery
- Disaster recovery plan

### Monitoring Alerts
- High error rates
- Slow response times
- Database connection issues
- Memory/CPU thresholds

## Future Enhancements

1. **GraphQL Support**: Alternative query interface
2. **WebSocket Support**: Real-time updates
3. **gRPC Support**: High-performance RPC
4. **Event Streaming**: Kafka/RabbitMQ integration
5. **Multi-tenancy**: Isolated project spaces
6. **API Gateway**: Kong/Traefik integration
7. **Service Mesh**: Istio compatibility
8. **Serverless**: AWS Lambda/Vercel deployment