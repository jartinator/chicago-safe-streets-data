"""Central configuration for the Chicago Bike Safety Correlation Dashboard pipeline.

All dataset IDs, paths, filters, and mapping tables live here so that swapping a
data source (or forking for another city) means editing this file, not the modules.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "pipeline" / "raw"
SITE_DATA_DIR = REPO_ROOT / "site" / "data"
SNAPSHOT_DIR = REPO_ROOT / "data" / "snapshots"

SOCRATA_DOMAIN = "https://data.cityofchicago.org"

# Mellow Bike Map (jeancochrane/mellow-bike-map, MIT licensed) — crowdsourced
# low-stress-street tags. Not Socrata; a small third-party Django app, so
# pull_mellow.py treats failures as non-fatal (falls back to the stub layer).
MELLOW_API_URL = "https://mellowbikemap.com/api/routes/"

# Socrata dataset IDs (Chicago Data Portal, open JSON endpoints, no auth for modest volumes)
DATASETS = {
    "crashes": "85ca-t3if",        # Traffic Crashes - Crashes (one row per crash)
    "people": "u6pd-qa9d",         # Traffic Crashes - People (person_type filter lives here)
    "vehicles": "68nd-jvt3",       # Traffic Crashes - Vehicles (units)
    "bike_routes": "hvv9-38ut",    # CDOT Bike Routes (line geometry, current-state only)
    "wards": "p293-wvbd",          # Ward boundaries (2023 remap). If this 404s, search the
                                   # portal for "Boundaries - Wards (2023-)" and update.
    "sr311": "v6vf-nfxy",          # 311 Service Requests (unified, Dec 2018-)
    "speed_cameras": "hhkd-xvj4",  # Speed Camera Violations
    "red_light_cameras": "spng-6irc",  # Red Light Camera Violations
}

# Crash data is citywide-reliable only from this date (capability report).
CRASH_START_DATE = "2017-09-01"

# Batched $where ... in(...) lookups: ids per request.
ID_BATCH_SIZE = 50

# Socrata paging size.
PAGE_SIZE = 50000

# Spatial join: crashes farther than this from any bikeway get segment_id = null.
NEAREST_SEGMENT_MAX_DISTANCE_M = 30

# CRS: project to UTM 16N for distance ops; publish EPSG:4326.
METRIC_CRS = "EPSG:26916"
OUTPUT_CRS = "EPSG:4326"

# Raw CDOT facility labels -> public-facing categories (UI plan taxonomy).
# The raw taxonomy may be coarser/differently-worded; unmatched labels fall to "other"
# and are logged so this table can be extended after the first real pull.
FACILITY_CATEGORY_MAP = {
    "PROTECTED BIKE LANE": "protected",
    "BARRIER PROTECTED BIKE LANE": "protected",
    "PROTECTED LANE": "protected",
    "BUFFERED BIKE LANE": "buffered",
    "BUFFERED LANE": "buffered",
    "BIKE LANE": "painted",
    "CONVENTIONAL BIKE LANE": "painted",
    "NEIGHBORHOOD GREENWAY": "greenway",
    "NEIGHBORHOOD ROUTE": "greenway",
    "SHARED-LANE": "sharrow",
    "SHARED LANE": "sharrow",
    "MARKED SHARED LANE": "sharrow",
    "OFF-STREET TRAIL": "trail",
    "OFF STREET TRAIL": "trail",
    "TRAIL": "trail",
    "ACCESS PATH": "other",
}

FACILITY_CATEGORIES = ["protected", "buffered", "painted", "greenway", "sharrow", "trail", "other"]

# 311 is a biased proxy. Rather than hard-coding sr_type names (the city renames them),
# match on substrings; pull_311.py also supports --list-types to inspect the live taxonomy.
SR311_TYPE_SUBSTRINGS = ["BIKE", "BICYCLE"]
SR311_START_DATE = "2018-12-18"  # unified 311 dataset begins

# Injury severity normalization (People dataset injury_classification -> published enum).
INJURY_SEVERITY_MAP = {
    "FATAL": "fatal",
    "INCAPACITATING INJURY": "incapacitating",
    "NONINCAPACITATING INJURY": "non_incapacitating",
    "REPORTED, NOT EVIDENT": "reported_not_evident",
    "NO INDICATION OF INJURY": "none",
}

DATA_TIERS = ("real", "proxy", "mock", "crowdsourced")

CONTRACT_VERSION = "1.2"
