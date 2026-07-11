"""Generate deterministic mock bike-lane obstruction data for dashboard development.

Synthesizes point geometries along real Chicago bikeways with obstruction-like attributes,
writing a GeoJSON FeatureCollection that mirrors Bike Lane Uprising's submission schema.
Useful for testing the pipeline and dashboard before live crowdsourced submissions arrive.

Usage: python make_mock_obstructions.py [--count 400] [--seed 42]
"""
import argparse
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

from config import RAW_DIR, SITE_DATA_DIR
from socrata import write_json

# Schema enum for obstruction type. SWAPPABLE: pending Bike Lane Uprising consultation.
OBSTRUCTION_TYPES = [
    "vehicle_in_lane",
    "delivery_vehicle",
    "debris",
    "construction",
    "poor_design",
    "snow_ice",
    "other",
]

PLATE_STATES = ["IL", "IN", "WI", "MI", "OH", "unknown"]

GENERIC_COMPANIES = [
    "Generic Delivery Co.",
    "Placeholder Logistics",
    "Mock Transport Inc.",
    None,
]

NOTES_TEMPLATES = [
    "Observed during rush hour",
    "Partially blocking lane",
    "Creates hazard for cyclists",
    "Bike lane obstruction",
    "Safety concern",
    "Parked incorrectly",
]

M_PER_DEG_LAT = 111_320.0

# Fixed "as of" anchor, matching make_fixtures.py's convention, so --seed N
# produces byte-identical output on every run regardless of wall-clock date.
AS_OF = datetime(2026, 7, 1)


def m_per_deg_lng(lat):
    return M_PER_DEG_LAT * math.cos(math.radians(lat))


def jitter_point(rng, lat, lng, sigma_m=15):
    """Jitter a point by gaussian noise (default ~15m stdev)."""
    return (lat + rng.gauss(0, sigma_m) / M_PER_DEG_LAT,
            lng + rng.gauss(0, sigma_m) / m_per_deg_lng(lat))


def load_bike_routes():
    """Load bike routes GeoJSON; exit if missing."""
    path = RAW_DIR / "bike_routes.geojson"
    if not path.exists():
        print(f"Error: {path} not found.")
        print("Run pull_bike_routes.py or make_fixtures.py first.")
        exit(1)
    with open(path) as f:
        return json.load(f)


def extract_street_name(properties):
    """Find street name in properties, case-insensitive against known keys.

    Candidate list matches aggregate.py's build_routes() street-key lookup so
    this module clusters obstructions on the same streets aggregate.py reports.
    """
    lower = {k.lower(): k for k in properties}
    for key in ["st_name", "street", "street_nam", "name"]:
        if key in lower:
            return properties[lower[key]]
    return "Unknown"


def group_segments_by_street(features):
    """Group LineString features by street name; return dict of street -> feature list."""
    by_street = {}
    for feature in features:
        street = extract_street_name(feature["properties"])
        if street not in by_street:
            by_street[street] = []
        by_street[street].append(feature)
    return by_street


def flatten_line_coords(coords):
    """Flatten LineString or MultiLineString coordinates to one list of [lng, lat] pairs.

    make_fixtures.py emits LineString; the live CDOT pull is MultiLineString
    (each feature can hold multiple disjoint parts) — normalize both here.
    """
    if coords and isinstance(coords[0][0], (int, float)):
        return coords
    return [pt for part in coords for pt in part]


def extract_random_point_on_linestring(rng, linestring_coords):
    """Pick a random vertex on a LineString and jitter it."""
    if len(linestring_coords) < 2:
        return None
    idx = rng.randint(0, len(linestring_coords) - 1)
    lng, lat = linestring_coords[idx]
    lat, lng = jitter_point(rng, lat, lng, sigma_m=15)
    return (lat, lng)


