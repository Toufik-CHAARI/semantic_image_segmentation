import os
from datetime import datetime

import tensorflow as tf
from fastapi import APIRouter

from app.schemas.responses import HealthResponse, InfoResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    """API Health Endpoint"""
    return HealthResponse(
        status="healthy",
        message="Service is operational",
        timestamp=datetime.now().isoformat(),
    )


@router.get("/info", response_model=InfoResponse)
async def info():
    """API Info Endpoint"""
    # check if model exists and get model info
    from app.config import settings

    model_path = settings.MODEL_PATH
    model_exists = os.path.exists(model_path)

    model_info = {
        "name": "U-Net for Cityscapes",
        "classes": 8,
        "input_size": (256, 512),
        "model_loaded": model_exists,
        "model_path": model_path,
    }

    if model_exists:
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            model_info["model_summary"] = str(model.summary(print_fn=lambda x: None))
            model_info["total_params"] = model.count_params()
        except Exception as e:
            model_info["error"] = str(e)

    return InfoResponse(
        name="Cityscapes Semantic Segmentation API",
        version="1.0.0",
        description=(
            "API for semantic segmentation of urban images " "using a U-Net model"
        ),
        model_info=model_info,
        endpoints=[
            "GET / - Home page",
            "GET /health - Health check",
            "GET /info - API information",
            "POST /segment - Image segmentation",
        ],
    )
