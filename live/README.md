# EnaGIS Live

**Search any place. EnaGIS gathers open data for it right now, works out who can reach each
collection point by road, estimates the electricity a value chain would need there, and says how
sure it is and what to check first.**

This is the working tool. The Canadian prairie app in `../app/` is the recorded, preregistered
pilot that tested the method where ground truth exists. EnaGIS Live applies the same principles
(evidence labels, UNKNOWN never zero, simpler baselines, honest limits) to any place you search.

## Run it

Pick one of these:

- **Open `live/index.html` in Chrome, Edge or Firefox.** No install, no server, no account.
- **Serve the folder:** `python -m http.server -d live 8080`, then open <http://localhost:8080>.
- **Publish it:** the `live/` folder is a static site and works on GitHub Pages as it is.

Searching needs the internet. Without it you can:

- press **Nyabihu · Irish potato cold storage** (Featured analysis) to open a dated, hashed snapshot of
  real open data; it uses the local map and no public servers. Page Down / Page Up (or → / ←) step
  through six preset views with nothing shown on screen; `?presenter=1` shows them for rehearsal;
- open an analysis you saved earlier ("Save analysis" writes one file that replays offline);
- press **Synthetic sample** to explore a clearly labelled synthetic area.

**Before a presentation**, press **Save example districts** on the start screen once, on the computer
and browser you will present from. It gathers the six example districts (Musanze, Nyabihu, Rubavu,
Gicumbi, Gatsibo, Kirehe) into the browser's cache (kept 14 days), so they then open in seconds, even
without internet.

## What happens when you search

| Step | Source (open, keyless) | What the tool does |
|---|---|---|
| 1. Find the area | Nominatim (OpenStreetMap geocoder) | Gets the official boundary of the district, sector or town |
| 2. Gather | Overpass API (OpenStreetMap) | Markets, cooperatives, mills, stores, milk centres, cold rooms, towns, villages |
| 2. Gather | Overture Maps (PMTiles, read tile by tile) | Every building footprint (OpenStreetMap + Google Open Buildings + Microsoft); roads and paths; power lines, pylons, substations, generators; agricultural places listed by Meta and Microsoft |
| 2. Gather | WorldPop API | Population inside the boundary (2020). Used to calibrate people per building |
| 3. Climate | Open-Meteo historical weather (ERA5), 2024 | Hottest month (sizes cooling loads), rainy months, sunshine (sizes solar) |
| 4. Catchments | Engine | Each building is linked to the site it can reach fastest by road or path. Rain slows earth roads and walking, so dry and rainy catchments differ |
| 5. Need | Engine + NISR statistics | People in reach × production per person × share handled by the site gives volume; physics turns volume into kWh per peak day for the chosen value chain. In Rwanda, production per person is the **district** figure (NISR Seasonal Agricultural Survey 2024 and 2022 census), so Nyabihu's potato belt counts about 578 kg per person a year instead of the national 62 |
| 6. How sure | Engine | Every assumption is varied 300 times. Sites that stay in the top 10 are **Robust**, the rest **Contested** or **Check first** |
| 7. Supply | Engine | Distance to mapped grid, and the solar array that would cover one peak day |
| 7b. Siting model | `js/siting.js` (Phase 4R) | Scores every 1 km square for how much it looks like places where collection or processing points are documented (roof sizes, building density, roads, grid, settlements), and lists unrecorded look-alikes to check. PREDICTED; its registered test result is shown on screen |
| 8. Respond | Interface | Ranked list, findings in plain language, site card with the one question to ask first, CSV/GeoJSON, printable site brief |

Value chains available: cold storage of Irish potato, milk cooling at collection, maize milling,
maize drying. Switching value chain re-analyzes instantly with the data already gathered.

## Map views

