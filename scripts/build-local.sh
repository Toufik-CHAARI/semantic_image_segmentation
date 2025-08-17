#!/bin/bash

# Local Docker Build Script for Semantic Image Segmentation API
# This script builds the Docker image locally with AWS credentials

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

echo -e "${BLUE}🔨 Building Docker images locally...${NC}"

# Check if .env file exists
if [ -f ".env/.env" ]; then
    echo -e "${BLUE}📁 Loading AWS credentials from .env/.env${NC}"
    # Skip the problematic line
    grep -v "^EC2_INSTANCE_ID$" .env/.env | source /dev/stdin
else
    echo -e "${YELLOW}⚠️  .env/.env file not found${NC}"
    echo -e "${YELLOW}   Please create .env/.env with your AWS credentials:${NC}"
    echo -e "${YELLOW}   AWS_ACCESS_KEY_ID=your_key${NC}"
    echo -e "${YELLOW}   AWS_SECRET_ACCESS_KEY=your_secret${NC}"
    echo -e "${YELLOW}   AWS_DEFAULT_REGION=eu-west-3${NC}"
    exit 1
fi

# Check if AWS credentials are available
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${RED}❌ AWS credentials not found in .env/.env${NC}"
    exit 1
fi

# Build the main Docker image
echo -e "${BLUE}📦 Building main Docker image...${NC}"
docker build \
    --build-arg AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    --build-arg AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    --build-arg AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-eu-west-3}" \
    -t "$IMAGE_NAME" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Main Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Main Docker build failed${NC}"
    exit 1
fi

# Build the test Docker image
echo -e "${BLUE}🧪 Building test Docker image...${NC}"
docker build \
    --build-arg AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    --build-arg AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    --build-arg AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-eu-west-3}" \
    -f Dockerfile.test \
    --file Dockerfile.test \
    -t "$TEST_IMAGE_NAME" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Test Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 All Docker images built successfully!${NC}"
echo -e "${BLUE}📦 Available images:${NC}"
echo -e "${BLUE}   - $IMAGE_NAME (main application)${NC}"
echo -e "${BLUE}   - $TEST_IMAGE_NAME (test environment)${NC}"

# Show image sizes
echo -e "${BLUE}📊 Image sizes:${NC}"
docker images | grep semantic-segmentation
