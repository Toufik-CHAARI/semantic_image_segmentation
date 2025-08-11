#!/bin/bash

# Comprehensive Lambda Container Deployment Script
set -e

ENVIRONMENT="mvp"
REGION="eu-west-3"
STACK_NAME="sentiment-analysis-lambda-container-mvp"
REPO_NAME="${ENVIRONMENT}-sentiment-analysis-api"

echo "🚀 Starting comprehensive deployment..."

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $ACCOUNT_ID"

# Step 1: Create ECR repository if it doesn't exist
echo "📦 Creating ECR repository..."
aws ecr describe-repositories --repository-names "$REPO_NAME" --region $REGION 2>/dev/null || \
aws ecr create-repository --repository-name "$REPO_NAME" --region $REGION

# Step 2: Build and push Docker image
echo "🐳 Building Docker image..."
docker build -f Dockerfile.lambda -t $REPO_NAME:latest .

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "🏷️  Tagging and pushing image..."
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest"
docker tag $REPO_NAME:latest $ECR_URI
docker push $ECR_URI

echo "✅ Image pushed successfully: $ECR_URI"

# Step 3: Check and fix CloudFormation stack
echo "🔍 Checking CloudFormation stack status..."
STACK_STATUS=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].StackStatus' \
  --output text 2>/dev/null || echo "STACK_NOT_FOUND")

echo "Current stack status: $STACK_STATUS"

if [ "$STACK_STATUS" = "ROLLBACK_COMPLETE" ]; then
    echo "❌ Stack is in ROLLBACK_COMPLETE state. Deleting stack..."
    aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
    aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION
    echo "✅ Stack deleted successfully"
fi

# Step 4: Deploy CloudFormation stack
echo "🚀 Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file aws/lambda-container-deployment.yml \
  --stack-name $STACK_NAME \
  --parameter-overrides Environment=$ENVIRONMENT \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# Step 5: Get outputs
echo "🔗 Getting API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 API Gateway URL: $API_URL"
echo "📚 Documentation: $API_URL/docs"
echo "🏥 Health Check: $API_URL/health"
echo ""
echo "🧪 Test your API:"
echo "curl -X POST \"$API_URL/predict-sentiment/\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"text\": \"I really enjoyed this movie!\"}'" 