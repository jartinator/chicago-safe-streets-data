(function () {
  let wardsData = null;
  let aldemenData = null;
  let corridorsData = null;
  let ward311Data = null;
  let isLoading = false;

  async function loadAllData() {
    try {
      [wardsData, aldemenData, corridorsData, ward311Data] = await Promise.all([
        BSD.loadJSON("data/wards.geojson"),
        BSD.loadJSON("data/aldermen.json"),
        BSD.loadJSON("data/corridors.json"),
        BSD.loadJSON("data/ward_311.json")
      ]);
    } catch (err) {
      throw new Error(`Failed to load data: ${err.message}`);
    }
  }

  function findWorstCorridor() {
    if (!corridorsData || corridorsData.length === 0) return null;
    return corridorsData[0];
  }

  function getWardData(ward) {
    if (!wardsData || !wardsData.features) return null;
    for (const feature of wardsData.features) {
      if (feature.properties && feature.properties.ward === String(ward)) {
        return feature.properties;
      }
    }
    return null;
  }

  function getAldermanForWard(ward) {
    if (!aldemenData || !aldemenData.wards) return null;
    for (const w of aldemenData.wards) {
      if (w.ward === String(ward)) {
        return w;
      }
    }
    return null;
  }

  function get311ComplaintsForWard(ward) {
    if (!ward311Data || !ward311Data.wards) return null;
    for (const w of ward311Data.wards) {
      if (w.ward === String(ward)) {
        return w.total;
      }
    }
    return 0;
  }

  function renderTalkingPoints(ward) {
    const app = document.getElementById("app");
    const existingCard = app.querySelector(".talking-points-card");
    if (existingCard) {
      existingCard.remove();
    }

    const wardData = getWardData(ward);
    if (!wardData) {
      return;
    }

    const card = document.createElement("div");
    card.className = "card talking-points-card";

    let html = `<h3>Ward ${BSD.esc(wardData.ward)} — Talking Points</h3>`;
    html += `<div style="margin: 0.8rem 0; line-height: 1.8;">`;

    html += `<div><strong>Cyclist crashes:</strong> <span class="stat" style="font-size: 1.4rem;">${BSD.fmt(wardData.cyclist_crashes)}</span></div>`;
    html += `<div><strong>Injury crashes:</strong> ${BSD.fmt(wardData.injuries)}</div>`;
    html += `<div><strong>Fatalities:</strong> ${BSD.fmt(wardData.fatalities)}</div>`;

    const complaints311 = get311ComplaintsForWard(ward) || 0;
    html += `<div><strong>311 bike complaints:</strong> ${BSD.fmt(complaints311)} ${BSD.badgeHTML("proxy")}</div>`;

    html += `<div><strong>Density band:</strong> ${BSD.esc(wardData.density_band)}</div>`;

    html += `</div>`;

    const worstCorridor = findWorstCorridor();
    if (worstCorridor) {
      html += `<div class="muted" style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid var(--line);">`;
      html += `<strong>Citywide context:</strong> ${BSD.esc(worstCorridor.street)} has ${BSD.fmt(worstCorridor.crashes_per_km)} crashes/km.`;
      html += `</div>`;
    }

    const alderman = getAldermanForWard(ward);
    html += `<div style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid var(--line);">`;
    if (alderman && alderman.alderman) {
      html += `<strong>${BSD.esc(alderman.alderman)}</strong>`;
      if (alderman.email) {
        html += ` — <a href="mailto:${BSD.esc(alderman.email)}">${BSD.esc(alderman.email)}</a>`;
      }
    } else {
      html += `<a href="${BSD.esc(BSD.LINKS.aldermanLookup)}" target="_blank" rel="noopener">Find your alderman →</a>`;
    }
    html += `</div>`;

    if (aldemenData && aldemenData.note) {
      html += `<div class="muted" style="margin-top: 0.6rem; font-size: 0.8rem;">`;
      html += BSD.esc(aldemenData.note);
      html += `</div>`;
    }

    card.innerHTML = html;
    app.appendChild(card);
  }

  async function render() {
    BSD.initPage("action.html");
    const app = document.getElementById("app");

    try {
      await loadAllData();

      const heading = document.createElement("div");
      heading.innerHTML = `<h1>Take Action</h1>`;
      app.appendChild(heading);

      const reportSection = document.createElement("section");
      reportSection.innerHTML = `<h2>See a problem? Report it directly</h2><p style="color: var(--ink-soft);">This dashboard is an evidence layer, not a collection layer. Submit your report to the systems that actually investigate and act:</p>`;
      app.appendChild(reportSection);

      const reportCards = document.createElement("div");
      reportCards.className = "cards-grid";

      const card311 = document.createElement("a");
      card311.href = BSD.LINKS.threeOneOne;
      card311.target = "_blank";
      card311.rel = "noopener";
      card311.className = "card";
      card311.style.textDecoration = "none";
      card311.style.color = "inherit";
      card311.innerHTML = `
        <h3 style="margin-top: 0; color: var(--accent);">311 — City Service Requests</h3>
        <p>Physical hazards, signals, debris, pothole repair requests. Report infrastructure problems directly to the city.</p>
      `;
      reportCards.appendChild(card311);

      const cardBLU = document.createElement("a");
      cardBLU.href = BSD.LINKS.blu;
      cardBLU.target = "_blank";
      cardBLU.rel = "noopener";
      cardBLU.className = "card";
      cardBLU.style.textDecoration = "none";
      cardBLU.style.color = "inherit";
      cardBLU.innerHTML = `
        <h3 style="margin-top: 0; color: var(--accent);">Bike Lane Uprising</h3>
        <p>Report blocked bike lanes and obstructions with a photo. Build the evidence base for advocacy.</p>
      `;
      reportCards.appendChild(cardBLU);

      app.appendChild(reportCards);

      const advocacySection = document.createElement("section");
      advocacySection.style.marginTop = "2rem";
      advocacySection.innerHTML = `<h2>Want to advocate?</h2><p style="color: var(--ink-soft);">Pick your ward to see local crash trends and reach your alderman.</p>`;
      app.appendChild(advocacySection);

      const selectContainer = document.createElement("div");
      selectContainer.className = "filter-row";
      selectContainer.style.marginBottom = "1rem";

      const label = document.createElement("label");
      label.textContent = "Ward:";
      label.style.fontWeight = "600";
      selectContainer.appendChild(label);

      const select = document.createElement("select");
      select.id = "ward-select";

      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "Select a ward...";
      select.appendChild(defaultOption);

      for (let i = 1; i <= 50; i++) {
        const option = document.createElement("option");
        option.value = String(i);
        option.textContent = `Ward ${i}`;
        select.appendChild(option);
      }

      const params = BSD.qs();
      const initialWard = params.get("ward");
      if (initialWard) {
        select.value = initialWard;
      }

      select.addEventListener("change", function () {
        const ward = this.value;
        if (ward) {
          BSD.setParams({ ward: ward });
          renderTalkingPoints(ward);
        } else {
          BSD.setParams({ ward: null });
          const existingCard = app.querySelector(".talking-points-card");
          if (existingCard) {
            existingCard.remove();
          }
        }
      });

      selectContainer.appendChild(select);
      app.appendChild(selectContainer);

      if (initialWard) {
        renderTalkingPoints(initialWard);
      }

      const closingLine = document.createElement("div");
      closingLine.className = "muted";
      closingLine.style.marginTop = "2rem";
      closingLine.style.paddingTop = "1.5rem";
      closingLine.style.borderTop = "1px solid var(--line)";
      closingLine.innerHTML = `This dashboard is an evidence layer showing correlation patterns — not a collection layer. Use it to understand where the problems are, then report directly to the systems that can act.`;
      app.appendChild(closingLine);

    } catch (err) {
      const noticeDiv = document.createElement("div");
      noticeDiv.innerHTML = BSD.noticeHTML(`Error loading data: ${BSD.esc(err.message)}`);
      app.appendChild(noticeDiv);
    }
  }

  render();
})();
