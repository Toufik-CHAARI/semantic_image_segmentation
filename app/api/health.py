from fastapi import APIRouter
from datetime import datetime
from app.schemas.responses import HealthResponse, InfoResponse
import tensorflow as tf
import os

router = APIRouter()



@router.get("/health", response_model=HealthResponse)
async def health():
    """Endpoint de santé alternatif"""
    return HealthResponse(
        status="healthy",
        message="Service is operational",
        timestamp=datetime.now().isoformat()
    )

@router.get("/info", response_model=InfoResponse)
async def info():
    """Endpoint d'information sur l'API et le modèle"""
    # Vérifier si le modèle existe
    model_path = "model/unet_best.keras"
    model_exists = os.path.exists(model_path)
    
    model_info = {
        "name": "U-Net for Cityscapes",
        "classes": 8,
        "input_size": (256, 512),
        "model_loaded": model_exists,
        "model_path": model_path
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
        description="API de segmentation sémantique pour les images urbaines utilisant un modèle U-Net",
        model_info=model_info,
        endpoints=[
            "GET / - Page d'accueil",
            "GET /health - Vérification de santé",
            "GET /info - Informations sur l'API",
            "POST /segment - Segmentation d'image"
        ]
    )
