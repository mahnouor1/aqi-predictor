#!/usr/bin/env python3
"""
Enhanced Feature Pipeline for AQI Predictor
Fetches weather and pollutant data, computes features, and stores in feature store
"""

import os
import sys
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/feature_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FeaturePipeline:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '6ba231e87114c1df16cde745209442d4')
        self.lat, self.lon = 24.8607, 67.0011  # Karachi coordinates
        self.feature_store_path = Path('feature_store')
        self.feature_store_path.mkdir(exist_ok=True)
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
    def fetch_weather_data(self) -> Dict:
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
            
            logger.info("✅ Weather data fetched successfully")
            return weather_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching weather data: {e}")
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
    
    def fetch_pollutant_data(self) -> Dict:
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
            
            logger.info("✅ Pollutant data fetched successfully")
            return pollutant_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching pollutant data: {e}")
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
    
    def compute_time_features(self, timestamp: datetime) -> Dict:
        """Compute time-based features"""
        return {
            'hour': timestamp.hour,
            'day': timestamp.day,
            'month': timestamp.month,
            'day_of_week': timestamp.weekday(),
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
            'season': (timestamp.month % 12 + 3) // 3,  # 1=Spring, 2=Summer, 3=Fall, 4=Winter
        }
    
    def compute_derived_features(self, weather_data: Dict, pollutant_data: Dict) -> Dict:
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
        wind_speed = weather_data.get('windspeed_10m', 5)
        
        derived_features = {
            'aqi': aqi,
            'temp_humidity_ratio': temp / (humidity + 1),  # Avoid division by zero
            'wind_pressure_ratio': wind_speed / (weather_data.get('surface_pressure', 1000) / 100),
            'pollution_index': (pollutant_data.get('pm2_5', 0) + pollutant_data.get('pm10', 0)) / 2,
            'gas_pollution_index': (pollutant_data.get('co', 0) + pollutant_data.get('no2', 0) + pollutant_data.get('so2', 0)) / 3,
        }
        
        return derived_features
    
    def load_historical_data(self) -> pd.DataFrame:
        """Load historical data for trend analysis"""
        try:
            historical_file = self.feature_store_path / 'historical_features.csv'
            if historical_file.exists():
                df = pd.read_csv(historical_file)
                logger.info(f"✅ Loaded {len(df)} historical records")
                return df
            else:
                logger.info("No historical data found, starting fresh")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error loading historical data: {e}")
            return pd.DataFrame()
    
    def compute_trend_features(self, current_data: Dict, historical_df: pd.DataFrame) -> Dict:
        """Compute trend-based features using historical data"""
        if historical_df.empty:
            return {
                'aqi_change_rate': 0.0,
                'temp_change_rate': 0.0,
                'pm25_change_rate': 0.0,
                'avg_aqi_7d': current_data.get('aqi', 3),
                'avg_temp_7d': current_data.get('temperature_2m', 30),
            }
        
        # Calculate change rates (last 24 hours)
        recent_data = historical_df.tail(24) if len(historical_df) >= 24 else historical_df
        
        trend_features = {}
        
        if len(recent_data) > 1:
            # AQI change rate
            aqi_values = recent_data['aqi'].values
            trend_features['aqi_change_rate'] = float(np.diff(aqi_values).mean()) if len(aqi_values) > 1 else 0.0
            
            # Temperature change rate
            temp_values = recent_data['temperature_2m'].values
            trend_features['temp_change_rate'] = float(np.diff(temp_values).mean()) if len(temp_values) > 1 else 0.0
            
            # PM2.5 change rate
            pm25_values = recent_data['pm2_5'].values
            trend_features['pm25_change_rate'] = float(np.diff(pm25_values).mean()) if len(pm25_values) > 1 else 0.0
        
        # 7-day averages
        week_data = historical_df.tail(168) if len(historical_df) >= 168 else historical_df  # 7 days * 24 hours
        if not week_data.empty:
            trend_features['avg_aqi_7d'] = float(week_data['aqi'].mean())
            trend_features['avg_temp_7d'] = float(week_data['temperature_2m'].mean())
        else:
            trend_features['avg_aqi_7d'] = current_data.get('aqi', 3)
            trend_features['avg_temp_7d'] = current_data.get('temperature_2m', 30)
        
        return trend_features
    
    def save_features(self, features: Dict, timestamp: datetime):
        """Save features to feature store"""
        try:
            # Save to historical features
            historical_file = self.feature_store_path / 'historical_features.csv'
            
            # Add timestamp
            features['timestamp'] = timestamp.isoformat()
            features['datetime'] = timestamp
            
            # Load existing data
            if historical_file.exists():
                df = pd.read_csv(historical_file)
                new_row = pd.DataFrame([features])
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = pd.DataFrame([features])
            
            # Remove duplicates and keep only last 30 days
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.drop_duplicates(subset=['datetime'])
            df = df.sort_values('datetime')
            
            # Keep only last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            df = df[df['datetime'] >= cutoff_date]
            
            # Save
            df.to_csv(historical_file, index=False)
            
            # Save latest features for model inference
            latest_file = self.feature_store_path / 'latest_features.json'
            with open(latest_file, 'w') as f:
                json.dump(features, f, indent=2, default=str)
            
            logger.info(f"✅ Features saved successfully at {timestamp}")
            
        except Exception as e:
            logger.error(f"❌ Error saving features: {e}")
    
    def run_pipeline(self):
        """Run the complete feature pipeline"""
        logger.info("🚀 Starting feature pipeline...")
        
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
            
            logger.info("✅ Feature pipeline completed successfully!")
            
            # Log feature summary
            logger.info(f"📊 Feature summary:")
            logger.info(f"   - Temperature: {all_features.get('temperature_2m', 'N/A')}°C")
            logger.info(f"   - PM2.5: {all_features.get('pm2_5', 'N/A')} μg/m³")
            logger.info(f"   - AQI: {all_features.get('aqi', 'N/A')}")
            logger.info(f"   - AQI Change Rate: {all_features.get('aqi_change_rate', 'N/A')}")
            
        except Exception as e:
            logger.error(f"❌ Feature pipeline failed: {e}")
            raise

def main():
    """Main function to run the feature pipeline"""
    pipeline = FeaturePipeline()
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()
