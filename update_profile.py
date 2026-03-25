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


def find(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1) if m else "N/A"


print("Downloading pages...")

profile_text = get_text(PROFILE_URL)
history_text = get_text(HISTORY_URL)
strength_text = get_text(STRENGTH_URL)

print("Extracting...")

all_time = find(r"(\d+\s+victories,\s+\d+\s+losses,\s+\d+\.?\d*%\s+win)", history_text)

season = find(r"(2025.?2026.*?\d+\s+victories,\s+\d+\s+losses,\s+\d+\.?\d*%)", history_text)

de_strength = find(r"DE\s+strength\s+(\d+)", strength_text)

pool_strength = find(r"Pool\s+strength\s+(\d+)", strength_text)

stats_html = f"""
<h2>Competitive Snapshot</h2>

<p><b>Season:</b> {season}</p>
<p><b>All time:</b> {all_time}</p>
<p><b>DE strength:</b> {de_strength}</p>
<p><b>Pool strength:</b> {pool_strength}</p>
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

print("Updated")