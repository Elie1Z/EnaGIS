# EnaGIS Live: method

EnaGIS Live turns a place name into a ranked, uncertainty-aware investigation shortlist. It does
this in the browser, from open data gathered at search time. The code is:

- `live/js/engine.js`: analysis;
- `live/js/sources.js`: data;
- `live/js/overture.js`: Overture tiles.

This page states every formula and assumption.

## 0. Data gathered for each search

| Layer | Source | Fallback |
|---|---|---|
| Boundary | Nominatim (OpenStreetMap geocoder) | map view box |
| Facilities, towns, villages | OpenStreetMap via Overpass | none |
| Extra facilities | Overture places (Meta, Microsoft): agricultural categories, confidence ≥ 0.5, look-alikes filtered | none |
| Buildings | Overture buildings: OpenStreetMap + Google Open Buildings + Microsoft ML footprints, one point per footprint | Overpass |
| Roads and paths | Overture transportation (from OpenStreetMap), rejoined across tile edges | Overpass |
| Power | Overture base: lines, pylons, poles, substations, generators (from OpenStreetMap) | Overpass |
| Population | WorldPop 2020 (`wpgppop`), total inside the boundary | assumption range |
| Climate | Open-Meteo ERA5 archive, 2024 | 25 °C assumed |

How Overture is read:

- **Tiles.** Overture is read as PMTiles at zoom 14 (power at 13). Only tiles touching the boundary are
  fetched, at most 650.
- **No duplicates.** A building counts in the tile that holds its centre, so tile overlaps are not counted
  twice.
- **Roads rejoined.** A road cut at a tile edge is relinked to its continuation in the next tile.
- **Cache.** Converted tiles are cached in the browser.

Decision record: [0013](decisions/0013-open-data-stack.md).

## 1. Unit of analysis

A **candidate aggregation site** inside the searched boundary. It is either:

- **documented** (OBSERVED in OpenStreetMap): market, cooperative, milk collection centre, cold
  store, mill, warehouse, agro-processing works, farm shop; or
