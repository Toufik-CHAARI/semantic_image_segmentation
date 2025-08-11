#!/bin/bash

# Script de déploiement pour l'API d'analyse de sentiment

set -e

# Variables
IMAGE_NAME="sentiment-analysis-api"
TAG=${1:-latest}
REGISTRY=${2:-""}

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé"
    exit 1
fi

# Vérifier que le modèle existe
if [ ! -d "models/" ]; then
    log_error "Le dossier models/ n'existe pas"
    exit 1
fi

# Fonction pour construire l'image
build_image() {
    log_info "Construction de l'image Docker..."
    docker build -t ${IMAGE_NAME}:${TAG} .
    
    if [ $? -eq 0 ]; then
        log_info "Image construite avec succès: ${IMAGE_NAME}:${TAG}"
    else
        log_error "Échec de la construction de l'image"
        exit 1
    fi
}

# Fonction pour tester l'image
test_image() {
    log_info "Test de l'image Docker..."
    
    # Démarrer le conteneur
    docker run -d --name test-${IMAGE_NAME} -p 8000:8000 ${IMAGE_NAME}:${TAG}
    
    # Attendre que l'application démarre
    sleep 10
    
    # Tester les endpoints
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Health check réussi"
    else
        log_error "Health check échoué"
        docker stop test-${IMAGE_NAME}
        docker rm test-${IMAGE_NAME}
        exit 1
    fi
    
    if curl -f http://localhost:8000/info > /dev/null 2>&1; then
        log_info "Info endpoint fonctionne"
    else
        log_error "Info endpoint échoué"
        docker stop test-${IMAGE_NAME}
        docker rm test-${IMAGE_NAME}
        exit 1
    fi
    
    # Nettoyer
    docker stop test-${IMAGE_NAME}
    docker rm test-${IMAGE_NAME}
    log_info "Tests réussis"
}

# Fonction pour pousser l'image vers le registry
push_image() {
    if [ -n "$REGISTRY" ]; then
        log_info "Tag de l'image pour le registry..."
        docker tag ${IMAGE_NAME}:${TAG} ${REGISTRY}/${IMAGE_NAME}:${TAG}
        
        log_info "Push de l'image vers le registry..."
        docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}
        
        if [ $? -eq 0 ]; then
            log_info "Image poussée avec succès: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
        else
            log_error "Échec du push de l'image"
            exit 1
        fi
    else
        log_warn "Aucun registry spécifié, skip du push"
    fi
}

# Fonction pour nettoyer les images
cleanup() {
    log_info "Nettoyage des images..."
    docker rmi ${IMAGE_NAME}:${TAG} 2>/dev/null || true
    if [ -n "$REGISTRY" ]; then
        docker rmi ${REGISTRY}/${IMAGE_NAME}:${TAG} 2>/dev/null || true
    fi
}

# Fonction d'aide
show_help() {
    echo "Usage: $0 [TAG] [REGISTRY]"
    echo ""
    echo "Options:"
    echo "  TAG       Tag de l'image (défaut: latest)"
    echo "  REGISTRY  Registry Docker (optionnel)"
    echo ""
    echo "Exemples:"
    echo "  $0                    # Build avec tag 'latest'"
    echo "  $0 v1.0.0           # Build avec tag 'v1.0.0'"
    echo "  $0 v1.0.0 my-registry.com  # Build et push vers le registry"
}

# Main
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
    esac
    
    log_info "Début du déploiement..."
    
    # Construire l'image
    build_image
    
    # Tester l'image
    test_image
    
    # Pousser vers le registry si spécifié
    push_image
    
    log_info "Déploiement terminé avec succès!"
}

# Exécuter le script principal
main "$@" 