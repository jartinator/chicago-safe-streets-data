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
    app.innerHTML = `<h1>Ward one-pager</h1>
      <p>Pick a ward to build a printable one-page report:</p>
      <p class="chip-toc">${Array.from({ length: 50 }, (_, i) =>
        `<a href="ward.html?ward=${i + 1}">Ward ${i + 1}</a>`).join("")}</p>`;
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
  ]).then(([safetyIndexData, aldermenData, wardsData, routesData, hearingsData, menuData, metaData, newsData]) => {
    const today = new Date().toISOString().slice(0, 10);
    const o = W.buildOnePager(
      { safetyIndexData, aldermenData, wardsData, routesData, hearingsData, menuData, metaData, newsData },
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

  function briefBody(o) {
    const r = o.windows && o.windows.recent, p = o.windows && o.windows.prior;
    let html = "";
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
    html += kv("Concern rank", o.concern
      ? `${B.fmt(o.concern.score)} / 100 — rank ${o.concern.rank} of ${o.concern.total} <span class="muted">(relative, higher = worse — <a href="methodology.html#ward-index">methodology</a>)</span>`
      : noData, "derived");
    if (o.topCorridors.length) {
      html += kv("Top corridors in/near this ward", o.topCorridors.map(c =>
        `${B.esc(c.street)} <span class="muted">(${B.fmt(c.crashes)} crashes near bikeway)</span>`).join("<br>"), "real");
    }
    html += kv("Menu-money on bike/traffic-calming", o.menuBikeSpent != null
      ? `${B.money(o.menuBikeSpent)} <span class="muted">of ${B.money(o.menuTotalSpent)} total — unverified extract, cross-check before citing</span>`
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
        highlights, "real");
    } else {
      html += kv("Next committee hearing",
        `<span class="muted">nothing scheduled — <a href="https://chicityclerkelms.chicago.gov/Meetings" target="_blank" rel="noopener">official calendar</a></span>`, "real");
    }
    // "In the news" (brief register only — the print one-pager's audience).
    // Outlet always named (coverage ≠ endorsement); explicit empty state so
    // no-coverage never reads as all-quiet (validation study 2026-07-13).
    html += kv("In the news (90 days)", o.news.length
      ? o.news.slice(0, 3).map(n =>
          `${B.esc(fmtDate(n.published))} · <span class="muted">${B.esc(n.source || "unknown outlet")}</span> · ` +
          `<a href="${B.esc(n.url)}" target="_blank" rel="noopener">${B.esc(n.title)}</a>`).join("<br>")
      : `<span class="muted">no coverage found for this ward — outlets cover some neighborhoods more than others</span>`,
      "real");
    return html;
  }

  function plainBody(o) {
    const r = o.windows && o.windows.recent, p = o.windows && o.windows.prior;
    let html = "";
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
    if (o.menuBikeSpent != null) {
      html += `<p class="op-plain">Every ward gets about $1.5 million a year to spend on streets
        ("menu money"). ${o.alderman ? `Your alderperson` : `This ward's office`} has put
        <strong>${B.money(o.menuBikeSpent)}</strong> of it toward bike safety and traffic calming, out of
        ${B.money(o.menuTotalSpent)} spent overall. <span class="muted">(This number comes from a volunteer
        project and hasn't been double-checked against city paperwork yet.)</span></p>`;
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
          (recent months provisional; dooring undercounted) · counts are raw, not ridership-normalized ·
          sponsorships ≠ votes · methodology &amp; caveats: the Methods page on this site
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
