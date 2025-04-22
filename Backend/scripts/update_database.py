# update_database.py

import os
import sqlite3
import pandas as pd
from typing import List
from datetime import datetime
from .preprocess import preprocess_weather_data, preprocess_pollutant_data


def delete_existing_entries(conn, date_str: str, tables: List[str]):
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f"DELETE FROM {table} WHERE date = ?", (date_str,))


def update_database(weather_df: pd.DataFrame, pollutant_df: pd.DataFrame):
    # Set the path to the SQLite database in persistent storage
    DATABASE_PATH = os.path.join('/app/data', 'aqi_forecast.db')
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)

    # 1. Preprocess new data
    weather_df = preprocess_weather_data(weather_df)
    pollutant_df = preprocess_pollutant_data(pollutant_df)

    # Ensure consistent date format
    weather_df['date'] = pd.to_datetime(weather_df['date'])
    pollutant_df['date'] = pd.to_datetime(pollutant_df['date'])

    # Debug: Print input DataFrames
    print("Weather DataFrame:")
    print(weather_df.head())
    print("Pollutant DataFrame:")
    print(pollutant_df.head())

    # 2. Get latest date (assumes all rows are for the same date)
    latest_date = weather_df['date'].max()
    latest_date_str = latest_date.strftime('%Y-%m-%d')  # Convert to string format

    # 3. Load existing data for that date
    existing_weather = pd.read_sql_query(
        "SELECT * FROM WeatherData WHERE date = ?", conn, params=(latest_date_str,)
    )
    existing_pollutant = pd.read_sql_query(
        "SELECT * FROM PollutantData WHERE date = ?", conn, params=(latest_date_str,)
    )

    # Ensure consistent date format in existing data
    existing_weather['date'] = pd.to_datetime(existing_weather['date'])
    existing_pollutant['date'] = pd.to_datetime(existing_pollutant['date'])

    # Debug: Print existing data
    print("Existing Weather DataFrame:")
    print(existing_weather.head())
    print("Existing Pollutant DataFrame:")
    print(existing_pollutant.head())

    # 4. Combine with new data
    full_weather = pd.concat([existing_weather, weather_df]) if not existing_weather.empty else weather_df
    full_pollutant = pd.concat([existing_pollutant, pollutant_df]) if not existing_pollutant.empty else pollutant_df

    # Separate numeric and non-numeric columns
    numeric_cols_weather = full_weather.select_dtypes(include=['number']).columns
    non_numeric_cols_weather = full_weather.select_dtypes(exclude=['number']).columns

    numeric_cols_pollutant = full_pollutant.select_dtypes(include=['number']).columns
    non_numeric_cols_pollutant = full_pollutant.select_dtypes(exclude=['number']).columns

    # Perform numeric aggregation
    avg_weather_numeric = full_weather.groupby("date", as_index=False)[numeric_cols_weather].mean()
    avg_pollutant_numeric = full_pollutant.groupby("date", as_index=False)[numeric_cols_pollutant].mean()

    # Retain the first non-numeric row for each date
    avg_weather_non_numeric = full_weather.groupby("date", as_index=False)[non_numeric_cols_weather].first()
    avg_pollutant_non_numeric = full_pollutant.groupby("date", as_index=False)[non_numeric_cols_pollutant].first()

    # Merge numeric and non-numeric columns
    avg_weather = pd.merge(avg_weather_numeric, avg_weather_non_numeric, on="date", how="inner")
    avg_pollutant = pd.merge(avg_pollutant_numeric, avg_pollutant_non_numeric, on="date", how="inner")

    # Debug: Print averaged DataFrames
    print("Averaged Weather DataFrame:")
    print(avg_weather.head())
    print("Averaged Pollutant DataFrame:")
    print(avg_pollutant.head())

    # 6. Merge to form RawData and CleanData
    avg_raw = pd.merge(avg_weather, avg_pollutant, on="date", how="inner")
    avg_raw = avg_raw.drop_duplicates(subset='date')  # Remove duplicate dates
    print("Merged DataFrame (avg_raw):")
    print(avg_raw.head())

    cleaned_features = [
        "date", "pm25", "pm10", "co", "no2", "so2", "o3", "AQI",
        "tempmax", "tempmin", "temp", "humidity", "dew",
        "windspeed", "winddir", "windgust", "precip", "cloudcover",
        "visibility", "sealevelpressure"
    ]
    # Ensure only existing columns are selected
    existing_features = list(set(cleaned_features).intersection(avg_raw.columns))
    avg_clean = avg_raw[existing_features].copy()

    # Convert date columns to string format
    for df in [avg_weather, avg_pollutant, avg_raw, avg_clean]:
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # Debug: Print cleaned DataFrame
    print("Cleaned DataFrame (avg_clean):")
    print(avg_clean.head())

    # 7. Overwrite today's data in all 4 tables
    try:
        delete_existing_entries(conn, latest_date_str, ['WeatherData', 'PollutantData', 'RawData', 'CleanedData'])

        avg_weather.to_sql('WeatherData', conn, if_exists='append', index=False)
        avg_pollutant.to_sql('PollutantData', conn, if_exists='append', index=False)
        avg_raw.to_sql('RawData', conn, if_exists='append', index=False)
        avg_clean.to_sql('CleanedData', conn, if_exists='append', index=False)

        conn.commit()
        print(f"Averaged data stored for {latest_date_str} in all 4 tables.")
    except Exception as e:
        conn.rollback()
        print(f"Database update failed: {e}")
    finally:
        conn.close()

