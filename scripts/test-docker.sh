#!/bin/bash

# Test Docker Container Script
set -e

echo "🐳 Building Docker test image..."
docker build -f Dockerfile.test -t sentiment-analysis-api:test .

echo "🚀 Starting container..."
docker run -d --name test-container -p 8000:8000 sentiment-analysis-api:test

echo "⏳ Waiting for application to start..."
sleep 20

echo "🔍 Checking if container is running..."
if ! docker ps | grep -q test-container; then
    echo "❌ Container is not running!"
    echo "📋 Container logs:"
    docker logs test-container
    exit 1
fi

echo "✅ Container is running"

echo "🏥 Testing health endpoint..."
if curl -f http://localhost:8000/health; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "📋 Container logs:"
    docker logs test-container
    exit 1
fi

echo "ℹ️  Testing info endpoint..."
if curl -f http://localhost:8000/info; then
    echo "✅ Info check passed"
else
    echo "❌ Info check failed"
    echo "📋 Container logs:"
    docker logs test-container
    exit 1
fi

echo "🧠 Testing sentiment endpoint..."
if curl -X POST http://localhost:8000/predict-sentiment/ \
    -H "Content-Type: application/json" \
    -d '{"text": "I really enjoyed this movie!"}'; then
    echo "✅ Sentiment check passed"
else
    echo "❌ Sentiment check failed"
    echo "📋 Container logs:"
    docker logs test-container
    exit 1
fi

echo "🧹 Cleaning up..."
docker stop test-container
docker rm test-container
docker rmi sentiment-analysis-api:test

echo "�� All tests passed!" 