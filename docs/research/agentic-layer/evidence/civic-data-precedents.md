---
run_date: 2026-07-23
topic: "How comparable civic-data, open-data, and public-interest data projects serve AI agents today — precedents for OYL's agentic layer"
study: agentic-layer (study #1)
---

# Civic-data precedents — landscape brief (mid-2026)

Scope note: this brief answers the kickoff question set only. It does not
propose changes to OYL's layer (see `02-layer-inventory.md` for the as-built
inventory this study treats as ground truth). Labels follow
`evidence/assistant-discovery.md`'s convention: `[verified]` (primary-source
fetched directly, or corroborated by independent data),
`[vendor-claim]` (stated by the publisher, not independently measured), or
`[folklore/unclear]` (widely repeated, not demonstrated). Every fetch attempt
— including 404s and 403s — is reported as evidence, not omitted.

---

## 1. Named precedents: what each publisher actually ships

### Federal / government data (US)

**GovInfo (Government Publishing Office)** — the strongest verified precedent
found. GPO shipped an official MCP server, in "Public Preview," announced
2026-01-22 `[verified — fetched usgpo/api's own docs/mcp.md directly]`. Its
own docs quote GPO's framing: *"For the first time, GPO is providing an
officially supported method to allow the use of LLMs and AI agents to
'converse' with GovInfo, the world's only certified trustworthy digital
repository."* Two tools are documented: `searchGovInfo` (titles, identifiers,
publication dates, summaries) and `describePackageOrGranule` (multi-format
package detail + metadata links). The docs carry an explicit caveat-carriage
line, quoted verbatim: *"Be aware that the data provided by GovInfo MCP will
be interpreted by your chosen LLM, and typical LLM quality assurance is
needed."* [github.com/usgpo/api, docs/mcp.md, fetched 2026-07-23]

