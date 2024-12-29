import pandas as pd
import os
from pathlib import Path

# Get the base directory (two levels up from this script's location)
BASE_DIR = Path(__file__).resolve().parent.parent

# Construct paths dynamically
datasets_dir = BASE_DIR / "datasets"
weather_data_path = datasets_dir / "weather_data.csv"
pollutants_data_path = datasets_dir / "pollutants_data.csv"
merged_data_path = datasets_dir / "merged_weather_pollutant_data.csv"

# Load the combined weather data
combined_weather_data = pd.read_csv(weather_data_path)

# Load the pollutant data
pollutant_data = pd.read_csv(pollutants_data_path)

# Ensure the 'date' column in pollutant data is in datetime format
pollutant_data['date'] = pd.to_datetime(pollutant_data['date'], errors='coerce', dayfirst=True)

# Ensure the 'datetime' column in weather data is in datetime format
combined_weather_data['datetime'] = pd.to_datetime(combined_weather_data['datetime'], errors='coerce')

# Merge the combined weather data with pollutant data
merged_data = pd.merge(pollutant_data, combined_weather_data, left_on='date', right_on='datetime', how='inner')

# Drop the redundant 'datetime' column if present
merged_data = merged_data.drop(columns=['datetime'], errors='ignore')  # Drop 'datetime' if it's redundant; keep 'date' for clarity

# Save the merged data to a CSV file
merged_data.to_csv(merged_data_path, index=False)

print(f"Merged data saved to '{merged_data_path}'")