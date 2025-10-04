#!/usr/bin/env python3
"""
Deployment Script for AQI Predictor
Handles deployment to different environments
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_path = self.project_root / 'scripts'
        
    def run_command(self, command: str, cwd: Path = None) -> bool:
        """Run a shell command and return success status"""
        try:
            if cwd is None:
                cwd = self.project_root
            
            logger.info(f"Running: {command}")
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Command completed successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Command failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running command: {e}")
            return False
    
    def setup_environment(self):
        """Set up the development environment"""
        logger.info("🔧 Setting up development environment...")
        
        # Create necessary directories
        directories = ['logs', 'feature_store', 'models', 'outputs']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
        
        # Install dependencies
        if not self.run_command("pip install -r requirements.txt"):
            logger.error("❌ Failed to install dependencies")
            return False
        
        logger.info("✅ Environment setup completed")
        return True
    
    def run_feature_pipeline(self):
        """Run the feature pipeline"""
        logger.info("🔄 Running feature pipeline...")
        
        if not self.run_command("python scripts/feature_pipeline.py"):
            logger.error("❌ Feature pipeline failed")
            return False
        
        logger.info("✅ Feature pipeline completed")
        return True
    
    def run_training_pipeline(self):
        """Run the training pipeline"""
        logger.info("🤖 Running training pipeline...")
        
        if not self.run_command("python scripts/training_pipeline.py"):
            logger.error("❌ Training pipeline failed")
            return False
        
        logger.info("✅ Training pipeline completed")
        return True
    
    def run_model_evaluation(self):
        """Run model evaluation"""
        logger.info("📊 Running model evaluation...")
        
        if not self.run_command("python scripts/model_evaluation.py"):
            logger.error("❌ Model evaluation failed")
            return False
        
        logger.info("✅ Model evaluation completed")
        return True
    
    def build_docker_image(self, tag: str = "aqi-predictor:latest"):
        """Build Docker image"""
        logger.info(f"🐳 Building Docker image: {tag}")
        
        if not self.run_command(f"docker build -t {tag} ."):
            logger.error("❌ Docker build failed")
            return False
        
        logger.info("✅ Docker image built successfully")
        return True
    
    def run_docker_container(self, tag: str = "aqi-predictor:latest", port: int = 8501):
        """Run Docker container"""
        logger.info(f"🚀 Starting Docker container on port {port}")
        
        # Stop existing container if running
        self.run_command(f"docker stop aqi-predictor-app || true")
        self.run_command(f"docker rm aqi-predictor-app || true")
        
        # Run new container
        command = f"""
        docker run -d \
            --name aqi-predictor-app \
            -p {port}:8501 \
            -v $(pwd)/feature_store:/app/feature_store \
            -v $(pwd)/models:/app/models \
            -v $(pwd)/outputs:/app/outputs \
            -v $(pwd)/logs:/app/logs \
            -e OPENWEATHER_API_KEY=$OPENWEATHER_API_KEY \
            {tag}
        """
        
        if not self.run_command(command):
            logger.error("❌ Failed to start Docker container")
            return False
        
        logger.info("✅ Docker container started successfully")
        return True
    
    def deploy_with_docker_compose(self):
        """Deploy using docker-compose"""
        logger.info("🐳 Deploying with docker-compose...")
        
        # Stop existing services
        self.run_command("docker-compose down")
        
        # Build and start services
        if not self.run_command("docker-compose up -d --build"):
            logger.error("❌ Docker-compose deployment failed")
            return False
        
        logger.info("✅ Docker-compose deployment completed")
        return True
    
    def run_tests(self):
        """Run tests"""
        logger.info("🧪 Running tests...")
        
        # Create a simple test
        test_script = """
import sys
import os
sys.path.append('.')

def test_imports():
    try:
        import pandas as pd
        import numpy as np
        import streamlit as st
        from sklearn.ensemble import RandomForestRegressor
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_loading():
    try:
        import joblib
        if os.path.exists('models/aqi_model.pkl'):
            model = joblib.load('models/aqi_model.pkl')
            print("✅ Model loaded successfully")
            return True
        else:
            print("⚠️ No model found")
            return True
    except Exception as e:
        print(f"❌ Model loading error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports() and test_model_loading()
    sys.exit(0 if success else 1)
        """
        
        with open('test_deployment.py', 'w') as f:
            f.write(test_script)
        
        success = self.run_command("python test_deployment.py")
        os.remove('test_deployment.py')
        
        if success:
            logger.info("✅ Tests passed")
        else:
            logger.error("❌ Tests failed")
        
        return success
    
    def check_health(self, port: int = 8501):
        """Check application health"""
        logger.info(f"🏥 Checking application health on port {port}")
        
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/_stcore/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Application is healthy")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def deploy_full_pipeline(self):
        """Deploy the complete pipeline"""
        logger.info("🚀 Starting full deployment pipeline...")
        
        steps = [
            ("Setup Environment", self.setup_environment),
            ("Run Feature Pipeline", self.run_feature_pipeline),
            ("Run Training Pipeline", self.run_training_pipeline),
            ("Run Model Evaluation", self.run_model_evaluation),
            ("Build Docker Image", self.build_docker_image),
            ("Run Tests", self.run_tests),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ Deployment failed at: {step_name}")
                return False
            logger.info(f"✅ {step_name} completed")
        
        logger.info("🎉 Full deployment pipeline completed successfully!")
        return True
    
    def deploy_production(self):
        """Deploy to production"""
        logger.info("🏭 Deploying to production...")
        
        # Use docker-compose for production
        if not self.deploy_with_docker_compose():
            logger.error("❌ Production deployment failed")
            return False
        
        # Wait for services to start
        import time
        logger.info("⏳ Waiting for services to start...")
        time.sleep(30)
        
        # Check health
        if not self.check_health():
            logger.error("❌ Production deployment health check failed")
            return False
        
        logger.info("✅ Production deployment completed successfully!")
        return True

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy AQI Predictor')
    parser.add_argument('--mode', choices=['dev', 'prod', 'full'], default='dev',
                       help='Deployment mode')
    parser.add_argument('--port', type=int, default=8501,
                       help='Port to run the application on')
    
    args = parser.parse_args()
    
    deployer = DeploymentManager()
    
    if args.mode == 'dev':
        success = deployer.deploy_full_pipeline()
    elif args.mode == 'prod':
        success = deployer.deploy_production()
    elif args.mode == 'full':
        success = deployer.deploy_full_pipeline()
        if success:
            success = deployer.deploy_production()
    
    if success:
        logger.info("🎉 Deployment completed successfully!")
        logger.info(f"🌐 Application should be available at: http://localhost:{args.port}")
    else:
        logger.error("❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
