#!/usr/bin/env python3
"""
AQI Predictor Setup Script
Initializes the project with all necessary components
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command: str, cwd: Path = None) -> bool:
    """Run a shell command and return success status"""
    try:
        if cwd is None:
            cwd = Path.cwd()
        
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
            return True
        else:
            logger.error(f"❌ Command failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running command: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    logger.info("📁 Creating project directories...")
    
    directories = [
        'logs',
        'feature_store', 
        'models',
        'outputs',
        'scripts',
        '.github/workflows'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created: {directory}")

def setup_environment():
    """Set up Python environment"""
    logger.info("🐍 Setting up Python environment...")
    
    # Check if virtual environment exists
    if not Path('venv').exists():
        logger.info("Creating virtual environment...")
        if not run_command("python -m venv venv"):
            logger.error("❌ Failed to create virtual environment")
            return False
    
    # Install dependencies
    logger.info("Installing dependencies...")
    if not run_command("pip install -r requirements.txt"):
        logger.error("❌ Failed to install dependencies")
        return False
    
    logger.info("✅ Environment setup completed")
    return True

def setup_git_hooks():
    """Set up Git hooks for pre-commit checks"""
    logger.info("🔧 Setting up Git hooks...")
    
    pre_commit_hook = """#!/bin/sh
# Pre-commit hook for AQI Predictor

echo "Running pre-commit checks..."

# Run linting
python -m flake8 scripts/ --max-line-length=100
if [ $? -ne 0 ]; then
    echo "❌ Linting failed"
    exit 1
fi

# Run tests
python -m pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✅ Pre-commit checks passed"
"""
    
    hooks_dir = Path('.git/hooks')
    if hooks_dir.exists():
        with open(hooks_dir / 'pre-commit', 'w') as f:
            f.write(pre_commit_hook)
        os.chmod(hooks_dir / 'pre-commit', 0o755)
        logger.info("✅ Git hooks configured")
    else:
        logger.warning("⚠️ Git repository not found, skipping Git hooks")

def create_sample_data():
    """Create sample data for testing"""
    logger.info("📊 Creating sample data...")
    
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create sample features
    dates = [datetime.now() - timedelta(hours=i) for i in range(168)]  # 7 days
    n_samples = len(dates)
    
    sample_data = {
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
        'day_of_week': [d.weekday() for d in dates],
        'is_weekend': [1 if d.weekday() >= 5 else 0 for d in dates],
        'season': [(d.month % 12 + 3) // 3 for d in dates],
        'aqi': np.random.randint(1, 6, n_samples)
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('feature_store/historical_features.csv', index=False)
    logger.info("✅ Sample data created")

def setup_environment_file():
    """Set up environment configuration"""
    logger.info("⚙️ Setting up environment configuration...")
    
    if not Path('.env').exists():
        if Path('env.example').exists():
            shutil.copy('env.example', '.env')
            logger.info("✅ Environment file created from example")
        else:
            # Create basic .env file
            env_content = """# AQI Predictor Environment Configuration
OPENWEATHER_API_KEY=your_api_key_here
LOG_LEVEL=INFO
DEBUG=False
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            logger.info("✅ Basic environment file created")
    else:
        logger.info("✅ Environment file already exists")

def run_initial_training():
    """Run initial model training with sample data"""
    logger.info("🤖 Running initial model training...")
    
    # Create sample data first
    create_sample_data()
    
    # Run training pipeline
    if run_command("python scripts/training_pipeline.py"):
        logger.info("✅ Initial training completed")
        return True
    else:
        logger.warning("⚠️ Initial training failed, but setup can continue")
        return False

def print_next_steps():
    """Print next steps for the user"""
    logger.info("\n🎉 Setup completed successfully!")
    logger.info("\n📋 Next Steps:")
    logger.info("1. Update your API keys in the .env file")
    logger.info("2. Run the application: streamlit run app.py")
    logger.info("3. Or use Docker: docker-compose up -d")
    logger.info("4. Access the dashboard at: http://localhost:8501")
    logger.info("\n🔧 Configuration:")
    logger.info("- Edit .env file for API keys and settings")
    logger.info("- Modify scripts/ for pipeline customization")
    logger.info("- Check logs/ directory for application logs")
    logger.info("\n📚 Documentation:")
    logger.info("- README.md for detailed instructions")
    logger.info("- GitHub Actions for CI/CD pipeline")
    logger.info("- Docker Compose for multi-service deployment")

def main():
    """Main setup function"""
    logger.info("🚀 Starting AQI Predictor setup...")
    
    try:
        # Create directories
        create_directories()
        
        # Set up environment
        if not setup_environment():
            logger.error("❌ Environment setup failed")
            return False
        
        # Set up Git hooks
        setup_git_hooks()
        
        # Set up environment file
        setup_environment_file()
        
        # Create sample data
        create_sample_data()
        
        # Run initial training
        run_initial_training()
        
        # Print next steps
        print_next_steps()
        
        logger.info("✅ Setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
