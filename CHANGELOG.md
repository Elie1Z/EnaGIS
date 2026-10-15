# Changelog

Dates are 2026. Each entry lists what changed and what it does **not** claim.

## Unreleased — advanced-tools track: XGBoost, second-site scouting, Njombe footprint test (10–11 Oct)

- **Phase 4X, XGBoost vs the registered siting model: TESTED, NOT BETTER.** The protocol
  (`docs/spec/phase4x-protocol.md`, SHA-256 `cf8e9382…`) was hashed before XGBoost was scored. It fixed the settings
  (depth 3, 200 trees, learning rate 0.05, no tuning), the paired bootstrap and the adoption rule. A Python port of
  the Phase 4R evaluation (`research/phase4x/`) first reproduced the registered result exactly (73.1% vs 49.3%,
  +23.9 [13.4, 34.4]).
  - XGBoost: 64.2%. Logistic: 73.1%. Paired difference −9.0 points (−15.1 to −3.3).
  - Calibration is fine for both; ranking is not. XGBoost is behind in 6 districts and ahead in none.
  - The app keeps the logistic model and shows a **Model comparison** card in the Likely sites lens.
  - Results: `docs/phase4x-results.md`, `docs/audits/phase4x-evaluation.json`; `make research-xgb` reruns it
    deterministically.
  - `xgboost-cpu` 3.4.1 (2.2 MB, approved by Elie) sits in an optional `research` dependency group. The app and CI
    defaults are unchanged.
- **Second-site scouting (Step B).** `scripts/scout-sites.mjs` and `configs/second-site-candidates.json` cover seven
  regions in 13 districts (India UP and WB potato belts, Bangladesh, Kenya, Uganda, Tanzania, Ethiopia).
  - Facilities are counted with the app's own rules and checked for spread over sub-districts.
  - Overture footprint samples, OpenAerialMap and Maxar Open Data coverage and licences, and World Bank
    electrification are recorded.
  - Total traffic was 26 MB, approved up to 300 MB. Output: `docs/second-site-scouting.md` and its audit JSON.
    `make scout-sites` rebuilds both offline from the cache.
  - **Result:** no region passes the image-detector checklist. Njombe, Tanzania passes the footprint-classifier
    checklist: 882 mills, 881 from a 2021 WFP field survey.
- **Phase 4N, footprint classifier on Njombe grain mills: KILL.** The protocol `d3a9cc02…` was frozen before download
  (65.7 MB, approved up to 200 MB).
  - Data: 673,866 footprints, 830 matched mills, 6 councils held out in turn.
  - Top 1%: logistic 5.7%, XGBoost 5.8%, closest to a major road 4.1%, largest roof 2.8%.
  - Margin +1.6 (−0.3 to 3.4). XGBoost is NOT BETTER than logistic.
  - Results: `docs/phase4n-results.md`. The new `docs/second-site.md` keeps all second-site numbers apart from Rwanda.
