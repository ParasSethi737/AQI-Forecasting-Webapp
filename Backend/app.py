# app.py

import os
import logging
import subprocess
import numpy as np
import pandas as pd
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import create_engine
from scripts.train_model import train_model
from scripts.forecast import get_aqi_forecast
from scripts.fetch_data import fetch_data_from_apis
from flask import Flask, request, jsonify, send_from_directory
from scripts.update_database import update_database, append_aqi_forecast_to_db

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# PostgreSQL connection string from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Create a database engine using SQLAlchemy
engine = create_engine(DATABASE_URL)

# Routes
@app.route('/')
def serve_react_app():
    return send_from_directory('../Frontend/dist', 'index.html')

# Route to trigger hourly tasks directly
@app.route('/api/run_hourly_tasks', methods=['POST'])
def run_hourly_tasks():
    try:
        # Call the functions directly within the app
        weather_df, pollutant_df = fetch_data_from_apis()
        update_database(weather_df, pollutant_df)

        forecast = get_aqi_forecast()
        append_aqi_forecast_to_db(forecast)

        return jsonify({"message": "Hourly tasks completed successfully!"}), 200
    except Exception as e:
        app.logger.error(f"Error during hourly tasks: {str(e)}")
        return jsonify({"error": "Error executing hourly tasks."}), 500


# Route to trigger daily tasks directly
@app.route('/api/run_daily_tasks', methods=['POST'])
def run_daily_tasks():
    try:
        # Call the function to train the model directly
        train_model()

        return jsonify({"message": "Daily tasks completed successfully!"}), 200
    except Exception as e:
        app.logger.error(f"Error during daily tasks: {str(e)}")
        return jsonify({"error": "Error executing daily tasks."}), 500

@app.route('/api/get_evaluation_metrics', methods=['GET'])
def get_evaluation_metrics():
    try:
        # Connect to PostgreSQL database using SQLAlchemy
        with engine.connect() as conn:
            query = """
                SELECT * FROM model_evaluation
                ORDER BY timestamp DESC
                LIMIT 1
            """
            df = pd.read_sql_query(query, conn)

            if df.empty:
                return jsonify({"message": "No evaluation metrics available yet."}), 404

            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()

            # Format the 'date' column if it exists
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Replace NaN with None for JSON response
            df = df.replace({np.nan: None})

            return jsonify({"data": df.to_dict(orient='records')})

    except Exception as e:
        app.logger.error(f"Error fetching evaluation metrics: {str(e)}")
        return jsonify({"error": "Internal Server Error, please try again later."}), 500


@app.route('/api/fetch_current_data', methods=['GET'])
def fetch_current_data():
    try:
        from_date = request.args.get('from_date')
        weather_df, pollutant_df = fetch_data_from_apis(from_date=from_date)

        if isinstance(weather_df, pd.DataFrame) and isinstance(pollutant_df, pd.DataFrame):
            response_data = {
                "weather_data": weather_df.to_dict(orient='records'),
                "pollutant_data": pollutant_df.to_dict(orient='records')
            }
            return jsonify(response_data)
        else:
            return jsonify({"message": "Failed to retrieve valid data."}), 500

    except Exception as e:
        app.logger.error(f"Error fetching current data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/get_forecast', methods=['GET'])
def get_forecast():
    try:
        # Connect to PostgreSQL database using SQLAlchemy
        with engine.connect() as conn:
            latest_forecast_date_query = """
                SELECT MAX(forecast_date) AS latest_forecast_date FROM aqi_forecast
            """
            latest_date_df = pd.read_sql_query(latest_forecast_date_query, conn)
            latest_forecast_date = latest_date_df["latest_forecast_date"].iloc[0]

            forecast_query = f"""
                SELECT * FROM aqi_forecast
                WHERE forecast_date = '{latest_forecast_date}'
                ORDER BY predicted_date ASC
            """
            forecast_df = pd.read_sql_query(forecast_query, conn)

            if forecast_df.empty:
                return jsonify({"message": "No forecast available yet."}), 404

            # Replace NaN with None for valid JSON
            forecast_df = forecast_df.replace({np.nan: None})
            return jsonify(forecast_df.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/view-data/<table_name>', methods=['GET'])
def view_data(table_name):
    try:
        allowed_tables = ['raw_data', 'cleaned_data', 'weather_data', 'pollutant_data', 'aqi_forecast', 'model_evaluation']

        if table_name not in allowed_tables:
            return jsonify({"error": f"Table '{table_name}' is not allowed to be viewed."}), 400

        # Determine the correct column for filtering based on table
        if table_name == 'aqi_forecast':
            date_column = 'forecast_date'
        elif table_name == 'model_evaluation':
            date_column = 'timestamp'
        else:
            date_column = 'date'

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = f"SELECT * FROM {table_name}"
        filters = []

        if start_date:
            filters.append(f"{date_column} >= '{start_date}'")
        if end_date:
            filters.append(f"{date_column} <= '{end_date}'")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        column_order = [
            'date', 'forecast_date', 'predicted_date', 'predicted_aqi', 'model_name', 'location',
            'pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'aqi_pm25', 'aqi_pm10', 'aqi_o3', 'aqi_no2', 'aqi_so2',
            'aqi_co', 'aqi', 'name', 'tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin', 'feelslike',
            'dew', 'humidity', 'precip', 'precipprob', 'precipcover', 'preciptype', 'snow', 'snowdepth',
            'windgust', 'windspeed', 'winddir', 'sealevelpressure', 'cloudcover', 'visibility', 'solarradiation',
            'solarenergy', 'uvindex', 'severerisk', 'sunrise', 'sunset', 'moonphase', 'conditions', 'description',
            'icon', 'stations', 'timestamp', 'mae', 'rmse', 'mape', 'r2'
        ]

        column_order = [col.strip().lower() for col in column_order]
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        df = df.sort_values(by=date_column, ascending=True) 
        df = df.replace({np.nan: None})
        return jsonify(df.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
