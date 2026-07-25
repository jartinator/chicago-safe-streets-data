"""Central configuration for the Chicago Bike Safety Correlation Dashboard pipeline.

All dataset IDs, paths, filters, and mapping tables live here so that swapping a
data source (or forking for another city) means editing this file, not the modules.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "pipeline" / "raw"
SITE_DIR = REPO_ROOT / "site"
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
# Public matter detail page (confirmed 200 with a matterId GUID, 2026-07-13) —
# where pull_agenda_items.py points each agenda item's "read the record" link.
ELMS_MATTER_PAGE_URL = "https://chicityclerkelms.chicago.gov/Matter/?matterId="
ELMS_COMMITTEES_OF_INTEREST = [
    "Committee on Pedestrian and Traffic Safety",
    "Committee on Transportation and Public Way",
]

# PeopleForBikes BNA / City Ratings (bna.peopleforbikes.org) — third-party annual
# bike-network score computed from OpenStreetMap (crowdsourced tier). Unauthenticated
# JSON API, verified 2026-07-13; access notes and full endpoint survey in
# docs/research/followups/peopleforbikes-bna-evaluation.md. Only the citywide
# scorecard (B1) ships from these endpoints; the block/ways file store is the
# gated B2/B3 work (docs/superpowers/plans/2026-07-13-pfb-bna-b2-*.md, -b3-*.md).
# Non-fatal like Mellow — the host may be egress-blocked in pipeline environments,
# in which case aggregate.py keeps shipping the committed bna_scores.json.
BNA_API_URL = "https://bna.peopleforbikes.org/api"
BNA_CITY_RATINGS_PATH = "city-ratings/United%20States/Illinois/Chicago"
# PFB's "large city" population floor, used for the peer-context rank.
BNA_LARGE_CITY_MIN_POPULATION = 300_000

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
    "speed hump", "traffic safety", "road diet", "curb extension", "dooring",
]

# News coverage feeds (pull_news.py) — public RSS only, headline+link+date+
# outlet, never body text. Feasibility evidence and outlet-by-outlet verdicts:
# docs/research/news-layer/evidence-feeds.md. Both outlets' robots.txt
# disallow AI-branded crawlers by name, so the pull identifies itself with its
# own honest User-Agent (same pattern as OSM_USER_AGENT above) and treats any
# 403/429 as the outlet opting out — skip, never work around.
NEWS_USER_AGENT = ("OnYourLeftNewsBot/1.0 (open-source Chicago bike-safety "
                   "dashboard; +https://github.com/jartinator/chicago-safe-streets-data)")
NEWS_FEEDS = [
    # source=None means "take the outlet name from the feed item itself"
    # (Google News carries a per-item <source> element).
    {"url": "https://chi.streetsblog.org/feed/",
     "source": "Streetsblog Chicago", "kind": "rss"},
    {"url": "https://blockclubchicago.org/category/transportation/feed/",
     "source": "Block Club Chicago", "kind": "rss"},
    # query_is_filter: this query is scoped tightly enough that its results
    # are bike-safety-relevant by construction — aggregate's relevance gate
    # accepts them without a keyword check. The roster-derived project query
    # (pull_news.project_query_feed) deliberately does NOT set this: its
    # corridor-name phrases can surface unrelated stories, which must pass
    # the normal keyword/project gate.
    {"url": ("https://news.google.com/rss/search?q=%22bike+lane%22+OR+"
             "%22bike+lanes%22+OR+%22protected+lane%22+OR+dooring+Chicago"
             "+when:90d&hl=en-US&gl=US&ceid=US:en"),
     "source": None, "kind": "google_news", "query_is_filter": True},
]
# Published window/cap: items older than this (relative to the pull's
# fetched_at, so re-aggregation is deterministic) are dropped at aggregate
# time; the list is newest-first and capped.
NEWS_WINDOW_DAYS = 90
NEWS_MAX_ITEMS = 60
NEWS_FEED_MAX_BYTES = 5 * 1024 * 1024

# Google News link resolution (issue #42): following the redirect gets a JS
# interstitial from datacenter IPs, so resolution instead replays the
# documented "batchexecute" decode Google's own front-end uses (scrape a
# signature+timestamp off the article stub page, then POST them to the
# batchexecute RPC to get the real publisher URL back). Unresolvable links
# keep the working redirect URL — never drop the item.
NEWS_RESOLVE_TIMEOUT_S = 20
NEWS_RESOLVE_ATTEMPTS = 2  # first try + one retry
NEWS_RESOLVE_BACKOFF_S = 2
GNEWS_ARTICLE_URL_TMPL = "https://news.google.com/rss/articles/{article_id}"
GNEWS_BATCHEXECUTE_URL = "https://news.google.com/_/DotsSplashUi/data/batchexecute"

# Proposed & in-progress bikeway projects — hand-curated editorial roster
# (the main_routes.json pattern): statuses are volunteer-reviewed with
# citations; the news layer auto-attaches coverage per project via its
# curated news_phrases. Design + validation: docs/superpowers/specs/
# 2026-07-13-proposed-projects-design.md. pull_news.py also derives one
# extra Google News query from the roster's phrases so coverage follows the
# roster (several real projects' current coverage lives on outlets outside
# the base allowlist).
PROPOSED_PROJECTS_PATH = REPO_ROOT / "data" / "proposed_projects.json"
NEWS_PROJECT_QUERY_PHRASES_PER_PROJECT = 2  # keeps the query URL sane

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

# Released FOIA record sets, one directory per request reference. Committed as
# received (minus oversized scans, which manifest.json still hashes) so every
# number we publish off them stays traceable to the file the agency sent.
FOIA_DIR = REPO_ROOT / "data" / "foia"

# CDOT FOIA S145367-071326 (released 2026-07-24) — the historical Bike Lane
# Mileage Tracker request. Its Complete Streets dashboard carries CDOT's own
# 2010–2025 annual bikeway mileage by facility type, and the 2024 bikeway layer
# carries the per-segment install year the public Bike Routes layer omits.
# See data/foia/S145367-071326/README.md and docs/foia/log.md row 1.
CDOT_MILEAGE_FOIA_DIR = FOIA_DIR / "S145367-071326" / "records"
CDOT_COMPLETE_STREETS_DASHBOARD = CDOT_MILEAGE_FOIA_DIR / "CompleteStreets_Dashboard.xlsx"
CDOT_BIKEWAY_2024_LAYER = CDOT_MILEAGE_FOIA_DIR / "GIS" / "Bikeway_Network_2024_Final.shp"
# Derived, committed output of pipeline/foia_bikeway_history.py.
CDOT_BIKEWAY_HISTORY_PATH = REPO_ROOT / "data" / "cdot_bikeway_history.json"

# facility_category -> main-route grade (network tiers v2 design, spec §3,
# docs/superpowers/specs/2026-07-13-network-tiers-design.md). Four independent
# grade levels: protected <- protected; paint <- buffered/painted (still just
# paint & signs); mellow <- greenway (its own grade now, not lumped into paint
# — greenways are traffic-calmed streets, not painted lanes) + mellow-derived
# connector geometry (see build_mellow_connectors); none <- sharrow and any
# unmatched/other facility_category (the .get(..., "none") default in
# build_main_routes covers "unmatched"); offstreet <- trail, unchanged.
MAIN_ROUTE_GRADE_MAP = {
    "trail": "offstreet",
    "protected": "protected",
    "buffered": "paint",
    "painted": "paint",
    "greenway": "mellow",
    "sharrow": "none",
    "other": "none",
}

# Buffer distance (meters) for matching mellow_routes geometry against
# bike_routes when building mellow_connectors.geojson (network tiers v2 design
# spec §4): a mellow line part is dropped as a duplicate when it falls within
# this distance of any published bike_routes segment. Applied in METRIC_CRS.
MELLOW_DEDUPE_BUFFER_M = 25.0

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

# Divvy (Lyft-operated bikeshare) trip data — PLANNED, not yet published.
# SCAFFOLDING ONLY (see pipeline/pull_divvy.py docstring): a monthly trip
# export is 100MB+ zipped, too large to fetch/validate in a normal pipeline
# run here, so this stanza and the pull script exist so a future session can
# run the real ingest without re-deriving the source/shape decisions. Mirrors
# the Smart Streets "FOIA-pending" precedent (SCHEMA.md "PLANNED (not yet
# published)") for "we know the source, we haven't validated the output."
# Modern feed (system_data.csv Data Portal set is deprecated/frozen); Lyft
# publishes monthly ZIPs of station-level and trip-level CSVs to this public,
# unauthenticated S3 bucket — see https://divvybikes.com/system-data.
DIVVY_S3_BASE_URL = "https://divvy-tripdata.s3.amazonaws.com/"
# Bucket is a public S3 listing (?list-type=2) rather than a Socrata API —
# pull_divvy.py lists it to find the most recent monthly file rather than
# hard-coding a filename that goes stale every month.
DIVVY_S3_LIST_URL = "https://divvy-tripdata.s3.amazonaws.com/?list-type=2"
DIVVY_USER_AGENT = ("chicago-safe-streets-data/1.0 (+https://github.com/"
                     "jartinator/chicago-safe-streets-data)")
# Station-level aggregation output (not yet built/published this PR) — a
# per-ward trip-density proxy for cycling VOLUME, never a per-rider risk
# rate (crashes / trips is explicitly forbidden — see pull_divvy.py).
DIVVY_WARD_EXPOSURE_PATH = SITE_DATA_DIR / "divvy_ward_exposure.json"
# Safety cap: a single monthly trip CSV can exceed 100MB unzipped. If a
# fetched archive exceeds this, pull_divvy.py aborts rather than parsing —
# same "fail honest, don't guess" posture as the rest of the pipeline.
DIVVY_MAX_DOWNLOAD_BYTES = 150 * 1024 * 1024

DATA_TIERS = ("real", "proxy", "mock", "crowdsourced", "derived")

CONTRACT_VERSION = "1.16"

# Agent-first static API (site/api/v1/) — a separate, smaller namespace of JSON
# files generated from the already-committed site/data/* contract for LLM
# agents to fetch and cite. See pipeline/emit_api.py.
API_VERSION = "1"
SITE_API_DIR = REPO_ROOT / "site" / "api" / "v1"
# llms.txt/sitemap.xml (Phase 5) are siblings of index.html at the site root,
# not part of the api/v1 namespace tree — they're written under SITE_DIR
# (above), never SITE_API_DIR, so _prune_stale (which only scans
# SITE_API_DIR) never touches them.
SITE_BASE_URL = "https://jartinator.github.io/chicago-safe-streets-data"
# emit_api.py hard-fails if any emitted file exceeds this — the design goal is
# a cold agent reaching a cited answer in <=3 fetches of <100 KB each.
API_SIZE_BUDGET_BYTES = 100_000
# Crash slices (site/api/v1/crashes/ward-NN.json) are columnar rows, not prose,
# and the worst ward (27, 1,187 crashes) needs more headroom than a hand-
# written endpoint ever would — this budget applies to that one family only,
# everything else still enforces API_SIZE_BUDGET_BYTES.
API_CRASH_SLICE_BUDGET_BYTES = 150_000
# crash_id in the source data is a 128-hex-char string; emitting it in full in
# every row of every ward file wastes bytes for no agent-facing benefit, so
# crash slices truncate to this many leading hex chars (falling back to the
# full id per-crash on the rare prefix collision — see crash_id_prefixes in
# emit_api.py).
CRASH_ID_PREFIX_LEN = 16
