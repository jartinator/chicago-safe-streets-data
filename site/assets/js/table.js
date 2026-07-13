/* Data table screen with filters, sorting, and CSV export.
 * Pure functions (filterCrashes, buildCSVRows) are Node-compatible. */

// Pure functions that work in Node and browser
function filterCrashes(crashes, filters) {
  return crashes.filter(crash => {
    if (filters.ward && crash.properties.ward !== filters.ward) return false;
    if (filters.severity && crash.properties.injury_severity !== filters.severity) return false;
    if (filters.crashType && crash.properties.crash_type !== filters.crashType) return false;
    if (filters.infrastructureType) {
      const fac = filters.facilityMap[crash.properties.segment_id] || null;
      const crashFacility = fac || "off-network";
      if (filters.infrastructureType !== "all" && filters.infrastructureType !== crashFacility) {
        return false;
      }
    }
    if (filters.dooringOnly && !crash.properties.dooring) return false;
    if (filters.dateFrom) {
      const crashDate = new Date(crash.properties.date);
      if (crashDate < filters.dateFrom) return false;
    }
    if (filters.dateTo) {
      const crashDate = new Date(crash.properties.date);
      if (crashDate > filters.dateTo) return false;
    }
    return true;
  });
}

function buildCSVRows(crashes, facilityMap, severityLabels) {
  return crashes.map(crash => {
    const props = crash.properties;
    const coords = crash.geometry.coordinates;
    const facility = facilityMap[props.segment_id] || "—";
    return {
      crash_id: props.crash_id,
      date: props.date,
      injury_severity: props.injury_severity,
      crash_type: props.crash_type,
      dooring: props.dooring ? "yes" : "—",
      hit_and_run: props.hit_and_run ? "yes" : "—",
      street: props.street,
      ward: props.ward || "—",
      facility: facility,
      lat: coords[1],
      lng: coords[0],
    };
  });
}

function buildSafetyIndexRows(wards) {
  return wards.map((w, i) => {
    const trend = w.crash_trend || {};
    return {
      rank: i + 1,
      ward: w.ward,
      comparable_danger_score: w.comparable_danger_score,
      cyclist_crashes: w.cyclist_crashes,
      crashes_per_10k_pop: w.crashes_per_10k_pop,
      crashes_per_bikeway_mile: w.crashes_per_bikeway_mile,
      bikeway_miles: w.bikeway_miles,
      population: w.population,
      trend_direction: trend.direction != null ? trend.direction : null,
      trend_pct_change: trend.pct_change != null ? trend.pct_change : null,
      bikeway_pct_protected: w.bikeway_pct_protected != null ? w.bikeway_pct_protected : null,
      road_miles: w.road_miles != null ? w.road_miles : null,
      bikeway_pct_of_roads: w.bikeway_pct_of_roads != null ? w.bikeway_pct_of_roads : null,
    };
  });
}

function buildCouncilRows(records) {
  return records.map(r => {
    const votes = r.recorded_votes;
    return {
      matter_id: r.matter_id,
      intro_date: (r.intro_date || "").slice(0, 10),
      title: r.title,
      type: r.type,
      status: r.status,
      sponsors: (r.sponsors || []).join("; "),
      source: r.source || "legistar",
      vote: votes ? `${votes.yes}–${votes.no} ${votes.result}` : "",
      no_voters: votes && votes.no_voters ? votes.no_voters : [],
      topic_tagged_by: r.topic_tagged_by,
      url: r.url,
    };
  });
}

// Comparator helper shared by the sortable dataset tables: nulls always sort
// to the bottom regardless of sort direction.
function compareNullsLast(aVal, bVal, asc) {
  const aNull = aVal == null;
  const bNull = bVal == null;
  if (aNull && bNull) return 0;
  if (aNull) return 1;
  if (bNull) return -1;
  if (aVal < bVal) return asc ? -1 : 1;
  if (aVal > bVal) return asc ? 1 : -1;
  return 0;
}

