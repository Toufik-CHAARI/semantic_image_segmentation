#!/bin/bash

# Test Docker Script for Semantic Image Segmentation API
# This script tests the Docker containers locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="semantic-segmentation-api"
TEST_IMAGE_NAME="semantic-segmentation-test"
CONTAINER_NAME="semantic-segmentation-test-container"
PORT=8000

echo -e "${BLUE}🧪 Testing Docker containers...${NC}"

# Check if images exist
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Main image not found. Building...${NC}"
    ./scripts/build-local.sh
fi

if ! docker image inspect "$TEST_IMAGE_NAME" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Test image not found. Building...${NC}"
    ./scripts/build-local.sh
fi

# Stop and remove existing test container
echo -e "${BLUE}🔄 Cleaning up existing test container...${NC}"
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Run the test container
echo -e "${BLUE}🚀 Starting test container...${NC}"
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$PORT:$PORT" \
    "$IMAGE_NAME"

# Wait for the application to start
echo -e "${BLUE}⏳ Waiting for application to start...${NC}"
sleep 15

# Test health endpoint
echo -e "${BLUE}🏥 Testing health endpoint...${NC}"
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo -e "${YELLOW}   Container logs:${NC}"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Test info endpoint
echo -e "${BLUE}ℹ️  Testing info endpoint...${NC}"
INFO_RESPONSE=$(curl -s http://localhost:$PORT/info)
echo "$INFO_RESPONSE" | jq . 2>/dev/null || echo "$INFO_RESPONSE"

# Test root endpoint
echo -e "${BLUE}🏠 Testing root endpoint...${NC}"
ROOT_RESPONSE=$(curl -s http://localhost:$PORT/)
echo "$ROOT_RESPONSE"

# Test segmentation endpoint with sample image
echo -e "${BLUE}🖼️  Testing segmentation endpoint...${NC}"
if [ -f "local_readme/frankfurt_000000_000294_leftImg8bit.png" ]; then
    echo -e "${BLUE}   Using sample image: frankfurt_000000_000294_leftImg8bit.png${NC}"
    curl -X POST http://localhost:$PORT/api/segment \
        -H "Content-Type: multipart/form-data" \
        -F "file=@local_readme/frankfurt_000000_000294_leftImg8bit.png" \
        --output test_segmented_image.png
    
    if [ -f "test_segmented_image.png" ]; then
        FILE_SIZE=$(stat -f%z test_segmented_image.png 2>/dev/null || stat -c%s test_segmented_image.png 2>/dev/null)
        if [ "$FILE_SIZE" -gt 1000 ]; then
            echo -e "${GREEN}✅ Segmentation test passed (file size: ${FILE_SIZE} bytes)${NC}"
        else
            echo -e "${YELLOW}⚠️  Segmentation returned small file (${FILE_SIZE} bytes) - might be an error${NC}"
            cat test_segmented_image.png
        fi
    else
        echo -e "${RED}❌ Segmentation test failed - no output file${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Sample image not found, skipping segmentation test${NC}"
fi

# Run unit tests in test container
echo -e "${BLUE}🧪 Running unit tests...${NC}"
docker run --rm "$TEST_IMAGE_NAME"

echo -e "${GREEN}🎉 All tests completed!${NC}"

# Show container status
echo -e "${BLUE}📦 Container status:${NC}"
docker ps --filter "name=$CONTAINER_NAME"

# Cleanup
echo -e "${BLUE}🧹 Cleaning up...${NC}"
docker stop "$CONTAINER_NAME"
docker rm "$CONTAINER_NAME"

echo -e "${GREEN}✅ Testing completed successfully!${NC}" 