import pytest
from pydantic import ValidationError

from app.schemas.responses import (
    HealthResponse,
    InfoResponse,
    SegmentationResponse,
    SegmentationStats,
)


class TestHealthResponse:
    """Tests for the HealthResponse schema"""

    def test_valid_health_response(self):
        """Test a valid health response"""
        response = HealthResponse(
            status="healthy", message="API is running", timestamp="2024-01-01T12:00:00"
        )

        assert response.status == "healthy"
        assert response.message == "API is running"
        assert response.timestamp == "2024-01-01T12:00:00"

    def test_health_response_missing_fields(self):
        """Test with missing fields"""
        with pytest.raises(ValidationError):
            HealthResponse(status="healthy")

    def test_health_response_invalid_types(self):
        """Test with invalid types"""
        with pytest.raises(ValidationError):
            HealthResponse(
                status=123,  # should be a string
                message="test",
                timestamp="2024-01-01T12:00:00",
            )


class TestInfoResponse:
    """Tests for the InfoResponse schema"""

    def test_valid_info_response(self):
        """Test a valid info response"""
        response = InfoResponse(
            name="Test API",
            version="1.0.0",
            description="Test description",
            model_info={"test": "info"},
            endpoints=["/health", "/info"],
        )

        assert response.name == "Test API"
        assert response.version == "1.0.0"
        assert response.description == "Test description"
        assert response.model_info == {"test": "info"}
        assert response.endpoints == ["/health", "/info"]

    def test_info_response_missing_fields(self):
        """Test with missing fields"""
        with pytest.raises(ValidationError):
            InfoResponse(
                name="Test API",
                version="1.0.0",
                # missing fields
            )


class TestSegmentationStats:
    """Tests for the SegmentationStats schema"""

    def test_valid_segmentation_stats(self):
        """Test valid segmentation statistics"""
        stats = SegmentationStats(pixel_count=1000, percentage=25.5)

        assert stats.pixel_count == 1000
        assert stats.percentage == 25.5

    def test_segmentation_stats_negative_values(self):
        """Test with negative values"""
        with pytest.raises(ValidationError):
            SegmentationStats(pixel_count=-100, percentage=25.5)  # negative

    def test_segmentation_stats_percentage_out_of_range(self):
        """Test with a percentage out of range"""
        with pytest.raises(ValidationError):
            SegmentationStats(pixel_count=1000, percentage=150.0)  # > 100%


class TestSegmentationResponse:
    """Tests for the SegmentationResponse schema"""

    def test_valid_segmentation_response(self):
        """Test a valid segmentation response"""
        stats = {
            "road": SegmentationStats(pixel_count=1000, percentage=25.0),
            "building": SegmentationStats(pixel_count=800, percentage=20.0),
        }

        response = SegmentationResponse(
            message="Segmentation successful",
            stats=stats,
            image_size=(256, 512),
            processing_time=1.5,
        )

        assert response.message == "Segmentation successful"
        assert len(response.stats) == 2
        assert response.image_size == (256, 512)
        assert response.processing_time == 1.5

    def test_segmentation_response_empty_stats(self):
        """Test with empty statistics"""
        response = SegmentationResponse(
            message="Test", stats={}, image_size=(256, 512), processing_time=1.0
        )

        assert response.stats == {}

    def test_segmentation_response_invalid_image_size(self):
        """Test with an invalid image size"""
        with pytest.raises(ValidationError):
            SegmentationResponse(
                message="Test",
                stats={},
                image_size=(0, 0),  # invalid size
                processing_time=1.0,
            )

    def test_segmentation_response_negative_processing_time(self):
        """Test with a negative processing time"""
        with pytest.raises(ValidationError):
            SegmentationResponse(
                message="Test",
                stats={},
                image_size=(256, 512),
                processing_time=-1.0,  # negative
            )


class TestSchemaValidation:
    """Tests for general schema validation"""

    def test_health_response_from_dict(self):
        """Test creation from a dictionary"""
        data = {
            "status": "healthy",
            "message": "API is running",
            "timestamp": "2024-01-01T12:00:00",
        }

        response = HealthResponse(**data)
        assert response.status == data["status"]

    def test_info_response_from_dict(self):
        """Test creation from a dictionary"""
        data = {
            "name": "Test API",
            "version": "1.0.0",
            "description": "Test description",
            "model_info": {"test": "info"},
            "endpoints": ["/health", "/info"],
        }

        response = InfoResponse(**data)
        assert response.name == data["name"]

    def test_segmentation_stats_from_dict(self):
        """Test creation from a dictionary"""
        data = {"pixel_count": 1000, "percentage": 25.5}

        stats = SegmentationStats(**data)
        assert stats.pixel_count == data["pixel_count"]
