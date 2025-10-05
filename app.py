import streamlit as st
import pandas as pd
import joblib
from datetime import datetime, timedelta

# Load trained model using joblib (NOT pickle)
model = joblib.load("aqi_model.pkl")

# Streamlit page config
st.set_page_config(page_title="AQI Predictor", layout="centered")

st.title("🌫️ AQI Predictor - Karachi")
st.markdown("Enter the required **weather + pollutant** data to predict AQI level (1-5).")

# Sidebar: Future days selection
st.sidebar.header("📅 Prediction Settings")
days_to_predict = st.sidebar.slider("Days ahead to predict", 1, 3, 1)

# --- Input fields ---
st.subheader("🌦️ Weather Features")
temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=30.0)
humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, value=70)
windspeed = st.number_input("Windspeed (m/s)", min_value=0.0, max_value=100.0, value=5.0)
winddir = st.number_input("Wind Direction (°)", min_value=0.0, max_value=360.0, value=180.0)
precipitation = st.number_input("Precipitation (mm)", min_value=0.0, value=0.0)
cloudcover = st.number_input("Cloud Cover (%)", min_value=0, max_value=100, value=50)
pressure = st.number_input("Surface Pressure (hPa)", min_value=900.0, max_value=1100.0, value=1000.0)

st.subheader("🧪 Pollutants")
co = st.number_input("CO (μg/m3)", value=50.0)
no = st.number_input("NO (μg/m3)", value=0.05)
no2 = st.number_input("NO₂ (μg/m3)", value=0.1)
o3 = st.number_input("O₃ (μg/m3)", value=40.0)
so2 = st.number_input("SO₂ (μg/m3)", value=0.3)
pm25 = st.number_input("PM2.5 (μg/m3)", value=20.0)
pm10 = st.number_input("PM10 (μg/m3)", value=50.0)
nh3 = st.number_input("NH₃ (μg/m3)", value=0.1)

# --- Time-based features ---
target_date = datetime.now() + timedelta(days=days_to_predict)
hour = target_date.hour
day = target_date.day
month = target_date.month

# --- Predict AQI ---
if st.button("🔮 Predict AQI"):
    # Provide all features the model expects (23 features total)
    # For historical features, use reasonable defaults
    input_df = pd.DataFrame([{
        # Basic weather and pollutant features (18)
        'temperature_2m': temperature,
        'relative_humidity_2m': humidity,
        'windspeed_10m': windspeed,
        'winddirection_10m': winddir,
        'precipitation': precipitation,
        'cloudcover': cloudcover,
        'surface_pressure': pressure,
        'co': co,
        'no': no,
        'no2': no2,
        'o3': o3,
        'so2': so2,
        'pm2_5': pm25,
        'pm10': pm10,
        'nh3': nh3,
        'hour': hour,
        'day': day,
        'month': month,
        
        # Historical features (5) - using defaults for demo
        'aqi_lag1': 3.0,  # Previous hour AQI
        'aqi_lag2': 3.0,  # 2 hours ago AQI
        'aqi_change_rate': 0.0,  # No change
        'aqi_rolling3': 3.0,  # 3-hour rolling average
        'aqi_rolling6': 3.0,  # 6-hour rolling average
    }])

    prediction = model.predict(input_df)[0]

    aqi_labels = {
        1: "Good 😊",
        2: "Fair 🙂",
        3: "Moderate 😐",
        4: "Poor 😷",
        5: "Very Poor 🤢"
    }

    st.success(f"**Predicted AQI (Day {days_to_predict}): {int(prediction)} → {aqi_labels.get(int(prediction), 'Unknown')}**")
    st.write("Model Input Data:")
    st.dataframe(input_df)
