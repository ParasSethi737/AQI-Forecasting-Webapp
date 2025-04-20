#app.py

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from scripts.forecast import get_aqi_forecast
from pathlib import Path 

from scripts.update_database import get_last_update_date_from_db, update_database,  append_aqi_forecast_to_db
import sqlite3
from flask import Response
from scripts.fetch_data import fetch_data_from_apis
from flask import render_template


load_dotenv()
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get_keys', methods=['GET'])
def get_keys():
    pollutant_key = os.getenv("POLLUTANT_KEY")
    weather_key = os.getenv("WEATHER_KEY")
    keys = {"POLLUTANT_KEY": pollutant_key, "WEATHER_KEY": weather_key}
    app.logger.debug(f"API Keys: {keys}")
    app.logger.debug(f"Access-Control-Allow-Origin: {request.environ.get('HTTP_ORIGIN')}")
    return jsonify(keys)

@app.route('/api/last_update_date', methods=['GET'])
def get_last_update_date():
    try:
        last_update_date = get_last_update_date_from_db()
        if last_update_date:
            app.logger.debug(f"Last update date from DB: {last_update_date}")
            return jsonify({"last_update_date": last_update_date})
        else:
            return jsonify({"message": "No update date found"}), 404

    except Exception as e:
        app.logger.error(f"Error retrieving last update date: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/fetch_current_data', methods=['GET'])
def fetch_current_data():
    try:
        from_date = request.args.get('from_date')
        weather_df, pollutant_df = fetch_data_from_apis(from_date=from_date)

        # Check if both are valid DataFrames
        if isinstance(weather_df, pd.DataFrame) and isinstance(pollutant_df, pd.DataFrame):
            # Update database with averaged data for today's date
            update_database(weather_df, pollutant_df)

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
        forecast = get_aqi_forecast()
        append_aqi_forecast_to_db(forecast)  
        print(f"Forecast data: {forecast}")
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/view-data/<table_name>', methods=['GET'])
def view_data(table_name):
    try:
        # Allowed tables to prevent SQL injection
        allowed_tables = ['RawData', 'CleanedData', 'WeatherData', 'PollutantData', 'AQIForecast']
        
        # Check if the table name is valid
        if table_name not in allowed_tables:
            return jsonify({"error": f"Table '{table_name}' is not allowed to be viewed."}), 400
        
        date_column = 'forecast_date' if table_name == 'AQIForecast' else 'date'
        # Get date range parameters from the request
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Construct the query
        query = f"SELECT * FROM {table_name}"
        filters = []

        # Apply date filters if provided
        if start_date:
            filters.append(f"{date_column} >= '{start_date}'")
        if end_date:
            filters.append(f"{date_column} <= '{end_date}'")
        
        # If there are filters, add them to the query
        if filters:
            query += " WHERE " + " AND ".join(filters)

        # Connect to the database
        conn = sqlite3.connect('aqi_forecast.db')
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Normalize column names in the DataFrame
        df.columns = df.columns.str.strip().str.lower()

        # Define the desired column order
        column_order = [
            'date', 'forecast_date', 'predicted_date', 'predicted_aqi', 'model_name', 'location',
            'pm25', 'pm10', 'o3', 'no2', 'so2', 'co',
            'aqi_pm25', 'aqi_pm10', 'aqi_o3', 'aqi_no2', 'aqi_so2', 'aqi_co', 'aqi',
            'name', 'tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin', 'feelslike',
            'dew', 'humidity', 'precip', 'precipprob', 'precipcover', 'preciptype', 'snow', 'snowdepth',
            'windgust', 'windspeed', 'winddir', 'sealevelpressure', 'cloudcover', 'visibility',
            'solarradiation', 'solarenergy', 'uvindex', 'severerisk', 'sunrise', 'sunset',
            'moonphase', 'conditions', 'description', 'icon', 'stations'
        ]

        # Normalize column names in the column_order list
        column_order = [col.strip().lower() for col in column_order]

        # Filter column_order to include only columns that exist in the DataFrame
        existing_columns = [col for col in column_order if col in df.columns]

        # Reorder the DataFrame columns
        df = df[existing_columns]

        # Convert DataFrame to JSON
        data = df.to_dict(orient='records')
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)