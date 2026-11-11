# EnaGIS Live

**Search any place. EnaGIS gathers open data for it right now, works out who can reach each
collection point by road, estimates the electricity an agricultural service would need there, and says how
sure it is and what to check first.**

This is the working tool. The Canadian prairie app in `../app/` is the recorded, preregistered
pilot that tested the method where ground truth exists. EnaGIS Live applies the same principles
(evidence labels, UNKNOWN never zero, simpler baselines, honest limits) to any place you search.

## Run it

Pick one of these:

- **Open `live/index.html` in Chrome, Edge or Firefox.** No install, no server, no account.
- **Serve the folder:** `python -m http.server -d live 8080`, then open <http://localhost:8080>.
- **Publish it:** the `live/` folder is a static site and works on GitHub Pages as it is.
- **Netlify Drop:** run `python -m scripts.package_netlify` from the repository root, then drop
  `outputs/netlify-drop/EnaGIS-Netlify-Drop.zip` at <https://app.netlify.com/drop>.
  See [packaging instructions](../docs/netlify-drop.md).

Searching needs the internet. Without it you can:

- choose **Open saved analysis** on the landing page to reopen a previous study;
- load the archived [`saved-analysis.json`](../data/rwanda/hero/nyabihu-potato/saved-analysis.json)
  for the dated Nyabihu case, using the local geographic basemap.

The landing page opens on a rotating satellite globe. Search a place or coordinates and select the
result to fly into the area while data loads. Rotation can be paused and follows reduced-motion
preferences. Large regions open as overviews and require a smaller study area for detailed analysis.
Choose a service after arrival. Save the completed analysis to retain inputs and assumptions for offline use.

## Agricultural services

| Service | Energy calculation |
| --- | --- |
| Cold storage | Refrigeration and holding electricity for reported eligible produce |
| Cooling | Produce pull-down cooling electricity |
| Milling | Electricity for grain milling |
| Drying | Electricity for fans and handling; heat requires separate inputs |
| Shelling and threshing | Equipment electricity per tonne supplied with provenance |
| Oil pressing | Equipment electricity per tonne supplied with provenance |
| Feed preparation | Grinding and mixing electricity per tonne supplied with provenance |

Users choose the service directly. Relevant production groups are combined behind the scenes and
disclosed under **What this service estimate covers**. The current Rwanda pack covers 11 reported
crop/product groups, with local potato/maize estimates where available and national proxies for other
components. Coverage is partial. Each service is a separate scenario and overlapping production must
not be added across services.

The first four services use INFERRED operating ranges transferred from existing screening equations.
Product compatibility, separate storage temperatures and actual equipment need local assessment.
The three additional services show mapped candidates while energy remains UNKNOWN until sourced
equipment figures are entered under **Assumptions**. Other countries need sourced local production
inputs. The current manual total is expressed in kg/person/year.

Service changes reuse gathered geography and reset operating overrides. Saved analyses retain scenario
versions, production sources and equipment evidence. Old commodity-specific saved files remain readable.
See the [service method and verification](../docs/proposals/service-screening-v1.md).

## What happens when you search

| Step | Source (open, keyless) | What the tool does |
|---|---|---|
| 1. Find the area | Nominatim (OpenStreetMap geocoder) | Gets the official boundary of the district, sector or town |
| 2. Gather | Overpass API (OpenStreetMap) | Markets, cooperatives, mills, stores, milk centres, cold rooms, towns, villages |
| 2. Gather | Overture Maps (PMTiles, read tile by tile) | Every building footprint (OpenStreetMap + Google Open Buildings + Microsoft); roads and paths; power lines, pylons, substations, generators; agricultural places listed by Meta and Microsoft |
| 2. Gather | WorldPop API | Population inside the boundary (2020). Used to calibrate people per building |
| 3. Climate | Open-Meteo historical weather (ERA5), 2024 | Hottest month (sizes cooling loads), rainy months, sunshine (sizes solar) |
| 4. Catchments | Engine | Each building is linked to the site it can reach fastest by road or path. Rain slows earth roads and walking, so dry and rainy catchments differ |
| 5. Need | Engine + available statistics or sourced manual inputs | Relevant production per person × people in reach × share handled gives volume. Service equations estimate kWh when operating inputs are available. Each production component declares its district or national basis. |
| 6. How sure | Engine | Every assumption is varied 300 times. Sites that stay in the top 10 are **Robust**, the rest **Contested** or **Check first** |
| 7. Supply | Engine | Distance to mapped grid, and the solar array that would cover one peak day |
| 7b. Siting model | `js/siting.js` (Phase 4R) | Within the Rwanda training scope, scores supported 1 km squares for resemblance to documented processing or collection locations. Outside that scope, predictions are withheld. |
| 8. Respond | Interface | Ranked list, findings in plain language, site card with the one question to ask first, CSV/GeoJSON, printable site brief |

Where energy inputs are missing, mapped candidates remain available with an explanation of the required evidence.

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
- Production components use disclosed local or national proxies where available. Other locations require local inputs.
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
| `js/config-v2.js` | Current service definitions, commodity recipes, operating ranges, production evidence and validation |
| `js/engine-v2.js` | Current deterministic analysis, production aggregation, scope guards and worker calculations |
| `js/config.js`, `js/engine.js` | Hash-pinned historical runtime for archived reproduction |
| `js/landing.js`, `landing.css` | Satellite globe, search, saved-analysis entry and flight into the workspace |
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

- **Service upgrade, 10 November 2026:** 240 Python tests, 74 Node tests and 126 browser checks passed.
- **Service engine:** `node --test tests/live/services.test.cjs`.
- **Service interface:** `node tests/live/services-ui.cjs`.
- **Complete Live checks:** `make live-test live-e2e hero-repro`.

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
