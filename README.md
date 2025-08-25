# 🎯 Semantic Image Segmentation API

A production-ready FastAPI-based semantic image segmentation service using a U-Net model for urban scene understanding. This API provides real-time image segmentation capabilities with comprehensive statistics and multiple deployment options.

## 🚀 **Live Deployment**

The application is successfully deployed and running:
- **🌐 API URL:** http://13.36.249.197:8000
- **💚 Health Check:** http://13.36.249.197:8000/health
- **📚 API Documentation:** http://13.36.249.197:8000/docs
- **🔍 Interactive Docs:** http://13.36.249.197:8000/redoc
- **🌍 Web Interface:** http://13.36.249.197:8000/web

## ✨ **Key Features**

- **🎯 Semantic Segmentation:** Segment urban images into 19 classes with high accuracy
- **⚡ FastAPI Backend:** High-performance RESTful API with automatic documentation
- **🐳 Docker Support:** Multi-stage containerized deployment with 2 specialized images
- **📊 Detailed Statistics:** Comprehensive segmentation analytics and metrics
- **🔧 DVC Integration:** Model versioning with S3 storage
- **☁️ AWS Deployment:** Production-ready EC2 deployment with CI/CD
- **🧪 Comprehensive Testing:** Full test suite with coverage reporting
- **📈 Performance Monitoring:** Built-in health checks and metrics

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   U-Net Model   │
│   (Web/API)     │◄──►│   Application   │◄──►│   (TensorFlow)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   DVC + S3      │
                       │   Model Store   │
                       └─────────────────┘
```

## 📡 **API Endpoints**

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Welcome page with web interface | HTML/JSON |
| `/health` | GET | Health check | JSON |
| `/info` | GET | API information and model status | JSON |
| `/docs` | GET | Interactive API documentation | HTML |
| `/redoc` | GET | Alternative API documentation | HTML |
| `/web` | GET | Web interface for image upload | HTML |
| `/api/segment` | POST | Image segmentation (binary response) | Image/PNG |
| `/api/segment-with-stats` | POST | Segmentation with detailed statistics | JSON |

## 🎨 **Segmentation Classes**

The model can identify and segment 19 different classes in urban scenes:

- **Infrastructure:** road, sidewalk, building, wall, fence, pole
- **Traffic:** traffic light, traffic sign, car, truck, bus, train, motorcycle, bicycle
- **Environment:** vegetation, terrain, sky
- **People:** pedestrian, rider

## 🚀 **Quick Start**

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd semantic_image_segmentation

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build and run with Docker
make docker-build
make docker-run

# Or use docker-compose
docker-compose up -d
```

### Complete Development Workflow

```bash
# Run the complete development workflow (build, test, validate)
make dev-workflow
```

## 🐳 **Docker Images**

This project includes two specialized Docker images:

1. **Production Image** (`Dockerfile`) - Optimized for production deployment
2. **Test Image** (`Dockerfile.test`) - Includes testing framework and tools

### Build All Images

```bash
make docker-build-all
```

### Test All Images

```bash
make docker-test-all
```

## 🧪 **Testing**

### Run All Tests

```bash
# Complete test suite with coverage
make test-coverage-detail

# Fast tests only
make test-fast

# Unit tests only
make test-unit

# Integration tests only
make test-integration
```

### Test Categories

- **Unit Tests:** Individual component testing
- **Integration Tests:** API endpoint testing
- **Performance Tests:** Load and stress testing
- **Docker Tests:** Container validation
- **Security Tests:** Vulnerability scanning

## 📊 **Model Information**

- **Architecture:** U-Net (Convolutional Neural Network)
- **Framework:** TensorFlow 2.16.1
- **Input Size:** 256x512 pixels (automatically resized)
- **Output Classes:** 19 semantic classes
- **Model Size:** ~30MB
- **Accuracy:** Optimized for urban scene understanding
- **Processing Time:** 1-5 seconds per image

## 🛠️ **Technologies Used**

### Backend & API
- **FastAPI** 0.104.1 - High-performance web framework
- **Uvicorn** 0.35.0 - ASGI server
- **Pydantic** 2.5.0 - Data validation
- **Python** 3.12 - Programming language

### Machine Learning
- **TensorFlow** 2.16.1 - Deep learning framework
- **OpenCV** 4.8.1.78 - Computer vision
- **NumPy** 1.26.4 - Numerical computing
- **Pillow** 10.0.1 - Image processing

### DevOps & Deployment
- **Docker** - Containerization
- **DVC** 3.50.2 - Model versioning with S3
- **AWS EC2** - Cloud deployment
- **AWS ECR** - Container registry
- **GitHub Actions** - CI/CD pipeline

## 📁 **Project Structure**

```
semantic_image_segmentation/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   ├── services/          # Business logic
│   ├── schemas/           # Data models
│   ├── static/            # Static files
│   ├── config.py          # Configuration
│   └── main.py            # Application entry point
├── model/                 # ML model files
│   └── unet_best.keras    # Trained model (DVC managed)
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── aws/                   # AWS deployment configs
├── Dockerfile             # Production Docker image
├── Dockerfile.test        # Test Docker image
├── docker-compose.yml     # Local development
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── Makefile              # Build automation
└── README files          # Documentation
```

## 🔧 **Configuration**

### Environment Variables

```bash
# API Configuration
API_TITLE=Semantic Image Segmentation API
API_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000

# Model Configuration
MODEL_PATH=model/unet_best.keras
IMG_SIZE=256x512

# AWS Configuration (for DVC)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=eu-west-3
```

## 📈 **Performance & Monitoring**

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check model status
curl http://localhost:8000/info
```

### Performance Metrics

- **Response Time:** < 5 seconds for typical images
- **Throughput:** 10-20 requests per minute
- **Memory Usage:** ~2GB RAM
- **CPU Usage:** Optimized for single-threaded processing

## 🔒 **Security**

- **CORS Configuration:** Configurable origins
- **Input Validation:** File type and size validation
- **Error Handling:** Secure error responses
- **Docker Security:** Non-root user in containers

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test-coverage-detail`
5. Submit a pull request

## 📚 **Documentation**

- **[Docker Guide](README_Docker.md)** - Complete Docker workflow
- **[Frontend Guide](README_Frontend.md)** - Frontend integration guide
- **[API Documentation](http://13.36.249.197:8000/docs)** - Interactive API docs

## 🐛 **Troubleshooting**

### Common Issues

1. **Model Loading Error:** Ensure DVC is configured and model is pulled
2. **Memory Issues:** Increase Docker memory allocation
3. **Port Conflicts:** Use different ports with `-p` flag
4. **Dependencies:** Install with `pip install -r requirements.txt`

### Debug Commands

```bash
# Check installation
make check-install

# Health check
make health-check

# Docker logs
docker logs <container-name>

# Test coverage
make test-coverage-detail
```

## 📄 **License**

MIT License - see LICENSE file for details.

## 🙏 **Acknowledgments**

- **Cityscapes Dataset** - Urban scene understanding
- **U-Net Architecture** - Semantic segmentation
- **FastAPI Community** - Web framework
- **TensorFlow Team** - Machine learning framework

---

**Happy Segmentation! 🎯**

*For support and questions, please refer to the API documentation or create an issue in the repository.*
