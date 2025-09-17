# Docker Setup for Novellus Project

This directory contains Docker configuration files for various services used by the Novellus MCP Server project.

## Directory Structure

```
docker/
├── README.md                    # This file
├── postgres/                    # PostgreSQL database setup
│   ├── docker-compose.yml      # PostgreSQL + PgAdmin services
│   ├── Dockerfile.postgres     # Custom PostgreSQL image
│   ├── .env.docker             # Environment variables template
│   └── init-scripts/           # Database initialization scripts
└── mongodb/                     # MongoDB database setup
    ├── docker-compose.yml      # MongoDB + Mongo Express services
    ├── Dockerfile.mongodb      # Custom MongoDB image
    ├── mongod.conf             # MongoDB configuration
    └── init-scripts/           # Database initialization scripts
```

## Services

### PostgreSQL (`postgres/`)

Contains PostgreSQL database configuration with PgAdmin web interface for database management.

### MongoDB (`mongodb/`)

Contains MongoDB database configuration with Mongo Express web interface for database management.

## Quick Start (PostgreSQL)

### 1. Setup Environment

Copy the environment template and configure your settings:

```bash
cd docker/postgres
cp .env.docker .env
```

Edit `.env` file and set your passwords:

```bash
# Change these values
POSTGRES_PASSWORD=your_secure_password
PGADMIN_PASSWORD=your_admin_password
```

### 2. Start Services

Start PostgreSQL and PgAdmin:

```bash
cd docker/postgres
docker-compose up -d
```

### 3. Verify Services

Check that services are running:

```bash
docker-compose ps
```

### 4. Access Services

- **PostgreSQL**: `localhost:5432`
- **PgAdmin**: http://localhost:8080

## Service Details

### PostgreSQL

- **Image**: postgres:15-alpine
- **Port**: 5432 (configurable via POSTGRES_PORT)
- **Database**: novellus (configurable via POSTGRES_DB)
- **User**: novellus_user (configurable via POSTGRES_USER)
- **Data Volume**: `postgres_data` (persistent)

### PgAdmin

- **Image**: dpage/pgadmin4:latest
- **Port**: 8080 (configurable via PGADMIN_PORT)
- **Default Email**: admin@novellus.local
- **Data Volume**: `pgadmin_data` (persistent)

## Database Schema

The initialization script creates the following tables:

1. **demo_users** - Sample user data
2. **products** - Product catalog
3. **orders** - Order records
4. **order_details** - View combining order, user, and product data

## Connecting from MCP Server

Update your main `.env` file (in project root) to connect to the Docker PostgreSQL:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=novellus
POSTGRES_USER=novellus_user
POSTGRES_PASSWORD=your_secure_password
```

## Management Commands (PostgreSQL)

All commands should be run from the `docker/postgres/` directory:

### Start services
```bash
cd docker/postgres
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f postgres
docker-compose logs -f pgadmin
```

### Restart services
```bash
docker-compose restart
```

### Remove everything (including data)
```bash
docker-compose down -v
```

### Access PostgreSQL directly
```bash
docker-compose exec postgres psql -U novellus_user -d novellus
```

## Backup and Restore (PostgreSQL)

### Create backup
```bash
cd docker/postgres
docker-compose exec postgres pg_dump -U novellus_user novellus > backup.sql
```

### Restore backup
```bash
cd docker/postgres
cat backup.sql | docker-compose exec -T postgres psql -U novellus_user novellus
```

## Custom Configuration

### Using Custom Dockerfile

To build with the custom Dockerfile:

```bash
docker-compose -f docker-compose.yml -f docker-compose.custom.yml up -d
```

### Adding Custom Initialization Scripts

Add `.sql` files to the `init-scripts/` directory. They will be executed in alphabetical order when the container starts for the first time.

## Troubleshooting

### Container won't start
- Check if ports 5432 and 8080 are available
- Verify environment variables in `.env` file
- Check logs: `docker-compose logs postgres`

### Connection refused
- Wait for health check to pass: `docker-compose ps`
- Verify PostgreSQL is listening: `docker-compose exec postgres pg_isready`

### Data persistence
- Data is stored in Docker volumes `postgres_data` and `pgadmin_data`
- To reset data: `docker-compose down -v`

## Quick Start (MongoDB)

### 1. Start MongoDB Services

Start MongoDB and Mongo Express:

```bash
cd docker/mongodb
docker-compose up -d
```

### 2. Verify Services

Check that services are running:

```bash
docker-compose ps
```

### 3. Access Services

- **MongoDB**: `localhost:27017`
- **Mongo Express**: http://localhost:8081 (admin/admin123)

## Service Details

### MongoDB

- **Image**: mongo:7.0
- **Port**: 27017
- **Database**: novellus
- **Admin User**: admin/admin123
- **App User**: novellus_user/novellus_password
- **Data Volume**: `mongodb_data` (persistent)

### Mongo Express

- **Image**: mongo-express:1.0.0-alpha
- **Port**: 8081
- **Login**: admin/admin123

## Database Schema (MongoDB)

The initialization script creates the following collections:

1. **demo_users** - Sample user data with skills and departments
2. **demo_products** - Product catalog with pricing and inventory
3. **demo_logs** - Application logs with different levels
4. **user_stats** - Aggregation view for user statistics

## Connecting from MCP Server (MongoDB)

Update your main `.env` file (in project root) to connect to the Docker MongoDB:

```bash
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=novellus
MONGODB_USER=novellus_user
MONGODB_PASSWORD=novellus_password
```

## Management Commands (MongoDB)

All commands should be run from the `docker/mongodb/` directory:

### Start services
```bash
cd docker/mongodb
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f mongodb
docker-compose logs -f mongo-express
```

### Access MongoDB directly
```bash
docker-compose exec mongodb mongo -u admin -p admin123 --authenticationDatabase admin
```

### MongoDB shell with app user
```bash
docker-compose exec mongodb mongo -u novellus_user -p novellus_password novellus
```

## Backup and Restore (MongoDB)

### Create backup
```bash
cd docker/mongodb
docker-compose exec mongodb mongodump --username admin --password admin123 --authenticationDatabase admin --db novellus --out /backup
docker cp novellus-mongodb:/backup ./backup
```

### Restore backup
```bash
cd docker/mongodb
docker cp ./backup novellus-mongodb:/restore
docker-compose exec mongodb mongorestore --username admin --password admin123 --authenticationDatabase admin --db novellus /restore/novellus
```

## Multi-Database Setup

To run both PostgreSQL and MongoDB simultaneously:

### 1. Start both services
```bash
# Start PostgreSQL
cd docker/postgres
docker-compose up -d

# Start MongoDB
cd ../mongodb
docker-compose up -d
```

### 2. Configure environment
Update your main `.env` file to include both databases:

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=novellus
POSTGRES_USER=novellus_user
POSTGRES_PASSWORD=your_secure_password

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=novellus
MONGODB_USER=novellus_user
MONGODB_PASSWORD=novellus_password
```

## Security Notes

- Change default passwords in production
- Consider using Docker secrets for sensitive data
- Restrict network access in production environments
- Regularly update MongoDB and PostgreSQL image versions
- Use authentication in production MongoDB deployments
- Consider enabling SSL/TLS for database connections in production