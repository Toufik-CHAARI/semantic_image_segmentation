#!/bin/bash

# Script pour exécuter les tests de l'application de segmentation sémantique

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si on est dans le bon répertoire
if [ ! -f "app.py" ]; then
    print_error "Ce script doit être exécuté depuis le répertoire racine du projet"
    exit 1
fi

# Vérifier si l'environnement virtuel est activé
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Environnement virtuel non détecté. Assurez-vous qu'il est activé."
fi

# Installer les dépendances de test si nécessaire
print_message "Vérification des dépendances de test..."
if ! pip show pytest > /dev/null 2>&1; then
    print_message "Installation des dépendances de test..."
    pip install -r requirements-test.txt
fi

# Fonction pour exécuter les tests
run_tests() {
    local test_type=$1
    local coverage=$2
    
    print_message "Exécution des tests $test_type..."
    
    if [ "$coverage" = "true" ]; then
        pytest tests/$test_type/ --cov=app --cov-report=html --cov-report=term -v
    else
        pytest tests/$test_type/ -v
    fi
}

# Fonction pour exécuter tous les tests
run_all_tests() {
    local coverage=$1
    
    print_message "Exécution de tous les tests..."
    
    if [ "$coverage" = "true" ]; then
        pytest tests/ --cov=app --cov-report=html --cov-report=term -v
    else
        pytest tests/ -v
    fi
}

# Fonction pour nettoyer les fichiers de couverture
clean_coverage() {
    print_message "Nettoyage des fichiers de couverture..."
    rm -rf htmlcov/
    rm -f .coverage
    print_success "Fichiers de couverture supprimés"
}

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help          Afficher cette aide"
    echo "  -c, --coverage      Inclure la couverture de code"
    echo "  --clean             Nettoyer les fichiers de couverture"
    echo ""
    echo "TEST_TYPE:"
    echo "  unit                Tests unitaires uniquement"
    echo "  integration         Tests d'intégration uniquement"
    echo "  all                 Tous les tests (par défaut)"
    echo ""
    echo "EXEMPLES:"
    echo "  $0                  Exécuter tous les tests"
    echo "  $0 unit             Exécuter les tests unitaires"
    echo "  $0 -c integration   Exécuter les tests d'intégration avec couverture"
    echo "  $0 --clean          Nettoyer les fichiers de couverture"
}

# Variables par défaut
TEST_TYPE="all"
COVERAGE="false"
CLEAN="false"

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--coverage)
            COVERAGE="true"
            shift
            ;;
        --clean)
            CLEAN="true"
            shift
            ;;
        unit|integration|all)
            TEST_TYPE="$1"
            shift
            ;;
        *)
            print_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Nettoyer si demandé
if [ "$CLEAN" = "true" ]; then
    clean_coverage
    exit 0
fi

# Exécuter les tests selon le type
case $TEST_TYPE in
    unit)
        run_tests "unit" "$COVERAGE"
        ;;
    integration)
        run_tests "integration" "$COVERAGE"
        ;;
    all)
        run_all_tests "$COVERAGE"
        ;;
    *)
        print_error "Type de test inconnu: $TEST_TYPE"
        exit 1
        ;;
esac

# Afficher le résultat
if [ $? -eq 0 ]; then
    print_success "Tous les tests ont réussi!"
    
    if [ "$COVERAGE" = "true" ]; then
        print_message "Rapport de couverture généré dans htmlcov/index.html"
    fi
else
    print_error "Certains tests ont échoué"
    exit 1
fi
