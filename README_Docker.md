# 🐳 Docker Workflow Guide - Semantic Image Segmentation API

This comprehensive guide covers all Docker-related processes for the Semantic Image Segmentation API project, including building, testing, and deploying two specialized Docker images for different deployment scenarios.

## 📋 **Table of Contents**

- [Overview](#overview)
- [Docker Images](#docker-images)
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Building Images](#building-images)
- [Testing Images](#testing-images)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Performance Optimization](#performance-optimization)

## 🎯 **Overview**

This project includes two specialized Docker images designed for different deployment scenarios:

1. **🏭 Production Image** (`Dockerfile`) - Multi-stage optimized container for production
2. **🧪 Test Image** (`Dockerfile.test`) - Testing environment with full framework

### **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐
│   Production    │    │   Test Image    │
│   Image         │    │                 │
│   (Multi-stage) │    │   (Single-stage)│
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Long-running  │    │   Development   │
│   Services      │    │   & Testing     │
└─────────────────┘    └─────────────────┘
```

## 🏗️ **Docker Images**

### **1. Production Image (`Dockerfile`)**

**Purpose**: Production-ready API server for long-running services

**Key Features**:
- ✅ Multi-stage build for size optimization
- ✅ Non-root user (`appuser`) for security
- ✅ Health checks with curl
- ✅ Production environment variables
- ✅ Optimized for performance and security
- ✅ Minimal attack surface

**Base Image**: `python:3.12-slim` (Debian-based)
**Package Manager**: `apt-get`
**Dependencies**: `requirements.txt` (full production stack)
**Final Size**: ~1.15GB

**Build Command**:
```bash
# ⚠️ IMPORTANT: Use the build script to load AWS credentials
./scripts/build-with-model.sh

# Alternative: Direct docker build (requires AWS credentials manually)
docker build \
  --build-arg AWS_ACCESS_KEY_ID=your_key \
  --build-arg AWS_SECRET_ACCESS_KEY=your_secret \
  -t semantic-image-segmentation-api:latest .
```

**Run Command**:
```bash
make docker-run
# or
docker run -d --name api-server -p 8000:8000 semantic-image-segmentation-api:latest
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

### **2. Test Image (`Dockerfile.test`)**

**Purpose**: Testing environment with comprehensive testing framework

**Key Features**:
- ✅ Includes pytest and testing tools
- ✅ Minimal system dependencies
- ✅ Built-in pytest configuration
- ✅ Fast iteration for development
- ✅ Includes all testing dependencies
- ✅ Development-friendly environment

**Base Image**: `python:3.12-slim` (Debian-based)
**Package Manager**: `apt-get`
**Dependencies**: `requirements-test.txt` (testing + minimal production)
**Final Size**: ~3.7GB

**Build Command**:
```bash
# ⚠️ IMPORTANT: Use the build script to load AWS credentials
./scripts/build-with-model.sh Dockerfile.test test semantic-image-segmentation-test

# Alternative: Direct docker build (requires AWS credentials manually)
docker build \
  --build-arg AWS_ACCESS_KEY_ID=your_key \
  --build-arg AWS_SECRET_ACCESS_KEY=your_secret \
  -f Dockerfile.test -t semantic-image-segmentation-api:test .
```

**Run Command**:
```bash
make docker-test
# or
docker run --rm semantic-image-segmentation-api:test python -m pytest tests/ -v
```

**Test Execution**:
```bash
# Run all tests
docker run --rm semantic-image-segmentation-api:test python -m pytest tests/ -v

# Run specific test categories
docker run --rm semantic-image-segmentation-api:test python -m pytest tests/unit/ -v
docker run --rm semantic-image-segmentation-api:test python -m pytest tests/integration/ -v

# Run with coverage
docker run --rm semantic-image-segmentation-api:test python -m pytest tests/ --cov=app --cov-report=html
```

## 🚀 **Quick Start**

### **Complete Setup in 5 Minutes**

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd semantic_image_segmentation

# 2. Build all images (using script with AWS credentials)
./scripts/build-with-model.sh

# 3. Test all images
make docker-test-all

# 4. Run production container
make docker-run

# 5. Verify deployment
curl http://localhost:8000/health
```

### **Individual Image Setup**

```bash
# Production only (with AWS credentials)
./scripts/build-with-model.sh && make docker-run

# Test only (with AWS credentials)
./scripts/build-with-model.sh Dockerfile.test test semantic-image-segmentation-test && make docker-test
```

## 🔄 **Development Workflow**

### **Complete Docker Workflow**

For comprehensive validation of all Docker images:

```bash
# Complete development workflow (includes Docker)
make dev-workflow
```

This command executes:
1. ✅ Code quality checks (linting, formatting)
2. 🏗️ Build all Docker images
3. 🧪 Test all Docker images
4. 📊 Run full test suite with coverage

### **Individual Docker Workflow Steps**

```bash
# Step 1: Build all images
make docker-build-all

# Step 2: Test all images
make docker-test-all

# Step 3: Validate functionality
make test-coverage-detail

# Step 4: Clean up (optional)
make clean-docker
```

### **Daily Development Workflow**

```bash
# Morning setup (with AWS credentials)
./scripts/build-with-model.sh Dockerfile.test test semantic-image-segmentation-test
make docker-test

# During development
make docker-run  # Start production container
# ... make changes ...
make docker-test  # Test changes

# Before commit
make dev-workflow  # Full validation
```

## 🏗️ **Building Images**

### **⚠️ IMPORTANT: AWS Credentials Required**

**Local builds require AWS credentials to pull models from S3.** The Docker build process needs to download the ML model from the S3 bucket during the build phase.

**✅ Recommended Approach:**
```bash
# Use the build script that automatically loads credentials from .env/.env
./scripts/build-with-model.sh
```

**❌ Common Mistake:**
```bash
# This will fail without AWS credentials
make docker-build
docker build -t semantic-image-segmentation-api:latest .
```

**📋 Prerequisites:**
- AWS credentials configured in `.env/.env` file
- S3 bucket access for model storage
- DVC configured for model versioning

### **Build All Images**

```bash
# ⚠️ IMPORTANT: Use the build script to load AWS credentials
./scripts/build-with-model.sh

# For test image specifically:
./scripts/build-with-model.sh Dockerfile.test test semantic-image-segmentation-test
```

This command builds:
- Production image: `semantic-image-segmentation-api:latest`
- Test image: `semantic-image-segmentation-test:test`

### **Build Individual Images**

```bash
# Production image only (with AWS credentials)
./scripts/build-with-model.sh

# Test image only (with AWS credentials)
./scripts/build-with-model.sh Dockerfile.test test semantic-image-segmentation-test
```

### **Build Process Details**

**Production Image Build**:
```bash
# Multi-stage build process
docker build -t semantic-image-segmentation-api:latest .

# Build with specific tag
docker build -t semantic-image-segmentation-api:v1.0.0 .

# Build with no cache (for clean builds)
docker build --no-cache -t semantic-image-segmentation-api:latest .
```

**Test Image Build**:
```bash
# Uses .dockerignore.test for test-specific exclusions
docker build -f Dockerfile.test -t semantic-image-segmentation-api:test .

# Build with development dependencies
docker build -f Dockerfile.test -t semantic-image-segmentation-api:dev .
```

### **Build Optimization**

```bash
# Parallel builds (if supported)
docker buildx build --platform linux/amd64,linux/arm64 -t semantic-image-segmentation-api:latest .

# Build with build arguments
docker build --build-arg ENVIRONMENT=production -t semantic-image-segmentation-api:latest .

# Build with specific target
docker build --target production -t semantic-image-segmentation-api:latest .
```

## 🧪 **Testing Images**

### **Test All Images**

```bash
# Test all Docker images automatically
make docker-test-all
```

This command:
- Starts each container
- Tests health endpoints
- Validates runtime functionality
- Cleans up containers
- Provides detailed feedback

### **Test Individual Images**

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
```

### **Comprehensive Testing**

```bash
# Test with specific environment
ENVIRONMENT=staging make docker-test-all

# Test with custom ports
docker run --rm -d --name test-custom -p 9000:8000 semantic-image-segmentation-api:latest

# Test with environment variables
docker run --rm -d --name test-env -p 8000:8000 \
  -e LOG_LEVEL=debug \
  -e HOST=0.0.0.0 \
  semantic-image-segmentation-api:latest

# Test with volume mounts
docker run --rm -d --name test-volume -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  semantic-image-segmentation-api:latest
```

### **Manual Testing Commands**

```bash
# Check if images exist
docker images | grep semantic

# Run interactive shell in container
docker run --rm -it semantic-image-segmentation-api:latest /bin/bash

# View container logs
docker logs <container-name>

# Check container status
docker ps -a

# Inspect container configuration
docker inspect <container-name>

# Check container resource usage
docker stats <container-name>
```

## 🚀 **Deployment**

### **Production Deployment**

```bash
# Build production image
make docker-build

# Push to registry
make docker-push-main

# Deploy to ECR
make docker-push-ecr
```

### **Local Deployment**

```bash
# Start production container
make docker-run

# Start with custom port
docker run -d --name my-api -p 9000:8000 semantic-image-segmentation-api:latest

# Start with environment variables
docker run -d --name my-api -p 8000:8000 \
  -e LOG_LEVEL=debug \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  semantic-image-segmentation-api:latest

# Start with resource limits
docker run -d --name my-api -p 8000:8000 \
  --memory=2g \
  --cpus=1.0 \
  semantic-image-segmentation-api:latest
```

### **Docker Compose Deployment**

```bash
# Start all services
docker-compose up -d

# Start with specific services
docker-compose up -d semantic-image-segmentation-api

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 **Docker Commands Reference**

### **Build Commands**

```bash
# ⚠️ IMPORTANT: Use build scripts to load AWS credentials
./scripts/build-with-model.sh                                    # Build production image
./scripts/build-with-model.sh Dockerfile.test test semantic-image-segmentation-test  # Build test image

# Alternative: Direct docker commands (requires manual AWS credentials)
make docker-build           # Build production image (manual credentials needed)
make docker-build-test      # Build test image (manual credentials needed)
make docker-build-all       # Build all images (manual credentials needed)
```

### **Test Commands**

```bash
make docker-test            # Test test image
make docker-test-all        # Test all images
```

### **Run Commands**

```bash
make docker-run             # Run production container
make docker-stop            # Stop containers
```

### **Registry Commands**

```bash
make docker-tag             # Tag images for registry
make docker-push            # Push all images
make docker-push-main       # Push production image
make docker-push-ecr        # Push to AWS ECR
```

### **Cleanup Commands**

```bash
make clean-docker           # Clean Docker system
docker system prune -f      # Remove unused images
docker image prune -f       # Remove dangling images
docker container prune -f   # Remove stopped containers
```

## 🐛 **Troubleshooting**

### **Common Docker Issues**

#### **1. OpenGL Dependency Error**

**Error**: `ImportError: libGL.so.1: cannot open shared object file`

**Solution**: Ensure `libgl1` package is installed in Dockerfile
```dockerfile
RUN apt-get update && apt-get install -y libgl1-mesa-glx
```

#### **2. Build Context Issues**

**Error**: `COPY failed: file not found`

**Solution**: Check `.dockerignore` files
```bash
# For test builds, use .dockerignore.test
cp .dockerignore.test .dockerignore
docker build -f Dockerfile.test .

# Check what files are being copied
docker build --progress=plain -f Dockerfile.test .
```

#### **3. Port Conflicts**

**Error**: `bind: address already in use`

**Solution**: Use different ports
```bash
docker run -p 8001:8000 semantic-image-segmentation-api:latest

# Or stop existing containers
docker stop $(docker ps -q)
```

#### **4. Memory Issues**

**Error**: `Killed` during build

**Solution**: Increase Docker memory allocation
- Docker Desktop: Settings → Resources → Memory (increase to 4GB+)
- Linux: Increase available memory or use swap

#### **5. Network Issues**

**Error**: `Failed to connect to registry`

**Solution**: Check network connectivity
```bash
# Test connectivity
docker pull python:3.12-slim

# Use different DNS
docker run --dns 8.8.8.8 semantic-image-segmentation-api:latest
```

#### **6. Permission Issues**

**Error**: `Permission denied` when running container

**Solution**: Check user permissions
```bash
# Run with specific user
docker run --user $(id -u):$(id -g) semantic-image-segmentation-api:latest

# Fix file permissions
chmod -R 755 .
```

#### **7. AWS Credentials Issues**

**Error**: `Unable to locate credentials` or `failed to connect to s3`

**Solution**: Ensure AWS credentials are properly configured
```bash
# Check if .env/.env file exists and has credentials
ls -la .env/.env
cat .env/.env | grep AWS

# Use the build script that loads credentials automatically
./scripts/build-with-model.sh

# Or manually provide credentials during build
docker build \
  --build-arg AWS_ACCESS_KEY_ID=your_key \
  --build-arg AWS_SECRET_ACCESS_KEY=your_secret \
  -t semantic-image-segmentation-api:latest .
```

### **Debug Commands**

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

# Check Docker system info
docker system df

# Check build cache
docker builder prune
```

### **Performance Optimization**

```bash
# Use build cache effectively
docker build --no-cache=false .

# Parallel builds (if supported)
docker buildx build --platform linux/amd64 .

# Multi-stage optimization
# Already implemented in production Dockerfile

# Use .dockerignore effectively
# Exclude unnecessary files from build context
```

## 📊 **Image Comparison**

| Aspect | Production | Test |
|--------|------------|------|
| **Base Image** | `python:3.12-slim` | `python:3.12-slim` |
| **Size** | ~3.5GB | ~3.7GB |
| **Security** | Non-root user | Default user |
| **Optimization** | Multi-stage | Single stage |
| **Dependencies** | Full stack | Test + minimal |
| **Use Case** | Long-running | Development |
| **Startup Time** | ~30s | ~25s |
| **Memory Usage** | ~2GB | ~2.2GB |

## 🎯 **Best Practices**

### **1. Always Build All Images**

```bash
# Before commits
make docker-build-all

# Before deployments
make docker-test-all

# Regular maintenance
make clean-docker && make docker-build-all
```

### **2. Use Specific Tags**

```bash
# Tag with version
docker tag semantic-image-segmentation-api:latest semantic-image-segmentation-api:v1.0.0

# Tag with environment
docker tag semantic-image-segmentation-api:latest semantic-image-segmentation-api:staging

# Tag with date
docker tag semantic-image-segmentation-api:latest semantic-image-segmentation-api:$(date +%Y%m%d)
```

### **3. Clean Up Regularly**

```bash
# Weekly cleanup
make clean-docker

# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

### **4. Monitor Resource Usage**

```bash
# Check image sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Monitor container resources
docker stats

# Check disk usage
docker system df
```

### **5. Use Health Checks**

```bash
# Production image includes health checks
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Custom health check
docker run --health-cmd="curl -f http://localhost:8000/health" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  semantic-image-segmentation-api:latest
```

### **6. Security Best Practices**

```bash
# Run as non-root user (already implemented)
# Use specific base image versions
# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image semantic-image-segmentation-api:latest

# Use secrets management
docker run --secret db_password semantic-image-segmentation-api:latest
```

## 📈 **Performance Metrics**

### **Build Times (Typical)**

- **Production Image**: ~5-8 minutes
- **Test Image**: ~3-5 minutes  
- **All Images**: ~8-13 minutes

### **Image Sizes**

- **Production Image**: ~3.5GB
- **Test Image**: ~3.7GB

### **Resource Requirements**

- **Memory**: 2GB+ for builds
- **CPU**: 2+ cores recommended
- **Storage**: 10GB+ for all images
- **Network**: Stable internet connection

### **Runtime Performance**

- **Startup Time**: 10-30 seconds
- **Memory Usage**: 1.8-2.2GB
- **CPU Usage**: 1-2 cores under load
- **Network**: Minimal (API responses only)

## 🔄 **CI/CD Integration**

### **GitHub Actions Example**

```yaml
name: Docker Build and Test

on: [push, pull_request]

jobs:
  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build all images
        run: make docker-build-all
      
      - name: Test all images
        run: make docker-test-all
      
      - name: Run tests
        run: make test-coverage-detail
      
      - name: Push to ECR
        if: github.ref == 'refs/heads/main'
        run: make docker-push-ecr
```

### **Local Development Workflow**

```bash
# Daily development
make dev-workflow

# Before commits
make docker-build-all && make docker-test-all

# Before deployments
make docker-push-ecr

# Regular maintenance
make clean-docker && make docker-build-all
```

### **Environment-Specific Workflows**

```bash
# Development environment
ENVIRONMENT=dev make docker-build-all

# Staging environment
ENVIRONMENT=staging make docker-build-all

# Production environment
ENVIRONMENT=production make docker-build-all
```

## 🔍 **Advanced Topics**

### **Multi-Architecture Builds**

```bash
# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 \
  -t semantic-image-segmentation-api:latest .

# Push multi-arch images
docker buildx build --platform linux/amd64,linux/arm64 \
  -t semantic-image-segmentation-api:latest \
  --push .
```

### **Custom Base Images**

```bash
# Use custom base image
docker build --build-arg BASE_IMAGE=python:3.12-alpine \
  -t semantic-image-segmentation-api:alpine .

# Use specific TensorFlow base
docker build --build-arg TF_VERSION=2.16.1 \
  -t semantic-image-segmentation-api:tf-2.16.1 .
```

### **Optimization Techniques**

```bash
# Layer caching optimization
docker build --target builder -t semantic-image-segmentation-api:builder .
docker build --cache-from semantic-image-segmentation-api:builder \
  -t semantic-image-segmentation-api:latest .

# Multi-stage with specific targets
docker build --target production -t semantic-image-segmentation-api:latest .
```

---

**Happy Docker Development! 🐳**

*For additional support, refer to the main README.md or create an issue in the repository.*
