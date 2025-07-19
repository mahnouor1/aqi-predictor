# data_collection.py
import requests
import pandas as pd
from datetime import datetime
import os

# ✅ Use GitHub Secret instead of hardcoding
API_KEY = os.getenv("API_KEY")  # This must be set in GitHub Secrets!

def fetch_iqair_data(api_key):
    url = f"http://api.airvisual.com/v2/nearest_city?key={api_key}"
    response = requests.get(url).json()

    if response['status'] != 'success':
        print("❌ Failed to fetch data:", response)
        return pd.DataFrame()

    pollution = response['data']['current']['pollution']
    weather = response['data']['current']['weather']
    ts = pd.to_datetime(pollution['ts'])

    record = {
        "datetime": ts,
        "aqi_us": pollution['aqius'],
        "main_pollutant": pollution['mainus'],
        "temperature": weather['tp'],
        "humidity": weather['hu'],
        "wind_speed": weather['ws'],
        "hour": ts.hour,
        "day": ts.day,
        "month": ts.month
    }

    df = pd.DataFrame([record])
    if os.path.exists("raw_data.csv"):
        df.to_csv("raw_data.csv", mode='a', header=False, index=False)
    else:
        df.to_csv("raw_data.csv", index=False)

    print("✅ Data saved at", ts)
    return df

# Run script
df = fetch_iqair_data(API_KEY)

if not df.empty:
    print(df)
else:
    print("❌ No data returned. Check your API key or try again later.")
