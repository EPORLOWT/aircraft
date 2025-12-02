# Aircraft Database (Auto-Generated)

This repo maintains a machine-readable aircraft type database for my ESP32 ADS-B flight display project.

- Source aircraft metadata: [OpenSky Network aircraft-types API](https://opensky-network.org/)
- Seat counts: `data/seats_reference.csv` + optional Wikipedia scraping (`scripts/scrape_seats.py`)
- Output: `aircraft_seats.json` (schema version 2)

## Layout

- `aircraft_seats.json` — generated JSON used by devices
- `data/seats_reference.csv` — manual/seed seat + class overrides
- `data/airlines.csv` — airline metadata for optional logo fetching
- `scripts/build_db.py` — main builder used in CI
- `scripts/scrape_seats.py` — helper to fill seat counts from Wikipedia
- `scripts/airline_logos.py` — helper to pull airline logos into `logos/`
- `.github/workflows/update_aircraft.yml` — GitHub Action to regenerate the DB daily

## JSON Schema v2

```jsonc
{
  "schema": 2,
  "generated_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "source": { ... },
  "aircraft": {
    "A320": {
      "icao": "A320",
      "manufacturer": "Airbus",
      "name": "A320",
      "full_name": "Airbus A320",
      "seats": 186,
      "class": "L2J"
    }
  }
}
