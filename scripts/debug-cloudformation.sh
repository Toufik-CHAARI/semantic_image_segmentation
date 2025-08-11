#!/bin/bash

# Debug CloudFormation Deployment Issues
set -e

STACK_NAME="sentiment-analysis-lambda-container-mvp"
REGION="eu-west-3"

echo "🔍 Debugging CloudFormation deployment..."

echo "📋 Checking stack status..."
aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].{Status:StackStatus,StatusReason:StackStatusReason}' \
  --output table

echo ""
echo "❌ Failed events:"
aws cloudformation describe-stack-events \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED` || ResourceStatus==`UPDATE_FAILED`].{Resource:LogicalResourceId,Status:ResourceStatus,Reason:ResourceStatusReason,Timestamp:Timestamp}' \
  --output table

echo ""
echo "📦 Checking ECR repository..."
aws ecr describe-repositories \
  --repository-names "mvp-sentiment-analysis-api" \
  --region $REGION \
  --query 'repositories[0].{Name:repositoryName,URI:repositoryUri}' \
  --output table 2>/dev/null || echo "ECR repository not found"

echo ""
echo "🐳 Checking ECR images..."
aws ecr describe-images \
  --repository-name "mvp-sentiment-analysis-api" \
  --region $REGION \
  --query 'imageDetails[].{Tag:imageTags[0],Size:imageSizeInBytes,PushedAt:imagePushedAt}' \
  --output table 2>/dev/null || echo "No images found in repository"

echo ""
echo "🔑 Checking IAM roles..."
aws iam get-role \
  --role-name "mvp-sentiment-analysis-lambda-role" \
  --query 'Role.{Name:RoleName,Arn:Arn}' \
  --output table 2>/dev/null || echo "IAM role not found"

echo ""
echo "📊 Recent stack events (last 10):"
aws cloudformation describe-stack-events \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'StackEvents[0:10].{Resource:LogicalResourceId,Status:ResourceStatus,Reason:ResourceStatusReason,Timestamp:Timestamp}' \
  --output table 