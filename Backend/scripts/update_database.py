import os
import pandas as pd
from typing import List
from datetime import datetime
from sqlalchemy import create_engine, text
from scripts.preprocess import preprocess_weather_data, preprocess_pollutant_data
from dotenv import load_dotenv

def delete_existing_entries(conn, date_str: str, tables: List[str]):
    for table in tables:
        conn.execute(
            text(f"DELETE FROM {table} WHERE date = :date_str"),
            {"date_str": date_str}
        )

# Function to update the database with new weather and pollutant data
def update_database(weather_df: pd.DataFrame, pollutant_df: pd.DataFrame):
    # Connect to PostgreSQL (use DATABASE_URL from environment variables)
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()

    # 1. Preprocess new data
    weather_df = preprocess_weather_data(weather_df)
    pollutant_df = preprocess_pollutant_data(pollutant_df)

    # Ensure consistent date format
    weather_df['date'] = pd.to_datetime(weather_df['date'])
    pollutant_df['date'] = pd.to_datetime(pollutant_df['date'])

    # 2. Get the latest date (assumes all rows are for the same date)
    latest_date = weather_df['date'].max()
    latest_date_str = latest_date.strftime('%Y-%m-%d')  # Convert to string format

    # 3. Load existing data for that date
    existing_weather = pd.read_sql_query(
        "SELECT * FROM weather_data WHERE date = %s", conn, params=(latest_date_str,)
    )
    print("Existing weather data loaded:", existing_weather.shape)
    print("data:", weather_df)
    existing_pollutant = pd.read_sql_query(
        "SELECT * FROM pollutant_data WHERE date = %s", conn, params=(latest_date_str,)
    )

    # Ensure consistent date format in existing data
    existing_weather['date'] = pd.to_datetime(existing_weather['date'])
    existing_pollutant['date'] = pd.to_datetime(existing_pollutant['date'])

    # 4. Combine with new data
    if not existing_weather.empty:
        print("Existing weather data found. Appending new data.")
        full_weather = pd.concat([existing_weather, weather_df], ignore_index=True)
        full_weather = full_weather.dropna(axis=1, how='all')  # Remove all-NA columns
    else:
        full_weather = weather_df.copy()

    if not existing_pollutant.empty:
        print("Existing pollutant data found. Appending new data.")
        full_pollutant = pd.concat([existing_pollutant, pollutant_df], ignore_index=True)
    else:
        full_pollutant = pollutant_df.copy()

    # 5. Perform numeric aggregation and merge
    numeric_cols_weather = full_weather.select_dtypes(include=['number']).columns
    non_numeric_cols_weather = full_weather.select_dtypes(exclude=['number']).columns

    numeric_cols_pollutant = full_pollutant.select_dtypes(include=['number']).columns
    non_numeric_cols_pollutant = full_pollutant.select_dtypes(exclude=['number']).columns

    # Perform numeric aggregation
    avg_weather_numeric = full_weather.groupby("date", as_index=False)[
        [col for col in numeric_cols_weather if col != "date"]
    ].mean()

    avg_pollutant_numeric = full_pollutant.groupby("date", as_index=False)[
        [col for col in numeric_cols_pollutant if col != "date"]
    ].mean()

    avg_weather_non_numeric = full_weather.groupby("date", as_index=False)[non_numeric_cols_weather].first()
    avg_pollutant_non_numeric = full_pollutant.groupby("date", as_index=False)[non_numeric_cols_pollutant].first()

    # Merge numeric and non-numeric columns
    avg_weather = pd.merge(avg_weather_numeric, avg_weather_non_numeric, on="date", how="inner")
    avg_pollutant = pd.merge(avg_pollutant_numeric, avg_pollutant_non_numeric, on="date", how="inner")

    # 6. Merge to form RawData and CleanData
    avg_raw = pd.merge(avg_weather, avg_pollutant, on="date", how="inner")
    avg_raw = avg_raw.drop_duplicates(subset='date')  # Remove duplicate dates

    cleaned_features = [
        "date", "pm25", "pm10", "co", "no2", "so2", "o3", "AQI",
        "tempmax", "tempmin", "temp", "humidity", "dew",
        "windspeed", "winddir", "windgust", "precip", "cloudcover",
        "visibility", "sealevelpressure"
    ]
    existing_features = list(set(cleaned_features).intersection(avg_raw.columns))
    avg_clean = avg_raw[existing_features].copy()

    # Convert date columns to string format
    for df in [avg_weather, avg_pollutant, avg_raw, avg_clean]:
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # 7. Delete existing entries for the date
    try:
        delete_existing_entries(conn, latest_date_str, ['weather_data', 'pollutant_data', 'raw_data', 'cleaned_data'])

        # Insert new data into the tables
        avg_weather.to_sql('weather_data', conn, if_exists='append', index=False)
        avg_pollutant.to_sql('pollutant_data', conn, if_exists='append', index=False)
        avg_raw.to_sql('raw_data', conn, if_exists='append', index=False)
        avg_clean.to_sql('cleaned_data', conn, if_exists='append', index=False)

        conn.commit()
        print(f"Averaged data stored for {latest_date_str} in all 4 tables.")
    except Exception as e:
        conn.rollback()
        print(f"Database update failed: {e}")
    finally:
        conn.close()

