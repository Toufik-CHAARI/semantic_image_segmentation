import io
from unittest.mock import Mock, patch

import numpy as np
import pytest
from PIL import Image

from app.services.segmentation_service import SegmentationService


class TestSegmentationService:
    """Tests for the segmentation service"""

    @pytest.fixture
    def mock_model(self):
        """Mock the TensorFlow model"""
        mock = Mock()
        mock.predict.return_value = [np.random.rand(256, 512, 8)]
        return mock

    @pytest.fixture
    def service(self, mock_model):
        """Instance of the service with a mocked model"""
        with patch(
            "app.services.segmentation_service.tf.keras.models.load_model",
            return_value=mock_model,
        ):
            return SegmentationService()

    @pytest.fixture
    def sample_image_bytes(self):
        """Test image in bytes"""
        # create a simple test image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def test_init(self, mock_model):
        """Test initialization of the service"""
        with (
            patch("os.path.exists", return_value=True),
            patch(
                "app.services.segmentation_service.tf.keras.models.load_model",
                return_value=mock_model,
            ),
        ):
            service = SegmentationService()

            assert service.N_CLASSES == 8
            assert service.IMG_SIZE == (256, 512)
            assert len(service.CLASS_NAMES) == 8
            assert service.model == mock_model

    def test_preprocess_image(self, service, sample_image_bytes):
        """Test image preprocessing"""
        result = service.preprocess_image(sample_image_bytes)

        assert isinstance(result, np.ndarray)
        assert result.shape == (256, 512, 3)
        assert result.dtype == np.float32
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_preprocess_image_invalid_bytes(self, service):
        """Test image preprocessing with invalid bytes"""
        with pytest.raises(Exception):
            service.preprocess_image(b"invalid_image_data")

    def test_preprocess_image_pil_fallback(self, service):
        """Test image preprocessing with PIL fallback"""
        # Create a valid image but mock PIL to fail
        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        image_bytes = img_bytes.getvalue()

        with patch("PIL.Image.open", side_effect=Exception("PIL failed")):
            result = service.preprocess_image(image_bytes)

        assert isinstance(result, np.ndarray)
        assert result.shape == (256, 512, 3)
        assert result.dtype == np.float32
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_preprocess_image_pil_and_numpy_fallback(self, service):
        """Test image preprocessing with PIL -> numpy -> cv2 fallback"""
        # Create a valid image but mock both PIL and numpy to fail
        img = Image.new("RGB", (100, 100), color="green")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        image_bytes = img_bytes.getvalue()

        with (
            patch("PIL.Image.open", side_effect=Exception("PIL failed")),
            patch("numpy.frombuffer", side_effect=Exception("numpy failed")),
        ):
            with pytest.raises(Exception):
                service.preprocess_image(image_bytes)

    def test_preprocess_image_cv2_direct_success(self, service):
        """Test image preprocessing with cv2 direct (Method 3)"""
        # Create a valid image
        img = Image.new("RGB", (100, 100), color="yellow")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        image_bytes = img_bytes.getvalue()

        with (
            patch("PIL.Image.open", side_effect=Exception("PIL failed")),
            patch("PIL.Image.fromarray", side_effect=Exception("PIL fromarray failed")),
        ):
            result = service.preprocess_image(image_bytes)

        assert isinstance(result, np.ndarray)
        assert result.shape == (256, 512, 3)
        assert result.dtype == np.float32
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_get_segmentation_stats(self, service):
        """Test segmentation statistics calculation"""
        # create test data
        segmentation_ids = np.random.randint(0, 8, (256, 512))

        stats = service._get_segmentation_stats(segmentation_ids)

        assert isinstance(stats, dict)
        assert len(stats) == 8

        # check if all classes are present
        for class_name in service.CLASS_NAMES:
            assert class_name in stats
            assert "pixel_count" in stats[class_name]
            assert "percentage" in stats[class_name]
            assert isinstance(stats[class_name]["pixel_count"], int)
            assert isinstance(stats[class_name]["percentage"], float)

        # check if the percentages sum to 100%
        total_percentage = sum(stats[class_name]["percentage"] for class_name in stats)
        assert (
            abs(total_percentage - 100.0) < 0.1
        )  # larger tolerance for rounding errors

    def test_segment_image(self, service, sample_image_bytes):
        """Test complete image segmentation"""
        with (
            patch("os.path.exists", return_value=True),
            patch(
                "app.services.segmentation_service.tf.keras.models.load_model"
            ) as mock_load,
        ):
            mock_model = Mock()
            mock_model.predict.return_value = [np.random.rand(256, 512, 8)]
            mock_load.return_value = mock_model

            result_bytes, stats = service.segment_image(sample_image_bytes)

            assert isinstance(result_bytes, bytes)
            assert isinstance(stats, dict)
            assert len(stats) == 8

            # check if the resulting image is a valid PNG
            try:
                img = Image.open(io.BytesIO(result_bytes))
                assert img.format == "PNG"
            except Exception:
                pytest.fail("The resulting image is not a valid PNG")

    def test_segment_image_empty_bytes(self, service):
        """Test segmentation with empty bytes"""
        with pytest.raises(Exception):
            service.segment_image(b"")

    def test_palette_consistency(self, service):
        """Test palette consistency"""
        assert len(service.PALETTE) == 8
        assert service.PALETTE.shape == (8, 3)

        # check if all values are between 0 and 255
        assert service.PALETTE.min() >= 0
        assert service.PALETTE.max() <= 255

        # check if the palette is of type uint8
        assert service.PALETTE.dtype == np.uint8

    def test_class_names_consistency(self, service):
        """Test class names consistency"""
        expected_names = [
            "road",
            "building",
            "car",
            "traffic_sign",
            "person",
            "vegetation",
            "sky",
            "background",
        ]

        assert service.CLASS_NAMES == expected_names
        assert len(service.CLASS_NAMES) == service.N_CLASSES

    def test_check_model_exists_success(self, service):
        """Test when the model file exists"""
        with patch("os.path.exists", return_value=True):
            # Should not raise an exception
            service._check_model_exists()

    def test_check_model_exists_file_not_found(self, service):
        """Test when the model file does not exist"""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Model file not found"):
                service._check_model_exists()

    def test_check_model_exists_file_exists(self, service):
        """Test when the model file already exists"""
        with patch("os.path.exists", return_value=True):
            # Should not raise an exception
            service._check_model_exists()

    def test_model_property_with_test_mode(self, service):
        """Test model property in test mode"""
        with (
            patch("os.path.exists", return_value=True),  # File exists
            patch("os.getenv", return_value="true"),  # TEST_MODE=true
            patch(
                "app.services.segmentation_service.tf.keras.models.load_model"
            ) as mock_load,
        ):
            mock_load.side_effect = Exception("Model loading failed")

            result = service.model
            assert result is not None
            assert hasattr(result, "predict")

    def test_model_property_with_test_mode_and_load_failure(self, service):
        """Test model property in test mode with load failure"""
        with (
            patch("os.path.exists", return_value=True),  # File exists
            patch("os.getenv", return_value="true"),  # TEST_MODE=true
            patch(
                "app.services.segmentation_service.tf.keras.models.load_model"
            ) as mock_load,
        ):
            mock_load.side_effect = Exception("Model loading failed")

            result = service.model
            assert result is not None
            assert hasattr(result, "predict")

    def test_model_property_without_test_mode(self, service):
        """Test model property without test mode (exception raised)"""
        with (
            patch("os.path.exists", return_value=True),  # File exists
            patch(
                "os.getenv",
                side_effect=lambda key, default=None: (
                    "false" if key == "TEST_MODE" else default
                ),
            ),  # TEST_MODE=false, others default
            patch(
                "app.services.segmentation_service.tf.keras.models.load_model"
            ) as mock_load,
        ):
            mock_load.side_effect = Exception("Model loading failed")

            with pytest.raises(Exception, match="Model loading failed"):
                service.model

    def test_model_property_with_model_check(self, service):
        """Test model property with model check"""
        with (
            patch.object(service, "_check_model_exists") as mock_check,
            patch(
                "app.services.segmentation_service.tf.keras.models.load_model"
            ) as mock_load,
        ):

            mock_model = Mock()
            mock_load.return_value = mock_model

            result = service.model

            mock_check.assert_called_once()
            mock_load.assert_called_once_with("model/V3_unet_best.keras", compile=False)
            assert result == mock_model

    def test_model_property_without_model_check(self, service):
        """Test model property without model check (file exists)"""
        with (
            patch("os.path.exists", return_value=True),
            patch(
                "app.services.segmentation_service.tf.keras.models.load_model"
            ) as mock_load,
        ):

            mock_model = Mock()
            mock_load.return_value = mock_model

            result = service.model

            mock_load.assert_called_once_with("model/V3_unet_best.keras", compile=False)
            assert result == mock_model