def append_aqi_forecast_to_db(forecast):
    # Set the path to the SQLite database in persistent storage
    DATABASE_PATH = os.path.join('/app/data', 'aqi_forecast.db')
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    forecast_date = datetime.today().strftime('%Y-%m-%d')  # when the forecast was made
    model_name = 'XGBoost_V1'
    location = 'Delhi'

    for predicted_date, predicted_aqi in forecast.items():
        # Upsert (insert or replace) based on forecast_date and predicted_date
        cursor.execute('''
            INSERT INTO AQIForecast (forecast_date, predicted_date, predicted_aqi, model_name, location)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(forecast_date, predicted_date) DO UPDATE SET
                predicted_aqi=excluded.predicted_aqi,
                model_name=excluded.model_name,
                location=excluded.location;
        ''', (forecast_date, predicted_date, predicted_aqi, model_name, location))

    conn.commit()
    conn.close()
    print("Forecast data appended to AQIForecast table.")

def load_and_merge_data_from_csv():
    # Adjust the path to the datasets folder
    datasets_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets')
    # Set the path to the SQLite database in persistent storage
    DATABASE_PATH = os.path.join('/app/data', 'aqi_forecast.db')
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)

    # Load weather data from CSV
    weather_csv_path = os.path.join(datasets_folder, 'weather_data.csv')
    print("Loading weather data from CSV...")
    weather_df = pd.read_csv(weather_csv_path)
    weather_df['date'] = pd.to_datetime(weather_df['date'], format='%Y-%m-%d', errors='coerce')

    # Save weather data to WeatherData table (override existing data)
    print("Saving weather data to WeatherData table...")
    weather_df.to_sql('WeatherData', conn, if_exists='replace', index=False)

    # Load pollutant data from CSV
    pollutant_csv_path = os.path.join(datasets_folder, 'pollutant_data.csv')
    print("Loading pollutant data from CSV...")
    pollutant_df = pd.read_csv(pollutant_csv_path)
    pollutant_df['date'] = pd.to_datetime(pollutant_df['date'], format='%Y-%m-%d', errors='coerce')

    # Save pollutant data to PollutantData table (override existing data)
    print("Saving pollutant data to PollutantData table...")
    pollutant_df.to_sql('PollutantData', conn, if_exists='replace', index=False)

    # Merge weather and pollutant data
    print("Merging weather and pollutant data...")
    merged_df = pd.merge(weather_df, pollutant_df, on='date', how='inner')

    # Insert merged data into RawData table (override existing data)
    print("Inserting merged data into RawData table...")
    merged_df.to_sql('RawData', conn, if_exists='replace', index=False)

    # Clean and extract relevant features
    print("Cleaning and extracting relevant features...")
    cleaned_features = [
        "date", "pm25", "pm10", "co", "no2", "so2", "o3", "AQI",
        "tempmax", "tempmin", "temp", "humidity", "dew",
        "windspeed", "winddir", "windgust", "precip", "cloudcover",
        "visibility", "sealevelpressure"
    ]
    cleaned_df = merged_df[cleaned_features].copy()

    # Insert cleaned data into CleanData table (override existing data)
    print("Inserting cleaned data into CleanData table...")
    cleaned_df.to_sql('CleanedData', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    print("Data from CSVs successfully loaded, merged, and saved to the database.")

""" if __name__ == "__main__":
    load_and_merge_data_from_csv() """
