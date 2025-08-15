#!/bin/bash

# Setup script for environment variables
set -e

echo "🔧 Setting up environment variables for Docker builds..."

# Check if .env directory exists
if [ ! -d ".env" ]; then
    echo "📁 Creating .env directory..."
    mkdir -p .env
fi

# Check if .env file already exists
if [ -f ".env/.env" ]; then
    echo "⚠️  .env/.env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

echo "📝 Please provide your AWS credentials:"
echo ""

# Get AWS Access Key ID
read -p "AWS Access Key ID: " aws_access_key_id
if [ -z "$aws_access_key_id" ]; then
    echo "❌ AWS Access Key ID is required"
    exit 1
fi

# Get AWS Secret Access Key
read -s -p "AWS Secret Access Key: " aws_secret_access_key
echo
if [ -z "$aws_secret_access_key" ]; then
    echo "❌ AWS Secret Access Key is required"
    exit 1
fi

# Get AWS Region (optional, with default)
read -p "AWS Region [eu-west-3]: " aws_region
aws_region=${aws_region:-eu-west-3}

# Get S3 Bucket (optional, with default)
read -p "S3 Bucket [semantic-segmentation-models-1754924238]: " s3_bucket
s3_bucket=${s3_bucket:-semantic-segmentation-models-1754924238}

# Create the .env file
echo "📄 Creating .env/.env file..."
cat > .env/.env << EOF
# AWS Credentials for DVC Model Management
# Generated on $(date)

# AWS Access Key ID for S3 bucket access
AWS_ACCESS_KEY_ID=$aws_access_key_id

# AWS Secret Access Key for S3 bucket access
AWS_SECRET_ACCESS_KEY=$aws_secret_access_key

# AWS Region
AWS_DEFAULT_REGION=$aws_region

# S3 Bucket name for model storage
DVC_S3_BUCKET=$s3_bucket

# Optional: AWS Session Token (if using temporary credentials)
# AWS_SESSION_TOKEN=your_session_token_here
EOF

echo "✅ Environment file created successfully!"
echo ""
echo "🔒 Security note:"
echo "   - The .env/.env file is already in .gitignore"
echo "   - Keep your AWS credentials secure"
echo "   - Never commit this file to version control"
echo ""
echo "🚀 You can now build Docker images with:"
echo "   ./scripts/build-with-model.sh Dockerfile.test test semantic-segmentation-test"
echo "   ./scripts/build-with-model.sh Dockerfile latest semantic-segmentation-api"
echo "   ./scripts/build-with-model.sh Dockerfile.lambda latest semantic-segmentation-lambda"
