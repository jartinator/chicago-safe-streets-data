/* Printable ward one-pager (ward.html?ward=N&register=brief|plain).
 * Two registers for the same numbers (REPORT-ux-proposal.md P3):
 *  - "brief":  advocate/ward-office framing (KSI vocabulary, terse labels) —
 *              the leave-behind for a meeting or a Monday briefing;
 *  - "plain":  ~6th-8th grade reading level, no jargon, ends with ONE
 *              suggested action (research: jargon reads as "not for me";
 *              fear without an action loses residents).
 * Print CSS keeps it to one page; every number carries as-of + tier, and the
 * page identifies itself when photocopied (P4: provenance travels). */
(function () {
  const B = window.BSD;
  const W = window.BSDWard;
  B.initPage("ward.html");
  const app = document.getElementById("app");

  const params = B.qs();
  const ward = params.get("ward") || "";
  let register = params.get("register") === "plain" ? "plain" : "brief";

  const MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function fmtDate(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(iso || ""));
    if (!m) return String(iso || "—");
    return `${MONTH_ABBR[Number(m[2]) - 1]} ${Number(m[3])}, ${m[1]}`;
  }

  // Normalize "03"/"007" -> "3": all data files key wards as unpadded
  // strings, and a strict-match miss would render a plausible-looking
  // all-"no data" printout for a ward that has data.
  const wardNorm = /^\d+$/.test(ward) ? String(Number(ward)) : ward;
  if (!wardNorm || !/^\d+$/.test(wardNorm) || Number(wardNorm) < 1 || Number(wardNorm) > 50) {
    const chipList = `<p class="chip-toc">${Array.from({ length: 50 }, (_, i) =>
      `<a href="ward.html?ward=${i + 1}">Ward ${i + 1}</a>`).join("")}</p>`;
    app.innerHTML = `<h1>Ward one-pager</h1>
      <p>Know your alderperson's name but not your ward number? Type it below:</p>
      <p><input type="text" id="aldLookup" placeholder="Type your alderperson's name"
        class="op-plain" style="width:100%;max-width:24rem;padding:.4rem;box-sizing:border-box;"
        autocomplete="off"></p>
      <div id="aldResults" class="fine-print"></div>
      <p>Or pick a ward to build a printable one-page report:</p>
      ${chipList}`;
    // Self-locating resolver (P7): no offline geocoder or community-area
    // crosswalk exists in this repo, so the sanctioned fallback is a
    // client-side, dependency-free alderman-name filter over aldermen.json.
    // Degrades gracefully — the ward-chip list above always works even if
    // this fetch fails.
    B.loadJSON("data/aldermen.json").then(data => {
      const input = document.getElementById("aldLookup");
      const results = document.getElementById("aldResults");
      const wards = (data && data.wards) || [];
      input.addEventListener("input", () => {
        const q = input.value.trim().toLowerCase();
        if (!q) { results.innerHTML = ""; return; }
        const matches = wards.filter(w => w.alderman && w.alderman.toLowerCase().includes(q));
        results.innerHTML = matches.length
          ? `<p class="chip-toc">${matches.map(w =>
              `<a href="ward.html?ward=${B.esc(w.ward)}">Ward ${B.esc(w.ward)} — ${B.esc(w.alderman)}</a>`).join("")}</p>`
          : `<p class="muted">no match — browse all wards below</p>`;
      });
    }).catch(() => {
      // No aldermen data this run: input stays inert, chips remain the
      // fallback path.
    });
    return;
  }

  Promise.all([
    B.loadJSON("data/ward_safety_index.json").catch(() => null),
    B.loadJSON("data/aldermen.json").catch(() => null),
    B.loadJSON("data/wards.geojson").catch(() => null),
    B.loadJSON("data/bike_routes.geojson").catch(() => null),
    B.loadJSON("data/hearings.json").catch(() => null),
    B.loadJSON("data/menu_spending.json").catch(() => null),
    B.loadJSON("data/meta.json").catch(() => null),
    B.loadJSON("data/news_items.json").catch(() => null),
    B.loadJSON("data/divvy_ward_exposure.json").catch(() => null),
  ]).then(([safetyIndexData, aldermenData, wardsData, routesData, hearingsData, menuData, metaData, newsData, divvyData]) => {
    const today = new Date().toISOString().slice(0, 10);
    const o = W.buildOnePager(
      { safetyIndexData, aldermenData, wardsData, routesData, hearingsData, menuData, metaData, newsData, divvyData },
      wardNorm, today);
    render(o);
  }).catch(err => {
    app.innerHTML = `<div class="notice">Failed to load data: ${B.esc(err.message)}</div>`;
  });

  function kv(label, valueHTML, tier) {
    return `<div class="op-row"><span class="op-label">${B.esc(label)}${tier ? " " + B.badgeHTML(tier) : ""}</span>` +
      `<span class="op-value">${valueHTML}</span></div>`;
  }
  const noData = `<span class="muted">no data this run</span>`;
  // One correction destination, on purpose (critique round-2 §3.5/§7.5) —
  // methodology.js's corrections link points at the same URL.
  const DIVVY_ISSUES_URL = "https://github.com/jartinator/chicago-safe-streets-data/issues/new";
  const DIVVY_ATTRIBUTION = "On Your Left!, from Lyft's public Divvy trip export";
  function divvyFinePrint() {
    return `<div class="fine-print">${DIVVY_ATTRIBUTION} — ` +
      `<a href="${DIVVY_ISSUES_URL}" target="_blank" rel="noopener">something look wrong? tell us →</a></div>`;
  }
  function divvyStaleNotice(o) {
    return `<div class="notice">This ward's Divvy count is from ${W.fmtMonth(o.divvy.asOf)} — more than ` +
      `${W.STALE_THRESHOLD_MONTHS} months behind this page's own data refresh. The weekly Divvy pull may ` +
      `be stuck; treat this number as extra stale until it updates.</div>`;
  }
  // Brief-register kv row for the Divvy trip-volume proxy (states A/B/C; E is
  // appended separately since it's a flag, not a branch — 03-experience.md §5).
  function divvyBriefRow(o) {
    if (!o.divvy) {
      // State C: no file, fetch failed, or status !== "ok" — explicit empty
      // state reusing the page's own shipped idiom (critique round-2 §3.6),
      // not a new phrase.
      return kv("Divvy trips originating here", noData, "proxy");
    }
    if (!o.divvy.hasCoverage) {
      // State B, softened per critique round-2 §4/§7.3: absence in wards[]
      // can mean no stations OR unlocatable stations — never assert the
      // physical fact "no stations here" from a missing JSON row.
      return kv("Divvy trips originating here", `
        <span class="muted">No Divvy stations are recorded in this ward for ${W.fmtMonth(o.divvy.asOf)} —
        this reflects station coverage in the data, not zero cycling. A low or absent count here means
        fewer nearby stations, not necessarily less riding. Never a rate: not divided by, or dividing,
        crash counts.</span>
        ${divvyFinePrint()}
      `, "proxy");
    }
    const divvy = W.roundForDisplay(o.divvy.tripCount);
    const restated = divvy.approx ? `${B.fmt(o.divvy.tripCount)} exactly, ` : "";
    return kv("Divvy trips originating here", `
      <strong>${divvy.display}</strong>
      <br><span class="muted">${restated}${W.fmtMonth(o.divvy.asOf)} — Divvy bikeshare only, a floor on
      cycling, not a full count. Station placement skews downtown/North Side, so a low count can mean
      fewer stations, not less riding. Never a rate: not divided by, or dividing, crash counts.</span>
      ${divvyFinePrint()}
    `, "proxy");
  }
  // Two visual bands so three uncertain numbers (safety index, menu money,
  // legislative record) never read as one certain verdict alongside the two
  // directly-counted numbers (crashes, bikeway mileage). Plain inline style
  // mirrors the existing "Media coverage" divider below — border-top +
  // bold survives print (no color/background dependency).
  function sectionLabel(text, note) {
    return `<div class="op-section-label" style="margin-top:.75rem;padding-top:.4rem;border-top:1px solid currentColor;font-weight:bold;">${B.esc(text)}${note ? ` <span class="muted" style="font-weight:normal;">${note}</span>` : ""}</div>`;
  }
  // Committee-vs-floor caveat (P3): council_records.json carries only
  // sponsorship + workflow status (Introduced/Passed/Adopted/Failed to
  // Pass/Substituted/Placed on File) — never a recorded floor vote, and
  // never a committee-vs-floor split. Most measures pass by voice vote.
  // State this plainly wherever legislative/sponsorship data shows up —
  // silence here reads as false certainty, not honest absence.
  const COMMITTEE_VS_FLOOR_BRIEF =
    `<span class="muted">Record shows sponsorship &amp; final status only — committee action vs. floor vote is not distinguished in the source, and most measures pass by voice vote (no recorded roll call).</span>`;
  const COMMITTEE_VS_FLOOR_PLAIN =
    `The city's public record shows who sponsored a proposal and whether it eventually passed — it doesn't separately record what happened in committee versus a final floor vote. Most things pass on a voice vote, with no one's name attached to a "yes" or "no."`;

  function briefBody(o) {
    const r = o.windows && o.windows.recent, p = o.windows && o.windows.prior;
    let html = "";
    html += sectionLabel("Measured", "— directly counted, not modeled");
    html += kv("Cyclist crashes (12 mo)", r
      ? `<strong class="op-big">${B.fmt(r.crashes)}</strong> <span class="muted">vs ${B.fmt(p ? p.crashes : null)} prior 12 mo</span>`
      : noData, "real");
    html += kv("KSI — killed or seriously injured (12 mo)", r
      ? `<strong>${B.fmt(r.ksi)}</strong> <span class="muted">(${B.fmt(r.fatal)} deaths) vs ${B.fmt(p ? p.ksi : null)} prior</span>`
      : noData, "real");
    if (o.totalSince2017 != null) {
      html += kv("Total crashes since Sept 2017", `${B.fmt(o.totalSince2017)}`, "real");
    }
    html += kv("% of bikeway miles protected", o.pctProtected != null
      ? `<strong>${B.esc(String(o.pctProtected))}%</strong> <span class="muted">of ${B.fmt(o.bikewayMiles)} bikeway mi</span>` : noData, "real");
    html += kv("% of streets with any bike infrastructure", o.pctRoads != null
      ? `<strong>${B.esc(String(o.pctRoads))}%</strong>` : noData, "real");
    if (o.topCorridors.length) {
      html += kv("Top corridors in/near this ward", o.topCorridors.map(c =>
        `${B.esc(c.street)} <span class="muted">(${B.fmt(c.crashes)} crashes near bikeway)</span>`).join("<br>"), "real");
    }
    html += sectionLabel("Derived & proxy", "— modeled, estimated, or third-party — read alongside Measured, not as one verdict");
    html += kv("Concern rank", o.concern
      ? `${B.fmt(o.concern.score)} / 100 — rank ${o.concern.rank} of ${o.concern.total} <span class="muted">(relative, higher = worse — <a href="methodology.html#ward-index">methodology</a>)</span>`
      : noData, "derived");
    html += divvyBriefRow(o);
    if (o.divvy && o.divvy.isStale) html += divvyStaleNotice(o);
    html += kv("Menu-money on bike/traffic-calming", o.menuBikeSpent != null
      ? `${B.money(o.menuBikeSpent)} <span class="muted">of ${B.money(o.menuTotalSpent)} total — source: ` +
        `<a href="https://www.wardwisechicago.org" target="_blank" rel="noopener">Ward Wise</a> (Chi Hack Night volunteer ` +
        `project), an unverified extract — cross-check against the ward office before citing</span>`
      : noData, "proxy");
    if (o.nextMeeting) {
      // Up to two agenda highlights (this ward's items first, then safety
      // matches) — verbatim official titles, see BSD.agendaHighlights.
      const highlights = B.agendaHighlights(o.nextMeeting, o.ward, 2).map(h => {
        const label = h.url
          ? `<a href="${B.esc(h.url)}" target="_blank" rel="noopener">${B.esc(h.label)}</a>`
          : B.esc(h.label);
        return `<div class="fine-print">${h.forWard ? `<strong>Ward ${B.esc(h.ward)}</strong> · ` : ""}${label}</div>`;
      }).join("");
      html += kv("Next committee hearing",
        `${B.esc(fmtDate(o.nextMeeting.date))} — ${B.esc(String(o.nextMeeting.committee).replace(/^Committee on /, ""))}` +
        (o.nextMeeting.comment ? `<div class="fine-print">${B.esc(o.nextMeeting.comment)}</div>` : "") +
        highlights +
        `<div class="fine-print">${COMMITTEE_VS_FLOOR_BRIEF}</div>`, "real");
    } else {
      html += kv("Next committee hearing",
        `<span class="muted">nothing scheduled — <a href="https://chicityclerkelms.chicago.gov/Meetings" target="_blank" rel="noopener">official calendar</a></span>` +
        `<div class="fine-print">${COMMITTEE_VS_FLOOR_BRIEF}</div>`, "real");
    }
    // "In the news" (brief register only — the print one-pager's audience).
    // Outlet always named (coverage ≠ endorsement); explicit empty state so
    // no-coverage never reads as all-quiet (validation study 2026-07-13).
    // P2: media coverage sits in its own labeled section so a reader never
    // reads news volume as a safety number — the divider must survive print.
    html += `<div class="op-section-label" style="margin-top:.75rem;padding-top:.4rem;border-top:1px solid currentColor;font-weight:bold;">Media coverage (not a safety measure)</div>`;
    html += kv("In the news (90 days)", o.news.length
      ? o.news.slice(0, 3).map(n =>
          `${B.esc(fmtDate(n.published))} · <span class="muted">${B.esc(n.source || "unknown outlet")}</span> · ` +
          `<a href="${B.esc(n.url)}" target="_blank" rel="noopener">${B.esc(n.title)}</a>`).join("<br>")
      : `<span class="muted">no coverage found for this ward — outlets cover some neighborhoods more than others</span>`,
      "real");
    return html;
  }

  // Plain-register paragraph(s) for the Divvy trip-volume proxy — states
  // A/B/C, plus E appended separately (03-experience.md §6.2, §5).
  function divvyPlainParagraphs(o) {
    if (!o.divvy) {
      return `<p class="op-plain muted">We don't have Divvy bike-share numbers for this ward yet in the current data.</p>`;
    }
    let html;
    if (!o.divvy.hasCoverage) {
      // Softened per critique round-2 §4/§7.3 — reports the record, not the
      // physical fact the record can't establish.
      html = `<p class="op-plain">Divvy's data shows no bike-share stations in Ward ${B.esc(o.ward)} for
        ${W.fmtMonth(o.divvy.asOf)}, so there's no trip count to show. That doesn't mean nobody bikes here.
        <span class="muted">If this looks wrong, or doesn't match something an AI assistant told you,
        <a href="${DIVVY_ISSUES_URL}" target="_blank" rel="noopener">tell the project on GitHub</a> —
        source: ${DIVVY_ATTRIBUTION}.</span></p>`;
    } else {
      const divvy = W.roundForDisplay(o.divvy.tripCount);
      const restated = divvy.approx ? ` (${B.fmt(o.divvy.tripCount)} exactly)` : "";
      html = `<p class="op-plain">Divvy — Chicago's bike-share system — recorded ${divvy.display} rides
        starting in Ward ${B.esc(o.ward)} in ${W.fmtMonth(o.divvy.asOf)}${restated}. That's not the full
        picture of biking here: it only counts Divvy's rental bikes, not people on their own bikes, and
        Divvy has more stations downtown and on the North Side. A low number here can mean fewer nearby
        stations, not fewer people biking. <strong>This number is never used to work out a safety
        rate</strong> — it's shown for background next to the crash count above, not as a way to measure
        risk. <span class="muted">If this looks wrong, or doesn't match something an AI assistant told you,
        <a href="${DIVVY_ISSUES_URL}" target="_blank" rel="noopener">tell the project on GitHub</a> —
        source: ${DIVVY_ATTRIBUTION}.</span></p>`;
    }
    if (o.divvy && o.divvy.isStale) {
      html += `<p class="op-plain muted">Note: this Divvy number hasn't updated in a while — it's from
        ${W.fmtMonth(o.divvy.asOf)}, older than the rest of this page. Treat it as extra out of date until
        it refreshes.</p>`;
    }
    return html;
  }

  function plainBody(o) {
    const r = o.windows && o.windows.recent, p = o.windows && o.windows.prior;
    let html = "";
    html += sectionLabel("What we actually counted");
    if (r) {
      const dir = p && p.crashes != null && r.crashes != null
        ? (r.crashes > p.crashes ? "That is more than the year before" :
           r.crashes < p.crashes ? "That is fewer than the year before" : "About the same as the year before")
        : "";
      html += `<p class="op-plain"><strong class="op-big">${B.fmt(r.crashes)}</strong> people crashed while
        biking in Ward ${B.esc(o.ward)} in the last 12 months. ${B.esc(dir)}${dir ? ` (${B.fmt(p.crashes)}).` : ""}
        ${B.fmt(r.ksi)} were killed or badly hurt.</p>`;
    } else {
      html += `<p class="op-plain">We don't have crash numbers for this ward in the current data.</p>`;
    }
    if (o.pctProtected != null || o.pctRoads != null) {
      html += `<p class="op-plain">`;
      if (o.pctRoads != null) {
        html += `Only <strong>${B.esc(String(o.pctRoads))}%</strong> of this ward's streets have any
          bike lane or path at all. `;
      }
      if (o.pctProtected != null) {
        html += `Of the bike lanes that exist, <strong>${B.esc(String(o.pctProtected))}%</strong> have real
          physical protection — the rest is mostly paint, and paint doesn't stop cars.`;
      }
      html += `</p>`;
    }
    if (o.topCorridors.length) {
      html += `<p class="op-plain">The streets with the most bike crashes around here:
        <strong>${o.topCorridors.map(c => B.esc(c.street)).join(", ")}</strong>.</p>`;
    }
    // Header triggers on Divvy or menu-money (implementation note,
    // 03-experience.md §6.2) — Divvy always contributes content (explicit
    // states A/B/C/E), so this section is no longer gated on menu-money alone.
    html += sectionLabel("Estimates & other sources", "— not directly counted by us, read with care");
    html += divvyPlainParagraphs(o);
    if (o.menuBikeSpent != null) {
      html += `<p class="op-plain">Every ward gets about $1.5 million a year to spend on streets
        ("menu money"). ${o.alderman ? `Your alderperson` : `This ward's office`} has put
        <strong>${B.money(o.menuBikeSpent)}</strong> of it toward bike safety and traffic calming, out of
        ${B.money(o.menuTotalSpent)} spent overall. <span class="muted">Source:
        <a href="https://www.wardwisechicago.org" target="_blank" rel="noopener">Ward Wise</a>, a volunteer
        project by Chi Hack Night — this number hasn't been double-checked against city paperwork yet, so
        cross-check it before you cite it.</span></p>`;
    }
    // ONE suggested action — the plain register never ends on fear.
    const subject = encodeURIComponent(`Bike safety in Ward ${o.ward}`);
    const action = o.alderman && o.alderman.email
      ? `<a class="btn primary" href="mailto:${B.esc(o.alderman.email)}?subject=${subject}">Email ${B.esc(o.alderman.name)}</a>
         <span class="muted">One email from a resident gets read. Attach this page.</span>`
      : `<a class="btn primary" href="${B.esc(B.LINKS.aldermanLookup)}" target="_blank" rel="noopener">Find your alderperson</a>`;
    html += `<div class="op-action"><strong>One thing you can do:</strong><br>${action}</div>`;
    if (o.nextMeeting) {
      const wardItems = B.agendaHighlights(o.nextMeeting, o.ward, 0).filter(h => h.forWard);
      const wardNote = wardItems.length
        ? ` ${wardItems.length === 1 ? "One item on its agenda is" : `${B.fmt(wardItems.length)} items on its agenda are`}
           specifically about Ward ${B.esc(o.ward)}.`
        : "";
      html += `<p class="op-plain muted">City Council's next street-safety meeting:
        ${B.esc(fmtDate(o.nextMeeting.date))} (${B.esc(String(o.nextMeeting.committee).replace(/^Committee on /, ""))}).${wardNote}
        Anyone can send a written comment.</p>`;
      html += `<p class="op-plain muted">${COMMITTEE_VS_FLOOR_PLAIN}</p>`;
    }
    return html;
  }

  function render(o) {
    const aldLine = o.alderman
      ? `${B.esc(o.alderman.name)}${o.alderman.email ? ` · ${B.esc(o.alderman.email)}` : ""}${o.alderman.phone ? ` · ${B.esc(o.alderman.phone)}` : ""}`
      : `<a href="${B.esc(B.LINKS.aldermanLookup)}" target="_blank" rel="noopener">find your alderperson</a>`;

    app.innerHTML = `
      <div class="no-print op-toolbar">
        <a class="btn" href="ward.html">All wards</a>
        <span class="op-switch">
          <button class="btn ${register === "brief" ? "primary" : ""}" data-reg="brief">Brief</button>
          <button class="btn ${register === "plain" ? "primary" : ""}" data-reg="plain">Plain language</button>
        </span>
        <button class="btn primary" id="printBtn">Print / save PDF</button>
      </div>
      <article class="onepager card">
        <header class="op-head">
          <div>
            <span class="report-kicker">${register === "plain" ? "Your ward's bike safety, on one page" : "Ward one-pager — bike safety"}</span>
            <h1 class="op-title">Ward ${B.esc(o.ward)}</h1>
            <div class="muted">Alderperson: ${aldLine}</div>
          </div>
          <div class="op-brand">On Your Left!<br><span class="muted">chicago bike safety, on the record</span></div>
        </header>
        ${register === "plain" ? plainBody(o) : briefBody(o)}
        <footer class="op-foot">
          On Your Left! · data as of ${B.esc(o.asOf || "unknown")} · crash records: Chicago Data Portal
          (recent months provisional; dooring undercounted) · counts are raw, not ridership-normalized —
          the Divvy trip count on this page, where shown, is not a ridership denominator and no rate is
          computed from the two ·
          concern rank is a relative comparison across wards, not an absolute risk grade ·
          Divvy trip counts: ${DIVVY_ATTRIBUTION} (proxy tier, station-coverage biased — not a cycling
          exposure measure) ·
          menu-money is an unverified <a href="https://www.wardwisechicago.org" target="_blank" rel="noopener">Ward Wise</a>
          extract (Chi Hack Night volunteer project), cross-check before citing ·
          sponsorships ≠ votes — the record shows sponsorship &amp; final status only, not committee vs. floor action,
          and most measures pass by voice vote (no recorded roll call) ·
          methodology &amp; caveats: the Methods page on this site
        </footer>
      </article>`;

    document.getElementById("printBtn").addEventListener("click", () => window.print());
    app.querySelectorAll("[data-reg]").forEach(btn => btn.addEventListener("click", () => {
      register = btn.dataset.reg;
      B.setParams({ ward: o.ward, register });
      render(o);
    }));
  }
})();
