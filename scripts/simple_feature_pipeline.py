#!/usr/bin/env python3
"""
Simplified Feature Pipeline for AQI Predictor
Fetches weather and pollutant data, computes features, and stores in feature store
"""

import os
import sys
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleFeaturePipeline:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '6ba231e87114c1df16cde745209442d4')
        self.lat, self.lon = 24.8607, 67.0011  # Karachi coordinates
        self.feature_store_path = Path('feature_store')
        self.feature_store_path.mkdir(exist_ok=True)
        
    def fetch_weather_data(self) -> dict:
        """Fetch current weather data from Open-Meteo API"""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current_weather=true&hourly=temperature_2m,relative_humidity_2m,precipitation,cloudcover,surface_pressure"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            current = data["current_weather"]
            hourly = data["hourly"]
            
            # Get current hour index
            current_time = datetime.now()
            hour_index = current_time.hour
            
            weather_data = {
                'temperature_2m': current['temperature'],
                'windspeed_10m': current['windspeed'],
                'winddirection_10m': current['winddirection'],
                'relative_humidity_2m': hourly['relative_humidity_2m'][hour_index] if hour_index < len(hourly['relative_humidity_2m']) else 50,
                'precipitation': hourly['precipitation'][hour_index] if hour_index < len(hourly['precipitation']) else 0,
                'cloudcover': hourly['cloudcover'][hour_index] if hour_index < len(hourly['cloudcover']) else 50,
                'surface_pressure': hourly['surface_pressure'][hour_index] if hour_index < len(hourly['surface_pressure']) else 1000,
            }
            
            print("✅ Weather data fetched successfully")
            return weather_data
            
        except Exception as e:
            print(f"❌ Error fetching weather data: {e}")
            # Return default values
            return {
                'temperature_2m': 30.0,
                'windspeed_10m': 5.0,
                'winddirection_10m': 180.0,
                'relative_humidity_2m': 70.0,
                'precipitation': 0.0,
                'cloudcover': 50.0,
                'surface_pressure': 1000.0,
            }
    
    def fetch_pollutant_data(self) -> dict:
        """Fetch air pollution data from OpenWeather API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pollutants = data["list"][0]["components"]
            
            pollutant_data = {
                'co': pollutants.get('co', 0.0),
                'no': pollutants.get('no', 0.0),
                'no2': pollutants.get('no2', 0.0),
                'o3': pollutants.get('o3', 0.0),
                'so2': pollutants.get('so2', 0.0),
                'pm2_5': pollutants.get('pm2_5', 0.0),
                'pm10': pollutants.get('pm10', 0.0),
                'nh3': pollutants.get('nh3', 0.0),
            }
            
            print("✅ Pollutant data fetched successfully")
            return pollutant_data
            
        except Exception as e:
            print(f"❌ Error fetching pollutant data: {e}")
            # Return default values
            return {
                'co': 50.0,
                'no': 0.05,
                'no2': 0.1,
                'o3': 40.0,
                'so2': 0.3,
                'pm2_5': 20.0,
                'pm10': 50.0,
                'nh3': 0.1,
            }
    
    def compute_time_features(self, timestamp: datetime) -> dict:
        """Compute time-based features"""
        return {
            'hour': timestamp.hour,
            'day': timestamp.day,
            'month': timestamp.month,
            'day_of_week': timestamp.weekday(),
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
            'season': (timestamp.month % 12 + 3) // 3,  # 1=Spring, 2=Summer, 3=Fall, 4=Winter
        }
    
    def compute_derived_features(self, weather_data: dict, pollutant_data: dict) -> dict:
        """Compute derived features from raw data"""
        # AQI calculation based on PM2.5 (simplified)
        pm25 = pollutant_data.get('pm2_5', 0)
        if pm25 <= 12:
            aqi = 1
        elif pm25 <= 35.4:
            aqi = 2
        elif pm25 <= 55.4:
            aqi = 3
        elif pm25 <= 150.4:
            aqi = 4
        else:
            aqi = 5
        
        # Weather-based features
        temp = weather_data.get('temperature_2m', 30)
        humidity = weather_data.get('relative_humidity_2m', 70)
        
        return {
            'aqi': aqi,
            'aqi_change_rate': 0.0,  # Simplified - no historical comparison
            'heat_index': temp + humidity * 0.1,  # Simplified heat index
            'comfort_index': 1 if 20 <= temp <= 25 and 40 <= humidity <= 60 else 0,
            'pollution_index': pm25 / 50.0,  # Normalized pollution
        }
    
    def load_historical_data(self) -> pd.DataFrame:
        """Load historical data for trend analysis"""
        try:
            # Try to load existing historical data
            historical_file = self.feature_store_path / 'historical_data.json'
            if historical_file.exists():
                with open(historical_file, 'r') as f:
                    data = json.load(f)
                return pd.DataFrame(data)
            else:
                # Return empty DataFrame if no historical data
                return pd.DataFrame()
        except Exception as e:
            print(f"⚠️ Could not load historical data: {e}")
            return pd.DataFrame()
    
    def compute_trend_features(self, current_data: dict, historical_df: pd.DataFrame) -> dict:
        """Compute trend features from historical data"""
        if historical_df.empty:
            # Return default trend features if no historical data
            return {
                'aqi_lag1': current_data.get('aqi', 1),
                'aqi_lag2': current_data.get('aqi', 1),
                'aqi_rolling3': current_data.get('aqi', 1),
                'aqi_rolling6': current_data.get('aqi', 1),
            }
        
        try:
            # Get recent AQI values
            recent_aqi = historical_df['aqi'].tail(6).tolist()
            
            return {
                'aqi_lag1': recent_aqi[-1] if len(recent_aqi) >= 1 else current_data.get('aqi', 1),
                'aqi_lag2': recent_aqi[-2] if len(recent_aqi) >= 2 else current_data.get('aqi', 1),
                'aqi_rolling3': np.mean(recent_aqi[-3:]) if len(recent_aqi) >= 3 else current_data.get('aqi', 1),
                'aqi_rolling6': np.mean(recent_aqi[-6:]) if len(recent_aqi) >= 6 else current_data.get('aqi', 1),
            }
        except Exception as e:
            print(f"⚠️ Error computing trend features: {e}")
            return {
                'aqi_lag1': current_data.get('aqi', 1),
                'aqi_lag2': current_data.get('aqi', 1),
                'aqi_rolling3': current_data.get('aqi', 1),
                'aqi_rolling6': current_data.get('aqi', 1),
            }
    
    def save_features(self, features: dict, timestamp: datetime):
        """Save features to feature store"""
        try:
            # Save current features
            features['timestamp'] = timestamp.isoformat()
            features_file = self.feature_store_path / f'features_{timestamp.strftime("%Y%m%d_%H%M%S")}.json'
            
            with open(features_file, 'w') as f:
                json.dump(features, f, indent=2, default=str)
            
            # Update historical data
            historical_file = self.feature_store_path / 'historical_data.json'
            historical_data = []
            
            if historical_file.exists():
                with open(historical_file, 'r') as f:
                    historical_data = json.load(f)
            
            # Add current features to historical data
            historical_data.append(features)
            
            # Keep only last 100 records to avoid file size issues
            if len(historical_data) > 100:
                historical_data = historical_data[-100:]
            
            with open(historical_file, 'w') as f:
                json.dump(historical_data, f, indent=2, default=str)
            
            print(f"✅ Features saved successfully at {timestamp}")
            
        except Exception as e:
            print(f"❌ Error saving features: {e}")
    
    def run_pipeline(self):
        """Run the complete feature pipeline"""
        print("🚀 Starting simplified feature pipeline...")
        
        try:
            # Get current timestamp
            timestamp = datetime.now()
            
            # Fetch data
            weather_data = self.fetch_weather_data()
            pollutant_data = self.fetch_pollutant_data()
            
            # Compute features
            time_features = self.compute_time_features(timestamp)
            derived_features = self.compute_derived_features(weather_data, pollutant_data)
            
            # Load historical data for trends
            historical_df = self.load_historical_data()
            trend_features = self.compute_trend_features(
                {**weather_data, **pollutant_data, **derived_features}, 
                historical_df
            )
            
            # Combine all features
            all_features = {
                **weather_data,
                **pollutant_data,
                **time_features,
                **derived_features,
                **trend_features
            }
            
            # Save features
            self.save_features(all_features, timestamp)
            
            print("✅ Feature pipeline completed successfully!")
            
            # Log feature summary
            print(f"📊 Feature summary:")
            print(f"   - Temperature: {all_features.get('temperature_2m', 'N/A')}°C")
            print(f"   - PM2.5: {all_features.get('pm2_5', 'N/A')} μg/m³")
            print(f"   - AQI: {all_features.get('aqi', 'N/A')}")
            print(f"   - AQI Change Rate: {all_features.get('aqi_change_rate', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Feature pipeline failed: {e}")
            raise

def main():
    """Main function to run the pipeline"""
    try:
        pipeline = SimpleFeaturePipeline()
        pipeline.run_pipeline()
        print("🎉 Pipeline completed successfully!")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
