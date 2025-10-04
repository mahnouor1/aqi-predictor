# 🧪 AQI Predictor Testing Guide

## 🚀 Quick Start Testing

### **Step 1: Environment Setup**
```bash
# Navigate to project directory
cd /Users/Maha/Downloads/aqi-pp/aqi-predictor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run initial setup
python3 setup.py
```

### **Step 2: Test Individual Components**

#### **A. Test Feature Pipeline**
```bash
# Test data fetching and feature engineering
python3 scripts/feature_pipeline.py

# Check if features were created
ls -la feature_store/
cat feature_store/historical_features.csv | head -5
```

#### **B. Test Training Pipeline**
```bash
# Test model training
python3 scripts/training_pipeline.py

# Check if models were created
ls -la models/
```

#### **C. Test Model Evaluation**
```bash
# Test model evaluation and SHAP
python3 scripts/model_evaluation.py

# Check evaluation outputs
ls -la outputs/
```

#### **D. Test Web Application**
```bash
# Start the Streamlit app
streamlit run app.py

# Open browser to: http://localhost:8501
# Test the prediction interface
```

### **Step 3: Test Docker Deployment**

#### **A. Build Docker Image**
```bash
# Build the Docker image
docker build -t aqi-predictor .

# Check if image was created
docker images | grep aqi-predictor
```

#### **B. Test Docker Container**
```bash
# Run container
docker run -d --name aqi-test -p 8501:8501 aqi-predictor

# Check container status
docker ps

# Check logs
docker logs aqi-test

# Test health endpoint
curl http://localhost:8501/_stcore/health
```

#### **C. Test Docker Compose**
```bash
# Start all services
docker-compose up -d

# Check all services
docker-compose ps

# View logs
docker-compose logs
```

### **Step 4: Test CI/CD Pipeline**

#### **A. Test GitHub Actions Locally**
```bash
# Install act (GitHub Actions runner)
brew install act  # On macOS
# OR
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test the workflow
act -j feature-pipeline
act -j training-pipeline
```

#### **B. Test with GitHub (Recommended)**
```bash
# Push to GitHub to trigger CI/CD
git add .
git commit -m "Initial CI/CD pipeline setup"
git push origin main

# Check GitHub Actions tab in your repository
```

## 🔍 **What to Test**

### **1. Data Pipeline Testing**
- ✅ API connectivity (OpenWeather, Open-Meteo)
- ✅ Feature engineering (time features, derived features)
- ✅ Data storage (CSV files)
- ✅ Error handling (API failures, missing data)

### **2. Model Training Testing**
- ✅ Multiple model training (8 algorithms)
- ✅ Hyperparameter tuning
- ✅ Cross-validation
- ✅ Model performance metrics
- ✅ Model saving and loading

### **3. Model Evaluation Testing**
- ✅ SHAP explanations generation
- ✅ Performance visualizations
- ✅ Model quality assessment
- ✅ Feature importance analysis

### **4. Web Application Testing**
- ✅ Streamlit interface loading
- ✅ Input validation
- ✅ Prediction functionality
- ✅ Real-time updates

### **5. Docker Testing**
- ✅ Image building
- ✅ Container startup
- ✅ Port mapping
- ✅ Volume mounting
- ✅ Health checks

### **6. CI/CD Testing**
- ✅ GitHub Actions workflow
- ✅ Automated pipeline execution
- ✅ Artifact generation
- ✅ Deployment automation

## 🐛 **Common Issues & Solutions**

### **Issue 1: API Key Missing**
```bash
# Solution: Set environment variable
export OPENWEATHER_API_KEY=your_api_key_here
# OR add to .env file
echo "OPENWEATHER_API_KEY=your_api_key_here" >> .env
```

### **Issue 2: Python Dependencies**
```bash
# Solution: Install missing packages
pip install -r requirements.txt
# OR for specific packages
pip install streamlit pandas scikit-learn
```

### **Issue 3: Docker Issues**
```bash
# Solution: Check Docker status
docker --version
docker ps

# If Docker not running, start Docker Desktop
```

### **Issue 4: Port Conflicts**
```bash
# Solution: Use different port
streamlit run app.py --server.port 8502
# OR stop existing process
lsof -ti:8501 | xargs kill -9
```

## 📊 **Expected Test Results**

### **Feature Pipeline Success:**
- ✅ `feature_store/historical_features.csv` created
- ✅ Log message: "✅ Feature pipeline completed successfully!"
- ✅ Data contains: weather, pollutant, and derived features

### **Training Pipeline Success:**
- ✅ `models/aqi_model.pkl` created
- ✅ Log message: "✅ Training pipeline completed successfully!"
- ✅ Multiple model files in `models/` directory

### **Model Evaluation Success:**
- ✅ `outputs/` directory with visualizations
- ✅ SHAP plots generated
- ✅ Performance metrics calculated

### **Web App Success:**
- ✅ Streamlit interface loads at `http://localhost:8501`
- ✅ Prediction form works
- ✅ AQI predictions generated

### **Docker Success:**
- ✅ Container runs without errors
- ✅ Health check passes
- ✅ Application accessible via browser

## 🚀 **Next Steps After Testing**

### **1. Production Deployment**
```bash
# Deploy to production
python3 scripts/deploy.py --mode prod

# OR use Docker Compose
docker-compose up -d --build
```

### **2. GitHub Integration**
```bash
# Push to GitHub
git add .
git commit -m "Complete CI/CD pipeline implementation"
git push origin main

# Set up GitHub Secrets:
# - OPENWEATHER_API_KEY
# - HOPSWORKS_API_KEY (optional)
# - MLFLOW_TRACKING_URI (optional)
```

### **3. Monitoring Setup**
- Monitor GitHub Actions for pipeline status
- Check application logs: `logs/`
- Monitor model performance: `outputs/`
- Set up alerts for failures

### **4. Customization**
- Modify feature engineering in `scripts/feature_pipeline.py`
- Add new models in `scripts/training_pipeline.py`
- Customize dashboard in `app.py`
- Adjust CI/CD schedule in `.github/workflows/ci-cd-pipeline.yml`

## 📈 **Performance Benchmarks**

### **Expected Performance:**
- **Feature Pipeline**: < 30 seconds
- **Training Pipeline**: 2-5 minutes
- **Model Evaluation**: 1-2 minutes
- **Docker Build**: 2-3 minutes
- **Application Startup**: < 10 seconds

### **Resource Usage:**
- **Memory**: 1-2 GB RAM
- **CPU**: 2-4 cores
- **Storage**: 500 MB - 1 GB
- **Network**: API calls every hour

## 🎯 **Success Criteria**

✅ All components run without errors
✅ Data pipeline fetches and processes data
✅ Models train and evaluate successfully
✅ Web application is accessible
✅ Docker containers run properly
✅ CI/CD pipeline executes automatically
✅ Monitoring and logging work
✅ Documentation is complete

---

**🎉 Once all tests pass, your AQI Predictor is ready for production!**
