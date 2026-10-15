# Validation

Two registered siting tests, two different answers, both reported, plus a registered model comparison:

| Test | Where | Verdict | Details |
|---|---|---|---|
| Phase 4: road-accessible production → grain elevators | Canadian prairies, 7 blocks | **KILL** (−4.05 points) | §1 below |
| Phase 4R: roofs, roads, settlement structure → collection and processing points | Rwanda, all 30 districts | **KEEP** (+23.9 points, 13.4 to 34.4) | §1b below and [phase4r-results.md](phase4r-results.md) |
| Phase 4X: XGBoost (fixed settings) vs the Phase 4R logistic model, same table and test | Rwanda, all 30 districts | **TESTED, NOT BETTER** (−9.0 points, −15.1 to −3.3) | §1c below and [phase4x-results.md](phase4x-results.md) |
| Phase 4N (second site): footprint classifier for surveyed grain mills | Njombe, Tanzania, 6 councils | **KILL** (+1.6 points, −0.3 to 3.4); XGBoost NOT BETTER | §1d below and [phase4n-results.md](phase4n-results.md) |

Section 1 numbers come from [audits/phase4-evaluation.json](audits/phase4-evaluation.json) (status
`complete_registered_evaluation_verified`, 8 October 2026). They are verified with
`python -m enagis verify-experiment outputs/phase4` (6 artifacts). Wording follows the
registered protocol.

## 1. Facility-siting experiment, Canada (Phase 4)

| Item | Value |
|---|---|
| Question | Does a proxy for road-accessible wheat production help locate documented primary elevators, beyond simpler baselines? |
| Unit / outcome | Census consolidated subdivision (CCS); documented presence of an AAFC 2024 primary elevator |
| Cohort (primary) | 369 CCS in → **155 complete**, 60 positive, 214 excluded (production unknown 212, snap failure 9, population unknown 7, spatial review 2; reasons overlap) |
| Spatial blocks | **7** positive census agricultural regions (CAR), block hold-out |
| Metric | Mean over blocks of recall of positive CCS in the top 20% of scores |
| Interval | 95% paired bootstrap, 2,000 draws, seed 20261008 |
| Protocol | [spec/phase4-preregistration.md](spec/phase4-preregistration.md), protocol SHA-256 `ccb98f6b…`, frozen at Git tag `preregister-phase4-canada-v1.1` (commit `948cf2fd`), pushed to `https://github.com/Elie1Z/EnaGIS.git` before evaluation |

| Arm | Recall @ top 20% | 95% interval |
|---|---:|---|
| B0 production only | **39.76%** | 26.66 – 60.71 |
| Nearest presence | 38.81% | 22.62 – 61.43 |
| Population only | 37.38% | 23.10 – 51.67 |
| Base model | 36.43% | 22.14 – 50.71 |
| **Full model** | **35.71%** | 21.43 – 50.00 |
| Area only | 29.29% | 16.19 – 43.57 |
| B1 Euclidean production | 26.19% | 16.67 – 32.86 |
| B2 road production | 25.48% | 15.95 – 32.14 |

**Margin, full model − best baseline: −4.05 percentage points, 95% interval [−39.29, −0.71].
Verdict: KILL — no demonstrated improvement from this proxy-based accessible-production
feature.** With 7 blocks the intervals are wide; report them descriptively. This is not evidence
against road-catchment logic in general. The production proxy assumed uniform distribution
within reporting regions.

A sensitivity cohort (360 CCS, 14 blocks) is descriptive only and cannot override the primary
result. It also gave `kill_or_no_demonstrated_improvement`.

## 1b. Facility-siting model, Rwanda (Phase 4R, EnaGIS Live)

