"""Smart Streets camera enforcement, redacted from DOF FOIA F146238-072126.

DOF released 112,318 violation records on 2026-07-28 — every warning and citation
issued by the bike-lane, bus-lane, and bus-stop cameras from 2024-11-06 onward.
It is the first enforcement data the project has held with a named actor behind
each record.

**This module exists because the released file cannot be published.** DOF withheld
license plates and addresses under 5 ILCS 140/7(1)(b)-(c), but left `Owner First
Name` and `Owner Last Name` populated. 82,880 rows (73.8%) therefore name a
private individual next to the violation they received, its address, and its
timestamp — which is precisely what OYL's own request offered to give up in
exchange for the business names it actually wanted.

So the source `.xlsx` is gitignore'd and stays on local disk. This module reads it
and writes a name-free CSV that is safe to commit and safe to build on. Everything
downstream reads the CSV. Nothing downstream should ever open the xlsx.

Run to regenerate the committed output:

    python pipeline/foia_smart_streets.py

On a fresh clone the source will be absent. That is expected, not an error: the
CSV is committed, and this script simply declines to run.

## The redaction rule

Names survive only when the registrant is confidently an **organization**. The
default is redaction, not disclosure — an unclassifiable row loses its name.

A row is a business only if it has no first name *and* its owner field carries an
explicit organizational token (`INC`, `LLC`, `TRUST`, `RENTAL`, ...). A row with a
first name is an individual, always. A row with neither a first name nor a
recognizable token is `unknown`, and is redacted like an individual — there is no
category whose benefit of the doubt runs toward publishing a name.

## Two caveats the data forces on any consumer

1. **76% of rows are zero-fine warnings.** `is_warning` separates them. A count of
   "violations" that does not exclude warnings overstates enforcement roughly
   fourfold, and the pilot's first month is almost entirely installation warnings.
2. **One company, many spellings.** FEDERAL EXPRESS, FEDERAL EXPRESS CORP, and
   FEDERAL EXPRESS CORPORATION are three strings for one fleet.
   `registrant_normalized` folds legal suffixes so they group; rank on that
   column, never on `registrant`.

A third, softer caveat: rental and leasing companies (Enterprise, Hertz, PV
Holding) rank high because the *lessor* is the registered owner, not the driver.
They are not comparable to a delivery fleet and should not share a ranking with
one without saying so.
"""
import csv
import re
import sys
from collections import Counter

from config import (
    SMART_STREETS_RAW_XLSX,
    SMART_STREETS_VIOLATIONS_PATH,
)

SHEET = "Sheet 1"

# Tokens that mark the owner field as an organization rather than a person.
# `LSE`/`LSR` are the City's own lessee/lessor markers and appear as trailing
# words on fleet registrations. Deliberately generous: a false "business" only
# happens when the row also lacks a first name, and the suffix list below strips
# these again before grouping.
BUSINESS_TOKENS = frozenset(
    """
    INC INCORPORATED LLC LLP LP CORP CORPORATION CO COMPANY LTD LIMITED
    TRUST HOLDINGS HOLDING GROUP ENTERPRISES ENTERPRISE PARTNERS ASSOCIATES
    RENTAL RENTALS LEASING LEASE LSE LSR FLEET FLEETS
    SERVICES SERVICE SYSTEMS SYSTEM SOLUTIONS LOGISTICS TRANSPORT
    TRANSPORTATION TRUCKING EXPRESS DELIVERY DISTRIBUTORS DISTRIBUTING
    CONSTRUCTION CONTRACTORS PLUMBING ELECTRIC MECHANICAL
    BANK FINANCIAL CREDIT INSURANCE MOTORS AUTO AUTOMOTIVE
    HOSPITAL MEDICAL HEALTH CLINIC UNIVERSITY COLLEGE SCHOOL CHURCH
    FOUNDATION INSTITUTE ASSOCIATION SOCIETY COUNCIL AUTHORITY
    DEPT DEPARTMENT CITY COUNTY STATE FEDERAL MUNICIPAL
    RESTAURANT PIZZA CATERING FOODS BEVERAGE BREWING
    PROPERTIES REALTY MANAGEMENT DEVELOPMENT BUILDERS
    """.split()
)

# Stripped from the tail of a business name before grouping, so that
# FEDERAL EXPRESS / FEDERAL EXPRESS CORP / FEDERAL EXPRESS CORPORATION collapse.
# Order matters only in that this runs repeatedly until nothing more comes off.
TRAILING_SUFFIXES = frozenset(
    "INC INCORPORATED LLC LLP LP CORP CORPORATION CO COMPANY LTD LT LIMITED "
    "TRUST LSE LSR THE".split()
)

# Fleet/unit numbers the City appends to some large registrants — the release
# carries FEDERAL EXPRESS 225877, FEDERAL EXPRESS CORP 224670, and others that
# are one fleet split across dozens of strings. Four digits or more, so a real
# name like STUDIO 41 keeps its number.
FLEET_NUMBER = re.compile(r"^\d{4,}$")

