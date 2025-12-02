#!/usr/bin/env python3
import csv
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEATS_REF = ROOT / "data" / "seats_reference.csv"

WIKI_API = "https://en.wikipedia.org/w/api.php"

def guess_wiki_title(icao: str) -> str:
    """
    Very naive: map some common ICAOs to canonical page titles.
    You can expand this mapping as needed.
    """
    icao = icao.upper()
    mapping = {
        "A320": "Airbus A320 family",
        "A319": "Airbus A320 family",
        "A321": "Airbus A320 family",
        "B738": "Boeing 737 Next Generation",
        "B739": "Boeing 737 Next Generation",
        "B752": "Boeing 757",
        "B753": "Boeing 757",
        "B77W": "Boeing 777",
        "B789": "Boeing 787 Dreamliner",
        "A359": "Airbus A350 XWB",
        "A388": "Airbus A380",
        "B744": "Boeing 747",
    }
    return mapping.get(icao, icao)

def fetch_wiki_html(title: str) -> str:
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "redirects": 1
    }
    r = requests.get(WIKI_API, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    html = data["parse"]["text"]["*"]
    return html

def extract_capacity(html: str) -> int | None:
    """
    Try to find an integer 'seats' value from the infobox.
    This is intentionally basic and may need tuning by type.
    """
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        return None

    text = infobox.get_text(" ", strip=True)
    # Look for 'Capacity' or 'Passengers' lines
    m = re.search(r"(Capacity|Passengers)[^0-9]*([0-9]{2,3})", text)
    if m:
        return int(m.group(2))
    return None

def main():
    rows = []
    with SEATS_REF.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        rows = list(rd)

    updated = 0

    for row in rows:
        icao = row["icao"].strip().upper()
        seats = row.get("seats", "").strip()

        if seats:
            continue  # already has value

        title = guess_wiki_title(icao)
        print(f"[scrape] {icao}: trying Wikipedia page '{title}'")
        try:
            html = fetch_wiki_html(title)
            cap = extract_capacity(html)
        except Exception as e:
            print(f"  -> error: {e}")
            continue

        if cap:
            print(f"  -> found capacity ~{cap}")
            row["seats"] = str(cap)
            if not row.get("class"):
                row["class"] = "L2J"
            updated += 1
        else:
            print("  -> no capacity found")

    if updated:
        print(f"[scrape] Writing updated CSV with {updated} new seat values")
        with SEATS_REF.open("w", newline="", encoding="utf-8") as f:
            fieldnames = ["icao", "seats", "class"]
            wr = csv.DictWriter(f, fieldnames=fieldnames)
            wr.writeheader()
            wr.writerows(rows)
    else:
        print("[scrape] No rows updated")

if __name__ == "__main__":
    main()
