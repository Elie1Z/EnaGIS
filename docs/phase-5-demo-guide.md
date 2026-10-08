# Phase 5 demo guide

## Open it

Open `demo/index.html` in a current Chrome, Edge or Firefox browser. Keep the complete folder
together. The page uses local assets and embedded public data; no internet, account, API key
or runtime server is required. The repository's checked-in `demo/` is a ready presentation.
Read its `README.md` for claims and rights. For WebGL-free devices, the schematic fallback
appears automatically; `index.html?map=schematic` selects it explicitly when served for testing.

Click **Start guided demo**. The guide has Previous, Next, Finish and Close controls; Escape
closes it. You can select map pins or list rows, find a site/operator, inspect the complete
node card, and switch among the three views throughout the walkthrough. Nearby pins separate
for readability; source coordinates retain their dots and P2 precision.

## Three-minute presentation

| Time | Screen / action | Say / show |
|---|---|---|
| 0:00–0:25 | Start guide → Investigate | “Where should a site-assessment team investigate first? We turn public evidence into a short list and a concrete next question.” Show 261 candidates, 186 scenario estimates and ten sites. |
| 0:25–1:00 | Next → select Dixon, then a Melfort operator | Show identity, reported storage and estimated concurrent fan kW. “The supply is undocumented in this source, so the electrical margin stays unknown. This question is what we resolve before a decision.” Same-town elevators remain distinct. |
| 1:00–1:40 | Next → Follow the evidence | Trace pinned inputs → conserved assignment → inventory → fan duty → documentation → shortlist. Show 16 known and nine unknown origins. Unknown does not become zero. Open an actual source/method and the explicit temporary parameters. |
| 1:40–2:30 | Next → Test against simpler choices | Show 155 complete CCS, 60 positives, seven positive CAR blocks. Full model recall 35.7%; production-only 39.8%. The frozen margin interval is negative and the verdict is KILL. Read the recorded interpretation. Shipping-point hindcast is a separate diagnostic; it is not validation of site energy. |
| 2:30–3:00 | Next → Investigate, export, Finish | “We leave with a transparent first-visit list and the evidence needed to challenge it. We verify current licensing/location, inventory and actual fan/supply duty next.” Export the CSV or a selected trace. |

Dixon is first because of the recorded ordering; five shortlisted nodes share the same
unrounded requirement. Stable IDs break ties, so do not claim Dixon is scientifically more
urgent than those peers. The top ten are all Saskatchewan in this particular temporary run;
the development footprint and coverage include Alberta. No list has been curated for the pitch.

## Answers to likely reviewer questions

| Question | Evidence to open |
|---|---|
| Where did this location/number come from? | Node card → evidence/uncertainty, full JSON trace; Follow the evidence → source date, licence, method and checksum. |
| Is this a measured energy deficit? | No. Fan kW is ESTIMATED under temporary assumptions. Storage is OBSERVED all-crop tonnes. Installed electrical capacity/margin are UNKNOWN. |
| Is the ranking robust? | Not assessed. Equal deterministic endpoints are not uncertainty intervals. No Monte Carlo tier or field accuracy is claimed. |
| Does the extra siting feature improve recall? | No demonstrated improvement from this proxy-based accessible-production feature. It is not evidence against road-catchment logic. Report intervals and counts descriptively because CAR blocks are few. |
| What is validated? | Artifact integrity, arithmetic constraints and conservation. The shipping-point hindcast is retrospective/diagnostic; absolute volumes, commercial energy and field hits are unvalidated. Field sample n = 0. |
| Could this work elsewhere? | Regions enter through adapters/configuration. Local source coverage and untouched spatial transfer must be evaluated; this pilot does not establish worldwide accuracy. Manitoba remains untouched. |

## Rebuild and verification

From the repository root, after the ordinary pinned environment setup:

```sh
uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py
uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py --verify
uv run --offline --locked --cache-dir .uv-cache python -m pytest
uv run --offline --locked --cache-dir .uv-cache python -m ruff check .
uv run --offline --locked --cache-dir .uv-cache python -m ruff format --check .
uv run --offline --locked --cache-dir .uv-cache python -m enagis smoke --fixture tests/fixtures/phase1.json
```

`make demo`, `make verify-demo` and `make check` expose the same operations. The exporter reads
the checked-in historical evidence archive and already generalized map context. A different
output directory is supported with `--output outputs/phase5-rebuild`. The exact index.html
bytes and all asset hashes should match the checked-in demo for the same exporter/template.
No model fitting, scoring, outcome acquisition or scientific pipeline rerun is required.

To derive context from the already pinned local spine, use this first-export command:

```sh
uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py --phase3 outputs/phase3 --phase4 outputs/phase4 --spine data/processed/phase2 --output outputs/phase5-fresh
```

This reads AB/SK major roads and boundary context, validates consumed file hashes, clips to
the development footprint, simplifies display geometry and leaves all original scientific
files untouched. It cannot overwrite a scientific input directory. A different Phase 3
index fails the comparison-link check, even if numerical ranks look similar.

## Deliverables and rights

The folder supplies shortlist CSV and GeoJSON, per-site trace download, separate ODbL
roads.geojson, source/vendor licences, a checksum manifest and verified original run artifacts.
All 11 displayed public snapshots permit redistribution. OSM attribution stays on the map
and in the bundle, and its derivative is separately downloadable. App code is MIT; MapLibre
5.12.0 is vendored with upstream BSD and dependency notices. Baseline results come from the
registered v1.1 experiment, with the remote commit/tag included in the evidence view.

This is not the PRD's final scientific uncertainty/verification product. Commercial
parameters, harvest season profiles, real supply, independent review and field/transfer
evaluation still need evidence. Do not call the demonstration a feasibility study.
