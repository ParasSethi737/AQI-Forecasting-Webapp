# tasks.py

from scripts.fetch_data import fetch_data_from_apis
from scripts.update_database import update_database, append_aqi_forecast_to_db
from scripts.forecast import get_aqi_forecast
from datetime import datetime

def run_scheduled_tasks():
    # Fetch data from APIs and update the database`
    weather_df, pollutant_df = fetch_data_from_apis()
    update_database(weather_df, pollutant_df)

    # Get AQI forecast and append it to the database
    forecast = get_aqi_forecast()
    append_aqi_forecast_to_db(forecast)

if __name__ == "__main__":
    run_scheduled_tasks()
    print("Scheduled tasks completed at:", datetime.now())
