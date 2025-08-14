#!/bin/bash

# Script to set up DVC for Lambda deployment

set -e

# Colors for messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a Lambda environment
if [ -n "$AWS_LAMBDA_FUNCTION_NAME" ]; then
    log_info "Running in Lambda environment"
    
    # Set up DVC remote configuration
    if [ ! -d ".dvc" ]; then
        log_error ".dvc directory not found"
        exit 1
    fi
    
    # Ensure DVC remote is configured
    if ! dvc remote list | grep -q "myremote"; then
        log_info "Setting up DVC remote..."
        dvc remote add myremote s3://semantic-segmentation-models-1754924238
    fi
    
    # Pull the model
    log_info "Pulling model from S3..."
    cd model
    dvc pull unet_best.keras.dvc
    
    if [ $? -eq 0 ]; then
        log_info "Model downloaded successfully"
        ls -la
    else
        log_error "Failed to download model"
        exit 1
    fi
else
    log_info "Not in Lambda environment, skipping DVC setup"
fi
