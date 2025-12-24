# pipeline/predict.py
import os
import pandas as pd
import joblib
from sqlalchemy import text

from database import get_engine
from .train_model import FEATURE_COLS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_FILE = os.path.join(ROOT, "model", "model.pkl")


def predict_for_username(username: str) -> float:
    engine = get_engine()

    # Load the feature rows for this user
    try:
        df = pd.read_sql(
            text("SELECT * FROM dsa_features WHERE username = :u ORDER BY week"),
            engine,
            params={"u": username}
        )
    except Exception as e:
        engine.dispose()
        raise ValueError(f"Error reading features for {username}: {e}")

    if df.empty:
        engine.dispose()
        raise ValueError(f"No data for user: {username}")

    # Ensure model exists
    if not os.path.exists(MODEL_FILE):
        engine.dispose()
        raise FileNotFoundError("Model missing. Run pipeline first.")

    # Select the most recent row
    last = df.iloc[-1]

    # Build input vector
    X = last[FEATURE_COLS].values.reshape(1, -1)

    # Load model
    model = joblib.load(MODEL_FILE)

    # Dispose DB engine (avoid connection errors)
    engine.dispose()

    # Return prediction
    return float(model.predict(X)[0])