def generate_random_date(rng, days_back=18 * 30):
    """Generate random datetime in last ~18 months, biased toward weekdays and rush hours."""
    end = AS_OF
    start = end - timedelta(days=days_back)

    # Pick random day
    days_span = (end - start).days
    day_offset = rng.randint(0, days_span)
    d = start + timedelta(days=day_offset)

    # Bias toward weekdays (~70%)
    while rng.random() < 0.3 and d.weekday() >= 5:  # 5=Sat, 6=Sun
        d -= timedelta(days=1)

    # Bias toward rush hours (7-10am, 4-7pm)
    if rng.random() < 0.6:
        if rng.random() < 0.5:
            hour = rng.randint(7, 9)
        else:
            hour = rng.randint(16, 18)
    else:
        hour = rng.randint(0, 23)

    minute = rng.randint(0, 59)
    return d.replace(hour=hour, minute=minute, second=0, microsecond=0)


def generate_obstructions(rng, count, by_street):
    """Generate mock obstruction features. Returns (features, street_counts)."""
    features = []
    street_counts = {}
    streets = list(by_street.keys())

    # Pick ~4 hot-spot streets
    if len(streets) > 4:
        hot_streets = rng.sample(streets, min(4, len(streets)))
    else:
        hot_streets = streets

    for i in range(count):
        # ~50% from hot-spot streets
        if rng.random() < 0.5:
            street = rng.choice(hot_streets)
        else:
            street = rng.choice(streets)

        street_counts[street] = street_counts.get(street, 0) + 1

        segments = by_street[street]
        feature = rng.choice(segments)
        coords = flatten_line_coords(feature["geometry"]["coordinates"])

        point = extract_random_point_on_linestring(rng, coords)
        if not point:
            continue

        lat, lng = point

        # Generate properties
        obstruction_id = f"MOCK-{i + 1:06d}"
        obstruction_type = rng.choice(OBSTRUCTION_TYPES)
        photo_count = rng.randint(0, 5)
        plate_state = rng.choice(PLATE_STATES)

        # Plate number: null or MOCK-based
        if rng.random() < 0.3:
            plate_number = None
        else:
            plate_number = f"MOCK{rng.randint(100, 999)}"

        company_name = rng.choice(GENERIC_COMPANIES)
        notes = rng.choice(NOTES_TEMPLATES)
        occurred_at = generate_random_date(rng)
        crash_occurred = rng.random() < 0.03  # ~3%

        feature_dict = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat],
            },
            "properties": {
                "id": obstruction_id,
                "obstruction_type": obstruction_type,
                "photo_count": photo_count,
                "plate_state": plate_state,
                "plate_number": plate_number,
                "company_name": company_name,
                "notes": notes,
                "metro_city": "Chicago",
                "occurred_at": occurred_at.isoformat(),
                "crash_occurred": crash_occurred,
                "data_tier": "mock",
                "lat": lat,
                "lng": lng,
            },
        }
        features.append(feature_dict)

    return features, street_counts


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--count", type=int, default=400, help="Number of mock obstructions")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for determinism")
    args = ap.parse_args()

    rng = random.Random(args.seed)

    # Load bike routes
    geojson = load_bike_routes()
    features = geojson.get("features", [])

    # Group by street
    by_street = group_segments_by_street(features)

    # Generate obstructions
    obs_features, street_counts = generate_obstructions(rng, args.count, by_street)

    # Get top 3 streets
    top_3 = sorted(street_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    # Get date range
    dates = [datetime.fromisoformat(f["properties"]["occurred_at"]) for f in obs_features]
    date_min = min(dates)
    date_max = max(dates)

    # Build output GeoJSON
    output = {
        "type": "FeatureCollection",
        "properties": {
            "data_tier": "mock",
            "note": "Synthetic demonstration data. NOT real reports. Schema mirrors Bike Lane Uprising's public submission fields; category enum is a placeholder.",
        },
        "features": obs_features,
    }

    # Write output
    output_path = write_json(SITE_DATA_DIR / "obstructions_mock.geojson", output)

    # Print summary
    top_3_str = ", ".join(f"{street} ({count})" for street, count in top_3)
    print(f"mock obstructions: {len(obs_features)} features, "
          f"{date_min.date()} to {date_max.date()}, "
          f"top-3: {top_3_str} (seed={args.seed})")


if __name__ == "__main__":
    main()
