# 🌐 Frontend Integration Guide - Semantic Image Segmentation API

## 🎯 **Overview**

This comprehensive guide provides frontend developers with everything needed to integrate with the Semantic Image Segmentation API. The API offers real-time image segmentation capabilities with multiple response formats and detailed analytics.

## 📡 **API Information**

### **Production Endpoints**
```
Base URL: http://13.36.249.197:8000
Health Check: http://13.36.249.197:8000/health
Documentation: http://13.36.249.197:8000/docs
Web Interface: http://13.36.249.197:8000/web
```

### **Available Endpoints**

| Endpoint | Method | Description | Response Type |
|----------|--------|-------------|---------------|
| `/api/segment` | POST | Image segmentation (binary) | Image/PNG |
| `/api/segment-with-stats` | POST | Segmentation with statistics | JSON |
| `/health` | GET | API health status | JSON |
| `/info` | GET | API information | JSON |

## 🔗 **API Endpoints Documentation**

### **1. `/api/segment` - Binary Image Response**

**Purpose**: Get the segmented image directly as a binary file
**Method**: `POST`
**Content-Type**: `multipart/form-data`

#### **Request Format**
```javascript
const formData = new FormData();
formData.append('file', imageFile);
```

#### **Response Format**
- **Content-Type**: `image/png`
- **Body**: Binary image data
- **Headers**:
  - `X-Processing-Time`: Processing time in seconds
  - `X-Image-Stats`: Basic image statistics

#### **JavaScript Example**
```javascript
async function segmentImage(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    try {
        const response = await fetch('http://13.36.249.197:8000/api/segment', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        // Get the segmented image as blob
        const segmentedImageBlob = await response.blob();
        
        // Get processing time from headers
        const processingTime = response.headers.get('X-Processing-Time');
        const imageStats = response.headers.get('X-Image-Stats');
        
        // Create URL for the segmented image
        const imageUrl = URL.createObjectURL(segmentedImageBlob);
        
        return {
            imageUrl,
            processingTime,
            imageStats: imageStats ? JSON.parse(imageStats) : null
        };
    } catch (error) {
        console.error('Segmentation error:', error);
        throw error;
    }
}
```

### **2. `/api/segment-with-stats` - JSON Response with Statistics**

**Purpose**: Get detailed segmentation statistics and analytics
**Method**: `POST`
**Content-Type**: `multipart/form-data`

#### **Request Format**
```javascript
const formData = new FormData();
formData.append('file', imageFile);
```

#### **Response Format**
```json
{
    "message": "Segmentation effectuée avec succès",
    "stats": {
        "total_pixels": 786432,
        "segmented_pixels": 123456,
        "segmentation_ratio": 0.157,
        "unique_classes": 5,
        "class_distribution": {
            "road": 0.45,
            "building": 0.30,
            "car": 0.15,
            "person": 0.08,
            "vegetation": 0.02
        }
    },
    "image_size": "512x512",
    "processing_time": 2.345
}
```

#### **JavaScript Example**
```javascript
async function getSegmentationStats(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    try {
        const response = await fetch('http://13.36.249.197:8000/api/segment-with-stats', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        return stats;
    } catch (error) {
        console.error('Stats error:', error);
        throw error;
    }
}
```

## 🎨 **Complete Frontend Integration Examples**