- **Answers for judges (Step D):** a suggested-tools section in the Monday guide (20-second answer, slide table, "not
  tested" list), plus updates to the FAQ, validation, README and limitations.
- **Tests:** `tests/test_phase4x.py`, `tests/test_phase4n.py`, `tests/live/scouting.test.mjs`,
  `tests/live/phase4n.test.mjs`. The browser e2e now also checks the model-comparison card (40 checks).
- **Lint:** formatting fixes in `tests/live/make_test_tiles.py`, so `make check` stays green once `live/` is committed.

## Unreleased — Nyabihu snapshot presented as the product (10 Oct, evening)

- **No presentation wording on the page.** The start screen shows **Featured analysis · Rwanda** with one
  button, **Nyabihu · Irish potato cold storage**, instead of "Hero case" and "Replay hero (offline, frozen)".
  The six-step bar and its captions are gone from the default page. The presenter moves through the six
  views with Page Down/Page Up (clicker) or →/←, and Escape returns to free exploration. `?presenter=1` shows the
  controls for rehearsal only. Labels renamed: Why Nyabihu, Verification, Assumptions, Save example districts,
  Synthetic sample. Provenance lists snapshot-relative paths. The app no longer names a person.
- **GeoJSON export (plan item F).** `data/rwanda/hero/export/nyabihu-potato-ranking.geojson` holds 310 ranked
  sites plus 5 siting look-alikes, with evidence labels, units, CRS, licence and verification counts
  (all 0). `make hero-geojson` rebuilds it, and refuses unless the ranking equals expected.json.
  `make hero-repro` now also checks the export is current.
- **Tests:** a wording guard and a GeoJSON test in `tests/live/hero.test.cjs` (32 live tests). The browser preflight
  drives the six views by keyboard and asserts that no "demo/hero/frozen/presenter/guided" text and no step bar
  is visible (24 checks).
- **Does not claim:** any change to rankings, ranges, labels, Phase 4R KEEP +23.9, Canadian KILL or the protocols.
  Cross-checking against a public cooperative/cold-store list (rest of item F) was not done: it needs a download
  approval.

## Unreleased — frozen Nyabihu hero (10 Oct)

- Added real offline replay, SHA-256 manifest, expected dry/rainy ranking and `hero-repro`.
  Acquisition transferred 13.3 MB with Elie's approval. Kora Market remains 142 kWh/day (56–388).
- Added a six-step optional guide (later made keyboard-only; see above), provenance, linked assumptions, source research and descriptive
  sensitivity from the existing 300 draws. No tested single endpoint displaces a top-three site
  beyond rank ten; joint-draw departures are reported separately.
- Added 15 human-review targets, local imagery/phone forms, CSV schemas and per-site printable
  English/Kinyarwanda scripts. The activity-only protocol was approved and hashed before any calls.
  Real imagery checks, calls and field visits remain zero; no human observations were invented.
- Added offline browser preflight and screenshot backups, including saved-analysis and file-URL paths.
  Fixed worker-error fallback for local-file operation; browser tests wait for results instead of
  assuming fixed sub-second execution times.
- `live-siting` is a read-only frozen-artifact integrity check. Historical fitting tools remain
  available, but the demo workflow does not retrain or overwrite the registered model/results.
- Newer NISR 2025/2026 and WorldPop Global 2 references were found and linked only, per Elie's choice.
  Scientific ranges, Phase 4R KEEP +23.9, Canadian KILL, protocols and source training table are unchanged.

## Unreleased — Rwanda siting model, all 30 districts, Monday demo (10 Oct)

- **Phase 4R, Rwanda siting model: KEEP.** Protocol written first (`docs/spec/phase4r-protocol.md`, v1.1),
  then run on 25,281 squares of 1 km in all 30 districts, each district held out in turn. The model
  (roof sizes from footprint geometry, roads, settlement structure) puts 73.1% of documented collection and
  processing points in its top 10%. Counting buildings puts 49.3% there. Margin +23.9 points (13.4 to 34.4).
  The narrower processing-only label had 44 squares, below the registered gate: reported as FEASIBILITY.
  Results: `docs/phase4r-results.md`, `docs/audits/phase4r-evaluation.json`. The training table is in
  `data/rwanda/siting_cells.csv` (SHA-256 `664350e8…`). `node live/tools/train-siting.cjs` reproduces it.
- **Post-hoc label audit.** All 157 documented facilities were read by name. 7 positive squares rested on
  plainly wrong labels: a hotel ("Mille" matched "mill"), a football club ("amata" matched), a café, shops, a
  phone-repair shop, a tile seller. Without them the margin is +23.6 (13.2 to 34.7). Without Kigali it is
  +27.8. The registered verdict is not re-decided. `docs/audits/phase4r-label-audit.json`,
  `live/tools/label-audit.cjs`.
- **Likely sites lens** in the app: the model's score for every square, documented squares outlined, and
  up to 12 look-alikes with no facility on record, each with a check-first card. Labelled PREDICTED.
- **District production for Rwanda:** potato and maize per person by district (NISR SAS 2024 Season A
  shares scaled to 2024 national totals; 2022 census population). For example, Nyabihu has 578 kg of
  potato per person against 62 nationally. Milk stays national. Labelled ESTIMATED.
  `data/rwanda/district_production_2024.csv`.
- **All 30 districts run end to end** (`live/tools/harvest.js`, `docs/rwanda-national-screening.md`).
  Overpass overload had silently dropped OpenStreetMap facilities in 16 districts; requests now retry.
- **Classification fixes from the real data** (all with tests):
  - streets, toilets, hotels, cafés, clubs, campuses and tourism businesses are never collection points;
  - tea factories and tea-leaf collection centres are their own type (not potato, milk or maize);
  - two villages with the same name are told apart.
- **How sure lens** shows the straight-line headcount's picks on the map (H1–H10). **Prepare demo
  districts** saves the six hero districts in the browser so they open in seconds, even offline.
- **Tests:** 24 engine, data and siting tests; browser test 39 checks (including upright look-alike markers).
- **Does not claim:** that a predicted square holds a facility, that documented facilities are complete,
  any field verification (n = 0), or any change to the Canadian Phase 4 result (KILL stands).

## Unreleased — EnaGIS Live data stack (9 Oct, evening)

- **Fix: no ranking in real districts.** Public Overpass timed out (HTTP 504) on buildings and roads, so
  Gasabo found 21 facilities but ranked none. Heavy layers now come from Overture Maps PMTiles, read in the
  browser, with Overpass kept as the fallback. Overture supplies:
  - buildings: OpenStreetMap + Google Open Buildings + Microsoft footprints;
  - roads, rejoined across tile edges;
  - power infrastructure;
  - agricultural places.
- **People per building** is calibrated to WorldPop 2020 population inside the boundary (±20%).
- **Live check, Gasabo:** 338,902 buildings, WorldPop 889,650, 29 sites ranked, 74 s gather, 1.7 s
  analysis.
- **Look-alikes filtered:** a church called "Isoko …", stores filed as warehouses, a broadcaster tagged
  `man_made=works`, a tax "Collection Centre". All are covered by tests.
- **Map:** symbols for each kind of facility and power asset (also on pins, list and legend), a demand
  glow under the top sites, and building footprints from zoom 14 coloured by source in the Map data lens.
  Streets is now the default basemap, falling back to the offline map automatically.
- **Tests:** 13 engine/data tests; browser test now 30 checks, including synthetic Overture archives and
  the Overpass fallback. Decision 0013.
- **Does not claim:** footprints newer than their 2020–2023 imagery, WorldPop 2020 equal to today's
  population, or any field validation (n = 0).

## Unreleased — EnaGIS Live (9 Oct)

- **New `live/` app:** search any place; the browser gathers OpenStreetMap and Open-Meteo data,
  builds dry/rainy road catchments, estimates need for four value chains with 300-draw
  simulations, assigns Robust/Contested/Check first tiers, adds grid distance, solar sizing and a
  straight-line baseline, and writes findings. Five basemaps, six lenses, compare view, offline
  replay of saved analyses, CSV/GeoJSON, site brief. Method in `docs/live-engine.md`; decision 0012.
- **Tests:** `make live-test` (engine, in CI) and `make live-e2e` (browser, services intercepted
  with synthetic data).
- **App:** top-bar rule rendered as a soft brand-coloured shadow.
- **Does not claim:** field validation (n = 0), approved energy parameters, completeness of
  OpenStreetMap, or any change to the registered Canadian results.

## Unreleased — final audit and documentation pass (9 Oct)

- **Brand:** EnaGIS wordmark and icon in the app, site brief and limitations page; navy/emerald palette.
- **App fixes:** map pins no longer overlap each other or panels; status bar shows the region name; exact ties shown as "Tied ×N".
- **Docs:** new README; overview, method, validation, limitations, evidence ledger, data catalogue (generated), reproducibility, scaling, scope and transfer, architecture, glossary, judge FAQ, challenger Q&A, proof of work, team guide, roadmap, AI-use disclosure; CONTRIBUTING, CODE_OF_CONDUCT, CITATION.cff, LICENSE (MIT), LICENSE-DATA; issue and PR templates.
- **Tools:** `scripts/demo_preflight.mjs` (15 browser checks), `scripts/evidence_ledger.py`, `scripts/data_catalogue.py`.
- **Proposals (not adopted):** durum residual bounds, location-conflict region rule, sparse-data stress diagnostic with decline-to-rank rule.
- **Unchanged:** scientific source (`code_hash` `f2b1f095…`), configs, registered protocol, results and verdicts.

## Phase 8 — global map MVP and defense package (9 Oct, `8f90a5b`, CI fixes `533abd8`, `63579eb`)
Offline app with worldwide search, four lenses, exports and site brief. Scientific completion: false.

## Phase 7 — verification toolkit (8–9 Oct, `d5acd20`, `6b16604`)
Freeze, seeded sampling and private-record analysis; synthetic rehearsal only; real n = 0.

## Phase 6 — gated scientific engine (8 Oct, `5953c5f`, `1ee5be4`)
Routing, capacity, Monte Carlo and stability tiers; synthetic end-to-end run; real run gated.

## Phase 5 — offline guided demo (8 Oct, `b22df9f`)
Historical archive in `demo/`.

## Phase 4 — registered siting comparison (8 Oct, `de21725`, `948cf2f`, `19ff881`)
Protocol tagged `preregister-phase4-canada-v1.1`; verdict KILL; hindcast on 52 groups.

## Phase 3 — walking skeleton (7 Oct, `dee3748`)
Real-data pipeline; 261 nodes, 186 ranked; temporary engineering shortlist.

## Phase 2 — offline data spine (7 Oct, `d8dcc66`)
21 pinned sources with hashes and licences.

## Phase 1 — contracts and CI (7 Oct, `2cd9e0f`)

## Phase 0 — scope and architecture lock (7 Oct, `b4cd44c`)
