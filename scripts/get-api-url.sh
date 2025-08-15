#!/bin/bash

# Script to get the API Gateway URL for the deployed Lambda function
set -e

ENVIRONMENT=${1:-mvp}
REGION=${2:-eu-west-3}
STACK_NAME="semantic-image-segmentation-lambda-container-${ENVIRONMENT}"

echo "🔍 Getting API Gateway URL for environment: $ENVIRONMENT"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials are not configured"
    exit 1
fi

# Get the API Gateway URL
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text 2>/dev/null || echo "STACK_NOT_FOUND")

if [ "$API_URL" = "STACK_NOT_FOUND" ]; then
    echo "❌ Stack '$STACK_NAME' not found in region '$REGION'"
    exit 1
fi

echo ""
echo "✅ API Gateway URL: $API_URL"
echo ""
echo "🧪 Test your API:"
echo "curl -X POST \"$API_URL/api/segment\" \\"
echo "     -H \"Content-Type: multipart/form-data\" \\"
echo "     -F \"file=@path/to/image.jpg\""
echo ""
echo "📚 Documentation: $API_URL/docs"
echo "🏥 Health Check: $API_URL/health" 