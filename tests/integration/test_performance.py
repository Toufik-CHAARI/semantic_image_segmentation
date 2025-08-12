import concurrent.futures
import io
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


class TestPerformance:
    """Tests de performance pour l'application"""

    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        return TestClient(app)

    @pytest.fixture
    def sample_image_bytes(self):
        """Image de test en bytes"""
        img = Image.new("RGB", (512, 256), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def test_single_request_performance(self, client, sample_image_bytes):
        """Test de performance pour une requête unique"""
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            start_time = time.time()
            files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
            response = client.post("/api/segment", files=files)
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200
            assert response_time < 2.0  # Moins de 2 secondes

            # Vérifier le header de temps de traitement
            processing_time = float(
                response.headers.get("X-Processing-Time", "0").replace("s", "")
            )
            assert processing_time < 1.0  # Moins de 1 seconde de traitement

    def test_concurrent_requests_performance(self, client, sample_image_bytes):
        """Test de performance pour des requêtes concurrentes"""
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            def make_request():
                files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
                return client.post("/api/segment", files=files)

            # Test avec 5 requêtes concurrentes
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                responses = [future.result() for future in futures]
            end_time = time.time()

            total_time = end_time - start_time

            # Vérifier que toutes les requêtes ont réussi
            for response in responses:
                assert response.status_code == 200

            # Le temps total devrait être raisonnable (moins de 10 secondes)
            assert total_time < 10.0

            # Vérifier que le service a été appelé 5 fois
            assert mock_service.call_count == 5

    def test_large_image_performance(self, client):
        """Test de performance avec une image volumineuse"""
        # Créer une image plus grande
        large_img = Image.new("RGB", (2048, 1024), color="green")
        large_img_bytes = io.BytesIO()
        large_img.save(large_img_bytes, format="PNG")
        large_image_data = large_img_bytes.getvalue()

        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (large_image_data, {})

            start_time = time.time()
            files = {"file": ("large_image.png", large_image_data, "image/png")}
            response = client.post("/api/segment", files=files)
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200
            assert response_time < 5.0  # Moins de 5 secondes pour une grande image

    def test_memory_usage_performance(self, client, sample_image_bytes):
        """Test de performance pour l'utilisation mémoire"""
        import os

        import psutil

        # Obtenir l'utilisation mémoire avant
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            # Faire plusieurs requêtes pour tester l'utilisation mémoire
            for _ in range(10):
                files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
                response = client.post("/api/segment", files=files)
                assert response.status_code == 200

        # Obtenir l'utilisation mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        # L'augmentation mémoire ne devrait pas être excessive (< 100 MB)
        assert memory_increase < 100.0

    def test_response_size_performance(self, client, sample_image_bytes):
        """Test de performance pour la taille des réponses"""
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
            response = client.post("/api/segment", files=files)

            assert response.status_code == 200

            # Vérifier que la taille de la réponse est raisonnable
            response_size = len(response.content)
            assert response_size > 0
            assert response_size < 10 * 1024 * 1024  # Moins de 10 MB

    def test_health_endpoint_performance(self, client):
        """Test de performance pour l'endpoint de santé"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 0.1  # Moins de 100ms pour l'endpoint de santé

    def test_info_endpoint_performance(self, client):
        """Test de performance pour l'endpoint d'information"""
        start_time = time.time()
        response = client.get("/info")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 1.0  # Moins de 1 seconde pour l'endpoint d'info

    @pytest.mark.slow
    def test_stress_test_performance(self, client, sample_image_bytes):
        """Test de stress avec de nombreuses requêtes"""
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            def make_request():
                files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
                return client.post("/api/segment", files=files)

            # Test avec 20 requêtes concurrentes
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(20)]
                responses = [future.result() for future in futures]
            end_time = time.time()

            total_time = end_time - start_time

            # Vérifier que toutes les requêtes ont réussi
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count == 20

            # Le temps total devrait être raisonnable
            assert total_time < 30.0  # Moins de 30 secondes pour 20 requêtes

            # Vérifier que le service a été appelé 20 fois
            assert mock_service.call_count == 20