### **Vanilla JavaScript Example**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Segmentation - Vanilla JS</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 60px 20px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s ease;
            background: #f8f9ff;
        }

        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }

        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8ebff;
            transform: scale(1.02);
        }

        .file-input {
            display: none;
        }

        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
        }

        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .preview {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }

        .image-container {
            background: #f8f9ff;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }

        .image-container h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }

        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .stats {
            background: linear-gradient(135deg, #f8f9ff 0%, #e8ebff 100%);
            padding: 25px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            margin-top: 30px;
            border-left: 4px solid #667eea;
        }

        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.2rem;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin-right: 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #ffe6e6;
            color: #d63031;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #d63031;
            margin: 20px 0;
        }

        .success {
            background: #e6ffe6;
            color: #00b894;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #00b894;
            margin: 20px 0;
        }

        .progress-bar {
            width: 100%;
            height: 6px;
            background: #f0f0f0;
            border-radius: 3px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
        }

        @media (max-width: 768px) {
            .preview {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Image Segmentation</h1>
            <p>Upload an image to see semantic segmentation in action</p>
        </div>
        
        <div class="content">
            <div class="upload-area" id="uploadArea">
                <input type="file" id="fileInput" class="file-input" accept="image/*">
                <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                    📁 Choose Image
                </button>
                <p style="margin-top: 15px; color: #666;">
                    or drag and drop an image here
                </p>
            </div>
            
            <div class="progress-bar" id="progressBar" style="display: none;">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            
            <div id="preview" class="preview" style="display: none;">
                <div class="image-container">
                    <h3>📸 Original Image</h3>
                    <img id="originalImage" alt="Original">
                </div>
                <div class="image-container">
                    <h3>🎨 Segmented Image</h3>
                    <img id="segmentedImage" alt="Segmented">
                </div>
            </div>
            
            <div id="stats" class="stats" style="display: none;"></div>
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                Processing your image...
            </div>
            <div id="error" class="error" style="display: none;"></div>
            <div id="success" class="success" style="display: none;"></div>
        </div>
    </div>

    <script>
        const API_BASE_URL = 'http://13.36.249.197:8000';
        
        // DOM elements
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        
        // Event listeners
        fileInput.addEventListener('change', handleFileSelect);
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                validateAndProcessFile(file);
            }
        }
        
        function handleDragOver(event) {
            event.preventDefault();
            uploadArea.classList.add('dragover');
        }
        
        function handleDragLeave(event) {
            event.preventDefault();
            uploadArea.classList.remove('dragover');
        }
        
        function handleDrop(event) {
            event.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                validateAndProcessFile(files[0]);
            }
        }
        
        function validateAndProcessFile(file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                showError('Please select a valid image file (JPEG, PNG, WebP)');
                return;
            }
            
            // Validate file size (10MB limit)
            if (file.size > 10 * 1024 * 1024) {
                showError('File size must be less than 10MB');
                return;
            }
            
            processImage(file);
        }
        
        async function processImage(file) {
            showLoading();
            hideError();
            hideSuccess();
            
            try {
                // Show original image
                const originalUrl = URL.createObjectURL(file);
                document.getElementById('originalImage').src = originalUrl;
                document.getElementById('preview').style.display = 'grid';
                
                // Simulate progress
                simulateProgress();
                
                // Get segmented image
                const segmentedResult = await segmentImage(file);
                document.getElementById('segmentedImage').src = segmentedResult.imageUrl;
                
                // Get detailed stats
                const stats = await getSegmentationStats(file);
                displayStats(stats, segmentedResult.processingTime);
                
                hideLoading();
                showSuccess('Image segmented successfully!');
                
            } catch (error) {
                hideLoading();
                showError(error.message);
            }
        }
        
        async function segmentImage(imageFile) {
            const formData = new FormData();
            formData.append('file', imageFile);
            
            const response = await fetch(`${API_BASE_URL}/api/segment`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            const segmentedImageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(segmentedImageBlob);
            const processingTime = response.headers.get('X-Processing-Time');
            
            return { imageUrl, processingTime };
        }
        
        async function getSegmentationStats(imageFile) {
            const formData = new FormData();
            formData.append('file', imageFile);
            
            const response = await fetch(`${API_BASE_URL}/api/segment-with-stats`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        }
        
        function displayStats(stats, processingTime) {
            const statsDiv = document.getElementById('stats');
            const processingTimeDisplay = processingTime || stats.processing_time || 'N/A';
            
            statsDiv.innerHTML = `
                <h3>📊 Segmentation Statistics</h3>
                <p><strong>Processing Time:</strong> ${processingTimeDisplay}</p>
                <p><strong>Image Size:</strong> ${stats.image_size || 'N/A'}</p>
                <p><strong>Total Pixels:</strong> ${stats.stats?.total_pixels?.toLocaleString() || 'N/A'}</p>
                <p><strong>Segmented Pixels:</strong> ${stats.stats?.segmented_pixels?.toLocaleString() || 'N/A'}</p>
                <p><strong>Segmentation Ratio:</strong> ${((stats.stats?.segmentation_ratio || 0) * 100).toFixed(1)}%</p>
                <p><strong>Unique Classes:</strong> ${stats.stats?.unique_classes || 'N/A'}</p>
                
                ${stats.stats?.class_distribution ? `
                <h4>Class Distribution:</h4>
                <div style="margin-top: 10px;">
                    ${Object.entries(stats.stats.class_distribution)
                        .map(([class_name, percentage]) => `
                            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                                <span>${class_name}:</span>
                                <span>${(percentage * 100).toFixed(1)}%</span>
                            </div>
                        `).join('')}
                </div>
                ` : ''}
            `;
            statsDiv.style.display = 'block';
        }
        
        function simulateProgress() {
            progressBar.style.display = 'block';
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) {
                    progress = 90;
                    clearInterval(interval);
                }
                progressFill.style.width = progress + '%';
            }, 200);
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'flex';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            progressBar.style.display = 'none';
            progressFill.style.width = '0%';
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        function hideError() {
            document.getElementById('error').style.display = 'none';
        }
        
        function showSuccess(message) {
            const successDiv = document.getElementById('success');
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        }
        
        function hideSuccess() {
            document.getElementById('success').style.display = 'none';
        }
    </script>
