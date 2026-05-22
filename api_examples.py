"""
Example usage of the Flood Prediction API
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:5000/api/predict"  # Local development
# For production: API_URL = "https://your-vercel-app.vercel.app/api/predict"

# Example 1: Simple prediction with single values
def example_single_prediction():
    """Make a single prediction"""
    payload = {
        "curah_hujan": 50.0,          # Rainfall in mm (optional)
        "debit_air": 25.5,            # Water discharge in m3/s (optional)
        "tinggi_muka_air": 0.85,      # Water level in m (optional)
        "tinggi_genangan": 0.3        # Flood depth in m (optional)
    }
    
    response = requests.post(API_URL, json=payload)
    result = response.json()
    
    print("Single Prediction Result:")
    print(json.dumps(result, indent=2))
    print()


# Example 2: Batch prediction
def example_batch_prediction():
    """Make multiple predictions at once"""
    payload = {
        "predictions": [
            {"curah_hujan": 30.0, "debit_air": 15.0, "tinggi_muka_air": 0.5},
            {"curah_hujan": 75.0, "debit_air": 35.0, "tinggi_muka_air": 1.0},
            {"curah_hujan": 120.0, "debit_air": 50.0, "tinggi_muka_air": 1.5},
        ]
    }
    
    response = requests.post(
        "http://localhost:5000/api/predict/batch",
        json=payload
    )
    result = response.json()
    
    print("Batch Prediction Results:")
    print(json.dumps(result, indent=2))
    print()


# Example 3: Minimal input (using defaults)
def example_minimal_input():
    """Make prediction with minimal input (only TMA)"""
    payload = {
        "tinggi_muka_air": 0.7
    }
    
    response = requests.post(API_URL, json=payload)
    result = response.json()
    
    print("Minimal Input Prediction:")
    print(json.dumps(result, indent=2))
    print()


# Example 4: Using cURL (for testing without Python)
def show_curl_examples():
    """Show how to use the API with cURL"""
    print("=== CURL Examples ===")
    print("\n1. Single Prediction:")
    print('''
curl -X POST http://localhost:5000/api/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "curah_hujan": 50.0,
    "debit_air": 25.5,
    "tinggi_muka_air": 0.85,
    "tinggi_genangan": 0.3
  }'
    ''')
    
    print("\n2. Batch Prediction:")
    print('''
curl -X POST http://localhost:5000/api/predict/batch \\
  -H "Content-Type: application/json" \\
  -d '{
    "predictions": [
      {"curah_hujan": 30, "debit_air": 15, "tinggi_muka_air": 0.5},
      {"curah_hujan": 75, "debit_air": 35, "tinggi_muka_air": 1.0}
    ]
  }'
    ''')


if __name__ == "__main__":
    print("🌊 Flood Prediction API - Usage Examples\n")
    
    # Show curl examples
    show_curl_examples()
    
    # Note: These examples require the server to be running
    # Uncomment below to test against a running server
    
    # try:
    #     print("\n\n=== Running Python Examples ===\n")
    #     example_single_prediction()
    #     example_batch_prediction()
    #     example_minimal_input()
    # except requests.exceptions.ConnectionError:
    #     print("Error: Could not connect to API. Make sure the server is running.")
