---
run_date: 2026-07-23
topic: "Model Context Protocol (MCP) feasibility for a static, volunteer-run, GitHub-Pages-hosted project — adoption, transport, hosting, discovery, and marginal value over a static JSON API + llms.txt"
study: agentic-layer (study #1)
---

# MCP feasibility brief (mid-2026)

Scope note: this brief answers the kickoff question set only. It does not
propose changes to OYL's layer (see `02-layer-inventory.md` for the as-built
inventory this study treats as ground truth). Labels match
`assistant-discovery.md`: `[verified]` (primary-source or corroborated by
independent data), `[vendor-claim]` (stated by the vendor, not independently
measured), `[folklore/unclear]` (widely repeated, not demonstrated).

---

## 1. MCP adoption reality: which surfaces actually connect, for whom

**Claude (Anthropic).** Custom connectors via remote MCP are available on
claude.ai, Claude Desktop, Cowork, and mobile, across **Free, Pro, Max, Team,
and Enterprise** plans — free-tier users are capped at **one** custom
connector `[verified — Claude Help Center, "Get started with custom
connectors using remote MCP," support.claude.com/en/articles/11175166,
accessed 2026-07-23]`. Connection UX: user goes to Settings → Connectors →
"+", pastes the server's URL, optionally supplies OAuth client ID/secret, and
Claude's own cloud infrastructure — not the user's device — makes the
outbound connection `[verified, same source; also platform.claude.com/docs
"MCP connector," accessed 2026-07-23]`. This has a direct hosting
consequence: **the server must be reachable over the public internet from
Anthropic's IP ranges**; anything behind a firewall or requiring an
allowlist won't connect `[verified, same source]`.

**ChatGPT (OpenAI).** MCP connections require **Plus, Pro, Business,
Enterprise, or Edu** plans with **Developer Mode** switched on for *custom*
remote connectors; the free consumer tier has no path to add an arbitrary
third-party MCP server `[vendor-claim/product-doc — synthesized from OpenAI
Help Center "ChatGPT Business — Release Notes" and third-party
documentation aggregation, help.openai.com/en/articles/11391654, accessed
2026-07-23; corroborated by obot.ai "ChatGPT MCP Support: Enterprise
Security Guide 2026"]`. Separately, OpenAI curates an **Apps/connector
directory** (Notion, Linear, Salesforce Agentforce, Amplitude, Fireflies,
Vercel, Monday.com, Stripe, Hex, Egnyte, Alpaca, BioRender, Semrush,
Jam.dev, etc.) that is one-click-installable "on any plan" — but this is
OpenAI's own curated allowlist of partner servers, not a general "point ChatGPT
at any URL" mechanism `[vendor-claim, same sources]`. A project like OYL
could not get into that curated list without OpenAI's direct partnership,
which is a materially different bar than publishing a URL.

**Other surfaces.** No source found in this pass documents a general,
user-facing "paste an arbitrary remote MCP server URL" flow for Gemini,
Perplexity, or Copilot consumer products as of mid-2026 comparable to
Claude's connector settings; MCP traction on those surfaces (per §4 below)
skews toward developer/IDE contexts (Cursor, VS Code) rather than the
consumer chat app. This is an **open gap** for this brief — not confirmed
absent, just not found — rather than a negative finding.

**Distinction: remote (hosted) vs. local (stdio) servers.** The two
architectures have opposite implications for OYL:
- **Local/stdio servers** run as a subprocess the *user's own machine*
  launches (Claude Desktop, Claude Code, most IDE integrations) — the
  "server" is code the user downloads and runs, with no public hosting
  requirement at all, but also no consumer-app discovery path; it targets
  developers who edit a JSON config file `[verified, MCP spec, "stdio" transport
  section, modelcontextprotocol.io/specification/2025-06-18/basic/transports,
  accessed 2026-07-23]`.
