# Draft issues (ready to open on GitHub)

Drafted 9 October 2026. They have not been opened yet: opening issues is a public action left to
the maintainer. Each issue uses a template in `.github/ISSUE_TEMPLATE/`.

## Data wanted (each turns an UNKNOWN into an invitation)

| # | Title | Closes | Details |
|---|---|---|---|
| D1 | [data] Aeration fan nameplate kW per elevator or elevator class | 261 UNKNOWN gaps | help-wanted #1 |
| D2 | [data] Electrical service capacity (kVA) for Prairie primary elevators | Supply state | help-wanted #2 |
| D3 | [data] One season of metered aeration kWh at any commercial elevator | kW/kWh calibration | help-wanted #3 |
| D4 | [data] Typical wheat residence time and occupancy at primary elevators | Inventory parameter | help-wanted #4 |
| D5 | [data] Commercial bin airflow and static pressure design values | Airflow / pressure | help-wanted #5 |
| D6 | [data] Regional durum production for 9 suppressed AB/SK regions, or review of the residual-bound proposal | 72 nodes | proposals/durum-residual-bounds.md |
| D7 | [data] Confirm coordinates of Rycroft (G3) and Woodrow (Canada Direct Processing) | 2 nodes | proposals/location-conflict-region-invariance.md |
| D8 | [data] Spring road-ban schedules for AB and SK | Seasonal access, visit window | help-wanted #8 |
| D9 | [data] Field partner for a frozen n ≥ 12 phone check | Field verification n = 0 | help-wanted #10 |
| D10 | [data] Candidate energy-access region with facility registry and production statistics | Transfer | scope-and-transfer.md |

## Good first issues

| # | Title | Files | Done when |
|---|---|---|---|
| G1 | Add a keyboard-only walkthrough check to the demo preflight | `scripts/demo_preflight.mjs` | Tab order reaches list, lenses and card; check passes |
| G2 | Translate the limitations page into French | `web/mvp/limitations.html` | FR page linked from FR UI; numbers unchanged |
| G3 | Export the shortlist as GeoPackage as well as CSV/GeoJSON (PRD core 12) | `scripts/build_demo.py` | `.gpkg` with same rows; test checks row count |
| G4 | Add a test asserting the Tied ×N badge count equals exact-equal kW groups | `tests/`, `web/mvp/app.js` | test passes on built app |
| G5 | Make `scripts/data_catalogue.py` fail CI if `docs/data-catalogue.md` is stale | `scripts/`, CI | CI step diff-checks the generated file |
| G6 | Make `scripts/evidence_ledger.py` run in CI and fail on an unexpected UNKNOWN increase | CI | CI prints counts; threshold documented |
| G7 | Document a minimal regional view package example (synthetic) in `docs/spec/` | `docs/spec/regional-view-package.md` | example validates with `web/view-model.js` |
| G8 | Add `uv sync --python` guidance for Windows Application Control to the README troubleshooting | `docs/reproducibility.md` | reviewed by a Windows user |
| G9 | Improve flat-map label rendering overlap in fallback mode | `web/mvp/app.js` | no overlapping labels in `?map=flat` preflight screenshot |
| G10 | Link each glossary term from first use in method.md | `docs/` | links resolve |
