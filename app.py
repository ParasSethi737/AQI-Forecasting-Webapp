from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from scripts.forecast import get_forecast_for_last_date
from pathlib import Path 

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Data processing functions
def process_data(data):
    try:
        combined_results = []

        for day_data in data:
            # Extract individual day's data
            pollutant_data = day_data['pollutant']
            weather_data = day_data['weather']

            combined_data = {
                'date': day_data['date'],
                'pm25': pollutant_data['pm25'],
                'pm10': pollutant_data['pm10'],
                'co': pollutant_data['co'],
                'no2': pollutant_data['no2'],
                'so2': pollutant_data['so2'],
                'o3': pollutant_data['o3'],
                'AQI': pollutant_data['AQI'],
                'tempmax': weather_data['tempmax'],
                'tempmin': weather_data['tempmin'],
                'temp': weather_data['temp'],
                'humidity': weather_data['humidity'],
                'dew': weather_data['dew'],
                'windspeed': weather_data['windspeed'],
                'winddir': weather_data['winddir'],
                'windgust': weather_data['windgust'],
                'precip': weather_data['precip'],
                'cloudcover': weather_data['cloudcover'],
                'visibility': weather_data['visibility'],
                'sealevelpressure': weather_data['pressure']
            }

            combined_results.append(combined_data)

        combined_df = pd.DataFrame(combined_results)  # Multiple rows as a DataFrame
        return combined_df

    except Exception as e:
        app.logger.error(f"Error in process_data: {e}")
        raise

def update_csv(combined_data):
    try:
        BASE_DIR = Path(__file__).resolve().parent
        DATASETS_DIR = BASE_DIR / "datasets"

        cleaned_data_path = DATASETS_DIR / "cleaned_data.csv"
        weather_data_path = DATASETS_DIR / "weather_data.csv"
        combined_df = pd.DataFrame(combined_data)

        # Ensure 'date' is in the correct datetime format with year-first (YYYY-MM-DD)
        combined_df['date'] = pd.to_datetime(combined_df['date']).dt.strftime('%Y-%m-%d')

        # Update cleaned_data.csv
        df_cleaned = pd.read_csv(cleaned_data_path)
        df_cleaned_updated = pd.concat([df_cleaned, combined_df], ignore_index=True)
        df_cleaned_updated = df_cleaned_updated.drop_duplicates(subset=['date'], keep='first')
        df_cleaned_updated = df_cleaned_updated.interpolate(method='linear', axis=0)
        df_cleaned_updated = df_cleaned_updated.fillna(method='bfill')
        df_cleaned_updated.to_csv(cleaned_data_path, index=False)

        # Update weather_data.csv
        weather_columns = [
            'date', 'tempmax', 'tempmin', 'temp', 'humidity', 'dew',
            'windspeed', 'winddir', 'windgust', 'precip', 'cloudcover',
            'visibility', 'sealevelpressure'
        ]

        # Read the existing weather data
        df_weather = pd.read_csv(weather_data_path)

        # Select relevant weather columns from combined_df
        df_weather_combined = combined_df[weather_columns]

        # Concatenate and update weather data
        df_weather_updated = pd.concat([df_weather, df_weather_combined], ignore_index=True)

        # Remove duplicates based on 'date' and handle missing values
        df_weather_updated = df_weather_updated.drop_duplicates(subset=['date'], keep='first')
        df_weather_updated = df_weather_updated.interpolate(method='linear', axis=0)
        df_weather_updated = df_weather_updated.fillna(method='bfill')

        # Save the updated weather data
        df_weather_updated.to_csv(weather_data_path, index=False)

        return {
            "message": "Data updated successfully",
            "paths": {
                "cleaned_data": str(cleaned_data_path),
                "weather_data": str(weather_data_path)
            }
        }

    except Exception as e:
        return {
            "message": "Error updating data",
            "error": str(e)
        }


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

@app.route('/update_data', methods=['POST'])
def api_update_csv():
    try:
        json_data = request.data.decode('utf-8')
        app.logger.debug(f"Received JSON data: {json_data}")

        data = json.loads(json_data)
        processed_data = process_data(data)
        app.logger.debug(f"Processed data: {processed_data}")

        response = update_csv(processed_data.to_dict(orient='records'))  # Multiple rows as a list of dictionaries
        app.logger.debug(f"Response: {response}")
        
        return jsonify(response)  # Converting response to JSON format
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/datasets/cleaned_data.csv')
def get_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the base directory
    datasets_dir = os.path.join(base_dir, "datasets")  # Concatenates with 'datasets'
    cleaned_data_path = os.path.join(datasets_dir, "cleaned_data.csv")
    return send_file(cleaned_data_path, as_attachment=True)

@app.route('/api/last_update_date', methods=['GET'])
def get_last_update_date():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
        cleaned_data_path = os.path.join(DATASETS_DIR, "cleaned_data.csv")

        if os.path.exists(cleaned_data_path):
            df = pd.read_csv(cleaned_data_path)
            last_update_date = df['date'].max()
            app.logger.debug(f"Last update date: {last_update_date}")
            return jsonify({"last_update_date": last_update_date})
        else:
            return jsonify({"message": "Data file does not exist"}), 404

    except Exception as e:
        app.logger.error(f"Error retrieving last update date: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_forecast', methods=['GET'])
def get_forecast():
    try:
        forecast = get_forecast_for_last_date()
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)