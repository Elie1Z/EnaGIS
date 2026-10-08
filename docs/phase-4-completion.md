# Phase 4 completion — registered v1.1 comparison

**COMPLETE, 8 October 2026. Verdict: KILL / no demonstrated improvement from this
proxy-based accessible-production feature.** This is not evidence against road-catchment logic.
With seven positive CAR blocks, bootstrap intervals are wide and potentially unstable and are
reported descriptively. The AAFC registry is close to a census of primary elevators, so this
experiment cannot test robustness to documentation bias.

## Registration and guards

Approved protocol `phase4-canada-v1.1` was amended before registration. Exact user approval is
recorded in configuration and the frozen protocol. Registration commit:
`948cf2fddbb5a9f093883dd06b1a58a1d5a905fe`; tag: `preregister-phase4-canada-v1.1`;
remote: [Elie1Z/EnaGIS](https://github.com/Elie1Z/EnaGIS). Both remote references were independently
verified at that commit before evaluation. The [registration](../data/manual/phase4-preregistration.json)
pins protocol, code, sources, preparation, Phase 3 run, review document and lockfile hashes.

Counts and frozen-values gates passed. Primary 20%, secondary 10%, 2,000 draws, seed 20261008,
60-positive/six-CAR gate, 15-group hindcast minimum, folds, hyperparameters and keep rule remain
unchanged from v1. No scientific method/config/code changed after registration. No new source
or crop raster was acquired. Manitoba remains outside the real evaluation.

## Cohorts and coverage

| Cohort | Input CCS | Complete CCS | Positive CCS | Positive CARs | Excluded CCS |
|---|---:|---:|---:|---:|---:|
| Primary common comparison | 369 | 155 | 60 | 7 | 214 |
| Descriptive nonproduction sensitivity | 369 | 360 | 130 | 14 | 9 |

| Exclusion reason | Primary | Sensitivity |
|---|---:|---:|
| Population unknown | 7 | 7 |
| Production unknown | 212 | 0 |
| Snap failure / uncertain nearby origin coverage | 9 | 0 |
| Spatial review | 2 | 2 |
| Unresolved unit-level match | 0 | 0 |

Reason counts overlap. Sensitivity drops production features and their catchment/snap requirements,
retaining population, road/junction density, log CCS area and geometry/label review rules. It is
a descriptive availability comparison only and cannot override the primary result. Unlabeled CCS
remain background, not verified absences.

## Primary comparison

Equal-weight CAR recall within the top 20% of each held-out block's eligible CCS. Values are
percentages with paired CAR-bootstrap 95% percentile intervals. All arms use the same 155 CCS;
seven positive CARs contribute to recall inference.

| Arm | Mean recall (%) | 95% interval (%) |
|---|---:|---:|
| Full model: base + proxy accessible production | 35.71 | 21.43–50.00 |
| Base model, including log CCS area | 36.43 | 22.14–50.71 |
| B0: administrative production context | 39.76 | 26.66–60.71 |
| B1: Euclidean production proxy | 26.19 | 16.67–32.86 |
| B2: road-accessible production proxy | 25.48 | 15.95–32.14 |
| Population | 37.38 | 23.10–51.67 |
| Nearest training presence | 38.81 | 22.62–61.43 |
| Area only | 29.29 | 16.19–43.57 |

Full-minus-best-baseline margin: **−4.05 percentage points**, 95% interval **[−39.29, −0.71]**.
The lower bound does not exceed zero, so the frozen rule gives **KILL**. The strongest comparator
is recomputed in every draw; the point-estimate strongest comparator is B0. This means **no
demonstrated improvement from this proxy-based accessible-production feature**, not evidence
against road-catchment logic. The proxy cannot resolve crop placement within a SADR. Crop
inventory remains possible future v2 only. No calibrated occurrence probability, unmet-need
estimate or worldwide predictive performance is established.

Secondary top-10% full-model recall is 22.38% (95% interval 13.33–30.00%). Boyce has five common
complete blocks; full-model mean is 0.546 (95% interval 0.219–0.872). Neither diagnostic changes
the decision. Exact results and undefined-window reasons are in the [machine audit](audits/phase4-evaluation.json).

## Shipping-point hindcast

Status: **evaluated diagnostic**. Of 138 observed shipping points, 52 common groups in seven CARs
meet the 15-group gate; 86 groups are excluded. Each observed point is counted once even with
multiple elevators. There are zero fabricated facility-level observations.

| Arm | Spearman correlation | 95% CAR-bootstrap interval | Top-volume group recall |
|---|---:|---:|---:|
| Phase 3 allocation | 0.773 | 0.282–0.821 | 4/11 = 36.36% |
| B0 | 0.638 | 0.018–0.769 | 4/11 = 36.36% |
| B1 | 0.573 | 0.143–0.736 | 6/11 = 54.55% |
| B2 | 0.657 | 0.200–0.815 | 8/11 = 72.73% |
| Population | 0.333 | −0.192–0.701 | 2/11 = 18.18% |

Every arm uses the same 52 groups and 11-group top-20% budget, with 2,000 valid correlation draws.
Phase 3 has the highest Spearman point estimate, while B2 has the highest top-volume recall;
these diagnostics do not establish an overall superiority claim.

Phase 3 volume residuals: MAE 53,412.69 tonnes/group; mean bias +5,842.01 tonnes/group; summed
prediction/observation ratio 1.07015. **Absolute-volume accuracy is not validated:** harvest and
marketed crop-year deliveries differ, while channel share, carry-over and within-year registry
chronology remain unresolved. CAR fallback totals are partial matched-point totals, not complete
district observations. No expert shortlist was supplied or invented.

## Verification, files and disposition

Run `phase4:ccb98f6b1f4f:050f5cff43a9` completed successfully. Independent `verify-experiment`
verified all six artifacts: features, predictions, fold models, hindcast groups, report and
protocol, plus their hashed index under `outputs/phase4`. Large outputs/preparation remain local
and ignored by Git; preserve them separately. The committed machine audit retains result tables,
registration and artifact hashes. All **127 tests**, lint, format and frozen-values checks passed
before registration. GitHub CLI could not query CI without authentication; no remote CI-success
claim is made from that optional lookup.

The [run log](phase4-run-log.md) records UTF-8 check-script correction, formatting fixes, the Windows
sandbox restriction and authorized successful test rerun, descriptive-cohort interpretation and
publication within registration. No scientific setting was changed to improve results. No
post-registration evaluation or verification error occurred.

The proxy-accessibility siting addition is not promoted for operational use. Phase 5 can integrate
the existing engineering shortlist with its evidence and uncertainty labels and these Phase 4
results. Field verification, complete district observations, expert input, commercial energy
parameters and Manitoba transfer remain separate unresolved gates.
