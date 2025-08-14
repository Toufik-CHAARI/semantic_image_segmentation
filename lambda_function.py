# lambda_function.py
"""
Lambda handler for Semantic Image Segmentation API
"""

import os
import sys
from pathlib import Path

# If app/ isn't a package, ensure it's on sys.path
sys.path.append(str(Path(__file__).parent / "app"))

# Quiet TF + ensure temp dir for joblib (writes must be under /tmp on Lambda)
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("JOBLIB_TEMP_FOLDER", "/tmp")

from mangum import Mangum
from app.main import app


handler = Mangum(app, lifespan="off")