| Item | Value |
|---|---|
| Question | Can open, label-independent map layers rank 1 km squares in a held-out district so that squares with a documented agricultural collection or processing point come out on top, better than the best single rule? |
| Unit / outcome | 1 km square; documented mill, milk centre, cold store, washing station, warehouse, agro-processing or tea factory, market or cooperative (OpenStreetMap + Overture places) |
| Cohort | **25,281 squares, 30 districts, 134 positive squares in 27 districts** |
| Features | 11, fixed in advance: building counts, roof sizes from footprint geometry (Google, Microsoft, OpenStreetMap via Overture), roads, grid and settlement distances, density |
| Validation | Leave one district out; pooled recall of positive squares in the top 10% of their own district |
| Interval | Cluster bootstrap over districts, 2,000 draws, seed 20261011 |
| Protocol | [spec/phase4r-protocol.md](spec/phase4r-protocol.md) v1.1, SHA-256 `1a3bc8ca…`, frozen 10 Oct 2026 before any real square was scored. The v1 label (processing or storage only: 44 squares in 20 districts) failed the feasibility gate and is reported as FEASIBILITY |
| Input | [`data/rwanda/siting_cells.csv`](../data/rwanda/siting_cells.csv), SHA-256 `664350e8…` |

| Arm | Recall @ top 10% | 95% interval | AUC |
|---|---:|---|---:|
| **Siting model** | **73.1%** | 61.5 – 83.9 | 0.934 |
| Same model without roof sizes | 59.7% | 50.0 – 69.9 | 0.895 |
| Most buildings in the square (best baseline) | 49.3% | 39.1 – 59.8 | 0.854 |
| Most buildings within 2 km | 35.1% | 28.5 – 41.0 | 0.782 |
| Closest to a major road | 34.3% | 24.8 – 43.4 | 0.826 |
| Closest to a town or village | 29.1% | 20.3 – 40.8 | 0.761 |
| Closest to the mapped grid | 16.4% | 9.2 – 24.1 | 0.703 |

**Margin, model − best baseline: +23.9 percentage points, 95% interval [13.4, 34.4]. Verdict: KEEP.**
Roof sizes add +13.4 points (5.1 to 21.4).

**Post-hoc label audit (descriptive; the verdict is not re-decided):** 7 positive squares rested on labels that
are plainly wrong (a hotel, a football club, a café, shops). With them removed the margin is +23.6 (13.2 to
34.7). With Kigali's three districts also left out it is +27.8 (15.7 to 39.4).
[audits/phase4r-label-audit.json](audits/phase4r-label-audit.json).

The model learns where facilities are **documented**, not where they exist. It never changes the energy
ranking. In the app its output is labelled PREDICTED. Full write-up: [phase4r-results.md](phase4r-results.md).

## 1c. Gradient-boosted trees vs the registered model, Rwanda (Phase 4X)

The challenge brief suggests XGBoost. Phase 4X compares it with the Phase 4R logistic model on the same table, 11 features,
label, leave-one-district-out split and metric. The protocol ([spec/phase4x-protocol.md](spec/phase4x-protocol.md),
SHA-256 `cf8e9382…`) fixed XGBoost's settings before it was scored: depth 3, 200 trees, learning rate 0.05, subsample
0.8, min_child_weight 5, balanced weights, no tuning. It also required the Python port to reproduce the registered
Phase 4R numbers first, which it did exactly.

| Arm | Recall @ top 10% | 95% interval (Phase 4X bootstrap, seed 20261012) | AUC |
|---|---:|---|---:|
| **Logistic (registered model)** | **73.1%** | 61.3 – 83.9 | 0.934 |
| XGBoost, fixed settings | 64.2% | 54.1 – 75.4 | 0.914 |
| Most buildings in the square | 49.3% | 40.1 – 59.7 | 0.854 |

**XGBoost − logistic: −9.0 points, paired 95% interval [−15.1, −3.3]. Verdict: TESTED, NOT BETTER.** The adoption rule
needed ≥ +3 points with an interval above zero, plus calibration not worse. Calibration was fine (ECE 0.0029 vs 0.0009);
ranking was not. XGBoost was behind in 6 districts, tied in 21 and ahead in none. It still beats every simple rule by
+14.9 points (5.9 to 25.6). The app keeps the logistic model; the registered Phase 4R result is unchanged.
[audits/phase4x-evaluation.json](audits/phase4x-evaluation.json), [phase4x-results.md](phase4x-results.md).

## 1d. Second site: footprint classifier for grain mills, Njombe, Tanzania (Phase 4N)