- **listed** in Overture places (OBSERVED, with the listing's category and confidence). Only these count:
  - agricultural categories (markets, cooperatives, dairy, mills, cold storage, agricultural services);
  - names that clearly say cooperative, milk collection, mill or cold store.

  Warehouses and factories need an agricultural word in the name. Churches, shops, offices and
  government agencies are excluded even when their name contains "market" or "isoko"; or
- a **town or village centre** (INFERRED). These stand in only where no documented facility is
  mapped within 1.5 km.

Classification uses OSM tags first, then name patterns in English, French and Kinyarwanda
(`koperative`, `amata`, `isoko`, `ububiko`…). Cafés, supermarkets, sawmills, banks and similar
are excluded. Duplicates within 80 m are merged. Each value chain accepts only some site types
(for example, milk cooling does not use mills).

## 2. Catchments (who can reach each site)

- **Road graph.** Built from every mapped road and path. Speeds (km/h) are 50 primary, 40
  secondary, 30 tertiary, 25 unclassified, 15 track, 5 path. They are assumptions in `SPEEDS`.
- **Rain factor.** The rainy season multiplies speed by a factor from the surface tag:

  | Surface | Rain factor |
  |---|---|
  | Paved | 0.9 |
  | Gravel / compacted | 0.7 |
  | Earth, dirt, mud | 0.45 |
  | Untagged major road | 0.85 |
  | Untagged minor road | 0.6 |

  Walking off the network is 20% slower in the rain.
- **Assignment.** Each site snaps to the nearest road vertex within 3 km. A multi-source Dijkstra
  search then gives every vertex its fastest site. Each building reaches its nearest vertex on
  foot (straight line × 1.3 at 4 km/h), or walks straight to a site within 4 km if that is faster.
- **Travel limit.** Buildings beyond the limit (60 / 90 / 120 min, sampled) are not assigned.
- **People.** Buildings × people per building.
  - **With WorldPop:** WorldPop population inside the boundary ÷ buildings inside the boundary, with a range
    of ±20% (ESTIMATED).
  - **Without WorldPop:** 2.5 / 4.0 / 5.0 (INFERRED).
- **Urban cells.** Buildings in dense cells (≥ 100 buildings per 250 m cell) count at a reduced
  producer weight (0.05 / 0.15 / 0.30), because town residents grow little.

## 3. Production

In Rwanda, production per person comes from the **district** the searched area lies in (a district,
or a sector or cell whose address names its district). Areas spanning several districts (a province, a
drawn map view) and milk (no district series yet) use the national figure. Elsewhere there is no
default: requirements stay UNKNOWN until the user enters kg per person per year. The tool never
borrows Rwanda's numbers silently. Local variation inside the district is simulated (section 5) and
the user can override any figure.

| Item | Value | Source |
|---|---|---|
| Population by district | 2022 census (sums to 13,246,394) | NISR, 5th Population and Housing Census (via citypopulation.de) |
| Irish potato, national | 827,355 t (2024: A 460,830 + B 285,596 + C 80,929) | NISR Seasonal Agricultural Survey 2024, annual report, Table 0 |
| Maize, national | 627,086 t (2024: A 507,985 + B 119,101) | same |
| Potato and maize by district | Season A 2024 area (Table 9) × yield (Table 11), as a share of the national Season A total, applied to the 2024 annual total | NISR SAS 2024 Season A report; table in `data/rwanda/district_production_2024.csv` |
| Milk, national | >1,000,000 t (2023) | MINAGRI, as reported by The New Times |

Checks: district Season A area sums to the national 54,048 ha (potato) and 249,435 ha (maize);
area × yield reproduces the national Season A production within 0.5% (potato) and 2.4% (maize).
Kirehe, Ngoma and Bugesera yields are not legible in the source and use the area-weighted mean of
the other Eastern districts (flagged in the table and on screen). The district shares assume the
Season B and C geography follows Season A; this is an estimate (label ESTIMATED).

Why it matters: Nyabihu grows about **578 kg of potatoes per person a year** and Kicukiro less than 1 kg;
the national average is 62 kg. A national average would hide Rwanda's potato belt.

## 4. Energy requirement (per peak day)

Every model takes a site's annual volume, A = catchment production × capture share × site-type
multiplier, and returns kWh per peak day and kW while running. Ranges are low / central / high.
None of them are human-approved.

| Value chain | Formula |
|---|---|
| Cold storage, Irish potato | Intake = A × peak-month share ÷ 30; stored = intake × storage days; heat = intake × cp × (T_hot − T_store) + stored × holding load; kWh = heat ÷ COP. T_hot = hottest-month mean daily maximum from Open-Meteo |
| Milk cooling | kg/day = A ÷ 365 × rainy-season peak; heat = kg × cp × (T_in − T_out) × (1 + holding share); kWh = heat ÷ COP |
| Maize milling | t/day = A ÷ operating days; kWh = t/day × specific energy (15 / 25 / 40 kWh/t) |
| Maize drying (fans and handling) | t/day = A ÷ seasons ÷ harvest window; kWh = t/day × specific energy (4 / 8 / 15 kWh/t); heat from other fuels is not counted |

kW = kWh ÷ running hours. All parameter ranges, units and evidence labels live in
`live/js/config.js` and can be edited in the app under **Assumptions**.

## 5. Uncertainty and ranking

- **Central estimate.** Every parameter at its central value; this sets the rank. Ties break by
  site ID.
- **Simulation.** 300 draws, seed 20261026. Each draw samples:
  - every model and shared parameter (triangular over low / central / high);
  - the site-type multipliers;
  - persons per building;
  - a per-site local production factor, lognormal with mean 1 and log-sd 0.2 / 0.35 / 0.5.

  The local factor is the main source of rank change between sites.
- **Reported per site:**
  - the 5th, 50th and 95th percentile of kWh/day and kW;
  - the share of draws in the top 10;
  - the 5th–95th percentile rank.
- **Tiers.** With more than 10 sites, a top-10 site is:
  - **Robust** if it stays in the top 10 in at least 80% of draws;
  - **Contested** if 40–80%;
  - **Check first** below 40%.

  With 10 or fewer sites, tiers use how far the rank moves instead (spread of 1 or less, up to 3,
  or more).
- **Drivers.** For each top-20 site, each assumption is moved from low to high with everything
  else central. The biggest swings are shown in Expert mode and choose the "Check first" question.

## 6. Supply context

- **Grid.** The distance from each site to the nearest mapped power line (sampled every 100 m) or
  substation gives three states:
  - grid mapped within 500 m;
  - grid mapped within 5 km;
  - no grid mapped within 5 km.

  All three are INFERRED: a mapped line does not prove a connection, and a missing line does not
  prove there is none. Electrical capacity is always UNKNOWN.
- **Solar.** kWp = kWh per peak day ÷ (darkest-month sun hours × performance ratio 0.75). Night-time
  storage is not included.

## 7. Map coverage

The map-coverage rating uses buildings per km² and road km per km²:

- **well mapped:** at least 100 buildings and at least 2 road km per km²;
- **partly mapped:** at least 20 buildings or at least 0.8 road km per km²;
- **thinly mapped:** below both.

Grid squares (1 km, or 2 km for areas over 800 km²) with no buildings and almost no roads are
hatched as "not yet known".

## 8. Simpler baseline

Every mapped building counts equally and goes to the nearest site in a straight line, with no
roads, no travel limit and no value-chain assumptions. The app reports how many of the top 10 the
two methods share. Where they agree, the extra modelling did not change the decision.

## 8b. Siting model (Phase 4R)

`live/js/siting.js` scores 1 km cells for how much they look like places where agricultural collection
or processing points are documented. Features use only layers that never encode the label: building
counts and roof sizes (Overture footprints; area computed from the tile geometry, checked against
known synthetic footprints), building density within about 2 km, major and minor road length,
distances to a major road, the mapped grid and the nearest town or village point, and the share of
buildings in dense blocks. The model is an L2-regularised logistic regression with balanced weights.

Its test is registered in `docs/spec/phase4r-protocol.md` (leave-one-district-out over all 30
districts, recall in the top 10% against five single-signal rules, cluster bootstrap, keep rule fixed
in advance) and run by `live/tools/train-siting.cjs`, which writes the frozen model and
`docs/audits/phase4r-evaluation.json`. The training table is built by `live/tools/harvest.js`, which
runs the app's own gatherers over every district. In the app, the **Likely sites** lens shows the
top 20% of cells, the cells with a documented point, and up to 12 "look-alikes": high-scoring
cells with at least one roof of 150 m² or more and nothing documented. Each site card gives its
cell's percentile. The score never changes the energy ranking.

**Result (registered test): KEEP.** Recall in the top 10% is 73.1% for the model and 49.3% for the best
single rule (most buildings in the cell). The margin is +23.9 points, 95% interval 13.4 to 34.4, over
25,281 cells and 134 positive cells in 27 districts. A label audit after the test removed 7 plainly wrong
positives (a hotel, a football club, a café, shops); the margin stays +23.6 (13.2 to 34.7). Details:
[phase4r-results.md](phase4r-results.md).

## 8c. Robustness of the live gatherers

- Overture Maps release is pinned to the one the siting model was trained on (`2026-09-23.1`); if
  it is withdrawn, the app switches to the latest release automatically.
- Overpass (OpenStreetMap facilities and settlements) is retried three rounds over two public
  servers with a growing pause, because public servers refuse bursts (429) and time out under load
  (504). During the national harvest, 16 of 30 first attempts failed this way; without the retry a
  search would silently lose its mapped facilities and town centres.
- Streets are never read as facilities ("Rue du Marché", "Mill Road"), and the Kinyarwanda word for
  milk, *amata*, only matches as a whole word (not inside place names such as Nyamata).
- Names found in the real Rwanda data are excluded as look-alikes. They include toilets ("Vunga
  market's Public Toilet"), hotels ("Hôtel des Mille Collines": "Mille" is not a mill), cafés ("coffee
  shop"), clubs, campuses, tourism businesses, police stations and town halls. Tea factories and tea-leaf
  collection centres are their own type and never serve potato, milk or maize.
- Two sites with the same name are told apart: "Cyamabuye (west)" and "Cyamabuye (east)". Unnamed
  stand-ins get their coordinates.
- "Save example districts" gathers the example districts into the browser cache in advance and
  reports any district whose sources were busy.

## 9. What is and is not validated

| Validated (software) | Not validated |
|---|---|
| Deterministic engine: same data and seed give the same result (unit tests) | That the top 10 are the right sites (no field visits, n = 0) |
| Rainy season never brings more people within reach (unit test) | Energy factors (no meters) |
| UNKNOWN stays UNKNOWN; missing data degrades gracefully (unit tests) | Production per person below district level |
| Full browser path with intercepted services, Overture tiles (synthetic archives), Overpass fallback, offline replay, file:// opening, siting lens (39 checks) | Completeness of OpenStreetMap and Overture in any given area |
| **Siting model, registered test on all 30 Rwandan districts: KEEP** (+23.9 points over the best single rule; holds after a label audit and without Kigali) | That a predicted cell or look-alike holds a facility (no phone checks yet) |
| All 30 districts run end to end with the shipped engine ([national screening](rwanda-national-screening.md)) | District production below district level (ESTIMATED, spread evenly) |
| Overture road pieces rejoin across tile edges into the source network (same component count) | Age of building footprints (2020–2023 imagery) |
| Live run, Gasabo: 338,902 buildings, WorldPop 889,650, 29 sites ranked, gather 74 s, analysis 1.7 s | That WorldPop 2020 matches today's population everywhere |
| District-scale run: 250,000 buildings, 35,000 roads, 293 sites in about 4 s, off the main thread | Transfer of the Canadian pilot result to Rwanda |

The registered Canadian siting experiment (verdict KILL) and the Phase 3 pipeline are unchanged.
The Rwanda test (Phase 4R) asks a different question with different features; it does not re-run
or overturn Phase 4.

## 10. Reproducing an analysis

"Save analysis" writes one JSON file with every raw response, retrieval time, endpoint, query and
option. Opening it replays the exact analysis offline. OpenStreetMap changes daily, so a new search
of the same place can differ; the saved file is the record.
