from pathlib import Path

path = Path("profile.html")
html = path.read_text(encoding="utf-8")

html = html.replace(
    "</body>",
    "\n<!-- auto-update test -->\n</body>"
)

path.write_text(html, encoding="utf-8")
print("profile.html updated")