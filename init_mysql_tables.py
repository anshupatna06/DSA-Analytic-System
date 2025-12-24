from database import get_engine

sql = """
CREATE TABLE IF NOT EXISTS dsa_features (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    week INT,
    date VARCHAR(20),
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
"""

engine = get_engine()
with engine.begin() as conn:
    conn.exec_driver_sql(sql)

print("✅ dsa_features table fixed successfully!")

