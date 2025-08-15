# app/services/segmentation_service.py
import io
import os
from typing import Tuple

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

from app.config import settings

# Import boto3 conditionally for AWS Lambda environment
try:

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class SegmentationService:
    def __init__(self):
        self.N_CLASSES = settings.N_CLASSES
        self.IMG_SIZE = settings.IMG_SIZE
        self.PALETTE = np.array(settings.PALETTE, np.uint8)
        self.CLASS_NAMES = settings.CLASS_NAMES
        self._model = None

    def _check_model_exists(self):
        """Vérifie que le modèle existe dans l'image Docker"""
        if not os.path.exists(settings.MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at {settings.MODEL_PATH}. "
                "The model should be included in the Docker image."
            )

    @property
    def model(self):
        """Charge le modèle de manière lazy"""
        if self._model is None:
            try:
                print(f"Loading model from: {settings.MODEL_PATH}")
                print(f"Model file exists: {os.path.exists(settings.MODEL_PATH)}")

                # Vérifier que le modèle existe dans l'image Docker
                self._check_model_exists()

                # Load the model
                self._model = tf.keras.models.load_model(
                    settings.MODEL_PATH, compile=False
                )
                print("Model loaded successfully")

            except Exception as e:
                print(f"Error loading model: {e}")
                # En mode test, on peut utiliser un mock
                if os.getenv("TEST_MODE", "false").lower() == "true":
                    print("Using mock model for test mode")
                    # Créer un modèle mock pour les tests
                    from unittest.mock import Mock

                    mock_model = Mock()
                    mock_model.predict.return_value = [
                        np.random.rand(*self.IMG_SIZE, self.N_CLASSES)
                    ]
                    self._model = mock_model
                else:
                    raise e
        return self._model

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Prétraite une image à partir de bytes"""
        try:
            print(f"Preprocessing image of {len(image_bytes)} bytes")

            # Try multiple approaches for Lambda compatibility
            try:
                # Method 1: Direct PIL approach
                img = Image.open(io.BytesIO(image_bytes))
            except Exception as e1:
                print(f"Method 1 failed: {e1}")
                try:
                    # Method 2: Convert to numpy first, then to PIL
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    img = Image.fromarray(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))
                except Exception as e2:
                    print(f"Method 2 failed: {e2}")
                    # Method 3: Use cv2 directly
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                    print(f"Image opened successfully with cv2: {img_array.shape}")
                    img_resized = cv2.resize(
                        img_array, (self.IMG_SIZE[1], self.IMG_SIZE[0])
                    )
                    print(f"Image resized to: {img_resized.shape}")
                    return img_resized.astype(np.float32) / 255.0

            print(f"Image opened successfully: {img.size} {img.mode}")
            img = img.convert("RGB")
            img_array = np.array(img)
            print(f"Image converted to array: {img_array.shape}")
            img_resized = cv2.resize(img_array, (self.IMG_SIZE[1], self.IMG_SIZE[0]))
            print(f"Image resized to: {img_resized.shape}")
            return img_resized.astype(np.float32) / 255.0
        except Exception as e:
            print(f"Error in preprocess_image: {e}")
            raise Exception(f"Error preprocessing image: {str(e)}")

    def segment_image(self, image_bytes: bytes) -> Tuple[bytes, dict]:
        """Effectue la segmentation d'une image et retourne le résultat encodé en PNG"""
        # print("Starting image segmentation...")
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Starting image segmentation...")

        # Prétraitement
        print("Preprocessing image...")
        x = self.preprocess_image(image_bytes)[None, ...]
        print(f"Preprocessed image shape: {x.shape}")

        # Prédiction
        model = self.model
        print(f"Model loaded: {type(model)}")

        print("Running prediction...")
        out = model.predict(x)[0]  # (H,W,8)
        print(f"Prediction output shape: {out.shape}")

        ids = np.argmax(out, -1).astype(np.uint8)
        print(f"Segmentation IDs shape: {ids.shape}")

        color = self.PALETTE[ids]
        print(f"Color image shape: {color.shape}")

        # Encodage PNG en mémoire
        print("Encoding PNG...")
        _, buf = cv2.imencode(".png", cv2.cvtColor(color, cv2.COLOR_RGB2BGR))
        print(f"PNG encoded, size: {len(buf.tobytes())} bytes")

        # Statistiques de segmentation
        print("Calculating statistics...")
        stats = self._get_segmentation_stats(ids)
        print(f"Statistics calculated: {stats}")

        print("Segmentation completed successfully")
        return buf.tobytes(), stats

    def _get_segmentation_stats(self, segmentation_ids: np.ndarray) -> dict:
        """Calcule les statistiques de segmentation"""
        total_pixels = segmentation_ids.size

        stats = {}
        for i, class_name in enumerate(self.CLASS_NAMES):
            pixel_count = np.sum(segmentation_ids == i)
            percentage = (pixel_count / total_pixels) * 100
            stats[class_name] = {
                "pixel_count": int(pixel_count),
                "percentage": round(percentage, 2),
            }

        return stats
