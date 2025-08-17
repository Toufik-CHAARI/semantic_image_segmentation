# app/main.py
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import health, segmentation
from app.config import settings

# Création de l'application FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(health.router, tags=["Health & Info"])
app.include_router(segmentation.router, prefix="/api", tags=["Segmentation"])

# Mount static files
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Événement exécuté au démarrage de l'application"""
    print("🚀 Démarrage de l'API de segmentation sémantique...")
    print("✅ API prête à recevoir des requêtes")


@app.on_event("shutdown")
async def shutdown_event():
    """Événement exécuté à l'arrêt de l'application"""
    print("🛑 Arrêt de l'API de segmentation sémantique...")


@app.get("/")
async def root(request: Request):
    """Route racine - retourne HTML pour les navigateurs, JSON pour les API"""
    user_agent = request.headers.get("user-agent", "").lower()
    accept_header = request.headers.get("accept", "").lower()

    if (
        "mozilla" in user_agent
        or "chrome" in user_agent
        or "safari" in user_agent
        or "firefox" in user_agent
        or "edge" in user_agent
        or "text/html" in accept_header
    ):
        return get_web_interface_response()

    return {
        "message": "Bienvenue sur l'API de segmentation sémantique Cityscapes",
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "health_check": "/health",
        "info": "/info",
        "web_interface": "/web",
    }


@app.get("/info")
def info():
    """Status info including whether the model is loaded"""
    from app.services.model_loader import is_model_loaded

    return {
        "status": "ok",
        "model_loaded": is_model_loaded(),
        "version": settings.API_VERSION,
    }


@app.get("/web")
async def web_interface():
    """Interface web pour l'upload d'images"""
    return get_web_interface_response()


def get_web_interface_response():
    """Helper function to return the web interface HTML response"""
    from fastapi.responses import HTMLResponse

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semantic Image Segmentation API</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }
        .upload-area:hover {
            border-color: #007bff;
        }
        .upload-area.dragover {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
        #fileInput {
            display: none;
        }
        .upload-btn {
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        .upload-btn:hover {
            background: #0056b3;
        }
        .preview {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            gap: 20px;
        }
        .image-container {
            flex: 1;
            text-align: center;
        }
        .image-container img {
            max-width: 100%;
            max-height: 400px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .loading {
            text-align: center;
            color: #007bff;
            font-weight: bold;
        }
        .error {
            color: #dc3545;
            text-align: center;
            margin: 10px 0;
        }
        .success {
            color: #28a745;
            text-align: center;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Semantic Image Segmentation</h1>

        <div class="upload-area" id="uploadArea">
            <p>📁 Faites glisser une image ici ou
            cliquez pour télécharger</p>
            <input type="file" id="fileInput" accept="image/*">
            <button
                class="upload-btn"
                onclick="document.getElementById('fileInput').click()"
            >
                Télécharger l'image
            </button>
        </div>

        <div id="preview" class="preview" style="display: none;">
            <div class="image-container">
                <h3>Original Image</h3>
                <img id="originalImage" alt="Original">
            </div>
            <div class="image-container">
                <h3>Segmented Image</h3>
                <img id="segmentedImage" alt="Segmented">
            </div>
        </div>

        <div id="stats" class="stats" style="display: none;"></div>
        <div id="loading" class="loading" style="display: none;">
            Processing image...
        </div>
        <div id="error" class="error" style="display: none;"></div>
        <div id="success" class="success" style="display: none;"></div>
    </div>

    <script>
        const API_BASE_URL = window.location.origin;

        // File input handling
        document
            .getElementById('fileInput')
            .addEventListener('change', handleFileSelect);

        // Drag and drop handling
        const uploadArea = document.getElementById(
            'uploadArea'
        );
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                handleFile(file);
            }
        }

        function handleFile(file) {
            if (!file.type.startsWith('image/')) {
                showError('Please select an image file.');
                return;
            }

            // Show original image
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('originalImage').src =
                    e.target.result;
                document.getElementById('preview').style.display =
                    'flex';
                document.getElementById('segmentedImage').src = '';
                document.getElementById('stats').style.display =
                    'none';
                document.getElementById('error').style.display =
                    'none';
                document.getElementById('success').style.display =
                    'none';
            };
            reader.readAsDataURL(file);

            // Process image
            processImage(file);
        }

        async function processImage(file) {
            showLoading();

            const formData = new FormData();
            formData.append('file', file);

            try {
                // First, get the segmented image
                const imageResponse = await fetch(
                    `${API_BASE_URL}/api/segment`,
                    {
                    method: 'POST',
                    body: formData
                });

                if (!imageResponse.ok) {
                    throw new Error(
                    `HTTP error! status: ${imageResponse.status}`
                );
                }

                const imageBlob = await imageResponse.blob();
                const imageUrl = URL.createObjectURL(imageBlob);
                document.getElementById('segmentedImage').src =
                    imageUrl;

                // Get processing time from headers
                const processingTime = imageResponse.headers.get(
                    'X-Processing-Time'
                );
                const imageStats = imageResponse.headers.get(
                    'X-Image-Stats'
                );

                // Then, get detailed stats
                const statsResponse = await fetch(
                    `${API_BASE_URL}/api/segment-with-stats`,
                    {
                    method: 'POST',
                    body: formData
                });

                if (statsResponse.ok) {
                    const stats = await statsResponse.json();
                    displayStats(stats, processingTime);
                }

                showSuccess('Image segmented successfully!');
                hideLoading();

            } catch (error) {
                console.error('Error:', error);
                showError(
                    'Error processing image: ' + error.message
                );
                hideLoading();
            }
        }

        function displayStats(stats, processingTime) {
            const statsDiv = document.getElementById(
                'stats'
            );
            statsDiv.innerHTML = `
Processing Time: ${processingTime || 'N/A'}
Image Size: ${stats.image_size || 'N/A'}
Message: ${stats.message || 'N/A'}

Statistics:
${JSON.stringify(stats.stats, null, 2)}
            `;
            statsDiv.style.display = 'block';
        }

        function showLoading() {
            document.getElementById('loading').style.display =
                'block';
            document.getElementById('error').style.display =
                'none';
            document.getElementById('success').style.display = 'none';
        }

        function hideLoading() {
            document.getElementById('loading').style.display =
                'none';
        }

        function showError(message) {
            document.getElementById('error').textContent =
                message;
            document.getElementById('error').style.display
            = 'block';
            document.getElementById('success').style.display
            = 'none';
        }

        function showSuccess(message) {
            document.getElementById('success').textContent =
                message;
            document.getElementById('success').style.display
            = 'block';
            document.getElementById('error').style.display
            = 'none';
        }
    </script>
</body>
</html>
    """

    return HTMLResponse(
        content=html_content,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
