#!/usr/bin/env python
"""
Test script to verify model loading and basic predictions
Run this before deploying to ensure everything works
"""

import pickle
import numpy as np
import sys
from pathlib import Path

def test_model_loading():
    """Test if model can be loaded"""
    print("=" * 50)
    print("1. Testing Model Loading...")
    print("=" * 50)
    
    model_path = Path(__file__).parent / 'model_banjir.pkl'
    
    if not model_path.exists():
        print(f"❌ Model file not found at: {model_path}")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"✅ Model loaded successfully from: {model_path}")
        print(f"   Model type: {type(model)}")
        print(f"   Model: {model}")
        return model
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None


def test_prediction(model):
    """Test making predictions"""
    if model is None:
        print("⚠️  Skipping prediction test - model not loaded")
        return
    
    print("\n" + "=" * 50)
    print("2. Testing Predictions...")
    print("=" * 50)
    
    # Test case 1: Normal water level
    test_cases = [
        {
            "name": "Normal (Low water level)",
            "input": np.array([[0, 10.0, 5.0, 0.5]]),
            "description": "TMA < 0.57m"
        },
        {
            "name": "Waspada (Medium water level)",
            "input": np.array([[0, 50.0, 25.0, 0.75]]),
            "description": "0.57m ≤ TMA < 0.93m"
        },
        {
            "name": "Siaga (High water level)",
            "input": np.array([[0, 100.0, 45.0, 1.1]]),
            "description": "0.93m ≤ TMA ≤ 1.30m"
        },
        {
            "name": "Awas (Very high water level)",
            "input": np.array([[0, 150.0, 60.0, 1.5]]),
            "description": "TMA > 1.30m"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            prediction = model.predict(test_case["input"])[0]
            probabilities = model.predict_proba(test_case["input"])[0]
            
            print(f"\nTest Case {i}: {test_case['name']}")
            print(f"  Description: {test_case['description']}")
            print(f"  Input: Kecamatan=0, Curah Hujan={test_case['input'][0][1]}, "
                  f"Debit Air={test_case['input'][0][2]}, Muka Air={test_case['input'][0][3]}")
            print(f"  ✅ Predicted Class: {prediction}")
            print(f"     Probabilities: {probabilities}")
            
        except Exception as e:
            print(f"  ❌ Prediction failed: {e}")


def test_dependencies():
    """Test if all required packages are installed"""
    print("\n" + "=" * 50)
    print("3. Checking Dependencies...")
    print("=" * 50)
    
    required_packages = [
        'flask',
        'pickle',
        'numpy',
        'pandas',
        'xgboost',
        'sklearn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'pickle':
                # pickle is built-in
                __import__('pickle')
            elif package == 'sklearn':
                __import__('sklearn')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def test_model_features():
    """Test model features and properties"""
    print("\n" + "=" * 50)
    print("4. Model Properties...")
    print("=" * 50)
    
    if not hasattr(model, 'n_classes_'):
        print("❌ Model doesn't have n_classes_ attribute")
        return
    
    try:
        print(f"✅ Number of classes: {model.n_classes_}")
        print(f"✅ Number of features: {model.n_features_in_}")
        print(f"✅ Model estimators: {model.n_estimators}")
        
        # Expected: 4 features (Kecamatan, Curah Hujan, Debit Air, Muka Air)
        # Expected: 4 classes (0, 1, 2, 3)
        if model.n_features_in_ == 4 and model.n_classes_ == 4:
            print("\n✅ Model configuration matches expectations!")
            print("   - 4 features expected ✅")
            print("   - 4 classes expected ✅")
        else:
            print(f"\n⚠️  Unexpected model configuration:")
            print(f"   - Features: {model.n_features_in_} (expected 4)")
            print(f"   - Classes: {model.n_classes_} (expected 4)")
    except Exception as e:
        print(f"❌ Error reading model properties: {e}")


def test_api_components():
    """Test if API components work"""
    print("\n" + "=" * 50)
    print("5. Testing API Components...")
    print("=" * 50)
    
    try:
        from flask import Flask, request, jsonify
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Flask: {e}")
        return False
    
    try:
        from pathlib import Path
        print("✅ pathlib imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pathlib: {e}")
        return False
    
    print("✅ All API components available!")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("🌊 Flood Prediction Model & API Test Suite")
    print("=" * 50)
    
    # Test 1: Dependencies
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Please install missing dependencies and try again")
        sys.exit(1)
    
    # Test 2: Load model
    global model
    model = test_model_loading()
    
    if model is None:
        print("\n❌ Cannot continue without model")
        sys.exit(1)
    
    # Test 3: Make predictions
    test_prediction(model)
    
    # Test 4: Model properties
    test_model_features()
    
    # Test 5: API components
    test_api_components()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run locally: python api/index.py")
    print("2. Test the API: curl http://localhost:5000/api/predict")
    print("3. Deploy to Vercel using the guide: VERCEL_DEPLOYMENT_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
