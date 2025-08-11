import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io
import json
from unittest.mock import patch, Mock
from app.main import app


class TestAPIEndpoints:
    """Tests d'intégration pour les endpoints API"""
    
    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Image de test en bytes"""
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    @pytest.fixture
    def mock_segmentation_service(self):
        """Mock du service de segmentation"""
        with patch('app.api.segmentation.segmentation_service.segment_image') as mock_service:
            # Mock des données de retour
            mock_stats = {
                'road': {'pixel_count': 1000, 'percentage': 25.0},
                'building': {'pixel_count': 800, 'percentage': 20.0},
                'car': {'pixel_count': 600, 'percentage': 15.0},
                'traffic_sign': {'pixel_count': 400, 'percentage': 10.0},
                'person': {'pixel_count': 300, 'percentage': 7.5},
                'vegetation': {'pixel_count': 500, 'percentage': 12.5},
                'sky': {'pixel_count': 300, 'percentage': 7.5},
                'background': {'pixel_count': 100, 'percentage': 2.5}
            }
            
            # Créer une image PNG mock
            mock_img = Image.new('RGB', (256, 512), color='red')
            mock_img_bytes = io.BytesIO()
            mock_img.save(mock_img_bytes, format='PNG')
            
            mock_service.return_value = (mock_img_bytes.getvalue(), mock_stats)
            yield mock_service
    
    def test_root_endpoint(self, client):
        """Test de l'endpoint racine"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "documentation" in data
        assert "health_check" in data
        assert "info" in data
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self, client):
        """Test de l'endpoint de santé"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "message" in data
        assert "timestamp" in data
    
    def test_info_endpoint(self, client):
        """Test de l'endpoint d'information"""
        response = client.get("/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "model_info" in data
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)
    
    def test_segment_endpoint_success(self, client, sample_image_bytes, mock_segmentation_service):
        """Test de l'endpoint de segmentation avec succès"""
        files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
        response = client.post("/api/segment", files=files)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert "X-Processing-Time" in response.headers
        assert "X-Image-Stats" in response.headers
        
        # Vérifier que le service a été appelé
        mock_segmentation_service.assert_called_once()
    
    def test_segment_endpoint_invalid_file_type(self, client):
        """Test de l'endpoint de segmentation avec un type de fichier invalide"""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/segment", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "image" in data["detail"].lower()
    
    def test_segment_endpoint_no_file(self, client):
        """Test de l'endpoint de segmentation sans fichier"""
        response = client.post("/api/segment")
        
        assert response.status_code == 422  # Validation error
    
    def test_segment_with_stats_endpoint_success(self, client, sample_image_bytes, mock_segmentation_service):
        """Test de l'endpoint de segmentation avec statistiques"""
        files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
        response = client.post("/api/segment-with-stats", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "stats" in data
        assert "image_size" in data
        assert "processing_time" in data
        
        # Vérifier la structure des statistiques
        stats = data["stats"]
        assert len(stats) == 8  # 8 classes
        for class_name, class_stats in stats.items():
            assert "pixel_count" in class_stats
            assert "percentage" in class_stats
    
    def test_segment_with_stats_endpoint_invalid_file(self, client):
        """Test de l'endpoint de segmentation avec statistiques et fichier invalide"""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/segment-with-stats", files=files)
        
        assert response.status_code == 400
    
    def test_documentation_endpoints(self, client):
        """Test des endpoints de documentation"""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema(self, client):
        """Test du schéma OpenAPI"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Cityscapes Semantic Segmentation API"
    
    def test_cors_headers(self, client):
        """Test des headers CORS"""
        # Test avec un endpoint qui supporte OPTIONS (POST)
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
        response = client.options("/api/segment", headers=headers)
        
        # Vérifier que les headers CORS sont présents
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_error_handling(self, client, sample_image_bytes):
        """Test de la gestion d'erreurs"""
        # Mock une erreur dans le service
        with patch('app.api.segmentation.segmentation_service.segment_image', side_effect=Exception("Test error")):
            files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
            response = client.post("/api/segment", files=files)
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "error" in data["detail"].lower()
    
    def test_large_image_handling(self, client):
        """Test de la gestion d'images volumineuses"""
        # Créer une image plus grande
        large_img = Image.new('RGB', (2000, 2000), color='green')
        large_img_bytes = io.BytesIO()
        large_img.save(large_img_bytes, format='PNG')
        
        with patch('app.api.segmentation.segmentation_service.segment_image') as mock_service:
            mock_service.return_value = (large_img_bytes.getvalue(), {})
            
            files = {"file": ("large_image.png", large_img_bytes.getvalue(), "image/png")}
            response = client.post("/api/segment", files=files)
            
            assert response.status_code == 200
    
    def test_multiple_concurrent_requests(self, client, sample_image_bytes, mock_segmentation_service):
        """Test de requêtes concurrentes"""
        import asyncio
        import concurrent.futures
        
        def make_request():
            files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
            return client.post("/api/segment", files=files)
        
        # Faire 5 requêtes concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]
        
        # Vérifier que toutes les requêtes ont réussi
        for response in responses:
            assert response.status_code == 200
        
        # Vérifier que le service a été appelé 5 fois
        assert mock_segmentation_service.call_count == 5