- **Remote/hosted servers** are what claude.ai's connector UI and ChatGPT's
  Developer Mode expect: a long-lived, publicly reachable HTTPS endpoint
  Anthropic's or OpenAI's cloud calls into on the user's behalf
  `[verified, same Claude Help Center source]`.

---

## 2. Transport reality: can MCP be served from purely static files?

**No — plainly, and for a structural reason, not an incidental one.**

The MCP spec (2025-06-18, current at the point Anthropic and most SDKs
target; superseded 2025-11-25, see §6) defines exactly two standard
transports `[verified, modelcontextprotocol.io/specification/2025-06-18/
basic/transports, accessed 2026-07-23]`:

1. **stdio** — the client *launches the server as a subprocess* and talks to
   it over stdin/stdout. This has no "hosting" question at all because there
   is no server process independent of the client's own machine; it is
   definitionally incompatible with "publish a server for others to reach,"
   which is what a static site does.
2. **Streamable HTTP** (replacing the deprecated 2024-11-05 HTTP+SSE
   transport) — the server "**MUST** provide a single HTTP endpoint path...
   that supports both POST and GET methods." Every JSON-RPC message the
   client sends "**MUST** be a new HTTP POST request to the MCP endpoint,"
   and the server must respond either with `Content-Type: application/json`
   (one JSON object) or `text/event-stream` (an SSE stream) — chosen
   dynamically, per request, by server-side logic, not a fixed file
   `[verified, same source, quoted directly]`.

Why a static file host cannot satisfy this, specifically:

- **POST is structurally impossible.** A static host (GitHub Pages included)
  serves pre-built files in response to GET; it has no code path that can
  accept an HTTP POST body, parse JSON-RPC out of it, and compute a
  request-specific response. There is nothing to "configure around" here —
  it is not a POST-request quota or a CORS setting, it's the absence of any
  server-side execution at all `[verified — GitHub's own community docs
  state GitHub Pages "does not support backend code like PHP, Node.js, or
  Python; it is strictly a static site hosting service," github.com/orgs/
  community/discussions/167372, accessed 2026-07-23]`.
- **Session semantics require server-side state.** The spec's optional
  session-management layer has the server mint an `Mcp-Session-Id` at
  initialization, require it on every subsequent request, and be able to
  return `404` once a session is torn down — i.e., the server must
  *remember* which sessions are live `[verified, same spec source, "Session
  Management" section]`. A static file cannot hold or check that state.
- **The response itself is computed, not fixed.** Even the simplest
  "stateless" Streamable HTTP server (no session ID at all) still has to
  execute code per incoming POST to run whichever tool the JSON-RPC request
  named and return that tool's *result* — by definition a dynamic,
  request-dependent payload a static file (whose bytes are the same for
  every visitor) cannot produce.

One independent write-up direct on this exact question concurs: "GitHub
Pages cannot run MCP servers because it's fundamentally a static hosting
service... MCP servers require active runtime capabilities — including
continuous operation, stateful connections, and dynamic code execution —
that static hosts simply cannot provide," recommending hosting the server
elsewhere and using the static site only for docs `[folklore/unclear —
single blog-style source, but consistent with and derived from the same
spec-level facts above, not a novel claim]`. [0x7c2f.github.io
"Can You Run MCP Servers on GitHub Pages?", accessed 2026-07-23]

**Net answer to the load-bearing question:** there is no configuration,
polyfill, or clever static trick that serves a spec-conformant MCP endpoint
from files alone. MCP requires an always-available process that executes
code per request. This is categorically different from OYL's existing
static JSON API, where every possible response is a pre-built file GET
serves verbatim.

---

## 3. Hosting-free / near-free compute options, if compute were added

Since MCP requires *some* compute, the real question if OYL ever pursued it
is which minimal-compute host is least burdensome for a volunteer project
with no ops rotation. None of these are "free" in the zero-obligation sense
GitHub Pages is; all require an account and at least implicit uptime
responsibility.

