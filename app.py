import os
import hashlib
import pandas as pd
import streamlit as st
from sqlalchemy import text

from database import get_engine,init_tables_and_migrate
from create_admin import create_initial_admin
from pipeline.run_pipeline import run_full_pipeline
from pipeline.predict import predict_for_username
from visualize import plot_weekly_progress, plot_growth_curve, plot_user_comparison, plot_difficulty_ratio, plot_weekly_breakdown,plot_hard_density,plot_rolling_growth 
from reset_db import reset_database
# TEMP: run migration once
# TEMP cleanup



init_tables_and_migrate()
# -----------------------------
# Initialize DB & Admin
# -----------------------------
create_initial_admin()

st.set_page_config(
    page_title="DSA Analytics System",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# LOGIN SYSTEM
# -----------------------------
def verify_user(username, password):
    engine = get_engine()

    pwd_hash = hashlib.sha256(password.encode()).hexdigest()

    row = pd.read_sql(
        text("SELECT * FROM users WHERE username = :u"),
        engine,
        params={"u": username}
    )

    engine.dispose()

    if row.empty:
        return None

    user = row.iloc[0]

    if user["password_hash"] == pwd_hash:
        return user

    return None

def signup_screen():
    st.title("🆕 Create an Account")

    new_user = st.text_input("Choose a Username")
    new_pass = st.text_input("Choose a Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if new_pass != confirm_pass:
            st.error("Passwords do not match.")
            return

        engine = get_engine()
        pwd_hash = hashlib.sha256(new_pass.encode()).hexdigest()

        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO users (username, password_hash, is_admin)
                        VALUES (:u, :p, FALSE)
                    """),
                    {"u": new_user, "p": pwd_hash}
                )
            st.success("Account created successfully! Please login now.")
            st.session_state["signup_mode"] = False
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            engine.dispose()


def login_screen():
    st.title("🔐 Login to DSA Analytics")

    if st.session_state.get("signup_mode", False):
        signup_screen()
        return

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = verify_user(username, password)
        if user is not None:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["is_admin"] = bool(user["is_admin"])
            st.rerun()
        else:
            st.error("Incorrect username or password.")

    st.write("")
    st.markdown("Don't have an account?")
    if st.button("👉 Sign Up"):
        st.session_state["signup_mode"] = True
        st.rerun()


# If not logged in → show login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "signup_mode" not in st.session_state:
    st.session_state["signup_mode"] = False


if not st.session_state["logged_in"]:
    login_screen()
    st.stop()


# -----------------------------
# LOGOUT BUTTON
# -----------------------------
st.sidebar.write(f"👤 Logged in as: **{st.session_state['username']}**")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()



# -----------------------------
# CACHED DB LOAD
# -----------------------------
@st.cache_data(ttl=10)
def load_data():
    engine = get_engine()
    try:
        df_data = pd.read_sql("SELECT * FROM dsa_data ORDER BY username, week", engine)
    except:
        df_data = pd.DataFrame()

    try:
        df_feat = pd.read_sql("SELECT * FROM dsa_features ORDER BY username, week", engine)
    except:
        df_feat = pd.DataFrame()

    engine.dispose()
    return df_data, df_feat


# -----------------------------
# MAIN MENU
# -----------------------------
menu = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Leaderboard", "Visual Charts","Advanced Charts", "Predict Next Week","My LeetCode Profile", "Run Pipeline", "Admin Tools"]
)


# -----------------------------
# Dashboard
# -----------------------------
if menu == "Dashboard":
    st.header("📌 User Dashboard")

    df_data, df_feat = load_data()
    if df_feat.empty:
        st.warning("No feature data available.")
    else:
        username = st.selectbox("Select user", df_feat["username"].unique())
        user_df = df_feat[df_feat["username"] == username].sort_values("week")

        st.subheader("📈 Stats")
        st.dataframe(user_df.tail(5))

        st.subheader("📊 Growth Curve")
        st.pyplot(plot_growth_curve(user_df))


# -----------------------------
# Leaderboard
# -----------------------------
elif menu == "Leaderboard":
    st.header("🏆 Leaderboard")

    _, df_feat = load_data()
    if df_feat.empty:
        st.warning("No data.")
    else:
        last_rows = df_feat.groupby("username").tail(1)
        st.dataframe(
            last_rows.sort_values("total_solved", ascending=False)
        )


# -----------------------------
# Visual Charts
# -----------------------------
elif menu == "Visual Charts":
    st.header("📊 Visual Charts")

    _, df_feat = load_data()
    if df_feat.empty:
        st.warning("No data.")
    else:
        username = st.selectbox("Select user", df_feat["username"].unique())
        df = df_feat[df_feat["username"] == username]
        st.pyplot(plot_weekly_progress(df))
        st.pyplot(plot_growth_curve(df))

# -----------------------------
# Advanced Charts (User Comparison + Advanced analytics)
# -----------------------------
elif menu == "Advanced Charts":
    st.header("📊 Advanced Analytics Suite")

    df_data, df_feat = load_data()

    if df_feat.empty:
        st.warning("No feature data available.")
        st.stop()

    users = sorted(df_feat["username"].unique())

    # -----------------------------
    # User Comparison
    # -----------------------------
    st.subheader("👥 Compare Two Users")

    col1, col2 = st.columns(2)
    user1 = col1.selectbox("Select User 1", users, key="adv_user1")
    user2 = col2.selectbox("Select User 2", users, key="adv_user2")

    if user1 == user2:
        st.warning("Please select two different users.")
    else:
        st.pyplot(plot_user_comparison(df_feat, user1, user2))

    st.markdown("---")

    # -----------------------------
    # Difficulty Ratio Chart
    # -----------------------------
    st.subheader("🎯 Difficulty Ratio (Latest Week)")
    current_user = st.selectbox("Select User for Difficulty Chart", users, key="diff_user")

    user_df = df_feat[df_feat["username"] == current_user].sort_values("week")
    st.pyplot(plot_difficulty_ratio(user_df))

    st.markdown("---")

    # -----------------------------
    # Weekly Solved Breakdown
    # -----------------------------
    st.subheader("📦 Weekly Problem Breakdown")
    st.pyplot(plot_weekly_breakdown(user_df))

    st.markdown("---")

    # -----------------------------
    # Hard Problem Density
    # -----------------------------
    st.subheader("🔥 Hard Problem Density Trend")
    st.pyplot(plot_hard_density(user_df))

    st.markdown("---")

    # -----------------------------
    # Rolling Growth
    # -----------------------------
    st.subheader("📈 Rolling 3-Week Growth Trend")
    st.pyplot(plot_rolling_growth(user_df))


# -----------------------------
# Prediction
# -----------------------------
elif menu == "Predict Next Week":
    st.header("🤖 Predict Growth")
    _, df_feat = load_data()

    if df_feat.empty:
        st.warning("No data.")
    else:
        username = st.selectbox("Select user", df_feat["username"].unique())
        if st.button("Predict"):
            pred = predict_for_username(username)
            st.success(f"Prediction: {pred:.2f}")

# -----------------------------
# My LeetCode Profile (User Input)
# -----------------------------
elif menu == "My LeetCode Profile":
    st.header("🧑‍💻 My LeetCode Username")

    engine = get_engine()

    # Fetch current linked username
    existing = pd.read_sql(
        text("SELECT leetcode_username FROM leetcode_profiles WHERE username = :u"),
        engine,
        params={"u": st.session_state["username"]}
    )

    current_un = None
    if not existing.empty:
        current_un = existing.iloc[0]["leetcode_username"]

    st.write("### Linked LeetCode Username:")
    if current_un:
        st.success(f"Linked: **{current_un}**")
    else:
        st.info("No LeetCode username linked yet.")

    new_un = st.text_input("Enter / Update LeetCode username:")

    if st.button("Save Username"):
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO leetcode_profiles (username, leetcode_username)
                        VALUES (:u, :lu)
                        ON DUPLICATE KEY UPDATE leetcode_username = :lu
                    """),
                    {"u": st.session_state["username"], "lu": new_un}
                )
            st.success("LeetCode username updated successfully!")
            st.cache_data.clear()
        except Exception as e:
            st.error(str(e))

    if current_un:
        if st.button("Remove Username"):
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("DELETE FROM leetcode_profiles WHERE username = :u"),
                        {"u": st.session_state["username"]}
                    )
                st.success("LeetCode username removed.")
                st.cache_data.clear()
            except Exception as e:
                st.error(str(e))

    engine.dispose()



