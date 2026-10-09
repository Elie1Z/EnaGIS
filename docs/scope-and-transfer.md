# Scope and transfer statement

## Which geography and why

**Used:** primary grain elevators in Alberta and Saskatchewan, Canada (development; 261 sites),
with Manitoba (79 sites) reserved as an untouched transfer hold-out. Non-durum wheat, ambient-air
aeration electricity, 2024 harvest / 2024–2025 crop year.
Decision record: [0003](decisions/0003-benchmark-lock.md); global direction: [0002](decisions/0002-global-transfer.md).

**Why:** OSEAS provides no ground truth. Canada offered, under open licences, everything the method
needs to be *tested*: a near-census facility registry with coordinates and storage, regional
production statistics, census boundaries for spatial blocks, OSM roads, and independent delivery
outcomes (CGC shipping points) for a hindcast. That made a preregistered, spatially held-out test
possible. Most energy-access contexts lack at least one of these today.

**The cost of that choice:** Canada is not an energy-access context. Its grid is extensive, so the
pilot tests the *method*, not energy-access impact. It also lacked the operating evidence
(installed fans, electrical capacity) needed to compute a real gap.

## What was validated, and what was not

| Validated | Not validated |
|---|---|
| Reproducible pipeline, provenance, mass conservation, UNKNOWN handling (230 tests, CI) | Energy coefficients, inventory, fan duty |
| One preregistered ML siting test (result: KILL) | That the top 10 are the right sites |
| Shipping-point hindcast on 52 groups (mixed) | Absolute volumes; facility-level throughput |
| Synthetic geography checks in five non-Canadian settings (software portability) | Transfer to Manitoba or any energy-access region |
| | Field verification (n = 0) |

## Exact path to an energy-access region (example: Rwanda maize or coffee)

| # | Need | Candidate open source (to confirm) | Gate |
|---|---|---|---|
| 1 | Facility registry: dryers, warehouses, washing stations, mills, with location and capacity | NAEB washing-station lists; MINAGRI/RAB warehouse registers; programme reports; OSM | Precision class P1–P5 per record; licence |
| 2 | Production by admin unit | NISR Seasonal Agricultural Survey (district/sector); HDX boundaries | Units (t, bags), seasons A/B |
| 3 | Roads and seasonal access | OSM / HOT; HeiGIT road surface | Wet/dry speeds sourced |
| 4 | Service model and parameters | Drying or cooling energy per tonne from engineering literature; equipment surveys | **Human approval** |
| 5 | Electrical supply | REG grid extent; mini-grid lists (EDCL, partners); facility surveys | Three supply states; never infer from absence |
| 6 | Outcome for evaluation | Reported throughput or delivery volumes per facility or cooperative | Untouched spatial blocks |
| 7 | Verification partner | Energy programme or cooperative union | Frozen sample, consent, n ≥ 12 |

Steps and config keys: [scaling.md](scaling.md). Expected result if data is thin: an
**insufficient-data** outcome or a documented baseline fallback is a valid, reportable result.
EnaGIS must not produce a ranking it cannot support.
