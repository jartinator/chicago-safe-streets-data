"""Pull Divvy (Lyft-operated bikeshare) trip data and build a per-ward trip-density proxy.

What this does:
  1. List the public S3 bucket (DIVVY_S3_LIST_URL) to find the most recent
     monthly "*-divvy-tripdata.zip" key — the modern feed. (The old Data
     Portal "Divvy Trips" Socrata dataset is deprecated and frozen; do not
     use it.)
  2. HEAD the object first and abort if Content-Length exceeds
     DIVVY_MAX_DOWNLOAD_BYTES (config.py) — fail before spending the
     bandwidth/memory, not after.
  3. Download with an honest User-Agent (DIVVY_USER_AGENT), unzip in memory,
     and aggregate to STATION level: group trips by (start_station_id,
     start_station_name) -> trip count, keeping one representative lat/lng
     per station. This collapses several hundred thousand trip rows to
     roughly a thousand stations *before* any geometry work, which is the
     only way this is cheap enough to run routinely.
  4. Point-in-polygon each station's (lat, lng) against site/data/wards.geojson
     (geopandas + shapely, same method as spatial_join.py) to roll station
     trip counts up to ward totals.
  5. Write site/data/divvy_ward_exposure.json labeled `data_tier: "proxy"`
     with a note spelling out the bias: this is a SYSTEM-AREA-BIASED PROXY
     FOR CYCLING VOLUME, NOT EXPOSURE. It undercounts non-Divvy cycling
     entirely, and Divvy station placement itself skews downtown/North Side
     relative to the West Side, so low ward counts here conflate "less
     riding" with "no station coverage." This is ward-level CONTEXT to sit
     beside crash counts — never a denominator.

HARD RULE, enforced by omission in this module: never compute crashes/trips
or any other per-rider risk rate from this data. Exposure count and crash
count are published side by side, never divided into each other — the trip
count has no denominator relationship to crashes and dividing them produces
a number that looks like a risk rate but isn't one (Divvy trips are not all
cycling trips, and crash victims are not all Divvy riders).

Failure handling: ANY failure (network/egress blocked, listing empty, object
too large, zip/CSV parse error, wards.geojson missing) is non-fatal, matching
the other optional pulls (pull_bna, pull_osm_trails): print a clear WARNING
to stderr, leave site/data/divvy_ward_exposure.json untouched (absent if it
was already absent), and exit 0 so run_all.py continues. It never writes
synthetic/fabricated numbers to fill the gap.
"""
import argparse
import io
import re
import sys
import zipfile
from collections import defaultdict
from xml.etree import ElementTree as ET

import requests

from config import (
    DIVVY_S3_BASE_URL,
    DIVVY_S3_LIST_URL,
    DIVVY_USER_AGENT,
    DIVVY_MAX_DOWNLOAD_BYTES,
    DIVVY_WARD_EXPOSURE_PATH,
    SITE_DATA_DIR,
)
from socrata import write_json

_S3_LIST_NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
_TRIPDATA_ZIP_RE = re.compile(r"^\d{6}-divvy-tripdata\.zip$")


def _headers():
    return {"User-Agent": DIVVY_USER_AGENT}


def find_latest_tripdata_key():
    """Return the most recent 'YYYYMM-divvy-tripdata.zip' key in the bucket, or None."""
    resp = requests.get(DIVVY_S3_LIST_URL, headers=_headers(), timeout=60)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    keys = [
        el.text for el in root.findall(".//s3:Contents/s3:Key", _S3_LIST_NS)
        if el.text and _TRIPDATA_ZIP_RE.match(el.text.rsplit("/", 1)[-1])
    ]
    return sorted(keys)[-1] if keys else None


def fetch_tripdata_zip(key):
    """Download one monthly Divvy zip, aborting honestly if it's larger than the cap.

    Returns the raw zip bytes, or raises RuntimeError with a clear reason.
    """
    url = DIVVY_S3_BASE_URL + key
    head = requests.head(url, headers=_headers(), timeout=30)
    head.raise_for_status()
    content_length = head.headers.get("Content-Length")
    if content_length and int(content_length) > DIVVY_MAX_DOWNLOAD_BYTES:
        raise RuntimeError(
            f"{key} is {int(content_length):,} bytes, over the "
            f"{DIVVY_MAX_DOWNLOAD_BYTES:,}-byte cap — refusing to download"
        )
    resp = requests.get(url, headers=_headers(), timeout=300, stream=True)
    resp.raise_for_status()
    chunks = []
    total = 0
    for chunk in resp.iter_content(chunk_size=1024 * 1024):
        total += len(chunk)
        if total > DIVVY_MAX_DOWNLOAD_BYTES:
            raise RuntimeError(
                f"{key} exceeded the {DIVVY_MAX_DOWNLOAD_BYTES:,}-byte cap "
                f"mid-download — refusing to buffer further"
            )
        chunks.append(chunk)
    return b"".join(chunks)


