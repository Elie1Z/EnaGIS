# Validation

All numbers come from [audits/phase4-evaluation.json](audits/phase4-evaluation.json) (status
`complete_registered_evaluation_verified`, 8 October 2026). They are verified with
`python -m enagis verify-experiment outputs/phase4` (6 artifacts). Wording follows the
registered protocol.

## 1. Facility-siting experiment (the ML deliverable)

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
- No expert shortlist baseline.

## 5. What these results do and do not show

They show the pipeline is reproducible, conserves mass, keeps UNKNOWN explicit, and that one
honest preregistered ML test was run and lost. They do **not** show that the top 10 are the right
sites to visit, that the kW numbers are right, or that EnaGIS beats simpler investigation
strategies.
