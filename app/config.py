import os
from typing import List


class Settings:
    """Configuration de l'application"""

    # Informations de l'API
    API_TITLE = "Cityscapes Semantic Segmentation API"
    API_DESCRIPTION = (
        "API de segmentation sémantique pour les images urbaines "
        "utilisant un modèle U-Net"
    )
    API_VERSION = "1.0.0"

    # Configuration du modèle
    MODEL_PATH = "model/V3_unet_best.keras"
    N_CLASSES = 8
    IMG_SIZE = (256, 512)

    # Palette de couleurs pour la segmentation
    PALETTE = [
        [128, 64, 128],  # road
        [220, 20, 60],  # building
        [0, 0, 142],  # car
        [70, 70, 70],  # traffic sign
        [190, 153, 153],  # person
        [107, 142, 35],  # vegetation
        [70, 130, 180],  # sky
        [0, 0, 0],  # background
    ]

    # Noms des classes
    CLASS_NAMES = [
        "road",
        "building",
        "car",
        "traffic_sign",
        "person",
        "vegetation",
        "sky",
        "background",
    ]

    # Configuration CORS
    CORS_ORIGINS: List[str] = ["*"]  # En production, spécifiez les domaines autorisés

    # Configuration du serveur
    HOST = os.getenv("HOST", "0.0.0.0")

    @property
    def PORT(self) -> int:
        port_str = os.getenv("PORT", "8000")
        try:
            return int(port_str)
        except ValueError:
            raise ValueError(f"Invalid PORT value: {port_str}")

    @property
    def RELOAD(self) -> bool:
        reload_str = os.getenv("RELOAD", "true")
        return reload_str.lower() in ("true", "1", "yes", "on")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")


# Instance globale des paramètres
settings = Settings()
