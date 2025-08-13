.PHONY: test test-unit test-integration test-coverage install-test clean run dev

# Variables
PYTHON = python
PIP = pip
PYTEST = python -m pytest
APP_NAME = semantic-image-segmentation-api
ENVIRONMENT ?= mvp
AWS_REGION = eu-west-3
AWS_ACCOUNT_ID = 024848440742

# Environment validation
ifeq ($(filter $(ENVIRONMENT),mvp staging production),)
    $(error ENVIRONMENT must be one of: mvp, staging, production)
endif

# Installation des dépendances de test
install-test:
	@echo "Vérification des dépendances de test..."
	@$(PIP) show pytest > /dev/null 2>&1 || $(PIP) install -r requirements-dev.txt

# Installation des dépendances de production
install:
	@echo "Installation des dépendances de production..."
	$(PIP) install -r requirements.txt

# Installation des dépendances de développement
install-dev:
	@echo "Installation des dépendances de développement..."
	$(PIP) install -r requirements-dev.txt

# Exécution de tous les tests
test: install-test
	$(PYTEST) tests/ -v

# Tests unitaires uniquement
test-unit: install-test
	$(PYTEST) tests/unit/ -v

# Tests d'intégration uniquement
test-integration: install-test
	$(PYTEST) tests/integration/ -v

# Tests avec couverture de code
test-coverage: install-test
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term

# Tests avec couverture détaillée
test-coverage-detail: install-test
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term --cov-report=xml

# Tests de performance uniquement
test-performance: install-test
	$(PYTEST) tests/integration/test_performance.py -v

# Tests de validation des schémas
test-schemas: install-test
	$(PYTEST) tests/unit/test_schemas.py -v

# Tests du service de segmentation
test-service: install-test
	$(PYTEST) tests/unit/test_segmentation_service.py -v

# Tests de configuration
test-config: install-test
	$(PYTEST) tests/unit/test_config.py -v

# Tests des endpoints API
test-endpoints: install-test
	$(PYTEST) tests/integration/test_api_endpoints.py -v

# Tests de l'application complète
test-full-app: install-test
	$(PYTEST) tests/integration/test_full_application.py -v

# Tests rapides (sans les tests lents)
test-fast: install-test
	$(PYTEST) tests/ -m "not slow" -v

# Tests lents uniquement
test-slow: install-test
	$(PYTEST) tests/ -m "slow" -v

# Tests avec arrêt au premier échec
test-fail-fast: install-test
	$(PYTEST) tests/ -x -v

# Tests avec plus de détails
test-verbose: install-test
	$(PYTEST) tests/ -v -s --tb=long

# Tests avec rapport HTML
test-html: install-test
	$(PYTEST) tests/ --html=reports/test-report.html --self-contained-html

# Démarrer l'application en mode développement
dev:
	$(PYTHON) app.py

# Démarrer l'application en mode production
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker commands
docker-build:
	docker build -t $(APP_NAME):$(ENVIRONMENT) .

docker-build-test:
	cp .dockerignore .dockerignore.backup && \
	cp .dockerignore.test .dockerignore && \
	docker build -f Dockerfile.test -t $(APP_NAME):test . && \
	mv .dockerignore.backup .dockerignore

docker-build-lambda:
	docker build -f Dockerfile.lambda -t $(APP_NAME)-lambda:$(ENVIRONMENT) .

# Build all Docker images for development
docker-build-all:
	@echo "🏗️ Building all Docker images for development..."
	@echo "📦 Building production image..."
	@make docker-build
	@echo "🧪 Building test image..."
	@make docker-build-test
	@echo "☁️ Building Lambda image..."
	@make docker-build-lambda
	@echo "✅ All images built successfully!"
	@echo ""
	@echo "📊 Image summary:"
	@docker images | grep $(APP_NAME) || echo "No images found"

# Build and deploy Lambda for specific environment
docker-deploy-lambda:
	@echo "🚀 Building and deploying Lambda for environment: $(ENVIRONMENT)"
	@make docker-build-lambda
	@make docker-push-ecr-lambda
	@echo "✅ Lambda deployment completed for $(ENVIRONMENT)"

# Docker registry commands
docker-tag:
	@echo "Tagging images for registry..."
	@read -p "Enter registry URL (e.g., your-registry.com/username): " registry; \
	docker tag $(APP_NAME):latest $$registry/$(APP_NAME):latest; \
	docker tag $(APP_NAME):test $$registry/$(APP_NAME):test; \
	docker tag $(APP_NAME)-lambda:latest $$registry/$(APP_NAME)-lambda:latest; \
	echo "Images tagged with: $$registry"

docker-push:
	@echo "Pushing images to registry..."
	@read -p "Enter registry URL (e.g., your-registry.com/username): " registry; \
	docker push $$registry/$(APP_NAME):latest; \
	docker push $$registry/$(APP_NAME):test; \
	docker push $$registry/$(APP_NAME)-lambda:latest; \
	echo "All images pushed to: $$registry"

