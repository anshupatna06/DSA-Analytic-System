# pipeline/feature_engineering.py
import pandas as pd
from sqlalchemy import text
from database import get_engine


def engineer():
    engine = get_engine()

    df = pd.read_sql(
        text("SELECT * FROM dsa_data ORDER BY username, date"),
        engine
    )

    if df.empty:
        print("[FE] No raw data.")
        engine.dispose()
        return

    # ==== COMPUTE FEATURES ====
    df["prev_total"] = df.groupby("username")["total_solved"].shift(1).fillna(0)
    df["prev_easy"] = df.groupby("username")["easy_solved"].shift(1).fillna(0)
    df["prev_medium"] = df.groupby("username")["medium_solved"].shift(1).fillna(0)
    df["prev_hard"] = df.groupby("username")["hard_solved"].shift(1).fillna(0)

    df["weekly_growth"] = df["total_solved"] - df["prev_total"]
    df["weekly_easy_growth"] = df["easy_solved"] - df["prev_easy"]
    df["weekly_medium_growth"] = df["medium_solved"] - df["prev_medium"]
    df["weekly_hard_growth"] = df["hard_solved"] - df["prev_hard"]

    df["easy_ratio"] = df["easy_solved"] / df["total_solved"].replace(0, 1)
    df["medium_ratio"] = df["medium_solved"] / df["total_solved"].replace(0, 1)
    df["hard_ratio"] = df["hard_solved"] / df["total_solved"].replace(0, 1)
    df["balance_score"] = df["easy_ratio"] + df["medium_ratio"] + df["hard_ratio"]

    df["consistency_score"] = (
        df.groupby("username")["weekly_growth"]
        .rolling(3).std().reset_index(0, drop=True).fillna(0)
    )

    df["hard_problem_density"] = df["hard_solved"] / df["total_solved"].replace(0, 1)
    df["rolling_growth_3week"] = (
        df.groupby("username")["weekly_growth"]
        .rolling(3).mean().reset_index(0, drop=True).fillna(0)
    )

    # ===== SAFE WRITE BACK =====
    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM dsa_features")

    df.drop(columns=["id"], errors="ignore").to_sql(
        "dsa_features",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=200
    )

    engine.dispose()
    print("[FE] Features updated.")

