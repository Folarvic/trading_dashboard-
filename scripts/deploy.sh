#!/bin/bash
# Deployment script for AI Trading Dashboard

set -e

echo "🚀 Deploying AI Trading Dashboard..."

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required"; exit 1; }

# Create environment file if not exists
if [ ! -f .env ]; then
    echo "⚠️  .env not found, copying from example"
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys"
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🗄️  Initializing database..."
docker-compose up -d postgres redis
sleep 5  # Wait for postgres to start

# Run migrations
docker-compose exec postgres psql -U trading -d trading -f /docker-entrypoint-initdb.d/schema.sql

echo "🚀 Starting all services..."
docker-compose up -d

echo "✅ Deployment complete!"
echo ""
echo "Dashboard: http://localhost"
echo "API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "View logs: docker-compose logs -f"
