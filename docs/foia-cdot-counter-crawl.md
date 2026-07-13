# CDOT bicycle count data — reference crawl for the next FOIA

*Method: six parallel research agents crawled public sources per
`docs/research/followups/agent-research-crawl-foia.md` (targeted
reference-finding, no deep PDF reading), July 2026. **Caveat:** direct
fetches to chicago.gov / data.cityofchicago.org / streetsblog and several
other domains were proxy-blocked (403) in the research environment, so
citations rest on search-indexed snippets. Every artifact's existence and
URL was corroborated across queries, but verify quotes/page contents by
opening the URLs before filing.*

## What we now know (the shape of CDOT's count data)

1. **CDOT has held bicycle count data since at least 2009, on the record.**
   Its own Feb 25, 2011 news release describes a **Bicycle Count Study**
   using automated pneumatic tube counters at **26 locations citywide**
   (24-hour Tue/Wed/Thu counts, summer/fall 2009; peak >3,000 cyclists/day
   at 640 N Milwaukee), run by the CDOT Bicycle Program under **Ben
   Gomberg**, tied to the Bike 2015 Plan's count-gathering goal.
2. **Manual/volunteer counts continued through the 2010s**: a spring 2015
   weekday AM-rush count of 543 riders at Chicago/Wells; volunteer counts
   showing cyclists >40% of summer rush trips on Milwaukee (2015 coverage,
   CDOT spokesman Mike Claffey responding).
3. **The Chicago/Wells Eco-Counter (Dec 2022) is developer-funded** (AMLI,
   SVP Jennifer Wolf quoted on making the data public) with CDOT involved
   in siting/approval — so the *raw feed* may live with AMLI/Eco-Counter,
   and the CDOT-FOIA-able records are the correspondence, agreements, and
   any data shared with the city. Eco-Counter's public display map lists
   the counter (site 300037197) but — checked 2026-07-13 — shows "last
   published data 2/17/2026" and no accessible history: the feed went dark
   after ~26 months and the public page is a dead end, so the data path is
   CDOT records (FOIA item 3) or AMLI/Eco-Counter directly. A second counter (Eco-Totem, 1237 N
   Milwaukee, developer LG paying $30k of $40k) was council-approved in
   2017 and stalled in city process — its paper trail is FOIA-able.
4. **CDOT's modern volume numbers come from Replica** (plus Divvy): the
   2024 CDOT/Replica/Sam Schwartz analysis (biking +119% 2019→2023, South
   Side +170%; **Dave Smith, CDOT Director of Complete Streets**, quoted),
   described by the Sun-Times as "sponsored by the city transportation
   department" — meaning a CDOT–Replica engagement (agreement, deliverables,
   underlying tables) exists to request.
5. **No standalone Chicago bike-count open dataset exists** on the portal
   (unlike NYC's Bicycle Counters or DC's counter dataset) — confirming the
   gap is real and the portal is the natural destination to propose.

## Draft FOIA request items (specific, artifact-anchored)

> To: CDOT FOIA Officer (see CDOT 2025 org chart; Commissioner Tom Carney)
>
> 1. The bicycle count data underlying the Chicago Department of
>    Transportation's February 25, 2011 news release "CDOT Bicycle Count
>    Study" — the location-level counts from the automated tube counters
>    deployed at 26 locations in summer/fall 2009, in spreadsheet or
>    database form if maintained.
> 2. Any subsequent CDOT bicycle count data 2010–present, including manual
>    or volunteer counts (e.g., the spring 2015 counts at Chicago Ave &
>    Wells St referenced in public reporting) and any automated counts, in
>    the form maintained.
> 3. Records of data received by CDOT from the permanent bicycle counter at
>    Chicago Ave & Wells St (installed December 2022 by AMLI with
>    Eco-Counter), and any agreement governing the counter's data.
> 4. The agreement and deliverables for the CDOT-sponsored Replica / Sam
>    Schwartz analysis of Chicago bicycling trends released May 2024
>    ("Measuring Chicago's Boost in Biking"), including underlying summary
>    tables by neighborhood and trip purpose.
> 5. The data sources and methodology behind the statement in the 2023
>    Chicago Cycling Strategy that short bike trips more than doubled
>    between 2019 and 2023.
>
> We are glad to receive whatever form is least burdensome — an export of
> the existing spreadsheet/database is preferable to any newly created
> document.

*(Item-numbering keeps each ask independently grantable; a partial response
is still a win. Log the filing in `docs/foia-log.md`.)*

## Open-data enablement blurb (attach as a closing note — optional, tested language)

> Separately from this request: if this data is something CDOT would
> consider publishing on the City's data portal on an ongoing basis (as New
> York and Washington, DC do for their bicycle counters), we would
> enthusiastically use and publicize it, and we're happy to share a short
> note on dataset structures that have worked well in other cities — as a
> resource, not a prescription. A recurring portal dataset would also spare
> your office future one-off requests like this one.

## Follow-ups this crawl surfaced (do before/alongside filing)

