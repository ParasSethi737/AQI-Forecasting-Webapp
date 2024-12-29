import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error, mean_absolute_percentage_error
from xgboost import XGBRegressor
import joblib

# Load the dataset
cleaned_data_path = r'C:\Codes\WebDev\AQI-Forecasting-Webapp\datasets\cleaned_data.csv'
data = pd.read_csv(cleaned_data_path)

# Drop the 'date' column as it's not being used in the model
# Feature Engineering Function
def engineer_additional_features(df):
    # 1. Total Pollution (sum of pollutants)
    df['total_pollution'] = df[['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']].sum(axis=1)
    
    # 2. Cumulative AQI over 7 days (rolling sum of AQI)
    df['aqi_cum_sum_7'] = df['AQI'].rolling(window=7).sum()

    # 3. Seasonal Features: Is it summer (June, July, August)?
    if 'date' in df.columns:
        df['month'] = pd.to_datetime(df['date'], errors='coerce').dt.month
    df['is_summer'] = df['month'].apply(lambda x: 1 if x in [6, 7, 8] else 0)
    
    # 4. Seasonal Features: Is it winter (December, January, February)?
    df['is_winter'] = df['month'].apply(lambda x: 1 if x in [12, 1, 2] else 0)

    # 5. PM25-CO Interaction
    df['pm25_co_interaction'] = df['pm25'] * df['co']
    
    # Additional Engineered Features:
    df['temp_humidity_interaction'] = df['temp'] * df['humidity']  # Interaction between temp and humidity
    df['pm25_cumulative_sum_7'] = df['pm25'].rolling(window=7).sum()  # Cumulative sum of PM25 over 7 days
    df['pm25_no2_interaction'] = df['pm25'] * df['no2']  # Interaction between PM25 and NO2
    df['pm25_so2_interaction'] = df['pm25'] * df['so2']  # Interaction between PM25 and SO2

    return df

# Apply feature engineering
data = engineer_additional_features(data)

# Drop the 'date' column if it's no longer needed for training
data = data.drop(columns=['date','precip','windgust' ], errors='ignore')

# Add lag features for AQI (lag for the last 7 days)
for i in range(1, 8):
    data[f'lag_{i}_AQI'] = data['AQI'].shift(i)

# Drop rows with NaN values due to shifting
data = data.dropna()

# Separate features (X) and target variable (y)
X = data.drop(columns=['AQI'])
y = data[['AQI']]  # Use only the AQI column for prediction

# Create target variables for the next F days (e.g., 3 days)
F = 7
y_next_F_days = pd.DataFrame()
for i in range(1, (F + 1)):
    y_next_F_days[f"AQI_day_{i}"] = data['AQI'].shift(-i)

# Remove the last F rows since they won't have target data for the next F days
X = X.iloc[:-F]
y_next_F_days = y_next_F_days.iloc[:-F]

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y_next_F_days, test_size=0.2, random_state=42, shuffle=False)

# XGBoost model
xgb_model = XGBRegressor(
    colsample_bytree=0.9, gamma=0, learning_rate=0.05, max_depth=3, 
    min_child_weight=1, n_estimators=200, subsample=0.7, random_state=42
)

# Function to evaluate the model
def evaluate_model(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Evaluation metrics
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = mean_absolute_percentage_error(y_test, y_pred)

    return mae, r2, rmse, mape, y_pred

# Evaluate XGBoost model
print("Training and evaluating XGBoost...")
mae, r2, rmse, mape, y_pred = evaluate_model(xgb_model, X_train, X_test, y_train, y_test)

print(f"XGBoost - MAE: {mae:.4f}, R²: {r2:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.4f}")

# Save the XGBoost model
model_path = r'C:\Codes\WebDev\AQI-Forecasting-Webapp\models\xgboost_model.pkl'
joblib.dump(xgb_model, model_path)
print(f"XGBoost model saved to {model_path}")

# To load the model in the future:
# loaded_model = joblib.load(model_path)
# predictions = loaded_model.predict(X_test)
