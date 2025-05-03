# fetch_data.py

import os
import requests
import pandas as pd
from zoneinfo import ZoneInfo # for timezone handling
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def fetch_data_from_apis(from_date=None):
    WEATHER_API_KEY = os.getenv("WEATHER_KEY")
    POLLUTANT_API_KEY = os.getenv("POLLUTANT_KEY")
    STATION = "@10124"
    LOCATION = "INDIRA GANDHI INTERNATIONAL, IN"

    today = datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d') # Current date in IST timezone
    from_date = from_date or today
    to_date = today

    # Weather API call
    weather_url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{LOCATION}/{from_date}/{to_date}?unitGroup=metric&include=days&key={WEATHER_API_KEY}&contentType=json"
    )
    weather_response = requests.get(weather_url).json()

    weather_data = []
    for day in weather_response.get("days", []):
        weather_data.append({
            "date": day.get("datetime"),
            "name": weather_response.get("resolvedAddress", "Unknown"),
            "tempmax": day.get("tempmax"),
            "tempmin": day.get("tempmin"),
            "temp": day.get("temp"),
            "feelslikemax": day.get("feelslikemax"),
            "feelslikemin": day.get("feelslikemin"),
            "feelslike": day.get("feelslike"),
            "dew": day.get("dew"),
            "humidity": day.get("humidity"),
            "precip": day.get("precip"),
            "precipprob": day.get("precipprob"),
            "precipcover": day.get("precipcover"),
            "preciptype": ",".join(day.get("preciptype", [])) if day.get("preciptype") else None,
            "snow": day.get("snow"),
            "snowdepth": day.get("snowdepth"),
            "windgust": day.get("windgust"),
            "windspeed": day.get("windspeed"),
            "winddir": day.get("winddir"),
            "sealevelpressure": day.get("sealevelpressure"),
            "cloudcover": day.get("cloudcover"),
            "visibility": day.get("visibility"),
            "solarradiation": day.get("solarradiation"),
            "solarenergy": day.get("solarenergy"),
            "uvindex": day.get("uvindex"),
            "severerisk": day.get("severerisk"),
            "sunrise": day.get("sunrise"),
            "sunset": day.get("sunset"),
            "moonphase": day.get("moonphase"),
            "conditions": day.get("conditions"),
            "description": day.get("description"),
            "icon": day.get("icon"),
            "stations": ",".join(day.get("stations", [])) if day.get("stations") else None
        })
    print(weather_data)
    weather_df = pd.DataFrame(weather_data)

    # Pollutant API call
    pollutant_url = f"https://api.waqi.info/feed/{STATION}/?token={POLLUTANT_API_KEY}"
    pollutant_response = requests.get(pollutant_url).json()
    iaqi = pollutant_response.get("data", {}).get("iaqi", {})

    pollutant_df = pd.DataFrame([{
        "date": today,
        "pm25": iaqi.get("pm25", {}).get("v"),
        "pm10": iaqi.get("pm10", {}).get("v"),
        "o3": iaqi.get("o3", {}).get("v"),
        "no2": iaqi.get("no2", {}).get("v"),
        "so2": iaqi.get("so2", {}).get("v"),
        "co": iaqi.get("co", {}).get("v"),
        "AQI_pm25": None,
        "AQI_pm10": None,
        "AQI_o3": None,
        "AQI_no2": None,
        "AQI_so2": None,
        "AQI_co": None,
        "AQI": pollutant_response.get("data", {}).get("aqi")
    }])
    print(pollutant_df)
    return weather_df, pollutant_df
