#!/bin/bash

# EC2 Deployment Script for Semantic Image Segmentation API
# This script builds and deploys the application to EC2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="semantic-segmentation-api"
CONTAINER_NAME="semantic-segmentation-container"
PORT=8000

echo -e "${BLUE}🚀 Starting EC2 deployment for Semantic Image Segmentation API${NC}"

# Check if AWS credentials are available
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}⚠️  AWS credentials not found in environment variables${NC}"
    echo -e "${YELLOW}   Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY${NC}"
    exit 1
fi

# Build the Docker image
echo -e "${BLUE}📦 Building Docker image...${NC}"
docker build \
    --build-arg AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    --build-arg AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    --build-arg AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-eu-west-3}" \
    -t "$IMAGE_NAME" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Stop and remove existing container if it exists
echo -e "${BLUE}🔄 Stopping existing container...${NC}"
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Run the new container
echo -e "${BLUE}🚀 Starting container...${NC}"
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$PORT:$PORT" \
    --restart unless-stopped \
    "$IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
fi

# Wait for the application to start
echo -e "${BLUE}⏳ Waiting for application to start...${NC}"
sleep 10

# Test the health endpoint
echo -e "${BLUE}🏥 Testing health endpoint...${NC}"
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo -e "${YELLOW}   Container logs:${NC}"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Test the info endpoint
echo -e "${BLUE}ℹ️  Testing info endpoint...${NC}"
if curl -f http://localhost:$PORT/info > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Info endpoint working${NC}"
else
    echo -e "${RED}❌ Info endpoint failed${NC}"
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📊 Application is running on: http://localhost:$PORT${NC}"
echo -e "${BLUE}📋 API Documentation: http://localhost:$PORT/docs${NC}"
echo -e "${BLUE}🔍 Health Check: http://localhost:$PORT/health${NC}"

# Show container status
echo -e "${BLUE}📦 Container status:${NC}"
docker ps --filter "name=$CONTAINER_NAME"
