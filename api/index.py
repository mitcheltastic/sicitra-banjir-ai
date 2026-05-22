import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

# Load model
MODEL_PATH = Path(__file__).parent.parent / 'model_banjir.pkl'

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Flood level mapping based on TMA thresholds
def get_flood_level(tma):
    """
    Determine flood level based on Tinggi Muka Air (TMA)
    - 0: Normal (< 0.57)
    - 1: Waspada/Siaga 3 (0.57 - 0.93)
    - 2: Siaga/Siaga 2 (0.93 - 1.30)
    - 3: Awas/Siaga 1 (> 1.30)
    """
    if tma < 0.57:
        return "0 - Normal"
    elif 0.57 <= tma < 0.93:
        return "1 - Waspada (Siaga 3)"
    elif 0.93 <= tma <= 1.30:
        return "2 - Siaga (Siaga 2)"
    else:
        return "3 - Awas (Siaga 1)"


@app.route('/', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Flood Prediction API is running",
        "model_loaded": model is not None
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict flood level based on input parameters
    
    Expected JSON payload:
    {
        "curah_hujan": 0.0 (optional),
        "debit_air": 0.0 (optional),
        "tinggi_muka_air": 0.0 (optional),
        "tinggi_genangan": 0.0 (optional),
        "kecamatan": "Dayeuhkolot" (optional, defaults to first location)
    }
    
    Returns:
    {
        "success": true,
        "prediction": {
            "flood_level": "0 - Normal",
            "flood_class": 0,
            "tma_value": 0.5,
            "description": "Kondisi aman"
        },
        "input_received": {...}
    }
    """
    try:
        if model is None:
            return jsonify({
                "success": False,
                "error": "Model not loaded"
            }), 500
        
        data = request.get_json()
        
        # Extract parameters with defaults
        curah_hujan = float(data.get('curah_hujan', 0.0))
        debit_air = float(data.get('debit_air', 0.0))
        tinggi_muka_air = float(data.get('tinggi_muka_air', 0.0))
        tinggi_genangan = float(data.get('tinggi_genangan', 0.0))
        
        # Get flood level from TMA
        flood_level_str = get_flood_level(tinggi_muka_air)
        
        # Prepare input for model prediction
        # Model expects: [Kecamatan, Curah Hujan, Debit Air, Muka Air]
        # Using 0 as default kecamatan encoding (you may need to adjust based on your data)
        kecamatan_encoded = 0  # Default value, can be enhanced with actual mapping
        
        input_features = np.array([[
            kecamatan_encoded,
            curah_hujan,
            debit_air,
            tinggi_muka_air
        ]])
        
        # Make prediction
        prediction_class = model.predict(input_features)[0]
        prediction_proba = model.predict_proba(input_features)[0]
        
        # Map prediction class to description
        class_descriptions = {
            0: "Kondisi aman",
            1: "Tingkat kewaspadaan meningkat",
            2: "Perlu siaga khusus",
            3: "Kondisi darurat banjir"
        }
        
        description = class_descriptions.get(prediction_class, "Unknown")
        
        return jsonify({
            "success": True,
            "prediction": {
                "flood_level": flood_level_str,
                "flood_class": int(prediction_class),
                "class_probability": {
                    "class_0_normal": float(prediction_proba[0]) if len(prediction_proba) > 0 else 0,
                    "class_1_waspada": float(prediction_proba[1]) if len(prediction_proba) > 1 else 0,
                    "class_2_siaga": float(prediction_proba[2]) if len(prediction_proba) > 2 else 0,
                    "class_3_awas": float(prediction_proba[3]) if len(prediction_proba) > 3 else 0,
                },
                "tma_value": tinggi_muka_air,
                "description": description,
                "risk_level": flood_level_str.split(' - ')[0]
            },
            "input_received": {
                "curah_hujan": curah_hujan,
                "debit_air": debit_air,
                "tinggi_muka_air": tinggi_muka_air,
                "tinggi_genangan": tinggi_genangan
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid input values: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Prediction failed: {str(e)}"
        }), 500


@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint - predict multiple samples at once
    
    Expected JSON payload:
    {
        "predictions": [
            {
                "curah_hujan": 0.0,
                "debit_air": 0.0,
                "tinggi_muka_air": 0.0
            },
            ...
        ]
    }
    """
    try:
        if model is None:
            return jsonify({
                "success": False,
                "error": "Model not loaded"
            }), 500
        
        data = request.get_json()
        predictions_input = data.get('predictions', [])
        
        results = []
        
        for idx, pred_data in enumerate(predictions_input):
            try:
                curah_hujan = float(pred_data.get('curah_hujan', 0.0))
                debit_air = float(pred_data.get('debit_air', 0.0))
                tinggi_muka_air = float(pred_data.get('tinggi_muka_air', 0.0))
                
                # Get flood level from TMA
                flood_level_str = get_flood_level(tinggi_muka_air)
                
                # Prepare input for model
                input_features = np.array([[0, curah_hujan, debit_air, tinggi_muka_air]])
                
                # Make prediction
                prediction_class = model.predict(input_features)[0]
                prediction_proba = model.predict_proba(input_features)[0]
                
                results.append({
                    "index": idx,
                    "flood_level": flood_level_str,
                    "flood_class": int(prediction_class),
                    "class_probability": list(map(float, prediction_proba)),
                    "tma_value": tinggi_muka_air,
                    "input": {
                        "curah_hujan": curah_hujan,
                        "debit_air": debit_air,
                        "tinggi_muka_air": tinggi_muka_air
                    }
                })
            except Exception as e:
                results.append({
                    "index": idx,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "batch_size": len(predictions_input),
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Batch prediction failed: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed. Use POST for predictions"
    }), 405


if __name__ == '__main__':
    app.run(debug=True)
