import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

PROFILE_URL = "https://fencingtracker.com/p/100316536/Lillian-Wen"
HISTORY_URL = "https://fencingtracker.com/p/100316536/Lillian-Wen/history"
STRENGTH_URL = "https://fencingtracker.com/p/100316536/Lillian-Wen/strength"


def get_text(url):
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.get_text(" ", strip=True)


def extract_history_stats(history_text):
    victories_match = re.search(
        r"Victories\s+(\d+)\s+\d+\s+-\s+-\s+-\s+(\d+)",
        history_text,
        re.IGNORECASE,
    )
    losses_match = re.search(
        r"Losses\s+(\d+)\s+\d+\s+-\s+-\s+-\s+(\d+)",
        history_text,
        re.IGNORECASE,
    )
    win_ratio_match = re.search(
        r"Win Ratio\s+([\d.]+%)\s+[\d.]+%\s+-\s+-\s+-\s+([\d.]+%)",
        history_text,
        re.IGNORECASE,
    )

    season_victories = victories_match.group(1) if victories_match else "N/A"
    all_time_victories = victories_match.group(2) if victories_match else "N/A"

    season_losses = losses_match.group(1) if losses_match else "N/A"
    all_time_losses = losses_match.group(2) if losses_match else "N/A"

    season_ratio = win_ratio_match.group(1) if win_ratio_match else "N/A"
    all_time_ratio = win_ratio_match.group(2) if win_ratio_match else "N/A"

    return {
        "season_record": f"{season_victories}-{season_losses} ({season_ratio})",
        "all_time_record": f"{all_time_victories}-{all_time_losses} ({all_time_ratio})",
    }


def extract_strength_stats(strength_text):
    de_match = re.search(r"Foil\s+DE\s+(\d+)", strength_text, re.IGNORECASE)
    pool_match = re.search(r"Foil\s+Pool\s+(\d+)", strength_text, re.IGNORECASE)

    return {
        "de_strength": de_match.group(1) if de_match else "N/A",
        "pool_strength": pool_match.group(1) if pool_match else "N/A",
    }


def main():
    print("Downloading pages...")

    profile_text = get_text(PROFILE_URL)
    history_text = get_text(HISTORY_URL)
    strength_text = get_text(STRENGTH_URL)

    print("Extracting...")

    history_stats = extract_history_stats(history_text)
    strength_stats = extract_strength_stats(strength_text)

    stats_html = f"""
<h2>Competitive Snapshot</h2>
<p><b>Birth Year:</b> 2015</p>
<p><b>Club:</b> Gold Fencing Club</p>
<p><b>Weapon:</b> Women's Foil</p>
<p><b>Season:</b> {history_stats['season_record']}</p>
<p><b>All time:</b> {history_stats['all_time_record']}</p>
<p><b>DE strength:</b> {strength_stats['de_strength']}</p>
<p><b>Pool strength:</b> {strength_stats['pool_strength']}</p>
"""

    path = Path("profile.html")
    html = path.read_text(encoding="utf-8")

    html = re.sub(
        r"<!-- PROFILE_STATS_START -->.*?<!-- PROFILE_STATS_END -->",
        f"<!-- PROFILE_STATS_START -->\n{stats_html}\n<!-- PROFILE_STATS_END -->",
        html,
        flags=re.S,
    )

    path.write_text(html, encoding="utf-8")
    print("Updated profile.html")


if __name__ == "__main__":
    main()