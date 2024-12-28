# Create a Clean Dataset with Engineered Features
import pandas as pd
from pathlib import Path

# Get the base directory (parent directory)
BASE_DIR = Path(__file__).resolve().parent.parent

# Define path for datasets
DATASETS_DIR = BASE_DIR / "datasets"

# Path to the merged weather and pollutant data
merged_data_path = DATASETS_DIR / "merged_weather_pollutant_data.csv"

# Load the dataset
data = pd.read_csv(merged_data_path)

# Strip any leading or trailing spaces from the column names
data.columns = data.columns.str.strip()

# Add engineered features in the dataset
data['temp_humidity_interaction'] = data['temp'] * data['humidity']
data['pm25_cumulative_sum_7'] = data['pm25'].rolling(window=7).sum()
data['pm25_no2_interaction'] = data['pm25'] * data['no2']
data['pm25_so2_interaction'] = data['pm25'] * data['so2']

# List of selected features to keep
selected_features = [
    'date',                                               # Time-related
    'pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'AQI',      # Pollutants
    'tempmax', 'tempmin', 'temp', 'humidity', 'dew', 'windspeed', 'winddir', 'windgust',
    'precip', 'cloudcover', 'visibility',                 # Weather
    'sealevelpressure',                                   # Environmental
    'temp_humidity_interaction', 'pm25_cumulative_sum_7', # Engineered features
    'pm25_no2_interaction', 'pm25_so2_interaction'
]

# Filter out only the selected features
data_filtered = data[selected_features]

# Output the filtered dataset as a CSV file
data_filtered.to_csv(DATASETS_DIR / "cleaned_data.csv", index=False)

print("Filtered data saved to 'datasets/cleaned_data.csv'")

# Print the filtered dataset (or inspect the first few rows)
print(data_filtered.head())
