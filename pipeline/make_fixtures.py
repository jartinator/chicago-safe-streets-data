"""Generate deterministic synthetic raw inputs so the pipeline can run offline.

Writes fixture files into pipeline/raw/ in the exact shapes the pull_* modules
produce, so spatial_join.py and aggregate.py exercise the REAL pipeline code
paths without network access. Fixture geometry follows real Chicago streets
approximately, but every value is synthetic — downstream meta.json records
provenance as "fixtures" so the site can say so.

Usage: python make_fixtures.py [--seed 42]
"""
import argparse
import math
import random
from datetime import datetime, timedelta

from config import RAW_DIR, FIXTURE_SNAPSHOT_DIR
from socrata import write_json

# Approximate Chicago corridors: (street, [(lat, lng) endpoints], raw facility label)
CORRIDORS = [
    ("MILWAUKEE AVE", [(41.882, -87.640), (41.917, -87.687), (41.960, -87.760)], "BIKE LANE"),
    ("DAMEN AVE", [(41.870, -87.676), (41.975, -87.679)], "BIKE LANE"),
    ("HALSTED ST", [(41.845, -87.646), (41.950, -87.649)], "BIKE LANE"),
    ("CLARK ST", [(41.900, -87.631), (41.975, -87.660)], "PROTECTED BIKE LANE"),
    ("DEARBORN ST", [(41.870, -87.629), (41.900, -87.629)], "PROTECTED BIKE LANE"),
    ("ELSTON AVE", [(41.900, -87.660), (41.970, -87.740)], "BUFFERED BIKE LANE"),
    ("KINZIE ST", [(41.889, -87.640), (41.889, -87.680)], "PROTECTED BIKE LANE"),
    ("55TH ST", [(41.795, -87.580), (41.795, -87.680)], "BUFFERED BIKE LANE"),
    ("AUGUSTA BLVD", [(41.899, -87.660), (41.899, -87.740)], "NEIGHBORHOOD GREENWAY"),
    ("WOOD ST", [(41.885, -87.672), (41.940, -87.672)], "NEIGHBORHOOD GREENWAY"),
    ("ARCHER AVE", [(41.845, -87.635), (41.800, -87.720)], "SHARED-LANE"),
    ("VINCENNES AVE", [(41.720, -87.630), (41.780, -87.615)], "SHARED-LANE"),
    ("STONY ISLAND AVE", [(41.740, -87.586), (41.790, -87.586)], "PROTECTED BIKE LANE"),
]

BBOX = (41.64, -87.85, 42.02, -87.52)  # south, west, north, east
M_PER_DEG_LAT = 111_320.0


def m_per_deg_lng(lat):
    return M_PER_DEG_LAT * math.cos(math.radians(lat))


