# app/services/model_loader.py
import os

from app.config import settings


def is_model_loaded():
    """Check if the model file exists and can be loaded"""
    try:
        # Check if the model file exists
        if not os.path.exists(settings.MODEL_PATH):
            return False

        # Try to load the model to verify it's valid
        import tensorflow as tf

        model = tf.keras.models.load_model(settings.MODEL_PATH, compile=False)
        return model is not None
    except Exception as e:
        print(f"Model loading check failed: {e}")
        return False
