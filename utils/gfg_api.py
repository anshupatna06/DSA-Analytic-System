# utils/gfg_api.py
import requests
from bs4 import BeautifulSoup


def fetch_gfg_stats(username: str) -> dict | None:
    """
    Fetch solved problem stats from GeeksforGeeks profile page.
    """

    url = f"https://auth.geeksforgeeks.org/user/{username}/practice/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        solved_tag = soup.find("div", class_="score_card_value")
        total = int(solved_tag.text.strip()) if solved_tag else 0

        return {
            "platform": "gfg",
            "easy_solved": None,     # GFG doesn't split reliably
            "medium_solved": None,
            "hard_solved": None,
            "total_solved": total,
        }

    except Exception:
        return None

