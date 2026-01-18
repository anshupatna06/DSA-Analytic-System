# utils/aggregator.py

from utils.leetcode_api import fetch_profile_counts
# (future)
from utils.codeforces_api import fetch_codeforces_stats
from utils.gfg_api import fetch_gfg_stats
from utils.hackerrank_api import fetch_hackerrank_stats


def fetch_all_platform_stats(platform: str, username: str):
    """
    Unified stats fetcher for all coding platforms
    Returns a dict with:
    easy_solved, medium_solved, hard_solved, total_solved
    """

    platform = platform.lower()

    if platform == "leetcode":
        return fetch_profile_counts(username)

    # ---- future-ready stubs ----
    elif platform == "codeforces":
         return fetch_codeforces_stats(username)
    
    elif platform == "gfg":
         return fetch_gfg_stats(username)
    
    elif platform == "hackerrank":
         return fetch_hackerrank_stats(username)

    else:
        raise ValueError(f"Unsupported platform: {platform}")
