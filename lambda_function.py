"""
Lambda handler for FastAPI application
"""

import os
from mangum import Mangum
from main import app

# Ensure cache directories exist
os.makedirs("/tmp/hf", exist_ok=True)

# Create Mangum handler
handler = Mangum(app, lifespan="off") 