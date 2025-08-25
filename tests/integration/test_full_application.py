import io
import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


class TestFullApplication:
    """Integration tests for the full application"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI"""
        return TestClient(app)

    @pytest.fixture
    def temp_model_file(self):
        """Create a temporary model file for tests"""
        with tempfile.NamedTemporaryFile(suffix=".keras", delete=False) as tmp_file:
            # create a simple model for tests
            import tensorflow as tf

            # create a simple U-Net model
            inputs = tf.keras.layers.Input(shape=(256, 512, 3))
            x = tf.keras.layers.Conv2D(8, (3, 3), activation="relu", padding="same")(
                inputs
            )
            x = tf.keras.layers.Conv2D(8, (1, 1), activation="softmax")(x)
            model = tf.keras.Model(inputs=inputs, outputs=x)

            model.save(tmp_file.name)
            yield tmp_file.name

        # clean up after tests
        if os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)

    @pytest.fixture
    def sample_image(self):
        """Create a realistic test image"""
        # create an image that resembles an urban scene
        img = Image.new("RGB", (512, 256), color="gray")

        # add some elements to simulate an urban scene
        # road (bottom of the image)
        for x in range(512):
            for y in range(200, 256):
                img.putpixel((x, y), (128, 64, 128))  # road color

        # buildings (top of the image)
        for x in range(512):
            for y in range(0, 100):
                img.putpixel((x, y), (220, 20, 60))  # buildings color

        # sky (top of the image)
        for x in range(512):
            for y in range(0, 50):
                img.putpixel((x, y), (70, 130, 180))  # sky color

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def test_application_startup(self, client):
        """Test that the application starts correctly"""
        # check if the application responds (test API JSON)
        headers = {"Accept": "application/json"}
        response = client.get("/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

        # check if the documentation is accessible
        response = client.get("/docs")
        assert response.status_code == 200

    def test_health_check_workflow(self, client):
        """Test health check workflow"""
        # test health endpoint
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

        # test info endpoint
        response = client.get("/info")
        assert response.status_code == 200

        data = response.json()
        assert "model_info" in data
        assert "endpoints" in data

    def test_segmentation_workflow_with_mock_model(self, client, sample_image):
        """Test segmentation workflow with mock model"""
        # mock segmentation service
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            # mock segmentation response
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

            # create a mock segmented image
            segmented_img = Image.new("RGB", (512, 256), color="red")
            segmented_bytes = io.BytesIO()
            segmented_img.save(segmented_bytes, format="PNG")

            mock_service.return_value = (segmented_bytes.getvalue(), mock_stats)

            # test segment endpoint
            files = {"file": ("test_image.png", sample_image, "image/png")}
            response = client.post("/api/segment", files=files)

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

            # test segment-with-stats endpoint
            response = client.post("/api/segment-with-stats", files=files)

            assert response.status_code == 200
            data = response.json()

            assert "stats" in data
            assert len(data["stats"]) == 8
            assert data["processing_time"] > 0

    def test_error_handling_workflow(self, client):
        """Test error handling workflow"""
        # test with an invalid file
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/segment", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

        # test without file
        response = client.post("/api/segment")
        assert response.status_code == 422

    def test_api_documentation_workflow(self, client):
        """Test API documentation workflow"""
        # check if all documentation endpoints are accessible
        endpoints = ["/docs", "/redoc", "/openapi.json"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

    def test_cors_workflow(self, client):
        """Test CORS workflow"""
        # test OPTIONS (preflight) request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }

        response = client.options("/api/segment", headers=headers)

        # check if CORS headers are present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    def test_performance_workflow(self, client, sample_image):
        """Test performance workflow"""
        import time

        # mock service to measure response time
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image, {})

            # measure response time
            start_time = time.time()
            files = {"file": ("test_image.png", sample_image, "image/png")}
            response = client.post("/api/segment", files=files)
            end_time = time.time()

            assert response.status_code == 200

            # check if response time is reasonable (< 5 seconds)
            response_time = end_time - start_time
            assert response_time < 5.0

            # check if processing time header is present
            assert "X-Processing-Time" in response.headers

    def test_concurrent_requests_workflow(self, client, sample_image):
        """Test concurrent requests workflow"""
        import concurrent.futures

        # mock service
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image, {})

            # create multiple concurrent requests
            def make_request():
                files = {"file": ("test_image.png", sample_image, "image/png")}
                return client.post("/api/segment", files=files)

            # execute 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in futures]

            # check if all requests were successful
            for response in responses:
                assert response.status_code == 200

            # check if the service was called 10 times
            assert mock_service.call_count == 10

    def test_different_image_formats_workflow(self, client):
        """Test different image formats workflow"""
        # create images in different formats
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
        """Test large payload workflow"""
        # create a larger image
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
        """Test application configuration workflow"""
        # check if the configuration is applied correctly
        response = client.get("/info")
        data = response.json()

        assert data["name"] == "Cityscapes Semantic Segmentation API"
        assert data["version"] == "1.0.0"
        assert "model_info" in data

        # check if the listed endpoints correspond to the ones available
        # the endpoints are listed with descriptions, not just the paths
        expected_patterns = ["/ -", "/health", "/info", "/segment"]
        for pattern in expected_patterns:
            assert any(
                pattern in listed_endpoint for listed_endpoint in data["endpoints"]
            )
