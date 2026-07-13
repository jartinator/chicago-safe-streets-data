# Strava Metro application — draft answers

Apply at https://metro.strava.com/ ("Request access" / partner application).
Metro has been free for urban planners, city governments, and
safe-infrastructure advocates since September 2020; ~3,500 orgs use it.
Answers below are drafted for the typical application fields — adapt to the
actual form. One framing note: Metro grants access to *organizations* with a
transportation-improvement mission. If the form resists an unincorporated
open-source project, the fallback is applying in partnership with (or via a
letter of support from) an established advocacy org — but try the direct
application first; "safe-infrastructure advocates" is their own language.

**Organization name:** On Your Left! (OYL)

**Organization type:** Advocacy / civic technology (open-source,
noncommercial)

**Website:** [the GitHub Pages URL for this repo's site]

**Geography of interest:** City of Chicago, Illinois, USA

**What we do:** On Your Left! is an independent, open-source, read-only
evidence dashboard for Chicago bike safety. It joins the city's public
crash records, CDOT's bikeway network, ward boundaries, City Council
records, and other open datasets into ward- and corridor-level views used
by advocates, residents, and ward offices. Every layer carries a published
provenance tier (real / proxy / crowdsourced / derived), and all outputs
are freely downloadable.

**How we would use Metro data:** Our largest documented gap — confirmed by
a formal user-needs study across advocacy, government, and resident
audiences — is exposure data: crash counts cannot be presented as risk
without ridership context. We would use Metro's aggregated, de-identified
corridor activity data as a clearly labeled exposure *proxy* (a floor, not
a denominator), shown alongside — never silently divided into — police
crash records, with Metro's recreational-use skew disclosed on every
surface where it appears. Aggregates would inform corridor-level context
in our published views; we would follow all Metro license terms regarding
raw data redistribution.

**Who benefits:** Chicago safe-streets advocates preparing ward-level
materials for alderpersons; ward offices and CDOT staff who currently lack
any public exposure signal; residents deciding whether their own routes'
crash patterns reflect danger or simply high ridership. Chicago has no
public bike-count dataset (unlike NYC or DC), one permanent counter
citywide, and its most recent volume analysis (CDOT/Replica, 2024) is not
public data — Metro would be the first recurring exposure signal available
to the public here.

**Data handling:** Aggregated derivatives only in published files, each
tagged `proxy` tier with a skew caveat; no attempt to de-anonymize; access
restricted to project maintainers.

---

*After approval:* add a `pull_strava_metro.py` scaffold mirroring
`pull_divvy.py` (PR C), publish as a second labeled exposure proxy, and add
the "who each source misses" row per RESPONSES.md §2.
