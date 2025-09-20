# Novellus FastAPI Service

A comprehensive RESTful API for novel worldbuilding and content management, built with FastAPI.

## Features

- 📚 **Project & Novel Management**: Organize multiple writing projects
- 🌍 **Worldbuilding Tools**: Manage domains, law chains, and cultural frameworks
- ✍️ **Content Creation**: Batch management and collaborative writing workflows
- 🔄 **Conflict Analysis**: Cross-domain conflicts and story hook generation
- 🤖 **AI Integration**: Claude API integration for content generation
- 📊 **Analytics**: Search, statistics, and reporting capabilities
- 🔐 **Security**: JWT authentication, API keys, and rate limiting
- 📈 **Scalable**: Async operations, caching, and horizontal scaling support

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- MongoDB 7.0+
- Redis 7+ (optional, for caching)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/novellus.git
cd novellus
```

2. **Install dependencies:**
```bash
# Using pip
pip install -r requirements-api.txt

# Using uv (recommended)
uv pip install -r requirements-api.txt
```

3. **Configure environment:**
```bash
cp .env.api.example .env
# Edit .env with your configuration
```

4. **Initialize database:**
```bash
python start_api.py --init-db
```

5. **Start the server:**
```bash
# Development mode (with auto-reload)
python start_api.py --mode dev

# Production mode
python start_api.py --mode prod --workers 4
```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Using Docker Compose

1. **Start all services:**
```bash
docker-compose -f docker-compose.api.yml up -d
```

2. **View logs:**
```bash
docker-compose -f docker-compose.api.yml logs -f api
```

3. **Stop services:**
```bash
docker-compose -f docker-compose.api.yml down
```

### Production Deployment with Monitoring

```bash
# Start with monitoring stack
docker-compose -f docker-compose.api.yml --profile monitoring up -d

# Access services:
# - API: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000
```

## API Documentation

Interactive documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/info` | API information |

### Project Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects` | List projects |
| GET | `/api/v1/projects/{id}` | Get project |
| PUT | `/api/v1/projects/{id}` | Update project |
| DELETE | `/api/v1/projects/{id}` | Delete project |
| GET | `/api/v1/projects/{id}/novels` | Get project novels |
| GET | `/api/v1/projects/{id}/statistics` | Get statistics |

### Novel Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/novels` | Create novel |
| GET | `/api/v1/novels` | List novels |
| GET | `/api/v1/novels/{id}` | Get novel |
| PUT | `/api/v1/novels/{id}` | Update novel |
| DELETE | `/api/v1/novels/{id}` | Delete novel |

### Content Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/content/batches` | Create batch |
| GET | `/api/v1/content/batches` | List batches |
| POST | `/api/v1/content/segments` | Create segment |
| GET | `/api/v1/content/segments` | List segments |

### Worldbuilding

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/worldbuilding/domains` | Create domain |
| POST | `/api/v1/worldbuilding/law-chains` | Create law chain |
| POST | `/api/v1/worldbuilding/characters` | Create character |

### Cultural Framework

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cultural/frameworks` | Create framework |
| POST | `/api/v1/cultural/entities` | Create entity |
| POST | `/api/v1/cultural/relations` | Create relation |

### Search & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/search/content` | Search content |
| GET | `/api/v1/search/statistics` | Get statistics |

## Authentication

### API Key Authentication

Include API key in request headers:
```http
X-API-Key: your-api-key
```

### JWT Authentication

1. **Get token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

2. **Use token:**
```bash
curl http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer <token>"
```

## Rate Limiting

Default limits:
- 100 requests per minute per client
- 10 request burst capacity

Headers returned:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `Retry-After`: Seconds until reset (when limited)

## Configuration

### Environment Variables

Key configuration options:

```env
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=novellus

# Cache
CACHE_ENABLED=true
REDIS_HOST=localhost

# Authentication
AUTH_ENABLED=false
JWT_SECRET_KEY=your-secret-key

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT=100
```

See `.env.api.example` for full configuration options.

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Coverage report
pytest --cov=api --cov-report=html
```

### Code Quality

```bash
# Format code
black src/api/

# Lint code
flake8 src/api/
pylint src/api/

# Type checking
mypy src/api/
```

### Load Testing

```bash
# Using locust
locust -f tests/load/locustfile.py --host http://localhost:8000
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn api.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

### Using systemd

Create `/etc/systemd/system/novellus-api.service`:

```ini
[Unit]
Description=Novellus API
After=network.target

[Service]
Type=forking
User=apiuser
Group=apiuser
WorkingDirectory=/opt/novellus
Environment="PATH=/opt/novellus/venv/bin"
ExecStart=/opt/novellus/venv/bin/gunicorn api.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --daemon
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.novellus.io;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Monitoring

### Prometheus Metrics

Available at `/metrics` when monitoring is enabled:
- Request counts and latencies
- Error rates by endpoint
- Database connection pool stats
- Cache hit/miss rates

### Health Checks

- `/health`: Overall system health
- `/ready`: Service readiness
- Database connectivity status

### Logging

Structured JSON logging with levels:
- DEBUG: Detailed debugging info
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL/MongoDB are running
   - Verify connection credentials in `.env`
   - Ensure databases are initialized

2. **Port Already in Use**
   ```bash
   # Change port in .env or command line
   python start_api.py --port 8001
   ```

3. **Import Errors**
   ```bash
   # Ensure PYTHONPATH includes src/
   export PYTHONPATH=$PYTHONPATH:./src
   ```

4. **Rate Limit Issues**
   - Increase `RATE_LIMIT` in `.env`
   - Disable with `RATE_LIMIT_ENABLED=false`

## Architecture

See [API_ARCHITECTURE.md](docs/API_ARCHITECTURE.md) for detailed architecture documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/novellus/issues)
- Email: support@novellus.io