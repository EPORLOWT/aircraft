#!/usr/bin/env python3
import csv
import os
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AIRLINES_CSV = ROOT / "data" / "airlines.csv"
LOGO_DIR = ROOT / "logos"

WIKI_API = "https://en.wikipedia.org/w/api.php"

LOGO_DIR.mkdir(exist_ok=True)

def fetch_logo_filename(page: str) -> str | None:
    params = {
        "action": "query",
        "prop": "pageimages",
        "piprop": "original",
        "titles": page,
        "format": "json"
    }
    r = requests.get(WIKI_API, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    pages = data.get("query", {}).get("pages", {})
    for _, p in pages.items():
        if "original" in p:
            return p["original"]["source"]
    return None

def download_logo(url: str, out_path: Path):
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()
    with out_path.open("wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

def main():
    with AIRLINES_CSV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            icao = row["icao"].strip().upper()
            wiki_page = row["wiki_page"].strip()
            if not icao or not wiki_page:
                continue

            out_file = LOGO_DIR / f"{icao}.png"
            if out_file.exists():
                print(f"[logos] {icao}: already exists, skipping")
                continue

            print(f"[logos] {icao}: fetching logo from '{wiki_page}'")
            try:
                url = fetch_logo_filename(wiki_page)
                if not url:
                    print("  -> no logo found in pageimages")
                    continue
                print(f"  -> logo url: {url}")
                download_logo(url, out_file)
                print(f"  -> saved to {out_file}")
            except Exception as e:
                print(f"  -> error: {e}")

if __name__ == "__main__":
    main()
