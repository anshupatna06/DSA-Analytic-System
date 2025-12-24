# pipeline/run_pipeline.py
from .fetch_data import run_fetch
from .feature_engineering import engineer
from .train_model import train


def run_full_pipeline():
    print(">>> Fetching from LeetCode & saving to dsa_data...")
    run_fetch()
    print(">>> Engineering features into dsa_features...")
    engineer()
    print(">>> Training ML model...")
    train()
    print(">>> Pipeline Done.")