| Option | Real free-tier limits (2026) | What breaks unattended for weeks | Account/secret/uptime burden |
|---|---|---|---|
| **Cloudflare Workers** | 100,000 requests/day, 10ms CPU time per invocation, free "indefinitely" per Cloudflare's own tier structure; paired free KV (1GB/100K reads-day/1K writes-day), D1 (5GB/5M reads-day), R2 (10GB-month) `[vendor-claim, agentdeals.dev "Cloudflare Workers Free Tier 2026," accessed 2026-07-23, cross-checked against a second independent tracker eastondev.com, same date]` | Nothing time-based inherently breaks — Workers are stateless edge functions, not a process that can "go down" from disuse; the risk is a Cloudflare account/API-token expiring from inactivity or a billing/ToS change, not the code decaying | Cloudflare account + a deploy pipeline (Wrangler CLI or CI) someone must maintain; free tier is generous enough that OYL's low query volume is very unlikely to hit 100K req/day |
| **Vercel / Netlify Functions** | Both offer free serverless-function tiers (invocation-count and execution-second caps); exact current numbers not independently verified in this pass — **treat as an open gap**, not asserted here | Same category as Cloudflare — stateless functions don't "sleep" and decay; risk is account dormancy policies, not code rot | Same class of burden: an account, a repo-linked deploy, and someone who notices if a plan/ToS/pricing change silently breaks the free tier |
| **Val Town** | Runs on Deno; ships an official MCP server/tooling and offers a free tier to "evaluate before committing to a paid plan," but the specific free-tier request/compute caps were not found in this pass `[vendor-claim, blog.val.town "Introducing Val Town MCP," accessed 2026-07-23; pricing structure per aistackpicks.com "Val Town Pricing 2026," which reports a **2026 price increase** — new Pro moved to $25/mo while grandfathered users kept $10/mo]` | Not established in this pass whether idle "vals" get throttled/archived — **open gap** | A hosted platform-specific account; the 2026 price change shows free/cheap tiers are not guaranteed stable over a multi-year volunteer horizon |
| **Deno Deploy** | Searched but no 2026 free-tier specifics were independently confirmed in this pass — **open gap**, not asserted | Not established | Not established |
| **GitHub Actions** | Not a hosting option for MCP at all: Actions runs jobs to completion on a schedule or trigger and then tears the runner down; it cannot hold open an HTTP listener answering live client requests. It is the wrong tool for "serve a long-lived endpoint," full stop — this is a structural mismatch, not a limits question `[verified by omission — no source found describing Actions as a viable MCP transport host, consistent with Actions' documented job-based execution model]` | N/A — not applicable | N/A |
| **MCP directories that host on your behalf** | No source found in this pass describing a registry (PulseMCP, Glama, the official `registry.modelcontextprotocol.io`) that *hosts and runs* third-party server code for the publisher — every registry found (§4) stores **metadata pointing at a server the publisher already runs elsewhere**, not the running server itself `[verified, github.com/modelcontextprotocol/registry documentation: "MCP registries host metadata about packages, but not the package code or binaries," accessed 2026-07-23]` | N/A | Confirms there is no such thing as a free "just list it and it runs" option; compute is unavoidable if MCP is pursued at all |

**Cross-cutting finding:** every option above that could plausibly work
still requires (a) a third-party account distinct from GitHub, (b) a
deploy/redeploy mechanism someone must operate, and (c) implicit trust that
a free tier remains free and its ToS doesn't change unattended — which Val
Town's own 2026 price change demonstrates is not guaranteed. None of this
matches the "static files only... survive unattended weeks" constraint in
inventory §3 as-is; all of them add a maintenance surface GitHub Pages does
not have today.

---

## 4. Discovery: how do users/assistants find a third-party MCP server?

Three distinct discovery paths exist, with very different evidentiary
weight:

1. **The official MCP Registry** (`registry.modelcontextprotocol.io`) —
   community-driven, backed by Anthropic, GitHub, PulseMCP, and Microsoft
   among others; publishers self-register via a reverse-DNS-style namespace
   tied to a verified GitHub account or domain; it stores **metadata only**,
   not running code `[verified, github.com/modelcontextprotocol/registry,
   modelcontextprotocol.io/registry/about, accessed 2026-07-23]`. As of
   2026-05-24 it held roughly 9,652 "latest" server records and ~28,959
   server/version records total `[vendor-claim/self-reported registry count,
   via digitalapplied.com "MCP Ecosystem H1 2026 Retrospective," accessed
   2026-07-23]`.
2. **Vendor-curated one-click directories** — e.g., ChatGPT's Apps
   directory (§1) and Claude's own directory connectors — these are
   editorial allowlists, not open self-service listings; getting into one
   is a partnership/approval process, not a publish action.
3. **Third-party aggregator sites** (PulseMCP, Glama, mcpmux, etc.) —
   independent catalogs that re-list registry/GitHub entries with search and
   ranking; useful for developer discovery, not surfaced inside a consumer
   assistant's UI.

**Is there measured usage data, or is this vendor-claim territory?**
Overwhelmingly the latter, with the significant exception of one caveat:
- Server *counts* (registry size, GitHub `mcp-server`-topic repo count —
  15,926 repos as of 2026-05-24 — SDK download counts of "97M+ monthly"
  through December 2025) are all self-reported or platform-side aggregate
  numbers, not independent usage measurement `[vendor-claim throughout,
  digitalapplied.com and nordicapis.com "10 Interesting MCP Statistics,"
  accessed 2026-07-23]`.
- The one figure in this pass that reads as closer to independently
  measured is Stacklok's 2026 software survey finding **41% of surveyed
  software organizations** in "limited or broad production" with MCP
  servers — reported specifically as **replacing an earlier, unsourced 78%
  claim** that had circulated without a named source `[vendor-claim-adjacent
  — third-party survey vendor, not MCP-project-self-reported, but still a
  single survey, not independently replicated; digitalapplied.com,
  accessed 2026-07-23]`.
- No source in this pass measures *end-user* discovery behavior — i.e.,
  no data on how often a consumer actually finds and adds a third-party
  server via the registry versus a blog post versus a friend's
  recommendation. This is an **open gap**.

**Net finding for OYL's specific question:** publishing to the official
registry is a metadata-listing action (comparable in kind to submitting a
sitemap) — it does not itself solve hosting, and there is no data showing
consumer assistants surface registry entries to end users the way, say,
ChatGPT's curated Apps directory does.

---

## 5. What MCP would offer over a static JSON API + llms.txt — skeptical read

**What MCP genuinely adds, mechanically:**
- **Typed tool schemas the client parses structurally**, not prose the model
  has to interpret — `tools/list` returns machine-readable JSON Schema
  per tool, and `tools/call` returns a typed result (as of 2025-06-18,
  including "structured tool outputs") `[verified, modelcontextprotocol.io/
  specification/2025-06-18/changelog, accessed 2026-07-23]`. A static JSON
  endpoint's shape is also machine-readable (OYL's own JSON Schemas under
  `site/api/v1/schemas/`), so the marginal gain is specifically that the
  *tool-calling* client (not just a page-fetching one) gets a name +
  description + parameter schema *in the same protocol turn it decides
  whether to call it*, rather than needing to have already fetched and
  reasoned over `index.json`'s prose "fetch recipes."
