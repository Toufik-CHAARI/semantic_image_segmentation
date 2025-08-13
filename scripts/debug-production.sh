#!/bin/bash

# Production Debugging Script for Semantic Image Segmentation API
# This script helps debug production deployment issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
STACK_NAME="semantic-image-segmentation-lambda-container-mvp"
REGION="eu-west-3"
LAMBDA_FUNCTION_NAME="production-semantic-image-segmentation-api"
API_URL="https://xzlfcbm67c.execute-api.eu-west-3.amazonaws.com/production"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Function to check if AWS CLI is available
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed or not in PATH"
        exit 1
    fi
    log_info "AWS CLI is available"
}

# Function to check CloudFormation stack status
check_stack_status() {
    log_info "Checking CloudFormation stack status..."
    STACK_STATUS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null || echo "STACK_NOT_FOUND")
    
    log_info "Stack status: $STACK_STATUS"
    
    if [[ "$STACK_STATUS" == "CREATE_COMPLETE" || "$STACK_STATUS" == "UPDATE_COMPLETE" ]]; then
        log_info "✅ Stack is healthy"
        return 0
    elif [[ "$STACK_STATUS" == "STACK_NOT_FOUND" ]]; then
        log_error "❌ Stack not found: $STACK_NAME"
        return 1
    else
        log_warn "⚠️ Stack status: $STACK_STATUS"
        return 1
    fi
}

# Function to get API Gateway URL
get_api_url() {
    log_info "Getting API Gateway URL..."
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text 2>/dev/null || echo "URL_NOT_FOUND")
    
    if [[ "$API_URL" == "URL_NOT_FOUND" || -z "$API_URL" ]]; then
        log_error "❌ Could not retrieve API Gateway URL"
        return 1
    else
        log_info "✅ API Gateway URL: $API_URL"
        return 0
    fi
}

# Function to test API endpoints
test_api_endpoints() {
    log_info "Testing API endpoints..."
    
    # Test health endpoint
    log_debug "Testing health endpoint..."
    HEALTH_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/health" -o /tmp/health_response.json)
    if [[ "$HEALTH_RESPONSE" == "200" ]]; then
        log_info "✅ Health endpoint: OK"
        cat /tmp/health_response.json | jq . 2>/dev/null || cat /tmp/health_response.json
    else
        log_error "❌ Health endpoint failed: HTTP $HEALTH_RESPONSE"
        cat /tmp/health_response.json | jq . 2>/dev/null || cat /tmp/health_response.json
    fi
    
    # Test root endpoint
    log_debug "Testing root endpoint..."
    ROOT_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/" -o /tmp/root_response.json)
    if [[ "$ROOT_RESPONSE" == "200" ]]; then
        log_info "✅ Root endpoint: OK"
        cat /tmp/root_response.json | jq . 2>/dev/null || cat /tmp/root_response.json
    else
        log_error "❌ Root endpoint failed: HTTP $ROOT_RESPONSE"
        cat /tmp/root_response.json | jq . 2>/dev/null || cat /tmp/root_response.json
    fi
    
    # Test info endpoint
    log_debug "Testing info endpoint..."
    INFO_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/info" -o /tmp/info_response.json)
    if [[ "$INFO_RESPONSE" == "200" ]]; then
        log_info "✅ Info endpoint: OK"
        cat /tmp/info_response.json | jq . 2>/dev/null || cat /tmp/info_response.json
    else
        log_error "❌ Info endpoint failed: HTTP $INFO_RESPONSE"
        cat /tmp/info_response.json | jq . 2>/dev/null || cat /tmp/info_response.json
    fi
}

# Function to check Lambda function logs
check_lambda_logs() {
    log_info "Checking Lambda function logs..."
    
    # Check if log group exists
    LOG_GROUP="/aws/lambda/$LAMBDA_FUNCTION_NAME"
    if aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" --region $REGION --query 'logGroups[0].logGroupName' --output text 2>/dev/null | grep -q "$LOG_GROUP"; then
        log_info "✅ Log group found: $LOG_GROUP"
    else
        log_error "❌ Log group not found: $LOG_GROUP"
        return 1
    fi
    
    # Get recent log streams
    log_debug "Getting recent log streams..."
    RECENT_STREAM=$(aws logs describe-log-streams \
        --log-group-name "$LOG_GROUP" \
        --region $REGION \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null || echo "NO_STREAMS")
    
    if [[ "$RECENT_STREAM" == "NO_STREAMS" ]]; then
        log_warn "⚠️ No log streams found"
        return 1
    fi
    
    log_info "Recent log stream: $RECENT_STREAM"
    
    # Get recent log events
    log_debug "Getting recent log events..."
    aws logs get-log-events \
        --log-group-name "$LOG_GROUP" \
        --log-stream-name "$RECENT_STREAM" \
        --region $REGION \
        --start-time $(date -d '1 hour ago' +%s)000 \
        --query 'events[*].message' \
        --output text 2>/dev/null | head -20 || log_warn "No recent log events found"
}

