---
run_date: 2026-07-22
topic: "How major AI assistants discover/fetch third-party site content in mid-2026, and whether llms.txt is real or folklore"
study: agentic-layer (study #1)
---

# Assistant discovery & fetch mechanisms — landscape brief (mid-2026)

Scope note: this brief answers the kickoff question set only. It does not
propose changes to OYL's layer (see `02-layer-inventory.md` for the as-built
inventory this study treats as ground truth). Every claim below is labeled
`[verified]` (primary-source or corroborated-by-independent-data),
`[vendor-claim]` (stated by the vendor, not independently measured), or
`[folklore/unclear]` (widely repeated, not demonstrated).

---

## 1. Per-surface discovery and fetch mechanisms

### ChatGPT (incl. Search) — OpenAI

Three distinct crawlers, independently controllable in `robots.txt`
`[verified]`:

- **GPTBot** — training-data crawler; content it collects "may be used to
  improve and train OpenAI's...models." Respects `robots.txt`; a site can
  block GPTBot while allowing the other two. [OpenAI crawler docs,
  developers.openai.com/api/docs/bots, accessed 2026-07-22]
- **OAI-SearchBot** — builds the index behind ChatGPT Search/citations, a
  traditional crawl-then-index pipeline distinct from live fetch. Respects
  `robots.txt`. [same source]
- **ChatGPT-User** — fires when a live user's turn causes ChatGPT (or a
  Custom GPT/agent) to visit a specific page in real time. OpenAI's own docs
  state robots.txt "may not apply" to these user-initiated actions
  `[vendor-claim, doc language hedges]`.

