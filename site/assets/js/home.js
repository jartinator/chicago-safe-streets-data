/* Home / orientation screen: what On Your Left! is, live headline data, who
 * it's for with a concrete next action per audience, and how to use the
 * machine-readable agent layer. Same structure as action.js — a pure,
 * Node-testable model function (no BSD/DOM dependency) plus browser-only DOM
 * code guarded behind `typeof document`. Headline numbers are never hardcoded:
 * the stat VALUES come from api/v1/citywide.json at load, so they stay correct
 * as the weekly refresh moves them. */
(function () {
  // ---- Pure model (Node + browser) ----

  // Select the headline findings to feature, in the given order, from a parsed
  // citywide.json. Returns one entry per id that exists in `citywide.findings`
  // (missing ids are skipped, never faked), carrying the finding's own stat and
  // data_tier so the tile's number and quality badge always match the source.
  function pickHeadlineStats(citywide, ids) {
    if (!citywide || !Array.isArray(citywide.findings) || !Array.isArray(ids)) return [];
    const byId = new Map(citywide.findings.map((f) => [f.id, f]));
    return ids
      .map((id) => byId.get(id))
      .filter((f) => f && f.stat != null)
      .map((f) => ({ id: f.id, stat: f.stat, tier: f.data_tier || "derived", title: f.title }));
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { pickHeadlineStats };
  }

  // ---- DOM code (browser only) ----
  if (typeof document === "undefined") return;

  const B = window.BSD;

  // Which citywide findings to surface, in order, with the short home-page
  // label shown under the number. The stat itself is pulled live from the JSON;
  // only the framing label lives here.
  const HEADLINE_STATS = [
    { id: "ksi-trend", label: "cyclists killed or seriously injured in the last 12 months" },
    { id: "protected-share", label: "of Chicago's bikeway miles are physically protected" },
    { id: "bna-score", label: "national low-stress network score (PeopleForBikes)" },
    { id: "hit-and-run", label: "of reported cyclist crashes are hit-and-run" },
  ];

  // The three things the project does — the "key functions".
  const FUNCTIONS = [
    {
      title: "See the map & network",
      body: "Every police-reported cyclist crash since 2017, layered over Chicago's bikeway " +
        "network by facility type — protected, buffered, painted, greenway, trail. Drill from " +
        "ward to corridor to intersection.",
      href: "map.html",
      cta: "Open the map",
    },
    {
      title: "Hold your ward accountable",
      body: "A per-ward record: crash trend, safety scorecard, your alderperson's sponsorship " +
        "and voting history on street-safety measures, menu-fund spending, and what's coming up " +
        "at City Hall.",
      href: "action.html",
      cta: "Find your ward",
    },
    {
      title: "Trust every number",
      body: "Rebuilt weekly from the Chicago Data Portal and other public sources. Every figure " +
        "is labeled real, proxy, derived, mock, or crowdsourced — and every methodology is written down.",
      href: "methodology.html",
      cta: "How the numbers work",
    },
  ];

  // Audience cards: heading, one-line value prop, and a concrete next step.
  const AUDIENCES = [
    {
      title: "Journalists & researchers",
      body: "Headline findings with the caveats attached, a full methodology, and downloadable " +
        "CSVs with provenance baked into every export.",
      links: [
        ["findings.html", "Read the findings"],
        ["methodology.html", "Methodology"],
        ["table.html", "Explore & download data"],
      ],
    },
    {
      title: "Advocates & community orgs",
      body: "Ward one-pagers for your next public comment, council voting records, upcoming " +
        "safety-committee hearings, and a tracker of proposed and in-progress projects.",
      links: [
        ["action.html", "Ward reports & hearings"],
        ["network.html", "Network quality"],
      ],
    },
    {
      title: "Developers & AI agents",
      body: "A documented, versioned JSON API mirroring every number on the site — plus an " +
        "llms.txt index written in plain language for language models. Details below.",
      links: [
        ["api/v1/index.json", "Browse the API"],
        ["contributing.html", "Downloads & docs"],
      ],
    },
    {
      title: "Elected officials & staff",
      body: "Your ward's crash record and safety scorecard on one page, the legislation tagged " +
        "to street safety, and the committee hearings coming up next.",
      links: [
        ["action.html", "Your ward's record"],
        ["findings.html", "Citywide picture"],
      ],
    },
  ];

  const SITE_ORIGIN = "https://jartinator.github.io/chicago-safe-streets-data";

  function heroHTML() {
    const l = B.LINKS;
    return `<section class="home-hero">` +
      `<h1>Chicago bike safety, on the record.</h1>` +
      `<p class="home-lead">On Your Left! turns Chicago's public crash, infrastructure, and ` +
      `City Council data into a ward-by-ward record of how safe the city's streets really are ` +
      `for people on bikes — rebuilt every week, with every number labeled by where it came from.</p>` +
      `<div class="home-cta-row">` +
      `<a class="btn primary" href="map.html">Explore the map →</a>` +
      `<a class="btn" href="action.html">Find your ward's record</a>` +
      `</div>` +
      `<p class="home-hero-note">See a blocked lane or a hazard? This is an evidence layer, not a ` +
      `reporting one — report it to <a href="${B.esc(l.threeOneOne)}" target="_blank" rel="noopener">311</a> ` +
      `or <a href="${B.esc(l.blu)}" target="_blank" rel="noopener">Bike Lane Uprising</a>.</p>` +
      `</section>`;
  }

  function statStripHTML(stats) {
    if (!stats.length) {
      return `<section class="home-stats"><p class="muted">Headline numbers are on the ` +
        `<a href="findings.html">findings page</a>.</p></section>`;
    }
    // The number+label link to the findings page; the tier badge is a sibling
    // <button> (never nested in the <a> — it opens the tier-explainer modal via
    // common.js's delegated handler, and a button-in-anchor is invalid HTML).
    const tiles = stats.map((s) => {
      const label = (HEADLINE_STATS.find((h) => h.id === s.id) || {}).label || s.title;
      return `<div class="home-stat">` +
        `<a class="home-stat-main card-link" href="findings.html">` +
        `<span class="home-stat-num">${B.esc(String(s.stat))}</span>` +
        `<span class="home-stat-label">${B.esc(label)}</span>` +
        `</a>` +
        `<span class="home-stat-badge">${B.badgeHTML(s.tier)}</span>` +
        `</div>`;
    }).join("");
    return `<section class="home-stats" aria-label="Headline data">${tiles}</section>` +
      `<p class="home-stats-foot muted">Live from the weekly data build · tap any label to see ` +
      `what its data-quality tag means · <a href="findings.html">all findings and caveats →</a></p>`;
  }

  function functionsHTML() {
    const cards = FUNCTIONS.map((f) =>
      `<div class="card home-func">` +
      `<h3>${B.esc(f.title)}</h3>` +
      `<p>${B.esc(f.body)}</p>` +
      `<a class="btn" href="${B.esc(f.href)}">${B.esc(f.cta)} →</a>` +
      `</div>`).join("");
    return `<section class="section-gap">` +
      `<h2>What this is</h2>` +
      `<div class="cards-grid">${cards}</div>` +
      `</section>`;
  }

  function audiencesHTML() {
    const cards = AUDIENCES.map((a) => {
      const links = a.links.map(([href, text]) =>
        `<a href="${B.esc(href)}">${B.esc(text)} →</a>`).join("");
      return `<div class="card home-audience">` +
        `<h3>${B.esc(a.title)}</h3>` +
        `<p>${B.esc(a.body)}</p>` +
        `<div class="home-audience-links">${links}</div>` +
        `</div>`;
    }).join("");
    return `<section class="section-gap">` +
      `<h2>Find what you came for</h2>` +
      `<p class="muted">Whoever you are, there's a concrete next step.</p>` +
      `<div class="cards-grid">${cards}</div>` +
      `</section>`;
  }

  // The agent-layer promotion: what it is + copy-paste access. The one-liner is
  // exactly what a person would paste into an AI assistant.
  function agentHTML() {
    const llms = `${SITE_ORIGIN}/llms.txt`;
    const apiIndex = `${SITE_ORIGIN}/api/v1/index.json`;
    const curl = `curl ${apiIndex}`;
    const oneLiner = `Read ${llms} and answer questions about Chicago cyclist ` +
      `safety, bike infrastructure, and City Council accountability, citing the data tier of each number.`;
    const copyBlock = (id, text) =>
      `<div class="agent-copy"><code id="${id}">${B.esc(text)}</code>` +
      `<button type="button" class="btn agent-copy-btn" data-copy="${id}">Copy</button></div>`;
    return `<section class="section-gap home-agent">` +
      `<h2>For AI agents & builders: the machine-readable layer</h2>` +
      `<p>Every number on this site is also a documented, versioned JSON endpoint. ` +
      `<code>llms.txt</code> is a plain-language index written for language models — it lists ` +
      `every endpoint, what each answers, and how much to trust it. No key, no sign-up, ` +
      `CORS-open, rebuilt weekly.</p>` +
      `<h3>Point an AI assistant at it</h3>` +
      `<p class="muted">Paste this into Claude, ChatGPT, or any assistant that can browse:</p>` +
      copyBlock("agent-oneliner", oneLiner) +
      `<h3>Start here</h3>` +
      copyBlock("agent-llms", llms) +
      copyBlock("agent-api", apiIndex) +
      `<h3>Or from the shell</h3>` +
      copyBlock("agent-curl", curl) +
      `<p class="home-agent-foot">Full contract, schemas, and download docs on the ` +
      `<a href="contributing.html">Downloads &amp; Docs page</a>. Every response envelope carries ` +
      `its own provenance, data tier, and license.</p>` +
      `</section>`;
  }

  function wireCopyButtons(root) {
    root.querySelectorAll(".agent-copy-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const el = document.getElementById(btn.dataset.copy);
        const text = el ? el.textContent : "";
        const done = () => { const o = btn.textContent; btn.textContent = "Copied"; setTimeout(() => { btn.textContent = o; }, 1200); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done).catch(() => {});
        } else if (el) {
          const r = document.createRange();
          r.selectNode(el);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(r);
          try { document.execCommand("copy"); done(); } catch (e) { /* noop */ }
          sel.removeAllRanges();
        }
      });
    });
  }

  async function render() {
    B.initPage("index.html");
    const app = document.getElementById("app");

    app.insertAdjacentHTML("beforeend", heroHTML());

    // Stat strip renders a placeholder immediately, then fills from live JSON.
    const statsSlot = document.createElement("div");
    statsSlot.innerHTML = `<section class="home-stats"><p class="muted">Loading headline data…</p></section>`;
    app.appendChild(statsSlot);

    app.insertAdjacentHTML("beforeend", functionsHTML());
    app.insertAdjacentHTML("beforeend", audiencesHTML());
    app.insertAdjacentHTML("beforeend", agentHTML());

    wireCopyButtons(app);

    try {
      const citywide = await B.loadJSON("api/v1/citywide.json");
      const stats = pickHeadlineStats(citywide, HEADLINE_STATS.map((h) => h.id));
      statsSlot.innerHTML = statStripHTML(stats);
    } catch (err) {
      // Never leave a broken/loading strip — fall back to the findings link.
      statsSlot.innerHTML = statStripHTML([]);
    }
  }

  render();
})();
