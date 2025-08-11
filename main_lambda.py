import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from mangum import Mangum
from main import app

# Create handler for Lambda
handler = Mangum(app, lifespan="off")

# Lambda handler function
def lambda_handler(event, context):
    """Lambda handler for FastAPI application"""
    return handler(event, context) 