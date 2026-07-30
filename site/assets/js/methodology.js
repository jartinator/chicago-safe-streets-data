/* Methods page: how every derived number is computed, in recitable form.
 * Research finding behind this page: users won't cite a number they can't
 * defend out loud against a hostile question — the methodology must be one
 * click from every derived stat (docs/research/user-needs/REPORT-ux-proposal.md, P5). */
(function () {
  // Exported for tests: every section needs a unique id, a title, and body HTML.
  const SECTIONS = [
    {
      id: "ward-index",
      title: "Ward concern rank (formerly “danger score”)",
      html:
        `<p>The 0–100 <strong>concern rank</strong> blends each ward's percentile rank on two
        component rates: <strong>crashes per 10,000 residents</strong> (population from the ACS
        5-year survey) and <strong>crashes per bikeway mile</strong> (CDOT bikeway geometry clipped
        to the ward). The blend is the average of the two percentile ranks. Both components are
        published as their own columns on the Explore Data page and in the CSV export — the
        components matter more than the blend: a ward can rank high because riders face
        exposure-adjusted danger, or because it simply has almost no bikeway miles. Those are
        different policy problems.</p>
        <p><strong>Higher = worse. Relative, not absolute:</strong> the rank compares wards to each
        other in this data. It is not a probability of harm, and it is not severity-weighted like
        CDOT's High Injury Network (which weights fatal and serious-injury crashes over a 3-year
        window). Wards missing population or bikeway data get no score and sort after every scored
        ward.</p>
        <p>Crash trends compare the trailing 365 days to the prior 365 days. Per-ward
        <em>trend</em> windows anchor to that ward's latest crash date; the comparable
        <em>windows</em> fields anchor to the global latest crash date so wards can be compared
        directly.</p>`,
    },
    {
      id: "severity",
      title: "Severity definitions (injury, KSI)",
      html:
        `<p><strong>Injury crashes</strong> are crashes whose most-severe injury is fatal,
        incapacitating, or non-incapacitating. <strong>KSI</strong> (“killed or seriously
        injured”) counts fatal + incapacitating only. These match the fields in the city's
        crash records; they are crash-level (most severe injury in the crash), not per-person
        counts. Recent months are provisional — crash records get amended upstream.</p>`,
    },
    {
      id: "coverage",
      title: "Street coverage denominators",
      html:
        `<p>“% of streets with bike infrastructure” divides bikeway centerline miles by
        <strong>3,945 miles of surface streets</strong>: the city Street Center Lines dataset
        filtered to arterials, collectors, and locals — expressways, ramps, alleys, and river
        channels excluded. “% protected” is the share of <em>on-street</em> bikeway miles
        that are physically protected lanes. Off-street trails are excluded from both sides of
        every street ratio (trails aren't roads). All lengths are projected centerline miles
        (EPSG:26916), so numerator and denominator are method-consistent.</p>`,
    },
    {
      id: "facilities",
      title: "Facility categories",
      html:
        `<p>CDOT's raw facility labels are mapped to seven categories: protected, buffered,
        painted, neighborhood greenway, shared-lane marking (sharrow), off-street trail, and
        other/unknown. The exact mapping lives in <code>pipeline/config.py</code>
        (<code>FACILITY_CATEGORY_MAP</code>) and is applied identically everywhere. Main-route
        report cards grade these into four tiers: off-street &gt; protected &gt; painted
        (buffered/painted/greenway) &gt; none (sharrow/other). The published CDOT layer carries
        no install dates, so facility history is built forward from dated snapshots — it
        cannot be backfilled.</p>`,
    },
    {
      id: "exposure",
      title: "What each source misses",
      html:
        `<p>No public cyclist-volume data is joined yet, so <strong>crash counts are raw, not
        ridership-normalized</strong>: a busy street can look worse than a dangerous quiet one.
        Every source here has a known blind spot — absence of data is not absence of harm:</p>
        <ul>
          <li><strong>Police crash records</strong> only include “reportable” crashes
          (injury or &gt;$1,500 damage). Dooring is structurally undercounted. Research also finds
          police reports systematically miss lower-severity crashes and undercount Black and
          Hispanic victims.</li>
          <li><strong>311 complaints</strong> track who reports, not just what happens: studies of
          Chicago-style 311 systems find lower reporting rates in lower-income and majority-Black
          and -Latino areas even when conditions are worse. Few complaints ≠ few problems.</li>
          <li><strong>Camera violations</strong> exist only where cameras are, and Chicago's
          cameras ticket South and West Side ZIP codes at roughly twice the rate of white ZIP
          codes — treat as an enforcement pattern, not a neutral safety signal.</li>
          <li><strong>Crowdsourced layers</strong> (trails, mellow routes) reflect who maps, and
          vary in completeness by neighborhood.</li>
          <li><strong>Divvy trip counts</strong> (ward pages) are Divvy bike-share trips only, not all
          cycling, and station placement skews toward downtown and the North Side — a low ward count can
          mean fewer nearby stations, not less riding. Never divided by, or dividing, crash counts.</li>
        </ul>`,
    },
    {
      id: "differences",
      title: "If our numbers differ from ATA's letter or CDOT's reports",
      html:
        `<p>Advocacy ward letters, CDOT annual reports, and this site can all be “right”
        and still disagree. The usual reasons, in order of likelihood:</p>
        <ul>
          <li><strong>Different time windows</strong> — calendar years vs. our trailing-365-day
          windows vs. CDOT's 3-year HIN windows.</li>
          <li><strong>Different severity definitions</strong> — “serious injuries”
          sometimes includes non-incapacitating injuries; our KSI does not.</li>
          <li><strong>Ward boundary vintage</strong> — everything here uses the 2023 remap.
          Numbers computed on pre-2023 boundaries will differ for many wards.</li>
          <li><strong>Located crashes only</strong> — we count crashes that geocode inside a
          ward; citywide reports may include unlocated records.</li>
          <li><strong>Provisional records</strong> — recent months get amended upstream, so two
          pulls weeks apart can differ.</li>
        </ul>
        <p>If a number still doesn't reconcile after checking these, please
        <a href="https://github.com/jartinator/chicago-safe-streets-data/issues/new" target="_blank" rel="noopener">open an issue</a> —
        an unexplained mismatch is a bug.</p>`,
    },
    {
      id: "freshness",
      title: "Freshness, exports, and screenshots",
      html:
        `<p>Data refreshes weekly via a human-reviewed pipeline run; every page footer shows the
        last refresh date, and recent months are provisional. <strong>CSV exports begin with
        “#” comment lines</strong> carrying the dataset name, tier, as-of date, and key
        caveat — strip lines starting with <code>#</code> when parsing. Findings cards carry
        their own as-of line so screenshots stay attributable. On Your Left! publishes no
        obstruction data — see a blocked bike lane? report it at
        <a href="https://www.bikelaneuprising.com" target="_blank" rel="noopener">Bike Lane Uprising</a>.</p>`,
    },
  ];

  function render() {
    if (typeof document === "undefined") return;
    BSD.initPage("methodology.html");
    const app = document.getElementById("app");

    const parts = [
      `<h1>How the numbers are computed</h1>`,
      `<p>Everything you might cite from this site, in defensible form: what was counted, over
      what window, divided by what, and what each source misses. Where the data comes from is on
      the <a href="sources.html">Sources page</a>; this page is the math and the caveats.</p>`,
      `<nav class="chip-toc">` +
        SECTIONS.map(s => `<a href="#${s.id}">${BSD.esc(s.title)}</a>`).join("") +
      `</nav>`,
      ...SECTIONS.map(s =>
        `<section class="card" id="${s.id}"><h2>${BSD.esc(s.title)}</h2>${s.html}</section>`),
    ];
    app.innerHTML = parts.join("\n");
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { SECTIONS };
  } else {
    render();
  }
})();