def interpolate(points, step_m=250):
    """Densify a polyline to ~step_m spacing; returns [(lat, lng), ...]."""
    out = [points[0]]
    for (la1, lo1), (la2, lo2) in zip(points, points[1:]):
        dy = (la2 - la1) * M_PER_DEG_LAT
        dx = (lo2 - lo1) * m_per_deg_lng((la1 + la2) / 2)
        dist = math.hypot(dx, dy)
        n = max(1, int(dist // step_m))
        for i in range(1, n + 1):
            out.append((la1 + (la2 - la1) * i / n, lo1 + (lo2 - lo1) * i / n))
    return out


def build_bike_routes(corridors=CORRIDORS):
    features = []
    seg_num = 0
    for street, pts, ftype in corridors:
        dense = interpolate(pts)
        # ~2 vertices per segment -> ~500 m segments
        for i in range(0, len(dense) - 1, 2):
            chunk = dense[i:i + 3]
            if len(chunk) < 2:
                continue
            seg_num += 1
            features.append({
                "type": "Feature",
                "geometry": {"type": "LineString",
                             "coordinates": [[lng, lat] for lat, lng in chunk]},
                "properties": {"objectid": seg_num, "st_name": street, "displayroute": ftype},
            })
    return {"type": "FeatureCollection", "features": features}


# Two dated fixture snapshots so an offline run exercises the over-time series/growth
# (infra_growth_trend needs >=2 snapshots; real snapshots start flat). The "older"
# network drops a few corridors and holds two corridors at a lesser facility type, so
# the newer network shows positive total AND positive protected-lane growth.
FIXTURE_SNAPSHOT_DATES = ("2025-01-15", "2026-07-12")


def older_corridors():
    older = []
    for street, pts, ftype in CORRIDORS[:-3]:  # fewer corridors than today -> total grows
        if street in ("KINZIE ST", "STONY ISLAND AVE") and ftype == "PROTECTED BIKE LANE":
            ftype = "BIKE LANE"  # upgraded to protected later -> protected grows
        older.append((street, pts, ftype))
    return older


def write_fixture_snapshots():
    """Write the older/newer synthetic snapshots into the fixtures-only snapshot dir.

    The newer snapshot mirrors build_bike_routes() (== the fixture raw/bike_routes.geojson),
    so ward_safety_index's current-state miles and the newest series point agree.
    """
    FIXTURE_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in FIXTURE_SNAPSHOT_DIR.glob("bike_routes_*.geojson"):
        stale.unlink()  # rebuild cleanly each run so dates/content stay deterministic
    old_date, new_date = FIXTURE_SNAPSHOT_DATES
    write_json(FIXTURE_SNAPSHOT_DIR / f"bike_routes_{old_date}.geojson",
               build_bike_routes(older_corridors()))
    write_json(FIXTURE_SNAPSHOT_DIR / f"bike_routes_{new_date}.geojson", build_bike_routes())


def build_wards():
    s, w, n, e = BBOX
    rows, cols = 10, 5
    features = []
    ward = 0
    for r in range(rows):
        for c in range(cols):
            ward += 1
            la0 = s + (n - s) * r / rows
            la1 = s + (n - s) * (r + 1) / rows
            lo0 = w + (e - w) * c / cols
            lo1 = w + (e - w) * (c + 1) / cols
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[
                    [lo0, la0], [lo1, la0], [lo1, la1], [lo0, la1], [lo0, la0]]]},
                "properties": {"ward": str(ward)},
            })
    return {"type": "FeatureCollection", "features": features}


def build_street_centerlines():
    """Synthetic surface-street grid covering the fixture wards, plus a few
    excluded-class/status rows so aggregate's denominator filter is exercised."""
    s, w, n, e = BBOX
    feats = []
    tid = 0

    def seg(coords, klass, status):
        nonlocal tid
        tid += 1
        feats.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"trans_id": str(tid), "class": klass, "status": status,
                           "street_nam": f"FIXTURE {tid}", "street_typ": "ST",
                           "pre_dir": "N", "length": "0"},
        })

    lat = s
    while lat <= n:                       # E-W locals every ~2.2 km
        seg([[w, lat], [e, lat]], "4", "N")
        lat = round(lat + 0.02, 6)
    lng = w
    while lng <= e:                       # N-S locals every ~2.5 km
        seg([[lng, s], [lng, n]], "4", "N")
        lng = round(lng + 0.03, 6)
    # Excluded rows — must NOT count as road miles downstream:
    seg([[w, s], [e, n]], "1", "N")                        # expressway
    seg([[w, (s + n) / 2], [e, (s + n) / 2]], "9", "N")    # ramp
    seg([[(w + e) / 2, s], [(w + e) / 2, n]], "4", "P")    # proposed local
    return {"type": "FeatureCollection", "features": feats}


def jitter_point(rng, lat, lng, sigma_m):
    return (lat + rng.gauss(0, sigma_m) / M_PER_DEG_LAT,
            lng + rng.gauss(0, sigma_m) / m_per_deg_lng(lat))


def random_corridor_point(rng, sigma_m=15):
    street, pts, _ = CORRIDORS[rng.randrange(len(CORRIDORS))]
    dense = interpolate(pts)
    lat, lng = dense[rng.randrange(len(dense))]
    lat, lng = jitter_point(rng, lat, lng, sigma_m)
    return street, lat, lng


def rand_date(rng, start, end):
    span = (end - start).days
    d = start + timedelta(days=rng.randrange(span), hours=rng.randrange(24),
                          minutes=rng.randrange(60))
    return d