def aggregate_station_counts(zip_bytes):
    """Group trips in the monthly zip's CSV(s) by start station -> trip count + one lat/lng.

    Collapses the trip-level rows (hundreds of thousands per month) down to
    roughly a thousand station rows before any geometry work is done, which
    is what keeps this affordable to run at all.
    """
    stations = {}  # station_key -> {name, lat, lng, trip_count}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        # Divvy builds these zips on a Mac: skip __MACOSX/._*.csv AppleDouble
        # members, which are binary (not UTF-8) despite the .csv suffix.
        csv_names = [
            n for n in zf.namelist()
            if n.lower().endswith(".csv")
            and not n.startswith("__MACOSX/")
            and not n.rsplit("/", 1)[-1].startswith("._")
        ]
        if not csv_names:
            raise RuntimeError("zip contained no CSV members")
        for name in csv_names:
            with zf.open(name) as fh:
                import csv
                reader = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8"))
                for row in reader:
                    station_id = row.get("start_station_id") or row.get("start_station_name")
                    if not station_id:
                        continue
                    if station_id not in stations:
                        stations[station_id] = {
                            "station_id": station_id,
                            "name": row.get("start_station_name"),
                            "lat": None,
                            "lng": None,
                            "trip_count": 0,
                        }
                    stations[station_id]["trip_count"] += 1
                    lat, lng = row.get("start_lat"), row.get("start_lng")
                    if lat and lng and stations[station_id]["lat"] is None:
                        try:
                            stations[station_id]["lat"] = float(lat)
                            stations[station_id]["lng"] = float(lng)
                        except (TypeError, ValueError):
                            pass
    return list(stations.values())


def join_stations_to_wards(stations):
    """Point-in-polygon each station against site/data/wards.geojson -> {ward: trip_count}.

    Same method as spatial_join.py (geopandas + shapely, point-within-polygon).
    Stations missing lat/lng, or falling outside every ward polygon, are
    excluded from the ward rollup (never guessed into a ward).
    """
    import json as _json

    import geopandas as gpd
    from shapely.geometry import Point

    wards_path = SITE_DATA_DIR / "wards.geojson"
    if not wards_path.exists():
        raise RuntimeError(f"{wards_path} not found — cannot join stations to wards")

    gj = _json.loads(wards_path.read_text())
    wards_gdf = gpd.GeoDataFrame.from_features(gj["features"], crs="EPSG:4326")
    props = gj["features"][0]["properties"] if gj["features"] else {}
    ward_key = next((k for k in props if k.lower() in ("ward", "ward_id")), None)
    if not ward_key:
        raise RuntimeError("wards.geojson has no ward/ward_id property")
    wards_gdf["ward"] = wards_gdf[ward_key].astype(str)

    located = [s for s in stations if s["lat"] is not None and s["lng"] is not None]
    if not located:
        raise RuntimeError("no stations had usable lat/lng after aggregation")

    pts = gpd.GeoDataFrame(
        located,
        geometry=[Point(s["lng"], s["lat"]) for s in located],
        crs="EPSG:4326",
    )
    joined = gpd.sjoin(pts, wards_gdf[["ward", "geometry"]], how="left", predicate="within")

    by_ward = defaultdict(int)
    for _, row in joined.iterrows():
        ward = row.get("ward")
        if ward is not None and ward == ward:  # drop NaN (unmatched)
            by_ward[str(ward)] += int(row["trip_count"])
    return dict(by_ward)


def as_of_from_key(key):
    """'202606-divvy-tripdata.zip' -> '2026-06' (the month the trips cover)."""
    m = re.match(r"(\d{4})(\d{2})-divvy-tripdata\.zip$", key.rsplit("/", 1)[-1])
    if not m:
        raise RuntimeError(f"cannot derive as_of month from key {key!r}")
    return f"{m.group(1)}-{m.group(2)}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args()

    try:
        key = find_latest_tripdata_key()
        if not key:
            raise RuntimeError("bucket listing returned no *-divvy-tripdata.zip keys")
        print(f"Latest Divvy tripdata key: {key}", file=sys.stderr)

        zip_bytes = fetch_tripdata_zip(key)
        stations = aggregate_station_counts(zip_bytes)
        by_ward = join_stations_to_wards(stations)

        output = {
            "data_tier": "proxy",
            "status": "ok",
            "as_of": as_of_from_key(key),
            "source_key": key,
            "note": (
                "System-area-biased proxy for cycling VOLUME, not exposure; "
                "not all cycling — only Divvy trips. Station placement skews "
                "toward downtown/North Side vs the West Side, so a low count "
                "here means fewer stations, not necessarily less riding. "
                "Never divide crashes by trips: this is context to display "
                "beside crash counts, never a denominator for a risk rate."
            ),
            "wards": [
                {"ward": ward, "trip_count": count}
                for ward, count in sorted(by_ward.items(), key=lambda kv: int(kv[0]))
            ],
        }
        write_json(DIVVY_WARD_EXPOSURE_PATH, output)
        print(f"divvy_ward_exposure: {len(stations)} stations, "
              f"{len(by_ward)} wards, {sum(by_ward.values())} total trips")
    except (requests.RequestException, RuntimeError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(
            f"WARNING: Divvy pull failed ({exc}) — "
            f"{DIVVY_WARD_EXPOSURE_PATH.name} left absent/unchanged this run. "
            f"Non-fatal (see module docstring); a failure here never writes "
            f"synthetic numbers.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