OUTPUT_COLUMNS = (
    "ticket_number",
    "issued_date",
    "location",
    "ward",
    "violation_code",
    "violation_description",
    "fine",
    "ticket_queue",
    "is_warning",
    "registrant_type",
    "registrant",
    "registrant_normalized",
)


def classify(last_name, first_name):
    """Return 'individual', 'business', or 'unknown' for one owner field.

    Privacy-first: only an explicit organizational token earns 'business'.
    Anything else is treated as a person, because being wrong in that direction
    costs a data point and being wrong in the other direction publishes a name.
    """
    if first_name and str(first_name).strip():
        return "individual"
    if not last_name:
        return "unknown"
    words = set(re.sub(r"[^A-Z0-9 ]", " ", str(last_name).upper()).split())
    return "business" if words & BUSINESS_TOKENS else "unknown"


def normalize_business(name):
    """Fold a business name to a grouping key.

    Uppercases, drops punctuation, then strips legal suffixes and fleet numbers
    from the tail until none remain. 'FEDERAL EXPRESS CORPORATION' and
    'FEDERAL EXPRESS 225877' both collapse to 'FEDERAL EXPRESS'.
    """
    words = re.sub(r"[^A-Z0-9 ]", " ", str(name).upper()).split()
    while words and (words[-1] in TRAILING_SUFFIXES or FLEET_NUMBER.match(words[-1])):
        words.pop()
    while words and words[0] in TRAILING_SUFFIXES:
        words.pop(0)
    return " ".join(words)


def is_warning(description, fine):
    """True when the record carries no monetary penalty.

    Both signals agree across the 2026-07-28 release (85,512 rows), but a zero
    fine is the load-bearing test — a future description string need not contain
    the word WARNING to be one.
    """
    if fine in (None, "", 0):
        return True
    return "WARNING" in str(description or "").upper()


def read_rows(path):
    """Yield redacted output dicts from the released workbook."""
    import openpyxl

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook[SHEET]
    rows = sheet.iter_rows(values_only=True)
    header = next(rows)
    if header[0] != "Ticket Number" or header[9] != "Owner First Name":
        raise SystemExit(
            f"unexpected column layout in {path.name}: {header!r}\n"
            "DOF changed the export. Re-read the file before trusting this script."
        )

    for row in rows:
        (
            ticket,
            issued,
            location,
            ward,
            code,
            description,
            fine,
            queue,
            last_name,
            first_name,
        ) = row[:10]

        kind = classify(last_name, first_name)
        # The redaction itself. Only a confirmed organization keeps its name.
        registrant = str(last_name).strip() if kind == "business" and last_name else ""
        yield {
            "ticket_number": ticket,
            "issued_date": issued.isoformat(sep=" ") if hasattr(issued, "isoformat") else issued,
            "location": location or "",
            "ward": ward or "",
            "violation_code": code or "",
            "violation_description": description or "",
            "fine": fine if fine is not None else "",
            "ticket_queue": queue or "",
            "is_warning": "true" if is_warning(description, fine) else "false",
            "registrant_type": kind,
            "registrant": registrant,
            "registrant_normalized": normalize_business(registrant) if registrant else "",
        }


def build():
    if not SMART_STREETS_RAW_XLSX.exists():
        print(
            f"source not present: {SMART_STREETS_RAW_XLSX}\n"
            "This is normal on a clone — the released workbook names private\n"
            "individuals and is deliberately not in the repository. The committed\n"
            f"CSV at {SMART_STREETS_VIOLATIONS_PATH.name} is the usable artifact.",
            file=sys.stderr,
        )
        return 0

    records = list(read_rows(SMART_STREETS_RAW_XLSX))

    # The guarantee this whole module exists to provide. If it ever fails, the
    # output is not safe to commit and the run must not produce a file.
    leaked = [r for r in records if r["registrant"] and r["registrant_type"] != "business"]
    if leaked:
        raise SystemExit(
            f"REDACTION FAILED: {len(leaked)} non-business rows carry a name. "
            "Refusing to write. First offender: " + repr(leaked[0])
        )

    SMART_STREETS_VIOLATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SMART_STREETS_VIOLATIONS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(records)

    kinds = Counter(r["registrant_type"] for r in records)
    warnings = sum(1 for r in records if r["is_warning"] == "true")
    print(f"wrote {len(records):,} rows -> {SMART_STREETS_VIOLATIONS_PATH}")
    print(f"  named (business):  {kinds['business']:,}")
    print(f"  redacted (individual): {kinds['individual']:,}")
    print(f"  redacted (unknown):    {kinds['unknown']:,}")
    print(f"  warnings (no fine):    {warnings:,} ({warnings / len(records):.1%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
