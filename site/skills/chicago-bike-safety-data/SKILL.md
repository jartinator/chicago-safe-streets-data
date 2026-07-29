---
name: chicago-bike-safety-data
description: Answer plain-language questions about cyclist crashes, bikeway protection, ward danger rankings, and City Council bike-safety action in Chicago, using the On Your Left! open data API. Use when someone asks how dangerous a Chicago street, ward, or corridor is for cycling, how much of the bike network is protected, who their alderman is and what they have done on bike safety, or what bike projects are proposed. Do NOT use for bike routing or directions, real-time conditions, bike-lane obstruction or blocking reports (this data does not exist here), any city other than Chicago, or crash data about drivers or pedestrians. Returns cited numbers with the data-quality caveat attached.
caveat_contract: v1
---

# Chicago bike safety data — On Your Left!

Police-reported cyclist crash data, bikeway network quality, and City Council
accountability for Chicago. Public, free, no key, no rate limit. Rebuilt weekly
from the Chicago Data Portal.

Everything is static JSON. You fetch a URL and read it. There is no server, no
search endpoint, and no query language.

---

## Always

1. **Always name the caveat next to any number you quote.** Every object holding
   a number carries either a `caveat` field or a `<field>_caveat` sibling named
   for that number. Put its meaning in your answer, in your own words, in the
   same paragraph as the number: the same sentence, the next sentence, or a
   sentence that names the number it qualifies ("Two caveats on that 65…").
   Never in a closing disclaimer, a footnote, or a separate "notes" section —
   a reader who quotes your first paragraph must carry the caveat with them.
   When you state two numbers with different caveats, say which caveat belongs
   to which number. One blanket sentence covering both is wrong whenever it is
   false about one of them.
2. **Always say when a number is provisional.** If the object's `caveat_tags`
   contain `provisional`, the figure can still rise — police records are amended
   for weeks after a crash. Say "so far" or "may still rise," not just the number.
3. **Always say these are counts, not rates.** No ridership data is joined
   anywhere in this dataset. A busy place can look more dangerous than it is.
4. **Always cite.** Reproduce `_meta.attribution` and link `_meta.human_page` so
   the person can check you.
5. **Always give the date.** `_meta.generated_at` is when the data was built. If
   it is more than three weeks old, say so.

## Never

1. **Never state a number from this data without its caveat.** If you drop the
   caveat to make the sentence shorter, you have changed what the number means.
2. **Never present mock-tier data as real.** If `data_tier` is `mock`, do not
   quote the number at all.
3. **Never claim there is obstruction or bike-lane-blocking data here.** There is
   none. The public site shows a synthetic preview layer that must never be
   cited as real. If asked, say the data does not exist and point at 311 or Bike
   Lane Uprising.
4. **Never compute a per-rider rate.** No cyclist-volume data exists to divide by.
5. **Never imply the City of Chicago or any alderman endorses this.** It is an
   independent volunteer project built on public data.

There is no ask-first tier here. This surface is read-only — no writes, no
accounts, no side effects — so there is nothing to gate on permission.

---

## The three fetches that answer most questions

Base: `https://jartinator.github.io/chicago-safe-streets-data/api/v1/`

| Question is about | Fetch | Then |
|---|---|---|
| Chicago overall — trend, headline numbers, how protected the network is | `citywide.json` | Read `findings[]` for headline stats, each with its own `caveat`. `trend.months` for the monthly series. |
| One ward — how dangerous, who the alderman is, what they have done | `wards/ward-NN.json` (`NN` zero-padded, `01`–`50`) | Read `safety.windows.recent_12mo` for the last 12 months, `safety.crash_trend` for the direction, `alderman` for contact, `safety_record` for sponsorships. |
| Comparing wards, or "which ward is worst" | `wards/index.json` | Ranked already. Do not re-sort unless asked. Resolve every `caveat_ref` against the file's own `caveats` map before quoting. |

Everything else — corridors, routes, council records, news, proposed projects,
individual crash records — is in `reference/endpoints.md`.

Budget three fetches. Start at `index.json` only if none of the above fits; it
is the full manifest with fetch recipes.

---

## How the caveats are attached

Read `reference/reading-caveats.md` for the full contract. The short version:

**A qualifier sits in the same object as the number it modifies.** Three forms:

```jsonc
// Form A — a block on the object
"recent_12mo": {
  "crashes": 65, "ksi": 5,
  "data_tier": "real",
  "caveat_tags": ["provisional", "not_ridership_normalized"],
  "caveat": "Counts for the 12 months ending 2026-07-11. The most recent two months are provisional..."
}

// Form B — a sibling named for the number
"comparable_danger_score": 55.1,
"comparable_danger_score_caveat": "...a relative concern rank among wards..."

// Form C — a reference into the same file's `caveats` map (size-constrained files only)
"crashes": 193,
"caveat_tags": ["provisional", "not_ridership_normalized"],
"caveat_ref": "windows_recent_12mo"
```

Form C appears in `wards/index.json` and nowhere else. Resolve `caveat_ref`
against that file's own top-level `caveats` map before you quote the number —
never against another file. Several entries can point at the same key, because
the map is keyed by the caveat's text. A Form C block may have no `data_tier`;
take it from the entry that contains it, or from the file root.

