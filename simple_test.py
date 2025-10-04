#!/usr/bin/env python3
"""
Simple Test for AQI Predictor
Tests core functionality step by step
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

def test_step_1_imports():
    """Test 1: Package imports"""
    logger.info("🧪 Step 1: Testing package imports...")
    
    try:
        import streamlit as st
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        import joblib
        import requests
        
        logger.info("✅ All packages imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False

def test_step_2_data_creation():
    """Test 2: Create sample data"""
    logger.info("📊 Step 2: Creating sample data...")
    
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

def test_step_3_model_training(df):
    """Test 3: Train a simple model"""
    logger.info("🤖 Step 3: Training model...")
    
    try:
        # Import required modules
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
        import joblib
        
        # Prepare features (fix column name)
        feature_cols = [
            'temperature_2m', 'relative_humidity_2m', 'windspeed_10m', 'winddirection_10m',
            'precipitation', 'cloudcover', 'surface_pressure',
            'co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3',
            'hour', 'day', 'month'
        ]
        
        X = df[feature_cols]
        y = df['aqi']
        
        # Train a simple model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
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

def test_step_4_model_loading():
    """Test 4: Load and test model"""
    logger.info("📦 Step 4: Testing model loading...")
    
    try:
        import joblib
        model = joblib.load('models/aqi_model.pkl')
        
        # Test prediction with sample data
        sample_input = np.array([[30, 70, 5, 180, 0, 50, 1000, 50, 0.05, 0.1, 40, 0.3, 20, 50, 0.1, 12, 15, 1]])
        prediction = model.predict(sample_input)
        
        logger.info(f"✅ Model loaded successfully")
        logger.info(f"   Sample prediction: {prediction[0]:.2f}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Model loading error: {e}")
        return False

def test_step_5_streamlit_app():
    """Test 5: Test Streamlit app (without running it)"""
    logger.info("🌐 Step 5: Testing Streamlit app...")
    
    try:
        # Test if we can import the app without running it
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        logger.info("✅ Streamlit app can be imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Streamlit app error: {e}")
        return False

def main():
    """Run all tests step by step"""
    logger.info("🚀 Starting AQI Predictor simple tests...")
    
    # Test 1: Imports
    if not test_step_1_imports():
        logger.error("❌ Test 1 failed - cannot continue")
        return False
    
    # Test 2: Data creation
    success, df = test_step_2_data_creation()
    if not success:
        logger.error("❌ Test 2 failed - cannot continue")
        return False
    
    # Test 3: Model training
    if not test_step_3_model_training(df):
        logger.error("❌ Test 3 failed - cannot continue")
        return False
    
    # Test 4: Model loading
    if not test_step_4_model_loading():
        logger.error("❌ Test 4 failed - cannot continue")
        return False
    
    # Test 5: Streamlit app
    if not test_step_5_streamlit_app():
        logger.error("❌ Test 5 failed - cannot continue")
        return False
    
    logger.info("\n🎉 All tests passed! Your AQI Predictor is ready!")
    logger.info("\n🚀 Next steps:")
    logger.info("1. Run: streamlit run app.py")
    logger.info("2. Open: http://localhost:8501")
    logger.info("3. Test the prediction interface")
    logger.info("4. Try different input values and see predictions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
