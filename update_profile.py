import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROFILE_URL = "https://fencingtracker.com/p/100316536/Lillian-Wen"
HISTORY_URL = "https://fencingtracker.com/p/100316536/Lillian-Wen/history"
STRENGTH_URL = "https://fencingtracker.com/p/100316536/Lillian-Wen/strength"


def get_text(url: str) -> str:
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(" ", strip=True)


def find(pattern: str, text: str, default: str = "N/A") -> str:
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return default


def parse_history_stats(history_text: str) -> tuple[str, str]:
    # Match the table rows directly:
    # Victories 148 83 - - - 231
    # Losses 69 64 - - - 133
    # Win Ratio 68.2% 56.5% - - - 63.5%
    victories_match = re.search(
        r"Victories\s+(\d+)\s+\d+\s+[-\d]+\s+[-\d]+\s+[-\d]+\s+(\d+)",
        history_text,
        re.IGNORECASE,
    )
    losses_match = re.search(
        r"Losses\s+(\d+)\s+\d+\s+[-\d]+\s+[-\d]+\s+[-\d]+\s+(\d+)",
        history_text,
        re.IGNORECASE,
    )
    win_ratio_match = re.search(
        r"Win Ratio\s+(\d+\.?\d*%)\s+\d+\.?\d*%\s+[-\d.%]+\s+[-\d.%]+\s+[-\d.%]+\s+(\d+\.?\d*%)",
        history_text,
        re.IGNORECASE,
    )

    if victories_match and losses_match and win_ratio_match:
        season = f"{victories_match.group(1)} victories, {losses_match.group(1)} losses, {win_ratio_match.group(1)} win ratio"
        all_time = f"{victories_match.group(2)} victories, {losses_match.group(2)} losses, {win_ratio_match.group(2)} win ratio"
        return season, all_time

    return "N/A", "N/A"


def main() -> None:
    print("Downloading pages...")

    profile_text = get_text(PROFILE_URL)
    history_text = get_text(HISTORY_URL)
    strength_text = get_text(STRENGTH_URL)

    print("Saving debug files...")
    Path("history_debug.txt").write_text(history_text, encoding="utf-8")
    Path("strength_debug.txt").write_text(strength_text, encoding="utf-8")

    print("Extracting...")

    name = "Lillian Wen"
    birth_year = find(r"\b(2015)\b", profile_text)
    club = find(r"(Gold Fencing Club)", profile_text)
    weapon = "Foil"

    season, all_time = parse_history_stats(history_text)

    de_strength = find(r"DE[^0-9]{0,50}(\d{3,4})", strength_text)
    pool_strength = find(r"Pool[^0-9]{0,50}(\d{3,4})", strength_text)

    print("Season:", season)
    print("All Time:", all_time)
    print("DE strength:", de_strength)
    print("Pool strength:", pool_strength)

    stats_html = f"""
<h2>Profile</h2>

<div class="profile-table">
    <div class="profile-label">Name</div>
    <div class="profile-value">{name}</div>

    <div class="profile-label">Birth Year</div>
    <div class="profile-value">{birth_year}</div>

    <div class="profile-label">Club</div>
    <div class="profile-value">{club}</div>

    <div class="profile-label">Weapon</div>
    <div class="profile-value">{weapon}</div>
</div>

<h2>Competitive Snapshot</h2>

<div class="profile-table">
    <div class="profile-label">Season</div>
    <div class="profile-value">{season}</div>

    <div class="profile-label">All Time</div>
    <div class="profile-value">{all_time}</div>

    <div class="profile-label">DE Strength</div>
    <div class="profile-value">{de_strength}</div>

    <div class="profile-label">Pool Strength</div>
    <div class="profile-value">{pool_strength}</div>
</div>
"""

    profile_path = Path("profile.html")
    html = profile_path.read_text(encoding="utf-8")

    updated_html = re.sub(
        r"<!-- PROFILE_STATS_START -->.*?<!-- PROFILE_STATS_END -->",
        f"<!-- PROFILE_STATS_START -->\n{stats_html}\n<!-- PROFILE_STATS_END -->",
        html,
        flags=re.DOTALL,
    )

    profile_path.write_text(updated_html, encoding="utf-8")

    print("Updated profile.html")
    print("Done.")


if __name__ == "__main__":
    main()