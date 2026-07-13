"""Pull the PeopleForBikes BNA / City Ratings citywide scorecard data.

Three unauthenticated JSON endpoints on bna.peopleforbikes.org (survey in
docs/research/followups/peopleforbikes-bna-evaluation.md): the Chicago
city-ratings record (score history back to 2023), the newest rating's detail
(subscores + low/high-stress mileage), and the all-cities index (for the
national-average and large-city-rank context the findings card carries).
Saved together as pipeline/raw/bna.json; shaping happens in bna_metrics.py.

Like pull_mellow.py this is a third-party host with no uptime guarantee — and
possibly egress-blocked in some pipeline environments — so failure is
non-fatal: it warns and leaves raw/bna.json absent, and aggregate.py falls
back to the committed site/data/bna_scores.json.
"""
import argparse
import sys

import requests

from config import BNA_API_URL, BNA_CITY_RATINGS_PATH, RAW_DIR
from socrata import write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull the PeopleForBikes BNA citywide scorecard for Chicago."
    )
    parser.parse_args()

    try:
        resp = requests.get(f"{BNA_API_URL}/{BNA_CITY_RATINGS_PATH}", timeout=60)
        resp.raise_for_status()
        city_ratings = resp.json()
        history = city_ratings.get("ratings") or []
        if not history:
            print("WARNING: BNA city-ratings returned no ratings for Chicago — "
                  "bna.json will not be written this run.", file=sys.stderr)
            return
        latest_id = max(history, key=lambda r: r.get("created_at") or "")["id"]

        resp = requests.get(f"{BNA_API_URL}/ratings/{latest_id}", timeout=60)
        resp.raise_for_status()
        latest = resp.json()

        resp = requests.get(f"{BNA_API_URL}/cities-index", timeout=120)
        resp.raise_for_status()
        cities_index = resp.json()
    except (requests.RequestException, ValueError, KeyError) as exc:
        print(f"WARNING: BNA pull failed ({exc}) — the committed bna_scores.json "
              f"will keep shipping this run. See DECISIONS.md.", file=sys.stderr)
        return

    write_json(RAW_DIR / "bna.json", {
        "city": city_ratings.get("city"),
        "history": history,
        "latest": latest,
        "cities_index": cities_index,
    })
    print(f"Latest rating: {latest.get('version')} score={latest.get('score')}; "
          f"history entries: {len(history)}; cities in index: {len(cities_index)}")


if __name__ == "__main__":
    main()
