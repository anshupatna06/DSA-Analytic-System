import matplotlib.pyplot as plt
import numpy as np

plt.style.use("ggplot")


# ----------------------------------------------------------
# 1️⃣ Weekly Total Solved (Your Original Chart - kept same)
# ----------------------------------------------------------
def plot_weekly_progress(df):
    fig, ax = plt.subplots(figsize=(6, 3))

    if df.empty:
        ax.text(0.5, 0.5, "No data available",
                ha="center", va="center", fontsize=11)
        ax.axis("off")
        return fig

    ax.plot(df["week"], df["total_solved"],
            marker="o", linewidth=1.5, markersize=5)

    ax.set_title("Weekly Total Solved", fontsize=12)
    ax.set_xlabel("Week")
    ax.set_ylabel("Total Solved")
    ax.grid(True, linewidth=0.3)

    fig.tight_layout()
    return fig


# ----------------------------------------------------------
# 2️⃣ Weekly Growth (Your Original Chart - kept same)
# ----------------------------------------------------------
def plot_growth_curve(df):
    fig, ax = plt.subplots(figsize=(6, 3))

    if df.empty or "weekly_growth" not in df.columns:
        ax.text(0.5, 0.5, "No growth data available",
                ha="center", va="center", fontsize=11)
        ax.axis("off")
        return fig

    ax.plot(df["week"], df["weekly_growth"],
            marker="s", linewidth=1.6, markersize=5,
            color="#2C82C9")

    ax.set_title("Weekly Growth", fontsize=12)
    ax.set_xlabel("Week")
    ax.set_ylabel("Growth")
    ax.grid(True, linewidth=0.3)

    fig.tight_layout()
    return fig


# ----------------------------------------------------------
# 3️⃣ Difficulty Ratio Donut Chart
# ----------------------------------------------------------
def plot_difficulty_ratio(df):
    fig, ax = plt.subplots(figsize=(4.5, 4))

    if df.empty:
        ax.text(0.5, 0.5, "No ratio data", ha="center", va="center")
        ax.axis("off")
        return fig

    last = df.iloc[-1]

    values = [
        float(last["easy_ratio"]),
        float(last["medium_ratio"]),
        float(last["hard_ratio"])
    ]

    labels = ["Easy", "Medium", "Hard"]
    colors = ["#6ECF68", "#FFD44F", "#FF6B6B"]

    wedges, _, _ = ax.pie(values, labels=labels, startangle=90,
                          autopct='%1.1f%%', colors=colors, pctdistance=0.78)

    # donut hole
    centre = plt.Circle((0, 0), 0.50, color="white")
    fig.gca().add_artist(centre)

    ax.set_title("Difficulty Ratio (Latest Week)", fontsize=12)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------
# 4️⃣ Weekly Breakdown Bar Chart (easy/medium/hard)
# ----------------------------------------------------------
def plot_weekly_breakdown(df):
    fig, ax = plt.subplots(figsize=(6, 3.3))

    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        ax.axis("off")
        return fig

    weeks = df["week"]
    ax.bar(weeks - 0.2, df["easy_solved"], width=0.2, label="Easy")
    ax.bar(weeks, df["medium_solved"], width=0.2, label="Medium")
    ax.bar(weeks + 0.2, df["hard_solved"], width=0.2, label="Hard")

    ax.set_title("Weekly Problem Breakdown", fontsize=12)
    ax.set_xlabel("Week")
    ax.set_ylabel("Count")
    ax.legend()
    fig.tight_layout()
    return fig


# ----------------------------------------------------------
# 5️⃣ Hard Problem Density Trend
# ----------------------------------------------------------
def plot_hard_density(df):
    fig, ax = plt.subplots(figsize=(6, 3))

    if df.empty:
        ax.text(0.5, 0.5, "No density data", ha="center", va="center")
        ax.axis("off")
        return fig

    ax.plot(df["week"], df["hard_problem_density"], marker="o",
            markersize=5, linewidth=1.4, color="#D9534F")

    ax.set_title("Hard Problem Density Trend", fontsize=12)
    ax.set_xlabel("Week")
    ax.set_ylabel("Density")
    ax.grid(True, linewidth=0.3)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------
# 6️⃣ Rolling 3-Week Growth Trend
# ----------------------------------------------------------
def plot_rolling_growth(df):
    fig, ax = plt.subplots(figsize=(6, 3))

    if df.empty:
        ax.text(0.5, 0.5, "No rolling data", ha="center", va="center")
        ax.axis("off")
        return fig

    ax.plot(df["week"], df["rolling_growth_3week"],
            marker="d", linewidth=1.5, markersize=5,
            color="#8A2BE2")

    ax.set_title("Rolling 3-Week Growth", fontsize=12)
    ax.set_xlabel("Week")
    ax.set_ylabel("Avg Growth")
    ax.grid(True, linewidth=0.3)
    fig.tight_layout()
    return fig
# ----------------------------------------------------------
# 7️⃣ User Comparison Chart (Growth comparison)
# ----------------------------------------------------------
def plot_user_comparison(df, user1, user2):
    fig, ax = plt.subplots(figsize=(7, 3.5))

    df1 = df[df["username"] == user1]
    df2 = df[df["username"] == user2]

    if df1.empty or df2.empty:
        ax.text(0.5, 0.5, "Not enough data for comparison",
                ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    ax.plot(df1["week"], df1["weekly_growth"], marker="o",
            label=f"{user1} Growth", linewidth=1.5)

    ax.plot(df2["week"], df2["weekly_growth"], marker="s",
            label=f"{user2} Growth", linewidth=1.5)

    ax.set_title("📈 User Growth Comparison", fontsize=13)
    ax.set_xlabel("Week")
    ax.set_ylabel("Weekly Growth")
    ax.legend()
    ax.grid(True, linewidth=0.3)

    fig.tight_layout()
    return fig

