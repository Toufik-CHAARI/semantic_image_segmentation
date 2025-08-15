#!/bin/bash

# Test script for Docker containers
set -e

echo "🧪 Testing Docker containers..."

# Test production container
echo "📦 Testing production container..."
docker build -t semantic-image-segmentation-api:test .

# Start container
docker run -d --name test-prod -p 8000:8000 semantic-image-segmentation-api:test

# Wait for startup
sleep 15

# Test endpoints
echo "🔍 Testing endpoints..."

# Test root endpoint
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Root endpoint works"
else
    echo "❌ Root endpoint failed"
    docker logs test-prod
    exit 1
fi

# Test health endpoint
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Health endpoint works"
else
    echo "❌ Health endpoint failed"
    docker logs test-prod
    exit 1
fi

# Test info endpoint
if curl -f http://localhost:8000/info > /dev/null 2>&1; then
    echo "✅ Info endpoint works"
else
    echo "❌ Info endpoint failed"
    docker logs test-prod
    exit 1
fi

# Test segment endpoint with test image
if curl -X POST http://localhost:8000/api/segment \
    -H "Content-Type: multipart/form-data" \
    -F "file=@test_image.png" > /dev/null 2>&1; then
    echo "✅ Segment endpoint works"
else
    echo "❌ Segment endpoint failed"
    docker logs test-prod
    exit 1
fi

# Cleanup
docker stop test-prod
docker rm test-prod
docker rmi semantic-image-segmentation-api:test

echo "�� All tests passed!" 