/* Take Action screen: the unified per-ward performance report (crash trends,
 * what's coming up at City Hall, safety scorecard, alderperson record, menu
 * spending, provenance modal), plus report-it-directly links and the citywide
 * hearings card. Pure functions are Node-testable (no BSD dependency — they
 * take data as arguments); DOM code is guarded and only runs in the browser,
 * same pattern as common.js/network-model.js. */
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

  // ISO date `days` before `today` ("YYYY-MM-DD"); null when today is unusable.
  function _isoDaysBefore(today, days) {
    if (!today) return null;
    const t = new Date(String(today).slice(0, 10) + "T00:00:00Z");
    if (isNaN(t.getTime())) return null;
    return new Date(t.getTime() - days * 86400000).toISOString().slice(0, 10);
  }

  // What's coming up for a ward: upcoming committee meetings (flattened from
  // hearings.json with committee/calendar_url attached, past dates dropped)
  // plus council records recently introduced by this ward's alderperson.
  // Sponsor matching is by pipeline-resolved sponsor_wards OR an EXACT
  // sponsors[] name match against aldermanName — never fuzzy (a wrong match
  // misattributes a real person's record).
  function getUpcomingForWard(hearingsData, councilData, aldermanName, ward, today) {
    const wardStr = String(ward);
    const todayStr = today ? String(today).slice(0, 10) : null;

    const meetings = [];
    if (hearingsData && hearingsData.structured_data_available !== false &&
        Array.isArray(hearingsData.committees)) {
      hearingsData.committees.forEach(c => {
        (Array.isArray(c.meetings) ? c.meetings : []).forEach(m => {
          if (!m || !m.date) return;
          if (todayStr && String(m.date).slice(0, 10) < todayStr) return;
          meetings.push(Object.assign({}, m, {
            committee: c.committee,
            calendar_url: c.calendar_url || null,
          }));
        });
      });
      meetings.sort((a, b) => String(a.date).localeCompare(String(b.date)));
    }

    let introduced = [];
    if (councilData && Array.isArray(councilData.records)) {
      const cutoff = _isoDaysBefore(todayStr, 180);
      introduced = councilData.records
        .filter(r => {
          if (!r || !r.intro_date) return false;
          if (r.status !== "Introduced" && r.status !== "Referred") return false;
          if (cutoff && String(r.intro_date).slice(0, 10) < cutoff) return false;
          const byWard = Array.isArray(r.sponsor_wards) &&
            r.sponsor_wards.some(w => String(w) === wardStr);
          const byName = !!aldermanName && Array.isArray(r.sponsors) &&
            r.sponsors.indexOf(aldermanName) !== -1;
          return byWard || byName;
        })
        .sort((a, b) => String(b.intro_date).localeCompare(String(a.intro_date)))
        .slice(0, 5);
    }

    return { meetings, introduced };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      getSafetyIndexForWard, getSponsorRecordsForWard, getMenuSpendingForWard,
      getUpcomingForWard,
    };
  }

  // ---- DOM code (browser only) ----
  if (typeof document === "undefined") return;

  const COVERAGE_NOTICE = "Legistar records end 2023-06-21 (system migration); Chicago " +
    "Councilmatic covers the council from then to the present.";
  const MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  let wardsData = null;
  let aldemenData = null;
  let ward311Data = null;
  let safetyIndexData = null;
  let aldermenSafetyData = null;
  let menuSpendingData = null;
  let hearingsData = null;
  let councilData = null;
  let metaData = null;

  async function loadAllData() {
    try {
      [
        wardsData, aldemenData, ward311Data,
        safetyIndexData, aldermenSafetyData, menuSpendingData, hearingsData,
        councilData, metaData,
      ] = await Promise.all([
        BSD.loadJSON("data/wards.geojson"),
        BSD.loadJSON("data/aldermen.json"),
        BSD.loadJSON("data/ward_311.json"),
        BSD.loadJSON("data/ward_safety_index.json").catch(() => null),
        BSD.loadJSON("data/aldermen_safety_record.json").catch(() => null),
        BSD.loadJSON("data/menu_spending.json").catch(() => null),
        BSD.loadJSON("data/hearings.json").catch(() => null),
        BSD.loadJSON("data/council_records.json").catch(() => null),
        BSD.loadJSON("data/meta.json").catch(() => null),
      ]);
    } catch (err) {
      throw new Error(`Failed to load data: ${err.message}`);
    }
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

  // "2026-07-10" (or a full ISO timestamp) -> "Jul 10, 2026". String-sliced,
  // never Date-parsed, so timezone offsets can't shift the printed day.
  function fmtDate(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(iso || ""));
    if (!m) return String(iso || "—");
    return `${MONTH_ABBR[Number(m[2]) - 1]} ${Number(m[3])}, ${m[1]}`;
  }

  // "2026-07-14T13:00:00" -> "Jul 14"
  function fmtMonthDay(iso) {
    const m = /^\d{4}-(\d{2})-(\d{2})/.exec(String(iso || ""));
    if (!m) return String(iso || "—");
    return `${MONTH_ABBR[Number(m[1]) - 1]} ${Number(m[2])}`;
  }

  function sectionHeadingHTML(text, tier) {
    return `<h3 class="card-heading">${BSD.esc(text)} ${BSD.badgeHTML(tier)}</h3>`;
  }

  function todayISO() {
    return new Date().toISOString().slice(0, 10);
  }

  // Crash-data end date: meta.json crashes source range, falling back to the
  // safety index window end, falling back to "present".
  function crashDataEndLabel(entry) {
    const src = metaData && Array.isArray(metaData.sources)
      ? metaData.sources.find(s => s.id === "crashes") : null;
    if (src && Array.isArray(src.date_range) && src.date_range[1]) {
      return fmtDate(src.date_range[1]);
    }
    if (entry && entry.windows && entry.windows.window_end) {
      return fmtDate(entry.windows.window_end);
    }
    return "present";
  }

  // ---- Report header ----
  function reportHeadHTML(ward, entry) {
    const alderman = getAldermanForWard(ward);
    let who;
    if (alderman && alderman.alderman) {
      who = `Current alderperson: <strong>${BSD.esc(alderman.alderman)}</strong>`;
      if (alderman.email) {
        who += ` · <a href="mailto:${BSD.esc(alderman.email)}" style="color: inherit;">${BSD.esc(alderman.email)}</a>`;
      }
    } else {
      const lookup = (aldemenData && aldemenData.lookup_url) || BSD.LINKS.aldermanLookup;
      who = `<a href="${BSD.esc(lookup)}" target="_blank" rel="noopener" style="color: inherit;">Find your alderperson →</a>`;
    }
    let meta = `${who} · Crash data Sep 2017 – ${BSD.esc(crashDataEndLabel(entry))}`;
    if (metaData && metaData.generated_at) {
      meta += ` · report built ${BSD.esc(fmtDate(metaData.generated_at))}`;
    }
    return `<header class="report-head">` +
      `<span class="report-kicker">Performance report</span>` +
      `<h2 style="margin: .1rem 0;">Ward ${BSD.esc(String(ward))}</h2>` +
      `<p class="report-meta">${meta}</p>` +
      `</header>`;
  }

  // ---- Crashes & complaints section ----

  // City median of the wards' latest trailing-12-month crash counts.
  function cityMedianRecentCrashes() {
    if (!safetyIndexData || !Array.isArray(safetyIndexData.wards)) return null;
    const vals = safetyIndexData.wards
      .filter(w => w.windows && w.windows.recent_12mo && w.windows.recent_12mo.crashes != null)
      .map(w => w.windows.recent_12mo.crashes)
      .sort((a, b) => a - b);
    if (!vals.length) return null;
    const mid = Math.floor(vals.length / 2);
    return vals.length % 2 ? vals[mid] : (vals[mid - 1] + vals[mid]) / 2;
  }

  function crashSectionHTML(ward, entry) {
    const wardData = getWardData(ward);
    let html = sectionHeadingHTML("Crashes & complaints", "real");

    // Chart first: trailing-12-month crashes vs the city median, with
    // serious/fatal months dotted on the baseline.
    if (entry && Array.isArray(entry.monthly) && entry.monthly.length >= 13) {
      const points = BSD.rollingSums(entry.monthly, "crashes", 12);
      const dots = entry.monthly
        .filter(m => (m.ksi || 0) > 0 || (m.fatal || 0) > 0)
        .map(m => ({ month: m.month, count: m.ksi || m.fatal || 0, kind: "serious/fatal" }));
      const svg = BSD.trendChartSVG(points, {
        label: `Ward ${ward} cyclist crashes, trailing 12 months`,
        median: cityMedianRecentCrashes(),
        dots,
      });
      if (svg) {
        html += `<div style="max-width: 560px;">${svg}</div>` +
          `<div class="muted" style="font-size: .8rem; margin-bottom: .6rem;">` +
          `Cyclist crashes per trailing 12 months · dots mark months with a death or serious injury</div>`;
      }
    }

    const win = entry && entry.windows;
    const totalAllTime = (entry && entry.cyclist_crashes != null)
      ? entry.cyclist_crashes
      : (wardData ? wardData.cyclist_crashes : null);

    html += `<div class="kv-list">`;
    if (win && win.recent_12mo) {
      const trend = entry.crash_trend ? ` ${BSD.trendHTML(entry.crash_trend)}` : "";
      html += `<div>Cyclist crashes: <span class="stat" style="font-size: 1.4rem;">${BSD.fmt(win.recent_12mo.crashes)}</span> in the last 12 months${trend}</div>`;
      if (totalAllTime != null) {
        html += `<div class="muted">${BSD.fmt(totalAllTime)} total since Sept 2017</div>`;
      }
      html += `<div>Serious injuries (12 mo): ${BSD.fmt(win.recent_12mo.ksi)} · Deaths (12 mo): ${BSD.fmt(win.recent_12mo.fatal)}</div>`;
    } else if (wardData) {
      // Old data files carry only all-time totals — label the window, never
      // show an unlabeled number.
      html += `<div>Cyclist crashes: <span class="stat" style="font-size: 1.4rem;">${BSD.fmt(wardData.cyclist_crashes)}</span> since Sept 2017</div>`;
      html += `<div>Injury crashes: ${BSD.fmt(wardData.injuries)} · Deaths: ${BSD.fmt(wardData.fatalities)} (both since Sept 2017)</div>`;
    } else {
      html += `<div class="muted">No crash data for this ward in the current pull.</div>`;
    }

    const complaints311 = get311ComplaintsForWard(ward) || 0;
    html += `<div>311 bike complaints: ${BSD.fmt(complaints311)} <span class="muted">(all requests on record)</span> ${BSD.badgeHTML("proxy")}</div>`;
    html += `</div>`;
    return html;
  }

  // ---- Coming up in Ward {N} section ----
  function upcomingSectionHTML(ward, aldermanName, upcoming) {
    let html = sectionHeadingHTML(`Coming up in Ward ${ward}`, "real");

    // Legacy pulls have no structured meetings — link out, never fabricate.
    if (hearingsData && hearingsData.structured_data_available === false) {
      const committees = Array.isArray(hearingsData.committees) ? hearingsData.committees : [];
      html += `<div class="kv-list">`;
      committees.forEach(c => {
        html += `<div><a href="${BSD.esc(c.calendar_url)}" target="_blank" rel="noopener">${BSD.esc(c.committee)}</a>` +
          `<div class="muted" style="font-size: .85rem;">Live calendar — no structured feed available yet.</div></div>`;
      });
      if (!committees.length) {
        html += `<div class="muted">No committee hearing data in the current pull.</div>`;
      }
      html += `</div>`;
      return html;
    }

    const meetings = upcoming.meetings;
    const introduced = upcoming.introduced;

    if (!meetings.length && !introduced.length) {
      const fallbackCal = (hearingsData && Array.isArray(hearingsData.committees) &&
        hearingsData.committees[0] && hearingsData.committees[0].calendar_url) ||
        "https://chicityclerkelms.chicago.gov/Meetings";
      html += `<p class="muted">Nothing scheduled for the safety committees right now — ` +
        `<a href="${BSD.esc(fallbackCal)}" target="_blank" rel="noopener">check the official calendar</a>.</p>`;
      return html;
    }

    if (meetings.length) {
      html += `<div class="kv-list">`;
      meetings.forEach((m, i) => {
        const shortName = String(m.committee || "").replace(/^Committee on /, "");
        html += `<div>${BSD.esc(fmtMonthDay(m.date))} · ${BSD.esc(shortName)}`;
        if (m.agenda_url) {
          html += ` · <a href="${BSD.esc(m.agenda_url)}" target="_blank" rel="noopener">Agenda (PDF)</a>`;
        }
        html += ` · <button type="button" class="btn" data-ics="${i}">Add to calendar</button></div>`;
        if (m.comment) {
          html += `<div class="fine-print">${BSD.esc(m.comment)}</div>`;
        }
      });
      html += `</div>`;
    }

    if (introduced.length) {
      const byWhom = aldermanName ? `by ${aldermanName}` : `for Ward ${ward}`;
      html += `<div class="muted" style="margin-top: .8rem; font-weight: 600;">Recently introduced ${BSD.esc(byWhom)}</div>`;
      html += `<div class="kv-list">`;
      introduced.forEach(rec => {
        const date = rec.intro_date ? fmtDate(rec.intro_date) : "—";
        const title = rec.url
          ? `<a href="${BSD.esc(rec.url)}" target="_blank" rel="noopener">${BSD.esc(rec.title)}</a>`
          : BSD.esc(rec.title);
        html += `<div>${BSD.esc(date)} · ${title} · ${BSD.esc(rec.status)}</div>`;
      });
      html += `</div>`;
    }

    return html;
  }

  // ---- Safety scorecard section ----
  function scorecardSectionHTML(ward) {
    const result = getSafetyIndexForWard(safetyIndexData, ward);
    let html = sectionHeadingHTML("Safety scorecard", "derived");

    if (!result) {
      html += `<p class="muted">No safety index data for this ward in the current pull.</p>`;
      return html;
    }

    const { entry, rank, total } = result;
    const score = entry.comparable_danger_score;
    const scoreDisplay = score == null ? "—" : `${BSD.esc(score)} / 100`;
    html += `<div>Danger score: <span class="stat" style="color: ${BSD.scoreColor(score)};">${scoreDisplay}</span> <span class="muted">(vs other wards — higher is worse)</span></div>`;
    html += `<div class="muted" style="margin-bottom: .6rem;">Rank ${BSD.fmt(rank)} of ${BSD.fmt(total)} wards</div>`;

    html += `<div class="kv-list">`;
    html += `<div><strong>Crashes per 10k population:</strong> ${BSD.fmt(entry.crashes_per_10k_pop)} <span class="muted">(since Sept 2017)</span></div>`;
    html += `<div><strong>Crashes per bikeway mile:</strong> ${BSD.fmt(entry.crashes_per_bikeway_mile)} <span class="muted">(since Sept 2017)</span></div>`;
    html += `<div><strong>Bikeway miles:</strong> ${BSD.fmt(entry.bikeway_miles)} <span class="muted">(current network)</span></div>`;
    html += `<div><strong>Population:</strong> ${BSD.fmt(entry.population)}</div>`;
    if (entry.crash_trend) {
      html += `<div><strong>Crash trend:</strong> ${BSD.trendHTML(entry.crash_trend)}</div>`;
    }
    html += `</div>`;

    if (!entry.infra_growth_trend) {
      html += `<div class="muted" style="margin-top: .6rem;">Infrastructure growth: needs two pipeline snapshots — check back after the next refresh.</div>`;
    } else {
      const g = entry.infra_growth_trend;
      const pctStr = g.pct_growth == null ? "—" : `${g.pct_growth > 0 ? "+" : ""}${g.pct_growth}%`;
      html += `<div class="muted" style="margin-top: .6rem;">Infrastructure growth: +${BSD.fmt(g.miles_added)} mi (${pctStr}) since ${BSD.esc(g.since)}.</div>`;
    }

    return html;
  }

  // ---- Alderperson record section ----
  function aldermanRecordSectionHTML(ward) {
    const { matched, aldermanName } = getSponsorRecordsForWard(aldermenSafetyData, aldemenData, ward);
    let html = sectionHeadingHTML("Alderperson record", "derived");

    if (matched) {
      html += `<div><span class="stat">${BSD.fmt(matched.safety_sponsorships)}</span> <span class="muted">tagged bike/traffic-safety sponsorships (all records on file)</span></div>`;
      // Loud, not a footnote (P6b): presenting sponsorship as a voting record
      // is the exact error that burns advocates in front of an alderperson.
      html += `<div class="notice" style="margin:.4rem 0;">Sponsorships are <strong>not votes</strong> — ` +
        `most safety measures pass by voice vote with no individual record.</div>`;

      const noVotes = matched.recorded_no_votes ?? 0;
      if (noVotes > 0) {
        html += `<div>Recorded "no" votes on tagged measures: ` +
          `<strong style="color: var(--sev-incap);" title="Times this alderperson appears in a contested roll-call's no_voters list — rare; most measures pass by voice vote">${BSD.fmt(noVotes)}</strong></div>`;
      } else {
        html += `<div>Recorded "no" votes on tagged measures: ${BSD.fmt(noVotes)}</div>`;
      }

      const records = Array.isArray(matched.records) ? matched.records.slice(0, 5) : [];
      if (records.length) {
        html += `<div class="kv-list" style="margin-top: .6rem;">`;
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
      html += `<p>No sponsorship records match this ward's alderperson yet — sponsor names are matched exactly, never guessed.</p>`;
      if (!aldermanName) {
        const lookup = (aldemenData && aldemenData.lookup_url) || BSD.LINKS.aldermanLookup;
        html += `<p><a href="${BSD.esc(lookup)}" target="_blank" rel="noopener">Official alderperson lookup →</a></p>`;
      }
    }

    return html;
  }

  // ---- Menu-fund spending section ----
  function menuSpendingSectionHTML(ward) {
    const spend = getMenuSpendingForWard(menuSpendingData, ward);
    let html = sectionHeadingHTML("Menu-fund spending", "proxy");

    if (!spend) {
      html += `<p class="muted">No menu-spending data for this ward in the current pull.</p>`;
    } else {
      html += `<div><span class="stat">${BSD.esc(BSD.money(spend.bike_safety_spent))}</span> <span class="muted">on bike/traffic-calming items</span></div>`;
      html += `<div class="muted">of ${BSD.esc(BSD.money(spend.total_spent))} total menu spending (${BSD.fmt(spend.items)} items, all years on record)</div>`;
    }

    return html;
  }

  // ---- Provenance modal ----
  function provenanceBodyHTML(ward) {
    const result = getSafetyIndexForWard(safetyIndexData, ward);
    const entry = result ? result.entry : null;
    const win = entry && entry.windows;
    const crashWindow = win && win.window_end
      ? `Window: 12 months ending ${fmtDate(win.window_end)}.`
      : "Window: since Sept 2017.";
    const per10k = entry ? BSD.fmt(entry.crashes_per_10k_pop) : "—";
    const perMile = entry ? BSD.fmt(entry.crashes_per_bikeway_mile) : "—";
    const rosterAsOf = aldemenData && aldemenData.as_of
      ? ` as of ${fmtDate(aldemenData.as_of)}` : "";

    const dd = (text, srcId) =>
      `<dd style="margin: 0 0 .7rem;">${text} ` +
      `<a href="sources.html#src-${srcId}">Source detail →</a></dd>`;

    let html = `<dl style="margin: 0;">`;
    html += `<dt><strong>Cyclist crashes / injuries / deaths</strong> — real · from official records</dt>`;
    html += dd(`Chicago Police crash reports via the Chicago Data Portal. Recent months are provisional; dooring is structurally undercounted. ${BSD.esc(crashWindow)}`, "crashes");

    html += `<dt><strong>Danger score</strong> — derived · calculated by us</dt>`;
    html += dd(`Formula: average of this ward's percentile ranks on crashes per 10k residents (${per10k}) and crashes per bikeway mile (${perMile}). A relative ranking across wards, not absolute risk.`, "ward_safety_index");

    html += `<dt><strong>311 bike complaints</strong> — proxy · a related signal</dt>`;
    html += dd(`Counts who complains, not conditions; biased toward wards with engaged 311 users.`, "sr311");

    html += `<dt><strong>Coming up / meetings</strong> — real · City Clerk eLMS public API</dt>`;
    html += dd(`Best-effort weekly pull from an undocumented API; verify against the official calendar before attending.`, "hearings");

    html += `<dt><strong>Current alderperson</strong> — real · city Ward Offices roster</dt>`;
    html += dd(`The city's own roster${BSD.esc(rosterAsOf)}; vacant seats appear as a lookup link, never a guessed name.`, "aldermen");

    html += `<dt><strong>Alderperson record</strong> — derived · calculated by us</dt>`;
    html += dd(`Counts council records whose sponsor name exactly matches this ward's alderperson. Coverage: ${BSD.esc(COVERAGE_NOTICE)}`, "aldermen_safety_record");

    html += `<dt><strong>Menu-fund spending</strong> — proxy · a related signal</dt>`;
    html += dd(`Ward Wise volunteer project structuring the city's PDF reports; not independently verified.`, "menu_spending");
    html += `</dl>`;

    html += `<p class="fine-print">Check the math yourself: ` +
      `<a href="data/ward_safety_index.json" download>download ward_safety_index.json</a> — ` +
      `every input above is in this ward's row.</p>`;
    return html;
  }

  // ---- Report assembly ----
  function buildWardReport(ward) {
    const result = getSafetyIndexForWard(safetyIndexData, ward);
    const entry = result ? result.entry : null;
    const alderman = getAldermanForWard(ward);
    const aldermanName = alderman && alderman.alderman ? alderman.alderman : null;
    const upcoming = getUpcomingForWard(hearingsData, councilData, aldermanName, ward, todayISO());

    const section = document.createElement("section");
    section.className = "report";
    section.id = "ward-report";
    section.innerHTML =
      reportHeadHTML(ward, entry) +
      `<div class="report-section">${crashSectionHTML(ward, entry)}</div>` +
      `<div class="report-section">${upcomingSectionHTML(ward, aldermanName, upcoming)}</div>` +
      `<div class="report-section">${scorecardSectionHTML(ward)}</div>` +
      `<div class="report-section">${aldermanRecordSectionHTML(ward)}</div>` +
      `<div class="report-section">${menuSpendingSectionHTML(ward)}</div>` +
      `<footer class="report-foot">` +
      `<a class="btn primary" href="ward.html?ward=${encodeURIComponent(ward)}">Printable one-pager →</a> ` +
      `<button type="button" class="linklike" id="ward-provenance">Where does this data come from?</button>` +
      `</footer>`;

    // Add-to-calendar buttons (delegating per-report keeps indices aligned
    // with the upcoming.meetings array this report was built from).
    section.querySelectorAll("button[data-ics]").forEach(btn => {
      btn.addEventListener("click", () => {
        const m = upcoming.meetings[Number(btn.dataset.ics)];
        if (!m) return;
        const shortName = String(m.committee || "meeting").replace(/^Committee on /, "");
        const filename = `${shortName.replace(/[^A-Za-z0-9]+/g, "-")}-${String(m.date).slice(0, 10)}.ics`;
        BSD.downloadICS(filename, BSD.icsForEvent({
          title: `${m.committee} — City Council`,
          startISO: m.date,
          location: m.location || "",
          url: m.agenda_url || m.calendar_url || "",
          description: m.comment || "",
        }));
      });
    });

    section.querySelector("#ward-provenance").addEventListener("click", () => {
      BSD.openModal({
        title: `Ward ${ward} report — where the data comes from`,
        bodyHTML: provenanceBodyHTML(ward),
      });
    });

    return section;
  }

  function renderWardReport(ward, slot) {
    const existing = document.getElementById("ward-report");
    const report = buildWardReport(ward);
    if (existing) existing.replaceWith(report);
    else slot.appendChild(report);
  }

  function clearWardReport() {
    const existing = document.getElementById("ward-report");
    if (existing) existing.remove();
  }

  // ---- Citywide hearings card (ward-independent) ----
  function buildHearingsCard() {
    const card = document.createElement("div");
    card.className = "card hearings-card";

    let html = sectionHeadingHTML("Upcoming committee hearings (citywide)", "real");

    const committees = (hearingsData && Array.isArray(hearingsData.committees)) ? hearingsData.committees : [];
    if (!committees.length) {
      html += `<p class="muted">No committee hearing data in the current pull.</p>`;
    } else if (hearingsData.structured_data_available === false) {
      html += `<div class="kv-list">`;
      committees.forEach(c => {
        html += `<div><a href="${BSD.esc(c.calendar_url)}" target="_blank" rel="noopener">${BSD.esc(c.committee)}</a>`;
        html += `<div class="muted" style="font-size: 0.85rem;">Live calendar — no structured feed available yet.</div></div>`;
      });
      html += `</div>`;
    } else {
      html += `<div class="kv-list">`;
      committees.forEach(c => {
        html += `<div><strong>${BSD.esc(c.committee)}</strong>`;
        const meetings = Array.isArray(c.meetings) ? c.meetings : [];
        if (!meetings.length) {
          html += `<div class="muted" style="font-size: 0.85rem;">No meetings currently scheduled — ` +
            `<a href="${BSD.esc(c.calendar_url)}" target="_blank" rel="noopener">official calendar</a>.</div>`;
        } else {
          meetings.forEach(m => {
            html += `<div>${BSD.esc(fmtMonthDay(m.date))}`;
            if (m.location) html += ` · ${BSD.esc(m.location)}`;
            if (m.agenda_url) html += ` · <a href="${BSD.esc(m.agenda_url)}" target="_blank" rel="noopener">Agenda (PDF)</a>`;
            html += `</div>`;
          });
        }
        html += `</div>`;
      });
      html += `</div>`;
    }

    if (hearingsData && hearingsData.note) {
      html += `<div class="fine-print">${BSD.esc(hearingsData.note)}</div>`;
    }

    card.innerHTML = html;
    return card;
  }

  async function render() {
    BSD.initPage("action.html");
    const app = document.getElementById("app");

    try {
      await loadAllData();

      const heading = document.createElement("div");
      heading.innerHTML = `<h1>Take Action</h1>` +
        `<p style="color: var(--ink-soft);">Evidence for your next email, public comment, or ward-night question.</p>`;
      app.appendChild(heading);

      // (2) Ward picker for the performance report.
      const pickerSection = document.createElement("section");
      pickerSection.innerHTML = `<h2>Get your ward's performance report</h2>` +
        `<p style="color: var(--ink-soft);">Pick your ward for local crash trends, what's coming up at City Hall, and your alderperson's record.</p>`;
      app.appendChild(pickerSection);

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

      selectContainer.appendChild(select);
      app.appendChild(selectContainer);

      // (3) The report renders directly below the picker, swapped in place.
      const reportSlot = document.createElement("div");
      reportSlot.id = "ward-report-slot";
      app.appendChild(reportSlot);

      select.addEventListener("change", function () {
        const ward = this.value;
        if (ward) {
          BSD.setParams({ ward: ward });
          renderWardReport(ward, reportSlot);
        } else {
          BSD.setParams({ ward: null });
          clearWardReport();
        }
      });

      if (initialWard) {
        renderWardReport(initialWard, reportSlot);
      }

      // (4) Report-it-directly links.
      const reportSection = document.createElement("section");
      reportSection.className = "section-gap";
      reportSection.innerHTML = `<h2>See a problem? Report it directly</h2>` +
        `<p style="color: var(--ink-soft);">This dashboard is an evidence layer, not a collection layer — submit to the systems that investigate and act.</p>`;
      app.appendChild(reportSection);

      const reportCards = document.createElement("div");
      reportCards.className = "cards-grid";

      const card311 = document.createElement("a");
      card311.href = BSD.LINKS.threeOneOne;
      card311.target = "_blank";
      card311.rel = "noopener";
      card311.className = "card card-link";
      card311.innerHTML = `<h3 style="margin-top: 0; color: var(--accent);">311 — City Service Requests</h3>` +
        `<p>Hazards, broken signals, debris, potholes — report infrastructure problems to the city.</p>`;
      reportCards.appendChild(card311);

      const cardBLU = document.createElement("a");
      cardBLU.href = BSD.LINKS.blu;
      cardBLU.target = "_blank";
      cardBLU.rel = "noopener";
      cardBLU.className = "card card-link";
      cardBLU.innerHTML = `<h3 style="margin-top: 0; color: var(--accent);">Bike Lane Uprising</h3>` +
        `<p>Photo-report blocked bike lanes and build the advocacy evidence base.</p>`;
      reportCards.appendChild(cardBLU);

      app.appendChild(reportCards);

      // (5) Citywide hearings card last.
      const hearingsSection = document.createElement("section");
      hearingsSection.className = "section-gap";
      app.appendChild(hearingsSection);
      app.appendChild(buildHearingsCard());

      // (6) Closing line.
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
