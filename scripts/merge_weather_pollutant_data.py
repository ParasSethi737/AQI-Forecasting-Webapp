import pandas as pd
import os
from pathlib import Path

# Get the base directory (two levels up from this script's location)
BASE_DIR = Path(__file__).resolve().parent.parent

# Construct paths dynamically
datasets_dir = BASE_DIR / "datasets"
weather_data_path = datasets_dir / "weather_data.csv"
pollutants_data_path = datasets_dir / "pollutant_data.csv" #changed from pollutants to pollutant   
merged_data_path = datasets_dir / "merged_weather_pollutant_data.csv" 

# Load the weather and pollutant data
weather_data = pd.read_csv(weather_data_path)
pollutant_data = pd.read_csv(pollutants_data_path)

# Convert 'date' column to datetime format in both datasets // not being in format causes error(an explosion)
weather_data['date'] = pd.to_datetime(weather_data['date'], format='%Y-%m-%d', errors='coerce')
pollutant_data['date'] = pd.to_datetime(pollutant_data['date'], format='%Y-%m-%d', errors='coerce')

# Merge the combined weather data with pollutant data
merged_data = pd.merge(pollutant_data, weather_data, left_on='date', right_on='date', how='inner')

# Save the merged data to a CSV file
merged_data.to_csv(merged_data_path, index=False)

print(f"Merged data saved to '{merged_data_path}'")