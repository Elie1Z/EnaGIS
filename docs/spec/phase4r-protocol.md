# Phase 4R protocol: Rwanda facility-siting model (frozen before evaluation)

**Status:** frozen 10 October 2026, before any real Rwanda cell was evaluated. The SHA-256 of this file is
recorded in `docs/audits/phase4r-evaluation.json` together with the results. Any change after freezing is a
new protocol version and must be reported as such.

**Relation to Phase 4 (Canada, KILL).** Phase 4 tested whether a road-accessible production feature improves
prediction of documented grain elevators on the Canadian prairies. It did not (margin −4.05 points, KILL).
Phase 4R asks a different, Rwanda-specific question with different features. It does not replace or re-run
Phase 4, and Phase 4's verdict stands.

## Question

From open, label-independent map layers, can a model rank 1 km cells in a **held-out Rwandan district** so
that cells holding a documented agricultural processing or storage facility come out on top more often
than with the best simple rule (most people, densest area, nearest major road, nearest town, nearest grid)?

## Units, labels and data

- **Unit:** 1 km × 1 km cell on a local metric grid, kept if its centre lies inside the district boundary
  (OpenStreetMap boundary via Nominatim).
- **Positive label (`y`):** the cell contains at least one documented facility of type mill, milk collection
  centre, cold store, coffee washing station, agricultural warehouse or agro-processing works, as classified by
  the EnaGIS Live rules (`live/js/engine.js classifySite`, `live/js/overture.js classifyPlace`) from
  OpenStreetMap (Overpass) and Overture places (confidence ≥ 0.5).
- **Unlabelled cells** are background, **not** proven absences. The model learns where facilities are
  *documented*, which is shaped by who mapped what. This is stated wherever results are shown.
- **Sensitivity label (`y_any`):** also counts markets and cooperatives. Reported descriptively only.
- **Data:** Overture Maps release `2026-09-23.1` (buildings with footprint area, transportation, base/power,
  places) read at zoom 14 (power at 13); OpenStreetMap via Overpass for facilities and settlement points.
  Retrieval date and tile counts are recorded per district.

## Features (fixed list, in this order)

1. log(1 + buildings in the cell)
2. log(1 + buildings in the surrounding 5 × 5 cells)
3. log(1 + footprints ≥ 200 m² in the cell)
4. log(1 + footprints ≥ 600 m² in the cell)
5. log(1 + largest footprint in the cell, m²)
6. major road length in the cell (motorway–tertiary), km, capped at 5
7. log(1 + minor road and track length in the cell, km)
8. log(1 + distance from cell centre to the nearest major road, km), capped at 15 km
9. log(1 + distance to the nearest mapped power line or pylon, km), capped at 25 km
10. log(1 + distance to the nearest town or village point, km), capped at 15 km
11. share of the cell's buildings in dense blocks (≥ 100 buildings per 250 m cell)

No feature uses facility locations, places listings, production statistics or any model output.

## Arms

- **Model:** L2-regularised logistic regression on standardised features, λ = 1, balanced class weights,
  IRLS (`live/js/siting.js fit`).
- **Ablation (descriptive):** the same model without features 3–5 (roof size).
- **Baselines (no training):** most buildings in the cell; most buildings within 2 km; closest to a major
  road; closest to a town or village; closest to the mapped grid.

## Validation and metric

- **Leave-one-district-out:** for each district, the model is fitted on all other districts and scores the
  held-out district's cells.
- **Primary metric:** pooled recall at the top 10% — of all positive cells in held-out districts, the share
  that falls in the top 10% of its own district's cells. Ties at the cut-off count fractionally.
- **Interval:** cluster bootstrap over districts with at least one positive, 2,000 draws, seed 20261011,
  2.5–97.5 percentiles. The strongest baseline is recomputed in every draw.
- **Secondary (descriptive):** recall at the top 20%, pooled AUC, per-district captures, roof-size gain,
  coefficient sign stability across folds.

## Gates and decision rule

- **Feasibility gate:** at least 60 positive cells in at least 6 districts. If not met, the result is
  reported as **FEASIBILITY** (not enough documented facilities to test), with counts.
- **KEEP** if the lower 2.5% bound of (model − strongest baseline) recall at the top 10% is above zero.
  Otherwise **KILL**. Both outcomes are published.
- **Use in the app if KEEP:** shown as a PREDICTED layer ("likely processing or storage sites") and as
  "look-alike cells with no documented facility: check". It never changes the energy-requirement ranking.
  **If KILL:** the layer is shown only as an experimental view with the verdict on screen.

## What this cannot show

It does not show that a predicted cell has a facility, that a documented facility operates, or anything
about energy demand. Recall is measured only against documented facilities. A field or phone check of
predicted cells is the next validation step.

## Amendment v1.1 (10 October 2026, before any evaluation was run)

**What we saw (counts only, no model results):** while gathering the first districts, documented processing
or storage facilities turned out to be very rare in open map data. Musanze, Rwanda's main potato district, has
2 cells with one; Nyabihu has none. The primary label will very likely fail the feasibility gate
(≥ 60 positive cells in ≥ 6 districts). Two classification bugs were also found and fixed before evaluation:
streets whose name contains "market" or "mill" were read as facilities, and the Kinyarwanda word for milk
("amata") matched inside place names such as Nyamata. Rows from districts gathered before the fix are rebuilt.
Two more look-alike rules were added before evaluation, after reading the district summaries (names only):
places named as churches, schools, campuses, clubs, institutes, hotels or tourism businesses are never
collection points, even when their name contains "isoko" (market, but also "source") or their listing
category is agricultural. The OpenStreetMap facility query had failed (server overload) in 16 of 30
districts on the first pass; it was fetched again with retries before evaluation, and every district's
rows were rebuilt from the cache with the final rules.

**Amendment:** the v1 label (`y`, processing or storage only) is still evaluated and reported first, with the
gate applied exactly as written. If it fails the gate, its result is **FEASIBILITY** and the **primary label
becomes `y_any`**: the cell holds at least one documented agricultural aggregation or processing point
(the v1 types plus markets and cooperatives). These are the candidate aggregation nodes of the EnaGIS PRD
(§5: collection centre, washing station, cooperative, market or warehouse). Features, model, baselines,
metric, interval, seed, gate and keep rule are unchanged. The amendment is decided on label counts alone,
before any model or baseline has been scored on real data.
