# DSA Analytics System

End-to-End Learning Analytics Platform for Competitive Programming

A production-style analytics system that ingests real coding-platform data, engineers learning behavior features, detects performance drift, and provides actionable insights through an interactive dashboard.

This project was built to go beyond simple problem counts and instead model learning consistency, stagnation, and performance drops over time.

# 🔍 What Problem Does This Solve?

Most competitive programmers track only:

Total problems solved

Daily streaks

This system answers deeper questions:

Am I improving consistently or stagnating?

Did my learning pace suddenly drop?

Am I inactive despite a high total score?

How does my weekly learning trend evolve?

# 🚀 Core Features
📥 Multi-Platform Data Ingestion

Supports LeetCode (extensible to GFG, Codeforces, HackerRank)

Daily snapshots with deduplication

Platform-agnostic aggregation layer

# 🧠 Feature Engineering on Learning Behavior

Weekly growth & rolling averages

Difficulty ratios (easy / medium / hard)

Consistency & balance scores

Inactivity tracking across weeks

# 🚨 Performance Drift Detection

Detects learning issues using:

Sudden drops in weekly growth

Consistent decline over consecutive weeks

Inactivity drift (no progress despite past activity)

Each drift event is stored with a human-readable reason.

# 🤖 Machine Learning Prediction

Predicts next-week growth using historical behavior

Trained on engineered learning features

Designed for extensibility to advanced models

# 📊 Interactive Analytics Dashboard

User-level dashboards

Leaderboard & comparison views

Drift alerts and trend visualizations

Built with Streamlit

# 🔐 Secure Authentication & User Profiles

User login system

Multi-platform profile linking

Admin-controlled pipeline execution

# 🏗️ System Architecture
Platform APIs
     ↓
Daily Data Ingestion
     ↓
PostgreSQL (Snapshots)
     ↓
Feature Engineering Pipeline
     ↓
Drift Detection + ML Prediction
     ↓
Interactive Streamlit Dashboard


Designed with production safety in mind:

Idempotent ingestion

Safe database migrations

Retention-aware cleanup

Modular pipeline stages

# 🧰 Tech Stack

Language: Python

Data: Pandas, NumPy

Database: PostgreSQL

ORM: SQLAlchemy

ML: Scikit-learn

Dashboard: Streamlit

Deployment: Hugging Face Spaces

# 🌐 Live Demo

👉 https://huggingface.co/spaces/anshupatna06/dsa-analytic-system

# 📌 Key Learnings & Engineering Highlights

Designed real-world data pipelines, not toy scripts

Handled database migrations across MySQL → PostgreSQL

Built drift logic inspired by production ML monitoring

Learned system-level debugging (data consistency, time windows, schema evolution)

Balanced ML modeling with practical analytics

# 🔮 Future Improvements

Full support for GFG, Codeforces, HackerRank

Advanced drift thresholds & alert tuning

Personalized learning recommendations

Model explainability for predictions

# ⚠️ Project Status

Actively maintained and iterated.
Built as a learning-to-production bridge, not a one-off demo.
