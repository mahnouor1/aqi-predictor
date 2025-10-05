#!/usr/bin/env python3
"""
Simplified Training Pipeline for AQI Predictor
Trains ML models and saves them
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import joblib

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ML imports
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

class SimpleTrainingPipeline:
    def __init__(self):
        self.models_path = Path('models')
        self.models_path.mkdir(exist_ok=True)
        self.feature_store_path = Path('feature_store')
        
    def load_training_data(self) -> pd.DataFrame:
        """Load training data from feature store"""
        try:
            # Load historical data
            historical_file = self.feature_store_path / 'historical_data.json'
            if not historical_file.exists():
                print("⚠️ No historical data found, creating synthetic data...")
                return self.create_synthetic_data()
            
            with open(historical_file, 'r') as f:
                data = json.load(f)
            
            if not data:
                print("⚠️ No data in historical file, creating synthetic data...")
                return self.create_synthetic_data()
            
            df = pd.DataFrame(data)
            print(f"✅ Loaded {len(df)} training samples")
            return df
            
        except Exception as e:
            print(f"❌ Error loading training data: {e}")
            print("Creating synthetic data...")
            return self.create_synthetic_data()
    
    def create_synthetic_data(self) -> pd.DataFrame:
        """Create synthetic training data"""
        print("Creating synthetic training data...")
        
        # Generate synthetic data
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'temperature_2m': np.random.normal(25, 10, n_samples),
            'windspeed_10m': np.random.normal(5, 3, n_samples),
            'winddirection_10m': np.random.uniform(0, 360, n_samples),
            'relative_humidity_2m': np.random.uniform(20, 90, n_samples),
            'precipitation': np.random.exponential(2, n_samples),
            'cloudcover': np.random.uniform(0, 100, n_samples),
            'surface_pressure': np.random.normal(1013, 20, n_samples),
            'co': np.random.exponential(50, n_samples),
            'no': np.random.exponential(0.05, n_samples),
            'no2': np.random.exponential(0.1, n_samples),
            'o3': np.random.exponential(40, n_samples),
            'so2': np.random.exponential(0.3, n_samples),
            'pm2_5': np.random.exponential(20, n_samples),
            'pm10': np.random.exponential(50, n_samples),
            'nh3': np.random.exponential(0.1, n_samples),
            'hour': np.random.randint(0, 24, n_samples),
            'day': np.random.randint(1, 32, n_samples),
            'month': np.random.randint(1, 13, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'is_weekend': np.random.randint(0, 2, n_samples),
            'season': np.random.randint(1, 5, n_samples),
        }
        
        # Create target variable (AQI) based on PM2.5
        pm25 = data['pm2_5']
        aqi = np.where(pm25 <= 12, 1,
                      np.where(pm25 <= 35.4, 2,
                              np.where(pm25 <= 55.4, 3,
                                      np.where(pm25 <= 150.4, 4, 5))))
        
        data['aqi'] = aqi
        data['aqi_change_rate'] = np.random.normal(0, 0.5, n_samples)
        data['heat_index'] = data['temperature_2m'] + data['relative_humidity_2m'] * 0.1
        data['comfort_index'] = np.where((data['temperature_2m'] >= 20) & (data['temperature_2m'] <= 25) & 
                                        (data['relative_humidity_2m'] >= 40) & (data['relative_humidity_2m'] <= 60), 1, 0)
        data['pollution_index'] = data['pm2_5'] / 50.0
        data['aqi_lag1'] = np.roll(aqi, 1)
        data['aqi_lag2'] = np.roll(aqi, 2)
        data['aqi_rolling3'] = pd.Series(aqi).rolling(3).mean().fillna(aqi).values
        data['aqi_rolling6'] = pd.Series(aqi).rolling(6).mean().fillna(aqi).values
        
        df = pd.DataFrame(data)
        print(f"✅ Created {len(df)} synthetic training samples")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features and target for training"""
        # Define feature columns
        feature_columns = [
            'temperature_2m', 'windspeed_10m', 'winddirection_10m',
            'relative_humidity_2m', 'precipitation', 'cloudcover', 'surface_pressure',
            'co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3',
            'hour', 'day', 'month', 'day_of_week', 'is_weekend', 'season',
            'aqi_change_rate', 'heat_index', 'comfort_index', 'pollution_index',
            'aqi_lag1', 'aqi_lag2', 'aqi_rolling3', 'aqi_rolling6'
        ]
        
        # Check which features are available
        available_features = [col for col in feature_columns if col in df.columns]
        missing_features = [col for col in feature_columns if col not in df.columns]
        
        if missing_features:
            print(f"⚠️ Missing features: {missing_features}")
            print(f"✅ Using {len(available_features)} available features")
        
        # Prepare features and target
        X = df[available_features].fillna(0)
        y = df['aqi']
        
        print(f"📊 Training data shape: {X.shape}")
        print(f"📊 Target distribution: {y.value_counts().to_dict()}")
        
        return X, y, available_features
    
    def train_model(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train Random Forest model"""
        try:
            # Handle small datasets
            if len(X) < 10:
                print("⚠️ Small dataset detected, using all data for training")
                X_train, X_test, y_train, y_test = X, X, y, y
            else:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
            
            print(f"📊 Training set: {X_train.shape[0]} samples")
            print(f"📊 Test set: {X_test.shape[0]} samples")
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            print("🚀 Training Random Forest model...")
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"📊 Model Performance:")
            print(f"   - RMSE: {rmse:.3f}")
            print(f"   - MAE: {mae:.3f}")
            print(f"   - R²: {r2:.3f}")
            
            return {
                'model': model,
                'features': X.columns.tolist(),
                'metrics': {
                    'rmse': rmse,
                    'mae': mae,
                    'r2': r2
                },
                'test_size': len(X_test)
            }
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            raise
    
    def save_model(self, model_info: dict):
        """Save trained model"""
        try:
            # Save model
            model_file = self.models_path / 'aqi_model.pkl'
            joblib.dump(model_info['model'], model_file)
            
            # Save model metadata
            metadata = {
                'features': model_info['features'],
                'metrics': model_info['metrics'],
                'test_size': model_info['test_size'],
                'trained_at': datetime.now().isoformat(),
                'model_type': 'RandomForestRegressor'
            }
            
            metadata_file = self.models_path / 'model_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Model saved to {model_file}")
            print(f"✅ Metadata saved to {metadata_file}")
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            raise
    
    def run_pipeline(self):
        """Run the complete training pipeline"""
        print("🚀 Starting simplified training pipeline...")
        
        try:
            # Load training data
            df = self.load_training_data()
            
            # Prepare features
            X, y, features = self.prepare_features(df)
            
            # Train model
            model_info = self.train_model(X, y)
            
            # Save model
            self.save_model(model_info)
            
            print("✅ Training pipeline completed successfully!")
            
        except Exception as e:
            print(f"❌ Training pipeline failed: {e}")
            raise

def main():
    """Main function to run the pipeline"""
    try:
        pipeline = SimpleTrainingPipeline()
        pipeline.run_pipeline()
        print("🎉 Training pipeline completed successfully!")
    except Exception as e:
        print(f"❌ Training pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
