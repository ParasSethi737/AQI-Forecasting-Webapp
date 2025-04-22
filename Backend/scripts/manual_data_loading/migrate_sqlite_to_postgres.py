import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Set your PostgreSQL database URL (from Render's Environment Variables or your local config)
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLite connection (your original .db file)
sqlite_conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "../../aqi_forecast.db"))  # Using relative path

# Connect to PostgreSQL
pg_engine = create_engine(DATABASE_URL)

# List of tables to migrate
tables = ['WeatherData', 'PollutantData', 'RawData', 'CleanedData', 'AQIForecast', 'ModelEvaluation']

# Migrate each table
for table in tables:
    # Read from SQLite
    df = pd.read_sql(f"SELECT * FROM {table}", sqlite_conn)
    
    # Insert into PostgreSQL
    df.to_sql(table, pg_engine, if_exists='replace', index=False)  # 'replace' overwrites if the table already exists

# Close SQLite connection
sqlite_conn.close()