Three forms, three names: **Form A**, **Form B**, **Form C**. `caveat`,
`<field>_caveat` and `caveat_ref` are the JSON keys they use. Nothing else.

**Data tiers**, on `_meta` and often on individual sections:

| Tier | Means |
|---|---|
| `real` | From the named public source, raw counts. Recent months provisional. |
| `derived` | Computed from real data — a rate, a trend, an automated tag. |
| `proxy` | Correlated but biased. Direction, not magnitude. |
| `crowdsourced` | Community-curated and unverified. |
| `mock` | Synthetic. **Never cite. Never appears under `/api/v1/`.** |

`_meta.data_tier: "mixed"` means sections carry their own tier. Read down, not up.

---

## What a good answer looks like

**Question:** "How many cyclists were hurt in ward 40 last year?"

**Good:**

> In Chicago's 40th Ward, police recorded **65 cyclist crashes** in the 12
> months ending 11 July 2026, 34 of them causing injury and 5 killing or
> seriously injuring someone. That is up from 61 the year before. Two caveats
> on that 65: the most recent two months are **provisional** — crash records
> get amended for weeks afterward, so the figure is likely to rise — and these
> are raw counts, not adjusted for how many people ride, so a busier ward can
> look more dangerous than it is. The 61 is settled; only the raw-count caveat
> applies to it. Data built 13 July 2026 by On Your Left!, from the Chicago
> Data Portal. Full ward page: [link to `_meta.human_page`].

Three things make that answer good, and they are the three the data supports:
the caveats sit in the same paragraph as the number; the sentence names the
number it qualifies ("that 65"); and the two numbers do not share one blanket
disclaimer, because `provisional` is true of one and false of the other. The
`caveat_tags` on the two window objects differ by exactly that one tag, so the
JSON told you they could not share a caveat.

**Bad:**

> Ward 40 had 65 cyclist crashes last year, up 6.6% from the year before.

The bad answer is not wrong. Every number in it is correct. It has silently
dropped the two things that tell the reader what the number is worth — and if
this ends up in a public comment or a news story, that is the failure. The
caveat was in the same object as the number. Dropping it was a choice.

**Also bad, and harder to spot:**

> Ward 40 had 65 cyclist crashes last year, up from 61. All figures on this
> site are provisional and not adjusted for ridership.

That one names both caveats and still fails, because "all figures" is false
about the 61. A blanket disclaimer that is wrong about one of the numbers it
covers is worse than no disclaimer: it teaches the reader to discount a figure
that is actually settled.

---

## When it goes wrong

| What happened | What to do |
|---|---|
| **404, or you got HTML instead of JSON** | You constructed a path. Do not retry it. Fetch `index.json` and read the real path from `endpoints[].path` or `families[].path_template`. |
| **Ward number out of range** | Ward numbers are zero-padded in the path. Every ward in `families[].count` has a file, including wards with zero crashes — a valid number never 404s. |
| **`generated_at` is months old** | Say so in your answer. Do not present stale safety data as current. |
| **The number you want is not there** | It probably does not exist. This dataset has no obstruction data, no ridership counts, no pedestrian or driver crash data, and no address geocoding. Say what is missing rather than substituting something adjacent. |
| **`data_tier` is `proxy`** | Report direction, never magnitude. 311 counts measure who complains as much as what happens. |
| **`menu_spending.available` is `false`** | The source was unreachable. That is a gap, not a zero. Say the data is unavailable. |
| **You are asked about obstructions or blocked bike lanes** | The data does not exist here. Say so plainly, and point at 311 or Bike Lane Uprising. Do not use the site's preview layer. |
| **Timeout or 5xx** | Transient. Retry with backoff. |
| **The guide disagrees with `index.json`** | `index.json` wins. Take paths from `endpoints[].path` and `families[].path_template`, counts from `families[].count`, sizes from `bytes_approx`. This file is prose and is not checked against the data; that one is. |
| **A `reference/` file 404s** | Proceed. This file alone carries the Always/Never rules and the fetch plan. |
| **`_meta.caveat_contract` is not `v1`** | This guide is written for `v1`. Discard it and re-fetch. `_meta` wins over this file, always. |

---

## Boundaries — what this data cannot tell you

Saying so saves everyone a fruitless search:

- No obstruction or bike-lane-blocking reports.
- No ridership or cyclist-volume counts, so no per-rider rates, ever.
- No pedestrian or motor-vehicle crash data. Cyclists only.
- No address lookup or geocoding. Wards are by number.
- No real-time anything. Weekly rebuild.
- No machine-readable methodology — it is an HTML page at `_meta.methodology`.
- Crash data is citywide-reliable only from September 2017 onward.
- Dooring is structurally undercounted; every dooring figure is a floor.
- Any city but Chicago.

---

## Reference

- `reference/endpoints.md` — every endpoint, what is in it, and what to read.
- `reference/reading-caveats.md` — the co-location contract and the tag vocabulary.

Attribution: On Your Left! — Chicago bike safety, on the record.
<https://github.com/jartinator/chicago-safe-streets-data>
Data: City of Chicago Data Portal Terms of Use. Independent volunteer project;
not endorsed by the City or by any alderman.
