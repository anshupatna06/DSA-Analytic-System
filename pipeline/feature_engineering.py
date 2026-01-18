# pipeline/feature_engineering.py

import pandas as pd
from sqlalchemy import text
from database import get_engine


def engineer():
    engine = get_engine()

    # -------------------------------------------------
    # Load raw data (ORDER BY username + date)
    # -------------------------------------------------
    df = pd.read_sql(
        text("""
            SELECT *
            FROM dsa_data
            ORDER BY username, date
        """),
        engine
    )

    if df.empty:
        print("[FE] No raw data found.")
        engine.dispose()
        return

    # -------------------------------------------------
    # Ensure numeric types (safety)
    # -------------------------------------------------
    num_cols = ["easy_solved", "medium_solved", "hard_solved", "total_solved"]
    df[num_cols] = df[num_cols].fillna(0).astype(int)

    # -------------------------------------------------
    # Lag Features
    # -------------------------------------------------
    df["prev_total"] = df.groupby("username")["total_solved"].shift(1).fillna(0)
    df["prev_easy"] = df.groupby("username")["easy_solved"].shift(1).fillna(0)
    df["prev_medium"] = df.groupby("username")["medium_solved"].shift(1).fillna(0)
    df["prev_hard"] = df.groupby("username")["hard_solved"].shift(1).fillna(0)

    # -------------------------------------------------
    # Growth Metrics
    # -------------------------------------------------
    df["weekly_growth"] = df["total_solved"] - df["prev_total"]
    df["weekly_easy_growth"] = df["easy_solved"] - df["prev_easy"]
    df["weekly_medium_growth"] = df["medium_solved"] - df["prev_medium"]
    df["weekly_hard_growth"] = df["hard_solved"] - df["prev_hard"]

    # -------------------------------------------------
    # Ratios (safe divide)
    # -------------------------------------------------
    denom = df["total_solved"].replace(0, 1)

    df["easy_ratio"] = df["easy_solved"] / denom
    df["medium_ratio"] = df["medium_solved"] / denom
    df["hard_ratio"] = df["hard_solved"] / denom
    df["balance_score"] = (
        df["easy_ratio"] + df["medium_ratio"] + df["hard_ratio"]
    )

    # -------------------------------------------------
    # Consistency & Rolling Metrics
    # -------------------------------------------------
    df["consistency_score"] = (
        df.groupby("username")["weekly_growth"]
          .rolling(3)
          .std()
          .reset_index(0, drop=True)
          .fillna(0)
    )

    df["hard_problem_density"] = df["hard_solved"] / denom

    df["rolling_growth_3week"] = (
        df.groupby("username")["weekly_growth"]
          .rolling(3)
          .mean()
          .reset_index(0, drop=True)
          .fillna(0)
    )

    # -------------------------------------------------
    # Ensure Drift Columns Exist (DB safety)
    # -------------------------------------------------
    with engine.begin() as conn:
        columns_to_add = {
            "week_start_date": "DATE",
            "prev_weekly_growth": "INT",
            "inactive_weeks": "INT DEFAULT 0",
            "sudden_drop": "BOOLEAN",
            "declining_trend": "BOOLEAN",
            "drift_flag": "BOOLEAN",
            "drift_reason": "VARCHAR(100)"
        }

        for col, dtype in columns_to_add.items():
            try:
                conn.exec_driver_sql(
                    f"ALTER TABLE dsa_features ADD COLUMN {col} {dtype}"
                )
                print(f"[FE] Added column: {col}")
            except Exception:
                pass

    df["week_start_date"] = pd.to_datetime(df["date"])

    # -------------------------------------------------
    # Drift Detection Logic
    # -------------------------------------------------

    # Previous week's growth
    df["prev_weekly_growth"] = (
        df.groupby("username")["weekly_growth"].shift(1)
    )

    # ---- Inactivity Detection (NEW)
    df["inactive_weeks"] = 0

    for user, group in df.groupby("username"):
        inactive = 0
        for idx in group.index:
            if df.loc[idx, "weekly_growth"] == 0:
                inactive += 1
            else:
                inactive = 0
            df.loc[idx, "inactive_weeks"] = inactive

    # ---- Sudden Drop
    df["sudden_drop"] = (
        (df["weekly_growth"] < 0) &
        (df["weekly_growth"].abs() > 0.5 * df["rolling_growth_3week"])
    )


    # ---- Declining Trend
    df["declining_trend"] = (
        (df["weekly_growth"] < df["prev_weekly_growth"]) &
        (df["prev_weekly_growth"] <
         df.groupby("username")["weekly_growth"].shift(2))
    )

    # ---- Final Drift Flag
    df["drift_flag"] = (
        (df["inactive_weeks"] >= 2) |
        df["sudden_drop"] |
        df["declining_trend"]
    )

    # ---- Drift Reason encouraging clarity
    df["drift_reason"] = None
    df.loc[df["inactive_weeks"] >= 2, "drift_reason"] = "No progress for 2+ weeks"
    df.loc[df["sudden_drop"], "drift_reason"] = "Sudden drop in weekly growth"
    df.loc[df["declining_trend"], "drift_reason"] = "Consistent decline over weeks"

    

    # -------------------------------------------------
    # Write back (atomic + safe)
    # -------------------------------------------------
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
    print("[FE] Feature engineering + drift detection completed successfully.")

