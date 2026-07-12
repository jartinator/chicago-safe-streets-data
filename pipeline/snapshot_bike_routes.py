"""Save a dated snapshot of the CDOT Bike Routes layer to build install history.

The Bike Routes dataset has no install-date field and is current-state only, so
the only way to know when a lane appeared or was upgraded is to snapshot the
layer regularly (start now, per the capability report). Snapshots land in
data/snapshots/bike_routes_YYYY-MM-DD.geojson; diffing two snapshots yields
"installed/changed between" evidence.

Usage: python snapshot_bike_routes.py   (after pull_bike_routes.py)
"""
import argparse
import shutil
import sys
from datetime import date

from config import RAW_DIR, SNAPSHOT_DIR, FIXTURE_SNAPSHOT_DIR


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    src = RAW_DIR / "bike_routes.geojson"
    if not src.exists():
        sys.exit("raw/bike_routes.geojson not found — run pull_bike_routes.py first")
    # A --fixtures run's raw/bike_routes.geojson is synthetic. make_fixtures.py already
    # seeds two deterministic fixture snapshots (in FIXTURE_SNAPSHOT_DIR), so snapshotting
    # here would be redundant and — worse — copying synthetic data into the real
    # SNAPSHOT_DIR would corrupt the committed history. Skip; snapshots are a live concern.
    provenance = ((RAW_DIR / "PROVENANCE").read_text().strip()
                  if (RAW_DIR / "PROVENANCE").exists() else "socrata")
    if provenance == "fixtures":
        print("snapshot: skipped (fixtures own their snapshots in "
              f"{FIXTURE_SNAPSHOT_DIR.name}/)")
        return
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    dst = SNAPSHOT_DIR / f"bike_routes_{date.today().isoformat()}.geojson"
    shutil.copyfile(src, dst)
    existing = sorted(SNAPSHOT_DIR.glob("bike_routes_*.geojson"))
    print(f"snapshot: wrote {dst.name} ({len(existing)} snapshots total)")


if __name__ == "__main__":
    main()
