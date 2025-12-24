# pipeline/fetch_data.py

import datetime as dt
from sqlalchemy import text
from database import get_engine
from utils.leetcode_api import fetch_profile_counts


def fetch_usernames_from_db(conn):
    """Fetch leetcode usernames from MySQL instead of users.txt."""
    rows = conn.execute(
        text("SELECT leetcode_username FROM leetcode_profiles")
    ).fetchall()

    return [r[0] for r in rows if r[0]]


def run_fetch():
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    today_dt = dt.datetime.strptime(today, "%Y-%m-%d")

    # 🔴 retention window (30 days)
    retention_cutoff = (today_dt - dt.timedelta(days=30)).strftime("%Y-%m-%d")

    engine = get_engine()

    with engine.begin() as conn:

        # =====================================================
        # 🔴 AUTO-CLEANUP: DELETE DATA OLDER THAN 30 DAYS
        # =====================================================
        deleted_data = conn.execute(
            text("""
                DELETE FROM dsa_data
                WHERE date < :cutoff
            """),
            {"cutoff": retention_cutoff}
        ).rowcount

        deleted_features = conn.execute(
            text("""
                DELETE FROM dsa_features
                WHERE date < :cutoff
            """),
            {"cutoff": retention_cutoff}
        ).rowcount

        print(
            f"[cleanup] Removed {deleted_data} old rows from dsa_data, "
            f"{deleted_features} from dsa_features"
        )

        # =====================================================
        # LOAD USERNAMES
        # =====================================================
        users = fetch_usernames_from_db(conn)
        if not users:
            print("[fetch] No usernames found in leetcode_profiles.")
            return

        # =====================================================
        # PROCESS EACH USER
        # =====================================================
        for u in users:

            # -- 1️⃣ Skip if today's snapshot already exists
            existing = conn.execute(
                text("""
                    SELECT id FROM dsa_data
                    WHERE username = :u AND date = :d
                """),
                {"u": u, "d": today}
            ).fetchone()

            if existing:
                print(f"[fetch] Already logged today → {u}")
                continue

            # -- 2️⃣ Fetch LeetCode stats
            stats = fetch_profile_counts(u)
            if not stats:
                print(f"[fetch] Failed to fetch data for {u}")
                continue

            # -- 3️⃣ Determine correct week number
            last_row = conn.execute(
                text("""
                    SELECT week, date FROM dsa_data
                    WHERE username = :u
                    ORDER BY id DESC LIMIT 1
                """),
                {"u": u}
            ).mappings().first()

            if last_row:
                last_week = last_row["week"]
                last_date = dt.datetime.strptime(last_row["date"], "%Y-%m-%d")
                days_passed = (today_dt - last_date).days

                next_week = last_week + 1 if days_passed >= 7 else last_week
            else:
                next_week = 1  # First entry ever

            # -- 4️⃣ Insert today's snapshot
            conn.execute(
                text("""
                    INSERT INTO dsa_data
                    (username, week, date, easy_solved, medium_solved, hard_solved, total_solved)
                    VALUES (:u, :w, :d, :e, :m, :h, :t)
                """),
                {
                    "u": u,
                    "w": next_week,
                    "d": today,
                    "e": stats["easy_solved"],
                    "m": stats["medium_solved"],
                    "h": stats["hard_solved"],
                    "t": stats["total_solved"],
                }
            )

            print(f"[fetch] Inserted week {next_week} → {u}")

    engine.dispose()

