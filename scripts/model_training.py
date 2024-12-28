from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib  # Import for saving/loading the model

# Get the base directory (parent directory)
BASE_DIR = Path(__file__).resolve().parent.parent

# Define paths for datasets and models
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"

# Path for the cleaned data
cleaned_data_path = DATASETS_DIR / "cleaned_data.csv"

# Load the dataset
data = pd.read_csv(cleaned_data_path)

# Separate features and target variable
X = data.drop(columns=['AQI', 'date'])
y = data['AQI']

# Backward fill to address NaNs at the start
X['pm25_cumulative_sum_7'] = X['pm25_cumulative_sum_7'].bfill()

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save the trained model to a file
model_path = MODELS_DIR / "aqi_model.pkl"
joblib.dump(rf_model, model_path)
print(f"Model saved to {model_path}")

# Evaluate the model
y_pred_rf = rf_model.predict(X_test)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
r2_rf = r2_score(y_test, y_pred_rf)
rmse_rf = mean_squared_error(y_test, y_pred_rf, squared=False)  # RMSE calculation

print(f"AQI Random Forest MAE: {mae_rf:.4f}, R²: {r2_rf:.4f}, RMSE: {rmse_rf:.4f}")

# To load the model in the future:
# loaded_model = joblib.load(model_path)
# predictions = loaded_model.predict(X_test)