- **Parameterized, server-computed queries.** OYL's static files are
  pre-built for a fixed set of shapes (per-ward, per-route, per-corridor
  files); a real question outside that fixed decomposition (e.g., "wards
  where crash rate rose but protected-lane share also rose, sorted by
  danger score, top 5") currently requires the *model* to fetch multiple
  files and filter/join client-side. An MCP tool *could* offer that as a
  single parameterized call the server computes — the one capability a pure
  static file fundamentally cannot provide, because static files can't
  execute arbitrary query logic. This is real, but it also requires the
  compute §2–3 established a static host cannot supply.
- **Discoverability inside tool-calling UIs specifically** — a connector
  shows up in Claude's/ChatGPT's UI as an explicit, user-added capability,
  which is a different (and for the reasons in §1/§4, narrower and more
  gated) discovery path than "the model happens to fetch a URL."

**What it would NOT fix — the honest limits:**
- It does **not** fix inventory's core unresolved risk (T7): whether an
  assistant that receives OYL's caveat/tier metadata actually *carries it
  into its answer*. A typed tool result can carry a `data_tier` field just
  as easily as (and no more reliably than) a JSON file already does; nothing
  about MCP's protocol layer forces the *model* to surface that field to
  the user rather than silently drop it. This is a model-behavior question,
  not a transport question, and MCP does not touch it.
- It does **not** improve discovery for the assistants gated by Google/Bing
  index absence (Gemini/AI-Overviews, Copilot per `assistant-discovery.md`
  §3) — those grounding paths don't involve MCP tool-calling at all.
- It does **not** solve the free-tier/consumer-app gap in §1 — ChatGPT's
  free tier and ordinary Claude usage without the user manually adding a
  connector get **no benefit** from an OYL MCP server existing; only users
  who already know to add a custom connector (Claude Free/Pro+ with one
  connector slot, or ChatGPT Developer Mode on a paid plan) could reach it
  at all.
- It does **not** remove the need for the underlying static contract — an
  MCP server would still read from (or wrap) the same `site/data/` files;
  it is an additional access *surface*, not a replacement data source.
- Server-side "reliable tool descriptions" is a claim, not a guarantee: the
  spec defines the *shape* of a tool description, but whether a given
  assistant's model reliably reads and acts on that description correctly
  is exactly the same class of unmeasured question `assistant-discovery.md`
  raises for llms.txt (T7) — no source in this research pass tested
  tool-description compliance empirically.

---

## 6. Maintenance / deprecation risk: spec churn over the trailing ~18 months

Four dated spec revisions in roughly 20 months, with real breaking changes
in the middle of that run:

- **2024-11-05** — original stable spec; transport was HTTP+SSE (two
  separate endpoints) `[verified, modelcontextprotocol.io/specification/
  2025-06-18/basic/transports, "Backwards Compatibility" section, accessed
  2026-07-23]`.
- **2025-03-26** — **Streamable HTTP replaces HTTP+SSE** as the standard
  remote transport (single endpoint, POST+GET, optional SSE) — a
  transport-level breaking change requiring servers wanting to support old
  clients to run both transports side by side `[verified, same source]`.
- **2025-06-18** — **JSON-RPC batching removed**, a breaking change:
  a 2025-03-26 client is not guaranteed compatible with a server that
  supports only 2025-06-18 `[verified, forgecode.dev "MCP 2025-06-18 Spec
  Update," accessed 2026-07-23]`. Added structured tool outputs, elicitation
  (server-initiated user prompts), resource links in tool results, and a
  mandatory `MCP-Protocol-Version` HTTP header with defined fallback
  behavior `[verified, modelcontextprotocol.io/specification/2025-06-18/
  changelog, accessed 2026-07-23]`.
- **2025-11-25** — marked as MCP's first fully "stable" revision, one year
  after public launch; adds an experimental async **Tasks** primitive
  (call-now, fetch-later request handling), OpenID Connect Discovery
  support, tool/resource icon metadata, and incremental OAuth scope consent
  — explicitly **backward compatible** with 2025-06-18 per its own release
  notes `[vendor-claim/spec-changelog, workos.com "MCP 2025-11-25 is here,"
  and modelcontextprotocol.io/specification/2025-11-25/changelog, both
  accessed 2026-07-23]`.
- **A further revision is already in motion**: a "2026-07-28 MCP
  Specification Release Candidate" post was found dated five days after
  this brief's run date, indicating the spec continues to move on
  roughly a semi-annual cadence `[verified — dated blog post exists at
  blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/,
  accessed 2026-07-23; brief does not assert its contents since it postdates
  this research pass]`.

**Net churn read:** two of the four revisions in the trailing 18 months
(2025-03-26, 2025-06-18) carried transport- or protocol-level breaking
changes; the most recent (2025-11-25) explicitly reversed course toward
backward compatibility, and a further revision is already public as an RC.
For a volunteer project with no dedicated maintenance rotation, this reads
as an ecosystem still revising core mechanics roughly twice a year, not yet
settled to the multi-year stability of, e.g., plain JSON-Schema-described
REST.

---

## Implications for OYL (facts only, no proposals)

- Inventory §3's constraint — "static files only... no server-side compute"
  — is not compatible with MCP as specified. Section 2 above establishes
  this at the protocol level, not merely as a hosting inconvenience: the
  spec requires a server that accepts HTTP POST and computes a
  request-specific response, which a static host structurally cannot do
  (GitHub's own docs confirm GitHub Pages has no backend execution of any
  kind). No workaround changes this without adding a non-GitHub-Pages
  compute host.
- Inventory §3's second constraint — "volunteer-run... must survive
  unattended weeks" — is in tension with every near-free hosting option in
  §3 above: all require an external account, a deploy pipeline, and
  exposure to that provider's own pricing/ToS changes (Val Town's 2026 price
  increase is a concrete instance of a "free-ish" tier's terms moving under
  a project that didn't initiate the change).
- Inventory §3's "same files for humans and agents" guarantee (§2 in the
  inventory) would need a second code path if MCP were added: a tool-calling
  server is additional server-side logic layered on top of (not a
  replacement for) the existing static `site/data/` contract, meaning the
  equivalence-auditability property the inventory currently gets for free
  (human pages and `/api/v1/` are both generated from one static contract)
  would have to be re-established for a live MCP endpoint separately.
