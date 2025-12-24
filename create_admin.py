# create_admin.py
import os
from sqlalchemy import text
from database import get_engine
import hashlib

def create_initial_admin():
    engine = get_engine()

    admin_username = os.getenv("ADMIN_USERNAME", "anshu")
    admin_password = os.getenv("ADMIN_PASSWORD", "radhe radhe")

    # Hash password
    pwd_hash = hashlib.sha256(admin_password.encode()).hexdigest()

    with engine.begin() as conn:
        # Check if admin exists
        result = conn.execute(
            text("SELECT id FROM users WHERE username = :u"),
            {"u": admin_username}
        ).fetchone()

        if result:
            print("Admin already exists.")
            return

        # Insert admin
        conn.execute(
            text("""
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (:u, :p, TRUE)
            """),
            {"u": admin_username, "p": pwd_hash}
        )

    engine.dispose()
    print("✅ Initial admin user created!")

