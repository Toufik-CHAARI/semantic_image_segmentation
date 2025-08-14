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

# Set up DVC and download model if in Lambda environment
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    try:
        print("Setting up DVC and downloading model...")
        subprocess.run(["./scripts/setup_dvc_lambda.sh"], check=True, shell=True)
        print("DVC setup completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up DVC: {e}")
        # Continue anyway, the service will handle model loading

# Create Mangum handler
handler = Mangum(app, lifespan="off") 