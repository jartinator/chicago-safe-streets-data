(function () {
  async function render() {
    BSD.initPage("findings.html");

    const app = document.getElementById("app");

    try {
      const [findings, meta, trend, bnaScores] = await Promise.all([
        BSD.loadJSON("data/findings.json"),
        BSD.loadJSON("data/meta.json"),
        BSD.loadJSON("data/citywide_trend.json").catch(() => null),
        BSD.loadJSON("data/bna_scores.json").catch(() => null),
      ]);

      // Page heading and intro
      const heading = document.createElement("div");
      heading.innerHTML = `
        <h1>What the data shows</h1>
        <p>Headline numbers and patterns worth exploring — each links to the view behind it.</p>
      `;
      app.appendChild(heading);

      // One collapsed reading guide (replaces the old directional +
      // normalization notices) in plainer voice.
      const guide = document.createElement("details");
      guide.className = "fine-print";
      guide.style.marginBottom = "1rem";
      guide.innerHTML =
        `<summary>How to read these numbers</summary>` +
        `<p>These are patterns worth investigating, not statistical proof. Counts are raw — ` +
        `busy corridors look worse than dangerous quiet ones because no public ridership ` +
        `data exists to divide by.</p>`;
      app.appendChild(guide);

      // Findings grid
      const grid = document.createElement("div");
      grid.className = "cards-grid";

      // Cards travel as screenshots in group chats and printouts — each one
      // must carry its own origin + as-of date, not rely on page context.
      const asOfShort = meta.generated_at ? String(meta.generated_at).slice(0, 10) : null;

      // The BNA score is a network-QUALITY measure, not crash data — pulling
      // it out of the crash-findings grid and into its own labeled section
      // pre-empts the "score = safety" / "more lanes -> more crashes" misread.
      let bnaFinding = null;

      for (const finding of findings) {
        if (finding.id === "bna-score") {
          bnaFinding = finding;
          continue;
        }

        const card = document.createElement("div");
        card.className = "card";

        // Build the explore link URL
        let exploreUrl;
        if (finding.map_state.screen === "table") {
          exploreUrl = "table.html";
        } else {
          // screen === "map"
          const params = new URLSearchParams();

          if (finding.map_state.layers && finding.map_state.layers.length > 0) {
            params.set("layers", finding.map_state.layers.join(","));
          }

          if (finding.map_state.ward) {
            params.set("ward", finding.map_state.ward);
          }

          if (finding.map_state.corridor) {
            params.set("corridor", finding.map_state.corridor);
          }

          if (finding.map_state.filters && finding.map_state.filters.dooring) {
            params.set("dooring", "1");
          }

          const queryString = params.toString();
          exploreUrl = "map.html" + (queryString ? "?" + queryString : "");
        }

        // Title with badge
        const titleWithBadge = document.createElement("h3");
        titleWithBadge.style.marginBottom = "0.4rem";
        titleWithBadge.innerHTML = `${BSD.esc(finding.title)} ${BSD.badgeHTML(finding.data_tier)}`;

        // Stat
        const stat = document.createElement("div");
        stat.className = "stat";
        stat.textContent = finding.stat;

        // KSI finding gets the citywide trailing-12-month trend chart between
        // stat and description; skipped silently when trend data is absent.
        let chart = null;
        if (finding.id === "ksi-trend" && trend && Array.isArray(trend.months)) {
          const points = BSD.rollingSums(trend.months, "ksi", 12);
          const svg = BSD.trendChartSVG(points, {
            label: "Cyclists killed or seriously injured, trailing 12 months",
            width: 560,
            height: 140,
          });
          if (svg) {
            chart = document.createElement("div");
            chart.innerHTML = svg;
          }
        }

        // Description
        const desc = document.createElement("p");
        desc.textContent = finding.description;

        // Caveat
        const caveat = document.createElement("p");
        caveat.className = "muted";
        caveat.style.fontSize = "0.86rem";
        caveat.textContent = finding.caveat;

        // Per-ward report links (ward-concentration carries a `wards` array;
        // older data files without it just skip this line).
        let wardLinks = null;
        if (Array.isArray(finding.wards) && finding.wards.length) {
          wardLinks = document.createElement("p");
          wardLinks.style.fontSize = "0.86rem";
          wardLinks.innerHTML = finding.wards.map(w =>
            `<a href="action.html?ward=${encodeURIComponent(w)}">Ward ${BSD.esc(w)} report →</a>`
          ).join(" · ");
        }

        // Explore button
        const btn = document.createElement("a");
        btn.href = exploreUrl;
        btn.className = "btn primary";
        btn.style.display = "inline-block";
        // The protected-share story IS the main-routes report card — say so.
        btn.textContent = finding.id === "protected-share"
          ? "See the main routes →"
          : "Explore on map →";

        // Screenshot-survivable provenance line
        let provLine = null;
        if (asOfShort) {
          provLine = document.createElement("p");
          provLine.className = "muted prov-line";
          provLine.textContent = `On Your Left! · data as of ${asOfShort}`;
        }

        // Assemble card
        card.appendChild(stat);
        card.appendChild(titleWithBadge);
        if (chart) card.appendChild(chart);
        card.appendChild(desc);
        card.appendChild(caveat);
        if (wardLinks) card.appendChild(wardLinks);
        card.appendChild(btn);
        if (provLine) card.appendChild(provLine);

        grid.appendChild(card);
      }

      app.appendChild(grid);

      // BNA score gets its own visually separated section, clearly labeled
      // as network quality rather than crash data — see reconciliation
      // sentence below. Rendered only if the finding is present; older
      // findings.json files without it just skip this whole block.
      if (bnaFinding) {
        const bnaSection = document.createElement("section");
        bnaSection.style.marginTop = "2.5rem";
        bnaSection.style.paddingTop = "1.5rem";
        bnaSection.style.paddingLeft = "1.25rem";
        bnaSection.style.paddingRight = "1.25rem";
        bnaSection.style.paddingBottom = "1.5rem";
        bnaSection.style.borderTop = "3px solid var(--line)";
        bnaSection.style.background = "var(--panel-alt, rgba(127, 127, 127, 0.06))";
        bnaSection.style.borderRadius = "8px";

        const bnaHeading = document.createElement("h2");
        bnaHeading.style.marginTop = "0";
        bnaHeading.textContent = "Network quality — not crash data";
        bnaSection.appendChild(bnaHeading);

        const reconciliation = document.createElement("p");
        reconciliation.style.fontWeight = "600";
        reconciliation.style.marginBottom = "1rem";
        reconciliation.textContent =
          "A growing bike network and rising raw crash counts can both be true at once when more " +
          "people ride — this score measures what's built, not what happened, and moves " +
          "independently of any crash trend.";
        bnaSection.appendChild(reconciliation);

        const bnaCard = document.createElement("div");
        bnaCard.className = "card";

        const bnaTitleWithBadge = document.createElement("h3");
        bnaTitleWithBadge.style.marginBottom = "0.4rem";
        bnaTitleWithBadge.innerHTML = `${BSD.esc(bnaFinding.title)} ${BSD.badgeHTML(bnaFinding.data_tier)}`;

        const bnaStat = document.createElement("div");
        bnaStat.className = "stat";
        bnaStat.textContent = bnaFinding.stat;

        // Version + as-of date on the card face, loaded from bna_scores.json.
        // Falls back to parsing the finding's own caveat text if that file
        // failed to load, so the card still renders standalone.
        let bnaVersion = bnaScores && bnaScores.version ? bnaScores.version : null;
        let bnaAsOf = bnaScores && bnaScores.as_of ? bnaScores.as_of : null;
        if (!bnaVersion || !bnaAsOf) {
          const match = /analysis\s+([\d.]+)\s*\(([^)]+)\)/i.exec(bnaFinding.caveat || "");
          if (match) {
            if (!bnaVersion) bnaVersion = match[1];
            if (!bnaAsOf) bnaAsOf = match[2];
          }
        }
        const bnaVersionLine = document.createElement("p");
        bnaVersionLine.className = "muted";
        bnaVersionLine.style.fontSize = "0.86rem";
        bnaVersionLine.textContent = bnaVersion
          ? `PeopleForBikes BNA analysis ${bnaVersion}${bnaAsOf ? " · as of " + bnaAsOf : ""}`
          : "PeopleForBikes Bicycle Network Analysis";

        const bnaDesc = document.createElement("p");
        bnaDesc.textContent = bnaFinding.description;

        const bnaCaveat = document.createElement("p");
        bnaCaveat.className = "muted";
        bnaCaveat.style.fontSize = "0.86rem";
        bnaCaveat.textContent = bnaFinding.caveat;

        const bnaExploreUrl = (() => {
          if (bnaFinding.map_state.screen === "table") return "table.html";
          const params = new URLSearchParams();
          if (bnaFinding.map_state.layers && bnaFinding.map_state.layers.length > 0) {
            params.set("layers", bnaFinding.map_state.layers.join(","));
          }
          if (bnaFinding.map_state.ward) params.set("ward", bnaFinding.map_state.ward);
          if (bnaFinding.map_state.corridor) params.set("corridor", bnaFinding.map_state.corridor);
          if (bnaFinding.map_state.filters && bnaFinding.map_state.filters.dooring) {
            params.set("dooring", "1");
          }
          const queryString = params.toString();
          return "map.html" + (queryString ? "?" + queryString : "");
        })();

        const bnaBtn = document.createElement("a");
        bnaBtn.href = bnaExploreUrl;
        bnaBtn.className = "btn primary";
        bnaBtn.style.display = "inline-block";
        bnaBtn.textContent = "Explore on map →";

        let bnaProvLine = null;
        if (asOfShort) {
          bnaProvLine = document.createElement("p");
          bnaProvLine.className = "muted prov-line";
          bnaProvLine.textContent = `On Your Left! · data as of ${asOfShort}`;
        }

        bnaCard.appendChild(bnaStat);
        bnaCard.appendChild(bnaTitleWithBadge);
        bnaCard.appendChild(bnaVersionLine);
        bnaCard.appendChild(bnaDesc);
        bnaCard.appendChild(bnaCaveat);
        bnaCard.appendChild(bnaBtn);
        if (bnaProvLine) bnaCard.appendChild(bnaProvLine);

        bnaSection.appendChild(bnaCard);
        app.appendChild(bnaSection);
      }

      // Footer with meta info
      const footer = document.createElement("div");
      footer.style.marginTop = "2rem";
      footer.style.paddingTop = "1rem";
      footer.style.borderTop = "1px solid var(--line)";
      footer.style.fontSize = "0.8rem";
      footer.style.color = "var(--ink-soft)";

      const date = new Date(meta.generated_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });

      let footerHTML = `<p>Data generated ${BSD.esc(date)}, contract v${BSD.esc(meta.contract_version)}.</p>`;
      footerHTML += "<p><strong>Sources:</strong> ";

      const sourceLines = meta.sources.map(src => {
        const records = src.records !== null ? ` (${BSD.fmt(src.records)} records)` : "";
        return `${BSD.esc(src.name)}${records} ${BSD.badgeHTML(src.tier)}`;
      });

      footerHTML += sourceLines.join(" • ");
      footerHTML += "</p>";

      footer.innerHTML = footerHTML;
      app.appendChild(footer);
    } catch (err) {
      const notice = document.createElement("div");
      notice.className = "notice";
      notice.textContent = "Error loading findings: " + BSD.esc(err.message);
      app.appendChild(notice);
    }
  }

  render();
})();