Whether ChatGPT's *search* answers are grounded on Bing's index, OpenAI's own
index, or both is **contested and evolving** — flag as a conflict:
- Multiple SEO-trade sources assert ChatGPT Search "directly connects to
  Bing's index" for its main product `[folklore/unclear — no OpenAI
  confirmation found]`. [aiplusautomation.com, practicalecommerce.com, 2026]
- The same sources note OAI-SearchBot behaves like an independent crawl/index
  pipeline, and that the logged-out free tier appears to use neither Google's
  nor an obviously-Bing-branded index, "suggesting OpenAI may be running its
  own experimental search crawler" `[folklore/unclear]`.
- No OpenAI primary source found that states the current (mid-2026) search
  backend explicitly; the historical Microsoft partnership for Bing-backed
  search launched 2023–2024, but its current share of ChatGPT Search traffic
  is not documented by OpenAI as of this brief.

JS rendering: independent crawl-behavior write-ups report none of GPTBot,
OAI-SearchBot, or ChatGPT-User render client-side JavaScript as of June 2026
— they read the HTML returned on first request only `[folklore/unclear,
consistent across multiple SEO-trade sources, no OpenAI primary-source
confirmation]`. [searchoptimo.com "Do AI Crawlers Render JavaScript?", 2026;
asklantern.com "AI Crawlers Do Not Render JavaScript", 2026]

### Claude (claude.ai + Claude Code/API web tools) — Anthropic

Three crawlers, documented together for the first time in an Anthropic
support-doc update flagged 2026-02-20/25 `[verified — vendor doc, corroborated
by trade press]`:

- **ClaudeBot** — training-data collection.
- **Claude-User** — fires when a Claude.ai/API user's question causes Claude
  to fetch a specific page.
- **Claude-SearchBot** — indexes content to improve Claude's own search-result
  quality (a separate crawl/index pipeline from Claude-User's live fetch).

Anthropic states **all three**, including the user-triggered Claude-User,
honor `robots.txt` and that Anthropic does not bypass CAPTCHAs or rely on
IP-based identification workarounds `[vendor-claim]`. This is a point of
contrast with OpenAI (hedges on ChatGPT-User) and a sharp contrast with
Perplexity (below). [seroundtable.com "Anthropic Updates Its Crawler
Documentation", 2026-02; searchengineland.com "Anthropic clarifies what its
three web crawlers do", 2026; ppc.land, 2026]

Web search backend: Claude.ai's live web-search tool is **almost certainly**
backed by Brave Search — Brave sits on Anthropic's published subprocessor
list (added March 2025) and an independent overlap study found 86.7%
statistically-significant overlap between Claude's cited results and Brave's
top non-sponsored results `[verified via subprocessor list; backend choice
itself is inference, not an Anthropic statement, so mark
vendor-claim-adjacent]`. Anthropic has never named a search provider publicly.
[xponent21.com "Anthropic Lists Two Web-Search Subprocessors", 2026;
mostailabs.com "How Claude Finds Your Business via Brave Search", 2026]
As of a dated addition (2026-05-06), **TurboPuffer** was added as a second
web-search subprocessor for all Anthropic products except Claude for
Government — role (vector index vs. crawl) not disclosed `[vendor-claim,
subprocessor-list level only]`. [xponent21.com, 2026]

### Gemini / Google

- **Google-Extended** — a `robots.txt` token, separate from the classic
  `Googlebot`, that controls inclusion in Gemini/AI-Overviews *grounding* and
  in training. Google's own docs state grounding-with-Google-Search "does not
  use web pages for grounding that have disallowed Google-Extended"
  `[verified, Google Cloud/AI docs, ai.google.dev + docs.cloud.google.com,
  accessed 2026-07-22]`.
- Gemini's grounding is explicitly built on **the Google Search index**, not
  a separate crawl — "Grounding with Google Search" connects the model to
  "real-time web content" via the existing Search infrastructure
  `[vendor-claim, Google docs]`.
- Google-Extended is reported (independent SEO-trade sources, not Google) as
  the one major AI crawler that **does** render JavaScript, "because it
  inherits Google's indexing infrastructure" `[folklore/unclear — plausible
  given Googlebot's rendering pipeline, but no Google primary-source
  statement isolating Google-Extended's rendering behavior was found]`.
- Timeline marker: Gemini 3 became the default AI Overviews model in January
  2026; source-link presentation (hover cards) strengthened in Feb 2026
  `[vendor-claim, Google Developers blog / product announcements, 2026]`.

### Perplexity

Two crawlers, and an unresolved public dispute over whether one of them must
honor `robots.txt`:

- **PerplexityBot** — traditional crawler feeding Perplexity's own index;
  Perplexity states it follows `robots.txt` and is "not used to train AI
  foundation models" `[vendor-claim, docs.perplexity.ai]`.
- **Perplexity-User** — fires on live user queries. Perplexity's public
  position (an August 2025 blog post, "Agents or Bots: Making Sense of AI on
  the Open Web") is that an agent acting on a specific human's request "isn't
  a bot" and is not bound by `robots.txt` the way a crawler is
  `[vendor-claim, contested]`.
- Cloudflare published a forensic rebuttal (2025-08-04) accusing Perplexity of
  spoofing generic Chrome user-agents and rotating ASNs specifically to evade
  declared blocks, then **delisted Perplexity as a Cloudflare Verified Bot**
  and added active blocking rules `[verified — Cloudflare's own blog +
  independent trade coverage]`. This is a live, unresolved conflict between a
  major vendor's stated policy and a major infra provider's forensic claims —
  report as conflicting, not settled. [searchengineworld.com "Perplexity
  Responds to Cloudflare"; searchenginejournal.com "Cloudflare Delists and
  Blocks Perplexity", 2025-2026]
- Perplexity's own index is reported at "50+ billion pages" as of Q1 2026,
  supplemented by Bing "for missing or very recent content" — Perplexity has
  not published this mix ratio itself `[vendor-claim for index size; the
  Bing-supplementation claim is trade-press inference, not confirmed by
  Perplexity, so folklore/unclear]`.

### Microsoft Copilot

No separate "CopilotBot." Copilot (web, Windows, M365) is served from the
**same Bing index** that Bingbot builds; independent trade sources describe
Bingbot, BingPreview, and AdIdxBot as the operative crawler family, with
BingPreview specifically generating the page snapshots used in AI-answer
citations `[folklore/unclear — consistent across multiple SEO-trade sources;
no single Microsoft doc enumerating this exact division was fetched]`.
Microsoft shipped an **AI Performance report** in Bing Webmaster Tools
(2026-02-11) exposing "grounding queries" (Copilot's internally-reformulated
search queries) and citation counts directly to site owners — the first major
AI vendor to expose this kind of first-party grounding telemetry
`[vendor-claim, Microsoft product announcement]`. Microsoft also announced
"Web IQ," a suite of "AI-native grounding APIs" over "Bing's re-architected
global index," at Build 2026 (2026-06-02) `[vendor-claim]`.

---

## 2. llms.txt: adoption reality check

**Origin.** Jeremy Howard (Answer.AI / fast.ai) proposed `llms.txt` on
2024-09-03: a markdown file at `/llms.txt` (H1 title, blockquote summary,
H2-delimited link lists, optional "Optional" section) meant to compress a
site into an LLM-context-sized index. Early adopters were Answer.AI/fast.ai's
own `nbdev`-generated doc sites; VitePress, Docusaurus, and Drupal plugins
followed `[verified, llmstxt.org spec page, accessed 2026-07-22]`.

**Site-side adoption is real and growing, but from a small base.**
Originality.ai's tracker (3M+ domains scanned) counted 4,088 `llms.txt`
instances in June 2025, growing 8.8x to 36,120 by May 2026 (companion
`llms-full.txt` grew faster still, 107x). rankability.com separately found
8.7% of the top-1,000 sites publish one as of June 2026
`[verified — independent tracker + independent measurement, both dated
2026]`. [ppc.land "llms.txt adoption rises 8.8x", 2026-07-02; rankability.com
"LLMS.txt Adoption: 8.7% of Top 1,000", 2026-06]

**Engine-side fetching is close to zero.** This is the load-bearing finding
for OYL's open question #5 (whether `llms.txt` is fetched by any production
assistant):

- **Ahrefs**, server-log analysis of 137,000 domains, published 2026-07-02:
  **97% of `llms.txt` files received zero requests in May 2026.** Of the
  requests that did occur, generic SEO-audit tools accounted for 21.7% (the
  single largest category); combined AI-retrieval-bot traffic was ~1.1% of
  all requests to the file. GPTBot accounted for 4.51% of *requests that
  happened at all* (not 4.51% of all `llms.txt` files); ClaudeBot 0.80%
  `[verified, primary study, ahrefs.com/blog/llmstxt-study/]`.
- **WISLR**, an independent 48-day CDN-log analysis (2026-02-01 to
  2026-03-20, republished 2026-07-20) of one site's own traffic: **zero AI
  bots requested `/llms.txt` across the full 48 days**, while the same bots
  (GPTBot, ClaudeBot, Claude-SearchBot, Bingbot) actively fetched
  `sitemap.xml` — Bingbot 139 times, Claude-SearchBot 135 times — and
  GPTBot/ClaudeBot both began fetching `sitemap.xml` for the first time on
  2026-03-18/19 `[verified, single-site case study, directionally consistent
  with the larger Ahrefs sample]`. [wislr.com/articles/ai-bot-behavior-log-analysis]
- A third source (cited within the ppc.land roundup) reports one study
  monitoring 500M+ AI bot visits over 90 days found **only 408 direct
  `/llms.txt` requests** total `[verified as reported, original study not
  independently located; treat as corroborating, not primary]`.

**Vendor statements are explicitly negative.** Google's John Mueller
(publicly, on Bluesky, and referenced in Search Off the Record-style
commentary) was asked whether Google's own presence of `llms.txt`-adjacent
files was an endorsement of the format: "I'm tempted to say something snarky
since this has come up so often, but to be direct, no." Google subsequently
clarified that any `llms.txt`-shaped files appearing on Google properties
were an artifact of an internal CMS template, not a deliberate SEO/AEO
signal, and that **Google Search does not use or endorse `llms.txt`**
`[verified — vendor statement, corroborated across seroundtable.com,
searchenginejournal.com, letsdatascience.com, all 2026]`. Mueller's practical
guidance: give a platform a file *if that specific platform asks for one*;
none currently require it.

**Verdict for OYL's open question #5:** site-side publication of `llms.txt`
is a real, growing, low-adoption convention with essentially **no measured
engine-side consumption** as of mid-2026. The strongest same-vendor
crawlers (GPTBot, ClaudeBot, Bingbot) that *do* request discovery files
overwhelmingly prefer `sitemap.xml` over `llms.txt` when both are offered.
This directly supports OYL's existing discovery-hardening posture of putting
the pointer in `sitemap.xml` and `robots.txt` as well as `llms.txt` itself
(see inventory §1.5) — the multi-channel approach is evidenced, not just
prudent.

---

## 3. Does absence from Google/Bing indexes hide a site from assistants?

Evidence is surface-specific, not a single yes/no:

- **Gemini / AI Overviews**: grounding is built directly on the Google
  Search index; `Google-Extended` opt-out is a separate control from classic
  indexability, but a page that isn't in Google's index at all has no path
  into Search-grounded Gemini answers by definition — grounding retrieves
  *from* the index `[verified via Google's own architecture description]`.
- **Copilot**: same relationship with Bing's index — Copilot's "grounding
  queries" run against Bing's index; a page absent from Bing is absent from
  the retrieval pool `[folklore/unclear on exact mechanics, but consistent
  with Microsoft's own framing of grounding as querying "the traditional
  Bing index"]`. [rankly.substack.com "How Microsoft Copilot Search Works", 2026]
- **ChatGPT Search**: contested (see §1) whether Bing-index-dependent,
  OAI-SearchBot's own index, or both; **if** Bing-dependent as widely
  claimed, Bing-index absence would matter here too, but this is not
  confirmed by OpenAI `[folklore/unclear]`.
- **Perplexity**: runs its **own** crawl/index (PerplexityBot →
  50B+-page index, vendor-claimed) with Bing as a claimed supplement for
  freshness/coverage gaps — meaning a site could in principle be absent from
  Google/Bing and still be reachable if PerplexityBot itself crawls and
  indexes it directly `[vendor-claim for index size; supplementation claim is
  trade-press inference]`.
- **Claude.ai web search**: backed by Brave's independent 30B+-page index
  (inferred, see §1), which is neither Google's nor Bing's index — so
  Google/Bing absence does not mechanically exclude a site from Claude's
  search grounding, though Brave's own crawl coverage is a separate unknown
  `[folklore/unclear — Brave index size is Brave's own claim, not verified
  here]`.

**Net finding:** for the two surfaces built directly on the Google and Bing
indexes (Gemini/AI-Overviews and Copilot respectively), index absence is
structurally exclusionary by the vendors' own architecture descriptions. For
Perplexity and Claude, index absence from Google/Bing specifically does
**not** by itself explain absence from those two assistants' answers, since
each runs its own retrieval index. ChatGPT Search's dependency is unresolved
in public sources as of this brief. This matches inventory §1.5's flagged
open gap ("search-engine indexing... is the known gap") but nuances it:
Google/Bing indexing appears to gate two of five surfaces outright, not all
five uniformly.

---

## 4. What measurably improves odds of being found/quoted (AEO/GEO): evidence vs. folklore

- **Structured data / JSON-LD `Dataset` markup — mixed, largely negative in
  the one controlled study found.** Ahrefs ran a difference-in-differences
  study (published 2026-05-11) on 1,885 pages that newly added JSON-LD schema
  (Aug 2025–Mar 2026) against 4,000 matched controls, restricted to pages
  already receiving 100+ AI Overview citations. Result: **Google AI
  Overviews −4.6% (statistically significant but small in absolute terms, ~12
  daily citations), Google AI Mode +2.4% (not distinguishable from zero),
  ChatGPT +2.2% (not distinguishable from zero)** — "no major uplift in
  citations on any platform" `[verified, controlled study,
  ahrefs.com/blog/schema-ai-citations/]`. This directly contradicts the
  widely-repeated marketing claim that "AI-cited pages are ~3x more likely
  to carry JSON-LD" — that correlational claim (also found in this research
  pass) does not establish causation, and the one causal test found says
  adding schema to an already-cited page does not reliably increase citation
  `[folklore/unclear for the causal claim; the correlational claim is
  separately real but is not evidence schema *causes* citation]`.
- **A conflicting technical claim** from a different source states that
  direct retrieval testing found AI systems "extracted only visible HTML
  content" and that JSON-LD, hidden Microdata, and hidden RDFa "were all
  ignored" by the extraction step itself `[folklore/unclear, single
  secondary source, not independently verified — but consistent with the
  Ahrefs null result]`.
- **Google Dataset Search**: no 2025–2026 study was found linking Dataset
  Search inclusion to assistant citation rates specifically; Dataset Search
  indexes `schema.org/Dataset` JSON-LD but its role (if any) in feeding
  Gemini/AI-Overviews grounding versus classic Search was not documented in
  any source surfaced by this research pass — treat as an **open gap**, not
  a negative finding.
- **Sitemaps**: `[verified]` — GPTBot and ClaudeBot both began actively
  requesting `sitemap.xml` in March 2026 (§2, WISLR log study), and multiple
  independent server-log write-ups describe sitemap-based discovery as the
  dominant AI-crawler behavior over `llms.txt`. This is the best-evidenced
  "improves discoverability" lever in this brief.
- **Inbound links / backlinks**: Ahrefs' correlational study (75,000 brands)
  found raw backlink count correlates only weakly with AI Overview
  visibility (r = 0.218), while **branded web mentions** (r = 0.664, ~3x
  stronger) and **branded anchor text** (r = 0.527) correlate much more
  strongly; a follow-up found YouTube mentions the single strongest
  correlate (r ≈ 0.737) `[verified as correlational study; explicitly
  correlational, not causal — Ahrefs itself frames backlinks as "a threshold
  condition... not the main driver"]`. [ahrefs.com/blog/ai-brand-visibility-correlations]

---

## 5. Static JSON APIs and "fetch recipes": documented agent behavior

- No vendor documentation was found (OpenAI, Anthropic, Google, Perplexity,
  Microsoft) that describes a distinct code path for "raw JSON API endpoint"
  versus "HTML page" — all describe fetching pages/URLs generically.
- Practitioner write-ups on ChatGPT's tool-use describe it as *not*
  reliably fetching and parsing arbitrary live JSON from a URL end-to-end in
  a single browsing step without an intermediate tool (a Custom
  GPT Action, an MCP server, or a scraping/rendering proxy) — the common
  pattern described is "fetch/render first (external tool), then hand text
  to the model," rather than the model's built-in browsing tool independently
  hitting a bare `.json` URL and reasoning over it `[folklore/unclear —
  practitioner accounts, not a vendor behavioral spec, and describes ChatGPT
  Actions/GPTs specifically, not necessarily ChatGPT-User's live-fetch path
  triggered by a plain user question]`.
- No study was found (search-engine-trade press, academic, or vendor) that
  specifically tested whether an assistant, given a page or `llms.txt` that
  points at a raw JSON URL, follows that pointer and fetches the JSON
  directly — let alone whether it correctly executes a multi-step "fetch
  recipe" (fetch A, then use a field from A to construct URL B) as OYL's
  `index.json` defines. **This is a genuine, unfilled evidence gap** — it
  maps directly onto inventory open-gap #4 ("whether the fetch recipes in
  `index.json` are ever followed as written") and cannot be answered from
  desk research; it requires the empirical audit the inventory document
  already calls for (NL's adversarial-protocol run).
- The one adjacent data point: because most crawlers/user-agents documented
  above (§1) do **not** render JavaScript and read only the HTML/text
  returned on first request, a bare JSON URL returning `Content-Type:
  application/json` should in principle be exactly the kind of URL these
  fetchers *can* read without a rendering step — but this is an inference
  from the JS-rendering findings, not a direct observation of JSON-specific
  behavior `[folklore/unclear — inference, not evidence]`.

---

## Implications for OYL (facts only, no proposals)

- OYL's `<noscript>` pointer and root-level `llms.txt`/`sitemap.xml`/
  `robots.txt` triple-placement (inventory §1.5) matches the two strongest
  evidenced patterns in this brief: (a) most documented crawlers do not
  render JavaScript, and (b) among discovery files, `sitemap.xml` is
  measurably fetched far more than `llms.txt` by the same crawlers.
- The inventory's own flagged gap — "rung 0 (indexability)... is the known
  gap," i.e., OYL is not yet confirmed indexed by Google/Bing — is, per §3,
  structurally more consequential for Gemini/AI-Overviews and Copilot (both
  architecturally dependent on those two indexes for grounding) than for
  Perplexity or Claude (each running independent retrieval indexes).
- No evidence in this brief demonstrates that OYL's `llms.txt` file is being
  fetched by any production assistant; the best available server-log studies
  (Ahrefs 137K-domain study, WISLR 48-day case study) both found effectively
  zero AI-crawler requests for `llms.txt` files generally. Inventory open
  gap #5 ("whether `llms.txt` is fetched at all... or is
  convention-folklore") is best answered, on current public evidence, as
  "closer to folklore than to measured practice," pending OYL's own
  server-side visibility (which GitHub Pages does not provide — inventory
  §3 constraint).
- Open gap #4 (whether fetch recipes in `index.json` are ever followed) has
  no answer in any public source surfaced by this research pass; it remains
  exactly the empirical question the inventory document already identifies
  as unmeasured, and desk research cannot close it.
- The one controlled causal study found on structured data (Ahrefs,
  1,885-page DiD) found **no positive citation effect** from adding JSON-LD
  schema, on pages that were already well-cited. OYL already ships a
  JSON-LD `Dataset` block (inventory §1.5); this brief found no evidence
  that step measurably changes assistant citation behavior, positively or
  negatively, though OYL's case (a previously-uncited, low-traffic site) is
  outside the studied population (pages with 100+ existing citations).

---

## Sources

- OpenAI, "Bots and crawlers" documentation — developers.openai.com/api/docs/bots (accessed 2026-07-22)
- Anagram, "GPTBot Explained... in 2026" — anagram.ai/blog/gptbot-explained-how-chatgpt-crawls-sees-and-cites-your-site-in-2026 (2026)
- SE Roundtable, "Anthropic Updates Its Crawler Documentation: ClaudeBot, Claude-User & Claude-SearchBot" — seroundtable.com/anthropic-updates-its-crawler-docs-40978.html (2026-02)
- Search Engine Journal, "Anthropic's Claude Bots Make Robots.txt Decisions More Granular" — searchenginejournal.com/anthropics-claude-bots-make-robots-txt-decisions-more-granular/568253/ (2026)
- ppc.land, "Anthropic clarifies what its three web crawlers do — and how to block them" (2026)
- Perplexity, "Perplexity Crawlers" docs — docs.perplexity.ai/docs/resources/perplexity-crawlers (accessed 2026-07-22)
- Perplexity, "Agents or Bots: Making Sense of AI on the Open Web" — perplexity.ai/hub/blog/agents-or-bots-making-sense-of-ai-on-the-open-web (2025-08)
- Search Engine World, "Perplexity Says an Agent isn't a Bot and Not Required to Honor Robots.txt" (2025-2026)
- Search Engine Journal, "Cloudflare Delists And Blocks Perplexity From Crawling Websites" — searchenginejournal.com/cloudflare-delists-and-blocks-perplexity-from-crawling-websites/552899/ (2025-08)
- Xponent21, "Anthropic Lists Two Web-Search Subprocessors for Claude: Brave & TurboPuffer" (2026)
- mostailabs, "How Claude Finds Your Business via Brave Search (2026)" (2026)
- Google, "Grounding with Google Search" — ai.google.dev/gemini-api/docs/google-search (accessed 2026-07-22)
- Google Cloud, "Grounding overview" — docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/overview (accessed 2026-07-22)
- Rankly Substack, "How Microsoft Copilot Search Works: The Architecture Deepdive" (2026)
- Otterly.ai, "Bing Webmaster Tools AI Performance Report" (2026-02-11)
- UltimateInfoGuide, "Microsoft Web IQ for AI Agents 2026" (2026-06-02)
- llmstxt.org — spec and origin page (accessed 2026-07-22)
- ppc.land, "llms.txt adoption rises 8.8x but 97% of files get zero AI requests" (2026-07-02)
- Ahrefs, "We Analyzed 137K Sites: 97% of llms.txt Files Never Get Read" — ahrefs.com/blog/llmstxt-study/ (2026-07-02)
- Rankability, "LLMS.txt Adoption: 8.7% of the Top 1,000 (June 2026)" (2026-06)
- SE Roundtable, "Google Search Team Does Not Endorse LLMs.txt Files" — seroundtable.com/google-does-not-endorse-llms-txt-40789.html (2026)
- Let's Data Science, "Google's Mueller Says llms.txt Won't Guide LLM Recommendations" (2026)
- Search Engine Journal, "Google Confirms LLMs.txt Has No Current Implementation" (2026)
- WISLR, "AI Bot Traffic Is Accelerating Fast. 48 Days of Server Logs..." — wislr.com/articles/ai-bot-behavior-log-analysis (2026-03-20, updated 2026-07-20)
- Ahrefs, "We Tracked 1,885 Pages Adding Schema. AI Citations Barely Moved." — ahrefs.com/blog/schema-ai-citations/ (2026-05-11)
- Ahrefs, AI brand-visibility correlation study (75,000 brands) — ahrefs.com/blog/ai-brand-visibility-correlations (2025-2026)
- searchoptimo.com, "Do AI Crawlers Render JavaScript? GPTBot, ClaudeBot, and Perplexity in 2026" (2026)
- asklantern.com, "AI Crawlers Do Not Render JavaScript" (2026)
- aiplusautomation.com, "Does ChatGPT Use Bing or Google? The Full Search Architecture Explained (2026)" (2026)
- practicalecommerce.com, "Google's index now powers ChatGPT" (2026)

## Known limitations of this brief

- Desk research only (WebSearch/WebFetch); no server logs of OYL's own site
  were available (GitHub Pages does not expose them — inventory §3), so
  nothing here is OYL-specific measurement.
- Several load-bearing numbers (Ahrefs schema study, Ahrefs llms.txt study,
  WISLR log study) come from single studies each; none were independently
  replicated by a second research group as of this brief's date.
- ChatGPT Search's index dependency (Bing vs. proprietary) could not be
  resolved to a primary OpenAI source and is reported here as an open
  conflict, not a settled fact.
- Google Dataset Search's role (if any) in assistant grounding is an
  unfilled gap, not a negative finding — absence of evidence, not evidence
  of absence.
