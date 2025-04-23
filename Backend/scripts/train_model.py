# train_model.py
import os
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error, mean_absolute_percentage_error
from xgboost import XGBRegressor

# Load the dataset from PostgreSQL
def load_data():
    # Set the database URL (use environment variable or hardcoded URL for local development)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Create a connection to the PostgreSQL database
    engine = create_engine(DATABASE_URL)

    # SQL query to fetch the data
    query = "SELECT * FROM cleaned_data"
    data = pd.read_sql(query, engine)

    # Close the connection
    engine.dispose()

    data = data.drop(columns=['precip'], errors='ignore')
    return data

# Feature Engineering Function
def engineer_additional_features(df):
    df['total_pollution'] = df[['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']].sum(axis=1)
    df['aqi_cum_sum_7'] = df['AQI'].rolling(window=7).sum()
    if 'date' in df.columns:
        df['month'] = pd.to_datetime(df['date'], errors='coerce').dt.month
    df['is_summer'] = df['month'].apply(lambda x: 1 if x in [6, 7, 8] else 0)
    df['is_winter'] = df['month'].apply(lambda x: 1 if x in [12, 1, 2] else 0)
    df['pm25_co_interaction'] = df['pm25'] * df['co']
    df['temp_humidity_interaction'] = df['temp'] * df['humidity']
    df['pm25_cumulative_sum_7'] = df['pm25'].rolling(window=7).sum()
    df['pm25_no2_interaction'] = df['pm25'] * df['no2']
    df['pm25_so2_interaction'] = df['pm25'] * df['so2']
    return df

# Function to create lag features
def create_lag_features(df, num_lags=7):
    """Creates lag features for AQI"""
    for i in range(1, num_lags + 1):
        df[f'lag_{i}_AQI'] = df['AQI'].shift(i)
    df = df.dropna()  # Drop rows with NaN values (from lagging)
    return df

# Prepare the data for training
def prepare_data():
    data = load_data()
    data = engineer_additional_features(data)
    
    data = data.drop(columns=['date'], errors='ignore')

    # Add lag features for AQI (lag for the last 7 days)
    data = create_lag_features(data)

    X = data.drop(columns=['AQI'])
    y = data[['AQI']]  

    # Create target variables for the next F days (e.g., 7 days)
    F = 7
    y_next_F_days = pd.DataFrame()
    for i in range(1, (F + 1)):
        y_next_F_days[f"AQI_day_{i}"] = data['AQI'].shift(-i)

    # Remove the last F rows since they won't have target data for the next F days
    X = X.iloc[:-F]
    y_next_F_days = y_next_F_days.iloc[:-F]

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y_next_F_days, test_size=0.2, random_state=42, shuffle=False)

    return X_train, X_test, y_train, y_test

# Train the XGBoost model
def train_model():
    X_train, X_test, y_train, y_test = prepare_data()

    # XGBoost model
    xgb_model = XGBRegressor(
        colsample_bytree=0.9, gamma=0, learning_rate=0.035, max_depth=3, 
        min_child_weight=1, n_estimators=200, subsample=0.7, random_state=42
    )

    # Fit the model
    xgb_model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = xgb_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = mean_absolute_percentage_error(y_test, y_pred)

    print(f"XGBoost - MAE: {mae:.4f}, R²: {r2:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.4f}")

    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    now = pd.Timestamp.now()

    metrics_data = {
        "timestamp": now.isoformat(),
        "mae": round(float(mae), 4),
        "r2": round(float(r2), 4),
        "rmse": round(float(rmse), 4),
        "mape": round(float(mape), 4),
        "eval_date": now.date()  # Clean and direct!
    }

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO model_evaluation (timestamp, eval_date, mae, r2, rmse, mape)
                VALUES (:timestamp, :eval_date, :mae, :r2, :rmse, :mape)
                ON CONFLICT (eval_date) DO UPDATE SET
                    timestamp = EXCLUDED.timestamp,
                    mae = EXCLUDED.mae,
                    r2 = EXCLUDED.r2,
                    rmse = EXCLUDED.rmse,
                    mape = EXCLUDED.mape;
            """),
            metrics_data
        )

    # Save the trained model
    # model_path = r'C:\Codes\WebDev\AQI-Forecasting-Webapp\Backend\ML_models\xgboost_model.pkl'
    # Save the trained model to a relative path
    # model_path = os.path.join(os.path.dirname(__file__), 'ML_models', 'xgboost_model.pkl')

    # for render
    model_path = '/app/data/xgboost_model.pkl'

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Save the trained model
    joblib.dump(xgb_model, model_path)
    print(f"XGBoost model saved to {model_path}")


if __name__ == '__main__':
    train_model()