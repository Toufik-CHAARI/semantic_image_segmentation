#!/bin/bash

# Get API Gateway URL from CloudFormation
STACK_NAME="sentiment-analysis-lambda-container-mvp"
REGION="eu-west-3"

echo "🔍 Getting API Gateway URL from CloudFormation stack..."

# Get the API Gateway URL
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

if [ -z "$API_URL" ] || [ "$API_URL" = "None" ]; then
    echo "❌ Could not find API Gateway URL in CloudFormation outputs"
    echo "📋 Checking all outputs:"
    aws cloudformation describe-stacks \
      --stack-name $STACK_NAME \
      --region $REGION \
      --query 'Stacks[0].Outputs'
else
    echo "✅ API Gateway URL found!"
    echo ""
    echo "🌐 API Gateway URL: $API_URL"
    echo "📚 Documentation: $API_URL/docs"
    echo "🏥 Health Check: $API_URL/health"
    echo ""
    echo "🧪 Test your API:"
    echo "curl -X POST \"$API_URL/predict-sentiment/\" \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"text\": \"I really enjoyed this movie!\"}'"
    echo ""
    echo "🔍 Test health endpoint:"
    echo "curl -f $API_URL/health"
fi 