def build_crashes_and_people(rng, n=1200):
    start = datetime(2017, 9, 1)
    end = datetime(2026, 7, 1)
    severities = (["FATAL"] * 1 + ["INCAPACITATING INJURY"] * 8 +
                  ["NONINCAPACITATING INJURY"] * 45 + ["REPORTED, NOT EVIDENT"] * 30 +
                  ["NO INDICATION OF INJURY"] * 16)
    crash_types = ["PEDALCYCLIST", "ANGLE", "TURNING", "SIDESWIPE SAME DIRECTION",
                   "REAR END", "FIXED OBJECT", "PARKED MOTOR VEHICLE"]
    lightings = ["DAYLIGHT"] * 6 + ["DARKNESS, LIGHTED ROAD"] * 3 + ["DUSK"]
    crashes, people, vehicles = [], [], []
    s, w, n_, e = BBOX
    for i in range(n):
        cid = f"FIXTURECRASH{i:05d}"
        if rng.random() < 0.7:
            street, lat, lng = random_corridor_point(rng)
        else:
            street = "RANDOM ST"
            lat = rng.uniform(s, n_)
            lng = rng.uniform(w, e)
        d = rand_date(rng, start, end)
        sev = rng.choice(severities)
        dooring = "Y" if rng.random() < 0.06 else "N"
        crashes.append({
            "crash_record_id": cid,
            "crash_date": d.strftime("%Y-%m-%dT%H:%M:%S"),
            "latitude": f"{lat:.6f}", "longitude": f"{lng:.6f}",
            "most_severe_injury": sev,
            "injuries_fatal": "1" if sev == "FATAL" else "0",
            "injuries_incapacitating": "1" if sev == "INCAPACITATING INJURY" else "0",
            "first_crash_type": rng.choice(crash_types),
            "crash_type": "INJURY AND / OR TOW DUE TO CRASH",
            "prim_contributory_cause": "FAILING TO YIELD RIGHT-OF-WAY",
            "lighting_condition": rng.choice(lightings),
            "weather_condition": "CLEAR",
            "roadway_surface_cond": "DRY",
            "posted_speed_limit": str(rng.choice([25, 30, 30, 30, 35])),
            "traffic_control_device": rng.choice(["NO CONTROLS", "TRAFFIC SIGNAL", "STOP SIGN/FLASHER"]),
            "hit_and_run_i": "Y" if rng.random() < 0.12 else "N",
            "dooring_i": dooring,
            "street_no": str(rng.randrange(100, 6000)),
            "street_direction": rng.choice(["N", "S", "E", "W"]),
            "street_name": street,
        })
        people.append({
            "crash_record_id": cid,
            "crash_date": d.strftime("%Y-%m-%dT%H:%M:%S"),
            "person_type": "BICYCLE",
            "injury_classification": sev,
            "age": str(rng.randrange(12, 75)), "sex": rng.choice(["M", "F", "X"]),
            "safety_equipment": rng.choice(["HELMET USED", "NONE PRESENT", "USAGE UNKNOWN"]),
        })
        vehicles.append({
            "crash_record_id": cid, "unit_no": "1", "unit_type": "DRIVER",
            "vehicle_type": rng.choice(["PASSENGER", "PASSENGER", "SPORT UTILITY VEHICLE (SUV)",
                                        "VAN/MINI-VAN", "TRUCK - SINGLE UNIT"]),
            "make": "FIXTURE", "model": "FIXTURE", "vehicle_year": "2020",
            "travel_direction": rng.choice(["N", "S", "E", "W"]),
            "maneuver": rng.choice(["STRAIGHT AHEAD", "TURNING RIGHT", "TURNING LEFT", "PARKED"]),
            "first_contact_point": "FRONT",
        })
    return crashes, people, vehicles


def build_311(rng, n=800):
    start = datetime(2018, 12, 18)
    end = datetime(2026, 7, 1)
    types = ["Bicycle Request/Complaint", "Vehicle Parked in Bike Lane",
             "Bike Lane Debris Removal"]
    rows = []
    for i in range(n):
        street, lat, lng = random_corridor_point(rng, sigma_m=25)
        d = rand_date(rng, start, end)
        rows.append({
            "sr_number": f"SRFIX{i:06d}", "sr_type": rng.choice(types),
            "created_date": d.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": rng.choice(["Completed", "Completed", "Open"]),
            "closed_date": None,
            "street_address": f"{rng.randrange(100, 6000)} {street}",
            "ward": None, "community_area": None,
            "latitude": f"{lat:.6f}", "longitude": f"{lng:.6f}",
        })
    return rows


