import io
import os
from typing import Tuple

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

from app.config import settings


class SegmentationService:
    def __init__(self):
        self.N_CLASSES = settings.N_CLASSES
        self.IMG_SIZE = settings.IMG_SIZE
        self.PALETTE = np.array(settings.PALETTE, np.uint8)
        self.CLASS_NAMES = settings.CLASS_NAMES
        self._model = None

    @property
    def model(self):
        """Charge le modèle de manière lazy"""
        if self._model is None:
            try:
                self._model = tf.keras.models.load_model(
                    settings.MODEL_PATH, compile=False
                )
            except Exception as e:
                # En mode test, on peut utiliser un mock ou lever une exception
                if os.getenv("TEST_MODE", "false").lower() == "true":
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
        img = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
        img = cv2.resize(img, (self.IMG_SIZE[1], self.IMG_SIZE[0]))
        return img.astype(np.float32) / 255.0

    def segment_image(self, image_bytes: bytes) -> Tuple[bytes, dict]:
        """Effectue la segmentation d'une image et retourne le résultat encodé en PNG"""
        # Prétraitement
        x = self.preprocess_image(image_bytes)[None, ...]

        # Prédiction
        out = self.model.predict(x)[0]  # (H,W,8)
        ids = np.argmax(out, -1).astype(np.uint8)
        color = self.PALETTE[ids]

        # Encodage PNG en mémoire
        _, buf = cv2.imencode(".png", cv2.cvtColor(color, cv2.COLOR_RGB2BGR))

        # Statistiques de segmentation
        stats = self._get_segmentation_stats(ids)

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
