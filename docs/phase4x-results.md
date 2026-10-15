# Phase 4X results: XGBoost against the registered siting model (Rwanda)

**Verdict: TESTED, NOT BETTER.** The registered logistic model stays in the app. On the same table, features, held-out
districts and metric, XGBoost found **64.2%** of documented collection and processing squares in the top 10% of
their hidden district. The registered logistic model found **73.1%**. The paired difference is **−9.0 points, 95%
interval −15.1 to −3.3**: XGBoost is worse, and the interval excludes zero. XGBoost still beats every simple rule,
by +14.9 points (5.9 to 25.6).

| | |
|---|---|
| Protocol | [spec/phase4x-protocol.md](spec/phase4x-protocol.md), SHA-256 `cf8e9382…` ([hash file](spec/phase4x-protocol.sha256)), frozen 10 Oct 2026 21:01 UTC, before XGBoost was scored |
| Results | [audits/phase4x-evaluation.json](audits/phase4x-evaluation.json) |
| Code | `research/phase4x/` (Python port of `live/js/siting.js` + XGBoost), `make research-xgb`, tests in `tests/test_phase4x.py` |
| Table | `data/rwanda/siting_cells.csv`, SHA-256 `664350e8…`, 25,281 squares, 30 districts, 134 positive squares in 27 districts (label `y_any`) |
| Software | Python 3.12.14, xgboost-cpu 3.4.1, NumPy 2.5.3, scikit-learn 1.9.1; AMD64 CPU, one thread, no GPU; 85 s |
| Registered result | Phase 4R KEEP (+23.9 points) unchanged; [phase4r-results.md](phase4r-results.md) |

## 1. Why this test

The challenge brief suggests XGBoost for predicting agro-storage and processing sites. We had used a logistic regression
and never tested the suggestion. This test replaces "we did not try it" with a recorded comparison under a rule fixed in
advance.

## 2. What was fixed before the run

- **The same everything:** table, 11 label-free features, label, leave-one-district-out split, recall at the top
  10%, fractional ties, baselines and feasibility gate (≥ 60 positive squares in ≥ 6 districts; met: 134 in 27).
- **XGBoost settings, declared and never tuned:** max_depth 3, 200 trees, learning rate 0.05, subsample 0.8,
  min_child_weight 5, λ 1, exact tree method, seed 20261012. Balanced class weights, as for the logistic model.
  There was no inner search and no early stopping.
- **Reproduction gate:** before XGBoost was scored, the Python port had to reproduce the registered Phase 4R numbers.
  It did, exactly: recall 73.1% against 49.3% for the most-buildings rule, and margin +23.9 (13.4 to 34.4) with the
  registered seed. Its coefficients on all districts match the frozen app model to within 4 × 10⁻¹⁴.
- **Adopt XGBoost only if** it beats logistic by ≥ 3 points, the paired 95% interval is above zero, and its held-out
  calibration is not worse (ECE within +0.01).
- **Paired cluster bootstrap:** 2,000 draws over the 27 districts with a positive, new seed 20261012. The same sampled
  districts are used for every arm.

## 3. Results (held-out districts; ESTIMATED: recall of documented squares)

| Arm | Recall, top 10% | 95% interval | Recall, top 20% | AUC |
|---|---:|---|---:|---:|
| **Logistic regression (registered model)** | **73.1%** | 61.3 – 83.9 | **88.1%** | **0.934** |
| XGBoost, fixed settings | 64.2% | 54.1 – 75.4 | 84.3% | 0.914 |
| Most buildings in the square | 49.3% | 40.1 – 59.7 | 62.7% | 0.854 |
| Most buildings within 2 km | 35.1% | 28.7 – 41.1 | 53.7% | 0.782 |
| Closest to a major road | 34.3% | 25.4 – 43.1 | 61.2% | 0.826 |
| Closest to a town or village | 29.1% | 20.4 – 40.4 | 48.5% | 0.761 |
| Closest to the mapped grid | 16.4% | 9.7 – 24.0 | 29.1% | 0.703 |

Intervals here come from the Phase 4X bootstrap (seed 20261012). The registered Phase 4R intervals (seed 20261011)
differ slightly in the last digit, e.g. 61.5 – 83.9 for the logistic model. Both are reported, neither replaces the other.

| Decision quantity | Value | Rule | Met |
|---|---|---|---|
| XGBoost − logistic, top 10% | **−9.0 points (−15.1 to −3.3)** | ≥ +3.0 points | no |
| Paired interval above zero | upper bound −3.3 | lower bound > 0 | no |
| Calibration, ECE (prior-corrected) | 0.0029 vs 0.0009 | ≤ logistic + 0.01 | yes |
| XGBoost − logistic, top 20% (descriptive) | −3.7 points (−7.1 to 0.0) | – | – |
| Brier score (descriptive) | 0.00495 vs 0.00498 | – | – |

- **Per district:** XGBoost found fewer documented squares than logistic in 6 districts: Gasabo, Kayonza, Ngororero,
  Nyabihu, Nyamasheke and Rusizi. It tied in the other 21 and was ahead in none.
- **Both are well calibrated** after correcting for the balanced weights. Calibration is not why XGBoost loses; ranking is.

## 4. What the models use

- **Roof size dominates both models.** In held-out permutation importance (drop in AUC), the largest roof in the
  square comes first for both: 0.164 for logistic, 0.051 for XGBoost.
- **XGBoost's split gain** ranks roofs ≥ 200 m², the largest roof, distance to a major road and distance to a
  centre highest.
- **The logistic model's key contrast** is many buildings in the square but fewer within 2 km (coefficients
  +1.01 and −2.35). That is a busy spot that is not inside a dense block. This contrast is the second-largest
  permutation importance for logistic (0.039). XGBoost barely uses it (0.001). It is one linear contrast that
  shallow trees approximate only in steps.
- **Agreement (Spearman):**
  - logistic permutation importance vs |coefficients|: 0.88;
  - XGBoost permutation importance vs logistic permutation importance: 0.34;
  - XGBoost permutation importance vs |coefficients|: 0.53.

  The two models agree on roof size and disagree on the density contrast.

## 5. What this shows and what it does not

**It shows** that, with 134 positive squares, a fixed and reasonable XGBoost configuration is clearly worse than the
regularised linear model at the registered task. The brief's suggestion was tested, not ignored. With so few positives,
a model with fewer degrees of freedom generalises better to unseen districts.

**It does not show** that XGBoost cannot win with other settings. Settings were fixed in advance on purpose: tuning
them on these held-out districts would turn the test into a search. A tuned comparison would need a new protocol
with an inner leave-one-district-out loop declared before running. It also says nothing about field truth: labels
come from open maps, are incomplete and sometimes wrong (see the Phase 4R label audit), and field n = 0.

## 6. Reproduce

```sh
uv sync --locked --group research     # one-time: adds xgboost-cpu 3.4.1 (2.2 MB)
make research-xgb                     # ~1.5 minutes, deterministic (verified: two runs identical)
uv run --group research python -m pytest tests/test_phase4x.py
```