**Census Bureau** — an MCP server exists and is described by third-party
trackers as connecting Census API data to AI assistants, but this research
pass could not confirm it is Census-Bureau-*official* versus a well-indexed
independent project; several competing "Census MCP Server" listings exist
across mcp.so, Composio, lobehub, and mcpbundles with different authorship
claims `[folklore/unclear — multiple non-primary directory listings, no
Census.gov primary-source page confirming an official server was fetched]`.
The Census API's own developer guide page (`census.gov/data/developers/
guidance/api-user-guide.html`) contains **no mention of AI, LLMs, MCP, or
citation/attribution requirements** as of this fetch `[verified — fetched
directly, 2026-07-23]`.

**US Digital Corps MCP pilot** — a GSA Digital Corps report ("Improving LLM
Access to Federal Open Data," digitalcorps.gsa.gov/pdfs/MCP_Report.pdf,
published 2026-05-18 per FedScoop's coverage) is the single most-cited
outcome number in this space: accuracy on USASpending and CDC PLACES
questions "jumping from near 0% to 95%... with MCP vs. without," starting
from a reported 0% baseline on USASpending and 2.1% on CDC PLACES
`[vendor-claim/secondary — the PDF itself could not be parsed by this
research pass (corrupted/image-heavy export); the 95% figure is reported
identically across FedScoop and paubox.com coverage, but was not independently
verified against the primary PDF text]`. [fedscoop.com
"Federal officials tap open-source standard to improve GenAI access to public
data"; paubox.com "Feds adopt open-source protocol to connect AI chatbots
with public data" — both 2026]

**data.gov** — no `llms.txt` found (`data.gov/llms.txt` → HTTP 404
`[verified]`). The public-facing page makes no mention of MCP, LLMs, or agent
guidance `[verified — fetched directly]`; catalog.data.gov is referenced as
"the next-generation Data Catalog" but this pass could not confirm CKAN vs.
another backend from the fetched content. Multiple *third-party* MCP servers
wrap data.gov's CKAN API (e.g., `adwait-ai/mcp_data_gov_in` — note: that
specific one is India's data.gov.in, not the US site) — these are
community-built wrappers, not something data.gov itself ships
`[verified as a distinction: search results return integration products, not
a data.gov-published server]`.

### Municipal open-data platforms (Socrata / CKAN)

**Socrata** (the platform behind Chicago's own `data.cityofchicago.org`,
which OYL's pipeline pulls from) — no `llms.txt` at `dev.socrata.com`
(HTTP 404 `[verified]`). No Socrata-vendor-shipped MCP server or agent API
was found; several *third-party* MCP servers exist (`Thomas-TyTech/
Socrata-MCP`, `cyanheads/socrata-mcp-server`, an "OpenGov Socrata MCP
Server" listed on mcpservers.org) that translate natural-language questions
into SoQL queries against any Socrata domain `[verified as
community-tooling, not a Socrata/OpenGov first-party ship]`.
A third-party research document (`npstorey/civic-ai-tools`,
`docs/research/landscape-analysis.md`, last updated 2026-04-24, fetched
directly) states plainly: *"[Socrata] has no native AI features as of March
2026."* That same document claims "official deployments from the Census
Bureau and GPO" among "11+ active MCP servers for civic data" and cites the
US Digital Corps pilot's 95% figure — treat this document itself as a
`[vendor-claim/secondary]` source (it is an advocacy/project README for a
tool the author is building, not an independent audit), though its GovInfo
and pilot citations check out against the primary sources fetched
independently above.

**DCAT metadata (relevant to OYL's own upstream source):** Socrata "natively
supports `data.json`" (the Project Open Data / DCAT-US catalog format), so
any Socrata-hosted portal — including `data.cityofchicago.org`, the source
OYL's pipeline pulls crash and street data from — automatically exposes a
DCAT-US-conformant catalog file without publisher effort
`[verified — dev.socrata.com RDF-XML docs + resources.data.gov's own DCAT-US
mapping documentation, both describe the same mechanism, though this pass
did not independently crawl data.cityofchicago.org's live `data.json` to
confirm Chicago has this enabled]`. DCAT-US v1.1 explicitly maps to
`schema.org/Dataset` and to classic DCAT `[verified, resources.data.gov]`.

**CKAN** — the international alternative platform per the same
`civic-ai-tools` landscape doc; this research pass did not independently
verify a CKAN-specific `llms.txt` or vendor MCP server; CKAN's own
`data.json`/DCAT export is a longstanding, pre-AI-era feature (not new agent
tooling) and was not further tested here.

### OpenStreetMap / Overpass

Not yet shipped, but a documented in-progress proposal: a community post
(`community.openstreetmap.org/t/llm-guidance-for-overpass/144622`, dated
2026-06-15, fetched directly) describes one Overpass-instance operator
building — in "a working branch," not yet merged — an `llms.txt` whose
content explicitly says **the opposite of an invitation**: *"the endpoint is
not intended for use by LLMs, AI agents, or high-volume scripts,"* plus
LLM-readable HTTP 429/504 error bodies suggesting backoff/query-optimization
`[verified — fetched directly, but explicitly a proposal in a working
branch, not deployed]`. This is the only precedent found in this research
pass where a civic/geo-data publisher's draft agent guidance is a
**refusal/rate-limit notice**, not an invitation to fetch.

### Transit data (GTFS / Mobility Database / Transitland)

No vendor-shipped `llms.txt` or MCP server found from MobilityData
(mobilitydatabase.org) or Transitland (transit.land, run by Interline) as
publishers. Third-party tooling exists: `jdamcd/gtfs-mcp` (community MCP
server against 6,000+ feeds via the Mobility Database catalog) and
"TransitGPT," an academic framework (published in *Public Transport*,
Springer, DOI via link.springer.com) that has LLMs generate and execute
Python against GTFS feeds rather than fetching a curated agent-facing file
`[verified as community/academic tooling, not publisher-shipped]`.

### Nonprofit / advocacy bike-safety data

**Bike Lane Uprising** does serve a `/llms.txt`
(`bikelaneuprising.com/llms.txt` → HTTP 200 `[verified — fetched directly]`),
but on inspection it is **generic Wix-platform boilerplate**, not
obstruction-data-specific guidance: the file states *"This site is powered by
Wix and supports the Model Context Protocol (MCP) for agentic AI access,"*
and its six tools (`GetBusinessDetails`, `SearchInSite`,
`GenerateVisitorToken`, `CallWixSiteAPI`, etc.) are Wix's standard
site-chrome/commerce tools — retrieving business hours, contact info,
bookings. **The crowdsourced obstruction/bike-lane-report dataset itself is
not exposed through this mechanism**; there is no obstruction-specific tool,
schema, or citation guidance in the file `[verified by direct inspection of
fetched content]`. This is a materially different thing from a
data-publisher-authored `llms.txt` and should not be counted as a
data-agent precedent despite superficially matching the "ships an llms.txt"
criterion.

**PeopleForBikes / BNA** — no `llms.txt` found at `bna.peopleforbikes.org`
(HTTP 404 `[verified]`). A public BNA API exists on GitHub
(`PeopleForBikes/bna-api`) but this pass found no AI-agent-specific
documentation layer on top of it.

### Journalism / advocacy data stores

**ProPublica** — `llms.txt` fetch attempt returned HTTP 404
`[verified]`. No agent-specific citation guidance found; ProPublica's
long-standing data API access is via an R package (`RPublica`, CRAN), a
traditional developer-API pattern predating the LLM-agent question entirely.

**OpenSecrets, GovTrack, LegiScan** — `llms.txt` fetch attempts all returned
HTTP 403 (bot-blocked), not a clean 404 `[verified — fetch attempted
directly; 403 is inconclusive, not proof of absence, since it may reflect a
general bot/scraper block rather than the specific path being missing]`.
This is reported honestly as **undetermined**, not as absence, per the
brief's sourcing rule that a fetch attempt (whatever its result) is the
evidence.

**Our World in Data, Wikidata** — `llms.txt` fetch attempts both returned
HTTP 404 `[verified]`.

### Wikipedia / Wikimedia (the "canonical machine-readable civic corpus")

No `/llms.txt` at `wikidata.org` (403, inconclusive per above). But Wikimedia
runs the most mature and heavily-documented licensing-for-AI mechanism found
in this entire brief: **Wikimedia Enterprise**, a commercial high-volume API
distinct from the free public API. In January 2026 (Wikipedia's 25th
anniversary), Wikimedia Foundation announced new Enterprise licensing
agreements with Microsoft, Meta, Perplexity, Mistral AI, Amazon, Google,
Ecosia, Nomic, Pleias, ProRata, and Reef Media `[verified — Wikimedia
Enterprise's own blog post + corroborating trade coverage in The Register and
Medianama, both 2026-01]`. Wikimedia Enterprise's own site states directly
(fetched 2026-07-23): *"Over 99.9% of data available through Wikimedia
Enterprise services is under a Creative Commons license"* and *"Every
request has metadata clearly explaining the attached license"*
`[verified — fetched directly]`. The page markets the service explicitly as
*"Built for AI, Search, and Knowledge Graphs"* and states it is *"used by the
largest organizations on the planet to populate and refine knowledge graphs,
train large language models (LLMs)"* `[vendor-claim]`. Notably, the mechanism
is **metadata-carries-the-license-per-request**, structurally the same
pattern as OYL's own `_meta.license`/`_meta.attribution` envelope fields
(inventory §1.2) — but Wikimedia's version is backed by paid commercial
contracts with named AI vendors, not a unilateral publisher declaration.

On the separate question of Wikipedia's *own* editorial policy toward AI
(not third-party consumption of its data): English Wikipedia passed an RfC
banning LLM-generated/rewritten article text on 2026-03-20 (44–2), citing
hallucination risk and a "compounding risk" of AI-written content being
scraped back into future training data `[verified — Medianama coverage of
the RfC outcome; this is about content-authorship policy, not data-citation
policy, and is tangential to OYL's question but shows the same organization
treating AI-mediation of its corpus as a live, actively-governed risk]`.

---

## 2. Agent-specific usage guidance, citation requirements, or caveat-carriage — direct quotes

- **GovInfo MCP docs**: *"Be aware that the data provided by GovInfo MCP will
  be interpreted by your chosen LLM, and typical LLM quality assurance is
  needed."* [usgpo/api, docs/mcp.md]
- **Overpass (proposed, not shipped)**: *"the endpoint is not intended for
  use by LLMs, AI agents, or high-volume scripts."* [OSM community forum,
  2026-06-15 post, working-branch draft]
- **Wikimedia Enterprise**: *"Every request has metadata clearly explaining
  the attached license."* [enterprise.wikimedia.com]
- No publisher in this pass was found instructing agents on **how to phrase
  an answer** (e.g., "restate this caveat," "say X not Y") the way OYL's
  `llms.txt` "When answering from this data" section does (inventory §1.4).
  The GovInfo line comes closest but is a generic QA disclaimer, not
  answer-phrasing guidance. This appears to be a genuinely uncommon practice
  among the precedents checked, not merely under-reported.

## 3. Measured outcomes reported by publishers

Thin, as expected:

- The GSA Digital Corps pilot's 95%-vs-near-0% figure (§1) is the only
  quantified before/after outcome found anywhere in this pass — and it
  measures **whether MCP access improves answer accuracy**, not whether
  caveats/attribution survive into the answer, and not from a source this
  pass could independently read in full (PDF parse failed).
- No publisher — GovInfo, Wikimedia Enterprise, Socrata, PeopleForBikes,
  ProPublica, or any other checked — was found publishing a measurement of
  *citation correctness*, *caveat retention*, or *attribution survival* in
  live assistant answers. This directly parallels
  `assistant-discovery.md`'s finding for OYL itself: structure is described
  and shipped; behavioral compliance is essentially unmeasured
  industry-wide, not just for OYL.

## 4. Schema.org / DCAT / data-catalog standards

- **DCAT-US** is the US government's standard catalog schema
  (`resources.data.gov`), explicitly mapped to both classic **DCAT** and
  **schema.org/Dataset** `[verified]`.
- **Socrata** (hence Chicago's own portal) natively emits `data.json`
  (DCAT-US-conformant) with no publisher effort required `[verified via
  Socrata's own RDF-XML docs + resources.data.gov's DCAT-US mapping
  documentation]` — this is the one standards-adoption claim in this brief
  that touches OYL's own supply chain directly (its upstream Chicago crash
  data source).
- **schema.org/Dataset adoption breadth**: a June 2026 Google/Schema.org
  joint transparency release reports the `Dataset` type in use across
  "10K–100K domains" based on Google's web index as of May 2026
  `[verified, per Schema.org's own blog post as reported]` — this is a
  broad web-wide figure, not civic-data-specific, and the source gives no
  breakdown isolating civic/government portals.
- **Assistant-behavior link to schema.org markup**: `assistant-discovery.md`
  (§4, already fetched and treated as ground truth for this study) already
  found the one controlled causal study (Ahrefs, 1,885-page DiD) showing
  **no positive citation uplift** from adding JSON-LD Dataset schema to
  pages already receiving 100+ AI Overview citations. This brief found no
  additional civic-specific study contradicting or supplementing that
  finding — Google Dataset Search's role in assistant grounding specifically
  (versus classic search) remains an **open gap**, not a negative finding,
  exactly as `assistant-discovery.md` already flagged.

## 5. Licensing/attribution norms surviving agent mediation

- **Creative Commons itself is actively working the problem, not settled.**
  CC's own site describes a 2026 initiative, "CC Signals," as *"a new
  preference signals framework designed to increase reciprocity and sustain
  a creative commons in the age of AI,"* explicitly framed as unresolved
  work-in-progress rather than a shipped, enforceable standard
  `[vendor-claim, creativecommons.org, 2026]`. CC's own guidance for AI
  training attribution is advisory, not a technical enforcement mechanism:
  *"For AI model training, attribution could be a simple link to the source
  of the dataset used to train the model. Where retrieval-augmented
  generation (RAG)... is available, providing attribution to the CC-licensed
  work tied to the particular model output with a link to the source is
  ideal"* `[vendor-claim — "could be," "is ideal," non-binding language]`.
- **Wikimedia Enterprise is the one commercial-scale mechanism found where
  attribution/license metadata is contractually attached to every API
  response** (§1) — but this is enforced through paid bilateral contracts
  with named AI companies, not through a mechanism that survives a free,
  unlicensed public fetch the way OYL's own file is consumed.
- **No litigation, published dispute, or publisher statement was found in
  this pass specifically about an AI assistant paraphrasing CC-BY-licensed
  *civic/open-government* data and dropping attribution.** This is a real
  gap in the public record as of this brief's date, not a finding that no
  disputes exist — CC-content licensing/AI-training litigation generally
  exists (e.g., the broader "using CC-licensed works for AI training"
  discourse CC itself references) but nothing sighted here is civic-data-,
  attribution-survival-, or paraphrase-specific.

## 6. Failure precedents: assistant misquoting/misattributing civic data

No publisher-authored, civic-data-specific write-up of an assistant
misquoting or misattributing that publisher's data was found in this
research pass, despite direct searching. What exists instead:

- A large, well-documented body of **legal-citation hallucination**
  tracking (Damien Charlotin's database at HEC Paris's Smart Law Hub,
  reported at 1,227 cataloged court-filing cases as of early 2026;
  the March 2026 Sixth Circuit sanctions in *Whiting v. City of Athens,
  Tennessee* over fabricated citations) `[verified via independent trade
  coverage, but this is the legal-citation domain, not civic open data]`.
- General hallucination-rate figures ("17%–34% of queries" for
  best-performing legal AI tools, attributed to Stanford research via a
  secondary source) `[folklore/unclear — secondary citation, domain
  mismatch with civic data]`.
- **Nothing civic-open-data-specific.** This should be reported honestly as
  thin-to-absent, matching the brief's own instruction to say so if it's
  thin: no public post-mortem, blog post, or news article was located in
  which a named civic/government/nonprofit data publisher documented an
  assistant misquoting or misattributing its published dataset. This mirrors
  `assistant-discovery.md`'s broader finding that engine-side behavioral
  measurement (as opposed to publisher-side shipping) is scarce across the
  board, and extends it: even the *failure* side of that measurement gap is
  undocumented, not just the success side.

---

## Implications for OYL (facts only, no proposals)

- Of all precedents checked, **GovInfo's MCP server is the only
  government-agency-shipped, first-party artifact found** that (a) is
  officially attributed to the publisher, (b) is confirmed live (not a
  draft), and (c) carries an explicit agent-facing QA/caveat disclaimer in
  its own docs. It is a different mechanism (MCP, a live protocol) from
  OYL's static `llms.txt` + JSON API approach (inventory §1.1, §1.4), and
  GovInfo runs on federal infrastructure, not GitHub Pages (inventory §3
  constraint).
- The single quantified outcome number found industry-wide (GSA Digital
  Corps' reported 95%-vs-near-0% MCP accuracy jump) measures whether
  structured machine access improves an assistant's raw answer accuracy —
  it does not measure caveat retention, attribution survival, or the
  specific failure mode (relative score laundered into absolute claim)
  that inventory §4/NL's protocol is built to test. No source in this
  brief measures that specific failure mode for any publisher, civic or
  otherwise.
- Bike Lane Uprising's `/llms.txt` — the one candidate on OYL's own
  "worth checking" list confirmed to return HTTP 200 — turned out on
  inspection to be generic Wix-platform tooling unconnected to its
  obstruction dataset, not a bike-safety-data-specific precedent. This
  matters to the extent OYL's `llms.txt` already disclaims obstruction data
  and points to Bike Lane Uprising by name (inventory §1.4): that disclaimer
  points to a site whose own agent-facing surface does not expose the
  obstruction data either.
- OYL's own upstream data source (`data.cityofchicago.org`, Socrata) already
  emits a DCAT-US-conformant `data.json` by default per Socrata's own
  platform behavior — a standards-adoption fact upstream of OYL's pipeline,
  independent of anything OYL itself ships.
- No publisher found in this pass — including the best-resourced ones
  (GovInfo, Wikimedia Enterprise, the GSA pilot) — publishes a measurement
  of whether an assistant *retains a data caveat* or *correctly attributes*
  in a live answer. This is the same empirical gap `02-layer-inventory.md`
  §5 and `assistant-discovery.md` already identify for OYL specifically;
  this brief's finding is that the gap is not OYL-specific — it is, on the
  evidence gathered here, industry-wide as of mid-2026.
- No civic-data publisher's own agent-facing guidance was found instructing
  assistants on **answer phrasing** the way OYL's llms.txt "When answering
  from this data" section does (§2 above). On the narrow dimension of
  "prescribing how an agent should phrase a caveat-carrying answer," OYL's
  practice was not observed to have a direct precedent among the sources
  checked in this pass — worth flagging as either a genuinely unusual
  design choice or a research-pass gap, not as a claim that no such
  precedent exists anywhere.

---

## Sources

- GPO / usgpo, GovInfo MCP server docs — github.com/usgpo/api/blob/main/docs/mcp.md (fetched 2026-07-23)
- FedScoop, "Federal officials tap open-source standard to improve GenAI access to public data" — fedscoop.com (2026)
- Paubox, "Feds adopt open-source protocol to connect AI chatbots with public data" — paubox.com/blog (2026)
- GSA U.S. Digital Corps, "Improving LLM Access to Federal Open Data" — digitalcorps.gsa.gov/pdfs/MCP_Report.pdf (2026-05-18; PDF fetched but not machine-parseable by this pass)
- data.gov — data.gov/ and data.gov/llms.txt (both fetched directly, 2026-07-23)
- github.com/GSA/data.gov (referenced from data.gov's own page)
- Census Bureau, API User Guide — census.gov/data/developers/guidance/api-user-guide.html (fetched directly, 2026-07-23)
- npstorey/civic-ai-tools, landscape analysis — github.com/npstorey/civic-ai-tools/blob/main/docs/research/landscape-analysis.md (fetched directly, last updated 2026-04-24)
- dev.socrata.com/llms.txt (fetched directly, 404, 2026-07-23)
- dev.socrata.com, RDF-XML format docs — dev.socrata.com/docs/formats/rdf-xml
- resources.data.gov, DCAT-US Schema v1.1 / field mappings — resources.data.gov/resources/dcat-us/, resources.data.gov/resources/podm-field-mapping/
- schema.org, Dataset type — schema.org/Dataset
- ppc.land, "Google and Schema.org finally show how the web uses structured data" (2026-06)
- OpenStreetMap Community Forum, "LLM guidance for Overpass" — community.openstreetmap.org/t/llm-guidance-for-overpass/144622 (posted 2026-06-15, fetched directly)
- mobilitydatabase.org — MobilityData's Global Catalog of GTFS/GTFS-RT/GBFS feeds
- transit.land — Transitland (Interline)
- jdamcd/gtfs-mcp — github.com/jdamcd/gtfs-mcp
- "TransitGPT: a generative AI-based framework for interacting with GTFS data using large language models," Public Transport (Springer) — link.springer.com/article/10.1007/s12469-025-00395-w
- bikelaneuprising.com/llms.txt (fetched directly, HTTP 200, 2026-07-23)
- bna.peopleforbikes.org/llms.txt (fetched directly, HTTP 404, 2026-07-23)
- github.com/PeopleForBikes/bna-api
- propublica.org/llms.txt (fetched directly, HTTP 404, 2026-07-23)
- opensecrets.org/llms.txt, govtrack.us/llms.txt, legiscan.com/llms.txt (all fetched directly, HTTP 403 — inconclusive, 2026-07-23)
- ourworldindata.org/llms.txt, wikidata.org/llms.txt (fetched directly: 404 and 403 respectively, 2026-07-23)
- Wikimedia Enterprise — enterprise.wikimedia.com/ (fetched directly, 2026-07-23) and enterprise.wikimedia.com/blog/wikipedia-25-enterprise-partners/
- The Register, "Six more AI outfits sign for Wikimedia's fastest APIs" — theregister.com (2026-01-16)
- Medianama, "Wikipedia Signs AI Content Deals With Microsoft, Meta & More" (2026-01) and "English Wikipedia bans AI-generated article content after RfC" (2026-03)
- Creative Commons, "CC Signals" — creativecommons.org/cc-signals/
- Creative Commons, "Using CC-Licensed Works for AI Training" — creativecommons.org/using-cc-licensed-works-for-ai-training-2/
- Creative Commons, "Building the Future in 2026" — creativecommons.org/2026/01/08/building-the-future-in-2026/
- Smart Law Hub (HEC Paris) / Damien Charlotin AI hallucination case database, as reported by blog.platinumids.com, "1,227 Fabricated Citations and Counting" (2026)

## Known limitations of this brief

- Desk research only (WebSearch/WebFetch); no interviews with any publisher
  named above, and no independent server-log access to any third-party site
  (this pass cannot see whether these publishers' own `llms.txt`/MCP surfaces
  are actually fetched by production assistants — that question is answered,
  for the assistant-discovery side generally, in `assistant-discovery.md`,
  not re-litigated here).
- Several HTTP 403 responses (OpenSecrets, GovTrack, LegiScan, Wikidata) are
  reported as **inconclusive**, not as absence — a 403 is consistent with a
  general bot-block unrelated to whether the specific file exists, and this
  brief did not have a way to distinguish the two from outside.
- The GSA Digital Corps pilot report — the single most load-bearing outcome
  number in this brief — could not be read in full; its PDF resisted
  text extraction in this pass, so its 95% figure rests on secondary
  reporting (FedScoop, Paubox) rather than a primary-source read of the
  report's own methodology, sample size, or caveats. This should be treated
  as a soft number pending a proper PDF read.
- The `npstorey/civic-ai-tools` landscape document, while useful and directly
  fetched, is itself an advocacy/project document for a tool its author is
  building, not an independent audit — its claims about "11+ active MCP
  servers" and the UK Meta/Anthropic partnership were not independently
  re-verified beyond the GovInfo and pilot claims this brief checked
  directly.
- Coverage is necessarily incomplete: dozens of named candidates in the
  kickoff prompt (e.g., CKAN generally beyond the DCAT/data.json mechanism,
  Streetlight/Replica, Vision Zero dashboards specifically, most
  data-journalism orgs beyond ProPublica) were not individually fetched in
  this pass due to time/scope; their absence from this brief is not evidence
  they lack agent-facing features, only that this pass did not check them.
- No civic-data-specific misattribution/misquote case study was found
  despite direct searching (§6) — this is reported as an honest gap, but a
  negative search result is weaker evidence than a positive one; it remains
  possible such a write-up exists and was not surfaced by the queries used
  here.
