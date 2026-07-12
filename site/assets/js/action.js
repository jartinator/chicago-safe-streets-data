/* Take Action screen: report links, per-ward talking points, and the ward
 * accountability report (safety scorecard, alderman record, menu spending,
 * upcoming hearings). Pure functions are Node-testable (no BSD dependency —
 * they take data as arguments); DOM code is guarded and only runs in the
 * browser, same pattern as common.js/network-model.js. */
(function () {
  // ---- Pure functions (Node + browser) ----

  // Look up a ward's row in ward_safety_index.json. Rank is the row's
  // position in the file's `wards` array (already sorted by the pipeline by
  // comparable_danger_score, descending) — never recomputed from the score.
  function getSafetyIndexForWard(safetyIndexData, ward) {
    if (!safetyIndexData || !Array.isArray(safetyIndexData.wards)) return null;
    const wardStr = String(ward);
    const idx = safetyIndexData.wards.findIndex(w => w.ward === wardStr);
    if (idx === -1) return null;
    return { entry: safetyIndexData.wards[idx], rank: idx + 1, total: safetyIndexData.wards.length };
  }

  // Resolve aldermen_safety_record.json entries for a ward. Matches ONLY:
  //   1. record.ward === String(ward) — pre-resolved by the pipeline, or
  //   2. exact sponsor_name === the aldermen.json name for that ward.
  // Never fuzzy-matched (no case-folding, trimming, or partial match) — a
  // wrong match here would misattribute a real person's voting record.
  function getSponsorRecordsForWard(aldermenSafetyData, aldermenData, ward) {
    const wardStr = String(ward);

    let aldermanName = null;
    if (aldermenData && Array.isArray(aldermenData.wards)) {
      const wardEntry = aldermenData.wards.find(w => w.ward === wardStr);
      if (wardEntry && wardEntry.alderman) aldermanName = wardEntry.alderman;
    }

    let matched = null;
    if (aldermenSafetyData && Array.isArray(aldermenSafetyData.aldermen)) {
      matched = aldermenSafetyData.aldermen.find(a => a.ward === wardStr) || null;
      if (!matched && aldermanName) {
        matched = aldermenSafetyData.aldermen.find(a => a.sponsor_name === aldermanName) || null;
      }
    }

    if (matched) {
      // Stale fixtures may predate the recorded_no_votes field entirely.
      matched = Object.assign({}, matched, { recorded_no_votes: matched.recorded_no_votes ?? 0 });
    }

    return { matched, aldermanName };
  }

  // Look up a ward's row in menu_spending.json (keyed by ward string).
  function getMenuSpendingForWard(menuData, ward) {
    if (!menuData || !menuData.wards) return null;
    const entry = menuData.wards[String(ward)];
    if (!entry) return null;
    return {
      total_spent: entry.total_spent,
      items: entry.items,
      bike_safety_spent: entry.bike_safety_spent ?? 0,
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { getSafetyIndexForWard, getSponsorRecordsForWard, getMenuSpendingForWard };
  }

  // ---- DOM code (browser only) ----
  if (typeof document === "undefined") return;

  const COVERAGE_NOTICE = "Legistar records end 2023-06-21 (system migration); Chicago " +
    "Councilmatic covers the council from then to the present.";

  let wardsData = null;
  let aldemenData = null;
  let corridorsData = null;
  let ward311Data = null;
  let safetyIndexData = null;
  let aldermenSafetyData = null;
  let menuSpendingData = null;
  let hearingsData = null;
  let isLoading = false;

  async function loadAllData() {
    try {
      [
        wardsData, aldemenData, corridorsData, ward311Data,
        safetyIndexData, aldermenSafetyData, menuSpendingData, hearingsData,
      ] = await Promise.all([
        BSD.loadJSON("data/wards.geojson"),
        BSD.loadJSON("data/aldermen.json"),
        BSD.loadJSON("data/corridors.json"),
        BSD.loadJSON("data/ward_311.json"),
        BSD.loadJSON("data/ward_safety_index.json").catch(() => null),
        BSD.loadJSON("data/aldermen_safety_record.json").catch(() => null),
        BSD.loadJSON("data/menu_spending.json").catch(() => null),
        BSD.loadJSON("data/hearings.json").catch(() => null),
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

  function cardHeadingHTML(text, tier) {
    return `<h3 style="margin-top: 0; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">${BSD.esc(text)} ${BSD.badgeHTML(tier)}</h3>`;
  }

  // ---- Ward safety scorecard (derived) ----
  function buildSafetyScorecardCard(ward) {
    const result = getSafetyIndexForWard(safetyIndexData, ward);
    const card = document.createElement("div");
    card.className = "card ward-safety-card";

    let html = cardHeadingHTML(`Ward ${ward} safety scorecard`, "derived");

    if (!result) {
      html += `<p class="muted">No safety index data for this ward in the current pull.</p>`;
      card.innerHTML = html;
      return card;
    }

    const { entry, rank, total } = result;
    const score = entry.comparable_danger_score;
    const scoreDisplay = score == null ? "—" : `${BSD.esc(score)} / 100`;
    html += `<div class="stat" style="color: ${BSD.scoreColor(score)};">${scoreDisplay}</div>`;
    html += `<div class="muted" style="margin-bottom: 0.6rem;">Rank ${BSD.fmt(rank)} of ${BSD.fmt(total)} wards</div>`;

    html += `<div style="line-height: 1.8;">`;
    html += `<div><strong>Crashes per 10k population:</strong> ${BSD.fmt(entry.crashes_per_10k_pop)}</div>`;
    html += `<div><strong>Crashes per bikeway mile:</strong> ${BSD.fmt(entry.crashes_per_bikeway_mile)}</div>`;
    html += `<div><strong>Bikeway miles:</strong> ${BSD.fmt(entry.bikeway_miles)}</div>`;
    html += `<div><strong>Population:</strong> ${BSD.fmt(entry.population)}</div>`;
    if (entry.crash_trend) {
      html += `<div><strong>Crash trend:</strong> ${BSD.trendHTML(entry.crash_trend)}</div>`;
    }
    html += `</div>`;

    if (!entry.infra_growth_trend) {
      html += `<div class="muted" style="margin-top: 0.6rem;">Infrastructure growth: needs two pipeline snapshots — check back after the next refresh.</div>`;
    } else {
      const g = entry.infra_growth_trend;
      const pctStr = g.pct_growth == null ? "—" : `${g.pct_growth > 0 ? "+" : ""}${g.pct_growth}%`;
      html += `<div class="muted" style="margin-top: 0.6rem;">Infrastructure growth: +${BSD.fmt(g.miles_added)} mi (${pctStr}) since ${BSD.esc(g.since)}.</div>`;
    }

    if (safetyIndexData && safetyIndexData.note) {
      html += `<div class="muted" style="margin-top: 0.6rem; font-size: 0.8rem;">${BSD.esc(safetyIndexData.note)}</div>`;
    }

    card.innerHTML = html;
    return card;
  }

  // ---- Alderman record (derived) ----
  function buildAldermanRecordCard(ward) {
    const { matched, aldermanName } = getSponsorRecordsForWard(aldermenSafetyData, aldemenData, ward);
    const card = document.createElement("div");
    card.className = "card alderman-record-card";

    let html = cardHeadingHTML("Alderman record", "derived");
    if (aldermanName) {
      html += `<div class="muted" style="margin-bottom: 0.4rem;">${BSD.esc(aldermanName)}</div>`;
    }

    if (matched) {
      html += `<div class="stat">${BSD.fmt(matched.safety_sponsorships)}</div>`;
      html += `<div class="muted" style="margin-bottom: 0.6rem;">tagged bike/traffic-safety sponsorships</div>`;

      const noVotes = matched.recorded_no_votes ?? 0;
      if (noVotes > 0) {
        html += `<div>Recorded "no" votes on tagged measures: ` +
          `<strong style="color: var(--sev-incap);" title="Times this alderman appears in a contested roll-call's no_voters list — rare; most measures pass by voice vote">${BSD.fmt(noVotes)}</strong></div>`;
      } else {
        html += `<div>Recorded "no" votes on tagged measures: ${BSD.fmt(noVotes)}</div>`;
      }

      const records = Array.isArray(matched.records) ? matched.records.slice(0, 5) : [];
      if (records.length) {
        html += `<div style="margin-top: 0.6rem; line-height: 1.8;">`;
        records.forEach(rec => {
          const date = rec.intro_date ? String(rec.intro_date).slice(0, 10) : "—";
          const title = rec.url
            ? `<a href="${BSD.esc(rec.url)}" target="_blank" rel="noopener">${BSD.esc(rec.title)}</a>`
            : BSD.esc(rec.title);
          html += `<div>${BSD.esc(date)} · ${title} · ${BSD.esc(rec.status)}</div>`;
        });
        html += `</div>`;
      }
    } else {
      html += `<p>Sponsorship records can't be tied to this ward yet — alderman names in aldermen.json are filled manually, never guessed.</p>`;
      html += `<p><a href="${BSD.esc(BSD.LINKS.aldermanLookup)}" target="_blank" rel="noopener">Official alderman lookup →</a></p>`;
    }

    html += `<div class="muted" style="margin-top: 0.6rem; font-size: 0.8rem; padding-top: 0.6rem; border-top: 1px solid var(--line);">${BSD.esc(COVERAGE_NOTICE)}</div>`;

    card.innerHTML = html;
    return card;
  }

  // ---- Menu-fund spending (proxy) ----
  function buildMenuSpendingCard(ward) {
    const spend = getMenuSpendingForWard(menuSpendingData, ward);
    const card = document.createElement("div");
    card.className = "card menu-spending-card";

    let html = cardHeadingHTML("Menu-fund spending", "proxy");

    if (!spend) {
      html += `<p class="muted">No menu-spending data for this ward in the current pull.</p>`;
    } else {
      html += `<div class="stat">${BSD.esc(BSD.money(spend.bike_safety_spent))}</div>`;
      html += `<div class="muted">of ${BSD.esc(BSD.money(spend.total_spent))} total menu spending (${BSD.fmt(spend.items)} items)</div>`;
    }

    if (menuSpendingData && menuSpendingData.note) {
      html += `<div class="muted" style="margin-top: 0.6rem; font-size: 0.8rem;">${BSD.esc(menuSpendingData.note)}</div>`;
    }

    card.innerHTML = html;
    return card;
  }

  // ---- Upcoming hearings (real) — ward-independent, rendered once ----
  function buildHearingsCard() {
    const card = document.createElement("div");
    card.className = "card hearings-card";

    let html = cardHeadingHTML("Upcoming hearings", "real");

    const committees = (hearingsData && Array.isArray(hearingsData.committees)) ? hearingsData.committees : [];
    if (!committees.length) {
      html += `<p class="muted">No committee hearing data in the current pull.</p>`;
    } else if (hearingsData.structured_data_available === false) {
      html += `<div style="line-height: 1.8;">`;
      committees.forEach(c => {
        html += `<div><a href="${BSD.esc(c.calendar_url)}" target="_blank" rel="noopener">${BSD.esc(c.committee)}</a>`;
        html += `<div class="muted" style="font-size: 0.85rem;">Live calendar — no structured feed available yet.</div></div>`;
      });
      html += `</div>`;
    } else {
      html += `<div style="line-height: 1.8;">`;
      committees.forEach(c => {
        html += `<div><strong>${BSD.esc(c.committee)}</strong>`;
        const meetings = Array.isArray(c.meetings) ? c.meetings : [];
        if (!meetings.length) {
          html += `<div class="muted" style="font-size: 0.85rem;">No meetings currently scheduled.</div>`;
        } else {
          meetings.forEach(m => {
            const when = m.date || m.datetime || "—";
            const what = m.title || m.description || "";
            html += `<div>${BSD.esc(when)}${what ? " · " + BSD.esc(what) : ""}</div>`;
          });
        }
        html += `</div>`;
      });
      html += `</div>`;
    }

    if (hearingsData && hearingsData.note) {
      html += `<div class="muted" style="margin-top: 0.6rem; font-size: 0.8rem;">${BSD.esc(hearingsData.note)}</div>`;
    }

    card.innerHTML = html;
    return card;
  }

  function removeWardScopedCards(app) {
    ["talking-points-card", "ward-safety-card", "alderman-record-card", "menu-spending-card"].forEach(cls => {
      const el = app.querySelector(`.${cls}`);
      if (el) el.remove();
    });
  }

  function renderTalkingPoints(ward) {
    const app = document.getElementById("app");
    removeWardScopedCards(app);

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

    // Ward-scoped accountability cards, re-rendered every time the ward changes.
    app.appendChild(buildSafetyScorecardCard(ward));
    app.appendChild(buildAldermanRecordCard(ward));
    app.appendChild(buildMenuSpendingCard(ward));
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

      const hearingsSection = document.createElement("section");
      hearingsSection.style.marginTop = "2rem";
      hearingsSection.innerHTML = `<h2>Upcoming committee hearings</h2>`;
      app.appendChild(hearingsSection);
      app.appendChild(buildHearingsCard());

      const advocacySection = document.createElement("section");
      advocacySection.style.marginTop = "2rem";
      advocacySection.innerHTML = `<h2>Want to advocate?</h2><p style="color: var(--ink-soft);">Pick your ward to see local crash trends, its safety scorecard, alderman record, and menu-fund spending.</p>`;
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
          removeWardScopedCards(app);
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