# Function to check Lambda function status
check_lambda_status() {
    log_info "Checking Lambda function status..."
    
    # Check if function exists
    if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $REGION &>/dev/null; then
        log_info "✅ Lambda function exists: $LAMBDA_FUNCTION_NAME"
        
        # Get function configuration
        FUNCTION_CONFIG=$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $REGION --query 'Configuration.{Runtime:Runtime,Handler:Handler,MemorySize:MemorySize,Timeout:Timeout}' --output table)
        log_info "Function configuration:"
        echo "$FUNCTION_CONFIG"
        
        # Get function URL
        FUNCTION_URL=$(aws lambda get-function-url-config --function-name $LAMBDA_FUNCTION_NAME --region $REGION --query 'FunctionUrl' --output text 2>/dev/null || echo "NO_URL")
        if [[ "$FUNCTION_URL" != "NO_URL" ]]; then
            log_info "✅ Function URL: $FUNCTION_URL"
        else
            log_warn "⚠️ No function URL configured"
        fi
    else
        log_error "❌ Lambda function not found: $LAMBDA_FUNCTION_NAME"
        return 1
    fi
}

# Function to check ECR repository
check_ecr_repository() {
    log_info "Checking ECR repository..."
    
    REPOSITORY_NAME="semantic-image-segmentation-api"
    
    if aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $REGION &>/dev/null; then
        log_info "✅ ECR repository exists: $REPOSITORY_NAME"
        
        # List recent images
        log_debug "Recent images in repository:"
        aws ecr describe-images \
            --repository-name $REPOSITORY_NAME \
            --region $REGION \
            --query 'imageDetails[*].{Tag:imageTags[0],PushedAt:imagePushedAt,Size:imageSizeInBytes}' \
            --output table 2>/dev/null | head -10 || log_warn "No images found"
    else
        log_error "❌ ECR repository not found: $REPOSITORY_NAME"
        return 1
    fi
}

# Function to rebuild and redeploy Lambda image
rebuild_lambda_image() {
    log_info "Rebuilding Lambda image..."
    
    # Build Lambda image
    log_debug "Building Docker image..."
    docker build -f Dockerfile.lambda -t semantic-image-segmentation-api-lambda:latest . || {
        log_error "❌ Failed to build Lambda image"
        return 1
    }
    
    log_info "✅ Lambda image built successfully"
    
    # Tag and push to ECR
    log_debug "Tagging and pushing to ECR..."
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin 024848440742.dkr.ecr.eu-west-3.amazonaws.com || {
        log_error "❌ Failed to login to ECR"
        return 1
    }
    
    docker tag semantic-image-segmentation-api-lambda:latest 024848440742.dkr.ecr.eu-west-3.amazonaws.com/semantic-image-segmentation-api:latest || {
        log_error "❌ Failed to tag image"
        return 1
    }
    
    docker push 024848440742.dkr.ecr.eu-west-3.amazonaws.com/semantic-image-segmentation-api:latest || {
        log_error "❌ Failed to push image to ECR"
        return 1
    }
    
    log_info "✅ Lambda image pushed to ECR successfully"
}

# Function to update Lambda function
update_lambda_function() {
    log_info "Updating Lambda function..."
    
    # Update function code
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --image-uri 024848440742.dkr.ecr.eu-west-3.amazonaws.com/semantic-image-segmentation-api:latest \
        --region $REGION || {
        log_error "❌ Failed to update Lambda function"
        return 1
    }
    
    log_info "✅ Lambda function updated successfully"
    
    # Wait for update to complete
    log_debug "Waiting for update to complete..."
    aws lambda wait function-updated --function-name $LAMBDA_FUNCTION_NAME --region $REGION
    
    log_info "✅ Lambda function update completed"
}

# Function to show common fixes
show_common_fixes() {
    log_info "Common fixes for production issues:"
    echo ""
    echo "1. OpenGL Error (libGL.so.1):"
    echo "   - Add 'mesa-libGL' to Dockerfile.lambda"
    echo "   - Rebuild and redeploy Lambda image"
    echo ""
    echo "2. Model Download Issues:"
    echo "   - Check S3 permissions"
    echo "   - Verify model path in config"
    echo ""
    echo "3. Memory/Timeout Issues:"
    echo "   - Increase Lambda memory allocation"
    echo "   - Increase Lambda timeout"
    echo ""
    echo "4. Cold Start Issues:"
    echo "   - Use provisioned concurrency"
    echo "   - Optimize image size"
    echo ""
}

# Function to run full diagnostic
run_full_diagnostic() {
    log_info "Running full production diagnostic..."
    echo "================================================"
    
    check_aws_cli
    echo ""
    
    check_stack_status
    echo ""
    
    if check_stack_status; then
        get_api_url
        echo ""
        
        test_api_endpoints
        echo ""
        
        check_lambda_status
        echo ""
        
        check_lambda_logs
        echo ""
        
        check_ecr_repository
        echo ""
    fi
    
    log_info "Full diagnostic completed"
}

# Main script logic
main() {
    case "${1:-diagnostic}" in
        "diagnostic")
            run_full_diagnostic
            ;;
        "test-api")
            get_api_url && test_api_endpoints
            ;;
        "check-logs")
            check_lambda_logs
            ;;
        "check-status")
            check_stack_status && check_lambda_status
            ;;
        "rebuild")
            rebuild_lambda_image
            ;;
        "redeploy")
            rebuild_lambda_image && update_lambda_function
            ;;
        "fixes")
            show_common_fixes
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  diagnostic  - Run full diagnostic (default)"
            echo "  test-api    - Test API endpoints"
            echo "  check-logs  - Check Lambda function logs"
            echo "  check-status - Check stack and Lambda status"
            echo "  rebuild     - Rebuild Lambda image"
            echo "  redeploy    - Rebuild and redeploy Lambda"
            echo "  fixes       - Show common fixes"
            echo "  help        - Show this help"
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