# -----------------------------
# Run Pipeline (Admin Only)
# -----------------------------
elif menu == "Run Pipeline":
    st.header("🔄 Run Full Pipeline")

    if not st.session_state["is_admin"]:
        st.error("Admin access required.")
        st.stop()

    if st.button("Run Now"):
        with st.spinner("Running pipeline..."):
            try:
                run_full_pipeline()
                st.success("Pipeline completed!")
                st.cache_data.clear()
            except Exception as e:
                st.error(str(e))


# -----------------------------
# Admin Tools
# -----------------------------
elif menu == "Admin Tools":
    st.header("⚙ Admin Tools")

    if not st.session_state["is_admin"]:
        st.error("Admin access required.")
        st.stop()

    st.subheader("Add New User")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    make_admin = st.checkbox("Make Admin?")

    if st.button("Create User"):
        engine = get_engine()
        pwd_hash = hashlib.sha256(new_pass.encode()).hexdigest()

        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO users (username, password_hash, is_admin)
                        VALUES (:u, :p, :a)
                    """),
                    {"u": new_user, "p": pwd_hash, "a": make_admin}
                )
            st.success("User created!")
        except Exception as e:
            st.error(str(e))
        finally:
            engine.dispose()

    st.subheader("Reset All Data")

    if st.button("RESET DATABASE NOW"):
        reset_database()
        st.success("Database cleared!")

