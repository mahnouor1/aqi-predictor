#!/usr/bin/env python3
"""
Basic Test Script for AQI Predictor
Tests core functionality without external dependencies
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required packages can be imported"""
    logger.info("🧪 Testing package imports...")
    
    try:
        import streamlit as st
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import plotly.graph_objects as go
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
        import joblib
        import requests
        
        logger.info("✅ All packages imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False

def test_data_creation():
    """Test data creation and processing"""
    logger.info("📊 Testing data creation...")
    
    try:
        # Create sample data
        dates = [datetime.now() - timedelta(hours=i) for i in range(24)]
        n_samples = len(dates)
        
        data = {
            'datetime': dates,
            'temperature_2m': np.random.normal(30, 5, n_samples),
            'relative_humidity_2m': np.random.normal(70, 10, n_samples),
            'windspeed_10m': np.random.normal(5, 2, n_samples),
            'winddirection_10m': np.random.uniform(0, 360, n_samples),
            'precipitation': np.random.exponential(0.5, n_samples),
            'cloudcover': np.random.uniform(0, 100, n_samples),
            'surface_pressure': np.random.normal(1000, 20, n_samples),
            'co': np.random.exponential(50, n_samples),
            'no': np.random.exponential(0.05, n_samples),
            'no2': np.random.exponential(0.1, n_samples),
            'o3': np.random.normal(40, 10, n_samples),
            'so2': np.random.exponential(0.3, n_samples),
            'pm2_5': np.random.exponential(20, n_samples),
            'pm10': np.random.exponential(50, n_samples),
            'nh3': np.random.exponential(0.1, n_samples),
            'hour': [d.hour for d in dates],
            'day': [d.day for d in dates],
            'month': [d.month for d in dates],
            'aqi': np.random.randint(1, 6, n_samples)
        }
        
        df = pd.DataFrame(data)
        logger.info(f"✅ Created sample data: {len(df)} rows, {len(df.columns)} columns")
        
        # Save to feature store
        os.makedirs('feature_store', exist_ok=True)
        df.to_csv('feature_store/historical_features.csv', index=False)
        logger.info("✅ Data saved to feature store")
        
        return True, df
    except Exception as e:
        logger.error(f"❌ Data creation error: {e}")
        return False, None

def test_model_training(df):
    """Test model training with sample data"""
    logger.info("🤖 Testing model training...")
    
    try:
        # Prepare features
        feature_cols = [
            'temperature_2m', 'relative_humidity2m', 'windspeed_10m', 'winddirection_10m',
            'precipitation', 'cloudcover', 'surface_pressure',
            'co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3',
            'hour', 'day', 'month'
        ]
        
        X = df[feature_cols]
        y = df['aqi']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"✅ Model trained successfully")
        logger.info(f"   Test MSE: {mse:.4f}")
        logger.info(f"   Test R²: {r2:.4f}")
        
        # Save model
        os.makedirs('models', exist_ok=True)
        joblib.dump(model, 'models/aqi_model.pkl')
        logger.info("✅ Model saved")
        
        return True
    except Exception as e:
        logger.error(f"❌ Model training error: {e}")
        return False

def test_model_loading():
    """Test model loading"""
    logger.info("📦 Testing model loading...")
    
    try:
        model = joblib.load('models/aqi_model.pkl')
        
        # Test prediction
        sample_input = np.array([[30, 70, 5, 180, 0, 50, 1000, 50, 0.05, 0.1, 40, 0.3, 20, 50, 0.1, 12, 15, 1]])
        prediction = model.predict(sample_input)
        
        logger.info(f"✅ Model loaded successfully")
        logger.info(f"   Sample prediction: {prediction[0]:.2f}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Model loading error: {e}")
        return False

def test_streamlit_app():
    """Test if Streamlit app can be imported"""
    logger.info("🌐 Testing Streamlit app...")
    
    try:
        # Test app.py import
        sys.path.append('.')
        import app
        
        logger.info("✅ Streamlit app imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Streamlit app error: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting AQI Predictor basic tests...")
    
    tests = [
        ("Package Imports", test_imports),
        ("Data Creation", lambda: test_data_creation()),
        ("Model Training", lambda df: test_model_training(df) if df is not None else False),
        ("Model Loading", test_model_loading),
        ("Streamlit App", test_streamlit_app)
    ]
    
    results = []
    df = None
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            if test_name == "Data Creation":
                success, df = test_func()
                results.append((test_name, success))
            elif test_name == "Model Training":
                success = test_func(df)
                results.append((test_name, success))
            else:
                success = test_func()
                results.append((test_name, success))
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Your AQI Predictor is ready!")
        logger.info("\n🚀 Next steps:")
        logger.info("1. Run: streamlit run app.py")
        logger.info("2. Open: http://localhost:8501")
        logger.info("3. Test the prediction interface")
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
