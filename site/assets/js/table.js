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

// DOM code only runs in browser
if (typeof document !== "undefined") {
  (async function init() {
    const SEVERITY_ORDER = BSD.SEVERITY_ORDER;
    const SEVERITY_LABELS = BSD.SEVERITY_LABELS;
    const FACILITY_LABELS = BSD.FACILITY_LABELS;

    // Initialize page
    BSD.initPage("table.html");

    const app = document.getElementById("app");

    // Create heading with badge
    const heading = document.createElement("div");
    heading.style.display = "flex";
    heading.style.alignItems = "center";
    heading.style.gap = "0.5rem";
    heading.style.marginBottom = "1rem";
    heading.innerHTML = "<h1 style='margin: 0;'>Non-Map Data Table</h1>";
    heading.appendChild(document.createElement("span")).outerHTML = BSD.badgeHTML("real");
    app.appendChild(heading);

    // Add notices
    const notices = document.createElement("div");
    notices.innerHTML = BSD.noticeHTML("directional") + BSD.noticeHTML("dooring");
    app.appendChild(notices);

    // Load data
    let crashes, facilityMap;
    try {
      const [crashesGeo, routesGeo] = await Promise.all([
        BSD.loadJSON("data/crashes_cyclist.geojson"),
        BSD.loadJSON("data/bike_routes.geojson"),
      ]);
      crashes = crashesGeo.features;
      facilityMap = {};
      routesGeo.features.forEach(f => {
        facilityMap[f.properties.segment_id] = f.properties.facility_category;
      });
    } catch (err) {
      app.innerHTML += BSD.noticeHTML(`Error loading data: ${err.message}`);
      return;
    }

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
    app.appendChild(filterRow);

    // Count display
    const countDiv = document.createElement("div");
    countDiv.style.marginBottom = "1rem";
    app.appendChild(countDiv);

    // Table wrapper
    const tableWrapper = document.createElement("div");
    tableWrapper.className = "table-scroll";
    app.appendChild(tableWrapper);

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
    app.appendChild(csvBtn);

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
        dooring: "Dooring",
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
  })();
}
