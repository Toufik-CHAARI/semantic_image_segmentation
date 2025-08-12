import pytest
from pydantic import ValidationError

from app.schemas.responses import (
    HealthResponse,
    InfoResponse,
    SegmentationResponse,
    SegmentationStats,
)


class TestHealthResponse:
    """Tests pour le schéma HealthResponse"""

    def test_valid_health_response(self):
        """Test d'une réponse de santé valide"""
        response = HealthResponse(
            status="healthy", message="API is running", timestamp="2024-01-01T12:00:00"
        )

        assert response.status == "healthy"
        assert response.message == "API is running"
        assert response.timestamp == "2024-01-01T12:00:00"

    def test_health_response_missing_fields(self):
        """Test avec des champs manquants"""
        with pytest.raises(ValidationError):
            HealthResponse(status="healthy")

    def test_health_response_invalid_types(self):
        """Test avec des types invalides"""
        with pytest.raises(ValidationError):
            HealthResponse(
                status=123,  # devrait être une string
                message="test",
                timestamp="2024-01-01T12:00:00",
            )


class TestInfoResponse:
    """Tests pour le schéma InfoResponse"""

    def test_valid_info_response(self):
        """Test d'une réponse d'information valide"""
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
        """Test avec des champs manquants"""
        with pytest.raises(ValidationError):
            InfoResponse(
                name="Test API",
                version="1.0.0",
                # champs manquants
            )


class TestSegmentationStats:
    """Tests pour le schéma SegmentationStats"""

    def test_valid_segmentation_stats(self):
        """Test de statistiques de segmentation valides"""
        stats = SegmentationStats(pixel_count=1000, percentage=25.5)

        assert stats.pixel_count == 1000
        assert stats.percentage == 25.5

    def test_segmentation_stats_negative_values(self):
        """Test avec des valeurs négatives"""
        with pytest.raises(ValidationError):
            SegmentationStats(pixel_count=-100, percentage=25.5)  # négatif

    def test_segmentation_stats_percentage_out_of_range(self):
        """Test avec un pourcentage hors limites"""
        with pytest.raises(ValidationError):
            SegmentationStats(pixel_count=1000, percentage=150.0)  # > 100%


class TestSegmentationResponse:
    """Tests pour le schéma SegmentationResponse"""

    def test_valid_segmentation_response(self):
        """Test d'une réponse de segmentation valide"""
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
        """Test avec des statistiques vides"""
        response = SegmentationResponse(
            message="Test", stats={}, image_size=(256, 512), processing_time=1.0
        )

        assert response.stats == {}

    def test_segmentation_response_invalid_image_size(self):
        """Test avec une taille d'image invalide"""
        with pytest.raises(ValidationError):
            SegmentationResponse(
                message="Test",
                stats={},
                image_size=(0, 0),  # taille invalide
                processing_time=1.0,
            )

    def test_segmentation_response_negative_processing_time(self):
        """Test avec un temps de traitement négatif"""
        with pytest.raises(ValidationError):
            SegmentationResponse(
                message="Test",
                stats={},
                image_size=(256, 512),
                processing_time=-1.0,  # négatif
            )


class TestSchemaValidation:
    """Tests de validation générale des schémas"""

    def test_health_response_from_dict(self):
        """Test de création depuis un dictionnaire"""
        data = {
            "status": "healthy",
            "message": "API is running",
            "timestamp": "2024-01-01T12:00:00",
        }

        response = HealthResponse(**data)
        assert response.status == data["status"]

    def test_info_response_from_dict(self):
        """Test de création depuis un dictionnaire"""
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
        """Test de création depuis un dictionnaire"""
        data = {"pixel_count": 1000, "percentage": 25.5}

        stats = SegmentationStats(**data)
        assert stats.pixel_count == data["pixel_count"]
