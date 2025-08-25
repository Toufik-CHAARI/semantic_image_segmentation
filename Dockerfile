# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Build argument to force cache invalidation
ARG BUILD_TIMESTAMP
ENV BUILD_TIMESTAMP=$BUILD_TIMESTAMP

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY app/ ./app/
COPY model/ ./model/
COPY .dvc/ ./.dvc/

# Initialize git and pull model (if AWS credentials are provided)
RUN git init && \
    git config user.email "docker@build.local" && \
    git config user.name "Docker Build" && \
    chown -R appuser:appuser /app

# Switch to non-root user for DVC operations
USER appuser

# Set AWS credentials for DVC (only during build)
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION=eu-west-3
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

# Pull the model using DVC from S3 (optional - will use local if available)
RUN dvc remote add myremote s3://semantic-segmentation-models-1754924238 --force || true && \
    dvc remote modify myremote region eu-west-3 && \
    (dvc pull model/V3_unet_best.keras.dvc || echo "Using local model file")

# Clear AWS credentials from environment (security)
ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_DEFAULT_REGION=

# Verify model file is included
RUN ls -la model/ && echo "Model file size:" && du -h model/V3_unet_best.keras

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 