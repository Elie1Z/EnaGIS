# Phase 4N protocol: footprint classifier for grain mills, Njombe Region, Tanzania (second site, track C1)

**Status:** frozen 11 October 2026, before any Njombe footprint was downloaded or scored. Its SHA-256 is in
`docs/spec/phase4n-protocol.sha256` and is copied into `docs/audits/phase4n-evaluation.json`. Changes after freezing
are dated amendments at the end of this file. Results are reported whichever way they go.

**Why Njombe.** Second-site scouting (`docs/second-site-scouting.md`) tested seven candidate regions. Njombe is the
only one that passes the footprint-classifier checklist: 882 documented processing points in all 6 district councils,
with redistributable labels (OpenStreetMap, ODbL). 881 of them come from one field survey ("WFP Field Survey 2021,
OMDTZ"), and all are grain mills. No candidate passes the image-detector checklist, so no image detector is trained.
This is a separate site and question. Nothing here changes Rwanda (Phase 4R KEEP, Phase 4X) or Canada (Phase 4 KILL).

## Question

Using only label-free footprint geometry and mapped context, can a model rank the building footprints of a **held-out
district council** so that footprints holding a surveyed grain mill come out on top more often than the simplest rule,
largest roofs first? And does XGBoost do better than a logistic regression here?

## Data (all retrieved after this freeze; release ids and SHA-256 recorded)

- **Boundary:** Njombe Region, OpenStreetMap relation 3775101 (Nominatim polygon, simplification 0.003°).
- **Councils:** the 6 district councils, admin level 5 (Nominatim polygons by relation id, simplification 0.002°). They
  are Njombe Town Council, Njombe District Council, Ludewa, Makambako Town, Wanging'ombe and Makete. Footprints whose
  centroid falls in no council polygon (simplification gaps) are excluded and counted.
- **Footprints (unit of analysis):** every Overture Maps building (release 2026-09-23.1, buildings theme, zoom 14)
  whose centroid lies inside the region boundary. Each building is kept once (the tile holding its centroid);
  underground parts are dropped.
- **Roads:** Overture transportation theme, same release, zoom 14 (segments with their class).
- **Settlements:** OpenStreetMap `place=city|town|village` nodes. **Grid:** OpenStreetMap `power=line|minor_line|tower|pole`.
  Both come from Overpass.
- **Labels:** OpenStreetMap elements inside the region that the app's `classifySite` rules mark `mill` (scouting
  retrieval of 10 Oct 2026). Each mill is matched to the footprint with the nearest centroid within **30 m**.
  A footprint matched by at least one mill is positive. Mills with no footprint within 30 m are reported as unmatched
  and not used. All other footprints are background, not proven absences.
- **CRS and units:** features are computed in UTM zone 36S (EPSG:32736), metres. Inputs are EPSG:4326 lon/lat.

## Features (fixed list, in this order)

1. log(footprint area, m²)
2. log(perimeter, m)
3. elongation: long ÷ short side of the minimum rotated rectangle
4. rectangularity: area ÷ minimum-rotated-rectangle area
5. log(1 + other buildings within 200 m)
6. log(1 + other buildings within 1 km)
7. area ÷ largest area among buildings within 200 m (itself included; 1 = largest nearby)
8. log(1 + distance to the nearest major road, m), major = motorway/trunk/primary/secondary/tertiary, capped at 15 km
9. log(1 + distance to the nearest road of any class, m), capped at 5 km
10. log(1 + distance to the nearest settlement point, m), capped at 15 km
11. log(1 + distance to the nearest mapped power line or support, m), capped at 25 km

No feature uses mill locations, the survey, names, places listings, the footprint's geometry source or any model output.
Road distances use segment vertices densified every 25 m.

## Arms

- **Logistic (primary model):** as Phase 4R. L2-regularised (λ = 1), standardised features, balanced class weights,
  IRLS.
- **XGBoost:** the Phase 4X settings (depth 3, 200 trees, learning rate 0.05, subsample 0.8, min_child_weight 5,
  λ 1, balanced weights, seed 20261012, no tuning). The one change, decided now for computing cost with about a
  million rows, is `tree_method="hist"`, `max_bin=256`, `n_jobs=4`. This is deterministic on CPU.
- **Baselines (no training):** largest roof first (area); most buildings within 200 m; closest to a major road.

## Validation and metrics

- **Split:** leave one council out (6 folds). Each arm is fitted on the other five councils.
- **Gate:** ≥ 300 matched positive footprints in ≥ 6 councils; otherwise **FEASIBILITY**.
- **Primary metric:** pooled recall at the **top 1%**. This is the share of positive footprints in the top 1% of their
  own council's footprints (cut-off m = ceil(0.01·n)), with fractional ties as in Phase 4R.
- **Secondary (descriptive):** recall at top 5%, pooled AUC, per-council captures, held-out calibration (prior-corrected
  ECE and Brier, as Phase 4X).
- **Intervals:** paired cluster bootstrap. Clusters are 10 × 10 km blocks of the UTM grid that hold at least one
  positive; each positive's capture is fixed by its council's cut-off. 2,000 draws, mulberry32, seed **20261015**,
  2.5–97.5 percentiles.

## Decision rules

1. **Footprint classifier (primary):** **KEEP** if the lower 95% bound of (logistic − strongest baseline, recomputed in
   every draw) at the top 1% is above zero; otherwise **KILL**. XGBoost's own margin over the strongest baseline is
   reported with the same rule, descriptively.
2. **XGBoost vs logistic:** **XGBOOST BETTER** only if it is ahead by ≥ 3.0 points, the paired 95% interval is above
   zero, and its ECE is ≤ logistic + 0.01. Otherwise **NOT BETTER**.

## Leakage check (descriptive, decided now)

The surveyors may have traced buildings around mill points, so mill footprints could come more often from OpenStreetMap
tracing than from the Google/Microsoft detectors. Shape features would then partly encode who mapped them. The check
reports the geometry-source shares of positive and background footprints. It also reruns the primary comparison on
footprints from the machine-learning sources only, descriptively.

## Outputs

`docs/audits/phase4n-evaluation.json`, `docs/phase4n-results.md`, and a "Second site" section in the documentation,
kept apart from the Rwanda numbers. No mill names or contact numbers are published. The footprint table stays in the
gitignored `outputs/` folder; its SHA-256 is recorded.

## What this cannot show

It cannot show that a predicted footprint is a mill, or anything about energy demand. Labels come from one 2021 survey
with unknown completeness: unsurveyed mills sit in the background and lower measured recall. The model is not
field-verified (n = 0). Grain mills are not cold stores; a result here does not transfer to cold storage.
