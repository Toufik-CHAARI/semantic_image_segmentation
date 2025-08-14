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
    
    # Create a writable copy of DVC config in /tmp
    log_info "Creating writable DVC configuration..."
    mkdir -p "/tmp/.dvc"
    cp -r .dvc/* /tmp/.dvc/ 2>/dev/null || true
    
    # Modify the DVC config to use writable directories
    log_info "Modifying DVC configuration for Lambda..."
    sed -i 's|/var/task/.dvc/tmp|/tmp/dvc-temp|g' /tmp/.dvc/config 2>/dev/null || true
    sed -i 's|/var/task/.dvc/cache|/tmp/dvc-cache|g' /tmp/.dvc/config 2>/dev/null || true
    
    # Set environment variables
    export DVC_CONFIG="/tmp/.dvc/config"
    export DVC_TEMP_DIR="/tmp/dvc-temp"
    export DVC_CACHE_DIR="/tmp/dvc-cache"
    mkdir -p "$DVC_TEMP_DIR"
    mkdir -p "$DVC_CACHE_DIR"
    
    # Configure DVC to use the temp directories
    dvc config core.temp_dir "$DVC_TEMP_DIR"
    dvc config core.cache_dir "$DVC_CACHE_DIR"
    
    # Ensure DVC remote is configured
    if ! dvc remote list | grep -q "myremote"; then
        log_info "Setting up DVC remote..."
        dvc remote add myremote s3://semantic-segmentation-models-1754924238
    fi
    
    # Try DVC first, but fall back to direct S3 download if it fails
    log_info "Attempting to pull model with DVC..."
    cd model
    
    if dvc pull unet_best.keras.dvc; then
        log_info "Model downloaded successfully with DVC"
        ls -la
    else
        log_warn "DVC failed, trying direct S3 download..."
        
        # Fall back to direct S3 download
        if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
            log_info "Downloading model directly from S3..."
            aws s3 cp s3://semantic-segmentation-models-1754924238/unet_best.keras ./unet_best.keras
            
            if [ $? -eq 0 ]; then
                log_info "Model downloaded successfully from S3"
                ls -la
            else
                log_error "Failed to download model from S3"
                exit 1
            fi
        else
            log_error "AWS credentials not available for direct S3 download"
            exit 1
        fi
    fi
else
    log_info "Not in Lambda environment, skipping DVC setup"
fi