- **Basemaps** change what the map looks like: Paper (offline), Light, Streets, Satellite, Terrain.
- **Lenses** change the question:
  - Where first
  - Harvest (estimated production)
  - Energy (mapped grid and solar)
  - Access (dry vs rainy roads)
  - Map data (where the map is thin)
  - How sure (with the simple headcount's picks marked H1–H10 on the map)
  - Likely sites (siting model: predicted squares and look-alikes to check)
- **Compare** puts two basemaps side by side with a slider (for example, your lens over Satellite).
- **Simple / Expert** switches between words only and full ranges, drivers and evidence.

## Honest limits

- **What it sees.** Facilities only show if they are mapped in OpenStreetMap or listed in Overture.
  Buildings are near-complete thanks to Google and Microsoft footprints, but those come from 2020–2023
  imagery. Hatched squares mean "not yet known", not "empty".
- **First search size.** A district's first search downloads tens of MB of map tiles. Later searches
  use the browser's cache. Use "Save analysis" to keep a copy for a demo.
- Production per person is a district average in Rwanda (national elsewhere, or for milk); it still varies inside a district.
- Agricultural facilities are rarely documented in open maps (a handful per district in Rwanda). The siting
  model is tested against what is documented, which depends on who mapped what.
- Energy factors are screening ranges, not approved or metered.
- A mapped power line nearby does not mean the site is connected.
- No field verification yet (n = 0).

Full method: [`docs/live-engine.md`](../docs/live-engine.md). Decision record:
[`docs/decisions/0012-live-analysis-engine.md`](../docs/decisions/0012-live-analysis-engine.md).

## Nyabihu snapshot checks

From the repository root: `make live-test live-siting live-e2e hero-repro`. If Make is unavailable,
run these same recipes directly:

```powershell
node --test tests/live/engine.test.cjs tests/live/overture.test.cjs tests/live/siting.test.cjs tests/live/hero.test.cjs
node live/tools/verify-siting.cjs
node tests/live/e2e.cjs outputs/live-e2e
node scripts/demo_preflight_live.mjs outputs/demo-preflight-live
node live/tools/hero-repro.cjs
```

Browser checks require Playwright and an installed Chromium browser. Set
`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` to a local Chrome/Edge executable when using an existing
browser, and `NODE_PATH` to the installed package directory if it is outside normal module paths.
Tests do not download browsers or public data. Preflight writes screenshots and saved JSON.

`hero-build` regenerates the assumption sheet and compressed browser bundle while requiring the
existing expected ranking to match. `live-siting` verifies frozen hashes/results without fitting.
The original `train-siting.cjs` and `label-audit.cjs` remain historical reproduction tools; they
write registered artifacts and must not be run as part of this frozen-demo workflow.

The [verification kit](../data/rwanda/hero/README.md) has 15 printable pages and CSV templates.
Real imagery reviews, calls, and a 3–4 minute recording on Elie's presenting laptop remain human
acceptance items. Newer datasets are [linked references](../docs/hero-data-freshness.md), not
unreviewed substitutions into the frozen case.

## Files

| File | Role |
|---|---|
| `js/config.js` | Value-chain models, ranges, country statistics with sources, OSM tag rules |
| `js/engine.js` | Pure, deterministic analysis (no network, no page). Also runs in a background worker |
| `js/sources.js` | Live gatherers for Nominatim, Overpass, WorldPop and Open-Meteo, with a browser cache |
| `js/overture.js` | Overture Maps reader: tiles → buildings, roads (rejoined across tile edges), power, places |
| `js/icons.js` | Map symbols for each kind of facility, settlement and power asset |
| `js/siting.js` | Siting model: 1 km cell features, logistic regression, leave-one-district-out evaluation, in-app scoring |
| `js/siting-model.js` | The frozen siting model and its registered evaluation (generated by `tools/train-siting.cjs`) |
| `tools/harvest.js` | Builds the national training table by running the same gatherers over every district |
| `tools/train-siting.cjs` | Runs the registered evaluation (`docs/spec/phase4r-protocol.md`) on `data/rwanda/siting_cells.csv` and freezes the model |
| `tools/label-audit.cjs` | Post-hoc label audit: reruns the same test with mislabelled squares removed (`docs/audits/phase4r-label-audit.json`); run after `train-siting.cjs` |
| `tools/national-report.cjs` | Writes `docs/rwanda-national-screening.md` from the harvest's district summaries |
| `vendor/enagis-tiles.js` | PMTiles and vector-tile decoders (BSD-3-Clause, see `vendor/LICENSE-tiles.txt`) |
| `js/app.js` | Interface: search, live step log, lenses, basemaps, compare, site card, exports |
| `js/synthetic.js` | Invented demo area for offline exploration (always labelled SYNTHETIC) |
| `js/world-data.js` | Natural Earth countries and places (public domain) for the offline basemap |

Tests:

- **Engine, data and siting:** `node --test tests/live/engine.test.cjs tests/live/overture.test.cjs tests/live/siting.test.cjs`.
- **Browser:** `node tests/live/e2e.cjs` (needs Playwright). Live services are intercepted with synthetic
  data, including small synthetic Overture archives in `tests/live/tiles/`. Rebuild those with
  `node tests/live/make_test_tiles.cjs && python3 tests/live/make_test_tiles.py`.

## Licences

Code MIT. Data:

- **OpenStreetMap:** © contributors, ODbL 1.0 (exports derived from it stay ODbL).
- **Overture Maps Foundation:** buildings, transportation and base under ODbL 1.0 (Google Open Buildings
  CC BY 4.0 / ODbL; Microsoft ML Building Footprints ODbL); places CDLA-Permissive-2.0.
- **WorldPop:** CC BY 4.0.
- **Open-Meteo:** CC BY 4.0.
- **Natural Earth:** public domain.
- **Basemap tiles:** OpenFreeMap, Esri (satellite) and OpenTopoMap (CC-BY-SA), each with on-map attribution.
