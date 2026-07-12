"""Run the full pipeline in dependency order — the one-command entry point.

    python run_all.py             # live pull from the Chicago Data Portal
    python run_all.py --fixtures  # offline: synthetic raw data through the real
                                  # join/aggregate stages (used in CI and sandboxes)

Stages:
  1. pull_people          (cyclist filter lives in the People dataset)
  2. pull_crashes, pull_vehicles   (batched CRASH_RECORD_ID lookups)
  3. pull_bike_routes, pull_wards, pull_311, pull_cameras, pull_mellow
  4. pull_ward_demographics, pull_council_records, pull_councilmatic (post-2023 council data via Councilmatic — see DECISIONS.md), pull_menu_spending, pull_hearings
     (ward-accountability layer — see DECISIONS.md; each is non-fatal on failure)
  5. snapshot_bike_routes (dated copy — builds install-date history over time)
  6. make_mock_obstructions
  7. spatial_join
  8. classify_safety_topic (LLM tagging stage — explicit exception, see CONTRIBUTING.md)
  9. aggregate            (writes site/data/*)

Weekly refresh = run this, review the printed sanity output, commit site/data.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

LIVE_STAGES = [
    ["pull_people.py"],
    ["pull_crashes.py"], ["pull_vehicles.py"],
    ["pull_bike_routes.py"], ["pull_wards.py"], ["pull_311.py"], ["pull_cameras.py"],
    ["pull_mellow.py"],
    ["pull_ward_demographics.py"], ["pull_council_records.py"], ["pull_councilmatic.py"],
    ["pull_menu_spending.py"], ["pull_hearings.py"],
]
COMMON_STAGES = [
    ["snapshot_bike_routes.py"],
    ["make_mock_obstructions.py"],
    ["spatial_join.py"],
    ["classify_safety_topic.py"],
    ["aggregate.py"],
]


def run(script_args):
    cmd = [sys.executable, str(HERE / script_args[0]), *script_args[1:]]
    print(f"==> {' '.join(cmd[1:])}")
    result = subprocess.run(cmd, cwd=HERE)
    if result.returncode != 0:
        sys.exit(f"stage failed: {script_args[0]} (exit {result.returncode})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixtures", action="store_true",
                    help="generate synthetic raw data instead of pulling from Socrata")
    args = ap.parse_args()

    if args.fixtures:
        run(["make_fixtures.py"])
    else:
        for stage in LIVE_STAGES:
            run(stage)
    for stage in COMMON_STAGES:
        run(stage)
    print("run_all: done — site/data is fresh; commit it to publish.")


if __name__ == "__main__":
    main()
