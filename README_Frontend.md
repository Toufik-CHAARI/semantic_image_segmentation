# Frontend Integration Guide - Semantic Image Segmentation API

## 🎯 **Overview**

This guide provides comprehensive documentation for frontend developers to integrate with the Semantic Image Segmentation API. The API provides two main endpoints for image segmentation with different response formats.

## 📡 **API Base URL**

```
Production: https://fx8r2pg0ml.execute-api.eu-west-3.amazonaws.com/production
MVP:        https://[mvp-api-url]/mvp
Staging:    https://[staging-api-url]/staging
```

## 🔗 **Available Endpoints**

### **1. `/api/segment` - Image Segmentation (Binary Response)**
Returns the segmented image directly as a binary file.

### **2. `/api/segment-with-stats` - Image Segmentation with Statistics (JSON Response)**
Returns detailed statistics about the segmentation process in JSON format.

## 📋 **API Endpoints Documentation**

### **Endpoint 1: `/api/segment`**

**Purpose**: Get the segmented image directly
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
        const response = await fetch('/api/segment', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
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
            imageStats
        };
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

### **Endpoint 2: `/api/segment-with-stats`**

**Purpose**: Get detailed segmentation statistics
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
        const response = await fetch('/api/segment-with-stats', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        return stats;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

## 🎨 **Complete Frontend Integration Example**

### **HTML Structure**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Segmentation</title>
    <style>
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
        }
        .preview {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }
        .image-container {
            flex: 1;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
        }
        .stats {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
        }
        .loading {
            color: #007bff;
            font-weight: bold;
        }
        .error {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Segmentation</h1>
        
        <div class="upload-area">
            <input type="file" id="fileInput" accept="image/*">
            <button onclick="document.getElementById('fileInput').click()">
                Choose Image
            </button>
        </div>
        
        <div id="preview" class="preview" style="display: none;">
            <div class="image-container">
                <h3>Original</h3>
                <img id="originalImage" alt="Original">
            </div>
            <div class="image-container">
                <h3>Segmented</h3>
                <img id="segmentedImage" alt="Segmented">
            </div>
        </div>
        
        <div id="stats" class="stats" style="display: none;"></div>
        <div id="loading" class="loading" style="display: none;">Processing...</div>
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script>
        const API_BASE_URL = 'https://fx8r2pg0ml.execute-api.eu-west-3.amazonaws.com/production';
        
        document.getElementById('fileInput').addEventListener('change', handleFileSelect);
        
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                processImage(file);
            }
        }
        
        async function processImage(file) {
            showLoading();
            
            try {
                // Show original image
                const originalUrl = URL.createObjectURL(file);
                document.getElementById('originalImage').src = originalUrl;
                document.getElementById('preview').style.display = 'flex';
                
                // Get segmented image
                const segmentedResult = await segmentImage(file);
                document.getElementById('segmentedImage').src = segmentedResult.imageUrl;
                
                // Get detailed stats
                const stats = await getSegmentationStats(file);
                displayStats(stats, segmentedResult.processingTime);
                
                hideLoading();
                
            } catch (error) {
                showError(error.message);
                hideLoading();
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
                throw new Error(`HTTP error! status: ${response.status}`);
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
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        }
        
        function displayStats(stats, processingTime) {
            const statsDiv = document.getElementById('stats');
            statsDiv.innerHTML = `
Processing Time: ${processingTime || stats.processing_time || 'N/A'}
Image Size: ${stats.image_size || 'N/A'}
Message: ${stats.message || 'N/A'}

Statistics:
${JSON.stringify(stats.stats, null, 2)}
            `;
            statsDiv.style.display = 'block';
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        function showError(message) {
            document.getElementById('error').textContent = message;
            document.getElementById('error').style.display = 'block';
        }
    </script>
</body>
</html>
```

## 🔧 **Framework-Specific Examples**

### **React Example**
```jsx
import React, { useState } from 'react';

const ImageSegmentation = () => {
    const [originalImage, setOriginalImage] = useState(null);
    const [segmentedImage, setSegmentedImage] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const API_BASE_URL = 'https://fx8r2pg0ml.execute-api.eu-west-3.amazonaws.com/production';

    const handleFileUpload = async (file) => {
        setLoading(true);
        setError(null);

        try {
            // Show original image
            const originalUrl = URL.createObjectURL(file);
            setOriginalImage(originalUrl);

            // Get segmented image
            const segmentedResult = await segmentImage(file);
            setSegmentedImage(segmentedResult.imageUrl);

            // Get stats
            const statsData = await getSegmentationStats(file);
            setStats(statsData);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const segmentImage = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/segment`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
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
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    };

    return (
        <div>
            <h1>Image Segmentation</h1>
            
            <input
                type="file"
                accept="image/*"
                onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0])}
            />

            {loading && <div>Processing...</div>}
            {error && <div style={{color: 'red'}}>{error}</div>}

            {originalImage && segmentedImage && (
                <div style={{display: 'flex', gap: '20px'}}>
                    <div>
                        <h3>Original</h3>
                        <img src={originalImage} alt="Original" style={{maxWidth: '100%'}} />
                    </div>
                    <div>
                        <h3>Segmented</h3>
                        <img src={segmentedImage} alt="Segmented" style={{maxWidth: '100%'}} />
                    </div>
                </div>
            )}

            {stats && (
                <div style={{background: '#f5f5f5', padding: '15px', marginTop: '20px'}}>
                    <h3>Statistics</h3>
                    <pre>{JSON.stringify(stats, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default ImageSegmentation;
```

### **Vue.js Example**
```vue
<template>
  <div>
    <h1>Image Segmentation</h1>
    
    <input
      type="file"
      accept="image/*"
      @change="handleFileUpload"
    />
    
    <div v-if="loading">Processing...</div>
    <div v-if="error" style="color: red">{{ error }}</div>
    
    <div v-if="originalImage && segmentedImage" style="display: flex; gap: 20px;">
      <div>
        <h3>Original</h3>
        <img :src="originalImage" alt="Original" style="max-width: 100%" />
      </div>
      <div>
        <h3>Segmented</h3>
        <img :src="segmentedImage" alt="Segmented" style="max-width: 100%" />
      </div>
    </div>
    
    <div v-if="stats" style="background: #f5f5f5; padding: 15px; margin-top: 20px;">
      <h3>Statistics</h3>
      <pre>{{ JSON.stringify(stats, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      originalImage: null,
      segmentedImage: null,
      stats: null,
      loading: false,
      error: null,
      API_BASE_URL: 'https://fx8r2pg0ml.execute-api.eu-west-3.amazonaws.com/production'
    };
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.loading = true;
      this.error = null;

      try {
        // Show original image
        this.originalImage = URL.createObjectURL(file);

        // Get segmented image
        const segmentedResult = await this.segmentImage(file);
        this.segmentedImage = segmentedResult.imageUrl;

        // Get stats
        this.stats = await this.getSegmentationStats(file);

      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    async segmentImage(file) {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.API_BASE_URL}/api/segment`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      return { imageUrl: URL.createObjectURL(blob) };
    },

    async getSegmentationStats(file) {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.API_BASE_URL}/api/segment-with-stats`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    }
  }
};
</script>
```

## ⚠️ **Error Handling**

### **Common HTTP Status Codes**
- `200`: Success
- `400`: Bad Request (invalid file format, missing file)
- `413`: Payload Too Large (file too big)
- `500`: Internal Server Error (processing error)

### **Error Response Format**
```json
{
    "detail": "Error message description"
}
```

### **JavaScript Error Handling**
```javascript
try {
    const response = await fetch('/api/segment', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    // Process successful response
} catch (error) {
    console.error('Segmentation error:', error);
    // Handle error in UI
}
```

## 📏 **File Requirements**

### **Supported Formats**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

### **Size Limits**
- **Maximum file size**: 10MB
- **Recommended size**: 512x512 to 1024x1024 pixels
- **Minimum size**: 64x64 pixels

### **Performance Notes**
- **Processing time**: 1-5 seconds depending on image size
- **Memory usage**: Images are automatically resized to 512x512 for processing
- **Concurrent requests**: Limited to prevent server overload

## 🔒 **Security Considerations**

### **CORS Configuration**
The API supports CORS for web applications. Make sure your domain is included in the allowed origins.

### **File Validation**
- Always validate file types on the frontend
- Check file size before upload
- Sanitize file names if needed

### **Rate Limiting**
- Implement client-side rate limiting
- Show appropriate messages for rate limit errors
- Consider implementing retry logic with exponential backoff

## 🚀 **Best Practices**

### **User Experience**
1. **Show loading states** during processing
2. **Display progress indicators** for large files
3. **Provide clear error messages**
4. **Implement drag-and-drop** for better UX
5. **Show image previews** before processing

### **Performance**
1. **Compress images** before upload if possible
2. **Use appropriate image formats** (WebP for better compression)
3. **Implement caching** for repeated requests
4. **Lazy load** segmented images

### **Accessibility**
1. **Add proper alt text** for images
2. **Use semantic HTML** elements
3. **Ensure keyboard navigation** works
4. **Provide screen reader** support

## 📞 **Support**

For technical support or questions about the API:
- **Documentation**: Visit `/docs` endpoint for interactive API documentation
- **Health Check**: Use `/health` endpoint to verify API status
- **Issues**: Report bugs or feature requests through your development team

---

**Happy coding! 🎯**
