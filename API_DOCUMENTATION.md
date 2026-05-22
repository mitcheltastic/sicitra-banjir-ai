# 🌊 Flood Prediction API Documentation

## Overview
This Flask API provides flood level predictions using an XGBoost machine learning model trained on Bandung region flood data. The API is designed to be deployed on Vercel as a serverless function.

## Model Information

### Model Type
- **Algorithm**: XGBoost Classifier (Multiclass)
- **File**: `model_banjir.pkl`
- **Output Classes**: 4 flood risk levels

### Input Features
The model expects 4 features:
1. **Kecamatan** (District) - Encoded as integer (default: 0)
2. **Curah Hujan** - Rainfall in mm (optional)
3. **Debit Air** - Water discharge in m³/s (optional)
4. **Muka Air** - Water level/height in meters (optional)

### Output Classes
```
0 - Normal         (TMA < 0.57 m)           → Safe condition
1 - Waspada        (0.57 ≤ TMA < 0.93 m)   → Alert level
2 - Siaga          (0.93 ≤ TMA ≤ 1.30 m)   → Warning level
3 - Awas           (TMA > 1.30 m)          → Emergency level
```

### Thresholds
- **TMA (Tinggi Muka Air)** thresholds determine the flood risk level
- Water level is the primary indicator used for classification

---

## API Endpoints

### 1. Health Check
**GET** `/`

Check if the API is running and the model is loaded.

**Response:**
```json
{
  "status": "ok",
  "message": "Flood Prediction API is running",
  "model_loaded": true
}
```

---

### 2. Single Prediction
**POST** `/api/predict`

Make a single flood level prediction.

**Request Body:**
```json
{
  "curah_hujan": 50.0,
  "debit_air": 25.5,
  "tinggi_muka_air": 0.85,
  "tinggi_genangan": 0.3
}
```

**Parameters:**
- `curah_hujan` (float, optional): Rainfall in mm. Default: 0.0
- `debit_air` (float, optional): Water discharge in m³/s. Default: 0.0
- `tinggi_muka_air` (float, optional): Water level in meters. Default: 0.0
- `tinggi_genangan` (float, optional): Flood depth in meters. Default: 0.0

**Response:**
```json
{
  "success": true,
  "prediction": {
    "flood_level": "1 - Waspada (Siaga 3)",
    "flood_class": 1,
    "class_probability": {
      "class_0_normal": 0.15,
      "class_1_waspada": 0.65,
      "class_2_siaga": 0.18,
      "class_3_awas": 0.02
    },
    "tma_value": 0.85,
    "description": "Tingkat kewaspadaan meningkat",
    "risk_level": "1"
  },
  "input_received": {
    "curah_hujan": 50.0,
    "debit_air": 25.5,
    "tinggi_muka_air": 0.85,
    "tinggi_genangan": 0.3
  }
}
```

**Status Codes:**
- `200`: Successful prediction
- `400`: Invalid input values
- `500`: Model not loaded or prediction error

---

### 3. Batch Prediction
**POST** `/api/predict/batch`

Make multiple predictions in a single request.

**Request Body:**
```json
{
  "predictions": [
    {"curah_hujan": 30.0, "debit_air": 15.0, "tinggi_muka_air": 0.5},
    {"curah_hujan": 75.0, "debit_air": 35.0, "tinggi_muka_air": 1.0},
    {"curah_hujan": 120.0, "debit_air": 50.0, "tinggi_muka_air": 1.5}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "batch_size": 3,
  "results": [
    {
      "index": 0,
      "flood_level": "0 - Normal",
      "flood_class": 0,
      "class_probability": [0.95, 0.04, 0.01, 0.0],
      "tma_value": 0.5,
      "input": {
        "curah_hujan": 30.0,
        "debit_air": 15.0,
        "tinggi_muka_air": 0.5
      }
    },
    ...
  ]
}
```

---

## Usage Examples

### Using cURL
```bash
# Single prediction
curl -X POST https://your-vercel-app.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "curah_hujan": 50.0,
    "debit_air": 25.5,
    "tinggi_muka_air": 0.85
  }'
```

### Using Python (requests library)
```python
import requests

url = "https://your-vercel-app.vercel.app/api/predict"
payload = {
    "curah_hujan": 50.0,
    "debit_air": 25.5,
    "tinggi_muka_air": 0.85
}

response = requests.post(url, json=payload)
result = response.json()
print(result)
```

### Using JavaScript (fetch)
```javascript
const url = "https://your-vercel-app.vercel.app/api/predict";
const payload = {
  curah_hujan: 50.0,
  debit_air: 25.5,
  tinggi_muka_air: 0.85
};

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Local Development

### Prerequisites
- Python 3.7+
- pip

### Installation
```bash
# Clone or navigate to the repository
cd sicitra-banjir-ai

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the API Locally
```bash
python api/index.py
```

The API will start at `http://localhost:5000`

### Testing Endpoints Locally
```bash
# Health check
curl http://localhost:5000/

# Single prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"tinggi_muka_air": 0.85}'
```

---

