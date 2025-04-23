# preprocess.py

import pandas as pd

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


def preprocess_pollutant_data(df):
    # Strip column names
    df.columns = df.columns.str.strip()

    # Convert to numeric
    cols = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').interpolate(method='linear')

    # AQI calculation (reuse your existing calculate_aqi() logic here)
    # Assume calculate_aqi() and breakpoints are defined above
    df['AQI_pm25'] = df['pm25'].apply(lambda x: calculate_aqi(x, breakpoints_pm25))
    df['AQI_pm10'] = df['pm10'].apply(lambda x: calculate_aqi(x, breakpoints_pm10))
    df['AQI_o3'] = df['o3'].apply(lambda x: calculate_aqi(x, breakpoints_o3))
    df['AQI_no2'] = df['no2'].apply(lambda x: calculate_aqi(x, breakpoints_no2))
    df['AQI_so2'] = df['so2'].apply(lambda x: calculate_aqi(x, breakpoints_so2))
    df['AQI_co'] = df['co'].apply(lambda x: calculate_aqi(x, breakpoints_co))
    df['AQI'] = df[['AQI_pm25', 'AQI_pm10', 'AQI_o3', 'AQI_no2', 'AQI_so2', 'AQI_co']].max(axis=1)

    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

def preprocess_weather_data(df):
    df.columns = df.columns.str.strip()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.drop(columns=['datetime'], errors='ignore')
    df = df.sort_values('date').drop_duplicates(subset='date')
    
    # Convert object columns to inferred types  
    df = df.infer_objects()
    df = df.interpolate(method='linear').bfill()  # This would replace the deprecated `fillna`
    
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df