</body>
</html>
```

## 🔧 **Framework-Specific Examples**

### **React Example with Hooks**

```jsx
import React, { useState, useCallback } from 'react';
import './ImageSegmentation.css';

const ImageSegmentation = () => {
    const [originalImage, setOriginalImage] = useState(null);
    const [segmentedImage, setSegmentedImage] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [progress, setProgress] = useState(0);

    const API_BASE_URL = 'http://13.36.249.197:8000';

    const validateFile = useCallback((file) => {
        if (!file.type.startsWith('image/')) {
            throw new Error('Please select a valid image file');
        }
        if (file.size > 10 * 1024 * 1024) {
            throw new Error('File size must be less than 10MB');
        }
        return true;
    }, []);

    const simulateProgress = useCallback(() => {
        let currentProgress = 0;
        const interval = setInterval(() => {
            currentProgress += Math.random() * 15;
            if (currentProgress > 90) {
                currentProgress = 90;
                clearInterval(interval);
            }
            setProgress(currentProgress);
        }, 200);
        return interval;
    }, []);

    const handleFileUpload = useCallback(async (file) => {
        try {
            validateFile(file);
            
            setLoading(true);
            setError(null);
            setProgress(0);
            
            const progressInterval = simulateProgress();

            // Show original image
            const originalUrl = URL.createObjectURL(file);
            setOriginalImage(originalUrl);

            // Get segmented image
            const segmentedResult = await segmentImage(file);
            setSegmentedImage(segmentedResult.imageUrl);

            // Get stats
            const statsData = await getSegmentationStats(file);
            setStats(statsData);

            clearInterval(progressInterval);
            setProgress(100);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
            setTimeout(() => setProgress(0), 1000);
        }
    }, [validateFile, simulateProgress]);

    const segmentImage = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/segment`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        return { imageUrl: URL.createObjectURL(blob) };
    };

    const getSegmentationStats = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/segment-with-stats`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    };

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    }, [handleFileUpload]);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
    }, []);

    return (
        <div className="image-segmentation">
            <div className="header">
                <h1>🎯 Image Segmentation</h1>
                <p>Upload an image to see semantic segmentation in action</p>
            </div>

            <div className="upload-area" 
                 onDrop={handleDrop} 
                 onDragOver={handleDragOver}>
                <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0])}
                    style={{ display: 'none' }}
                    id="file-input"
                />
                <label htmlFor="file-input" className="upload-button">
                    📁 Choose Image
                </label>
                <p>or drag and drop an image here</p>
            </div>

            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                    <p>Processing your image... {Math.round(progress)}%</p>
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                    </div>
                </div>
            )}

            {error && (
                <div className="error">
                    ❌ {error}
                </div>
            )}

            {originalImage && segmentedImage && (
                <div className="preview">
                    <div className="image-container">
                        <h3>📸 Original Image</h3>
                        <img src={originalImage} alt="Original" />
                    </div>
                    <div className="image-container">
                        <h3>🎨 Segmented Image</h3>
                        <img src={segmentedImage} alt="Segmented" />
                    </div>
                </div>
            )}

            {stats && (
                <div className="stats">
                    <h3>📊 Segmentation Statistics</h3>
                    <div className="stats-grid">
                        <div className="stat-item">
                            <span className="stat-label">Processing Time:</span>
                            <span className="stat-value">{stats.processing_time}s</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Image Size:</span>
                            <span className="stat-value">{stats.image_size}</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Total Pixels:</span>
                            <span className="stat-value">{stats.stats?.total_pixels?.toLocaleString()}</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Segmentation Ratio:</span>
                            <span className="stat-value">{((stats.stats?.segmentation_ratio || 0) * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                    
                    {stats.stats?.class_distribution && (
                        <div className="class-distribution">
                            <h4>Class Distribution:</h4>
                            <div className="distribution-grid">
                                {Object.entries(stats.stats.class_distribution).map(([className, percentage]) => (
                                    <div key={className} className="class-item">
                                        <span className="class-name">{className}</span>
                                        <span className="class-percentage">{(percentage * 100).toFixed(1)}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ImageSegmentation;
```

### **Vue.js 3 Composition API Example**

```vue
<template>
  <div class="image-segmentation">
    <div class="header">
      <h1>🎯 Image Segmentation</h1>
      <p>Upload an image to see semantic segmentation in action</p>
    </div>

    <div class="upload-area" 
         @drop="handleDrop" 
         @dragover.prevent
         @dragleave.prevent>
      <input
        type="file"
        accept="image/*"
        @change="handleFileSelect"
        ref="fileInput"
        style="display: none"
      />
      <button @click="$refs.fileInput.click()" class="upload-button">
        📁 Choose Image
      </button>
      <p>or drag and drop an image here</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Processing your image... {{ Math.round(progress) }}%</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
    </div>

    <div v-if="error" class="error">
      ❌ {{ error }}
    </div>

    <div v-if="originalImage && segmentedImage" class="preview">
      <div class="image-container">
        <h3>📸 Original Image</h3>
        <img :src="originalImage" alt="Original" />
      </div>
      <div class="image-container">
        <h3>🎨 Segmented Image</h3>
        <img :src="segmentedImage" alt="Segmented" />
      </div>
    </div>

    <div v-if="stats" class="stats">
      <h3>📊 Segmentation Statistics</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">Processing Time:</span>
          <span class="stat-value">{{ stats.processing_time }}s</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Image Size:</span>
          <span class="stat-value">{{ stats.image_size }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Total Pixels:</span>
          <span class="stat-value">{{ formatNumber(stats.stats?.total_pixels) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Segmentation Ratio:</span>
          <span class="stat-value">{{ formatPercentage(stats.stats?.segmentation_ratio) }}</span>
        </div>
      </div>
      
      <div v-if="stats.stats?.class_distribution" class="class-distribution">
        <h4>Class Distribution:</h4>
        <div class="distribution-grid">
          <div v-for="(percentage, className) in stats.stats.class_distribution" 
               :key="className" 
               class="class-item">
            <span class="class-name">{{ className }}</span>
            <span class="class-percentage">{{ formatPercentage(percentage) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const API_BASE_URL = 'http://13.36.249.197:8000'

const originalImage = ref(null)
const segmentedImage = ref(null)
const stats = ref(null)
const loading = ref(false)
const error = ref(null)
const progress = ref(0)

const validateFile = (file) => {
  if (!file.type.startsWith('image/')) {
    throw new Error('Please select a valid image file')
  }
  if (file.size > 10 * 1024 * 1024) {
    throw new Error('File size must be less than 10MB')
  }
  return true
}

const simulateProgress = () => {
  let currentProgress = 0
  const interval = setInterval(() => {
    currentProgress += Math.random() * 15
    if (currentProgress > 90) {
      currentProgress = 90
      clearInterval(interval)
    }
    progress.value = currentProgress
  }, 200)
  return interval
}

const segmentImage = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/api/segment`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }

  const blob = await response.blob()
  return { imageUrl: URL.createObjectURL(blob) }
}

const getSegmentationStats = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/api/segment-with-stats`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

const handleFileUpload = async (file) => {
  try {
    validateFile(file)
    
    loading.value = true
    error.value = null
    progress.value = 0
    
    const progressInterval = simulateProgress()

    // Show original image
    originalImage.value = URL.createObjectURL(file)

    // Get segmented image
    const segmentedResult = await segmentImage(file)
    segmentedImage.value = segmentedResult.imageUrl

    // Get stats
    stats.value = await getSegmentationStats(file)

    clearInterval(progressInterval)
    progress.value = 100

  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
    setTimeout(() => progress.value = 0, 1000)
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    handleFileUpload(file)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const files = event.dataTransfer.files
  if (files.length > 0) {
    handleFileUpload(files[0])
  }
}

const formatNumber = (num) => {
  return num ? num.toLocaleString() : 'N/A'
}

const formatPercentage = (value) => {
  return value ? `${(value * 100).toFixed(1)}%` : 'N/A'
}
</script>

<style scoped>
/* Add your CSS styles here - similar to the React example */
</style>
```

## ⚠️ **Error Handling & Best Practices**

### **HTTP Status Codes**

| Status | Description | Handling |
|--------|-------------|----------|
| `200` | Success | Process response normally |
| `400` | Bad Request | Show user-friendly error message |
| `413` | Payload Too Large | Suggest smaller image |
| `500` | Internal Server Error | Retry or show generic error |
| `503` | Service Unavailable | Show maintenance message |

### **Comprehensive Error Handling**

```javascript
class SegmentationAPI {
    constructor(baseURL = 'http://13.36.249.197:8000') {
        this.baseURL = baseURL;
        this.retryAttempts = 3;
        this.retryDelay = 1000;
    }

    async request(endpoint, options = {}) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(`${this.baseURL}${endpoint}`, {
                    ...options,
                    headers: {
                        'Accept': 'application/json',
                        ...options.headers
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new APIError(
                        response.status,
                        errorData.detail || `HTTP ${response.status}`,
                        response.statusText
                    );
                }

                return response;
            } catch (error) {
                lastError = error;
                
                if (attempt < this.retryAttempts && this.isRetryableError(error)) {
                    await this.delay(this.retryDelay * attempt);
                    continue;
                }
                
                throw this.formatError(error);
            }
        }
        
        throw lastError;
    }

    isRetryableError(error) {
        return error.status >= 500 || error.status === 429;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    formatError(error) {
        if (error instanceof APIError) {
            return error;
        }

        const status = error.status || 0;
        const message = this.getErrorMessage(status, error.message);
        
        return new APIError(status, message, error.statusText);
    }

    getErrorMessage(status, defaultMessage) {
        const errorMessages = {
            400: 'Invalid image format. Please use JPEG, PNG, or WebP.',
            413: 'Image file is too large. Please use an image smaller than 10MB.',
            429: 'Too many requests. Please wait a moment and try again.',
            500: 'Server error. Please try again later.',
            503: 'Service temporarily unavailable. Please try again later.'
        };

        return errorMessages[status] || defaultMessage || 'An unexpected error occurred.';
    }

    async segmentImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await this.request('/api/segment', {
            method: 'POST',
            body: formData
        });

        const blob = await response.blob();
        const processingTime = response.headers.get('X-Processing-Time');
        const imageStats = response.headers.get('X-Image-Stats');

        return {
            imageUrl: URL.createObjectURL(blob),
            processingTime,
            imageStats: imageStats ? JSON.parse(imageStats) : null
        };
    }

    async getSegmentationStats(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await this.request('/api/segment-with-stats', {
            method: 'POST',
            body: formData
        });

        return await response.json();
    }
}

class APIError extends Error {
    constructor(status, message, statusText) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.statusText = statusText;
    }
}

// Usage
const api = new SegmentationAPI();

try {
    const result = await api.segmentImage(file);
    // Handle success
} catch (error) {
    if (error instanceof APIError) {
        console.error(`API Error ${error.status}: ${error.message}`);
        // Show user-friendly error message
    } else {
        console.error('Network error:', error.message);
        // Show network error message
    }
}
```

## 📏 **File Requirements & Performance**

### **Supported Formats**
- **JPEG** (.jpg, .jpeg) - Recommended for photos
- **PNG** (.png) - Recommended for graphics with transparency
- **WebP** (.webp) - Best compression, modern browsers

### **Size Limits & Recommendations**

| Aspect | Limit | Recommendation |
|--------|-------|----------------|
| **File Size** | 10MB | < 5MB for faster processing |
| **Dimensions** | 64x64 to 4096x4096 | 512x512 to 1024x1024 |
| **Aspect Ratio** | Any | 1:1 to 2:1 preferred |

### **Performance Optimization**

```javascript
// Image compression before upload
async function compressImage(file, maxWidth = 1024, quality = 0.8) {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
            canvas.width = img.width * ratio;
            canvas.height = img.height * ratio;
            
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            
            canvas.toBlob(resolve, 'image/jpeg', quality);
        };
        
        img.src = URL.createObjectURL(file);
    });
}

// Usage
const compressedFile = await compressImage(originalFile);
const result = await api.segmentImage(compressedFile);
```

## 🔒 **Security Considerations**

### **CORS Configuration**
The API supports CORS for web applications. Ensure your domain is included in allowed origins.

### **File Validation**
```javascript
function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (!allowedTypes.includes(file.type)) {
        throw new Error('Invalid file type. Please use JPEG, PNG, or WebP.');
    }
    
    if (file.size > maxSize) {
        throw new Error('File too large. Maximum size is 10MB.');
    }
    
    return true;
}
```

### **Rate Limiting**
Implement client-side rate limiting to prevent abuse:
```javascript
class RateLimiter {
    constructor(maxRequests = 10, timeWindow = 60000) {
        this.maxRequests = maxRequests;
        this.timeWindow = timeWindow;
        this.requests = [];
    }
    
    async checkLimit() {
        const now = Date.now();
        this.requests = this.requests.filter(time => now - time < this.timeWindow);
        
        if (this.requests.length >= this.maxRequests) {
            throw new Error('Rate limit exceeded. Please wait before making another request.');
        }
        
        this.requests.push(now);
    }
}
```

## 🚀 **Best Practices**

### **User Experience**
1. **Show loading states** with progress indicators
2. **Provide clear error messages** with actionable suggestions
3. **Implement drag-and-drop** for better UX
4. **Show image previews** before processing
5. **Add retry functionality** for failed requests

### **Performance**
1. **Compress images** before upload
2. **Use appropriate formats** (WebP for better compression)
3. **Implement caching** for repeated requests
4. **Lazy load** segmented images
5. **Use progressive loading** for large images

### **Accessibility**
1. **Add proper alt text** for images
2. **Use semantic HTML** elements
3. **Ensure keyboard navigation** works
4. **Provide screen reader** support
5. **Add ARIA labels** where needed

## 📞 **Support & Resources**

### **API Documentation**
- **Interactive Docs:** http://13.36.249.197:8000/docs
- **Alternative Docs:** http://13.36.249.197:8000/redoc
- **Health Check:** http://13.36.249.197:8000/health

### **Testing Your Integration**
```javascript
// Test API connectivity
async function testAPI() {
    try {
        const response = await fetch('http://13.36.249.197:8000/health');
        const data = await response.json();
        console.log('API Status:', data);
        return data.status === 'ok';
    } catch (error) {
        console.error('API Test Failed:', error);
        return false;
    }
}

// Test with sample image
async function testSegmentation() {
    const response = await fetch('https://via.placeholder.com/512x512');
    const blob = await response.blob();
    const file = new File([blob], 'test.png', { type: 'image/png' });
    
    try {
        const result = await api.segmentImage(file);
        console.log('Segmentation Test Success:', result);
        return true;
    } catch (error) {
        console.error('Segmentation Test Failed:', error);
        return false;
    }
}
```

---

**Happy Integration! 🎯**

*For technical support or questions about the API, please refer to the interactive documentation or contact your development team.*
