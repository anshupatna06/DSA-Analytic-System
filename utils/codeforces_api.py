# utils/codeforces_api.py
import requests


def fetch_codeforces_stats(handle: str) -> dict | None:
    """
    Fetch solved problem stats from Codeforces API.
    """

    url = f"https://codeforces.com/api/user.status?handle={handle}"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        if data["status"] != "OK":
            return None

        solved = set()
        for sub in data["result"]:
            if sub.get("verdict") == "OK":
                solved.add((sub["problem"]["contestId"], sub["problem"]["index"]))

        return {
            "platform": "codeforces",
            "easy_solved": None,     # CF difficulty ≠ easy/medium/hard
            "medium_solved": None,
            "hard_solved": None,
            "total_solved": len(solved),
        }

    except Exception:
        return None

