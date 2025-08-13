# 🐳 Docker Workflow Guide

This guide covers all Docker-related processes for the Semantic Image Segmentation API project, including building, testing, and deploying all three Docker images.

## 📋 Table of Contents

- [Overview](#overview)
- [Docker Images](#docker-images)
- [Development Workflow](#development-workflow)
- [Building Images](#building-images)
- [Testing Images](#testing-images)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## 🎯 Overview

This project includes three specialized Docker images designed for different deployment scenarios:

1. **Production Image** (`Dockerfile`) - Multi-stage optimized container
2. **Test Image** (`Dockerfile.test`) - Testing environment with full framework
3. **Lambda Image** (`Dockerfile.lambda`) - AWS Lambda serverless deployment

## 🏗️ Docker Images

### 1. Production Image (`Dockerfile`)

**Purpose**: Production-ready API server for long-running services

**Key Features**:
- Multi-stage build for size optimization
- Non-root user (`appuser`) for security
- Health checks with curl
- Production environment variables
- Optimized for performance and security

**Base Image**: `python:3.12-slim` (Debian-based)
**Package Manager**: `apt-get`
**Dependencies**: `requirements.txt` (full production stack)

**Build Command**:
```bash
make docker-build
```

**Run Command**:
```bash
make docker-run
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

### 2. Test Image (`Dockerfile.test`)

**Purpose**: Testing environment with comprehensive testing framework

**Key Features**:
- Includes pytest and testing tools
- Minimal system dependencies
- Built-in pytest configuration
- Fast iteration for development
- Includes all testing dependencies

**Base Image**: `python:3.12-slim` (Debian-based)
**Package Manager**: `apt-get`
**Dependencies**: `requirements-test.txt` (testing + minimal production)

**Build Command**:
```bash
make docker-build-test
```

**Run Command**:
```bash
make docker-test
```

**Test Execution**:
```bash
docker run --rm semantic-image-segmentation-api:test python -m pytest tests/ -v
```

### 3. Lambda Image (`Dockerfile.lambda`)

**Purpose**: AWS Lambda serverless deployment

**Key Features**:
- AWS Lambda base image
- Event-driven execution model
- Optimized for cold starts
- AWS integration ready
- Minimal runtime footprint

**Base Image**: `public.ecr.aws/lambda/python:3.12` (Amazon Linux)
**Package Manager**: `microdnf` (Amazon Linux)
**Dependencies**: `requirements-lambda.txt` (minimal + AWS packages)

**Build Command**:
```bash
make docker-build-lambda
```

**Deployment**: AWS Lambda via ECR

## 🔄 Development Workflow

### Complete Docker Workflow

For comprehensive validation of all Docker images:

```bash
# Complete development workflow (includes Docker)
make dev-workflow
```

This command executes:
1. ✅ Code quality checks
2. 🏗️ Build all Docker images
3. 🧪 Test all Docker images
4. 📊 Run full test suite

### Individual Docker Workflow Steps

```bash
# Step 1: Build all images
make docker-build-all

# Step 2: Test all images
make docker-test-all

# Step 3: Validate functionality
make test-coverage-detail
```

## 🏗️ Building Images

### Build All Images

```bash
# Build all three Docker images
make docker-build-all
```

This command builds:
- Production image: `semantic-image-segmentation-api:latest`
- Test image: `semantic-image-segmentation-api:test`
- Lambda image: `semantic-image-segmentation-api-lambda:latest`

### Build Individual Images

```bash
# Production image only
make docker-build

# Test image only
make docker-build-test

# Lambda image only
make docker-build-lambda
```

### Build Process Details

**Production Image Build**:
```bash
# Multi-stage build process
docker build -t semantic-image-segmentation-api:latest .
```

**Test Image Build**:
```bash
# Uses .dockerignore.test for test-specific exclusions
docker build -f Dockerfile.test -t semantic-image-segmentation-api:test .
```

**Lambda Image Build**:
```bash
# AWS Lambda optimized build
docker build -f Dockerfile.lambda -t semantic-image-segmentation-api-lambda:latest .
```

## 🧪 Testing Images

### Test All Images

```bash
# Test all Docker images automatically
make docker-test-all
```

This command:
- Starts each container
- Tests health endpoints
- Validates runtime functionality
- Cleans up containers

### Test Individual Images

```bash
# Test production image
docker run --rm -d --name test-prod -p 8001:8000 semantic-image-segmentation-api:latest
sleep 10
curl -f http://localhost:8001/health
docker stop test-prod

# Test test image
docker run --rm -d --name test-test -p 8002:8000 semantic-image-segmentation-api:test
sleep 10
curl -f http://localhost:8002/health
docker stop test-test

# Test Lambda image
docker run --rm -d --name test-lambda -p 8003:8080 semantic-image-segmentation-api-lambda:latest
sleep 5
docker logs test-lambda | grep -q "rapid"
docker stop test-lambda
```

### Manual Testing Commands

```bash
# Check if images exist
docker images | grep semantic

# Run interactive shell in container
docker run --rm -it semantic-image-segmentation-api:latest /bin/bash

# View container logs
docker logs <container-name>

# Check container status
docker ps -a
```

## 🚀 Deployment

### Production Deployment

```bash
# Build production image
make docker-build

# Push to registry
make docker-push-main

# Deploy to ECR
make docker-push-ecr
```

### AWS Lambda Deployment

```bash
# Build Lambda image
make docker-build-lambda

# Push to ECR
make docker-push-ecr-all
```

### Local Deployment

```bash
# Start production container
make docker-run

# Start with custom port
docker run -d --name my-api -p 9000:8000 semantic-image-segmentation-api:latest

# Start with environment variables
docker run -d --name my-api -p 8000:8000 \
  -e LOG_LEVEL=debug \
  -e HOST=0.0.0.0 \
  semantic-image-segmentation-api:latest
```

## 🔧 Docker Commands Reference

### Build Commands

```bash
make docker-build           # Build production image
make docker-build-test      # Build test image
make docker-build-lambda    # Build Lambda image
make docker-build-all       # Build all images
```

### Test Commands

```bash
make docker-test            # Test test image
make docker-test-all        # Test all images
```

### Run Commands

```bash
make docker-run             # Run production container
make docker-stop            # Stop containers
```

### Registry Commands

```bash
make docker-tag             # Tag images for registry
make docker-push            # Push all images
make docker-push-main       # Push production image
make docker-push-ecr        # Push to AWS ECR
make docker-push-ecr-all    # Push all to ECR
```

### Cleanup Commands

```bash
make clean-docker           # Clean Docker system
docker system prune -f      # Remove unused images
docker image prune -f       # Remove dangling images
```

## 🐛 Troubleshooting

### Common Docker Issues

#### 1. OpenGL Dependency Error

**Error**: `ImportError: libGL.so.1: cannot open shared object file`

**Solution**: Ensure `libgl1` package is installed in Dockerfile
```dockerfile
RUN apt-get install -y libgl1
```

#### 2. Build Context Issues

**Error**: `COPY failed: file not found`

**Solution**: Check `.dockerignore` files
```bash
# For test builds, use .dockerignore.test
cp .dockerignore.test .dockerignore
docker build -f Dockerfile.test .
```

#### 3. Port Conflicts

**Error**: `bind: address already in use`

**Solution**: Use different ports
```bash
docker run -p 8001:8000 semantic-image-segmentation-api:latest
```

#### 4. Memory Issues

**Error**: `Killed` during build

**Solution**: Increase Docker memory allocation
- Docker Desktop: Settings → Resources → Memory (increase to 4GB+)

#### 5. Network Issues

**Error**: `Failed to connect to registry`

**Solution**: Check network connectivity
```bash
docker pull python:3.12-slim
```

### Debug Commands

```bash
# Check Docker daemon
docker info

# Check available images
docker images

# Check running containers
docker ps

# Check container logs
docker logs <container-name>

# Inspect container
docker inspect <container-name>

# Check container resource usage
docker stats
```

### Performance Optimization

```bash
# Use build cache
docker build --no-cache=false .

# Parallel builds (if supported)
docker buildx build --platform linux/amd64 .

# Multi-stage optimization
# Already implemented in production Dockerfile
```

## 📊 Image Comparison

| Aspect | Production | Test | Lambda |
|--------|------------|------|--------|
| **Base Image** | `python:3.12-slim` | `python:3.12-slim` | `public.ecr.aws/lambda/python:3.12` |
| **Size** | ~3.5GB | ~3.7GB | ~4.2GB |
| **Security** | Non-root user | Default user | Lambda user |
| **Optimization** | Multi-stage | Single stage | Lambda optimized |
| **Dependencies** | Full stack | Test + minimal | Minimal + AWS |
| **Use Case** | Long-running | Development | Event-driven |

## 🎯 Best Practices

### 1. Always Build All Images

```bash
# Before commits
make docker-build-all

# Before deployments
make docker-test-all
```

### 2. Use Specific Tags

```bash
# Tag with version
docker tag semantic-image-segmentation-api:latest semantic-image-segmentation-api:v1.0.0

# Tag with environment
docker tag semantic-image-segmentation-api:latest semantic-image-segmentation-api:staging
```

### 3. Clean Up Regularly

```bash
# Weekly cleanup
make clean-docker

# Remove old images
docker image prune -a
```

### 4. Monitor Resource Usage

```bash
# Check image sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Monitor container resources
docker stats
```

### 5. Use Health Checks

```bash
# Production image includes health checks
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

## 📈 Performance Metrics

### Build Times (Typical)

- **Production Image**: ~5-8 minutes
- **Test Image**: ~3-5 minutes  
- **Lambda Image**: ~8-12 minutes
- **All Images**: ~15-25 minutes

### Image Sizes

- **Production Image**: ~3.5GB
- **Test Image**: ~3.7GB
- **Lambda Image**: ~4.2GB

### Resource Requirements

- **Memory**: 2GB+ for builds
- **CPU**: 2+ cores recommended
- **Storage**: 15GB+ for all images
- **Network**: Stable internet connection

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build and Test

on: [push, pull_request]

jobs:
  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build all images
        run: make docker-build-all
      - name: Test all images
        run: make docker-test-all
      - name: Run tests
        run: make test-coverage-detail
```

### Local Development Workflow

```bash
# Daily development
make dev-workflow

# Before commits
make docker-build-all && make docker-test-all

# Before deployments
make docker-push-ecr-all
```

---

**Happy Docker Development! 🐳**
