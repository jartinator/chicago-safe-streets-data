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
    "red_light_cameras": "spqx-js37",  # Red Light Camera Violations
    "acs_ward": "k5pk-wpt9",       # ACS 5-Year Data by Ward - Most Recent Year (2023 remap,
                                   # pre-aggregated to wards by the city; confirmed live 2026-07-11)
}

# Legistar Web API (webapi.legistar.com) — the standard hosted API used by ~100+
# municipalities, including Chicago's pre-2023 council records. Confirmed live,
# no auth required, OData-style query params ($filter, $top, $orderby).
#
# IMPORTANT: Chicago's City Council migrated off Legistar to a new system (eLMS,
# chicityclerkelms.chicago.gov) around 2023-06-21 — the Legistar API's most recent
# MatterIntroDate is frozen at that date (confirmed live 2026-07-11). eLMS has a
# public-looking Swagger UI at api.chicityclerkelms.chicago.gov but no working
# endpoint could be found by direct guessing during research; see DECISIONS.md.
# Legistar therefore covers historical council activity (pre-2023-06-21) well but
# CANNOT answer "what's happening now" — pull_hearings.py degrades honestly for that.
LEGISTAR_CLIENT = "chicago"
LEGISTAR_API_URL = f"https://webapi.legistar.com/v1/{LEGISTAR_CLIENT}"
LEGISTAR_DATA_FROZEN_AT = "2023-06-21"

# City Clerk eLMS (successor to Legistar). Meetings page confirmed to exist and
# render a real meeting calendar/table, but it appears to be JS-rendered with no
# discovered public JSON endpoint — used only as a link-out target for now.
ELMS_MEETINGS_URL = "https://chicityclerkelms.chicago.gov/Meetings"
ELMS_COMMITTEES_OF_INTEREST = [
    "Committee on Pedestrian and Traffic Safety",
    "Committee on Transportation and Public Way",
]

# Ward Wise (Chi Hack Night, wardwisechicago.org) — volunteer project structuring
# Aldermanic Menu Program spending (city only publishes PDFs). States it has a
# public JSON API; every endpoint returned HTTP 500 during verification
# (2026-07-11) — likely a maintenance gap in a small volunteer project, not a
# permanent absence. pull_menu_spending.py treats failure as non-fatal, same
# pattern as pull_mellow.py.
WARD_WISE_API_URL = "https://www.wardwisechicago.org/api"

# Keyword net for street/bike-safety-relevant legislation. Deliberately broad —
# false positives get filtered out by classify_safety_topic.py, but a pull-time
# keyword miss is unrecoverable, so pull_council_records.py casts wide.
SAFETY_TOPIC_KEYWORDS = [
    "bike", "bicycle", "cyclist", "complete streets", "vision zero",
    "traffic calming", "protected lane", "bike lane", "pedestrian safety",
    "speed hump", "traffic safety", "road diet", "curb extension",
]

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

DATA_TIERS = ("real", "proxy", "mock", "crowdsourced", "derived")

CONTRACT_VERSION = "1.3"
