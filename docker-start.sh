#!/bin/bash

# Email Finder Docker Startup Script
echo "🐳 Starting Email Finder with Docker Compose..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "🔧 Building and starting containers..."
echo "📍 Port: 9080"
echo "🌐 Access: http://localhost:9080"
echo ""

# Build and start the application
docker-compose up --build -d

# Wait for the service to be ready
echo "⏳ Waiting for the service to be ready..."
sleep 10

# Check if the service is running
if curl -s http://localhost:9080/ > /dev/null; then
    echo "✅ Email Finder is running successfully!"
    echo ""
    echo "🚀 Available endpoints:"
    echo "   - http://localhost:9080/ (API info)"
    echo "   - http://localhost:9080/verify (single email verification)"
    echo "   - http://localhost:9080/verify-bulk (bulk verification up to 1000 emails)"
    echo "   - http://localhost:9080/stats (performance statistics)"
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    echo "❌ Service failed to start. Check logs with: docker-compose logs"
    exit 1
fi
