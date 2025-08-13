#!/bin/bash

# Lambda Container Deployment Script for Sentiment Analysis API MVP
# Usage: ./deploy-lambda-container.sh [environment] [region]

set -e

# Default values
ENVIRONMENT=${1:-mvp}
AWS_REGION=${2:-eu-west-3}
STACK_NAME="semantic-image-segmentation-lambda-container-${ENVIRONMENT}"

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Deploying Semantic Image Segmentation API to AWS Lambda Container (MVP)"
echo "Environment: $ENVIRONMENT"
echo "Region: $AWS_REGION"
echo "Stack Name: $STACK_NAME"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# ECR Repository name
ECR_REPOSITORY_NAME="${ENVIRONMENT}-semantic-image-segmentation-api"
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"

echo "📦 Building Docker image for Lambda..."
cd "$PROJECT_ROOT"

# Build the Lambda container image
docker build -f Dockerfile.lambda -t "${ECR_REPOSITORY_NAME}:${ENVIRONMENT}" .

echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "📤 Pushing image to ECR..."
# Tag the image for ECR
docker tag "${ECR_REPOSITORY_NAME}:${ENVIRONMENT}" "${ECR_REPOSITORY_URI}:${ENVIRONMENT}"

# Push to ECR
docker push "${ECR_REPOSITORY_URI}:${ENVIRONMENT}"

echo "☁️ Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file "${SCRIPT_DIR}/lambda-container-deployment.yml" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides Environment="$ENVIRONMENT" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$AWS_REGION"

echo "⏳ Waiting for stack deployment to complete..."
aws cloudformation wait stack-create-complete \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" || \
aws cloudformation wait stack-update-complete \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION"

echo "✅ Deployment completed successfully!"

# Get the API Gateway URL
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text)

echo ""
echo "🎉 Deployment successful!"
echo "📡 API Gateway URL: $API_URL"
echo ""
echo "🧪 Test your API:"
echo "curl -X POST \"$API_URL/predict-sentiment/\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"text\": \"I really enjoyed this movie!\"}'"
echo ""
echo "🗑️ To delete the stack:"
echo "aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION" 