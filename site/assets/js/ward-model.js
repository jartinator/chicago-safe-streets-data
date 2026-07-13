/* Pure model for the printable ward one-pager (ward.html). No DOM, no BSD —
 * takes loaded JSON as arguments, Node-testable (tests/ui/ward-model.test.js).
 * Research basis: REPORT-ux-proposal.md P3 — six of nine study personas
 * independently described this artifact ("my Wednesday-before-Thursday-
 * meeting document"). */
(function () {
  // Bbox of any GeoJSON geometry (ported from map.js — kept local so this
  // module stays dependency-free).
  function bboxOf(geom) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    const scan = c => {
      if (typeof c[0] === "number") {
        if (c[0] < minX) minX = c[0]; if (c[0] > maxX) maxX = c[0];
        if (c[1] < minY) minY = c[1]; if (c[1] > maxY) maxY = c[1];
      } else c.forEach(scan);
    };
    scan(geom.coordinates);
    return [minX, minY, maxX, maxY];
  }

  // Top corridors whose segments' bboxes overlap the ward's bbox, ranked by
  // crashes near the bikeway (same heuristic as the map's ward panel — an
  // overlap screen, not a strict clip; label output "in/near this ward").
  function topCorridorsForWard(wardFeature, routeFeatures, n) {
    if (!wardFeature || !Array.isArray(routeFeatures)) return [];
    const b = bboxOf(wardFeature.geometry);
    const streets = {};
    routeFeatures.forEach(rf => {
      const [minX, minY, maxX, maxY] = bboxOf(rf.geometry);
      if (maxX < b[0] || minX > b[2] || maxY < b[1] || minY > b[3]) return;
      const s = rf.properties.street || "(unnamed)";
      (streets[s] = streets[s] || { street: s, crashes: 0, length_m: 0 });
      streets[s].crashes += rf.properties.crashes_within_30m || 0;
      streets[s].length_m += rf.properties.length_m || 0;
    });
    return Object.values(streets)
      .sort((a, z) => z.crashes - a.crashes)
      .slice(0, n || 3);
  }

  // Next upcoming meeting across all committees (hearings.json), or null.
  // Skips legacy pulls with no structured data rather than fabricating.
  function nextMeeting(hearingsData, todayISO) {
    if (!hearingsData || hearingsData.structured_data_available === false ||
        !Array.isArray(hearingsData.committees)) return null;
    const today = todayISO ? String(todayISO).slice(0, 10) : null;
    let best = null;
    hearingsData.committees.forEach(c => {
      (Array.isArray(c.meetings) ? c.meetings : []).forEach(m => {
        if (!m || !m.date) return;
        const d = String(m.date).slice(0, 10);
        if (today && d < today) return;
        if (!best || d < String(best.date).slice(0, 10)) {
          best = { date: m.date, committee: c.committee, comment: m.comment || null,
                   agenda_url: m.agenda_url || null, location: m.location || null,
                   agenda_items: Array.isArray(m.agenda_items) ? m.agenda_items : null,
                   agenda_amended: !!m.agenda_amended };
        }
      });
    });
    return best;
  }

  // News items matched to this ward (news_items.json; pipeline computes
  // matches, each entry carrying its auditable `via` — this only filters and
  // caps, preserving the file's newest-first order).
  function newsForWard(newsData, ward, max) {
    if (!newsData || !Array.isArray(newsData.items)) return [];
    const wardStr = String(ward);
    return newsData.items
      .filter(item => item && item.matches && Array.isArray(item.matches.wards) &&
        item.matches.wards.some(w => w && String(w.ward) === wardStr))
      .slice(0, max == null ? 5 : max)
      .map(item => ({ title: item.title, url: item.url,
                      source: item.source || null, published: item.published }));
  }

  // Assemble everything the one-pager renders, from already-loaded JSON.
  // Every field is null-safe: the artifact renders honestly with gaps rather
  // than failing or inventing (missing data shows as "no data", never 0).
  function buildOnePager(inputs, ward, todayISO) {
    const wardStr = String(ward);
    const {
      safetyIndexData, aldermenData, wardsData, routesData,
      hearingsData, menuData, metaData, newsData,
    } = inputs || {};

    let entry = null, rank = null, total = null;
    if (safetyIndexData && Array.isArray(safetyIndexData.wards)) {
      const idx = safetyIndexData.wards.findIndex(w => w.ward === wardStr);
      if (idx !== -1) {
        entry = safetyIndexData.wards[idx];
        rank = idx + 1;
        total = safetyIndexData.wards.length;
      }
    }

    let alderman = null;
    if (aldermenData && Array.isArray(aldermenData.wards)) {
      alderman = aldermenData.wards.find(w => w.ward === wardStr) || null;
    }

    const wardFeature = wardsData && Array.isArray(wardsData.features)
      ? wardsData.features.find(f => f.properties && f.properties.ward === wardStr) || null
      : null;

    const win = entry && entry.windows;
    const menuEntry = menuData && menuData.wards ? menuData.wards[wardStr] || null : null;

    return {
      ward: wardStr,
      asOf: metaData && metaData.generated_at ? String(metaData.generated_at).slice(0, 10) : null,
      alderman: alderman && alderman.alderman
        ? { name: alderman.alderman, email: alderman.email || null, phone: alderman.phone || null }
        : null,
      windows: win ? {
        window_end: win.window_end || null,
        recent: win.recent_12mo || null,
        prior: win.prior_12mo || null,
      } : null,
      totalSince2017: entry && entry.cyclist_crashes != null ? entry.cyclist_crashes
        : (wardFeature ? wardFeature.properties.cyclist_crashes : null),
      concern: entry && entry.comparable_danger_score != null
        ? { score: entry.comparable_danger_score, rank, total } : null,
      pctProtected: entry && entry.bikeway_pct_protected != null ? entry.bikeway_pct_protected : null,
      pctRoads: entry && entry.bikeway_pct_of_roads != null ? entry.bikeway_pct_of_roads : null,
      bikewayMiles: entry && entry.bikeway_miles != null ? entry.bikeway_miles : null,
      topCorridors: topCorridorsForWard(wardFeature, routesData && routesData.features, 3),
      nextMeeting: nextMeeting(hearingsData, todayISO),
      news: newsForWard(newsData, wardStr, 5),
      menuBikeSpent: menuEntry ? (menuEntry.bike_safety_spent ?? 0) : null,
      menuTotalSpent: menuEntry ? menuEntry.total_spent : null,
    };
  }

  const api = { bboxOf, topCorridorsForWard, nextMeeting, newsForWard, buildOnePager };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.BSDWard = api;
})();
