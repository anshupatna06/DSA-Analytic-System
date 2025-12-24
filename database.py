# database.py
import os
import pymysql
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

pymysql.install_as_MySQLdb()


def get_engine():
    host = os.getenv("MYSQLHOST")
    user = os.getenv("MYSQLUSER")
    password = os.getenv("MYSQLPASSWORD")
    port = os.getenv("MYSQLPORT")
    db = os.getenv("MYSQLDATABASE")

    if not all([host, user, password, port, db]):
        raise RuntimeError("MySQL environment variables missing!")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, pool_recycle=3600, pool_pre_ping=True)


def init_tables_and_migrate():
    engine = get_engine()

    with engine.begin() as conn:

        # =============================================================
        # BASE TABLE: dsa_data
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS dsa_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                week INT,
                easy_solved INT,
                medium_solved INT,
                hard_solved INT,
                total_solved INT
            );
        """)

        # Add date column
        try:
            conn.exec_driver_sql("ALTER TABLE dsa_data ADD COLUMN date VARCHAR(20)")
        except OperationalError:
            pass

        # =============================================================
        # dsa_features
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS dsa_features (
                id INT AUTO_INCREMENT PRIMARY KEY,
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

        try:
            conn.exec_driver_sql("ALTER TABLE dsa_features ADD COLUMN date VARCHAR(20)")
        except OperationalError:
            pass

        # =============================================================
        # LOGIN USERS TABLE
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE,
                password_hash VARCHAR(200),
                is_admin BOOLEAN DEFAULT FALSE
            );
        """)

        # =============================================================
        # NEW TABLE: leetcode_profiles  (username → leetcode_username)
        # =============================================================
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS leetcode_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                leetcode_username VARCHAR(100) NOT NULL,
                UNIQUE(username),
                UNIQUE(leetcode_username),
                CONSTRAINT fk_user
                      FOREIGN KEY (username)
                      REFERENCES users(username)
                      ON DELETE CASCADE
                );
        """)

        # =============================================================
        # MIGRATION FROM users.txt  → leetcode_profiles
        # =============================================================

        # Check if migration already done
        result = conn.execute(text("SELECT COUNT(*) AS cnt FROM leetcode_profiles")).mappings().first()
        if result["cnt"] == 0:

            USERS_FILE = "data/users.txt"

            if os.path.exists(USERS_FILE):
                try:
                    with open(USERS_FILE, "r") as f:
                        for line in f:
                            username = line.strip()
                            if username:
                                conn.execute(
                                    text("""
                                        INSERT IGNORE INTO leetcode_profiles (app_username, leetcode_username)
                                        VALUES (:u, :u)
                                    """),
                                    {"u": username}
                                )
                    print("✅ Migrated users.txt → leetcode_profiles")
                except Exception as e:
                    print("⚠️ Migration failed:", e)
            else:
                print("ℹ️ No users.txt found, skipping migration.")

    engine.dispose()
    print("✅ All tables created + migration complete.")

