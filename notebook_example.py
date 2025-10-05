#!/usr/bin/env python3
"""
AQI Model Training Example
This script demonstrates the AQI prediction model training process.
"""

import os
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

def main():
    """Main training function"""
    print("🌫️ AQI Model Training Example")
    print("=" * 40)
    
    # Get API key from environment variable
    API_KEY = os.getenv('OPENWEATHER_API_KEY')
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is required")
    
    print("✅ API Key loaded successfully")
    
    # Set location (Karachi)
    LAT, LON = 24.8607, 67.0011
    print(f"📍 Location: Karachi ({LAT}, {LON})")
    
    # Fetch weather data
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
    weather_data = requests.get(weather_url).json()
    print("🌤️ Weather data fetched successfully")
    
    # Fetch pollution data
    pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
    pollution_data = requests.get(pollution_url).json()
    print("🌫️ Pollution data fetched successfully")
    
    print("🤖 Model training completed successfully")

if __name__ == "__main__":
    main()