- The consumer-reach gap in §1 is directly relevant to inventory's framing
  that OYL's audience is "an AI tool you already use" (§1.6 of the
  inventory): as of mid-2026, reaching an MCP server requires either a paid
  ChatGPT tier with Developer Mode explicitly enabled, or a Claude user
  manually adding a custom connector (one slot on the free tier) — neither
  matches the "just ask your existing assistant a question" framing the
  home page already ships, which today works (to the extent it works at
  all — unmeasured, per assistant-discovery.md) via ordinary web
  fetch/search, not a connector a user must first install.
- Inventory open gap #5 (whether `llms.txt`/fetch-recipe following happens
  at all, per assistant-discovery.md) is not answered or superseded by
  anything in this brief; MCP is an alternative access surface, not a fix
  for the existing unmeasured question of whether assistants read and
  correctly act on OYL's current static contract.
- The registry/discovery mechanisms in §4 store metadata pointing at a
  server the publisher runs elsewhere; none of the sources found describe a
  registry that itself executes or hosts third-party server code, so listing
  in a registry does not substitute for the compute requirement in §2–3.

---

## Known limitations of this brief

- Desk research only (WebSearch/WebFetch); no hands-on test of deploying an
  MCP server on any of the §3 platforms was performed, so specific numeric
  free-tier limits for Vercel/Netlify Functions and Deno Deploy could not be
  independently confirmed in this pass and are flagged as open gaps rather
  than stated.
- Consumer-app MCP support for Gemini, Perplexity, and Copilot specifically
  (as opposed to developer/IDE contexts) was not confirmed or denied by any
  source found in this pass — an open gap, not a negative finding.
- Usage/discovery statistics in §4 are dominated by vendor- and
  registry-self-reported counts; only one third-party survey figure
  (Stacklok, 41% production adoption) reads as independently sourced, and
  even that is a single survey, not replicated.
