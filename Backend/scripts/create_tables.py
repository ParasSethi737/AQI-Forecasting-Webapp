# Create_tables.py

import os
import sqlite3

print("Current working directory:", os.getcwd())
db_path = os.path.abspath("aqi_forecast.db")
print("Database will be created at:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Table for cleaned data
cursor.execute('''
CREATE TABLE IF NOT EXISTS CleanedData (
    date TEXT PRIMARY KEY,
    pm25 REAL, pm10 REAL, co REAL, no2 REAL, so2 REAL, o3 REAL,
    AQI REAL, tempmax REAL, tempmin REAL, temp REAL, humidity REAL,
    dew REAL, windspeed REAL, winddir REAL, windgust REAL, precip REAL,
    cloudcover REAL, visibility REAL, sealevelpressure REAL
);
''')

# Table for raw merged data
cursor.execute('''
CREATE TABLE IF NOT EXISTS RawData (
    date TEXT PRIMARY KEY,
    pm25 REAL, pm10 REAL, o3 REAL, no2 REAL, so2 REAL, co REAL,
    AQI_pm25 REAL, AQI_pm10 REAL, AQI_o3 REAL, AQI_no2 REAL, AQI_so2 REAL, AQI_co REAL, AQI REAL,
    name TEXT, tempmax REAL, tempmin REAL, temp REAL, feelslikemax REAL,
    feelslikemin REAL, feelslike REAL, dew REAL, humidity REAL, precip REAL,
    precipprob REAL, precipcover REAL, preciptype TEXT, snow REAL, snowdepth REAL,
    windgust REAL, windspeed REAL, winddir REAL, sealevelpressure REAL,
    cloudcover REAL, visibility REAL, solarradiation REAL, solarenergy REAL,
    uvindex REAL, severerisk REAL, sunrise TEXT, sunset TEXT,
    moonphase REAL, conditions TEXT, description TEXT, icon TEXT, stations TEXT
);
''')

# Table to store past forecasts
cursor.execute('''
CREATE TABLE IF NOT EXISTS AQIForecast (
    forecast_date TEXT NOT NULL,           -- Date when forecast was generated
    predicted_date TEXT NOT NULL,          -- Date for which AQI is predicted
    predicted_aqi REAL NOT NULL,           -- Forecasted AQI
    model_name TEXT DEFAULT 'XGBoost_V1',  -- Optional
    location TEXT DEFAULT 'Delhi',         -- Optional
    PRIMARY KEY (forecast_date, predicted_date)
);
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS WeatherData (
    date TEXT PRIMARY KEY,
    name TEXT,
    tempmax REAL, tempmin REAL, temp REAL,
    feelslikemax REAL, feelslikemin REAL, feelslike REAL,
    dew REAL, humidity REAL,
    precip REAL, precipprob REAL, precipcover REAL,
    preciptype TEXT, snow REAL, snowdepth REAL,
    windgust REAL, windspeed REAL, winddir REAL,
    sealevelpressure REAL, cloudcover REAL,
    visibility REAL, solarradiation REAL, solarenergy REAL,
    uvindex REAL, severerisk REAL,
    sunrise TEXT, sunset TEXT,
    moonphase REAL,
    conditions TEXT, description TEXT, icon TEXT, stations TEXT
);
''')

# Create the PollutantData table
cursor.execute('''
CREATE TABLE IF NOT EXISTS PollutantData (
    date TEXT PRIMARY KEY,
    pm25 REAL,
    pm10 REAL,
    o3 REAL,
    no2 REAL,
    so2 REAL,
    co REAL,
    AQI_pm25 REAL,
    AQI_pm10 REAL,
    AQI_o3 REAL,
    AQI_no2 REAL,
    AQI_so2 REAL,
    AQI_co REAL,
    AQI REAL
);
''')

conn.commit()
conn.close()
print("Tables created successfully.")
