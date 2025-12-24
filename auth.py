import bcrypt
from sqlalchemy import text
from database import get_engine

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username, password):
    engine = get_engine()
    with engine.begin() as conn:
        try:
            conn.execute(
                text("INSERT INTO users (username, password_hash) VALUES (:u, :p)"),
                {"u": username, "p": hash_password(password)}
            )
            return True, "Account created successfully."
        except Exception as e:
            return False, f"Error: {e}"

def authenticate(username, password):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT * FROM users WHERE username = :u"),
            {"u": username}
        ).fetchone()

    if not row:
        return False, "User not found."
    
    if verify_password(password, row["password_hash"]):
        return True, row
    else:
        return False, "Invalid password."

