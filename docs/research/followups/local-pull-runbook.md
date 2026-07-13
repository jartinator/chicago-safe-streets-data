# Local runbook — data refresh + portal queries the sandbox can't do

Three tasks that need a machine with normal internet access (the dev
sandbox's egress proxy blocks data.cityofchicago.org and most `.gov`).
Total time: ~20 min plus pipeline runtime.

## 1. Real data refresh (replaces the committed fixture data)

```bash
cd pipeline
python3 -m pip install -r requirements.txt
python3 run_all.py            # live pull from the Chicago Data Portal
```

Review the printed sanity output (row counts, date ranges, % crashes
matched to ward/bikeway — the README's weekly-refresh checklist), then:

```bash
git add site/data data/snapshots
git commit -m "data: live refresh (replaces fixture build)"
```

This also clears the "demo build" banner site-wide and gives the ward
one-pager (PR B) real numbers to render. Do this AFTER merging PRs #15/#16
so the refresh runs the current pipeline (curated-trails fallback, coverage
metrics, network nodes).

## 2. Contracts check — Eco-Counter / Replica (sharpen FOIA item 3–4)

```bash
curl "https://data.cityofchicago.org/resource/rsxa-ify5.json?\$q=eco-counter&\$limit=50"
curl "https://data.cityofchicago.org/resource/rsxa-ify5.json?\$q=replica&\$limit=50"
```

Also try the interactive Vendor/Contract/Payment search
(https://webapps1.chicago.gov/vcsearch) for vendor names "Eco-Counter",
"Eco Counter", "Replica", "Sidewalk Labs". A hit gives the FOIA a contract
number to cite; a miss supports the "developer-funded, agreement-based"
theory (note either way in `docs/foia-log.md`).

## 3. FOIA-precedent check — prior bike-count requests to CDOT

```bash
for q in "bicycle count" "bike count" "bike counter" "eco-counter" "replica"; do
  echo "== $q"
  curl -s "https://data.cityofchicago.org/resource/u9qt-tv7d.json" \
    --data-urlencode "\$q=$q" --data-urlencode "\$limit=100" -G \
    | python3 -m json.tool | head -80
done
```

(Field names vary by log; `$q` full-text search avoids guessing the
column. If the dataset ID errors, search the portal for "FOIA Request Log -
Transportation".) Prior granted requests = precedent to cite in the letter;
prior denials = wording to avoid. Note findings in `docs/foia-log.md`, then
send `docs/foia-cdot-counter-request-letter.md` after its checklist.

## Order of operations this week

1. Merge PRs #15 and #16.
2. Run §1 (refresh) — unblocks real numbers for PR B review.
3. Run §2 + §3 (5 min), finish the letter's checklist, file the FOIA.
4. Submit the Strava Metro application
   (`strava-metro-application.md`).
