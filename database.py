# database.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError



def get_engine():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")

    if not all([host, user, password, port, db]):
        raise RuntimeError("Database environment variables missing!")

    url = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{host}:{port}/{db}"
        "?sslmode=require"
    )

    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5
    )




def init_tables_and_migrate():
    engine = get_engine()

    with engine.begin() as conn:

        # =============================================================
        # BASE TABLE: dsa_data
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS dsa_data (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username VARCHAR(100),
                week INT,
                easy_solved INT,
                medium_solved INT,
                hard_solved INT,
                total_solved INT
            );
        """)


        # Add date column
        

        # =============================================================
        # dsa_features
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS dsa_features (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username VARCHAR(100),
                week INT,
                
                total_solved INT,
                easy_solved INT,
                medium_solved INT,
                hard_solved INT,
                prev_total INT,
                prev_easy INT,
                prev_medium INT,
                prev_hard INT,
                weekly_growth INT,
                weekly_easy_growth INT,
                weekly_medium_growth INT,
                weekly_hard_growth INT,
                easy_ratio FLOAT,
                medium_ratio FLOAT,
                hard_ratio FLOAT,
                balance_score FLOAT,
                consistency_score FLOAT,
                hard_problem_density FLOAT,
                rolling_growth_3week FLOAT
            );
        """)
        # 🔴 ADD week_start_date if missing (Postgres-safe)
        
        conn.exec_driver_sql("""
            ALTER TABLE dsa_features
            ADD COLUMN IF NOT EXISTS week_start_date DATE
        """)
        print("✅ Added week_start_date to dsa_features")
        

        

        # =============================================================
        # LOGIN USERS TABLE
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username VARCHAR(100) UNIQUE,
                password_hash VARCHAR(200),
                is_admin BOOLEAN DEFAULT FALSE
            );
        """)

        # =============================================================
        # PLATFORM PROFILES (MULTI-PLATFORM SUPPORT)
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS platform_profiles (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                platform_username VARCHAR(100) NOT NULL,
                UNIQUE(platform, platform_username),
                UNIQUE(username, platform),
                CONSTRAINT fk_platform_user
                     FOREIGN KEY (username)
                     REFERENCES users(username)
                     ON DELETE CASCADE
                );
        """)


        # =============================================================
        # MIGRATION FROM users.txt  → leetcode_profiles
        # =============================================================

        # Check if migration already done
        

    engine.dispose()
    print("✅ All tables created + migration complete.")

