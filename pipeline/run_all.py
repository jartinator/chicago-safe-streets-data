"""Run the full pipeline in dependency order — the one-command entry point.

    python run_all.py             # live pull from the Chicago Data Portal
    python run_all.py --fixtures  # offline: synthetic raw data through the real
                                  # join/aggregate stages (used in CI and sandboxes)

Stages:
  1. pull_people          (cyclist filter lives in the People dataset)
  2. pull_crashes, pull_vehicles   (batched CRASH_RECORD_ID lookups)
  3. pull_bike_routes, pull_wards, pull_aldermen (current alderperson roster ->
     site/data/aldermen.json directly), pull_311, pull_cameras, pull_mellow, pull_osm_trails
  4. pull_ward_demographics, restore_frozen (frozen pre-2023 Legistar council records —
     see note below), pull_councilmatic (post-2023 council data — see DECISIONS.md),
     pull_menu_spending, pull_hearings
     (ward-accountability layer — see DECISIONS.md; each is non-fatal on failure)
  5. snapshot_bike_routes (dated copy — builds install-date history over time)
  6. make_mock_obstructions
  7. spatial_join
  8. classify_safety_topic (LLM tagging stage — explicit exception, see CONTRIBUTING.md)
  9. aggregate            (writes site/data/*)

Weekly refresh = run this, review the printed sanity output, commit site/data.
Prints a per-stage timing table at the end so the slowest stages are visible.

Note: pre-2023 council records are FROZEN (Legistar migrated off 2023-06-21), so we no
longer pull them live each run — restore_frozen.py copies a committed snapshot into raw/
instead. Regenerate that snapshot with pull_council_records.py if the schema/keywords
change (see its docstring).
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

from config import RAW_DIR

HERE = Path(__file__).resolve().parent

LIVE_STAGES = [
    ["pull_people.py"],
    ["pull_crashes.py"], ["pull_vehicles.py"],
    ["pull_bike_routes.py"], ["pull_wards.py"], ["pull_aldermen.py"],
    ["pull_311.py"], ["pull_cameras.py"],
    ["pull_mellow.py"], ["pull_osm_trails.py"],
    ["pull_ward_demographics.py"], ["restore_frozen.py"], ["pull_councilmatic.py"],
    ["pull_menu_spending.py"], ["pull_hearings.py"],
]
COMMON_STAGES = [
    ["snapshot_bike_routes.py"],
    ["make_mock_obstructions.py"],
    ["spatial_join.py"],
    ["classify_safety_topic.py"],
    ["aggregate.py"],
]


def write_live_provenance():
    """Stamp raw/PROVENANCE = "socrata" for a live pull.

    aggregate.py records this marker as meta.json's provenance (absent → "socrata").
    make_fixtures.py writes "fixtures" here; without this, a live run performed after
    a prior `--fixtures` run would inherit that stale marker and mislabel real data as
    fixtures. Writing it makes the live path authoritative about its own build type.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "PROVENANCE").write_text("socrata\n")


def run(script_args, timings):
    cmd = [sys.executable, str(HERE / script_args[0]), *script_args[1:]]
    print(f"==> {' '.join(cmd[1:])}")
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=HERE)
    timings.append((script_args[0], time.monotonic() - start))
    if result.returncode != 0:
        print_timings(timings)
        sys.exit(f"stage failed: {script_args[0]} (exit {result.returncode})")


def print_timings(timings):
    """Print a slowest-first per-stage timing table so the expensive stages are obvious."""
    if not timings:
        return
    width = max(len(name) for name, _ in timings)
    print("\n=== stage timings ===")
    for name, secs in sorted(timings, key=lambda t: t[1], reverse=True):
        print(f"  {name:<{width}}  {secs:7.1f}s")
    print(f"  {'TOTAL':<{width}}  {sum(s for _, s in timings):7.1f}s")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixtures", action="store_true",
                    help="generate synthetic raw data instead of pulling from Socrata")
    args = ap.parse_args()

    timings = []
    if args.fixtures:
        run(["make_fixtures.py"], timings)
    else:
        write_live_provenance()
        for stage in LIVE_STAGES:
            run(stage, timings)
    for stage in COMMON_STAGES:
        run(stage, timings)
    print_timings(timings)
    print("run_all: done — site/data is fresh; commit it to publish.")


if __name__ == "__main__":
    main()
