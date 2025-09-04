#!/bin/bash

# Docker Setup Script for FastAPI Server with Redis
# This script helps set up the development environment

set -e

echo "🐳 FastAPI Server Docker Setup"
echo "=============================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    
    cat > .env << 'EOF'
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=appdb

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Cache Settings
CACHE_TTL_SECONDS=300
USER_CACHE_TTL_SECONDS=600
STATS_CACHE_TTL_SECONDS=60

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis123

# Environment
ENVIRONMENT=local

# CORS Origins (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
    
    echo "✅ Created .env file with default values"
    echo "⚠️  Please edit .env file and change default passwords and secret keys!"
else
    echo "✅ .env file already exists"
fi

# Function to wait for service to be healthy
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "healthy"; then
            echo "✅ $service is healthy"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting for $service..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service failed to become healthy after $max_attempts attempts"
    return 1
}

# Start services
echo ""
echo "🚀 Starting Docker services..."

# Start database first
echo "📊 Starting PostgreSQL database..."
docker-compose up -d db

# Wait for database
if wait_for_service db; then
    echo "✅ Database is ready"
else
    echo "❌ Database failed to start"
    exit 1
fi

# Start Redis
echo "🔄 Starting Redis cache..."
docker-compose up -d redis

# Wait for Redis
if wait_for_service redis; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Build and start the application
echo "🔧 Building and starting FastAPI application..."
docker-compose up -d --build app

# Wait a bit for the app to start
sleep 5

# Check if app is running
if docker-compose ps app | grep -q "Up"; then
    echo "✅ FastAPI application is running"
else
    echo "❌ FastAPI application failed to start"
    echo "📋 Check logs with: docker-compose logs app"
    exit 1
fi

# Run database migrations
echo "📊 Running database migrations..."
if docker-compose exec -T app alembic upgrade head; then
    echo "✅ Database migrations completed"
else
    echo "❌ Database migrations failed"
    echo "📋 Check logs with: docker-compose logs app"
fi

# Create superuser
echo "👤 Creating superuser..."
if docker-compose exec -T app python scripts/create_superuser.py; then
    echo "✅ Superuser created successfully"
else
    echo "⚠️  Superuser creation failed (may already exist)"
fi

# Test connections
echo ""
echo "🧪 Testing connections..."

# Test Redis
echo "🔄 Testing Redis connection..."
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis connection successful"
else
    echo "❌ Redis connection failed"
fi

# Test database
echo "📊 Testing database connection..."
if docker-compose exec -T db pg_isready -U postgres | grep -q "accepting connections"; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi

# Show service status
echo ""
echo "📋 Service Status:"
docker-compose ps

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📡 Services are available at:"
echo "   • FastAPI App: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • PostgreSQL: localhost:5442"
echo "   • Redis: localhost:6379"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • Access Redis CLI: docker-compose exec redis redis-cli"
echo "   • Access app shell: docker-compose exec app bash"
echo ""
echo "📚 For more information, see DOCKER_SETUP.md"
