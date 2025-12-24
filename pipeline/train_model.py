# pipeline/train_model.py
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import text

from database import get_engine

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_FILE = os.path.join(ROOT, "model", "model.pkl")

FEATURE_COLS = [
    "total_solved", "easy_solved", "medium_solved", "hard_solved",
    "prev_total",
    "weekly_growth", "weekly_easy_growth", "weekly_medium_growth", "weekly_hard_growth",
    "easy_ratio", "medium_ratio", "hard_ratio", "balance_score",
    "consistency_score", "hard_problem_density", "rolling_growth_3week",
]


def train():
    engine = get_engine()

    # Read feature data from MySQL
    try:
        df = pd.read_sql(text("SELECT * FROM dsa_features ORDER BY username, week"), engine)
    except Exception as e:
        print("[train] Error reading dsa_features:", e)
        engine.dispose()
        return

    if df.empty:
        print("[train] No feature rows found.")
        engine.dispose()
        return

    # Prepare training data
    X = df[FEATURE_COLS].fillna(0)
    y = df["weekly_growth"].fillna(0)

    # Train model
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
    )
    model.fit(X, y)

    # Save model
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print("[train] Model saved:", MODEL_FILE)

    # Dispose DB engine to prevent huggingface disconnect issues
    engine.dispose()

