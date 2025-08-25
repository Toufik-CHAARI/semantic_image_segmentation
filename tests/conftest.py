import io
import os
import sys
from unittest.mock import Mock, patch

import numpy as np
import pytest
from PIL import Image

# add the root directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def mock_tensorflow():
    """Mock TensorFlow to avoid loading the real model during tests"""
    with patch("tensorflow.keras.models.load_model") as mock_load_model:
        # create a mock of the model
        mock_model = Mock()
        mock_model.predict.return_value = [np.random.rand(256, 512, 8)]
        mock_model.count_params.return_value = 1000000
        mock_model.summary = Mock(return_value="Mock Model Summary")

        mock_load_model.return_value = mock_model
        yield mock_load_model


@pytest.fixture
def sample_image_bytes():
    """Test image in bytes"""
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


@pytest.fixture
def sample_urban_image_bytes():
    """Realistic test image"""
    img = Image.new("RGB", (512, 256), color="gray")

    # add urban elements
    # Route (bas)
    for x in range(512):
        for y in range(200, 256):
            img.putpixel((x, y), (128, 64, 128))

    # Bâtiments (haut)
    for x in range(512):
        for y in range(0, 100):
            img.putpixel((x, y), (220, 20, 60))

    # Ciel (coin supérieur)
    for x in range(512):
        for y in range(0, 50):
            img.putpixel((x, y), (70, 130, 180))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


@pytest.fixture
def mock_segmentation_stats():
    """Mocked segmentation statistics"""
    return {
        "road": {"pixel_count": 14336, "percentage": 28.0},
        "building": {"pixel_count": 10240, "percentage": 20.0},
        "car": {"pixel_count": 5120, "percentage": 10.0},
        "traffic_sign": {"pixel_count": 2560, "percentage": 5.0},
        "person": {"pixel_count": 1280, "percentage": 2.5},
        "vegetation": {"pixel_count": 2560, "percentage": 5.0},
        "sky": {"pixel_count": 12800, "percentage": 25.0},
        "background": {"pixel_count": 1536, "percentage": 3.0},
    }


@pytest.fixture
def mock_segmented_image_bytes():
    """Mocked segmented image in bytes"""
    img = Image.new("RGB", (512, 256), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


@pytest.fixture
def test_environment():
    """Test environment configuration"""
    # test environment variables
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "8000"
    os.environ["RELOAD"] = "false"
    os.environ["LOG_LEVEL"] = "error"

    yield

    # clean up after tests
    for var in ["HOST", "PORT", "RELOAD", "LOG_LEVEL"]:
        if var in os.environ:
            del os.environ[var]


@pytest.fixture(autouse=True)
def setup_test_environment(test_environment):
    """Automatic test environment configuration"""
    pass