// DOM code only runs in browser
if (typeof document !== "undefined") {
  (async function init() {
    const SEVERITY_ORDER = BSD.SEVERITY_ORDER;
    const SEVERITY_LABELS = BSD.SEVERITY_LABELS;
    const FACILITY_LABELS = BSD.FACILITY_LABELS;

    // Initialize page
    BSD.initPage("table.html");

    const app = document.getElementById("app");

    // Create heading
    const heading = document.createElement("div");
    heading.style.display = "flex";
    heading.style.alignItems = "center";
    heading.style.gap = "0.5rem";
    heading.style.marginBottom = "1rem";
    heading.innerHTML = "<h1 style='margin: 0;'>Explore the data</h1>";
    app.appendChild(heading);

    // ---- Dataset switcher ----
    const DATASETS = [
      { key: "crashes", label: "Crashes", tiers: ["real"] },
      { key: "safety_index", label: "Ward safety index", tiers: ["derived"] },
      { key: "council", label: "Council records", tiers: ["real", "derived"] },
    ];
    const validKeys = DATASETS.map(d => d.key);

    const tabRow = document.createElement("div");
    tabRow.style.display = "flex";
    tabRow.style.gap = "0.5rem";
    tabRow.style.flexWrap = "wrap";
    tabRow.style.alignItems = "center";
    tabRow.style.marginBottom = "1rem";
    const tabButtons = {};
    DATASETS.forEach(ds => {
      // Tier badges are themselves <button>s (tap opens the explainer modal),
      // so they must be siblings of the tab button — never nested inside it
      // (nested buttons are invalid HTML and break keyboard/screen-reader use).
      const tab = document.createElement("span");
      tab.style.display = "inline-flex";
      tab.style.alignItems = "center";
      tab.style.gap = "0.35rem";
      const btn = document.createElement("button");
      btn.className = "btn";
      btn.textContent = ds.label;
      btn.addEventListener("click", () => switchDataset(ds.key));
      tab.appendChild(btn);
      tab.insertAdjacentHTML("beforeend", ds.tiers.map(t => BSD.badgeHTML(t)).join(""));
      tabRow.appendChild(tab);
      tabButtons[ds.key] = btn;
    });
    app.appendChild(tabRow);

    const sectionEl = document.createElement("div");
    app.appendChild(sectionEl);

    let currentDataset = validKeys.includes(BSD.qs().get("dataset")) ? BSD.qs().get("dataset") : "crashes";

    function updateTabs() {
      DATASETS.forEach(ds => {
        tabButtons[ds.key].classList.toggle("primary", ds.key === currentDataset);
      });
    }

    async function switchDataset(key) {
      if (key === currentDataset) return;
      currentDataset = key;
      BSD.setParams({ dataset: key === "crashes" ? null : key });
      updateTabs();
      await showSection();
    }

    async function showSection() {
      sectionEl.innerHTML = `<div class="muted">Loading…</div>`;
      try {
        if (currentDataset === "crashes") {
          await renderCrashSection(sectionEl);
        } else if (currentDataset === "safety_index") {
          await renderSafetyIndexSection(sectionEl);
        } else if (currentDataset === "council") {
          await renderCouncilSection(sectionEl);
        }
      } catch (err) {
        sectionEl.innerHTML = BSD.noticeHTML(`Error loading data: ${err.message}`);
      }
    }

    // ---- Crashes section (pre-existing behavior; filters/CSV/sort untouched) ----
    let crashesCache = null;
    async function renderCrashSection(container) {
      if (!crashesCache) {
        const [crashesGeo, routesGeo] = await Promise.all([
          BSD.loadJSON("data/crashes_cyclist.geojson"),
          BSD.loadJSON("data/bike_routes.geojson"),
        ]);
        const facilityMap = {};
        routesGeo.features.forEach(f => {
          facilityMap[f.properties.segment_id] = f.properties.facility_category;
        });
        crashesCache = { crashes: crashesGeo.features, facilityMap };
      }
      const { crashes, facilityMap } = crashesCache;

      container.innerHTML = "";

      const badgeWrap = document.createElement("div");
      badgeWrap.style.marginBottom = "0.5rem";
      badgeWrap.innerHTML = BSD.badgeHTML("real");
      container.appendChild(badgeWrap);

      // Extract unique values for filters
      const uniqueWards = [...new Set(crashes.map(c => c.properties.ward).filter(w => w))].sort((a, b) => {
        const aNum = parseInt(a), bNum = parseInt(b);
        return isNaN(aNum) || isNaN(bNum) ? 0 : aNum - bNum;
      });
      const uniqueCrashTypes = [...new Set(crashes.map(c => c.properties.crash_type))].sort();
      const uniqueFacilities = ["off-network", ...new Set(crashes.map(c => facilityMap[c.properties.segment_id]).filter(f => f))].sort();

      // State
      let state = {
        ward: BSD.qs().get("ward") || null,
        severity: null,
        crashType: null,
        infrastructureType: "all",
        dooringOnly: BSD.qs().get("dooring") === "1",
        dateFrom: null,
        dateTo: null,
        sortCol: "date",
        sortAsc: false, // false = desc (most recent first)
      };

      // Filter row
      const filterRow = document.createElement("div");
      filterRow.className = "filter-row";

      const wardLabel = document.createElement("label");
      wardLabel.style.display = "flex";
      wardLabel.style.alignItems = "center";
      wardLabel.style.gap = "0.25rem";
      wardLabel.textContent = "Ward:";
      const wardSelect = document.createElement("select");
      wardSelect.innerHTML = "<option value=''>All</option>" +
        uniqueWards.map(w => `<option value='${w}'${state.ward === w ? " selected" : ""}>${w}</option>`).join("");
      wardSelect.addEventListener("change", e => {
        state.ward = e.target.value || null;
        BSD.setParams({ ward: state.ward, dooring: state.dooringOnly ? "1" : null });
        render();
      });
      wardLabel.appendChild(wardSelect);
      filterRow.appendChild(wardLabel);

      const severityLabel = document.createElement("label");
      severityLabel.style.display = "flex";
      severityLabel.style.alignItems = "center";
      severityLabel.style.gap = "0.25rem";
      severityLabel.textContent = "Severity:";
      const severitySelect = document.createElement("select");
      severitySelect.innerHTML = "<option value=''>All</option>" +
        SEVERITY_ORDER.map(s => `<option value='${s}'>${SEVERITY_LABELS[s]}</option>`).join("");
      severitySelect.addEventListener("change", e => {
        state.severity = e.target.value || null;
        render();
      });
      severityLabel.appendChild(severitySelect);
      filterRow.appendChild(severityLabel);

      const crashTypeLabel = document.createElement("label");
      crashTypeLabel.style.display = "flex";
      crashTypeLabel.style.alignItems = "center";
      crashTypeLabel.style.gap = "0.25rem";
      crashTypeLabel.textContent = "Crash Type:";
      const crashTypeSelect = document.createElement("select");
      crashTypeSelect.innerHTML = "<option value=''>All</option>" +
        uniqueCrashTypes.map(ct => `<option value='${ct}'>${BSD.esc(ct)}</option>`).join("");
      crashTypeSelect.addEventListener("change", e => {
        state.crashType = e.target.value || null;
        render();
      });
      crashTypeLabel.appendChild(crashTypeSelect);
      filterRow.appendChild(crashTypeLabel);

      const infraLabel = document.createElement("label");
      infraLabel.style.display = "flex";
      infraLabel.style.alignItems = "center";
      infraLabel.style.gap = "0.25rem";
      infraLabel.textContent = "Infrastructure:";
      const infraSelect = document.createElement("select");
      infraSelect.innerHTML = "<option value='all'>All</option>" +
        uniqueFacilities.map(f => `<option value='${f}'>${f === "off-network" ? "Off-network" : FACILITY_LABELS[f] || BSD.esc(f)}</option>`).join("");
      infraSelect.addEventListener("change", e => {
        state.infrastructureType = e.target.value;
        render();
      });
      infraLabel.appendChild(infraSelect);
      filterRow.appendChild(infraLabel);

      const dateFromLabel = document.createElement("label");
      dateFromLabel.style.display = "flex";
      dateFromLabel.style.alignItems = "center";
      dateFromLabel.style.gap = "0.25rem";
      dateFromLabel.textContent = "Date From:";
      const dateFromInput = document.createElement("input");
      dateFromInput.type = "date";
      dateFromInput.addEventListener("change", e => {
        state.dateFrom = e.target.value ? new Date(e.target.value) : null;
        render();
      });
      dateFromLabel.appendChild(dateFromInput);
      filterRow.appendChild(dateFromLabel);

      const dateToLabel = document.createElement("label");
      dateToLabel.style.display = "flex";
      dateToLabel.style.alignItems = "center";
      dateToLabel.style.gap = "0.25rem";
      dateToLabel.textContent = "Date To:";
      const dateToInput = document.createElement("input");
      dateToInput.type = "date";
      dateToInput.addEventListener("change", e => {
        state.dateTo = e.target.value ? new Date(e.target.value + "T23:59:59") : null;
        render();
      });
      dateToLabel.appendChild(dateToInput);
      filterRow.appendChild(dateToLabel);

      const dooringLabel = document.createElement("label");
      dooringLabel.style.display = "flex";
      dooringLabel.style.alignItems = "center";
      dooringLabel.style.gap = "0.25rem";
      const dooringCheckbox = document.createElement("input");
      dooringCheckbox.type = "checkbox";
      dooringCheckbox.checked = state.dooringOnly;
      dooringCheckbox.addEventListener("change", e => {
        state.dooringOnly = e.target.checked;
        BSD.setParams({ ward: state.ward, dooring: state.dooringOnly ? "1" : null });
        render();
      });
      dooringLabel.appendChild(dooringCheckbox);
      dooringLabel.appendChild(document.createTextNode("Dooring only"));
      filterRow.appendChild(dooringLabel);

      const resetBtn = document.createElement("button");
      resetBtn.className = "btn";
      resetBtn.textContent = "Reset";
      resetBtn.addEventListener("click", () => {
        state.ward = null;
        state.severity = null;
        state.crashType = null;
        state.infrastructureType = "all";
        state.dooringOnly = false;
        state.dateFrom = null;
        state.dateTo = null;
        BSD.setParams({ ward: null, dooring: null });
        wardSelect.value = "";
        severitySelect.value = "";
        crashTypeSelect.value = "";
        infraSelect.value = "all";
        dateFromInput.value = "";
        dateToInput.value = "";
        dooringCheckbox.checked = false;
        render();
      });
      filterRow.appendChild(resetBtn);
      container.appendChild(filterRow);

      // Count display
      const countDiv = document.createElement("div");
      countDiv.style.marginBottom = "1rem";
      container.appendChild(countDiv);

      // Collapsed explainer directly above the table (replaces the old
      // floating directional/dooring notices).
      const explainer = document.createElement("details");
      explainer.className = "fine-print";
      explainer.style.marginBottom = "0.75rem";
      explainer.innerHTML =
        `<summary>How to read this table</summary>` +
        `<p><strong>Dooring†</strong>: structurally undercounted — dooring is excluded from ` +
        `"reportable" crash records unless damage/injury thresholds are met; treat "yes" ` +
        `counts as a floor.</p>` +
        `<p><strong>Severity</strong>: as recorded by responding officers; recent months are provisional.</p>` +
        `<p>Counts are raw — not adjusted for how many people ride each street, so busy corridors ` +
        `look worse than dangerous quiet ones.</p>`;
      container.appendChild(explainer);

      // Table wrapper
      const tableWrapper = document.createElement("div");
      tableWrapper.className = "table-scroll";
      container.appendChild(tableWrapper);

      // CSV export button
      const csvBtn = document.createElement("button");
      csvBtn.className = "btn primary";
      csvBtn.textContent = "Export CSV";
      csvBtn.style.marginTop = "1rem";
      csvBtn.addEventListener("click", () => {
        const filters = {
          ward: state.ward,
          severity: state.severity,
          crashType: state.crashType,
          infrastructureType: state.infrastructureType,
          dooringOnly: state.dooringOnly,
          dateFrom: state.dateFrom,
          dateTo: state.dateTo,
          facilityMap,
        };
        const filtered = filterCrashes(crashes, filters);
        const csvRows = buildCSVRows(filtered, facilityMap, SEVERITY_LABELS);
        const cols = ["crash_id", "date", "injury_severity", "crash_type", "dooring", "hit_and_run", "street", "ward", "facility", "lat", "lng"];
        BSD.downloadCSV("cyclist_crashes_filtered.csv", csvRows, cols);
      });
      container.appendChild(csvBtn);

      function render() {
        const filters = {
          ward: state.ward,
          severity: state.severity,
          crashType: state.crashType,
          infrastructureType: state.infrastructureType,
          dooringOnly: state.dooringOnly,
          dateFrom: state.dateFrom,
          dateTo: state.dateTo,
          facilityMap,
        };

        const filtered = filterCrashes(crashes, filters);
        const totalCount = filtered.length;

        // Sort
        let sorted = [...filtered];
        sorted.sort((a, b) => {
          let aVal, bVal;
          if (state.sortCol === "date") {
            aVal = new Date(a.properties.date).getTime();
            bVal = new Date(b.properties.date).getTime();
          } else if (state.sortCol === "severity") {
            aVal = SEVERITY_ORDER.indexOf(a.properties.injury_severity);
            bVal = SEVERITY_ORDER.indexOf(b.properties.injury_severity);
          } else if (state.sortCol === "crash_type") {
            aVal = a.properties.crash_type;
            bVal = b.properties.crash_type;
          } else if (state.sortCol === "dooring") {
            aVal = a.properties.dooring ? 1 : 0;
            bVal = b.properties.dooring ? 1 : 0;
          } else if (state.sortCol === "hit_and_run") {
            aVal = a.properties.hit_and_run ? 1 : 0;
            bVal = b.properties.hit_and_run ? 1 : 0;
          } else if (state.sortCol === "street") {
            aVal = a.properties.street;
            bVal = b.properties.street;
          } else if (state.sortCol === "ward") {
            aVal = a.properties.ward || "";
            bVal = b.properties.ward || "";
          } else if (state.sortCol === "facility") {
            aVal = facilityMap[a.properties.segment_id] || "";
            bVal = facilityMap[b.properties.segment_id] || "";
          }
          if (aVal < bVal) return state.sortAsc ? -1 : 1;
          if (aVal > bVal) return state.sortAsc ? 1 : -1;
          return 0;
        });

        // Update count
        const renderCount = Math.min(sorted.length, 500);
        let countText = `${BSD.fmt(renderCount)} crash${renderCount !== 1 ? "es" : ""} match`;
        if (sorted.length > 500) {
          countText += ` (showing first 500 of ${BSD.fmt(totalCount)})`;
        }
        countDiv.innerHTML = `<strong>${countText}</strong>`;
        if (sorted.length > 500) {
          const note = document.createElement("div");
          note.className = "muted";
          note.style.marginTop = "0.25rem";
          note.textContent = "Export CSV for all rows";
          countDiv.appendChild(note);
        }

        // Build table
        const table = document.createElement("table");
        table.className = "data";

        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");
        const cols = ["date", "severity", "crash_type", "dooring", "hit_and_run", "street", "ward", "facility"];
        const labels = {
          date: "Date",
          severity: "Severity",
          crash_type: "Crash Type",
          dooring: "Dooring†",
          hit_and_run: "Hit & Run",
          street: "Street",
          ward: "Ward",
          facility: "Facility",
        };

        cols.forEach(col => {
          const th = document.createElement("th");
          th.textContent = labels[col];
          if (state.sortCol === col) {
            th.className = state.sortAsc ? "sorted-asc" : "sorted-desc";
          }
          th.addEventListener("click", () => {
            if (state.sortCol === col) {
              state.sortAsc = !state.sortAsc;
            } else {
              state.sortCol = col;
              state.sortAsc = false;
            }
            render();
          });
          headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        sorted.slice(0, 500).forEach(crash => {
          const props = crash.properties;
          const row = document.createElement("tr");
          const cells = [
            props.date,
            SEVERITY_LABELS[props.injury_severity] || props.injury_severity,
            props.crash_type,
            props.dooring ? "yes" : "—",
            props.hit_and_run ? "yes" : "—",
            props.street,
            props.ward || "—",
            facilityMap[props.segment_id] ? FACILITY_LABELS[facilityMap[props.segment_id]] || facilityMap[props.segment_id] : "—",
          ];
          cells.forEach(cell => {
            const td = document.createElement("td");
            td.textContent = cell;
            row.appendChild(td);
          });
          tbody.appendChild(row);
        });
        table.appendChild(tbody);

        tableWrapper.innerHTML = "";
        tableWrapper.appendChild(table);
      }

      render();
    }

    // ---- Ward safety index section ----
    let safetyIndexCache = null;
    async function renderSafetyIndexSection(container) {
      if (!safetyIndexCache) {
        safetyIndexCache = await BSD.loadJSON("data/ward_safety_index.json");
      }
      const data = safetyIndexCache;
      const rows = buildSafetyIndexRows(data.wards || []);

      container.innerHTML = "";

      const badgeWrap = document.createElement("div");
      badgeWrap.style.marginBottom = "0.5rem";
      badgeWrap.innerHTML = BSD.badgeHTML("derived");
      container.appendChild(badgeWrap);

      // Collapsed explainer replacing the raw data.note dump.
      const explainer = document.createElement("details");
      explainer.className = "fine-print";
      explainer.style.marginBottom = "0.75rem";
      explainer.innerHTML =
        `<summary>About this score</summary>` +
        `<p>The danger score is the average of each ward's percentile ranks on crashes per 10k ` +
        `residents and crashes per bikeway mile — 0–100, higher = more dangerous relative to ` +
        `other wards. It compares wards to each other; it is not an absolute risk measure. ` +
        `% protected is the protected share of the ward's on-street bikeway miles; % streets ` +
        `w/ bikeways is the share of the ward's surface-street miles with any bike infrastructure. ` +
        `<a href="sources.html#src-ward_safety_index">Full source detail →</a></p>`;
      container.appendChild(explainer);

      const countDiv = document.createElement("div");
      countDiv.style.margin = "1rem 0";
      countDiv.innerHTML = `<strong>${BSD.fmt(rows.length)} ward${rows.length !== 1 ? "s" : ""}</strong>`;
      container.appendChild(countDiv);

      const tableWrapper = document.createElement("div");
      tableWrapper.className = "table-scroll";
      container.appendChild(tableWrapper);

      const csvBtn = document.createElement("button");
      csvBtn.className = "btn primary";
      csvBtn.textContent = "Export CSV";
      csvBtn.style.marginTop = "1rem";
      csvBtn.addEventListener("click", () => {
        const cols = ["rank", "ward", "comparable_danger_score", "cyclist_crashes",
          "crashes_per_10k_pop", "crashes_per_bikeway_mile", "bikeway_miles",
          "bikeway_pct_protected", "road_miles", "bikeway_pct_of_roads", "population",
          "trend_direction", "trend_pct_change"];
        BSD.downloadCSV("ward_safety_index.csv", rows, cols);
      });
      container.appendChild(csvBtn);

      const COLS = [
        { key: "rank", label: "Rank" },
        { key: "ward", label: "Ward" },
        { key: "comparable_danger_score", label: "Danger score",
          title: "0–100 vs other wards — see 'About this score'" },
        { key: "cyclist_crashes", label: "Crashes" },
        { key: "crashes_per_10k_pop", label: "Per 10k pop" },
        { key: "crashes_per_bikeway_mile", label: "Per bikeway mile" },
        { key: "bikeway_miles", label: "Bikeway miles" },
        { key: "bikeway_pct_protected", label: "% protected",
          title: "Share of the ward's on-street bikeway miles that are physically protected lanes" },
        { key: "bikeway_pct_of_roads", label: "% streets w/ bikeways",
          title: "Share of the ward's surface-street miles with any bike infrastructure (off-street trails excluded)" },
        { key: "population", label: "Population" },
        { key: "trend_direction", label: "Trend" },
      ];

      let sortCol = "comparable_danger_score";
      let sortAsc = false;

      function renderTable() {
        const sorted = [...rows].sort((a, b) => {
          const aVal = sortCol === "trend_direction" ? a.trend_pct_change : a[sortCol];
          const bVal = sortCol === "trend_direction" ? b.trend_pct_change : b[sortCol];
          return compareNullsLast(aVal, bVal, sortAsc);
        });

        const table = document.createElement("table");
        table.className = "data";

        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");
        COLS.forEach(col => {
          const th = document.createElement("th");
          th.textContent = col.label;
          if (col.title) th.title = col.title;
          if (sortCol === col.key) th.className = sortAsc ? "sorted-asc" : "sorted-desc";
          th.addEventListener("click", () => {
            if (sortCol === col.key) sortAsc = !sortAsc;
            else { sortCol = col.key; sortAsc = false; }
            renderTable();
          });
          headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        sorted.forEach(row => {
          const tr = document.createElement("tr");
          const plainCells = [
            row.rank,
            row.ward,
            BSD.fmt(row.comparable_danger_score),
            BSD.fmt(row.cyclist_crashes),
            BSD.fmt(row.crashes_per_10k_pop),
            BSD.fmt(row.crashes_per_bikeway_mile),
            BSD.fmt(row.bikeway_miles),
            row.bikeway_pct_protected == null ? "—" : row.bikeway_pct_protected + "%",
            row.bikeway_pct_of_roads == null ? "—" : row.bikeway_pct_of_roads + "%",
            BSD.fmt(row.population),
          ];
          plainCells.forEach(cell => {
            const td = document.createElement("td");
            td.textContent = cell;
            tr.appendChild(td);
          });
          const trendTd = document.createElement("td");
          trendTd.innerHTML = BSD.trendHTML({ direction: row.trend_direction, pct_change: row.trend_pct_change });
          tr.appendChild(trendTd);
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        tableWrapper.innerHTML = "";
        tableWrapper.appendChild(table);
      }

      renderTable();
    }

    // ---- Council records section ----
    let councilCache = null;
    async function renderCouncilSection(container) {
      if (!councilCache) {
        councilCache = await BSD.loadJSON("data/council_records.json");
      }
      const data = councilCache;
      const rows = buildCouncilRows(data.records || []);

      container.innerHTML = "";

      // Collapsed explainer replacing the raw data.note dump; also carries the
      // Source-column explanation that used to hide in a hover-only tooltip.
      const explainer = document.createElement("details");
      explainer.className = "fine-print";
      explainer.style.marginBottom = "0.75rem";
      explainer.innerHTML =
        `<summary>About these records</summary>` +
        (data.note ? `<p>${BSD.esc(data.note)}</p>` : "") +
        `<p><strong>Source</strong>: which pull produced the record — legistar rows end ` +
        `2023-06-21 (system migration); councilmatic rows are current.</p>`;
      container.appendChild(explainer);

      const countDiv = document.createElement("div");
      countDiv.style.margin = "1rem 0";
      countDiv.innerHTML = `<strong>${BSD.fmt(rows.length)} record${rows.length !== 1 ? "s" : ""}</strong>`;
      container.appendChild(countDiv);

      const tableWrapper = document.createElement("div");
      tableWrapper.className = "table-scroll";
      container.appendChild(tableWrapper);

      const csvBtn = document.createElement("button");
      csvBtn.className = "btn primary";
      csvBtn.textContent = "Export CSV";
      csvBtn.style.marginTop = "1rem";
      csvBtn.addEventListener("click", () => {
        const cols = ["intro_date", "title", "type", "status", "sponsors", "source", "vote", "topic_tagged_by", "url"];
        BSD.downloadCSV("council_records.csv", rows, cols);
      });
      container.appendChild(csvBtn);

      const COLS = [
        { key: "intro_date", label: "Introduced" },
        { key: "title", label: "Title" },
        { key: "type", label: "Type" },
        { key: "status", label: "Status" },
        { key: "sponsors", label: "Sponsors" },
        { key: "source", label: "Source" },
        { key: "vote", label: "Vote" },
        { key: "topic_tagged_by", label: "Tagged by" },
      ];

      let sortCol = "intro_date";
      let sortAsc = false;

      function renderTable() {
        const sorted = [...rows].sort((a, b) => compareNullsLast(a[sortCol], b[sortCol], sortAsc));

        const table = document.createElement("table");
        table.className = "data";

        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");
        COLS.forEach(col => {
          const th = document.createElement("th");
          th.textContent = col.label;
          if (sortCol === col.key) th.className = sortAsc ? "sorted-asc" : "sorted-desc";
          th.addEventListener("click", () => {
            if (sortCol === col.key) sortAsc = !sortAsc;
            else { sortCol = col.key; sortAsc = false; }
            renderTable();
          });
          headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        sorted.forEach(row => {
          const tr = document.createElement("tr");

          const introTd = document.createElement("td");
          introTd.textContent = row.intro_date || "—";
          tr.appendChild(introTd);

          const titleTd = document.createElement("td");
          if (row.url) {
            const link = document.createElement("a");
            link.href = row.url;
            link.target = "_blank";
            link.rel = "noopener";
            link.textContent = row.title || "—";
            titleTd.appendChild(link);
          } else {
            titleTd.textContent = row.title || "—";
          }
          tr.appendChild(titleTd);

          const typeTd = document.createElement("td");
          typeTd.textContent = row.type || "—";
          tr.appendChild(typeTd);

          const statusTd = document.createElement("td");
          statusTd.textContent = row.status || "—";
          tr.appendChild(statusTd);

          const sponsorsTd = document.createElement("td");
          sponsorsTd.textContent = row.sponsors || "—";
          tr.appendChild(sponsorsTd);

          const sourceTd = document.createElement("td");
          sourceTd.textContent = row.source;
          tr.appendChild(sourceTd);

          const voteTd = document.createElement("td");
          if (row.vote) {
            voteTd.textContent = row.vote;
            // "No" voters render visibly — a title tooltip alone is invisible
            // on touch devices.
            if (row.no_voters && row.no_voters.length) {
              const noLine = document.createElement("div");
              noLine.className = "muted";
              noLine.style.fontSize = "0.8rem";
              noLine.textContent = "no: " + row.no_voters.join(", ");
              voteTd.appendChild(noLine);
            }
          } else {
            voteTd.textContent = "";
          }
          tr.appendChild(voteTd);

          const taggedTd = document.createElement("td");
          if (row.topic_tagged_by === "llm") {
            taggedTd.innerHTML = `<span class="badge tier-derived" title="${BSD.esc("LLM-reviewed topic tag")}">derived</span>`;
          } else if (row.topic_tagged_by === "keyword_fallback") {
            taggedTd.innerHTML = `<span class="badge tier-derived" title="${BSD.esc("keyword match, not yet LLM-reviewed")}">derived</span>`;
          } else {
            taggedTd.textContent = "—";
          }
          tr.appendChild(taggedTd);

          tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        tableWrapper.innerHTML = "";
        tableWrapper.appendChild(table);
      }

      renderTable();
    }

    updateTabs();
    await showSection();
  })();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { filterCrashes, buildCSVRows, buildSafetyIndexRows, buildCouncilRows };
}