def build_cameras(rng, n=40):
    rows = []
    for i in range(n):
        street, lat, lng = random_corridor_point(rng, sigma_m=60)
        kind = "speed" if rng.random() < 0.5 else "red_light"
        rows.append({
            "camera_id": f"CAMFIX{i:03d}", "kind": kind,
            "address": f"{rng.randrange(100, 6000)} {street}",
            "lat": round(lat, 6), "lng": round(lng, 6),
            "violations_total": rng.randrange(500, 40000),
            "first_date": "2019-01-01", "last_date": "2026-06-30",
        })
    return rows


def build_ward_demographics(rng):
    return [{"acs_year": "2023", "ward": str(w), "total_population": rng.randrange(30_000, 90_000)}
            for w in range(1, 51)]


FIXTURE_SPONSORS = [f"Alderman FIXTURE-{i}" for i in range(1, 11)]
SAFETY_TITLES = [
    "Protected bike lane installation on FIXTURE Ave",
    "Complete Streets policy amendment for FIXTURE ward",
    "Traffic calming speed humps on FIXTURE St",
    "Vision Zero pedestrian safety improvements at FIXTURE/FIXTURE",
]
NON_SAFETY_TITLES = [
    "Issuance of special event license for Bike the FIXTURE Boulevard (annual)",
    "Damage to vehicle claim for FIXTURE, Jane",
    "Zoning reclassification map at FIXTURE address",
]


def build_council_records(rng, n=20):
    records = []
    for i in range(n):
        is_safety = rng.random() < 0.6
        title = rng.choice(SAFETY_TITLES if is_safety else NON_SAFETY_TITLES)
        sponsors = rng.sample(FIXTURE_SPONSORS, k=rng.randrange(1, 3))
        d = rand_date(rng, datetime(2015, 1, 1), datetime(2023, 6, 21))
        records.append({
            "matter_id": 100000 + i,
            "title": title,
            "type": rng.choice(["Ordinance", "Order", "Resolution"]),
            "status": rng.choice(["Passed", "Referred", "Failed"]),
            "intro_date": d.strftime("%Y-%m-%dT%H:%M:%S"),
            "body": "City Council",
            "sponsors": sponsors,
            "url": f"https://chicago.legistar.com/LegislationDetail.aspx?ID={100000 + i}",
        })
    return {"data_frozen_at": "2023-06-21", "keywords": ["bike", "traffic safety"],
            "records": records}


def build_councilmatic_records(rng, n=8):
    """Synthetic post-2023 council records mirroring pull_councilmatic's output,
    so `run_all.py --fixtures` exercises the two-source merge and the
    recorded_votes path offline."""
    records = []
    for i in range(n):
        is_safety = rng.random() < 0.7
        title = rng.choice(SAFETY_TITLES if is_safety else NON_SAFETY_TITLES)
        sponsors = rng.sample(FIXTURE_SPONSORS, k=rng.randrange(1, 3))
        d = rand_date(rng, datetime(2023, 7, 1), datetime(2026, 6, 1))
        ident = f"O2025-{10000 + i}"
        records.append({
            "matter_id": ident,
            "title": title,
            "type": rng.choice(["ordinance", "resolution", "order"]),
            "status": rng.choice(["Passed", "Introduced", "Referred"]),
            "intro_date": d.strftime("%Y-%m-%dT%H:%M:%S"),
            "body": None,
            "sponsors": sponsors,
            "url": f"https://chicago.councilmatic.org/legislation/{ident}/",
            "source": "councilmatic",
        })
    # One record carries a contested split so the merge + accountability paths run.
    records[0]["recorded_votes"] = {
        "date": "2026-03-18", "yes": 30, "no": 18, "absent": 2,
        "no_voters": rng.sample(FIXTURE_SPONSORS, k=3), "result": "pass",
    }
    return {
        "source": "councilmatic",
        "covers_from": "2023-06-21",
        "latest_action_date": max(r["intro_date"] for r in records)[:10],
        "keywords": ["bike", "traffic safety"],
        "records": records,
    }


