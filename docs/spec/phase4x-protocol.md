# Phase 4X protocol: gradient-boosted trees vs the registered logistic siting model (Rwanda)

**Status:** frozen 10 October 2026, before XGBoost or any new arm was scored on the Rwanda table. Its SHA-256 is
in `docs/spec/phase4x-protocol.sha256` and is copied into `docs/audits/phase4x-evaluation.json`. Any change after
freezing is a dated amendment at the end of this file, reported as such; the results of the original version are
still reported.

**Relation to Phase 4R.** Phase 4R (`docs/spec/phase4r-protocol.md` v1.1, SHA-256 `1a3bc8ca…`) is registered and
its verdict (KEEP, +23.9 points) stands whatever Phase 4X finds. Phase 4X asks a new question on the same frozen
table. It does not refit, relabel or overwrite any Phase 4R artifact. The Canadian Phase 4 KILL is untouched.

## Question

On the same 25,281 Rwandan 1 km cells, the same 11 label-free features and the same leave-one-district-out test,
does a gradient-boosted tree model (XGBoost) rank held-out cells holding a documented aggregation or processing
point better than the registered logistic regression? The challenge brief suggests XGBoost; this test decides
with data whether the app should use it.

## Data (unchanged, not rebuilt)

- Table: `data/rwanda/siting_cells.csv`, SHA-256 `664350e8aa446b228ee541143621a3cdaeaca6250b4f6c136355f08565b11c92`,
  25,281 rows, 30 districts. The run aborts if the hash differs.
- Features: the 11 Phase 4R features, computed exactly as in `live/js/siting.js` (`FEATURES`), in that order.
- Label: `y_any` (the Phase 4R v1.1 primary label: documented mill, milk collection centre, cold store, coffee
  washing station, agricultural warehouse, agro-processing works, tea factory, market or cooperative).
  The narrower label `y` failed the Phase 4R feasibility gate (44 cells) and is reported here as counts only.
- Unlabelled cells are background, not proven absences.

## Arms

1. **Logistic (reference):** the registered Phase 4R model, ported to Python (`research/phase4x/`): L2-regularised
   logistic regression on standardised features (population standard deviation), λ = 1 on non-intercept
   coefficients, balanced class weights (n / 2·n_pos and n / 2·n_neg), IRLS with at most 50 iterations, stop when
   every step is below 1e-7.
   **Reproduction gate:** before XGBoost is scored, the port must reproduce the registered result. The checks are
   model recall at top 10% = 73.1% and best-baseline recall = 49.3% (most buildings in the cell), both to 0.1
   point. The margin must be +23.9 points with a 95% interval of 13.4 to 34.4, using seed 20261011 and the
   registered bootstrap generator (mulberry32). If any of these fails, the run stops and no XGBoost result is
   reported as a comparison.
2. **XGBoost (challenger):** `xgboost-cpu` 3.4.1 `XGBClassifier`, fixed hyperparameters, no tuning:
   `max_depth=3`, `n_estimators=200`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=1.0`,
   `min_child_weight=5`, `reg_lambda=1`, `reg_alpha=0`, `gamma=0`, `objective="binary:logistic"`,
   `tree_method="exact"`, `n_jobs=1`, `random_state=20261012`. Balanced class weights are passed as
   `sample_weight` with the same formula as the logistic arm, computed on each training set. Inputs are the 11
   features unstandardised (trees are invariant to monotone scaling).
   There is no hyperparameter search, no early stopping and no inner loop. No setting is changed after any
   result is seen.
3. **Baselines (no training), unchanged:** most buildings in the cell; most buildings within 2 km; closest to a
   major road; closest to a town or village; closest to the mapped grid.

## Validation and metrics

- **Split:** leave one district out. For each of the 30 districts, each arm is fitted on the other 29 and scores the
  held-out district's cells.
- **Primary metric:** pooled recall at top 10%. This is the share of all positive cells in held-out districts
  that fall in the top 10% of their own district's cells (cut-off m = ceil(0.1·n)). Ties at the cut-off count
  fractionally, as in `siting.js captured`.
- **Gate:** at least 60 positive cells in at least 6 districts (as Phase 4R).
- **Intervals:** cluster bootstrap over the districts with at least one positive cell, 2,000 draws, new seed
  **20261012**, mulberry32 generator, 2.5–97.5 percentiles (linear interpolation). In every draw the same sampled
  districts are used for all arms, so differences are **paired**. Reported intervals:
  - each arm's recall;
  - XGBoost − logistic (the decision quantity);
  - XGBoost − strongest baseline, with the strongest baseline recomputed in each draw (descriptive).
- **Calibration (held-out):** each arm's held-out predicted probability is prior-corrected for the balanced
  weights: logit p′ = logit p − ln(n_neg/n_pos) of that fold's training set. Both arms use the same correction.
  On the pooled held-out cells, report:
  - the Brier score;
  - the expected calibration error, ECE: 10 equal-count bins, the mean absolute gap between mean p′ and the
    observed share, weighted by bin size;
  - a 10-bin reliability table.
- **Secondary (descriptive):** recall at top 20%; pooled AUC (Mann-Whitney, ties averaged); per-district
  captures.

## Decision rule

**ADOPT XGBoost for the app** only if all three hold:

1. its recall at top 10% exceeds logistic by **at least 3.0 points** (point estimate);
2. the 95% paired bootstrap interval of XGBoost − logistic lies **entirely above zero**;
3. its calibration is **not worse**: ECE(XGBoost) ≤ ECE(logistic) + 0.01.

Otherwise the verdict is **TESTED, NOT BETTER** and the app keeps the logistic model. If the gate fails, the verdict
is **FEASIBILITY**. Whatever the verdict, the registered Phase 4R result is unchanged. If ADOPT, XGBoost scores are
exported as an **alternative, clearly labelled PREDICTED layer** in the Likely sites lens. They never replace the
registered logistic layer and never change the energy ranking.

## Interpretation reports (descriptive, decided now)

- **XGBoost feature importance:** total gain per feature from the model fitted on all 30 districts.
- **Permutation importance (held-out):** for each fold and each arm, shuffle one feature within the held-out
  district and re-score. Use 5 repeats, the generator seeded with 20261013, and the same permutations for both
  arms. Importance is the mean drop in pooled held-out AUC.
- **Agreement:** Spearman rank correlations between:
  - XGBoost and logistic permutation importances;
  - XGBoost permutation importance and |coefficient| of the logistic model fitted on all districts (standardised
    scale);
  - logistic permutation importance and those |coefficients|.

## Outputs

`docs/audits/phase4x-evaluation.json` contains the protocol and input SHA-256, library versions, the
reproduction check, every arm, the intervals, calibration, importances and the verdict. `docs/phase4x-results.md`
is the plain-language report. `live/js/model-comparison.js` holds the numbers shown in the app's model-comparison
card. One command reruns everything: `make research-xgb`. The output is deterministic, except for the run's own
timestamp and duration fields.

## What this cannot show

It cannot show that a predicted cell has a facility. Labels come from open maps: they are incomplete and sometimes
wrong (Phase 4R label audit). Recall is measured against documented points only. A better ranking of documented
points is not field validation (n = 0).