def append_aqi_forecast_to_db(forecast):
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    forecast_date = datetime.today().strftime('%Y-%m-%d')
    model_name = 'XGBoost_V1'
    location = 'Delhi'

    # Create a list of dictionaries to pass to execute()
    forecast_data = [
        {
            'forecast_date': forecast_date,
            'predicted_date': predicted_date,
            'predicted_aqi': predicted_aqi,
            'model_name': model_name,
            'location': location
        }
        for predicted_date, predicted_aqi in forecast.items()
    ]

    # Use SQLAlchemy-safe text query with named parameters
    upsert_query = text("""
        INSERT INTO aqi_forecast (forecast_date, predicted_date, predicted_aqi, model_name, location)
        VALUES (:forecast_date, :predicted_date, :predicted_aqi, :model_name, :location)
        ON CONFLICT(forecast_date, predicted_date) DO UPDATE SET
            predicted_aqi = EXCLUDED.predicted_aqi,
            model_name = EXCLUDED.model_name,
            location = EXCLUDED.location;
    """)

    with engine.begin() as conn:
        conn.execute(upsert_query, forecast_data)

    print(f"Forecasts for {forecast_date} inserted successfully.")

def load_and_merge_data_from_csv(save_to_sqlite=True, save_to_postgres=True):
    load_dotenv()

    # File paths
    datasets_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets')
    weather_csv_path = os.path.join(datasets_folder, 'weather_data.csv')
    pollutant_csv_path = os.path.join(datasets_folder, 'pollutant_data.csv')

    # Load CSVs
    print("Loading weather and pollutant data from CSV...")
    weather_df = pd.read_csv(weather_csv_path)
    weather_df['date'] = pd.to_datetime(weather_df['date'], errors='coerce')

    pollutant_df = pd.read_csv(pollutant_csv_path)
    pollutant_df['date'] = pd.to_datetime(pollutant_df['date'], errors='coerce')

    # Merge
    print("Merging datasets...")
    merged_df = pd.merge(weather_df, pollutant_df, on='date', how='inner')

    # Clean and extract
    cleaned_features = [
        "date", "pm25", "pm10", "co", "no2", "so2", "o3", "AQI",
        "tempmax", "tempmin", "temp", "humidity", "dew",
        "windspeed", "winddir", "windgust", "precip", "cloudcover",
        "visibility", "sealevelpressure"
    ]
    cleaned_df = merged_df[cleaned_features].copy()

    if save_to_postgres:
        print("Saving to PostgreSQL...")
        DATABASE_URL = os.getenv("DATABASE_URL")
        pg_engine = create_engine(DATABASE_URL)

        with pg_engine.begin() as conn:
            weather_df.to_sql('weather_data', conn, if_exists='replace', index=False)
            pollutant_df.to_sql('pollutant_data', conn, if_exists='replace', index=False)
            merged_df.to_sql('raw_data', conn, if_exists='replace', index=False)
            cleaned_df.to_sql('cleaned_data', conn, if_exists='replace', index=False)

    if save_to_sqlite:
        print("Saving to SQLite...")
        sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'aqi_forecast.db')
        sqlite_engine = create_engine(f'sqlite:///{sqlite_path}')

        with sqlite_engine.begin() as conn:
            weather_df.to_sql('WeatherData', conn, if_exists='replace', index=False)
            pollutant_df.to_sql('PollutantData', conn, if_exists='replace', index=False)
            merged_df.to_sql('RawData', conn, if_exists='replace', index=False)
            cleaned_df.to_sql('CleanedData', conn, if_exists='replace', index=False)

    print("CSVs imported and saved to databases successfully.")

""" if __name__ == '__main__':
    load_and_merge_data_from_csv() """