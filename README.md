# 🌫️ AQI Predictor - Karachi

Predict the **Air Quality Index (AQI)** in Karachi for the next **3 days** using weather + pollutant data.  
This project uses a **100% serverless stack**, machine learning, and a **Streamlit web app** for real-time predictions.

---

## 🚀 Features
- Fetch **historical + forecast weather data** from Open-Meteo API  
- Fetch **pollutant data (AQI, PM2.5, PM10, NO2, etc.)** from OpenWeather Air Pollution API  
- **Feature engineering** (time-based + lag features + AQI change rate)  
- **Train ML model (Random Forest)** to predict AQI level (1-5 scale)  
- **Streamlit web app** to predict AQI interactively  
- **Serverless-ready** (e.g. GitHub Actions for CI/CD automation)

---

## 🗂 Project Structure
```

aqi-predictor/
├── app.py                   # Streamlit UI
├── train.py                 # Model training script
├── fetch\_data.py            # Collect and merge weather + pollutant data
├── requirements.txt         # Dependencies
├── data/                    # Input & output datasets
│   ├── features.csv
│   ├── historical\_weather.csv
│   ├── historical\_aqi\_openweather.csv
│   └── merged\_weather\_aqi.csv
├── models/
│   └── aqi\_model.pkl        # Trained ML model
├── notebooks/
│   └── AQI\_Model\_Training.ipynb
└── README.md

````
### App Home
<img width="797" height="842" alt="image" src="https://github.com/user-attachments/assets/28a44c45-5d63-4715-b3f9-7816d927ea42" />

### Pollutant Form
<img width="780" height="760" alt="image" src="https://github.com/user-attachments/assets/98fc6dec-4ca3-404a-bfa4-d7690938f04c" />

### Prediction Output
<img width="783" height="427" alt="image" src="https://github.com/user-attachments/assets/19e85d7b-9133-4fc3-80ae-1932554cbeb5" />

---

## ⚡ How to Run Locally

1. **Clone the repo**
```bash
git clone https://github.com/<your-username>/aqi-predictor.git
cd aqi-predictor
````

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the Streamlit app**

```bash
streamlit run app.py
```

4. **Retrain the model (optional)**

```bash
python train.py
```

---

## 📊 Dataset Sources

* **Weather data:** [Open-Meteo API](https://open-meteo.com)
* **Air pollution data:** [OpenWeather Air Pollution API](https://openweathermap.org/api/air-pollution)

---

## 🎯 Model

* **Algorithm:** Random Forest Regressor
* **Target:** AQI index (1 to 5 scale)
* **Features:** Weather conditions + pollutants + time-based lag features
* **Evaluation Metrics:** MSE, R²

---

## 🌐 Deployment

This project is **serverless-ready**:

* Use **GitHub Actions** to automate:

  * Data fetching every hour
  * Model retraining daily
* Can be hosted on **Streamlit Cloud** or **Google Cloud Run**

---

## 🛠 Tech Stack

* Python 3.10+
* Streamlit
* Pandas / Numpy
* Scikit-learn (Random Forest)
* Open-Meteo API + OpenWeather API



## 👤 Author

**Mahnoor Umar**

* GitHub: [@mahnouor1](https://github.com/mahnouor1)
* LinkedIn: *(https://www.linkedin.com/in/mahnoor-umar-a61027226/)*


