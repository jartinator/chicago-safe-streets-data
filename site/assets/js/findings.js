(function () {
  async function render() {
    BSD.initPage("findings.html");

    const app = document.getElementById("app");

    try {
      const [findings, meta] = await Promise.all([
        BSD.loadJSON("data/findings.json"),
        BSD.loadJSON("data/meta.json"),
      ]);

      // Page heading and intro
      const heading = document.createElement("div");
      heading.innerHTML = `
        <h1>Dashboard: Top-Level Findings</h1>
        <p>Headline numbers and patterns worth exploring. Each finding links directly to the relevant map view — click to dig in.</p>
      `;
      app.appendChild(heading);

      // Notices
      const noticeContainer = document.createElement("div");
      noticeContainer.innerHTML = BSD.noticeHTML("directional") + BSD.noticeHTML("normalization");
      app.appendChild(noticeContainer);

      // Findings grid
      const grid = document.createElement("div");
      grid.className = "cards-grid";

      for (const finding of findings) {
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
          exploreUrl = "index.html" + (queryString ? "?" + queryString : "");
        }

        // Title with badge
        const titleWithBadge = document.createElement("h3");
        titleWithBadge.style.marginBottom = "0.4rem";
        titleWithBadge.innerHTML = `${BSD.esc(finding.title)} ${BSD.badgeHTML(finding.data_tier)}`;

        // Stat
        const stat = document.createElement("div");
        stat.className = "stat";
        stat.textContent = finding.stat;

        // Description
        const desc = document.createElement("p");
        desc.textContent = finding.description;

        // Caveat
        const caveat = document.createElement("p");
        caveat.className = "muted";
        caveat.style.fontSize = "0.86rem";
        caveat.textContent = finding.caveat;

        // Explore button
        const btn = document.createElement("a");
        btn.href = exploreUrl;
        btn.className = "btn primary";
        btn.style.display = "inline-block";
        btn.textContent = "Explore on map →";

        // Assemble card
        card.appendChild(stat);
        card.appendChild(titleWithBadge);
        card.appendChild(desc);
        card.appendChild(caveat);
        card.appendChild(btn);

        grid.appendChild(card);
      }

      app.appendChild(grid);

      // Footer with meta info
      const footer = document.createElement("div");
      footer.style.marginTop = "2rem";
      footer.style.paddingTop = "1rem";
      footer.style.borderTop = "1px solid #dde4ec";
      footer.style.fontSize = "0.8rem";
      footer.style.color = "#4a5568";

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
