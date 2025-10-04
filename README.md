# 🌫️ AQI Predictor - Complete CI/CD Pipeline

A comprehensive Air Quality Index (AQI) prediction system with automated CI/CD pipeline, featuring real-time data fetching, machine learning model training, and interactive dashboard.

## 🚀 Features

- **Real-time Data Pipeline**: Automated fetching of weather and pollutant data
- **Multi-Model Training**: Support for Random Forest, XGBoost, LightGBM, and more
- **CI/CD Pipeline**: Automated training and deployment with GitHub Actions
- **Docker Containerization**: Production-ready containerized deployment
- **Model Registry**: Version control and tracking of ML models
- **SHAP Explanations**: Model interpretability and feature importance
- **Interactive Dashboard**: Streamlit-based web interface
- **Monitoring & Alerts**: Health checks and performance monitoring

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Git
- API Keys (OpenWeather, optional: Hopsworks, MLflow)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mahnouor1/aqi-predictor.git
cd aqi-predictor
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file:
```bash
# API Keys
OPENWEATHER_API_KEY=your_openweather_api_key
HOPSWORKS_API_KEY=your_hopsworks_api_key  # Optional
MLFLOW_TRACKING_URI=http://localhost:5000  # Optional

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/aqi_predictor
```

## 🚀 Quick Start

### Option 1: Automated Deployment
```bash
# Full pipeline deployment
python scripts/deploy.py --mode full

# Development deployment
python scripts/deploy.py --mode dev

# Production deployment
python scripts/deploy.py --mode prod
```

### Option 2: Manual Setup
```bash
# 1. Run feature pipeline
python scripts/feature_pipeline.py

# 2. Train models
python scripts/training_pipeline.py

# 3. Evaluate models
python scripts/model_evaluation.py

# 4. Start the app
streamlit run app.py
```

### Option 3: Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d --build

# Or build manually
docker build -t aqi-predictor .
docker run -p 8501:8501 aqi-predictor
```

## 📊 CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow that:

### Feature Pipeline (Every Hour)
- Fetches weather and pollutant data
- Computes derived features and trends
- Stores data in feature store

### Training Pipeline (Daily)
- Trains multiple ML models
- Performs hyperparameter tuning
- Evaluates model performance
- Saves best model to registry

### Model Evaluation
- Generates SHAP explanations
- Creates performance visualizations
- Assesses model quality
- Updates model registry

### Deployment
- Builds Docker images
- Runs health checks
- Deploys to staging/production

## 🏗️ Project Structure

```
aqi-predictor/
├── .github/workflows/          # CI/CD pipelines
│   └── ci-cd-pipeline.yml
├── scripts/                    # Pipeline scripts
│   ├── feature_pipeline.py     # Data fetching & feature engineering
│   ├── training_pipeline.py    # Model training
│   ├── model_evaluation.py     # Model evaluation & SHAP
│   └── deploy.py              # Deployment automation
├── feature_store/             # Feature storage
├── models/                    # Trained models
├── outputs/                   # Evaluation results
├── logs/                      # Application logs
├── app.py                     # Streamlit dashboard
├── train.py                   # Legacy training script
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Multi-service deployment
└── README.md                  # This file
```

## 🔧 Configuration

### GitHub Actions Secrets
Add these secrets to your GitHub repository:

```
OPENWEATHER_API_KEY=your_api_key
HOPSWORKS_API_KEY=your_hopsworks_key
MLFLOW_TRACKING_URI=your_mlflow_uri
```

### Model Configuration
Edit `scripts/training_pipeline.py` to:
- Add new models
- Modify hyperparameter grids
- Adjust evaluation metrics

### Feature Engineering
Edit `scripts/feature_pipeline.py` to:
- Add new data sources
- Create additional features
- Modify trend calculations

## 📈 Monitoring & Observability

### Health Checks
- Application health: `http://localhost:8501/_stcore/health`
- Docker health: `docker ps` (check container status)

### Logs
- Application logs: `logs/`
- Pipeline logs: `logs/feature_pipeline.log`, `logs/training_pipeline.log`

### Metrics
- Model performance: `outputs/model_evaluation_report.json`
- Feature importance: `outputs/shap_*.png`
- Performance plots: `outputs/prediction_vs_actual.png`

## 🚨 Alerts & Notifications

The system includes automated alerts for:
- Pipeline failures
- Model performance degradation
- Data quality issues
- System health problems

## 🔄 Data Flow

```mermaid
graph TD
    A[External APIs] --> B[Feature Pipeline]
    B --> C[Feature Store]
    C --> D[Training Pipeline]
    D --> E[Model Registry]
    E --> F[Model Evaluation]
    F --> G[Dashboard]
    G --> H[User Interface]
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
python -m pytest tests/

# Integration tests
python scripts/deploy.py --mode dev
```

### Test Individual Components
```bash
# Test feature pipeline
python scripts/feature_pipeline.py

# Test training pipeline
python scripts/training_pipeline.py

# Test model evaluation
python scripts/model_evaluation.py
```

## 🐳 Docker Commands

```bash
# Build image
docker build -t aqi-predictor .

# Run container
docker run -p 8501:8501 aqi-predictor

# Run with environment variables
docker run -p 8501:8501 -e OPENWEATHER_API_KEY=your_key aqi-predictor

# View logs
docker logs aqi-predictor-app

# Stop container
docker stop aqi-predictor-app
```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Issues**
   ```bash
   # Check environment variables
   echo $OPENWEATHER_API_KEY
   ```

2. **Model Loading Issues**
   ```bash
   # Check if model exists
   ls -la models/
   ```

3. **Docker Issues**
   ```bash
   # Check Docker status
   docker ps
   docker logs aqi-predictor-app
   ```

4. **Port Conflicts**
   ```bash
   # Check port usage
   lsof -i :8501
   ```

### Debug Mode
```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python scripts/feature_pipeline.py
```

## 📚 API Documentation

### Feature Pipeline API
- **Input**: External weather/pollutant APIs
- **Output**: Processed features in CSV format
- **Schedule**: Every hour

### Training Pipeline API
- **Input**: Historical features from feature store
- **Output**: Trained models and performance metrics
- **Schedule**: Daily

### Model Evaluation API
- **Input**: Trained models and test data
- **Output**: SHAP explanations and performance reports
- **Schedule**: After training

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python scripts/deploy.py --mode dev`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenWeather API for weather data
- Open-Meteo API for additional weather data
- Streamlit for the web interface
- Scikit-learn, XGBoost, and LightGBM for ML models
- SHAP for model interpretability

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the logs in `logs/` directory
- Review the troubleshooting section above

---

**🌍 Help us predict air quality for a healthier planet!**