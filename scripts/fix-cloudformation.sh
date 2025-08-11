#!/bin/bash

# Fix CloudFormation Stack Issue
set -e

STACK_NAME="sentiment-analysis-lambda-container-mvp"
REGION="eu-west-3"

echo "🔍 Checking CloudFormation stack status..."

# Check if stack exists and get its status
STACK_STATUS=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].StackStatus' \
  --output text 2>/dev/null || echo "STACK_NOT_FOUND")

echo "Stack status: $STACK_STATUS"

if [ "$STACK_STATUS" = "ROLLBACK_COMPLETE" ]; then
    echo "❌ Stack is in ROLLBACK_COMPLETE state. Deleting stack..."
    aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
    
    echo "⏳ Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION
    echo "✅ Stack deleted successfully"
elif [ "$STACK_STATUS" = "STACK_NOT_FOUND" ]; then
    echo "ℹ️  Stack does not exist. Proceeding with deployment..."
else
    echo "ℹ️  Stack status: $STACK_STATUS"
fi

echo "🚀 Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file aws/lambda-container-deployment.yml \
  --stack-name $STACK_NAME \
  --parameter-overrides Environment=mvp \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

echo "✅ CloudFormation deployment completed!"

# Get the API Gateway URL
echo "🔗 Getting API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

echo "🌐 API Gateway URL: $API_URL"
echo "📚 Documentation: $API_URL/docs"
echo "🏥 Health Check: $API_URL/health" 