# pipeline/fetch_data.py

import datetime as dt
from sqlalchemy import text

from database import get_engine
from utils.aggregator import fetch_all_platform_stats


def fetch_profiles_from_db(conn):
    """
    Fetch platform usernames from platform_profiles.
    Currently supports only 'leetcode'.
    """
    rows = conn.execute(
        text("""
            SELECT username, platform, platform_username
            FROM platform_profiles
            WHERE platform = 'leetcode'
        """)
    ).mappings().all()

    return rows


def run_fetch():
    today_dt = dt.datetime.utcnow()
    today_date = today_dt.date()
    today = today_date.strftime("%Y-%m-%d")

    # 🔴 retention window (30 days)
    retention_cutoff = (today_date - dt.timedelta(days=30)).strftime("%Y-%m-%d")

    engine = get_engine()

    with engine.begin() as conn:

        # =====================================================
        # 🔴 AUTO-CLEANUP (30 DAYS)
        # =====================================================
        deleted_data = conn.execute(
            text("DELETE FROM dsa_data WHERE date < :cutoff"),
            {"cutoff": retention_cutoff}
        ).rowcount

        deleted_features = conn.execute(
            text("DELETE FROM dsa_features WHERE date < :cutoff"),
            {"cutoff": retention_cutoff}
        ).rowcount

        print(
            f"[cleanup] Removed {deleted_data} rows from dsa_data, "
            f"{deleted_features} from dsa_features"
        )

        # =====================================================
        # LOAD PLATFORM PROFILES
        # =====================================================
        profiles = fetch_profiles_from_db(conn)

        if not profiles:
            print("[fetch] No platform profiles found.")
            return

        # =====================================================
        # PROCESS EACH PROFILE
        # =====================================================
        for row in profiles:
            platform = row["platform"]
            platform_username = row["platform_username"]

            # -------------------------------------------
            # 1️⃣ Fetch stats
            # -------------------------------------------
            stats = fetch_all_platform_stats(platform, platform_username)
            if not stats:
                print(f"[fetch] Failed for {platform_username}")
                continue

            # -------------------------------------------
            # 2️⃣ Fetch LAST ROW (for week logic)
            # -------------------------------------------
            last_row = conn.execute(
                text("""
                    SELECT week, week_start_date
                    FROM dsa_data
                    WHERE username = :u
                    ORDER BY id DESC
                    LIMIT 1
                """),
                {"u": platform_username}
            ).mappings().first()

            if last_row:
                last_week = last_row["week"]
                week_start = last_row["week_start_date"]

                days_since_week_start = (today_date - week_start).days

                if days_since_week_start >= 7:
                    next_week = last_week + 1
                    new_week_start = today_date
                else:
                    next_week = last_week
                    new_week_start = week_start
            else:
                next_week = 1
                new_week_start = today_date

            # -------------------------------------------
            # 3️⃣ Check if TODAY already exists
            # -------------------------------------------
            today_row = conn.execute(
                text("""
                    SELECT id
                    FROM dsa_data
                    WHERE username = :u AND date = :d
                """),
                {"u": platform_username, "d": today}
            ).mappings().first()

            # -------------------------------------------
            # 4️⃣ UPDATE if exists, else INSERT
            # -------------------------------------------
            if today_row:
                conn.execute(
                    text("""
                        UPDATE dsa_data
                        SET
                            week = :w,
                            week_start_date = :ws,
                            easy_solved = :e,
                            medium_solved = :m,
                            hard_solved = :h,
                            total_solved = :t
                        WHERE id = :id
                    """),
                    {
                        "w": next_week,
                        "ws": new_week_start,
                        "e": stats["easy_solved"],
                        "m": stats["medium_solved"],
                        "h": stats["hard_solved"],
                        "t": stats["total_solved"],
                        "id": today_row["id"],
                    }
                )
                print(f"[fetch] Updated week {next_week} → {platform_username}")

            else:
                conn.execute(
                    text("""
                        INSERT INTO dsa_data
                        (username, week, week_start_date, date,
                         easy_solved, medium_solved, hard_solved, total_solved)
                        VALUES
                        (:u, :w, :ws, :d, :e, :m, :h, :t)
                    """),
                    {
                        "u": platform_username,
                        "w": next_week,
                        "ws": new_week_start,
                        "d": today,
                        "e": stats["easy_solved"],
                        "m": stats["medium_solved"],
                        "h": stats["hard_solved"],
                        "t": stats["total_solved"],
                    }
                )
                print(f"[fetch] Inserted week {next_week} → {platform_username}")

    engine.dispose()

