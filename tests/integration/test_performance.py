import concurrent.futures
import io
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


class TestPerformance:
    """Tests for application performance"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI"""
        return TestClient(app)

    @pytest.fixture
    def sample_image_bytes(self):
        """Test image in bytes"""
        img = Image.new("RGB", (512, 256), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def test_single_request_performance(self, client, sample_image_bytes):
        """Test single request performance"""
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
            assert response_time < 2.0  # less than 2 seconds

            # check if processing time header is present
            processing_time = float(
                response.headers.get("X-Processing-Time", "0").replace("s", "")
            )
            assert processing_time < 1.0  # Moins de 1 seconde de traitement

    def test_concurrent_requests_performance(self, client, sample_image_bytes):
        """Test concurrent requests performance"""
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            def make_request():
                files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
                return client.post("/api/segment", files=files)

            # test with 5 concurrent requests
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                responses = [future.result() for future in futures]
            end_time = time.time()

            total_time = end_time - start_time

            # check if all requests were successful
            for response in responses:
                assert response.status_code == 200

            # check if total time is reasonable (< 10 seconds)
            assert total_time < 10.0

            # check if the service was called 5 times
            assert mock_service.call_count == 5

    def test_large_image_performance(self, client):
        """Test large image performance"""
        # create a larger image
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
            assert response_time < 5.0  # less than 5 seconds for a large image

    def test_memory_usage_performance(self, client, sample_image_bytes):
        """Test memory usage performance"""
        import os

        import psutil

        # get memory usage before
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            # make multiple requests to test memory usage
            for _ in range(10):
                files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
                response = client.post("/api/segment", files=files)
                assert response.status_code == 200

        # get memory usage after
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        # check if memory increase is reasonable (< 100 MB)
        assert memory_increase < 100.0

    def test_response_size_performance(self, client, sample_image_bytes):
        """Test response size performance"""
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
            response = client.post("/api/segment", files=files)

            assert response.status_code == 200

            # check if response size is reasonable
            response_size = len(response.content)
            assert response_size > 0
            assert response_size < 10 * 1024 * 1024  # less than 10 MB

    def test_health_endpoint_performance(self, client):
        """Test health endpoint performance"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 0.1  # less than 100ms for the health endpoint

    def test_info_endpoint_performance(self, client):
        """Test info endpoint performance"""
        start_time = time.time()
        response = client.get("/info")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 2.0  # less than 2 seconds for the info endpoint

    @pytest.mark.slow
    def test_stress_test_performance(self, client, sample_image_bytes):
        """Test stress test with many requests"""
        with patch(
            "app.api.segmentation.segmentation_service.segment_image"
        ) as mock_service:
            mock_service.return_value = (sample_image_bytes, {})

            def make_request():
                files = {"file": ("test_image.png", sample_image_bytes, "image/png")}
                return client.post("/api/segment", files=files)

            # test with 20 concurrent requests
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(20)]
                responses = [future.result() for future in futures]
            end_time = time.time()

            total_time = end_time - start_time

            # check if all requests were successful
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count == 20

            # check if total time is reasonable (< 30 seconds)
            assert total_time < 30.0  # less than 30 seconds for 20 requests

            # check if the service was called 20 times
            assert mock_service.call_count == 20
