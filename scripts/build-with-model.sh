#!/bin/bash

# Build script for Docker images with model handling from S3
set -e

# Default values
DOCKERFILE=${1:-Dockerfile}
TAG=${2:-latest}
IMAGE_NAME=${3:-semantic-image-segmentation-api}

echo "🐳 Building Docker image with S3 model handling..."
echo "Dockerfile: $DOCKERFILE"
echo "Tag: $TAG"
echo "Image: $IMAGE_NAME"

# Load environment variables from .env file
if [ -f ".env/.env" ]; then
    echo "📁 Loading environment variables from .env/.env"
    export $(cat .env/.env | grep -v '^#' | xargs)
else
    echo "⚠️  .env/.env file not found"
    echo "Please create .env/.env file with your AWS credentials (see .env/.env.example)"
    exit 1
fi

# Check if AWS credentials are available
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found in .env/.env file"
    echo "Please ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set"
    exit 1
fi

echo "✅ AWS credentials loaded successfully"
echo "🔍 AWS Region: ${AWS_DEFAULT_REGION:-eu-west-3}"
echo "🔍 S3 Bucket: ${DVC_S3_BUCKET:-semantic-segmentation-models-1754924238}"

# Build the Docker image with build args for AWS credentials
echo "🔨 Building Docker image with S3 model pull..."
docker build \
    --build-arg AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    --build-arg AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    --build-arg AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-eu-west-3}" \
    -f "$DOCKERFILE" \
    -t "$IMAGE_NAME:$TAG" \
    .

echo "✅ Docker image built successfully: $IMAGE_NAME:$TAG"

# Test the image if it's a test build
if [[ "$DOCKERFILE" == *"test"* ]]; then
    echo "🧪 Testing the built image..."
    docker run --rm -d --name test-build -p 8000:8000 "$IMAGE_NAME:$TAG"
    
    # Wait for startup
    sleep 15
    
    # Test health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed"
        docker logs test-build
        docker stop test-build
        exit 1
    fi
    
    # Test info endpoint to verify model is loaded
    if curl -f http://localhost:8000/info > /dev/null 2>&1; then
        echo "✅ Info endpoint passed"
    else
        echo "❌ Info endpoint failed"
        docker logs test-build
        docker stop test-build
        exit 1
    fi
    
    # Cleanup
    docker stop test-build
    echo "✅ Test completed successfully"
fi

echo "🎉 Build completed successfully!"
echo ""
echo "📋 Image details:"
echo "   Name: $IMAGE_NAME:$TAG"
echo "   Model: Pulled from S3 bucket ${DVC_S3_BUCKET:-semantic-segmentation-models-1754924238}"
echo "   Consistency: ✅ Same as CI/CD pipeline"