def build_menu_spending(rng, n=60):
    categories = ["Street Resurfacing", "Bike Lane Striping", "Traffic Calming",
                  "Sidewalk Repair", "Lighting"]
    items = []
    for i in range(n):
        items.append({
            "ward": str(rng.randrange(1, 51)),
            "cost": round(rng.choice([0, rng.uniform(500, 40_000)]), 2),
            "category": rng.choice(categories),
            "year": rng.choice([2022, 2023, 2024]),
        })
    return items


def build_hearings():
    # pull_hearings.py is a LIVE_STAGES module (network), not run under
    # --fixtures — this mirrors its honest "no structured data" fallback
    # shape so aggregate.py's file-found branch is still exercised in CI.
    return {
        "as_of": "2026-07-11T00:00:00+00:00",
        "structured_data_available": False,
        "note": "Fixture: no public JSON/RSS endpoint confirmed; link-out only.",
        "committees": [
            {"committee": "Committee on Pedestrian and Traffic Safety", "meetings": [],
             "calendar_url": "https://chicityclerkelms.chicago.gov/Meetings?body=Committee+on+Pedestrian+and+Traffic+Safety"},
            {"committee": "Committee on Transportation and Public Way", "meetings": [],
             "calendar_url": "https://chicityclerkelms.chicago.gov/Meetings?body=Committee+on+Transportation+and+Public+Way"},
        ],
    }


# Two named off-street trails in the Overpass `out geom` shape (way elements with
# inline {lat, lon} geometry + tags.name). Lakefront moved here from CORRIDORS so
# the bike_routes fixture matches the real on-street-only CDOT layer.
def build_osm_trails_raw():
    def way(name, pts):
        return {"type": "way", "id": abs(hash(name)) % 100000,
                "tags": {"name": name, "highway": "cycleway"},
                "geometry": [{"lat": la, "lon": lo} for la, lo in pts]}
    return {"elements": [
        way("Lakefront Trail", [(41.750, -87.560), (41.850, -87.610), (41.980, -87.655)]),
        way("North Branch Trail", [(41.980, -87.700), (42.060, -87.760), (42.150, -87.785)]),
    ]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    routes = build_bike_routes()
    wards = build_wards()
    crashes, people, vehicles = build_crashes_and_people(rng)
    sr311 = build_311(rng)
    cameras = build_cameras(rng)
    ward_demographics = build_ward_demographics(rng)
    council_records = build_council_records(rng)
    councilmatic_records = build_councilmatic_records(rng)
    menu_spending = build_menu_spending(rng)
    hearings = build_hearings()
    osm_trails = build_osm_trails_raw()

    write_json(RAW_DIR / "bike_routes.geojson", routes)
    write_json(RAW_DIR / "wards.geojson", wards)
    write_json(RAW_DIR / "street_centerlines.geojson", build_street_centerlines())
    write_json(RAW_DIR / "crashes_cyclist.json", crashes)
    write_json(RAW_DIR / "people_bicycle.json", people)
    write_json(RAW_DIR / "vehicles_cyclist.json", vehicles)
    write_json(RAW_DIR / "sr311_bike.json", sr311)
    write_json(RAW_DIR / "cameras.json", cameras)
    write_json(RAW_DIR / "ward_demographics.json", ward_demographics)
    write_json(RAW_DIR / "council_records.json", council_records)
    write_json(RAW_DIR / "councilmatic_records.json", councilmatic_records)
    write_json(RAW_DIR / "menu_spending.json", menu_spending)
    write_json(RAW_DIR / "hearings.json", hearings)
    write_json(RAW_DIR / "osm_trails.json", osm_trails)
    (RAW_DIR / "PROVENANCE").write_text("fixtures\n")
    write_fixture_snapshots()

    print(f"fixtures: {len(routes['features'])} route segments, {len(wards['features'])} wards, "
          f"{len(crashes)} crashes, {len(sr311)} 311 rows, {len(cameras)} cameras, "
          f"{len(ward_demographics)} ward-pop rows, "
          f"{len(council_records['records'])} legistar + "
          f"{len(councilmatic_records['records'])} councilmatic council rows, "
          f"(seed={args.seed})")


if __name__ == "__main__":
    main()
