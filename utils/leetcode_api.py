import requests

BASE_URL = "https://leetcode-stats-api.herokuapp.com"

def fetch_profile_counts(username: str):
    try:
        resp = requests.get(f"{BASE_URL}/{username}", timeout=10)
        if resp.status_code != 200:
            return None

        data = resp.json()
        if "status" in data and data["status"] == "error":
            return None

        return {
            "easy_solved": data.get("easySolved", 0),
            "medium_solved": data.get("mediumSolved", 0),
            "hard_solved": data.get("hardSolved", 0),
            "total_solved": data.get("totalSolved", 0),
        }
    except Exception:
        return None

