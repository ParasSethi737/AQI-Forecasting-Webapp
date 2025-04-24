# forecast.py

import os
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from scripts.train_model import load_data, engineer_additional_features, create_lag_features

""" BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "ML_models"
MODEL_PATH = DATASETS_DIR / "xgboost_model.pkl" """

# for render
MODEL_PATH = '/app/data/xgboost_model.pkl'

def get_aqi_forecast():
    """Generates a forecast for the next 7 days using the latest data"""

    # Retrain the model if not found
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Retraining...")
        train_model()

    data = load_data()
    data = engineer_additional_features(data)
    data = create_lag_features(data)
    
    last_row = data.iloc[[-1]]
    X_last = last_row.drop(columns=['AQI', 'date'], errors='ignore')

    model = joblib.load(MODEL_PATH)
    predictions = model.predict(X_last)

    # Ensure predictions is a flat NumPy array
    if isinstance(predictions, (list, tuple)):
        predictions = np.array(predictions)
    elif np.isscalar(predictions):
        predictions = np.array([predictions])

    # Make sure it has 7 predictions
    if predictions.ndim > 1:
        predictions = predictions.flatten()

    if len(predictions) != 7:
        raise ValueError(f"Expected 7 predictions, got {len(predictions)}: {predictions}")

    # Convert to JSON-safe dict
    start_date = datetime.today()
    forecast = {
        (start_date + timedelta(days=i + 1)).strftime('%Y-%m-%d'): float(np.round(predictions[i], 2))
        for i in range(7)
    }

    return forecast


# Example usage
if __name__ == '__main__':
    forecast = get_aqi_forecast()
    print(forecast) 