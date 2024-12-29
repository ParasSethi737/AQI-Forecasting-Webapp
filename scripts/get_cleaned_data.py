# Create a Clean Dataset with Engineered Features
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
merged_data_path = DATASETS_DIR / "merged_weather_pollutant_data.csv"

# Load the dataset
data = pd.read_csv(merged_data_path)

# Strip any leading or trailing spaces from the column names
data.columns = data.columns.str.strip()

# List of selected features to keep
selected_features = [
    'date',                                               # Time-related
    'pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'AQI',      # Pollutants
    'tempmax', 'tempmin', 'temp', 'humidity', 'dew', 'windspeed', 'winddir', 'windgust',
    'precip', 'cloudcover', 'visibility',                 # Weather
    'sealevelpressure'
]

# Filter out only the selected features
data_filtered = data[selected_features]

# Output the filtered dataset as a CSV file
data_filtered.to_csv(DATASETS_DIR / "cleaned_data.csv", index=False)

print("Filtered data saved to 'datasets/cleaned_data.csv'")

# Print the filtered dataset (or inspect the first few rows)
print(data_filtered.head())