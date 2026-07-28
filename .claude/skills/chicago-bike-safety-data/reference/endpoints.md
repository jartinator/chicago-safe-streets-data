# Endpoints

Base: `https://jartinator.github.io/chicago-safe-streets-data/api/v1/`

All static JSON. No key, no rate limit, no query parameters. Every file opens
with a `_meta` envelope carrying provenance, tier, license, attribution, the
matching human page, the methodology link, and its own JSON Schema URL.

Byte sizes are approximate and from the 2026-07-13 build. The published cap is
100,000 bytes per file, 150,000 for crash slices.

---

## Start here, if nothing below fits

**`index.json`** (~10 KB) — the full manifest. Every endpoint with example
questions, every file family with its path template, and `fetch_recipes`
pairing a question with the files to fetch and what to read in them. It also
carries an `integration` object where present — stability, refresh cadence, the
caveat contract, identifiers and limits — for building software against this
data. Read it from the file; do not assume it is there.

---

## Citywide

**`citywide.json`** (~15 KB)

The best-designed file in the API for quoting: `findings[]` is an array of
headline stats, and **every finding carries its own `caveat` next to its
`stat`**. Use those caveats verbatim in meaning, if not in wording.

- `findings[]` — killed-or-seriously-injured trend, protected share of the
  network, street-grid coverage, top crash corridors, hit-and-run share, ward
  concentration, dooring undercount, national network score.
- `trend.months` — 107 months of citywide counts since September 2017. The
  trailing entries are provisional.
- `bikeway_mileage.series` — miles by facility type across dated snapshots.
- `protected_share` — the derived protected percentage. May be absent.

Answers: "Is cycling in Chicago getting more dangerous?" · "How much of the bike
network is protected?" · "How does Chicago's bike network rank nationally?"

---

## Wards

**`wards/index.json`** (~80 KB) — all 50 wards, already ranked, with danger
scores, crash counts, bikeway stats, and a `detail_url` per ward. Do not
re-sort unless asked. This file uses **Form C**: resolve each `caveat_ref`
against the file's own top-level `caveats` map before quoting. If you are going
to quote a ward's numbers rather than rank them, follow `detail_url` — the ward
file carries the same numbers with the caveat written out beside them.

Answers: "Which ward is worst for cyclists?" · "How does my ward compare?"

**`wards/ward-NN.json`** (~15-21 KB, `NN` is `01`-`50` zero-padded)

The single best fetch for a ward question — it bundles five things that would
otherwise be five files.

- `safety.windows.recent_12mo` / `prior_12mo` — the two 12-month crash windows.
  **The recent one is provisional; the prior one is not.** They carry different
  caveats on purpose. Do not merge them into one disclaimer.
- `safety.crash_trend` — direction and percent change. On low-count wards this
  is noisy and the caveat says so.
- `safety.monthly` — 107 months for this ward. The trailing entries carry their
  own `caveat_tags`.
- `safety.comparable_danger_score` — a **relative rank among the 50 wards**,
  higher is worse. Not an absolute risk and not a probability.
- `alderman` — name, email, phone, website, from the city's own Ward Offices
  dataset.
- `safety_record` — that alderman's tagged bike-safety sponsorships, with links
  to the official record. Matched by exact name only, so an empty list can mean
  "unmatched," not "did nothing."
- `sr311` — bike-related 311 requests. **Proxy tier**: it reflects who
  complains as much as what happens.
- `menu_spending` — often `{"available": false}`. That is a gap, not a zero.
- `crashes_url`, `one_pager_url`, `see_also` — where to go next.

Answers: "How dangerous is ward 40?" · "Who is my alderman and what have they
done on bike safety?" · "Is my ward getting better or worse?"

---

## Streets and routes

**`corridors.json`** (~44 KB) — per-street crash rates, facility mix, and
labelled hotspot intersections. `crashes_per_km` inflates short segments and is
not normalized by how many people ride. Say both.

**`routes/index.json`** (~17 KB) — the named main bike routes with
mileage-by-grade, crash totals, protected share, and network interchanges. The
roster is editorial and recomputed each build: read `count` and the slug list
from the file. Do not restate a number from here.

**`routes/line-{slug}.json`** (~3 KB) — one route's segment-level detail. Get
the slug list from `routes/index.json`; never construct one from a street name.

Answers: "Which streets are worst for cyclists?" · "How protected is Milwaukee
Avenue?" · "Where are the worst intersections?"

---

## Crashes

**`crashes/ward-NN.json`** (up to ~146 KB) — one ward's cyclist crash records
as columnar rows: `crash_id`, `date`, `lat`, `lng`, `injury_severity`,
`dooring`, `hit_and_run`, `street`.

Rows are columnar — zip the `columns` array with each row. `crash_id` is a
16-hex-character prefix of the full source id, lossy by design. `lat`/`lng` are
rounded to five decimal places. Three columns (`crash_type`, `lighting`,
`segment_id`) are dropped; the full records are at `full_data_url`.

Every ward has a file, including wards with zero crashes.

Answers: "List recent cyclist crashes in ward 40" · "How many dooring crashes
in ward 27?"

---

## City Council

**`council/index.json`** (~8 KB) — upcoming and recent bike-safety-relevant
committee hearings, plus a summary of tagged legislative activity.

**`council/records.json`** (~83 KB) — individual ordinances and resolutions
tagged bike/street-safety, with sponsors, status, dates, and official links.
Topic tagging is partly automated (`derived` tier) — an incidental match is
possible.

**`council/aldermen.json`** (~26 KB) — the 50-ward roster with contact info and
each member's sponsorship record.

Note on `recorded_no_votes`: most council street-safety actions pass by voice
vote with no individual vote recorded, so this is near zero for nearly everyone
**by design, not by omission.** Do not read a zero as approval.

Answers: "Has council held hearings on bike safety?" · "Which alderman sponsors
the most bike-safety legislation?" · "Is there a hearing coming up?"

---

## Context

**`news.json`** (~35 KB) — recent bike/street-safety coverage, matched to wards,
alderpersons, routes, and projects. Links only; headlines and outlets are real,
the matching is automated.

**`proposed.json`** (~12 KB) — curated roster of proposed and in-progress
bikeway and trail projects with volunteer-reviewed status and official links.
Status is hand-reviewed, so check `status_as_of`.

Answers: "What's the latest news about bike safety in my ward?" · "What's the
status of the 606 extension?"

---

## What is deliberately not here

- **Obstruction / blocked bike lane data.** None. The public site shows a
  synthetic preview layer that has no endpoint here and must never be cited as
  real.
- **Ridership or cyclist volume.** None joined, so no per-rider rates.
- **Pedestrian or motor-vehicle crashes.** Cyclists only.
- **Address geocoding.** Wards by number.
- **Machine-readable methodology.** HTML only, at `_meta.methodology`.
- **Anything before September 2017.** Crash data is citywide-reliable only from
  that date.
