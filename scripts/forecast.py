# forecast.py
import pandas as pd
import joblib
from .train_model import load_data, engineer_additional_features, create_lag_features
from pathlib import Path

# Path to the saved model
BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "models"
MODEL_PATH = DATASETS_DIR / "xgboost_model.pkl"

def get_forecast_for_last_date():
    """Generates a forecast for the next 7 days using the latest data"""
    # Load the cleaned dataset
    data = load_data()

    # Feature engineering
    data = engineer_additional_features(data)

    # Create lag features
    data = create_lag_features(data)

    # Get the last row of data (i.e., most recent date)
    last_row = data.iloc[[-1]]

    # Separate features (X) from the target (y)
    X_last = last_row.drop(columns=['AQI', 'date'], errors='ignore')

    # Load the model
    model = joblib.load(MODEL_PATH)

    # Predict for the next 7 days (ensure that model returns multiple predictions)
    predictions = model.predict(X_last)

    # If predictions is a single value (not an array of 7 days), reshape it
    if len(predictions) == 1:
        predictions = predictions[0]

    # Check that predictions is an array of 7 elements (as expected)
    if len(predictions) != 7:
        raise ValueError(f"Prediction output has unexpected shape. Expected 7 elements, but got {len(predictions)}")

    # Return predictions as a dictionary with day_1 to day_7
    forecast = {f"day_{i+1}": round(predictions[i]) for i in range(7)}

    return forecast

# Example usage
if __name__ == '__main__':
    forecast = get_forecast_for_last_date()
    print(forecast)