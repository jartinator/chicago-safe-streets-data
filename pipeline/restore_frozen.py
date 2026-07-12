"""Restore committed snapshots of frozen upstream data into raw/ (replaces a live pull).

Some upstream sources are immutable and re-fetching them every run is pointless and a
needless failure point. The pre-2023 Legistar council records are the case that motivated
this: Chicago's City Council migrated off Legistar around 2023-06-21
(LEGISTAR_DATA_FROZEN_AT), so those records can never change. We snapshot them once (with
pull_council_records.py) into pipeline/frozen/ and commit that, then this stage copies the
snapshot into raw/ so every downstream consumer (council_merge.py, classify_safety_topic.py,
aggregate.py) reads raw/council_records.json exactly as it did when the pull was live.

To regenerate a snapshot (e.g. the keyword net or Legistar schema changed): run the
matching pull_*.py once, then copy its raw/ output into pipeline/frozen/ and commit it.

Usage: python restore_frozen.py
"""
import argparse
import shutil
import sys

from config import FROZEN_DIR, RAW_DIR

# Frozen files to restore: (filename in FROZEN_DIR, same filename in RAW_DIR).
FROZEN_FILES = ["council_records.json"]


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    restored = 0
    for name in FROZEN_FILES:
        src = FROZEN_DIR / name
        if not src.exists():
            # Non-fatal, mirroring pull_council_records.py: downstream falls back to a stub
            # if raw/council_records.json is absent.
            print(f"restore_frozen: WARNING - {src} not found; skipping {name}", file=sys.stderr)
            continue
        shutil.copyfile(src, RAW_DIR / name)
        restored += 1
        print(f"restore_frozen: {name} -> raw/ ({src.stat().st_size} bytes)")
    if restored == 0:
        print("restore_frozen: 0 files restored", file=sys.stderr)


if __name__ == "__main__":
    main()
