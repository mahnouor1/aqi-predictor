#!/usr/bin/env python3
"""
Comprehensive Training Pipeline for AQI Predictor
Trains multiple ML models and evaluates performance
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from pathlib import Path
import joblib
import json

# ML Libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self):
        self.feature_store_path = Path('feature_store')
        self.models_path = Path('models')
        self.models_path.mkdir(exist_ok=True)
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        # Model configurations
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1),
            'elastic_net': ElasticNet(alpha=0.1, l1_ratio=0.5),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale'),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'lightgbm': lgb.LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
        }
        
        # Hyperparameter grids for tuning
        self.param_grids = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 10],
                'learning_rate': [0.01, 0.1, 0.2]
            },
            'lightgbm': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 10],
                'learning_rate': [0.01, 0.1, 0.2]
            }
        }
    
    def load_data(self) -> pd.DataFrame:
        """Load and prepare training data"""
        try:
            historical_file = self.feature_store_path / 'historical_features.csv'
            
            if not historical_file.exists():
                logger.error("❌ No historical data found. Run feature pipeline first.")
                return pd.DataFrame()
            
            df = pd.read_csv(historical_file)
            logger.info(f"✅ Loaded {len(df)} records from feature store")
            
            # Convert datetime column
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime')
            
            # Remove rows with missing target
            df = df.dropna(subset=['aqi'])
            
            logger.info(f"✅ Cleaned data: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            return pd.DataFrame()
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features and target for training"""
        try:
            # Define feature columns (exclude metadata)
            feature_cols = [
                'temperature_2m', 'relative_humidity_2m', 'windspeed_10m', 'winddirection_10m',
                'precipitation', 'cloudcover', 'surface_pressure',
                'co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3',
                'hour', 'day', 'month', 'day_of_week', 'is_weekend', 'season',
                'temp_humidity_ratio', 'wind_pressure_ratio', 'pollution_index', 'gas_pollution_index',
                'aqi_change_rate', 'temp_change_rate', 'pm25_change_rate', 'avg_aqi_7d', 'avg_temp_7d'
            ]
            
            # Check which features exist in the data
            available_features = [col for col in feature_cols if col in df.columns]
            missing_features = [col for col in feature_cols if col not in df.columns]
            
            if missing_features:
                logger.warning(f"⚠️ Missing features: {missing_features}")
            
            # Prepare X and y
            X = df[available_features].copy()
            y = df['aqi'].copy()
            
            # Handle missing values
            X = X.fillna(X.median())
            
            # Remove any remaining NaN values
            mask = ~(X.isna().any(axis=1) | y.isna())
            X = X[mask]
            y = y[mask]
            
            logger.info(f"✅ Prepared features: {X.shape[1]} features, {len(X)} samples")
            logger.info(f"📊 Target distribution: {y.value_counts().to_dict()}")
            
            return X, y, available_features
            
        except Exception as e:
            logger.error(f"❌ Error preparing features: {e}")
            return pd.DataFrame(), pd.Series(), []
    
    def train_model(self, model_name: str, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train a single model with hyperparameter tuning"""
        try:
            logger.info(f"🔄 Training {model_name}...")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=None
            )
            
            # Get model and parameters
            model = self.models[model_name]
            param_grid = self.param_grids.get(model_name, {})
            
            # Hyperparameter tuning if parameters available
            if param_grid:
                logger.info(f"🔍 Tuning hyperparameters for {model_name}...")
                grid_search = GridSearchCV(
                    model, param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                best_model = grid_search.best_estimator_
                logger.info(f"✅ Best parameters: {grid_search.best_params_}")
            else:
                best_model = model
                best_model.fit(X_train, y_train)
            
            # Make predictions
            y_train_pred = best_model.predict(X_train)
            y_test_pred = best_model.predict(X_test)
            
            # Calculate metrics
            train_metrics = self.calculate_metrics(y_train, y_train_pred, "train")
            test_metrics = self.calculate_metrics(y_test, y_test_pred, "test")
            
            # Cross-validation score
            cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
            cv_rmse = np.sqrt(-cv_scores.mean())
            
            results = {
                'model': best_model,
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'cv_rmse': cv_rmse,
                'feature_importance': self.get_feature_importance(best_model, X.columns)
            }
            
            logger.info(f"✅ {model_name} trained successfully")
            logger.info(f"   Test RMSE: {test_metrics['rmse']:.4f}")
            logger.info(f"   Test R²: {test_metrics['r2']:.4f}")
            logger.info(f"   CV RMSE: {cv_rmse:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error training {model_name}: {e}")
            return None
    
    def calculate_metrics(self, y_true, y_pred, dataset_name: str) -> dict:
        """Calculate evaluation metrics"""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'dataset': dataset_name
        }
    
    def get_feature_importance(self, model, feature_names) -> dict:
        """Get feature importance from model"""
        try:
            if hasattr(model, 'feature_importances_'):
                importance_dict = dict(zip(feature_names, model.feature_importances_))
                return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            elif hasattr(model, 'coef_'):
                importance_dict = dict(zip(feature_names, np.abs(model.coef_)))
                return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            else:
                return {}
        except:
            return {}
    
    def train_all_models(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train all models and compare performance"""
        logger.info("🚀 Starting model training...")
        
        results = {}
        
        for model_name in self.models.keys():
            try:
                result = self.train_model(model_name, X, y)
                if result:
                    results[model_name] = result
            except Exception as e:
                logger.error(f"❌ Failed to train {model_name}: {e}")
                continue
        
        return results
    
    def select_best_model(self, results: dict) -> tuple:
        """Select the best model based on test RMSE"""
        if not results:
            logger.error("❌ No models trained successfully")
            return None, None
        
        best_model_name = min(results.keys(), key=lambda x: results[x]['test_metrics']['rmse'])
        best_model = results[best_model_name]['model']
        
        logger.info(f"🏆 Best model: {best_model_name}")
        logger.info(f"   Test RMSE: {results[best_model_name]['test_metrics']['rmse']:.4f}")
        logger.info(f"   Test R²: {results[best_model_name]['test_metrics']['r2']:.4f}")
        
        return best_model_name, best_model
    
    def save_model(self, model, model_name: str, results: dict, feature_names: list):
        """Save the trained model and metadata"""
        try:
            # Save model
            model_file = self.models_path / f'{model_name}_model.pkl'
            joblib.dump(model, model_file)
            
            # Save metadata
            metadata = {
                'model_name': model_name,
                'training_date': datetime.now().isoformat(),
                'feature_names': feature_names,
                'performance': results[model_name]['test_metrics'],
                'feature_importance': results[model_name]['feature_importance']
            }
            
            metadata_file = self.models_path / f'{model_name}_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Save as the main model for the app
            main_model_file = self.models_path / 'aqi_model.pkl'
            joblib.dump(model, main_model_file)
            
            logger.info(f"✅ Model saved: {model_file}")
            logger.info(f"✅ Metadata saved: {metadata_file}")
            logger.info(f"✅ Main model updated: {main_model_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving model: {e}")
    
    def generate_model_report(self, results: dict, best_model_name: str):
        """Generate a comprehensive model report"""
        try:
            report = {
                'training_date': datetime.now().isoformat(),
                'total_models': len(results),
                'best_model': best_model_name,
                'model_comparison': {}
            }
            
            for model_name, result in results.items():
                report['model_comparison'][model_name] = {
                    'test_rmse': result['test_metrics']['rmse'],
                    'test_r2': result['test_metrics']['r2'],
                    'test_mae': result['test_metrics']['mae'],
                    'cv_rmse': result['cv_rmse']
                }
            
            # Save report
            report_file = self.models_path / 'training_report.json'
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Model report saved: {report_file}")
            
            # Print summary
            logger.info("📊 Model Performance Summary:")
            for model_name, result in results.items():
                metrics = result['test_metrics']
                logger.info(f"   {model_name}: RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
    
    def run_pipeline(self):
        """Run the complete training pipeline"""
        logger.info("🚀 Starting training pipeline...")
        
        try:
            # Load data
            df = self.load_data()
            if df.empty:
                logger.error("❌ No data available for training")
                return
            
            # Prepare features
            X, y, feature_names = self.prepare_features(df)
            if X.empty:
                logger.error("❌ No features available for training")
                return
            
            # Train all models
            results = self.train_all_models(X, y)
            if not results:
                logger.error("❌ No models trained successfully")
                return
            
            # Select best model
            best_model_name, best_model = self.select_best_model(results)
            if best_model is None:
                logger.error("❌ No best model selected")
                return
            
            # Save model and metadata
            self.save_model(best_model, best_model_name, results, feature_names)
            
            # Generate report
            self.generate_model_report(results, best_model_name)
            
            logger.info("✅ Training pipeline completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            raise

def main():
    """Main function to run the training pipeline"""
    pipeline = TrainingPipeline()
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()
