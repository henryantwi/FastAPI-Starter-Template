# Docker Setup with Redis

## Overview
Your Docker Compose setup now includes Redis caching alongside PostgreSQL and your FastAPI application.

## Services Configuration

### 1. PostgreSQL Database (`db`)
- **Image**: `postgres:17.5`
- **Port**: `5442:5432` (mapped to avoid conflicts)
- **Volume**: `postgres_data` for data persistence
- **Health check**: Ensures database is ready before starting the app

### 2. Redis Cache (`redis`)
- **Image**: `redis:7-alpine` (lightweight Alpine Linux)
- **Port**: `6379:6379`
- **Volume**: `redis_data` for data persistence
- **Configuration**:
  - Append-only file (AOF) persistence enabled
  - Max memory: 256MB with LRU eviction policy
  - Health check with `redis-cli ping`

### 3. FastAPI Application (`app`)
- **Build**: Uses `Dockerfile.second`
- **Port**: `8000:8000`
- **Dependencies**: Waits for both `db` and `redis` to be healthy
- **Environment**: Configured to connect to containerized services

## Quick Start

### 1. Start All Services
```bash
docker-compose up -d
```

### 2. Start Individual Services
```bash
# Start only Redis
docker-compose up -d redis

# Start only Database
docker-compose up -d db

# Start only the app (requires db and redis)
docker-compose up -d app
```

### 3. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f redis
docker-compose logs -f db
docker-compose logs -f app
```

### 4. Check Service Status
```bash
docker-compose ps
```

### 5. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: This deletes data)
docker-compose down -v
```

## Environment Variables

### Required for Local Development
Create a `.env` file in the project root with:

```env
# Database Configuration
POSTGRES_SERVER=localhost  # Use 'db' when running in Docker
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=appdb

# Cache Configuration
CACHE_ENABLED=true          # Set to false to disable Redis caching

# Redis Configuration (only needed if CACHE_ENABLED=true)
REDIS_HOST=localhost        # Use 'redis' when running in Docker
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Cache Settings
CACHE_TTL_SECONDS=300
USER_CACHE_TTL_SECONDS=600
STATS_CACHE_TTL_SECONDS=60

# JWT Configuration
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis123

# Environment
ENVIRONMENT=local
```

### Docker Compose Override
The `docker-compose.yml` automatically sets:
- `POSTGRES_SERVER=db`
- `REDIS_HOST=redis`
- `REDIS_PORT=6379`
- `REDIS_DB=0`
- `CACHE_ENABLED=false` (by default, use cache profile to enable)

### Running Without Redis
By default, the Docker Compose setup runs **without Redis** to keep it lightweight:
```bash
# Run without caching (default)
docker-compose up -d

# Run with caching enabled
docker-compose --profile cache up -d
# OR
docker-compose -f docker-compose.yml -f docker-compose.cache.yml up -d
```

## Redis Configuration Details

### Persistence
- **AOF (Append Only File)**: Enabled for data durability
- **Volume**: `redis_data` persists data between container restarts

### Memory Management
- **Max Memory**: 256MB limit
- **Eviction Policy**: `allkeys-lru` (Least Recently Used)
- **Optimal for**: Caching with automatic cleanup of old data

### Health Checks
- **Command**: `redis-cli ping`
- **Interval**: 10 seconds
- **Timeout**: 5 seconds
- **Retries**: 3 attempts

## Development Workflow

### 1. Full Stack Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Run migrations
docker-compose exec app alembic upgrade head

# Create superuser
docker-compose exec app python scripts/create_superuser.py
```

### 2. Local Development (App Only)
```bash
# Start supporting services
docker-compose up -d db redis

# Run app locally
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Testing Cache
```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Check cache keys
docker-compose exec redis redis-cli keys "*"

# Monitor Redis
docker-compose exec redis redis-cli monitor
```

## Monitoring and Debugging

### 1. Service Health
```bash
# Check all services
docker-compose ps

# Check specific service health
docker-compose exec redis redis-cli ping
docker-compose exec db pg_isready -U postgres
```

### 2. Cache Monitoring
```bash
# Redis info
docker-compose exec redis redis-cli info

# Memory usage
docker-compose exec redis redis-cli info memory

# Connected clients
docker-compose exec redis redis-cli info clients
```

### 3. Application Logs
```bash
# Follow app logs
docker-compose logs -f app

# Check startup logs
docker-compose logs app | grep -i redis
```

## Troubleshooting

### Redis Connection Issues
1. **Check Redis is running**:
   ```bash
   docker-compose ps redis
   ```

2. **Test Redis connectivity**:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

3. **Check app can reach Redis**:
   ```bash
   docker-compose exec app python -c "
   from app.core.redis import get_cache_info
   print(get_cache_info())
   "
   ```

### Database Connection Issues
1. **Check PostgreSQL is healthy**:
   ```bash
   docker-compose ps db
   ```

2. **Test database connectivity**:
   ```bash
   docker-compose exec db pg_isready -U postgres
   ```

### Port Conflicts
- **PostgreSQL**: Mapped to `5442` to avoid conflicts with local PostgreSQL
- **Redis**: Uses standard `6379` port
- **FastAPI**: Uses standard `8000` port

## Production Considerations

### 1. Security
- Set Redis password: `REDIS_PASSWORD=your-redis-password`
- Use environment-specific secrets
- Enable Redis AUTH in production

### 2. Performance
- Adjust `maxmemory` based on available RAM
- Consider Redis clustering for high availability
- Monitor cache hit ratios

### 3. Persistence
- AOF is enabled for durability
- Consider RDB snapshots for large datasets
- Regular backup of Redis data volume

### 4. Monitoring
- Use Redis monitoring tools
- Set up alerts for memory usage
- Monitor cache hit/miss ratios

## Useful Commands

```bash
# Restart specific service
docker-compose restart redis

# Rebuild and restart app
docker-compose up -d --build app

# View Redis configuration
docker-compose exec redis redis-cli config get "*"

# Clear all Redis data
docker-compose exec redis redis-cli flushall

# Backup Redis data
docker-compose exec redis redis-cli bgsave
```