## Deployment to Vercel

### Prerequisites
- Vercel account (free at https://vercel.com)
- Git repository (GitHub, GitLab, or Bitbucket)
- Vercel CLI (optional but recommended)

### Step 1: Prepare Your Repository
```bash
git add .
git commit -m "Add Flask API for flood prediction"
git push origin main
```

### Step 2: Deploy via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Select your Git repository (sicitra-banjir-ai)
4. Vercel will automatically detect the `vercel.json` configuration
5. Click "Deploy"

**The API will be available at:** `https://your-project.vercel.app`

### Step 3: Deploy via Vercel CLI (Alternative)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from your project directory
vercel

# For production deployment
vercel --prod
```

### Important: Model File Size
- Ensure `model_banjir.pkl` is included in your Git repository
- If the file is large (>50MB), you may hit Vercel's file size limits
- Consider:
  - Storing the model in a cloud storage service (AWS S3, Google Cloud Storage)
  - Or using a model registry like Hugging Face Model Hub
  - Or requesting a larger build timeout from Vercel support

### Environment Variables (if needed)
Create a `.env.local` file for local development:
```
MODEL_PATH=/path/to/model_banjir.pkl
```

---

## Response Descriptions

### Flood Level Classifications

| Class | Level | TMA Range | Description | Action |
|-------|-------|-----------|-------------|--------|
| 0 | Normal | < 0.57 m | Kondisi aman | Monitor routine |
| 1 | Waspada | 0.57-0.93 m | Tingkat kewaspadaan meningkat | Increase monitoring |
| 2 | Siaga | 0.93-1.30 m | Perlu siaga khusus | Prepare evacuation |
| 3 | Awas | > 1.30 m | Kondisi darurat banjir | Immediate evacuation |

### Probability Scores
The `class_probability` field provides confidence scores for each flood level class:
- Values range from 0 to 1
- Sum of all probabilities = 1.0
- Higher value = higher model confidence

---

## Error Handling

### Common Error Responses

**Model Not Loaded (500)**
```json
{
  "success": false,
  "error": "Model not loaded"
}
```

**Invalid Input (400)**
```json
{
  "success": false,
  "error": "Invalid input values: could not convert string to float"
}
```

**Endpoint Not Found (404)**
```json
{
  "success": false,
  "error": "Endpoint not found"
}
```

**Method Not Allowed (405)**
```json
{
  "success": false,
  "error": "Method not allowed. Use POST for predictions"
}
```

---

## Advanced Usage

### Real-time Monitoring Integration
```python
import requests
import time
from datetime import datetime

def monitor_flood_levels(sensor_url, prediction_url, interval=300):
    """Monitor sensor data and make predictions every interval seconds"""
    while True:
        try:
            # Get sensor data
            sensor_data = requests.get(sensor_url).json()
            
            # Make prediction
            pred_payload = {
                "curah_hujan": sensor_data.get("rainfall"),
                "debit_air": sensor_data.get("discharge"),
                "tinggi_muka_air": sensor_data.get("water_level")
            }
            
            response = requests.post(prediction_url, json=pred_payload)
            result = response.json()
            
            # Log result
            timestamp = datetime.now().isoformat()
            print(f"[{timestamp}] Flood Level: {result['prediction']['flood_level']}")
            
            # Alert if dangerous
            if result['prediction']['flood_class'] >= 2:
                send_alert(result)
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(interval)
```

### Model Information Endpoint (Future Enhancement)
Consider adding an endpoint to retrieve model metadata:
```python
@app.route('/api/model-info', methods=['GET'])
def model_info():
    return jsonify({
        "model_type": "XGBoost Classifier",
        "n_classes": 4,
        "n_features": 4,
        "feature_names": ["Kecamatan", "Curah Hujan", "Debit Air", "Muka Air"],
        "class_labels": ["Normal", "Waspada", "Siaga", "Awas"]
    })
```

---

## Troubleshooting

### Issue: Model file not found
**Solution**: Ensure `model_banjir.pkl` is in the root directory and committed to Git

### Issue: Slow predictions on Vercel
**Solution**: This is normal for cold starts. Consider:
- Implementing model caching
- Using Vercel Pro for faster CPU

### Issue: File too large error
**Solution**: Use a cloud storage service for the model file and download it at runtime

### Issue: CORS errors
**Solution**: Add CORS headers to the Flask app:
```python
from flask_cors import CORS
CORS(app)
```

---

## Performance Metrics

### Expected Response Times (Local)
- Health check: ~10ms
- Single prediction: ~50-100ms
- Batch prediction: ~50-200ms (depending on batch size)

### Expected Response Times (Vercel)
- Cold start: 1-3 seconds
- Warm requests: 100-300ms

---

## Support & Questions
For issues or questions about the model or API:
1. Check the [XGBoost.ipynb](../XGBoost.ipynb) for model training details
2. Review the README.md for project background
3. Check Vercel documentation: https://vercel.com/docs

---

**Last Updated**: May 2026
**Model Version**: model_banjir.pkl
**API Version**: 1.0
