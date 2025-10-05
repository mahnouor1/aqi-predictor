#!/usr/bin/env python3
"""
PM2.5 Data Fetcher - Real-time AQI Data Collection
Fetches weather and pollution data every hour for AQI prediction
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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PM25Fetcher:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is required")
        
        self.lat, self.lon = 24.8607, 67.0011  # Karachi coordinates
        self.data_path = Path('data')
        self.data_path.mkdir(exist_ok=True)
        
    def fetch_weather_data(self):
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
                'timestamp': current_time.isoformat(),
                'temperature_2m': current['temperature'],
                'windspeed_10m': current['windspeed'],
                'winddirection_10m': current['winddirection'],
                'relative_humidity_2m': hourly['relative_humidity_2m'][hour_index] if hour_index < len(hourly['relative_humidity_2m']) else 50,
                'precipitation': hourly['precipitation'][hour_index] if hour_index < len(hourly['precipitation']) else 0,
                'cloudcover': hourly['cloudcover'][hour_index] if hour_index < len(hourly['cloudcover']) else 50,
                'surface_pressure': hourly['surface_pressure'][hour_index] if hour_index < len(hourly['surface_pressure']) else 1000,
            }
            
            print(f"🌤️ Weather data fetched at {current_time}")
            return weather_data
            
        except Exception as e:
            print(f"❌ Error fetching weather data: {e}")
            return None
    
    def fetch_pollution_data(self):
        """Fetch air pollution data from OpenWeather API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pollutants = data["list"][0]["components"]
            
            pollution_data = {
                'timestamp': datetime.now().isoformat(),
                'co': pollutants.get('co', 0.0),
                'no': pollutants.get('no', 0.0),
                'no2': pollutants.get('no2', 0.0),
                'o3': pollutants.get('o3', 0.0),
                'so2': pollutants.get('so2', 0.0),
                'pm2_5': pollutants.get('pm2_5', 0.0),
                'pm10': pollutants.get('pm10', 0.0),
                'nh3': pollutants.get('nh3', 0.0),
            }
            
            print(f"🌫️ Pollution data fetched at {datetime.now()}")
            return pollution_data
            
        except Exception as e:
            print(f"❌ Error fetching pollution data: {e}")
            return None
    
    def save_data(self, weather_data, pollution_data):
        """Save fetched data to files"""
        try:
            timestamp = datetime.now()
            
            # Save weather data
            weather_file = self.data_path / f'weather_{timestamp.strftime("%Y%m%d_%H%M%S")}.json'
            with open(weather_file, 'w') as f:
                json.dump(weather_data, f, indent=2)
            
            # Save pollution data
            pollution_file = self.data_path / f'pollution_{timestamp.strftime("%Y%m%d_%H%M%S")}.json'
            with open(pollution_file, 'w') as f:
                json.dump(pollution_data, f, indent=2)
            
            # Update latest data
            latest_weather = self.data_path / 'latest_weather.json'
            latest_pollution = self.data_path / 'latest_pollution.json'
            
            with open(latest_weather, 'w') as f:
                json.dump(weather_data, f, indent=2)
            
            with open(latest_pollution, 'w') as f:
                json.dump(pollution_data, f, indent=2)
            
            print(f"💾 Data saved successfully at {timestamp}")
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def run_fetch(self):
        """Run the complete data fetching process"""
        print("🚀 Starting PM2.5 data fetching...")
        print(f"📍 Location: Karachi ({self.lat}, {self.lon})")
        print(f"⏰ Time: {datetime.now()}")
        
        # Fetch data
        weather_data = self.fetch_weather_data()
        pollution_data = self.fetch_pollution_data()
        
        if weather_data and pollution_data:
            # Save data
            self.save_data(weather_data, pollution_data)
            
            # Log summary
            print(f"📊 Data Summary:")
            print(f"   - Temperature: {weather_data.get('temperature_2m', 'N/A')}°C")
            print(f"   - PM2.5: {pollution_data.get('pm2_5', 'N/A')} μg/m³")
            print(f"   - PM10: {pollution_data.get('pm10', 'N/A')} μg/m³")
            print(f"   - O3: {pollution_data.get('o3', 'N/A')} μg/m³")
            
            print("✅ PM2.5 data fetching completed successfully!")
            return True
        else:
            print("❌ PM2.5 data fetching failed!")
            return False

def main():
    """Main function"""
    try:
        fetcher = PM25Fetcher()
        success = fetcher.run_fetch()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ PM2.5 fetcher failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