docker-push-main:
	@echo "Pushing main image to registry..."
	@read -p "Enter registry URL (e.g., your-registry.com/username): " registry; \
	docker tag $(APP_NAME):latest $$registry/$(APP_NAME):latest; \
	docker push $$registry/$(APP_NAME):latest; \
	echo "Main image pushed to: $$registry"

# AWS ECR commands
docker-push-ecr:
	@echo "Pushing production image to AWS ECR..."
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag $(APP_NAME):$(ENVIRONMENT) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME):$(ENVIRONMENT)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME):$(ENVIRONMENT)
	@echo "✅ Production image pushed to ECR: $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME):$(ENVIRONMENT)"

docker-push-ecr-lambda:
	@echo "Pushing Lambda image to AWS ECR..."
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag $(APP_NAME)-lambda:$(ENVIRONMENT) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ENVIRONMENT)-semantic-image-segmentation-api:$(ENVIRONMENT)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ENVIRONMENT)-semantic-image-segmentation-api:$(ENVIRONMENT)
	@echo "✅ Lambda image pushed to ECR: $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ENVIRONMENT)-semantic-image-segmentation-api:$(ENVIRONMENT)"

docker-push-ecr-all:
	@echo "Pushing all images to AWS ECR..."
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag $(APP_NAME):$(ENVIRONMENT) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME):$(ENVIRONMENT)
	docker tag $(APP_NAME):test $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME):test
	docker tag $(APP_NAME)-lambda:$(ENVIRONMENT) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ENVIRONMENT)-semantic-image-segmentation-api:$(ENVIRONMENT)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME):$(ENVIRONMENT)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME):test
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ENVIRONMENT)-semantic-image-segmentation-api:$(ENVIRONMENT)
	@echo "✅ All images pushed to ECR"

docker-run:
	docker run -d --name $(APP_NAME) -p 8000:8000 $(APP_NAME):latest

docker-stop:
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

docker-test:
	docker run --rm $(APP_NAME):test

# Test all Docker images
docker-test-all:
	@echo "🧪 Testing all Docker images..."
	@echo ""
	@echo "📦 Testing production image..."
	@docker run --rm -d --name test-prod -p 8001:8000 $(APP_NAME):$(ENVIRONMENT) || true
	@sleep 10
	@curl -f http://localhost:8001/health > /dev/null 2>&1 && echo "✅ Production image: HEALTH OK" || echo "❌ Production image: HEALTH FAILED"
	@docker stop test-prod > /dev/null 2>&1 || true
	@docker rm test-prod > /dev/null 2>&1 || true
	@echo ""
	@echo "🧪 Testing test image..."
	@docker run --rm -d --name test-test -p 8002:8000 $(APP_NAME):test || true
	@sleep 10
	@curl -f http://localhost:8002/health > /dev/null 2>&1 && echo "✅ Test image: HEALTH OK" || echo "❌ Test image: HEALTH FAILED"
	@docker stop test-test > /dev/null 2>&1 || true
	@docker rm test-test > /dev/null 2>&1 || true
	@echo ""
	@echo "☁️ Testing Lambda image..."
	@docker run --rm -d --name test-lambda -p 8003:8080 $(APP_NAME)-lambda:$(ENVIRONMENT) || true
	@sleep 5
	@docker logs test-lambda | grep -q "rapid" && echo "✅ Lambda image: RUNTIME OK" || echo "❌ Lambda image: RUNTIME FAILED"
	@docker stop test-lambda > /dev/null 2>&1 || true
	@docker rm test-lambda > /dev/null 2>&1 || true
	@echo ""
	@echo "🎉 All Docker images tested!"

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

docker-compose-test:
	docker-compose run --rm semantic-image-segmentation-api-test

# Linting and formatting
lint:
	flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format:
	black app/ tests/
	isort app/ tests/

format-check:
	black --check app/ tests/
	isort --check-only app/ tests/

security-scan:
	bandit -r app/ -f json -o bandit-report.json

# Vérification de la qualité du code
quality-check: lint format-check test-coverage security-scan

# Complete development workflow - build, test, and validate all images
dev-workflow:
	@echo "🚀 Starting complete development workflow..."
	@echo "================================================"
	@echo ""
	@echo "1️⃣ Running code quality checks..."
	@make quality-check
	@echo ""
	@echo "2️⃣ Building all Docker images..."
	@make docker-build-all
	@echo ""
	@echo "3️⃣ Testing all Docker images..."
	@make docker-test-all
	@echo ""
	@echo "4️⃣ Running full test suite..."
	@make test-coverage-detail
	@echo ""
	@echo "🎉 Development workflow completed successfully!"
	@echo "All images are ready for deployment!"

# Nettoyage des fichiers de test
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf reports/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Nettoyage Docker
clean-docker:
	docker system prune -f
	docker image prune -f

# Nettoyage complet
clean-all: clean clean-docker

# Vérification de l'installation
check-install:
	@echo "Vérification de l'installation..."
	@$(PYTHON) -c "import fastapi, tensorflow, numpy, cv2, PIL; print('✅ Toutes les dépendances sont installées')"

