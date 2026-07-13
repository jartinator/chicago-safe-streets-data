"""Central configuration for the Chicago Bike Safety Correlation Dashboard pipeline.

All dataset IDs, paths, filters, and mapping tables live here so that swapping a
data source (or forking for another city) means editing this file, not the modules.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "pipeline" / "raw"
SITE_DATA_DIR = REPO_ROOT / "site" / "data"
SNAPSHOT_DIR = REPO_ROOT / "data" / "snapshots"
# Fixtures write their own synthetic dated snapshots here (gitignored) so an offline
# --fixtures run computes a coherent bikeway-mileage series/growth against fixture wards,
# instead of overlaying the real SNAPSHOT_DIR geometry onto synthetic ward polygons.
# aggregate.py selects between the two by provenance ("fixtures" vs "socrata").
FIXTURE_SNAPSHOT_DIR = REPO_ROOT / "data" / "snapshots_fixtures"
# Committed one-time snapshots of frozen upstream data that never changes (e.g. the
# pre-2023 Legistar council records — see restore_frozen.py). Unlike RAW_DIR (gitignored,
# rebuilt each run), these are versioned so we don't re-pull immutable history every week.
FROZEN_DIR = REPO_ROOT / "pipeline" / "frozen"

SOCRATA_DOMAIN = "https://data.cityofchicago.org"

# Mellow Bike Map (jeancochrane/mellow-bike-map, MIT licensed) — crowdsourced
# low-stress-street tags. Not Socrata; a small third-party Django app, so
# pull_mellow.py treats failures as non-fatal (falls back to the stub layer).
MELLOW_API_URL = "https://mellowbikemap.com/api/routes/"

# OpenStreetMap Overpass API — source for named off-street trails (Lakefront,
# 312 RiverRun, North Shore Channel, North Branch, etc.) that CDOT's on-street
# Bike Routes layer structurally omits. Crowdsourced tier. Non-fatal like Mellow.
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
# overpass-api.de's usage policy requires clients to identify themselves; it
# rejects the default python-requests User-Agent with HTTP 406 Not Acceptable.
OSM_USER_AGENT = "chicago-safe-streets-data/1.0 (+https://github.com/jartinator/chicago-safe-streets-data)"
# (south, west, north, east) — Chicago plus the North Branch Trail's reach north
# into the forest preserves. Trails are shown full-length, not clipped at the city line.
OSM_TRAILS_BBOX = (41.60, -87.95, 42.20, -87.50)
# Named off-street ways only. is_sidepath!=yes drops road-parallel cycle tracks
# that duplicate CDOT on-street segments (see design doc). out geom returns inline
# per-way coordinate arrays so no second node-resolution pass is needed.
_OSM_BBOX_STR = ",".join(str(c) for c in OSM_TRAILS_BBOX)
OSM_TRAILS_QUERY = f"""[out:json][timeout:90];
(
  way["highway"="cycleway"]["name"]["is_sidepath"!="yes"]({_OSM_BBOX_STR});
  way["highway"="path"]["bicycle"="designated"]["name"]["is_sidepath"!="yes"]({_OSM_BBOX_STR});
  way["highway"="footway"]["bicycle"="designated"]["name"]["is_sidepath"!="yes"]({_OSM_BBOX_STR});
);
out geom;
"""

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
    "street_centerlines": "pr57-gg9e",  # Street Center Lines ("transportation") — the
                                        # tabular SODA copy. The 6imu-meau map view's rows
                                        # come back empty and its geospatial export is
                                        # truncated server-side (verified 2026-07-12).
                                        # 56,338 segments, last updated 2021-06; the street
                                        # grid changes slowly, fine for a denominator.
}

# Ward Offices — the city's official roster of current alderpersons (name, email,
# phone, website per ward). Same Socrata portal as crashes. Ingesting the official
# roster is NOT the "never auto-generate" guessing DECISIONS.md #8 forbids — that
# rule was about inferring names. Verified live 2026-07-12.
WARD_OFFICES_DATASET = "htai-wnw4"
ALDERMAN_LOOKUP_URL = "https://www.chicago.gov/city/en/about/wards.html"

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
# Councilmatic (COUNCILMATIC_DATASETTE_URL, below) now covers the far side of this boundary.
LEGISTAR_CLIENT = "chicago"
LEGISTAR_API_URL = f"https://webapi.legistar.com/v1/{LEGISTAR_CLIENT}"
LEGISTAR_DATA_FROZEN_AT = "2023-06-21"

# Chicago Councilmatic (DataMade, MIT-licensed) — official Chicago City Council
# data republished as a public Datasette (SQL-over-HTTP JSON API), updated
# nightly and CURRENT to the present day. This is how we cross the
# LEGISTAR_DATA_FROZEN_AT gap above. Confirmed live 2026-07-11 (data through
# 2026-07-09). Use the UN-hashed base URL: Datasette serves the DB under a
# content-hashed route (e.g. /chicago_council-464e17d) that changes on each
# nightly rebuild, and 302-redirects the un-hashed path to it (requests follows
# the redirect and preserves the ?sql= query string).
# Robust fallback if this host ever disappears: the nightly full-DB dump
# chicago_council.db.zip at github.com/datamade/chicago-council-scrapers/releases.
COUNCILMATIC_DATASETTE_URL = "https://puddle.datamade.us/chicago_council"

# City Clerk eLMS (successor to Legistar). The Meetings page below stays the
# human-facing link-out target; the API root powers structured pulls.
#
# eLMS public API — CONFIRMED WORKING 2026-07-12 (earlier research guessed plural/
# prefixed paths; the real endpoints are singular nouns at the API root, e.g.
# GET https://api.chicityclerkelms.chicago.gov/meeting?filter=body eq '<committee>'
# &sort=date desc&limit=50, rows under the "data" key of the response envelope).
# Undocumented and unversioned — treat as best-effort; pull_hearings.py keeps the
# link-out fallback shape on any failure.
ELMS_API_URL = "https://api.chicityclerkelms.chicago.gov"
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

# Concurrency for id-batch lookups. The crash/vehicle pulls issue hundreds of small
# sequential requests (one per ID_BATCH_SIZE chunk), which dominated pipeline runtime;
# fetching batches in a small thread pool cuts that wall-clock roughly proportionally.
# Kept modest to stay polite to Socrata's throttling (the retry/backoff in socrata._get
# still absorbs the occasional 429). Same magnitude as Legistar's SPONSOR_FETCH_WORKERS.
ID_FETCH_WORKERS = 8

# Socrata paging size.
PAGE_SIZE = 50000

# Spatial join: crashes farther than this from any bikeway get segment_id = null.
NEAREST_SEGMENT_MAX_DISTANCE_M = 30

# Valid coordinate bounds for Chicago. Socrata occasionally returns a geocoding
# failure as a present-but-invalid lat/lon (e.g. the string "0", which lands at
# (0, 0) "null island") rather than omitting the field, so a truthiness check
# alone lets it through. spatial_join.py drops crashes whose parsed lat/lon fall
# outside this box. Generous enough to keep every real Chicago crash (observed
# extents ~41.64..42.02 lat, -87.91..-87.52 lon); tight enough to exclude (0, 0)
# and other out-of-region errors.
CHICAGO_BBOX = {"min_lat": 41.6, "max_lat": 42.1, "min_lon": -88.0, "max_lon": -87.5}

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

# Coverage denominator: which street-centerline segments count as the city's
# bikeable surface-street grid. CLASS: 1=expressway (cycling prohibited),
# 2=arterial, 3=collector, 4=local, 5/7=alley-type stubs, 9=ramp,
# 99/E/S=system artifacts, RIV=river channel. STATUS: N=in service (P=proposed,
# V=vacated, UC/C=not usable roadway). Classes 2+3+4 with status N sum to
# ~3,945 centerline miles — matching the city's oft-cited ~4,000 street miles
# (verified live 2026-07-12).
STREET_CLASSES_INCLUDED = {"2", "3", "4"}
STREET_STATUS_INCLUDED = {"N"}

# Main routes ("rail vs bus" hierarchy) — curated line roster, checked in like
# other configs. See docs/superpowers/specs/2026-07-12-main-routes-design.md.
MAIN_ROUTES_PATH = REPO_ROOT / "data" / "main_routes.json"

# Hand-traced fallback geometry for the roster's off-street trails, used when
# neither a live Overpass pull (raw/osm_trails.json) nor its committed output
# exists in this run's environment. See docs/superpowers/specs/
# 2026-07-12-network-map-distinction.md §8. Tier crowdsourced, like mellow routes.
CURATED_TRAILS_PATH = REPO_ROOT / "data" / "curated_trails.geojson"

# Hand-picked major-road crossings on roster lines, for network-map wayfinding —
# see docs/superpowers/specs/2026-07-12-network-map-distinction.md §7.
ORIENTATION_POINTS_PATH = REPO_ROOT / "data" / "orientation_points.json"

# facility_category -> main-route grade (spec §4, user-locked 4-grade taxonomy).
# Buffers and greenways are still just paint & signs -> "painted"; sharrows
# count as nothing -> "none".
MAIN_ROUTE_GRADE_MAP = {
    "trail": "offstreet",
    "protected": "protected",
    "buffered": "painted",
    "painted": "painted",
    "greenway": "painted",
    "sharrow": "none",
    "other": "none",
}

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

CONTRACT_VERSION = "1.9"
