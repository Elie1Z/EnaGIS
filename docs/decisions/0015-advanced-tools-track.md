# 0015: Testing the suggested tools (XGBoost, image detectors) with evidence

Status: **implemented**, 10–11 October 2026, as a team decision.

## Context

The challenge brief suggests YOLO, XGBoost, GeoPandas/Rasterio and Earth Engine for detecting or predicting
agro-storage and processing sites. EnaGIS used a logistic regression on Rwanda and had not tested those tools. Our
earlier explanation, that the tools were inconvenient, was an opinion and not evidence.

## Decision

1. **XGBoost is tested, not assumed.** Phase 4X compares it with the registered Phase 4R logistic model under a
   protocol hashed before scoring: same table, features, held-out districts and metric, fixed settings, and a paired
   bootstrap. The rule was to adopt XGBoost only with ≥ +3 points, an interval above zero and calibration not worse.
   **Result: TESTED, NOT BETTER** (−9.0 points, −15.1 to −3.3). The app keeps the logistic model and shows the
   comparison. Phase 4R's KEEP is not re-decided.
2. **Image detectors need open imagery and open labels at the facilities.** `scripts/scout-sites.mjs` records, for each
   candidate region in `configs/second-site-candidates.json`:
   - documented facilities, counted with the app's own rules;
   - their spread over sub-districts;
   - Overture footprints and roof sizes;
   - OpenAerialMap and Maxar Open Data coverage and licences;
   - national electrification.

   The checklist decides whether a footprint classifier (C1) or an image detector (C2) can run. The result is in
   `docs/second-site-scouting.md`. A track runs only where its checklist passes. If none passes, the scouting record is
   the answer.
   **Result:** no region passes C2, so no detector is trained. Only Njombe, Tanzania passes C1: 882 grain mills, 881
   from a 2021 WFP field survey.
3. **C1 ran on Njombe (Phase 4N)**, under a protocol frozen before the download.
   **Result: KILL.** Logistic finds 5.7% of mills in the top 1%, against 4.1% for "closest to a major road":
   +1.6 points (−0.3 to 3.4). XGBoost is NOT BETTER. All second-site numbers live in `docs/second-site.md`, apart from
   Rwanda's.
4. **Research dependencies stay out of the app.** `xgboost-cpu` 3.4.1 sits in an optional `research` dependency group.
   The browser app, `make check` and CI defaults are unchanged. Network scouting is explicit
   (`node scripts/scout-sites.mjs`). `make scout-sites` only rebuilds the report from the cache.

## Consequences

- Judges get a recorded answer instead of an opinion.
- A tuned XGBoost comparison would need a new protocol with an inner leave-one-district-out search declared in
  advance. That is not done.
- Labels for any second site come from OpenStreetMap: incomplete, sometimes wrong, never field-verified (n = 0).
