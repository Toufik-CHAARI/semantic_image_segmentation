#!/bin/bash

# Script de configuration DVC avec S3
# Usage: ./scripts/setup_dvc_s3.sh <bucket-name> <aws-region>

set -e

BUCKET_NAME=${1:-"semantic-segmentation-models"}
AWS_REGION=${2:-"eu-west-3"}

echo "🚀 Configuration DVC avec S3..."
echo "📦 Bucket: $BUCKET_NAME"
echo "🌍 Région: $AWS_REGION"

# Vérifier que AWS CLI est configuré
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI n'est pas installé. Installez-le d'abord."
    exit 1
fi

# Vérifier les credentials AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials non configurés."
    echo "💡 Options de configuration :"
    echo "   1. aws configure (pour développement local)"
    echo "   2. Variables d'environnement (pour CI/CD)"
    echo "   3. IAM roles (pour EC2/ECS)"
    exit 1
fi

# Créer le bucket S3 s'il n'existe pas
echo "📦 Création du bucket S3..."
aws s3 mb "s3://$BUCKET_NAME" --region "$AWS_REGION" || echo "Bucket existe déjà"

# Configurer DVC remote S3
echo "🔗 Configuration du remote DVC..."
dvc remote add s3-remote "s3://$BUCKET_NAME/models" --default

# Configurer les options S3
dvc remote modify s3-remote region "$AWS_REGION"
dvc remote modify s3-remote profile default

echo "✅ Configuration terminée !"
echo ""
echo "📋 Commandes utiles :"
echo "  dvc push                    # Pousser le modèle vers S3"
echo "  dvc pull                    # Télécharger le modèle depuis S3"
echo "  dvc status                  # Vérifier le statut"
echo "  dvc remote list             # Lister les remotes"
echo ""
echo "🔧 Configuration actuelle :"
dvc remote list
