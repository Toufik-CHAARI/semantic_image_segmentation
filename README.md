# 🚀 API de Segmentation Sémantique - Cityscapes

API FastAPI pour la segmentation sémantique d'images urbaines utilisant un modèle U-Net.

## 📊 Métriques de Qualité

- **Couverture de code** : 95%
- **Tests unitaires** : 35 tests
- **Tests d'intégration** : 33 tests
- **Total** : 68 tests

## 🏗️ Architecture

```
semantic_image_segmentation/
├── app/                          # Application principale
│   ├── api/                      # Routes API
│   │   ├── health.py            # Endpoints de santé
│   │   └── segmentation.py      # Endpoints de segmentation
│   ├── services/                 # Logique métier
│   │   └── segmentation_service.py
│   ├── schemas/                  # Modèles Pydantic
│   │   └── responses.py
│   ├── config.py                 # Configuration
│   └── main.py                   # Point d'entrée
├── tests/                        # Suite de tests
│   ├── unit/                     # Tests unitaires
│   ├── integration/              # Tests d'intégration
│   └── conftest.py              # Configuration pytest
├── model/                        # Modèle U-Net
├── scripts/                      # Scripts utilitaires
└── Makefile                     # Commandes automatisées
```

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.12+
- Environnement virtuel activé

### Installation
```bash
# Activer l'environnement virtuel
source env/bin/activate

# Vérifier l'installation
make check-install
```

### Démarrage
```bash
# Mode développement
make dev

# Mode production
make run
```

L'API sera disponible sur `http://localhost:8000`

## 📚 Documentation API

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI** : http://localhost:8000/openapi.json

## 🧪 Tests

### Commandes Principales
```bash
# Tous les tests
make test

# Tests unitaires uniquement
make test-unit

# Tests d'intégration uniquement
make test-integration

# Tests avec couverture
make test-coverage
```

### Tests Spécialisés
```bash
# Tests de performance
make test-performance

# Tests des schémas
make test-schemas

# Tests du service
make test-service

# Tests des endpoints
make test-endpoints

# Tests rapides (sans tests lents)
make test-fast
```

## 🐳 Docker

### Construction et Exécution
```bash
# Construire l'image
make docker-build

# Démarrer le conteneur
make docker-run

# Arrêter le conteneur
make docker-stop
```

### Tests avec Docker
```bash
# Construire l'image de test
make docker-build-test

# Exécuter les tests
make docker-test
```

## 🎨 Qualité du Code

### Vérifications
```bash
# Vérification complète
make quality-check

# Linting
make lint

# Formatage
make format

# Scan de sécurité
make security-scan
```

## 🧹 Nettoyage

```bash
# Nettoyer les fichiers de test
make clean

# Nettoyer Docker
make clean-docker

# Nettoyage complet
make clean-all
```

## 📋 Endpoints Disponibles

### Endpoints de Base
- `GET /` - Page d'accueil
- `GET /health` - Vérification de santé
- `GET /info` - Informations sur l'API

### Endpoints de Segmentation
- `POST /api/segment` - Segmentation d'image (retourne l'image)
- `POST /api/segment-with-stats` - Segmentation avec statistiques

## 🔧 Configuration

L'application utilise des variables d'environnement :

```bash
HOST=0.0.0.0          # Hôte d'écoute
PORT=8000             # Port d'écoute
RELOAD=true           # Rechargement automatique
LOG_LEVEL=info        # Niveau de log
```

## 📈 Performance

- **Temps de réponse** : < 2s pour la segmentation
- **Requêtes concurrentes** : Support de 10+ requêtes simultanées
- **Images volumineuses** : Support jusqu'à 2048x2048 pixels

## 🛠️ Développement

### Structure des Tests
```
tests/
├── unit/                     # Tests unitaires
│   ├── test_config.py       # Tests de configuration
│   ├── test_schemas.py      # Tests des schémas
│   └── test_segmentation_service.py
├── integration/              # Tests d'intégration
│   ├── test_api_endpoints.py
│   ├── test_full_application.py
│   └── test_performance.py
└── conftest.py              # Fixtures communes
```

### 🗄️ Gestion des Modèles avec DVC

Le projet utilise DVC pour versionner et stocker le modèle U-Net dans AWS S3 :

```bash
# Configuration DVC avec S3
make dvc-setup-s3

# Pousser le modèle vers S3
make dvc-push

# Télécharger le modèle depuis S3
make dvc-pull

# Vérifier le statut
make dvc-status
```

**📖 Documentation complète :** Voir `DVC_README.md`

### Ajout de Nouveaux Tests
1. Créer le fichier de test dans le bon dossier
2. Utiliser les fixtures communes de `conftest.py`
3. Suivre les conventions de nommage
4. Ajouter les marqueurs appropriés (`@pytest.mark.slow` si nécessaire)

## 📊 Couverture de Code

```bash
# Générer le rapport de couverture
make test-coverage

# Ouvrir le rapport HTML
open htmlcov/index.html
```

## 🚨 Gestion d'Erreurs

L'API inclut une gestion d'erreurs robuste :
- Validation des types de fichiers
- Gestion des erreurs de segmentation
- Messages d'erreur informatifs
- Codes de statut HTTP appropriés

## 🔒 Sécurité

- Validation des entrées avec Pydantic
- Scan de sécurité avec Bandit
- Headers CORS configurables
- Validation des types de fichiers

## 📝 Logs

L'application génère des logs détaillés :
- Démarrage et arrêt de l'application
- Temps de traitement des requêtes
- Erreurs et exceptions
- Statistiques de segmentation

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Ajouter les tests correspondants
4. Vérifier la qualité du code : `make quality-check`
5. Soumettre une pull request

## 📄 Licence

Ce projet est sous licence MIT.

## 🆘 Support

Pour toute question ou problème :
1. Consulter la documentation API
2. Vérifier les logs de l'application
3. Exécuter les tests : `make test`
4. Ouvrir une issue sur GitHub

---

**Développé avec ❤️ pour la segmentation sémantique d'images urbaines**