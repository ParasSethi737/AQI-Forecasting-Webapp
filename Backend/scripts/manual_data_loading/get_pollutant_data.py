# Script to load data from raw file and load it into the csv file
# Calculating and adding AQI Values to raw pollutant dataset

import pandas as pd
from pathlib import Path

# Define the AQI calculation function for a given pollutant
def calculate_aqi(concentration, breakpoints, scale=False):
    if pd.isna(concentration):  # Handle NaN values gracefully
        return None

    # Iterate through the breakpoints
    for i in range(len(breakpoints)):
        C_LO, C_HI, I_LO, I_HI = breakpoints[i]
        
        # Check if the concentration falls within the range
        if C_LO <= concentration <= C_HI:
            # Calculate the AQI using linear scaling for the range
            if scale:
                # Proportional scaling formula: (concentration - C_LO) * (I_HI - I_LO) / (C_HI - C_LO) + I_LO
                return ((I_HI - I_LO) / (C_HI - C_LO)) * (concentration - C_LO) + I_LO
            else:
                # If we don't want proportional scaling, return concentration directly
                return concentration

    return None  # If concentration doesn't fit into any range

# Define CPCB breakpoints for each pollutant
breakpoints_pm25 = [(0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200), (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)]
breakpoints_pm10 = [(0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200), (251, 350, 201, 300), (351, 430, 301, 400), (431, 600, 401, 500)]
breakpoints_o3 = [(0, 50, 0, 50), (51, 100, 51, 100), (101, 168, 101, 200), (169, 208, 201, 300), (209, 748, 301, 400), (748, 1000, 401, 500)]
breakpoints_no2 = [(0, 40, 0, 50), (41, 80, 51, 100), (81, 180, 101, 200), (181, 280, 201, 300), (281, 400, 301, 400), (401, 800, 401, 500)]
breakpoints_so2 = [(0, 40, 0, 50), (41, 80, 51, 100), (81, 380, 101, 200), (381, 800, 201, 300), (801, 1600, 301, 400), (1601, 3000, 401, 500)]
breakpoints_co = [(0, 1.0, 0, 50), (1.1, 2.0, 51, 100), (2.1, 10, 101, 200), (10.1, 17.0, 201, 300), (17.1, 34.0, 301, 400), (34.1, 50, 401, 500)]

# Load your pollutants data

# Get the base directory (parent directory)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define path for datasets
DATASETS_DIR = BASE_DIR / "datasets"

# Path for the pollutants data file
RAW_DATASETS_DIR = DATASETS_DIR / "raw_data"
pollutants_data_path = RAW_DATASETS_DIR / "mandir-marg, delhi-air-quality.csv"

# Load your pollutants data
pollutant_data = pd.read_csv(pollutants_data_path)
pollutant_data.columns = pollutant_data.columns.str.strip()

# Convert pollutant values to numeric, forcing errors to NaN
pollutant_data['pm25'] = pd.to_numeric(pollutant_data['pm25'], errors='coerce')
pollutant_data['pm10'] = pd.to_numeric(pollutant_data['pm10'], errors='coerce')
pollutant_data['o3'] = pd.to_numeric(pollutant_data['o3'], errors='coerce')
pollutant_data['no2'] = pd.to_numeric(pollutant_data['no2'], errors='coerce')
pollutant_data['so2'] = pd.to_numeric(pollutant_data['so2'], errors='coerce')
pollutant_data['co'] = pd.to_numeric(pollutant_data['co'], errors='coerce')

# Interpolate missing values using linear interpolation
pollutant_data['pm25'] = pollutant_data['pm25'].interpolate(method='linear')
pollutant_data['pm10'] = pollutant_data['pm10'].interpolate(method='linear')
pollutant_data['o3'] = pollutant_data['o3'].interpolate(method='linear')
pollutant_data['no2'] = pollutant_data['no2'].interpolate(method='linear')
pollutant_data['so2'] = pollutant_data['so2'].interpolate(method='linear')
pollutant_data['co'] = pollutant_data['co'].interpolate(method='linear')

# Calculate AQI for each pollutant and add them to the dataframe
pollutant_data['AQI_pm25'] = pollutant_data['pm25'].apply(lambda x: calculate_aqi(x, breakpoints_pm25))
pollutant_data['AQI_pm10'] = pollutant_data['pm10'].apply(lambda x: calculate_aqi(x, breakpoints_pm10))
pollutant_data['AQI_o3'] = pollutant_data['o3'].apply(lambda x: calculate_aqi(x, breakpoints_o3))
pollutant_data['AQI_no2'] = pollutant_data['no2'].apply(lambda x: calculate_aqi(x, breakpoints_no2))
pollutant_data['AQI_so2'] = pollutant_data['so2'].apply(lambda x: calculate_aqi(x, breakpoints_so2))
pollutant_data['AQI_co'] = pollutant_data['co'].apply(lambda x: calculate_aqi(x, breakpoints_co))

# Ensure the AQI columns are in numeric format (float)
pollutant_data['AQI_pm25'] = pollutant_data['AQI_pm25'].astype(float)
pollutant_data['AQI_pm10'] = pollutant_data['AQI_pm10'].astype(float)
pollutant_data['AQI_o3'] = pollutant_data['AQI_o3'].astype(float)
pollutant_data['AQI_no2'] = pollutant_data['AQI_no2'].astype(float)
pollutant_data['AQI_so2'] = pollutant_data['AQI_so2'].astype(float)
pollutant_data['AQI_co'] = pollutant_data['AQI_co'].astype(float)

# Now calculate the overall AQI (maximum of all the pollutants)
pollutant_data['AQI'] = pollutant_data[['AQI_pm25', 'AQI_pm10', 'AQI_o3', 'AQI_no2', 'AQI_so2', 'AQI_co']].max(axis=1)

# Convert 'date' column to datetime format, auto-detect format
pollutant_data['date'] = pd.to_datetime(pollutant_data['date'], errors='coerce')

# Sort by date in ascending order (oldest first, latest at the bottom)
pollutant_data = pollutant_data.sort_values(by='date', ascending=True)

# Format date as 'YYYY-MM-DD' before saving
pollutant_data['date'] = pollutant_data['date'].dt.strftime('%Y-%m-%d')

# Save the updated dataframe with AQI to a CSV file
pollutant_data.to_csv(DATASETS_DIR / "pollutant_data.csv", index=False) #changed from pollutants to pollutant

print("Pollutants AQI values calculated and saved to 'datasets/pollutant_data.csv'")