- **Query the FOIA Request Log – Transportation dataset (`u9qt-tv7d`)** for
  prior bike-count requests (portal was proxy-blocked during the crawl; any
  normal browser or the pipeline's Socrata client can do it). Prior grants
  = precedent to cite; prior denials = wording to avoid.
- **Search the city Contracts dataset (`rsxa-ify5`) and vcsearch** for
  "Eco-Counter" and "Replica" line items (not web-indexed; needs direct
  query).
- **Check Eco-Counter's public display map** for the Chicago/Wells counter —
  if live, the raw tallies may need no FOIA at all.
- **Open the Cycling Strategy PDF and its executive summary** for the
  footnote sourcing the trip-doubling stat (fetch was blocked; likely cites
  Replica).
- Named people worth knowing (all from public documents): Ben Gomberg
  (Bicycle Program Coordinator, 2011-era), Dave Smith (Director of Complete
  Streets), Mike Claffey (spokesman), Luann Hamilton (Deputy Commissioner,
  per a NACTO deck), Erica Schroeder (bikeway mileage tracker context),
  Commissioner Tom Carney.

---

## Full citation list (merged & ranked by six-agent crawl)

### Direct evidence

- **Streetsblog Chicago, "The wait is over! Chicago now has a bike counter at Chicago/Wells in River North" (Dec 16, 2022)**
  https://chi.streetsblog.org/2022/12/16/the-wait-is-over-chicago-now-now-has-a-bike-counter-at-chicago-wells-in-river-north
  Reports installation of Chicago's first permanent bike counter (Eco-Counter brand) at Chicago Ave & Wells St in River North, Dec 2022, purchased/installed by developer AMLI (AMLI 808 building) with CDOT involvement in siting/approval; quotes Jennifer Wolf, AMLI SVP of Development, on working with Eco-Counter to make ridership data public; also cites a CDOT count of 543 bike riders at that same intersection during a spring 2015 weekday AM rush, evidencing CDOT-held historical manual count data for the corridor.
  *Named:* Jennifer Wolf (AMLI SVP of Development)
- **Streetsblog Chicago, "Developer: Milwaukee Avenue Bike Counter Project Hit a Pothole Due to City Red Tape" (May 16, 2018)**
  https://chi.streetsblog.org/2018/05/16/developer-milwaukee-avenue-bike-counter-project-hit-a-pothole-due-to-city-red-tape
  Details a stalled 2016-2018 plan for an Eco-Totem bike counter (costing $40,000, with developer LG Partners/LG Development paying $30,000) donated for 1237 N Milwaukee Ave; City Council approved installation for spring 2017, but CDOT's closure of a slip lane at Division/Ashland/Milwaukee and a Law Department economic-disclosure requirement (after the building sold to CIM Group) stalled it.
  *Named:* Barry Howard (former LG Partners representative)
- **Streetsblog Chicago, "How a Bike Counter on Milwaukee Ave. Could Help Cure the Dooring Epidemic" (Sep 24, 2015)**
  https://chi.streetsblog.org/2015/09/24/how-a-bike-counter-on-milwaukee-ave-could-help-cure-the-dooring-epidemic
  CDOT spokesman Mike Claffey is quoted responding to a proposal for an automated bike counter on Milwaukee Ave ("We are always looking to improve our ability to collect data..."); article cites past CDOT volunteer counts showing cyclists accounted for more than 40 percent of trips on Milwaukee during summer rush hours — earliest coverage proposing the counter and establishing CDOT's manual-count baseline.
  *Named:* Mike Claffey (CDOT spokesman)
- **City of Chicago (chicago.gov), "CDOT Bicycle Count Study" news release (Feb 25, 2011)**
  https://www.chicago.gov/city/en/depts/cdot/provdrs/bike/news/2011/feb/cdot_bicycle_countstudy.html
  Official CDOT release on results of a bike-count study: CDOT Bicycle Program staff used automated pneumatic tube counters (designed to count bicycles, not motor vehicles) at 26 locations citywide, conducting 24-hour Tue/Wed/Thu counts in summer/fall 2009; results released Feb 25, 2011; highest count over 3,000 cyclists/day at 640 N Milwaukee Ave. Names Ben Gomberg, CDOT Bicycle Program Coordinator, discussing use of counts to plan future facilities and ties counts to the Bike 2015 Plan's stated goal of gathering bike counts. A CDOT Commissioner is also reportedly quoted per one search summary but the name could not be independently confirmed — verify directly against the page before citing.
  *Named:* Ben Gomberg (CDOT Bicycle Program Coordinator); unconfirmed CDOT Commissioner quote (verify before citing)
- **City of Chicago (chicago.gov), "CDOT Releases Updated Cycling Strategy to Expand Bike Network and Increase Everyday Cycling in Chicago" (March 2023 news release)**
  https://www.chicago.gov/city/en/depts/cdot/provdrs/bike/news/2023/march/cdot-releases-updated-cycling-strategy-to-expand-bike-network-an.html
  Official CDOT announcement of the 2023 Chicago Cycling Strategy, stating short bike trips in Chicago more than doubled between 2019 and 2023 — a count-derived claim tied to the strategy document; page could not be fetched directly (403) so in-page citations are unconfirmed beyond the title/framing.
- **Chicago Cycling Strategy / "2023 Chicago Cycling Update" (chicago.gov PDF)**
  https://www.chicago.gov/content/dam/city/depts/cdot/bike/2023/2023_Chicago%20Cycling%20Update.pdf
  The 2023 Chicago Cycling Strategy PDF, cited by CDOT press materials as the source of the 2019-2023 trip-doubling statistic; search snippets indicate it also states Divvy trips rose 60% over the same period. Full PDF text not parsed in any pass (interior not OCR'd/fetch blocked) — worth a direct pull for footnotes/data-source citations (likely cites Replica).
- **Replica, "Measuring Chicago's Boost in Biking" (company blog post, ~May 2024)**
  https://www.replicahq.com/post/measuring-chicagos-boost-in-biking
  Replica's own writeup of its CDOT partnership analyzing citywide biking trends; methodology used cellphone location and credit-card transaction data plus Divvy trip data, comparing a normal weekday in 2019 vs. 2023; found bicycling grew 119% over four years, with South Side neighborhoods seeing the largest proportional (170%+) increase. Includes a direct quote from Dave (David) Smith, CDOT Director of Complete Streets, referencing "Replica data" reflecting observed increases in biking across Chicago neighborhoods — confirms Replica as CDOT's trend-analysis data vendor.
  *Named:* Dave (David) Smith, Director of Complete Streets, CDOT
- **Streetsblog Chicago, "CDOT built it, they came: New report shows Chicago leads the nation in biking growth" (May 28, 2024)**
  https://chi.streetsblog.org/2024/05/28/cdot-built-it-they-came-new-report-shows-chicago-leads-the-nation-in-biking-growth
  Reports on a joint CDOT/Replica/Sam Schwartz analysis finding Chicago bicycling grew 119% between fall 2019 and spring 2023 — the largest increase among the 10 largest US cities — with breakdowns by trip purpose (restaurant trips +93%, shopping trips +117%, neighborhood trips +113%) and geography (South Side up 170%+); explicitly ties the analysis to validating the 2023 Chicago Cycling Strategy released one year prior. Alex Perez of Active Transportation Alliance is quoted responding. Note: a search-summary-attributed quote to "Jose Manuel Almanza, spokesperson for Equiticity" in this article could not be independently verified and should not be cited without confirmation.
  *Named:* Alex Perez (Advocacy Manager, Active Transportation Alliance); Sam Schwartz (transportation firm, report co-author/partner)
- **Chicago Sun-Times, "Pedal mettle? Bicycling in Chicago doubled in 5 years, but cyclists still worry about safety" (May 9, 2024)**
  https://chicago.suntimes.com/transportation/2024/05/09/bicycle-chicago-safety-transportation-city-hall-roads-environment-commute-health
  Describes a "one-page report by the Chicago Department of Transportation and Replica" finding biking trips more than doubled 2019-2023; notes the analytics company's methodology used cellphone/credit-card data and Divvy trip data, and that the analysis was "sponsored by the city transportation department" — evidence of a CDOT-Replica engagement/contract worth FOIAing for underlying data-sharing or services agreement.
- **Chicago.gov Bikeways Program / Existing Bike Network page**
  https://www.chicago.gov/city/en/sites/complete-streets-chicago/home/bike-program/existing-bike-network.html
  Hosts CDOT's quarterly-updated Bike Lane Mileage Tracker (500+ miles of on-street bikeways/off-street trails, tracked by type in a table with an interactive map), with mileage "tracked and updated quarterly as new segments are installed." Page not opened directly (403 on fetch) — confirmed via search snippet only.
- **Streetsblog Chicago, "This year People for Bikes' City Ratings ranked Chicago as tied with El Paso for the worst large U.S. city for biking. Here's CDOT's response." (July 8, 2026)**
  https://chi.streetsblog.org/2026/07/08/this-year-people-for-bikes-city-rating-rated-chicago-as-tied-with-el-paso-as-the-worst-large-us-city-for-biking-heres-cdots-response
  CDOT spokesperson Erica Schroeder responded to the 2026 PeopleForBikes ranking by citing specific counter/trend data: bikeway network surpassed 500 miles, 136 miles of low-stress bikeways since 2021 (249% increase), 6.8 million Divvy trips in 2025, 6.1 million Lime scooter trips in 2025, and Replica mobility data showing Chicago has the fastest-growing bicycle mode share among the 10 largest US cities.
  *Named:* Erica Schroeder (CDOT spokesperson)
- **Active Transportation Alliance blog, "More bicyclists in Chicago, proof is in the official CDOT counts"**
  https://activetrans.org/blog/more-bicyclists-in-chicago-proof-is-in-the-official-cdot-counts
  Describes CDOT's own bike-counting program: quarterly downtown counts plus monthly counts at six neighborhood locations; cites CDOT count totals across 20 locations showing AM rush cyclist increases of 19.5% (2012-13) and 14.3% (2013-14), and PM increases of 26.2% and 15.2% over the same periods — the strongest lead for a concrete CDOT count dataset/methodology. Title and framing directly assert the existence of "official CDOT counts" as the evidentiary basis for growth claims; page could not be fully confirmed by direct fetch (blocked in some passes).
- **Streetsblog Chicago, "New CDOT report finds that while bike lanes improved safety, they didn't harm businesses, and may help make corridors more economically resilient" (May 19, 2026)**
  https://chi.streetsblog.org/2026/05/19/new-cdot-report-finds-that-while-bike-lanes-improved-safety-they-didnt-harm-businesses-and-may-help-make-corridors-more-economically-resilient
  Covers a named CDOT report, the "Economic Impacts of Bike Lanes Study," examining six named corridors (Milwaukee Ave between Western/California; North Ave between Central Park/California; Clark St; and others) compared to "control" corridors, tracking Divvy trips, crash costs, and property values before/after bike lane installation (e.g., Milwaukee Ave saw increased Divvy trips and decreased crash costs) — explicitly analyzing "bike usage data since the lanes were installed" alongside sales-tax, vacancy, and employment data, meaning CDOT holds underlying corridor-level bike-usage/count data feeding this study. Jim Merrell (Active Transportation Alliance) is quoted reacting to the report.
  *Named:* Jim Merrell (Active Transportation Alliance)
- **Block Club Chicago, "Chicago's Bike Lanes Don't Hurt Businesses, City Report Finds" (June 23, 2026)**
  https://blockclubchicago.org/2026/06/23/chicagos-bike-lanes-dont-hurt-businesses-city-report-finds/
  Second independent outlet's coverage of the same CDOT Economic Impacts of Bike Lanes Study; cites specific examples: Milwaukee Ave (employment +37%), North Ave (vacancy -20% vs. control +12%), Clark St/Andersonville (vacancy -18%, sales tax recovered to pre-pandemic levels) — corroborates the report exists and used bike-usage data by corridor, useful for triangulating exact report title/date for a FOIA request.
- **CDOT primary-source document via chicago.gov FileNet repository (Economic Impacts of Bike Lanes / corridor case-study report)**
  https://api.chicago.gov/filenet5/servlets/getDocumentContent?applicationId=CompleteStreets&documentId=%7B30AC179E-0000-CA1C-953A-DE0C6D3D2AA3%7D
  Surfaced directly by web search as the underlying chicago.gov-hosted document for the 2026 corridor economic study; WebFetch was blocked (403) so content/title/date could not be independently confirmed beyond the search index label "Chicago." This is the concrete record ID a FOIA request could point at to request the underlying dataset/methodology.
- **Chicago Sun-Times, "Record number of Divvy rides, more bike lanes made 2023 an 'incredible' year for cycling in Chicago, city official says" (Jan 10, 2024)**
  https://chicago.suntimes.com/2024/1/10/24033443/bicycles-cycling-chicago-protected-bike-lanes-streets-divvy
  David Smith (CDOT Director of Complete Streets) testified to the City Council Committee on Pedestrian and Traffic Safety that "average weekday" overall bike trips increased 120% since 2019 and biking pre-pandemic to today more than doubled citywide — a specific, dated, named-official public statement citing CDOT trip-count/trend data, tied to a committee hearing (a concrete procedural artifact FOIA could target for underlying data/testimony materials).
  *Named:* David Smith (Director of Complete Streets, CDOT)
- **Streetsblog Chicago, "CDOT Complete Streets director David Smith: 2023 was Chicago's busiest bikeway installation year ever" (Nov 1, 2023)**
  https://chi.streetsblog.org/2023/11/01/cdot-complete-streets-director-david-smith-2023-was-chicagos-busiest-bikeway-installation-year-ever
  David Smith recaps record 2023 bikeway mileage installed (protected bike lanes, Neighborhood Greenways), likely referencing CDOT's quarterly bikeway installation tracker as the data source; useful contact for a FOIA request tied to the mileage tracker.
  *Named:* David Smith (Director of Complete Streets, CDOT)
- **Active Transportation Alliance blog, "Volunteers needed for downtown Chicago and Evanston bike counts"**
  https://activetrans.org/blog/volunteers-needed-for-downtown-chicago-and-evanston-bike-counts
  Describes CDOT's Complete Streets Program recruiting volunteers for manual bike counts in downtown Chicago (jointly with City of Evanston); a prior count recorded over 15,500 bicycle trips, indicating CDOT maintains/co-sponsors a volunteer manual-count program distinct from the Eco-Counter automated counter.
- **Active Transportation Alliance media release, "New analysis finds average daily bike trips reach 125,000 in city of Chicago" (2014)**
  https://activetrans.org/media/new-analysis-finds-average-daily-bike-trips-reach-125000-in-city-of-chicago/
  Active Trans-commissioned analysis estimating ~125,000 average daily bike trips in Chicago (91,000 utilitarian, ~26,000 work, ~7,000 school trips), built using CMAP travel survey data in combination with count-derived estimates; ED Ron Burke quoted.
  *Named:* Ron Burke (Executive Director, Active Transportation Alliance)
- **City of Chicago (chicago.gov) CDOT press release, "Chicago Sees Record 11+ Million Shared Bike and Scooter Trips In 2024" (Jan 2025)**
  https://www.chicago.gov/city/en/depts/cdot/provdrs/bike/news/2025/january/chicago-sees-record-10--million-shared-bike-and-scooter-trips-in.html
  CDOT press release citing Replica data estimating biking in Chicago more than doubled since 2019, the highest growth among the 10 largest US cities — another dated, citable CDOT document referencing the Replica count/trend relationship.

### Supporting evidence

- **Planetizen News, "Chicago Gets its First Bike Counter" (Dec 2022)**
  https://www.planetizen.com/news/2022/12/120442-chicago-gets-its-first-bike-counter
  Corroborates the Chicago/Wells Eco-Counter installation as the city's first permanent bike counter, aggregating the Streetsblog report.
- **Streetsblog Chicago, "Cast Your Vote for the Milwaukee Avenue Bike Counter Design" (Apr 19, 2016)**
  https://chi.streetsblog.org/2016/04/19/cast-your-vote-for-the-milwaukee-avenue-bike-counter-design
  Covers the public design vote for the donated Eco-Totem counter later approved by City Council for the Milwaukee Ave location, establishing a paper trail (City Council approval, CDOT/developer coordination) predating the 2018 stall.
- **CDOT Bicycle Survey (chicago.gov publication, PDF)**
  https://www.chicago.gov/content/dam/city/depts/cdot/bicycling/publications/cdot_bicycle_survey.pdf
  A standalone CDOT-published bicycle survey document hosted under CDOT's bicycling/publications directory, referenced repeatedly in search results alongside count-study material; found via search listing only, interior/content not confirmed (WebFetch blocked 403) — a concrete, citable CDOT document to request in full under FOIA.
- **Chicago Streets for Cycling Plan 2020 (chicago.gov PDF, CDOT master bike plan)**
  https://www.chicago.gov/content/dam/city/depts/cdot/bike/general/ChicagoStreetsforCycling2020.pdf
  CDOT's earlier citywide bike master plan (referenced alongside the Bike 2015 Plan) that lists gathering/using bike counts as a stated planning goal.
- **Chicago Cycling Strategy Executive Summary PDF (CDOT, 2023)**
  https://www.chicago.gov/content/dam/city/sites/complete-streets/pdfs/2023_Chicago%20Cycling%20Strategy_Executive%20Summary.pdf
  Companion executive-summary PDF to the full strategy; likely repeats the same trip-growth statistics and could contain a citation/methodology footnote pointing to the source count data.
- **"THE CHICAGO CYCLING STRATEGY" — NACTO conference deck (Denver 2023)**
  https://nacto.org/wp-content/uploads/NACTO_Denver2023_Chicago_v2.pdf
  A CDOT-authored NACTO conference presentation on the Chicago Cycling Strategy's data-driven approach; found via search listing, not opened for detail.
- **Axios Chicago, "Chicago biking surges" (May 26, 2024)**
  https://www.axios.com/local/chicago/2024/05/26/local-biking-surges-in-chicago
  Additional press coverage of the same CDOT/Replica biking-growth report, useful for corroborating exact release date and any named CDOT spokesperson quoted.
- **NACTO, "Complete Streets Chicago: Data Driven Design" — presentation by Luann Hamilton (PDF)**
  https://nacto.org/wp-content/uploads/HamiltonLuann_DesigningCitiesPHX.pdf
  A CDOT presentation (Luann Hamilton, identified in search results as CDOT Deputy Commissioner) on data-driven Complete Streets design, situated among search results for bike-count data; not opened for full detail but names a specific CDOT official tied to data/count practices.
  *Named:* Luann Hamilton (CDOT Deputy Commissioner, per search summary)
- **Grid Chicago, "Bike counts are important to businesses and in evaluating our progress" (2012)**
  https://gridchicago.com/2012/bike-counts-are-important-to-businesses-and-in-evaluating-our-progress/
  Describes CDOT's earlier volunteer pencil-and-paper bike counts at downtown intersections used to track the Bike 2015 Plan, and notes CDOT was not yet purchasing automated counters like Eco-Counter as of 2012 — useful for dating the transition to automated/permanent counters and establishing a timeline baseline.
- **FOIA Request Log - Transportation (Chicago Data Portal dataset, ID u9qt-tv7d)**
  https://data.cityofchicago.org/FOIA/FOIA-Request-Log-Transportation/u9qt-tv7d
  Official log of all FOIA requests received by CDOT since May 1, 2010, searchable by keyword; would show prior requesters who asked about bike counts/counters. Direct access blocked by egress policy (403 on data.cityofchicago.org), so contents were not verified beyond the dataset's existence and description via search snippets.
- **File a Transportation FOIA Request (CDOT FOIA procedures page)**
  https://www.chicago.gov/city/en/depts/cdot/supp_info/cdot_foia.html
  Official CDOT FOIA contact page instructing requesters to be specific about locations/dates and to email cdotfoia@cityofchicago.org; establishes the correct intake channel and named-office contact for a bike-count FOIA request.
  *Named:* CDOT FOIA office (cdotfoia@cityofchicago.org)
- **Chicago Sun-Times, "How does the city decide where to put new bike lanes?" (May 22, 2022)**
  https://chicago.suntimes.com/2022/5/22/23103585/bike-lanes-david-smith-department-transportation-cdot
  Interview with David Smith, CDOT Complete Streets manager, discussing use of survey and data (implicitly including usage/count data) to decide bike lane placement.
  *Named:* David Smith (Complete Streets manager, CDOT)
- **Active Transportation Alliance blog, "Help make bicycling count"**
  https://activetrans.org/blog/help-make-bicycling-count
  Related ATA blog post on the same volunteer bike-count program; confirms this is a recurring effort tied to Chicago bicycling data collection.
- **Momentum Mag, "Bicycling grew more in Chicago than in any other major American city in the last five years"**
  https://momentummag.com/bicycling-grew-more-in-chicago-than-in-any-other-major-american-city-in-the-last-five-years/
  Independent coverage of the CDOT/Replica/Sam Schwartz study (119% growth fall 2019-spring 2023; 207% rise in zero-auto households cycling; 166% increase in non-white cyclists).
- **Streetsblog Chicago, "Common sense: CDOT's Chicago Traffic Crashes report illustrates the effectiveness of bike/ped investment" (Oct 24, 2024)**
  https://chi.streetsblog.org/2024/10/24/common-sense-cdots-chicago-traffic-crashes-report-illustrates-the-effectiveness-of-bike-ped-investment
  Covers CDOT's annual Chicago Traffic Crashes report, tying bike/ped infrastructure investment (50+ miles of low-stress bikeways under the 2023 Cycling Strategy) to safety outcomes — an annual CDOT report series that plausibly cross-references count/volume data.
- **Chicago Traffic Crashes annual report PDF via chicago.gov FileNet (documentId {60FB7292-0000-CB1B-AC4D-334F5F94606B})**
  https://api.chicago.gov/filenet5/servlets/getDocumentContent?applicationId=CompleteStreets&documentId=%7B60FB7292-0000-CB1B-AC4D-334F5F94606B%7D
  Primary-source location for the CDOT annual Traffic Crashes report; WebFetch blocked (403), content unverified beyond the search-index title "Chicago Traffic Crashes 1 CDOT Chicago Department of Transportation." Useful as the exact document a FOIA request could name/attach.
- **CDOT press release quoting Commissioner Tom Carney on the Replica 119% biking-growth finding (~May 24, 2024; exact URL uncertain)**
  https://www.chicago.gov/city/en/depts/cdot/provdrs/bike/news/2024/may/cdot-announces-upcoming--learn-to-ride--bike-riding-classes-for-.html
  CDOT Commissioner Tom Carney quoted commenting on the Replica-sourced 119% biking-growth figure ("There's never been a better time to ride a bike in Chicago..."); URL attribution from search engine is uncertain and should be verified directly before citing in a FOIA letter.
  *Named:* Tom Carney (CDOT Commissioner)
- **Primera Engineering, "IDOT and Primera Put Spotlight on Bicyclist and Pedestrian Safety"**
  https://primeraeng.com/bikepedsafety/
  Describes Primera's research for IDOT (District 1, covering Chicago-area roads) recommending a permanent, continuous 24-hour bicycle/pedestrian count program with conversion factors, noting no such continuous statewide counts existed yet — a concrete vendor/procurement-adjacent artifact for an IDOT-side FOIA angle.
- **CMAP, "My Daily Travel" household travel survey program page and reports**
  https://cmap.illinois.gov/data/transportation/travel-survey/
  CMAP's regional household travel survey (covering Chicago) includes bicycling mode-share/trip data used in regional monitoring alongside Divvy ridership data; a partner (non-CDOT) dataset referencing Chicago cycling volumes.

### Weak evidence

- **City of Chicago (chicago.gov), "2012 Bicycle Crash Analysis - Summary Report" (PDF)**
  https://www.chicago.gov/content/dam/city/depts/cdot/bike/general/BikeCrashReport2012.pdf
  CDOT crash-analysis report that may reference exposure/count data as denominator context; found via search listing only, interior not reviewed.
- **Shared-Use Mobility Center, "Bike Chicago Evaluation Report" (May 2024, PDF)**
  https://sharedusemobilitycenter.org/wp-content/uploads/2024/05/SUMC-Bike-Chicago-Evaluation-Report_final.pdf
  Third-party evaluation report on Chicago cycling, published same month as the CDOT/Replica release; likely cites CDOT count/trend data but interior not reviewed — flagged for a follow-up targeted pull.
- **trafficFOI dataset (Chicago Data Portal, ID vvu2-f9st) — appears to be a companion/duplicate FOIA log**
  https://data.cityofchicago.org/api/views/vvu2-f9st/rows.pdf?accessType=DOWNLOAD
  Search snippet describes this as containing FOIA request records to CDOT covering bike routes, protected bike lanes, and related traffic records; not independently verified due to blocked access.
- **Streetsblog Chicago, "Key findings from CDOT's annual Chicago Traffic Crashes report" (Nov 25, 2025)**
  https://chi.streetsblog.org/2025/11/25/key-findings-from-cdots-annual-chicago-traffic-crashes-report
  Confirms CDOT publishes an annual Chicago Traffic Crashes report analyzing crash trends (by mode, location, etc.) based on the IDOT statewide crash dataset. Search snippets did not surface any explicit citation of bicycle exposure/volume count data (e.g., counters or Replica) within this report specifically — crash counts are not the same as ridership/exposure counts.
- **CDOT Complete Streets, "Data Resources" page (traffic-safety section)**
  https://www.chicago.gov/city/en/sites/complete-streets-chicago/home/traffic-safety/data-resources.html
  Confirmed to exist and to be indexed under CDOT's traffic-safety data resources; exact contents (whether it lists bike count/counter data sources) could not be confirmed — WebFetch blocked (403) and no search snippet surfaced its content directly.
- **Eco-Counter public Eco-Display World Map (real-time counter dashboard)**
  https://eco-display-map.eco-counter.com/
  Public global map of 400+ Eco-Counter-brand installations; if the Chicago Ave/Wells counter is on this map, its raw count data may already be public via Eco-Counter directly (not CDOT), useful for scoping a FOIA request to CDOT-held records specifically (e.g., correspondence/reports, not raw counts CDOT doesn't possess).
- **MuckRock, agency page for Chicago Department of Transportation**
  https://www.muckrock.com/agency/chicago-169/chicago-department-of-transportation-10830/
  Search-indexed page confirming MuckRock tracks a CDOT agency profile with filed requests, but the page itself returned 403 when fetched directly, so the specific list of past requests (and whether any concern bike counts) could not be confirmed.
- **MuckRock, "Retention policies (Chicago Department of Transportation)" FOIA request**
  https://www.muckrock.com/foi/chicago-169/retention-policies-chicago-department-of-transportation-60492/
  A prior FOIA request filed to CDOT about its records retention policies generally; not bike-count-specific but could reveal what categories of traffic/count data CDOT retains and for how long, relevant to scoping a bike-count request.
- **IDOT sole-source contract notice with Sidewalk Labs Inc. for the Replica analysis tool**
  https://webapps.dot.illinois.gov/WCTB/ConstructionSupportNotice/BulletinItem/0ff7ba88-81f7-4cd8-b24b-bc153d493725?page=1
  A sole-source procurement notice for Replica (via Sidewalk Labs Inc.) exists at the state DOT level (IDOT), not confirmed as a City of Chicago/CDOT contract — flagged because it's easy to mis-cite as a CDOT contract; the actual CDOT-Replica arrangement (per Sun-Times) appears to be a sponsored analysis/report rather than a documented open procurement record found in this search.
- **City of Chicago (chicago.gov), CDOT 2025 Org Chart PDF**
  https://www.chicago.gov/content/dam/city/depts/cdot/84-%20CDOT_2025_OrgChart_rev.pdf
  Names Commissioner Tom Carney with direct phone (744.3501) and email (per snippet) — useful for addressing a FOIA request to a specific named official, though not itself count-data content.
  *Named:* Tom Carney (CDOT Commissioner)
- **CMAP, "_readme_bikewayInventorySystem.pdf" (Bikeway Inventory System documentation)**
  https://www.cmap.illinois.gov/documents/10180/1511030/_readme_bikewayInventorySystem.pdf/b0214419-adbd-5ec6-a4f4-c1b941ba8d00?t=1670538458996
  CMAP's readme for the regional Bikeway Inventory System (BIS) geodatabase covering existing/planned/programmed bike facilities in northeastern Illinois, including Chicago — an inventory/mileage dataset adjacent to but distinct from count data.
- **CMAP Data Hub, "Bikeway Inventory System List of Feature Classes, January 2022"**
  https://datahub.cmap.illinois.gov/documents/4052969559c74b7cbac62144e5f10eda
  Technical feature-class list for the BIS geodatabase (Jan 2022) — confirms CMAP maintains bikeway infrastructure records CDOT feeds into, but not a count dataset itself.
- **GitHub - CMAP-REPOS/mydailytravel (R analysis scripts for the My Daily Travel survey)**
  https://github.com/CMAP-REPOS/mydailytravel
  Public repo of CMAP's analysis code for the My Daily Travel survey, including bike-share/Divvy ridership pulls used alongside travel-survey bicycling data — a technical, citable artifact showing the analytic pipeline behind regional bike-trip estimates that touch Chicago.

## Dead ends (checked — don't re-search; grouped by crawl pass)

- [cdot-pages] chicago.gov Department of Procurement Services bid/RFP listings and Vendor/Contract/Payment search (webapps1.chicago.gov/vcsearch) — searched for a formal Eco-Counter / bike-counter procurement record; found only unrelated 2011 bike-share brokerage RFP and generic DPS pages, no specific bike-counter contract or line item.
- [cdot-pages] Direct WebFetch of chicago.gov and chi.streetsblog.org pages — all attempts returned HTTP 403 Forbidden; citations rely on WebSearch result snippets/summaries rather than full page text, so exact quotes/page numbers inside PDFs were not verified by direct read.
- [cdot-pages] CDOT Vision Zero annual report search — not separately queried in this pass; no evidence found or checked for bike-count citations within Vision Zero reports specifically (worth a follow-up query, not confirmed as a dead end vs. simply unexplored).
- [foia-logs] data.cityofchicago.org (Socrata data portal) is blocked by this session's egress proxy policy (403 CONNECT denial) — could not directly query the FOIA Request Log dataset (u9qt-tv7d) or trafficFOI dataset (vvu2-f9st) via API/JSON to keyword-search for 'bicycle'/'bike counter' entries; only search-engine snippets describing these datasets' existence were obtainable.
- [foia-logs] MuckRock.com pages (agency page, search results, individual request pages) returned HTTP 403 on every direct WebFetch attempt; a site:muckrock.com web search for Chicago bicycle counter / bike count terms returned no on-topic MuckRock request pages, suggesting no prior public MuckRock request specifically targeted Chicago bike-counter data (or it exists but isn't indexed under those terms).
- [foia-logs] No dedicated 'bicycle count' or 'bike count' dataset was found on the Chicago Data Portal via web search (unlike NYC's 'Bicycle Counters' open dataset or DC's automated counter dataset) — searches for Chicago-specific bike count datasets returned only out-of-state (California, Colorado, DVRPC/Philadelphia, Portland) results, suggesting CDOT does not publish a standalone bike-count dataset, supporting the case that count data would need to come via FOIA rather than the open data portal.
- [foia-logs] activetrans.org, replicahq.com, and chi.streetsblog.org article bodies were blocked (403) on direct WebFetch; content for those pages was inferred only from search-engine snippets/summaries, not full-text verification of methodology or additional named staff/dates that might be in the article bodies.
- [press] Direct WebFetch of chi.streetsblog.org article pages (Dec 2022 counter story, May 2024 Replica report story) returned HTTP 403 Forbidden — content only available via WebSearch snippets/summaries, not full article text, so exact quotes/dates beyond what's in search snippets are unconfirmed.
- [press] Direct WebFetch of chicago.gov CDOT press-release pages (March 2023 Cycling Strategy release) also returned HTTP 403 Forbidden — could not verify in-page count citations beyond the page title/URL.
- [press] Did not search procurement/contract records (e.g. city bid portal, purchase orders) for the Eco-Counter or Replica engagements — that source class is out of scope for this press/announcements pass and would need a separate targeted search.
- [press] A WebSearch-tool-generated summary attributed a quote to a 'Jose Manuel Almanza, spokesperson for Equiticity' inside the May 2024 'CDOT built it, they came' Streetsblog coverage; this could not be independently verified (page fetch blocked, and the quote did not reappear in any other search), so it was excluded from citations as unverified/possibly hallucinated by the search summarizer.
- [procurement] Chicago Data Portal 'Contracts' dataset (data.cityofchicago.org rsxa-ify5) and 'Contracts - Contract PDF Present' dataset: searched via web search engine for 'Eco-Counter' / 'bicycle counter' / 'Replica' line items; these are interactive/queryable datasets not indexed by web search, so no matching line item could be surfaced this way — needs a direct Socrata API/portal query, not general web search.
- [procurement] webapps1.chicago.gov/vcsearch (City's Vendor, Contract and Payment Search tool): searched for vendor names 'Replica' and 'Eco-Counter'/'Eco Counter'; the tool is an interactive search app not indexed by search engines, so no vendor/contract record was found via WebSearch — needs direct interactive querying.
- [procurement] CDOT Procurement News page (chicago.gov/.../cdot-procurement-news.html) and CDOT Contracts and RFPs page: no bicycle-counter- or Replica-related solicitation surfaced in search snippets.
- [procurement] City of Chicago FOIA Request Log - Transportation dataset (data.cityofchicago.org): confirmed to exist and would likely contain prior FOIA requests about bike counters/Replica, but its row-level contents are not searchable via general web search (interactive Socrata dataset); needs direct query.
- [procurement] Direct WebFetch of chicago.gov PDF/HTML pages and chi.streetsblog.org article pages: every attempted fetch returned HTTP 403 (bot-blocked), including a direct curl attempt through the environment's proxy which also failed with a 403 CONNECT tunnel error — all chicago.gov and streetsblog.org content in this report is based on WebSearch result snippets only, not verified full-text reads.
- [procurement] CDOT capital program / Capital Improvement Program (CIP) documents specifically for 'bicycle counter' or 'automated counting' equipment line items: general CIP contract-scope PDF was found (chicago.gov CIP 'ContractsInScopeForCIP.pdf') but not searched/opened for bicycle-counter-specific line items due to targeted-search scope; not confirmed to contain relevant entries.
- [partners] Direct WebFetch of activetrans.org, chi.streetsblog.org, replicahq.com, and chicago.gov article/PDF URLs all returned HTTP 403 Forbidden — content is based only on WebSearch result snippets, not full-page/PDF reads; a team member with browser access should re-fetch these directly.
- [partners] No university research (UIC, Northwestern, DePaul) study was found that specifically analyzes CDOT bicycle count data with CDOT acknowledgment — searches surfaced only tangential campus bike-map/sustainability pages and Northwestern library research guides pointing back to CMAP/CDOT data sources, not an actual study using CDOT counter data.
- [partners] Could not locate a specific, named IDOT District 1 permanent bicycle count program document/dataset covering Chicago streets — only a vendor teaser page (Primera Engineering) describing recommendations to IDOT; the underlying IDOT report/RFP was not found via search.
- [partners] Could not confirm specific content of the 'CDOT Bicycle Survey' PDF or the full 'Chicago Cycling Strategy' PDF (counts/citations within) since PDF fetches were blocked; only their existence and search-snippet context were confirmed.
- [partners] No procurement-specific documents (RFP, purchase order, contract line item) for the Chicago Ave & Wells Eco-Counter or any CDOT-owned bike counter were found — the Chicago Ave/Wells counter appears to be developer (AMLI)-funded/installed rather than a CDOT procurement, per available snippets.
- [trackers] WebFetch attempts on all identified chicago.gov, api.chicago.gov/filenet5, chi.streetsblog.org, blockclubchicago.org, and replicahq.com URLs returned HTTP 403 Forbidden — no full-text/page-content confirmation was possible for any source; all findings rest on WebSearch result snippets only.
- [trackers] Could not locate CDOT procurement records, purchase orders, or contract line items for bike counters (e.g. Eco-Counter equipment) via general web search — city procurement portal (chicago.gov eProcurement / transparency portals) does not appear to be indexed by general web search for this topic; would need direct portal search, not general web search.
- [trackers] Could not confirm via search snippets whether the CDOT annual Chicago Traffic Crashes report itself (as opposed to secondary press coverage) explicitly cites bicycle exposure/count data as a denominator for crash rate analysis — only crash-count trends were confirmed.
- [trackers] No additional named CDOT staff (beyond Erica Schroeder and David/Dave Smith) surfaced as authors/signatories on the Bike Lane Mileage Tracker or the 2026 corridor economic study specifically.