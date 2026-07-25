# Reading the caveats

`caveat_contract: "v1"` — declared in every file's `_meta`.

## The one rule

**A number and the qualifier that makes it honest are in the same object, or
adjacent keys in one object.** Never in another file. Never a fetch away.

That is a promise the publisher makes to you: if you loaded the number, you
loaded the caveat. There is no second request to make and nothing to go look
up. Which also means that if the caveat is missing from your answer, you took
it out.

---

## The three forms

### Form A — a block on the object

The object holds `data_tier`, `caveat_tags`, and `caveat`, and they apply to
**every number in that object**.

```json
"recent_12mo": {
  "crashes": 65,
  "injury_crashes": 34,
  "ksi": 5,
  "fatal": 0,
  "data_tier": "real",
  "caveat_tags": ["provisional", "not_ridership_normalized"],
  "caveat": "Counts for the 12 months ending 2026-07-11. The most recent two months are provisional — police crash records are amended for weeks after a crash, so these figures can rise. Counts are not adjusted for how many people ride, so a busier place can look more dangerous than it is."
}
```

The caveat covers all four numbers. It is written to be quotable on its own.

### Form B — a sibling named for the number

When a number sits on an object whose block does not cover it, its qualifier is
a sibling key **named for it**:

```json
"comparable_danger_score": 55.1,
"comparable_danger_score_caveat_tags": ["relative_rank"],
"comparable_danger_score_caveat": "comparable_danger_score is a relative concern rank among Chicago's 50 wards, higher = worse. It is not an absolute risk measure and it does not convert to a probability."
```

If you see `<something>_caveat`, it belongs to `<something>`. The key name is
the binding.

### Form C — a reference inside the same file

Only in files that would otherwise blow their size budget — currently
`wards/index.json` alone.

```json
"crashes": 193,
"injury_crashes": 87,
"caveat_tags": ["provisional", "not_ridership_normalized"],
"caveat_ref": "windows_recent_12mo"
```

Resolve it against the file's own top-level `caveats` map. **The reference
never crosses files.** If you cannot resolve it in the file you fetched, the
data is malformed — say so rather than quoting the number bare.

Two things about Form C that Forms A and B do not have:

- **Keys are shared.** The map is keyed by the caveat's text, so many entries
  point at the same key. `windows_recent_12mo` is one string used by all 50
  wards. Seeing the same key twice is normal, not an error.
- **`data_tier` may be missing.** Take it from the nearest enclosing object —
  the ward entry, or the file root. Both are in the file you already have.

Form C is the weakest of the three by design: it is the only one where the
caveat is not literally beside the number. Where a Form A or Form B version of
the same claim exists — and for every ward it does, in `wards/ward-NN.json` —
prefer that file if you are going to quote the number rather than rank it.

### Series

A series carries its qualifier on the array's container, and items that differ
carry their own tags:

```json
"monthly_caveat": "Monthly counts of police-reported cyclist crashes through 2026-07-11. The last 2 entries are provisional...",
"monthly": [
  {"month": "2026-05", "crashes": 6},
  {"month": "2026-06", "crashes": 10, "caveat_tags": ["provisional"]},
  {"month": "2026-07", "crashes": 4,  "caveat_tags": ["provisional"]}
]
```

If you chart or total the series, exclude or visibly mark the tagged tail.

---

## The tags

`caveat_tags` is the machine-readable twin of the prose. The prose is what goes
in your answer; the tags tell you which *kind* of qualification applies, so use
them to decide what to say.

| Tag | What your answer must convey |
|---|---|
| `provisional` | The number may still change. Say "so far" or "may rise," not just the figure. |
| `not_ridership_normalized` | It is a count, not a rate. More people riding can mean more crashes. |
| `small_n` | The count, or the stretch of road a rate is spread over, is small. The percent change or the rate is mostly noise. Do not lead with it. |
| `relative_rank` | It ranks wards against each other. Not an absolute risk, not a probability. |
| `self_reported` | The public reported it — a 311 request, not a police record. It reflects who reports as much as what happens. Direction, not magnitude. |
| `third_party_method` | Computed elsewhere, by a method that has changed. Not comparable across distant versions. |
| `coverage_gap` | It is a floor. The real number is higher. |
| `snapshot_derived` | Built from dated snapshots, not from an install record. Timing is approximate. |
| `exact_match_only` | Absence means unmatched, not zero. Do not read an empty list as "did nothing." |
| `unavailable` | The value is missing, not zero. Say the data is unavailable. |

Naming the tag is not enough. Writing "data_tier: real" into your answer is a
citation, not a qualification. Convey what it *means* for the number.

---

## Tiers

`data_tier` sits on `_meta` and often on individual sections. When
`_meta.data_tier` is `"mixed"`, `tier_note` says which section is which — and
sections carry their own. **Read down, not up.** A section's own tier always
wins over the file's.

| Tier | Means |
|---|---|
| `real` | From the named public source, raw counts. Recent months provisional. |
| `derived` | Computed from real underlying data — a rate, a trend, an automated tag. |
| `proxy` | Correlated but biased. Direction, not magnitude. |
| `crowdsourced` | Community-curated and unverified. |
| `mock` | Synthetic. **Never cite.** It never appears under `/api/v1/`. |

---

## The failure this is designed against

A person asks their assistant how dangerous their ward is. The assistant fetches
one file, reads one number, and writes one sentence. The sentence goes into a
public comment, a news tip, or an email to an alderman.

If the caveat did not make it into that sentence, the number is doing work it
cannot support — and the person will never know, because they never saw the
data. They saw a sentence.

That is why the caveat is in the same object as the number instead of in a
documentation page. It removes every excuse except the choice.

**Two specific traps:**

**One disclaimer for everything.** `windows.recent_12mo` and
`windows.prior_12mo` sit side by side in the same parent. One is provisional and
one is not. "All figures on this site are provisional" is easy, sounds careful,
and is false about one of them. Qualify each number with its own caveat.

**Compression.** Asked for a paragraph rather than a figure, the caveats are the
first thing that feels cuttable. They are the last thing that should be. If you
must shorten, cut the second decimal place, not the reason the number might be
wrong.