# Vérification de la santé de l'API
health-check:
	@echo "Vérification de la santé de l'API..."
	@curl -f http://localhost:8000/health || echo "❌ L'API n'est pas accessible"

# Génération de la documentation
docs:
	@echo "Génération de la documentation..."
	@mkdir -p docs
	@pydoc-markdown --render-toc --output-file docs/API.md app/

# DVC commands
dvc-setup-s3:
	@echo "Configuration DVC avec S3..."
	@./scripts/setup_dvc_s3.sh

dvc-push:
	@echo "Pousser le modèle vers S3..."
	dvc push

dvc-pull:
	@echo "Télécharger le modèle depuis S3..."
	dvc pull

dvc-status:
	@echo "Statut DVC..."
	dvc status

dvc-remote-list:
	@echo "Liste des remotes DVC..."
	dvc remote list

# Aide
help:
	@echo "🚀 Commandes disponibles pour l'API de Segmentation Sémantique"
	@echo ""
	@echo "📊 Tests:"
	@echo "  make test              - Exécuter tous les tests"
	@echo "  make test-unit         - Tests unitaires uniquement"
	@echo "  make test-integration  - Tests d'intégration uniquement"
	@echo "  make test-coverage     - Tests avec couverture de code (95%)"
	@echo "  make test-performance  - Tests de performance"
	@echo "  make test-schemas      - Tests des schémas Pydantic"
	@echo "  make test-service      - Tests du service de segmentation"
	@echo "  make test-config       - Tests de configuration"
	@echo "  make test-endpoints    - Tests des endpoints API"
	@echo "  make test-full-app     - Tests de l'application complète"
	@echo "  make test-fast         - Tests rapides (sans tests lents)"
	@echo "  make test-slow         - Tests lents uniquement"
	@echo "  make test-fail-fast    - Tests avec arrêt au premier échec"
	@echo "  make test-verbose      - Tests avec plus de détails"
	@echo "  make test-html         - Tests avec rapport HTML"
	@echo ""
	@echo "🏃‍♂️ Exécution:"
	@echo "  make dev               - Démarrer en mode développement"
	@echo "  make run               - Démarrer en mode production"
	@echo "  make check-install     - Vérifier l'installation"
	@echo "  make health-check      - Vérifier la santé de l'API"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build      - Construire l'image Docker"
	@echo "  make docker-build-test - Construire l'image de test"
	@echo "  make docker-build-lambda - Construire l'image Lambda"
	@echo "  make docker-build-all - Construire toutes les images Docker"
	@echo "  make docker-test-all - Tester toutes les images Docker"
	@echo "  make docker-deploy-lambda - Construire et déployer Lambda (ENVIRONMENT=mvp|staging|production)"
	@echo "  make docker-push-ecr-lambda - Pousser l'image Lambda vers ECR"
	@echo "  make docker-run        - Démarrer le conteneur"
	@echo "  make docker-stop       - Arrêter le conteneur"
	@echo "  make docker-test       - Tester l'image Docker"
	@echo "  make docker-tag        - Tagger les images pour le registry"
	@echo "  make docker-push       - Pousser toutes les images"
	@echo "  make docker-push-main  - Pousser l'image principale"
	@echo "  make docker-push-ecr   - Pousser l'image vers AWS ECR"
	@echo "  make docker-push-ecr-all - Pousser toutes les images vers ECR"
	@echo "  make docker-compose-up - Démarrer avec docker-compose"
	@echo "  make docker-compose-down - Arrêter docker-compose"
	@echo "  make docker-compose-test - Tests avec docker-compose"
	@echo ""
	@echo "🎨 Qualité du Code:"
	@echo "  make lint              - Vérifier le style de code"
	@echo "  make format            - Formater le code"
	@echo "  make format-check      - Vérifier le formatage"
	@echo "  make security-scan     - Scan de sécurité"
	@echo "  make quality-check     - Vérification complète de la qualité"
	@echo "  make dev-workflow      - Workflow complet de développement"
	@echo ""
	@echo "🧹 Nettoyage:"
	@echo "  make clean             - Nettoyer les fichiers de test"
	@echo "  make clean-docker      - Nettoyer Docker"
	@echo "  make clean-all         - Nettoyage complet"
	@echo "  make install           - Installer les dépendances de production"
	@echo "  make install-dev       - Installer les dépendances de développement"
	@echo "  make install-test      - Installer les dépendances de test"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  make docs              - Générer la documentation"
	@echo ""
	@echo "🗄️ DVC (Data Version Control):"
	@echo "  make dvc-setup-s3      - Configurer DVC avec S3"
	@echo "  make dvc-push          - Pousser le modèle vers S3"
	@echo "  make dvc-pull          - Télécharger le modèle depuis S3"
	@echo "  make dvc-status        - Vérifier le statut DVC"
	@echo "  make dvc-remote-list   - Lister les remotes DVC"
	@echo ""
	@echo "📈 Métriques:"
	@echo "  - Couverture de code: 95%"
	@echo "  - Tests unitaires: 35"
	@echo "  - Tests d'intégration: 33"
	@echo "  - Total: 68 tests"
	@echo ""
	@echo "  make help              - Afficher cette aide" 