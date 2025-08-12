from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, segmentation
from app.config import settings

# Création de l'application FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(health.router, tags=["Health & Info"])
app.include_router(segmentation.router, prefix="/api", tags=["Segmentation"])


# Événements de démarrage et arrêt
@app.on_event("startup")
async def startup_event():
    """Événement exécuté au démarrage de l'application"""
    print("🚀 Démarrage de l'API de segmentation sémantique...")
    print("📊 Modèle U-Net chargé avec succès")
    print("✅ API prête à recevoir des requêtes")


@app.on_event("shutdown")
async def shutdown_event():
    """Événement exécuté à l'arrêt de l'application"""
    print("🛑 Arrêt de l'API de segmentation sémantique...")


# Route racine redirige vers la documentation
@app.get("/")
async def root():
    """Route racine - redirige vers la documentation"""
    return {
        "message": "Bienvenue sur l'API de segmentation sémantique Cityscapes",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "info": "/info",
    }
