# Merging weather Data

import pandas as pd

# Load the weather datasets
weather_data_2013_12_09_to_2016_09_03 = pd.read_csv('datasets/INDIRA GANDHI INTERNATION... 2013-12-09 to 2016-09-03.csv')
weather_data_2016_09_04_to_2016_10_16 = pd.read_csv('datasets/INDIRA GANDHI INTERNATION... 2016-09-04 to 2016-10-16.csv')
weather_data_2016_10_17_to_2019_07_13 = pd.read_csv('datasets/INDIRA GANDHI INTERNATION... 2016-10-17 to 2019-07-13.csv')
weather_data_2019_07_14_to_2022_04_08 = pd.read_csv('datasets/INDIRA GANDHI INTERNATION... 2019-07-14 to 2022-04-08.csv')
weather_data_2022_04_09_to_2024_11_20 = pd.read_csv('datasets/INDIRA GANDHI INTERNATION... 2022-04-09 to 2024-11-20.csv')
weather_data_2024_11_21_to_2024_12_27 = pd.read_csv('datasets/INDIRA GANDHI INTERNATION... 2024-11-21 to 2024-12-27.csv')

# Combine all weather datasets
combined_weather_data = pd.concat([
    weather_data_2013_12_09_to_2016_09_03,
    weather_data_2016_09_04_to_2016_10_16, 
    weather_data_2016_10_17_to_2019_07_13,
    weather_data_2019_07_14_to_2022_04_08,
    weather_data_2022_04_09_to_2024_11_20,
    weather_data_2024_11_21_to_2024_12_27
])


# Ensure the 'datetime' column is in datetime format
combined_weather_data['datetime'] = pd.to_datetime(combined_weather_data['datetime'], format='%Y-%m-%d', errors='coerce')

# Interpolate missing values
combined_weather_data = combined_weather_data.interpolate(method='linear', axis=0)

# Remove duplicates and sort by datetime
combined_weather_data = combined_weather_data.drop_duplicates().sort_values(by='datetime')

combined_weather_data.to_csv('datasets/weather_data.csv', index=False)

print("Combined weather data saved to 'datasets/weather_data.csv'")