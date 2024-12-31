from pathlib import Path
import pandas as pd

# Define the base directory and datasets directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"

# Load individual weather datasets
weather_files = [
    "INDIRA GANDHI INTERNATION... 2013-12-09 to 2016-09-03.csv",
    "INDIRA GANDHI INTERNATION... 2016-09-04 to 2016-10-16.csv",
    "INDIRA GANDHI INTERNATION... 2016-10-17 to 2019-07-13.csv",
    "INDIRA GANDHI INTERNATION... 2019-07-14 to 2022-04-08.csv",
    "INDIRA GANDHI INTERNATION... 2022-04-09 to 2024-11-20.csv",
    "INDIRA GANDHI INTERNATION... 2024-11-21 to 2024-12-27.csv"
]

# Load and concatenate all weather datasets
combined_weather_data = pd.concat(
    [pd.read_csv(DATASETS_DIR / file) for file in weather_files]
)

# Ensure the 'datetime' column is in datetime format
combined_weather_data['datetime'] = pd.to_datetime(combined_weather_data['datetime'], format='%Y-%m-%d', errors='coerce')

# Rename 'datetime' to 'date'
combined_weather_data.rename(columns={'datetime': 'date'}, inplace=True)

# Remove duplicates and sort by 'date'
combined_weather_data = combined_weather_data.drop_duplicates().sort_values(by='date')

# Interpolate missing values
combined_weather_data = combined_weather_data.interpolate(method='linear', axis=0)

# Backfill remaining missing values
combined_weather_data = combined_weather_data.fillna(method='bfill')

# Save the combined data to CSV
combined_weather_data.to_csv(DATASETS_DIR / 'weather_data.csv', index=False)

print(f"Combined weather data saved to '{DATASETS_DIR / 'weather_data.csv'}'")