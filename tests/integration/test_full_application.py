import io
import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


class TestFullApplication:
    """Tests d'intégration pour l'application complète"""

    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        return TestClient(app)

    @pytest.fixture
    def temp_model_file(self):
        """Créer un fichier modèle temporaire pour les tests"""
        with tempfile.NamedTemporaryFile(suffix=".keras", delete=False) as tmp_file:
            # Créer un modèle simple pour les tests
            import tensorflow as tf

            # Créer un modèle U-Net simple
            inputs = tf.keras.layers.Input(shape=(256, 512, 3))
            x = tf.keras.layers.Conv2D(8, (3, 3), activation="relu", padding="same")(
                inputs
            )
            x = tf.keras.layers.Conv2D(8, (1, 1), activation="softmax")(x)
            model = tf.keras.Model(inputs=inputs, outputs=x)

            model.save(tmp_file.name)
            yield tmp_file.name

        # Nettoyer après les tests
        if os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)

    @pytest.fixture
    def sample_image(self):
        """Créer une image de test réaliste"""
        # Créer une image qui ressemble à une scène urbaine
        img = Image.new("RGB", (512, 256), color="gray")

        # Ajouter quelques éléments pour simuler une scène urbaine
        # Route (bas de l'image)
        for x in range(512):
            for y in range(200, 256):
                img.putpixel((x, y), (128, 64, 128))  # Couleur de la route

        # Bâtiments (haut de l'image)
        for x in range(512):
            for y in range(0, 100):
                img.putpixel((x, y), (220, 20, 60))  # Couleur des bâtiments

        # Ciel (coin supérieur)
        for x in range(512):
            for y in range(0, 50):
                img.putpixel((x, y), (70, 130, 180))  # Couleur du ciel

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def test_application_startup(self, client):
        """Test que l'application démarre correctement"""
        # Vérifier que l'application répond
        response = client.get("/")
        assert response.status_code == 200

        # Vérifier que la documentation est accessible
        response = client.get("/docs")
        assert response.status_code == 200

    def test_health_check_workflow(self, client):
        """Test du workflow de vérification de santé"""
        # Test de l'endpoint de santé
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

        # Test de l'endpoint d'information
        response = client.get("/info")
        assert response.status_code == 200

        data = response.json()
        assert "model_info" in data
        assert "endpoints" in data

    def test_segmentation_workflow_with_mock_model(self, client, sample_image):
        """Test du workflow de segmentation complet avec modèle mocké"""
        # Mock le service de segmentation
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            # Simuler une réponse de segmentation
            mock_stats = {
                "road": {"pixel_count": 14336, "percentage": 28.0},
                "building": {"pixel_count": 10240, "percentage": 20.0},
                "car": {"pixel_count": 5120, "percentage": 10.0},
                "traffic_sign": {"pixel_count": 2560, "percentage": 5.0},
                "person": {"pixel_count": 1280, "percentage": 2.5},
                "vegetation": {"pixel_count": 2560, "percentage": 5.0},
                "sky": {"pixel_count": 12800, "percentage": 25.0},
                "background": {"pixel_count": 1536, "percentage": 3.0},
            }

            # Créer une image segmentée mock
            segmented_img = Image.new("RGB", (512, 256), color="red")
            segmented_bytes = io.BytesIO()
            segmented_img.save(segmented_bytes, format="PNG")

            mock_service.return_value = (segmented_bytes.getvalue(), mock_stats)

            # Test de l'endpoint de segmentation
            files = {"file": ("test_image.png", sample_image, "image/png")}
            response = client.post("/api/segment", files=files)

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

            # Test de l'endpoint avec statistiques
            response = client.post("/api/segment-with-stats", files=files)

            assert response.status_code == 200
            data = response.json()

            assert "stats" in data
            assert len(data["stats"]) == 8
            assert data["processing_time"] > 0

    def test_error_handling_workflow(self, client):
        """Test du workflow de gestion d'erreurs"""
        # Test avec un fichier invalide
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/segment", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

        # Test sans fichier
        response = client.post("/api/segment")
        assert response.status_code == 422

    def test_api_documentation_workflow(self, client):
        """Test du workflow de documentation API"""
        # Vérifier que tous les endpoints de documentation sont accessibles
        endpoints = ["/docs", "/redoc", "/openapi.json"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

    def test_cors_workflow(self, client):
        """Test du workflow CORS"""
        # Test d'une requête OPTIONS (preflight)
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }

        response = client.options("/api/segment", headers=headers)

        # Vérifier les headers CORS
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    def test_performance_workflow(self, client, sample_image):
        """Test du workflow de performance"""
        import time

        # Mock le service pour mesurer le temps de réponse
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image, {})

            # Mesurer le temps de réponse
            start_time = time.time()
            files = {"file": ("test_image.png", sample_image, "image/png")}
            response = client.post("/api/segment", files=files)
            end_time = time.time()

            assert response.status_code == 200

            # Vérifier que le temps de réponse est raisonnable (< 5 secondes)
            response_time = end_time - start_time
            assert response_time < 5.0

            # Vérifier que le header de temps de traitement est présent
            assert "X-Processing-Time" in response.headers

    def test_concurrent_requests_workflow(self, client, sample_image):
        """Test du workflow de requêtes concurrentes"""
        import concurrent.futures

        # Mock le service
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image, {})

            # Créer plusieurs requêtes concurrentes
            def make_request():
                files = {"file": ("test_image.png", sample_image, "image/png")}
                return client.post("/api/segment", files=files)

            # Exécuter 10 requêtes concurrentes
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in futures]

            # Vérifier que toutes les requêtes ont réussi
            for response in responses:
                assert response.status_code == 200

            # Vérifier que le service a été appelé 10 fois
            assert mock_service.call_count == 10

    def test_different_image_formats_workflow(self, client):
        """Test du workflow avec différents formats d'images"""
        # Créer des images dans différents formats
        formats = ["PNG", "JPEG", "BMP"]

        for format_name in formats:
            img = Image.new("RGB", (100, 100), color="blue")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=format_name)

            with patch(
                "app.api.segmentation.segmentation_service.segment_image"
            ) as mock_service:
                mock_service.return_value = (img_bytes.getvalue(), {})

                files = {
                    "file": (
                        f"test.{format_name.lower()}",
                        img_bytes.getvalue(),
                        f"image/{format_name.lower()}",
                    )
                }
                response = client.post("/api/segment", files=files)

                assert response.status_code == 200

    def test_large_payload_workflow(self, client):
        """Test du workflow avec des payloads volumineux"""
        # Créer une image plus grande
        large_img = Image.new("RGB", (2048, 2048), color="green")
        large_img_bytes = io.BytesIO()
        large_img.save(large_img_bytes, format="PNG")

        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (large_img_bytes.getvalue(), {})

            files = {
                "file": ("large_image.png", large_img_bytes.getvalue(), "image/png")
            }
            response = client.post("/api/segment", files=files)

            assert response.status_code == 200

    def test_application_configuration_workflow(self, client):
        """Test du workflow de configuration de l'application"""
        # Vérifier que la configuration est correctement appliquée
        response = client.get("/info")
        data = response.json()

        assert data["name"] == "Cityscapes Semantic Segmentation API"
        assert data["version"] == "1.0.0"
        assert "model_info" in data

        # Vérifier que les endpoints listés correspondent à ceux disponibles
        # Les endpoints sont listés avec des descriptions, pas juste les chemins
        expected_patterns = ["/ -", "/health", "/info", "/segment"]
        for pattern in expected_patterns:
            assert any(
                pattern in listed_endpoint for listed_endpoint in data["endpoints"]
            )
