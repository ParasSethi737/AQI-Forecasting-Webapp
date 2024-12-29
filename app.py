import subprocess
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from scripts.forecast import get_forecast_for_last_date

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Data processing functions
def process_data(data):
    try:
        # Flatten pollutant data
        pollutant_data = pd.DataFrame([data['pollutant']])  # Convert to single-row DataFrame

        # Extract weather data directly from the dictionary
        weather_data = data['weather']

        # Combine pollutant and weather data into a single dictionary
        combined_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'pm25': pollutant_data['pm25'].iloc[0],
            'pm10': pollutant_data['pm10'].iloc[0],
            'co': pollutant_data['co'].iloc[0],
            'no2': pollutant_data['no2'].iloc[0],
            'so2': pollutant_data['so2'].iloc[0],
            'o3': pollutant_data['o3'].iloc[0],
            'AQI': pollutant_data['AQI'].iloc[0],
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

        # Convert combined data to a DataFrame
        combined_df = pd.DataFrame([combined_data])  # Single row as a list of dictionaries

        return combined_df

    except Exception as e:
        app.logger.error(f"Error in process_data: {e}")
        raise

def update_csv(combined_data):
    try:

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
        cleaned_data_path = os.path.join(DATASETS_DIR, "cleaned_data.csv")

        # Ensure CSV file exists, if not create it
        if not os.path.exists(cleaned_data_path):
            pd.DataFrame(columns=[
                'date', 'pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'AQI',
                'tempmax', 'tempmin', 'temp', 'humidity', 'dew', 'windspeed',
                'winddir', 'windgust', 'precip', 'cloudcover', 'visibility',
                'sealevelpressure'
            ]).to_csv(cleaned_data_path, index=False)

        # Convert combined_data into DataFrame
        df_combined = pd.DataFrame([combined_data])
        df = pd.read_csv(cleaned_data_path)

        # Concatenate and then drop duplicates
        df_updated = pd.concat([df, df_combined], ignore_index=True)
        df_updated = df_updated.drop_duplicates(subset=['date'], keep='last')

        df_updated.columns = df_updated.columns.str.strip()
        df_updated = df_updated.interpolate(method='linear', axis=0)
        df_updated = df_updated.fillna(method='bfill')

        # Save the updated Data Frame to CSV
        df_updated.to_csv(cleaned_data_path, index=False)

        return {
            "message": "Data updated successfully",
            "path": cleaned_data_path
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

        response = update_csv(processed_data.to_dict(orient='records')[0])  # Converting DataFrame to a serializable dictionary
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

        # Check if the CSV file exists
        if os.path.exists(cleaned_data_path):
            df = pd.read_csv(cleaned_data_path)
            last_update_date = df['date'].max()  # Get the latest date
            app.logger.debug(f"Last update date: {last_update_date}")
            return jsonify({"last_update_date": last_update_date})
        else:
            return jsonify({"message": "Data file does not exist"}), 404

    except Exception as e:
        app.logger.error(f"Error retrieving last update date: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_forecast', methods=['GET'])
def get_forecast():
    """Handles the GET request to fetch the AQI forecast for the last date"""
    forecast = get_forecast_for_last_date()
    return jsonify(forecast)

if __name__ == '__main__':
    app.run(debug=True)