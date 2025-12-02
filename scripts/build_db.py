#!/usr/bin/env python3
import requests
import csv
import json
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTFILE = ROOT / "aircraft_seats.json"
SEATS_REF = ROOT / "data" / "seats_reference.csv"

# ------------------------
# Load seat/class overrides (seed data)
# ------------------------
seat_lookup = {}

if SEATS_REF.exists():
    with SEATS_REF.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            icao = row["icao"].strip().upper()
            if not icao:
                continue
            seats = row.get("seats", "").strip()
            cls = row.get("class", "").strip() or "L2J"
            seat_lookup[icao] = {
                "seats": int(seats) if seats else None,
                "class": cls
            }

print(f"[build_db] Loaded {len(seat_lookup)} seat overrides from {SEATS_REF}")

# ------------------------
# Download OpenSky aircraft metadata
# ------------------------
print("[build_db] Fetching OpenSky aircraft-types…")
resp = requests.get("https://opensky-network.org/api/metadata/aircraft-types", timeout=30)
resp.raise_for_status()
opensky = resp.json()

print(f"[build_db] Got {len(opensky)} OpenSky type records")

aircraft = {}

for entry in opensky:
    icao = (entry.get("icaoType") or "").strip().upper()
    if not icao:
        continue

    manufacturer = (entry.get("manufacturer") or "").strip()
    model = (entry.get("model") or "").strip()

    if not manufacturer and not model:
        # Skip weird entries
        continue

    if not model and manufacturer:
        name = manufacturer
    elif not manufacturer and model:
        name = model
    else:
        name = model

    full_name = (manufacturer + " " + model).strip() if (manufacturer or model) else icao

    override = seat_lookup.get(icao, {})
    seats = override.get("seats", None)
    cls = override.get("class", "L2J")

    aircraft[icao] = {
        "icao": icao,
        "manufacturer": manufacturer,
        "name": name,
        "full_name": full_name,
        "seats": seats,
        "class": cls
    }

# ------------------------
# Final JSON object
# ------------------------
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

final = {
    "schema": 2,
    "generated_utc": now,
    "source": {
        "aircraft": "OpenSky aircraft-types",
        "seats": "data/seats_reference.csv + optional scrape_seats.py"
    },
    "aircraft": aircraft
}

OUTFILE.write_text(json.dumps(final, indent=2), encoding="utf-8")
print(f"[build_db] Wrote {OUTFILE} with {len(aircraft)} types")
