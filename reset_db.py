from database import get_engine

def reset_database():
    engine = get_engine()

    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM dsa_data;")
        conn.exec_driver_sql("DELETE FROM dsa_features;")
        conn.exec_driver_sql("ALTER TABLE dsa_data AUTO_INCREMENT = 1;")
        conn.exec_driver_sql("ALTER TABLE dsa_features AUTO_INCREMENT = 1;")

    engine.dispose()
    return "✔ All data cleared successfully!"
