# daily_tasks.py

import datetime
from scripts.train_model import train_model

def run_daily_tasks():
    """
    Function to run hourly tasks such as training the model.
    """
    # Train the model
    train_model()

if __name__ == "__main__":
    run_daily_tasks()
    print("Hourly tasks completed at:", datetime.now())