Scouting of seven candidate regions ([second-site-scouting.md](second-site-scouting.md)) found one site with enough
openly documented processing points: Njombe Region, with 882 grain mills, 881 from a 2021 WFP field survey mapped in
OpenStreetMap. No region had open sub-metre imagery over labelled facilities, so no image detector was trained. The
protocol ([spec/phase4n-protocol.md](spec/phase4n-protocol.md), SHA-256 `d3a9cc02…`) was frozen before any footprint
was downloaded.

| Arm | Recall @ top 1% of footprints | 95% interval | AUC |
|---|---:|---|---:|
| Logistic footprint model | 5.7% | 3.8 – 7.7 | 0.741 |
| XGBoost | 5.8% | 4.0 – 7.7 | 0.756 |
| Closest to a major road (best rule) | 4.1% | 2.7 – 5.7 | 0.637 |
| Largest roof first | 2.8% | 1.7 – 4.0 | 0.628 |

**Margin, logistic − best rule: +1.6 points, 95% interval [−0.3, 3.4]. Verdict: KILL.** XGBoost − logistic: +0.1
(−1.8 to 2.0), NOT BETTER. The test used 673,866 footprints and 830 matched mills, with each of the 6 councils held
out in turn. On footprints from the machine-learning detectors alone, the model ties the road rule. These numbers
are a separate site and never mixed with Rwanda's. [phase4n-results.md](phase4n-results.md), [second-site.md](second-site.md).

## 2. Shipping-point throughput hindcast

| Item | Value |
|---|---|
| Outcome | CGC deliveries 2024–2025 by shipping point (kilotonnes, never split across a point's elevators) |
| Common comparison | 52 shipping-point groups, 7 blocks, 2,000 bootstrap draws |

| Arm | Spearman ρ | 95% interval | Top-volume groups found (of 11) |
|---|---:|---|---:|
| EnaGIS Phase 3 | 0.773 | 0.282 – 0.821 | 4 |
| B2 road production | 0.657 | 0.200 – 0.815 | **8** |
| B0 production only | 0.638 | 0.018 – 0.769 | 4 |
| B1 Euclidean | 0.573 | 0.143 – 0.736 | 6 |
| Population | 0.333 | −0.192 – 0.701 | 2 |

Mixed. Phase 3 has the highest rank-correlation point estimate, but B2 finds more of the
highest-volume groups. Only 52 of 138 observed shipping points were comparable. **Absolute
volume accuracy was not validated** (`absolute_volume_accuracy_validated: false`).

## 3. Engineering checks (software, not science)

| Check | Result | Command |
|---|---|---|
| Unit tests | 230 passed | `python -m pytest` |
| Production conservation | assigned + unserved = input within tolerance | `pytest tests/test_pipeline.py` |
| Artifact integrity | data 32, run 10, experiment 6, demo 32, app 43 artifacts verified | `make verify-data verify-run verify-mvp` |
| Phase 6 replay (synthetic) | verified, `scientifically_ready_to_freeze: false` | `make phase6-fixture verify-phase6` |
| Demo path | 15 browser checks | `node scripts/demo_preflight.mjs` |

## 4. Not validated

- **Field verification: n = 0.** No frozen `ranking-v1`, no observations, no precision@10.
  Tooling passed a synthetic rehearsal only ([phase-7-status.md](phase-7-status.md)).
- Energy coefficients, inventory and fan duty: hypothetical, not approved, never compared with
  meters.
- Electrical supply: no observations, so no gap can be validated.
- Transfer: Manitoba hold-out untouched; no other region evaluated.
- Rwanda (EnaGIS Live): no site or look-alike has been phone-checked or visited. Energy factors are
  screening ranges. District production is ESTIMATED from NISR survey shares.
- No expert shortlist baseline.

## 5. What these results do and do not show

They show the pipeline is reproducible, conserves mass, keeps UNKNOWN explicit, and that two
registered ML tests were run and reported as they came out: one lost (Canada), one won (Rwanda). The
Rwanda model locates *documented* collection and processing points better than counting people.
They do **not** show that the top 10 are the right sites to visit, that the kW numbers are right,
that a predicted square holds a facility, or that EnaGIS beats an expert's shortlist.
