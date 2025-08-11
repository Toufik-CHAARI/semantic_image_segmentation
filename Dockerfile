# Multi-stage build pour optimiser la taille de l'image
FROM python:3.12-slim as builder

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage de production
FROM python:3.12-slim as production

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Créer un utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Créer le répertoire de travail
WORKDIR /app

# Copier les dépendances Python installées depuis le builder
COPY --from=builder /root/.local /home/appuser/.local

# Copier uniquement les fichiers nécessaires pour la production
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser lambda_function.py .
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser models/ ./models/

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Créer un cache HuggingFace accessible
RUN mkdir -p /app/cache && chown -R appuser:appuser /app/cache
ENV TRANSFORMERS_CACHE=/tmp/hf \
    HF_HOME=/tmp/hf \
    HF_DATASETS_CACHE=/tmp/hf \
    HF_METRICS_CACHE=/tmp/hf \
    XDG_CACHE_HOME=/tmp/hf \
    TMPDIR=/tmp

RUN mkdir -p /tmp/hf

# Changer vers l'utilisateur non-root
USER appuser

# Exposer le port
EXPOSE 8000

# Variables d'environnement pour la production
ENV HOST=0.0.0.0 \
    PORT=8000 \
    WORKERS=4 \
    LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage pour FastAPI
CMD ["python", "main.py"] 