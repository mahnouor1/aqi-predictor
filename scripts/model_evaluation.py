#!/usr/bin/env python3
"""
Model Evaluation and Registry Script
Evaluates trained models and manages model registry
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
import shap
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self):
        self.models_path = Path('models')
        self.feature_store_path = Path('feature_store')
        self.outputs_path = Path('outputs')
        self.outputs_path.mkdir(exist_ok=True)
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
    
    def load_latest_model(self):
        """Load the latest trained model"""
        try:
            model_file = self.models_path / 'aqi_model.pkl'
            if not model_file.exists():
                logger.error("❌ No trained model found")
                return None, None
            
            model = joblib.load(model_file)
            
            # Try to load metadata
            metadata_files = list(self.models_path.glob('*_metadata.json'))
            if metadata_files:
                latest_metadata = max(metadata_files, key=lambda x: x.stat().st_mtime)
                with open(latest_metadata, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = None
            
            logger.info("✅ Model loaded successfully")
            return model, metadata
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            return None, None
    
    def load_test_data(self):
        """Load test data for evaluation"""
        try:
            historical_file = self.feature_store_path / 'historical_features.csv'
            if not historical_file.exists():
                logger.error("❌ No historical data found")
                return pd.DataFrame()
            
            df = pd.read_csv(historical_file)
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            # Use last 20% of data as test set
            test_size = int(len(df) * 0.2)
            test_df = df.tail(test_size)
            
            logger.info(f"✅ Loaded {len(test_df)} test samples")
            return test_df
            
        except Exception as e:
            logger.error(f"❌ Error loading test data: {e}")
            return pd.DataFrame()
    
    def prepare_test_features(self, df: pd.DataFrame, feature_names: list):
        """Prepare test features"""
        try:
            # Select available features
            available_features = [col for col in feature_names if col in df.columns]
            X_test = df[available_features].copy()
            y_test = df['aqi'].copy()
            
            # Handle missing values
            X_test = X_test.fillna(X_test.median())
            
            # Remove any remaining NaN values
            mask = ~(X_test.isna().any(axis=1) | y_test.isna())
            X_test = X_test[mask]
            y_test = y_test[mask]
            
            logger.info(f"✅ Prepared {len(X_test)} test samples with {len(available_features)} features")
            return X_test, y_test
            
        except Exception as e:
            logger.error(f"❌ Error preparing test features: {e}")
            return pd.DataFrame(), pd.Series()
    
    def evaluate_model_performance(self, model, X_test, y_test):
        """Evaluate model performance on test data"""
        try:
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Calculate additional metrics
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            
            # AQI accuracy (within 1 level)
            aqi_accuracy = np.mean(np.abs(y_test - y_pred) <= 1) * 100
            
            metrics = {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(r2),
                'mape': float(mape),
                'aqi_accuracy': float(aqi_accuracy)
            }
            
            logger.info("📊 Model Performance Metrics:")
            logger.info(f"   RMSE: {rmse:.4f}")
            logger.info(f"   MAE: {mae:.4f}")
            logger.info(f"   R²: {r2:.4f}")
            logger.info(f"   MAPE: {mape:.2f}%")
            logger.info(f"   AQI Accuracy (±1): {aqi_accuracy:.2f}%")
            
            return metrics, y_pred
            
        except Exception as e:
            logger.error(f"❌ Error evaluating model: {e}")
            return {}, np.array([])
    
    def generate_shap_explanations(self, model, X_test, feature_names):
        """Generate SHAP explanations for model interpretability"""
        try:
            logger.info("🔍 Generating SHAP explanations...")
            
            # Create SHAP explainer
            if hasattr(model, 'predict_proba'):
                # For models with probability prediction
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_test)
            else:
                # For regression models
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_test)
            
            # Summary plot
            plt.figure(figsize=(10, 8))
            shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
            plt.title('SHAP Feature Importance Summary')
            plt.tight_layout()
            plt.savefig(self.outputs_path / 'shap_summary.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Feature importance bar plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X_test, feature_names=feature_names, plot_type="bar", show=False)
            plt.title('SHAP Feature Importance (Bar Plot)')
            plt.tight_layout()
            plt.savefig(self.outputs_path / 'shap_importance.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Calculate mean absolute SHAP values for feature importance
            mean_shap_values = np.abs(shap_values).mean(axis=0)
            feature_importance = dict(zip(feature_names, mean_shap_values))
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            
            logger.info("✅ SHAP explanations generated")
            return feature_importance
            
        except Exception as e:
            logger.error(f"❌ Error generating SHAP explanations: {e}")
            return {}
    
    def create_performance_visualizations(self, y_test, y_pred, metrics):
        """Create performance visualization plots"""
        try:
            # Prediction vs Actual scatter plot
            plt.figure(figsize=(10, 8))
            plt.scatter(y_test, y_pred, alpha=0.6)
            plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
            plt.xlabel('Actual AQI')
            plt.ylabel('Predicted AQI')
            plt.title(f'Prediction vs Actual (R² = {metrics["r2"]:.3f})')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.outputs_path / 'prediction_vs_actual.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Residuals plot
            residuals = y_test - y_pred
            plt.figure(figsize=(10, 6))
            plt.scatter(y_pred, residuals, alpha=0.6)
            plt.axhline(y=0, color='r', linestyle='--')
            plt.xlabel('Predicted AQI')
            plt.ylabel('Residuals')
            plt.title('Residuals Plot')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.outputs_path / 'residuals_plot.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Error distribution
            plt.figure(figsize=(10, 6))
            plt.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
            plt.xlabel('Prediction Error')
            plt.ylabel('Frequency')
            plt.title('Distribution of Prediction Errors')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.outputs_path / 'error_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("✅ Performance visualizations created")
            
        except Exception as e:
            logger.error(f"❌ Error creating visualizations: {e}")
    
    def generate_model_report(self, metrics, feature_importance, model_metadata):
        """Generate comprehensive model evaluation report"""
        try:
            report = {
                'evaluation_date': datetime.now().isoformat(),
                'model_metadata': model_metadata,
                'performance_metrics': metrics,
                'feature_importance': feature_importance,
                'model_quality': self.assess_model_quality(metrics)
            }
            
            # Save report
            report_file = self.outputs_path / 'model_evaluation_report.json'
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"✅ Model evaluation report saved: {report_file}")
            
            # Print summary
            logger.info("📋 Model Evaluation Summary:")
            logger.info(f"   Model Quality: {report['model_quality']}")
            logger.info(f"   R² Score: {metrics.get('r2', 'N/A'):.3f}")
            logger.info(f"   RMSE: {metrics.get('rmse', 'N/A'):.3f}")
            logger.info(f"   AQI Accuracy: {metrics.get('aqi_accuracy', 'N/A'):.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
    
    def assess_model_quality(self, metrics):
        """Assess overall model quality based on metrics"""
        r2 = metrics.get('r2', 0)
        rmse = metrics.get('rmse', float('inf'))
        aqi_accuracy = metrics.get('aqi_accuracy', 0)
        
        if r2 >= 0.8 and rmse <= 0.5 and aqi_accuracy >= 80:
            return "Excellent"
        elif r2 >= 0.6 and rmse <= 1.0 and aqi_accuracy >= 60:
            return "Good"
        elif r2 >= 0.4 and rmse <= 1.5 and aqi_accuracy >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def run_evaluation(self):
        """Run complete model evaluation"""
        logger.info("🚀 Starting model evaluation...")
        
        try:
            # Load model and metadata
            model, metadata = self.load_latest_model()
            if model is None:
                logger.error("❌ No model available for evaluation")
                return
            
            # Load test data
            test_df = self.load_test_data()
            if test_df.empty:
                logger.error("❌ No test data available")
                return
            
            # Prepare features
            feature_names = metadata.get('feature_names', []) if metadata else []
            X_test, y_test = self.prepare_test_features(test_df, feature_names)
            if X_test.empty:
                logger.error("❌ No test features available")
                return
            
            # Evaluate performance
            metrics, y_pred = self.evaluate_model_performance(model, X_test, y_test)
            if not metrics:
                logger.error("❌ Model evaluation failed")
                return
            
            # Generate SHAP explanations
            feature_importance = self.generate_shap_explanations(model, X_test, feature_names)
            
            # Create visualizations
            self.create_performance_visualizations(y_test, y_pred, metrics)
            
            # Generate report
            self.generate_model_report(metrics, feature_importance, metadata)
            
            logger.info("✅ Model evaluation completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            raise

def main():
    """Main function to run model evaluation"""
    evaluator = ModelEvaluator()
    evaluator.run_evaluation()

if __name__ == "__main__":
    main()
