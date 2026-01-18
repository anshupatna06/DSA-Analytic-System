# migrate_week_logic.py
from sqlalchemy import text
from database import get_engine


def migrate_week_start_date():
    engine = get_engine()

    with engine.begin() as conn:

        # 1️⃣ Add column if missing
        try:
            conn.exec_driver_sql("""
                ALTER TABLE dsa_data
                ADD COLUMN week_start_date DATE
            """)
            print("✅ week_start_date column added")
        except Exception:
            print("ℹ️ week_start_date already exists")

        # 2️⃣ Backfill week_start_date (PostgreSQL syntax)
        conn.exec_driver_sql("""
            UPDATE dsa_data d
            SET week_start_date = w.min_date
            FROM (
                SELECT
                    username,
                    week,
                    MIN(date::DATE) AS min_date
                FROM dsa_data
                GROUP BY username, week
            ) w
            WHERE d.username = w.username
              AND d.week = w.week
        """)
        print("✅ week_start_date backfilled")

        # 3️⃣ Enforce NOT NULL
        try:
            conn.exec_driver_sql("""
                ALTER TABLE dsa_data
                ALTER COLUMN week_start_date SET NOT NULL
            """)
            print("✅ week_start_date locked")
        except Exception:
            pass

    engine.dispose()
    print("🎯 Week migration completed successfully")


if __name__ == "__main__":
    migrate_week_start_date()

