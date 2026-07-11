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

from config import RAW_DIR
from socrata import write_json

# Approximate Chicago corridors: (street, [(lat, lng) endpoints], raw facility label)
CORRIDORS = [
    ("MILWAUKEE AVE", [(41.882, -87.640), (41.917, -87.687), (41.960, -87.760)], "BIKE LANE"),
    ("DAMEN AVE", [(41.870, -87.676), (41.975, -87.679)], "BIKE LANE"),
    ("HALSTED ST", [(41.845, -87.646), (41.950, -87.649)], "BIKE LANE"),
    ("CLARK ST", [(41.900, -87.631), (41.975, -87.660)], "PROTECTED BIKE LANE"),
    ("DEARBORN ST", [(41.870, -87.629), (41.900, -87.629)], "PROTECTED BIKE LANE"),
    ("ELSTON AVE", [(41.900, -87.660), (41.970, -87.740)], "BUFFERED BIKE LANE"),
    ("LAKEFRONT TRAIL", [(41.750, -87.560), (41.850, -87.610), (41.980, -87.655)], "OFF-STREET TRAIL"),
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


def build_bike_routes():
    features = []
    seg_num = 0
    for street, pts, ftype in CORRIDORS:
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

    write_json(RAW_DIR / "bike_routes.geojson", routes)
    write_json(RAW_DIR / "wards.geojson", wards)
    write_json(RAW_DIR / "crashes_cyclist.json", crashes)
    write_json(RAW_DIR / "people_bicycle.json", people)
    write_json(RAW_DIR / "vehicles_cyclist.json", vehicles)
    write_json(RAW_DIR / "sr311_bike.json", sr311)
    write_json(RAW_DIR / "cameras.json", cameras)
    write_json(RAW_DIR / "ward_demographics.json", ward_demographics)
    write_json(RAW_DIR / "council_records.json", council_records)
    (RAW_DIR / "PROVENANCE").write_text("fixtures\n")

    print(f"fixtures: {len(routes['features'])} route segments, {len(wards['features'])} wards, "
          f"{len(crashes)} crashes, {len(sr311)} 311 rows, {len(cameras)} cameras, "
          f"{len(ward_demographics)} ward-pop rows, {len(council_records['records'])} "
          f"council records (seed={args.seed})")


if __name__ == "__main__":
    main()
