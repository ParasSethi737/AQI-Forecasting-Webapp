#app.py

import sqlite3
import logging
import numpy as np
import pandas as pd
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from scripts.fetch_data import fetch_data_from_apis


load_dotenv()
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Routes
@app.route('/')
def serve_react_app():
    return send_from_directory('../Frontend/dist', 'index.html')

@app.route('/api/get_evaluation_metrics', methods=['GET'])
def get_evaluation_metrics():
    try:
        # Connect to the SQLite database using context manager
        with sqlite3.connect('aqi_forecast.db') as conn:
            # Query to get the evaluation metrics
            query = """
                SELECT * FROM ModelEvaluation
                ORDER BY timestamp DESC
                LIMIT 1
            """
            df = pd.read_sql_query(query, conn)

        # If the dataframe is empty, return a message indicating no metrics
        if df.empty:
            return jsonify({"message": "No evaluation metrics available yet."}), 404

        # Normalize column names in the DataFrame (strip and lower case)
        df.columns = df.columns.str.strip().str.lower()

        # Convert the 'date' column to a readable format (if exists)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Replace NaN values with None for valid JSON response
        df = df.replace({np.nan: None})

        # Return the evaluation metrics as a JSON response
        return jsonify({
            "data": df.to_dict(orient='records')
        })

    except Exception as e:
        # Log the error with the exception details
        app.logger.error(f"Error fetching evaluation metrics: {str(e)}")
        return jsonify({"error": "Internal Server Error, please try again later."}), 500


@app.route('/api/fetch_current_data', methods=['GET'])
def fetch_current_data():
    try:
        from_date = request.args.get('from_date')
        weather_df, pollutant_df = fetch_data_from_apis(from_date=from_date)

        # Check if both are valid DataFrames
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
        conn = sqlite3.connect('aqi_forecast.db')
        
        # Step 1: Get the latest forecast_date
        latest_forecast_date_query = """
            SELECT MAX(forecast_date) as latest_forecast_date FROM AQIForecast
        """
        latest_date_df = pd.read_sql_query(latest_forecast_date_query, conn)
        latest_forecast_date = latest_date_df["latest_forecast_date"].iloc[0]

        # Step 2: Fetch all rows with that forecast_date
        forecast_query = f"""
            SELECT * FROM AQIForecast
            WHERE forecast_date = '{latest_forecast_date}'
            ORDER BY predicted_date ASC
        """
        forecast_df = pd.read_sql_query(forecast_query, conn)
        conn.close()

        if forecast_df.empty:
            return jsonify({"message": "No forecast available yet."}), 404

        forecast_df = forecast_df.replace({np.nan: None})
        return jsonify(forecast_df.to_dict(orient='records'))

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

        # Replace NaN with None to ensure valid JSON
        df = df.replace({np.nan: None})

        # Convert DataFrame to JSON
        data = df.to_dict(orient='records')
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)