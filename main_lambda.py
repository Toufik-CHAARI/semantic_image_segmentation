"""
Main Lambda handler for Semantic Image Segmentation API
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from mangum import Mangum
from app.main import app

# Ensure cache directories exist
os.makedirs("/tmp/hf", exist_ok=True)

# Create handler for Lambda
handler = Mangum(app, lifespan="off")

# Lambda handler function
def lambda_handler(event, context):
    """Lambda handler for Semantic Image Segmentation API"""
    return handler(event, context) 