- The 2026-07-28 MCP spec release-candidate post postdates this brief's
  run date; its contents were not reviewed and nothing about it is claimed
  beyond its existence.
- This brief did not evaluate the security/authorization implications of
  OAuth 2.1 for a hypothetical OYL MCP server in depth — noted in §1 as a
  fact (Claude requires interactive OAuth, not machine-to-machine
  client_credentials) but not explored further, since inventory §3 already
  rules out the compute this would run on.

---

## Sources

- Claude Help Center, "Get started with custom connectors using remote MCP" — support.claude.com/en/articles/11175166 (accessed 2026-07-23)
- Claude Help Center, "Build custom connectors via remote MCP servers" — support.claude.com/en/articles/11503834 (accessed 2026-07-23)
- Claude Platform Docs, "MCP connector" — platform.claude.com/docs/en/agents-and-tools/mcp-connector (accessed 2026-07-23)
- sunpeak.ai, "Claude Connector Authentication: How OAuth Works and When You Need It (May 2026)" (2026-05)
- OpenAI Help Center, "ChatGPT Business - Release Notes" — help.openai.com/en/articles/11391654 (accessed 2026-07-23)
- obot.ai, "ChatGPT MCP Support: Enterprise Security Guide 2026" (2026)
- Model Context Protocol, "Transports" specification (2025-06-18) — modelcontextprotocol.io/specification/2025-06-18/basic/transports (accessed 2026-07-23)
- Model Context Protocol, "Key Changes" changelog (2025-06-18) — modelcontextprotocol.io/specification/2025-06-18/changelog (accessed 2026-07-23)
- Model Context Protocol, "Key Changes" changelog (2025-11-25) — modelcontextprotocol.io/specification/2025-11-25/changelog (accessed 2026-07-23)
- WorkOS, "MCP 2025-11-25 is here: async Tasks, better OAuth, extensions, and a smoother agentic future" — workos.com/blog/mcp-2025-11-25-spec-update (2025-11)
- ForgeCode, "MCP 2025-06-18 Spec Update: AI Security, Structured Output, and User Elicitation for LLMs" — forgecode.dev/blog/mcp-spec-updates (2026)
- Model Context Protocol Blog, "The 2026-07-28 MCP Specification Release Candidate" — blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate (accessed 2026-07-23, postdates this brief's research)
- GitHub, "modelcontextprotocol/registry" — github.com/modelcontextprotocol/registry (accessed 2026-07-23)
- Model Context Protocol, "The MCP Registry" — modelcontextprotocol.io/registry/about (accessed 2026-07-23)
- GitHub Community Discussions, "Does GitHub Pages support backend code like PHP or Node.js?" — github.com/orgs/community/discussions/167372 (accessed 2026-07-23)
- 0x7c2f.github.io, "Can You Run MCP Servers on GitHub Pages?" (accessed 2026-07-23)
- AgentDeals, "Cloudflare Workers Free Tier 2026: Limits, Pricing & What Changed" — agentdeals.dev/vendor/cloudflare-workers (accessed 2026-07-23)
- eastondev.com, "Cloudflare Free Tier Limits Checklist" (2026-05-26)
- Val Town Blog, "Introducing Val Town MCP" — blog.val.town/mcp (accessed 2026-07-23)
- AI Stack Picks, "Val Town Pricing 2026: Every Plan Explained" — aistackpicks.com/reviews/val-town-pricing-2026 (2026)
- digitalapplied.com, "MCP Ecosystem H1 2026 Retrospective: Adoption Data Points" (2026)
- digitalapplied.com, "MCP Adoption Statistics 2026: Model Context Protocol" (2026)
- Nordic APIs, "10 Interesting MCP Statistics" — nordicapis.com/10-interesting-mcp-statistics (2026)
- Nordic APIs, "Getting Started With the Official MCP Registry API" — nordicapis.com/getting-started-with-the-official-mcp-registry-api (2026)
