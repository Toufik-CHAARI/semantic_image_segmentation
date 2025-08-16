# Semantic Image Segmentation API

A FastAPI-based semantic image segmentation service using a U-Net model for urban scene understanding.

## 🚀 **Latest Update: EC2 Deployment Complete!**

The application is now successfully deployed on EC2 with full CI/CD automation:
- **API URL:** http://13.36.249.197:8000
- **Health Check:** http://13.36.249.197:8000/health
- **API Documentation:** http://13.36.249.197:8000/docs

## Features

- **Semantic Segmentation:** Segment urban images into 8 classes
- **RESTful API:** FastAPI-based endpoints
- **Docker Support:** Containerized deployment
- **DVC Integration:** Model versioning with S3
- **EC2 Deployment:** Production-ready deployment
- **CI/CD Pipeline:** Automated testing and deployment

## API Endpoints

- `GET /` - Welcome page
- `GET /health` - Health check
- `GET /info` - API information
- `POST /api/segment` - Image segmentation
- `POST /api/segment-with-stats` - Segmentation with statistics

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t semantic-segmentation-api .
docker run -p 8000:8000 semantic-segmentation-api
```

### EC2 Deployment
The application is automatically deployed to EC2 via CI/CD pipeline:
1. Push code to master branch
2. GitHub Actions builds Docker image
3. Image is pushed to ECR
4. Automatic deployment to EC2 instance
5. Health checks verify deployment

## Model Information

- **Architecture:** U-Net
- **Classes:** 8 (road, sidewalk, building, wall, fence, pole, traffic light, traffic sign, vegetation, terrain, sky, pedestrian, rider, car, truck, bus, train, motorcycle, bicycle)
- **Input Size:** 256x512
- **Model Size:** ~30MB

## Technologies Used

- **Backend:** FastAPI, Python 3.11
- **ML Framework:** TensorFlow 2.16.1
- **Image Processing:** OpenCV, Pillow
- **Containerization:** Docker
- **Model Management:** DVC with S3
- **Deployment:** AWS EC2, ECR
- **CI/CD:** GitHub Actions

## License

MIT License# Test comment
# Test workflow trigger
# Test renamed workflow
