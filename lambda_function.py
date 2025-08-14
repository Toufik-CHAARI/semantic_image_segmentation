"""
Lambda handler for Semantic Image Segmentation API
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from mangum import Mangum
from app.main import app

# Ensure cache directories exist
os.makedirs("/tmp/hf", exist_ok=True)

# Set DVC environment variables for Lambda
os.environ["DVC_TEMP_DIR"] = "/tmp/dvc-temp"
os.environ["DVC_CACHE_DIR"] = "/tmp/dvc-cache"
os.makedirs("/tmp/dvc-temp", exist_ok=True)
os.makedirs("/tmp/dvc-cache", exist_ok=True)

# Set up DVC and download model if in Lambda environment
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    print("Lambda environment detected, setting up DVC and model...")
    try:
        # Check if setup script exists
        if os.path.exists("./scripts/setup_dvc_lambda.sh"):
            print("Setup script found, executing...")
            result = subprocess.run(["./scripts/setup_dvc_lambda.sh"], 
                                  capture_output=True, text=True, shell=True)
            print(f"Setup script stdout: {result.stdout}")
            print(f"Setup script stderr: {result.stderr}")
            print(f"Setup script return code: {result.returncode}")
            if result.returncode == 0:
                print("DVC setup completed successfully")
            else:
                print("DVC setup failed, but continuing...")
                print("Will attempt to load model directly if it exists")
        else:
            print("Setup script not found, skipping DVC setup")
    except Exception as e:
        print(f"Error during DVC setup: {e}")
        print("Continuing without DVC setup...")
        print("Will attempt to load model directly if it exists")

# Create Mangum handler
handler = Mangum(app, lifespan="off") 