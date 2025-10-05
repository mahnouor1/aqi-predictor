#!/usr/bin/env python3
"""
Test script for feature pipeline
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_feature_pipeline_imports():
    """Test if all required imports work"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import requests
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        import logging
        from typing import Dict, List, Optional
        import json
        from pathlib import Path
        
        print("✅ Basic imports successful")
        
        # Test ML imports
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
        
        print("✅ ML imports successful")
        
        # Test if we can import the feature pipeline
        try:
            from scripts.feature_pipeline import FeaturePipeline
            print("✅ Feature pipeline import successful")
        except ImportError as e:
            print(f"❌ Feature pipeline import failed: {e}")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_feature_pipeline_basic():
    """Test basic feature pipeline functionality"""
    try:
        print("\nTesting feature pipeline basic functionality...")
        
        # Test if we can create a simple feature pipeline instance
        from scripts.feature_pipeline import FeaturePipeline
        
        # Create pipeline instance
        pipeline = FeaturePipeline()
        print("✅ Feature pipeline instance created")
        
        # Test basic data creation
        test_data = {
            'temperature': 25.0,
            'humidity': 60.0,
            'pressure': 1013.25,
            'wind_speed': 5.0,
            'wind_direction': 180.0,
            'pm2_5': 15.0,
            'pm10': 25.0,
            'o3': 0.05,
            'no2': 0.02,
            'so2': 0.01,
            'co': 1.0
        }
        
        # Test feature computation
        features = pipeline.compute_features(test_data)
        print(f"✅ Features computed: {len(features)} features")
        print(f"   Sample features: {list(features.keys())[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feature pipeline test failed: {e}")
        return False

def test_api_keys():
    """Test if API keys are available"""
    print("\nTesting API keys...")
    
    # Check for OpenWeather API key
    openweather_key = os.getenv('OPENWEATHER_API_KEY')
    if openweather_key:
        print("✅ OPENWEATHER_API_KEY found")
    else:
        print("⚠️  OPENWEATHER_API_KEY not found (will use mock data)")
    
    # Check for AQICN API key
    aqicn_key = os.getenv('AQICN_API_KEY')
    if aqicn_key:
        print("✅ AQICN_API_KEY found")
    else:
        print("⚠️  AQICN_API_KEY not found (will use mock data)")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Feature Pipeline")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_feature_pipeline_imports()
    
    if imports_ok:
        # Test basic functionality
        basic_ok = test_feature_pipeline_basic()
        
        # Test API keys
        api_ok = test_api_keys()
        
        if basic_ok and api_ok:
            print("\n🎉 All tests passed! Feature pipeline should work.")
            return True
        else:
            print("\n❌ Some tests failed. Check the errors above.")
            return False
    else:
        print("\n❌ Import tests failed. Check dependencies.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
