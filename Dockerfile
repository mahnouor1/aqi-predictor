# Multi-stage Dockerfile for AQI Predictor
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional ML dependencies
RUN pip install --no-cache-dir \
    xgboost \
    lightgbm \
    shap \
    mlflow \
    hopsworks-client

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    black \
    flake8 \
    jupyter

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p logs feature_store models outputs

# Expose port for Streamlit
EXPOSE 8501

# Default command for development
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy source code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p logs feature_store models outputs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port for Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Production command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
