# Phase 4 status

Status: **IMPLEMENTATION READY; scientific execution awaiting protocol approval**, 8 October 2026.

The user authorized development of Phase 4. All comparisons are implemented and exercised with
synthetic fixtures. Real source preparation is complete. The proposed scientific assumptions
remain unapproved, so no real baseline scores, fitted model, hindcast metrics or keep/kill result
are reported. This document is not a Phase 4 completion declaration.

## Delivered

| Requirement | Implementation and current evidence |
|---|---|
| B0/B1/B2/population | Administrative production context, Euclidean mass proxy, road-accessible mass proxy and audited population. Common comparison units and explicit UNKNOWN values. Proposed methods await approval. |
| Expert shortlist | Strict ordered shipping-point interface with provenance, elicitation date and consent/release reference. No expert list supplied. |
| Hindcast | Unique shipping-point aggregation, no repeated outcome per elevator, complete-member requirement, common cohort, Spearman/intervals and separate volume diagnostics. Partial matched-point CAR totals are explicitly incomplete. |
| Independent siting | Label-free feature module; regularized logistic presence/background models; leave-one-CAR-out CV with training-only preprocessing and nearest-presence baseline. |
| Keep/kill | Primary top-20% recall, paired 2,000-block bootstrap, lower 95% margin over best baseline >0; top-10% and Boyce diagnostics cannot override it. |
| Feasibility | Fewer than 60 positive CCS or six positive CARs in the final common cohort stops fitting. UNKNOWN inputs are never zero-filled to rescue the gate. |
| Reproducibility | Source pins, config/code/lock/source-index hashes, mandatory committed protocol and local preregistration tag, immutable registration, verified exports and fixed seed. |
| Holdout | No Manitoba unit, outcome, label selection or fitting enters the development comparison. |
| Safety of claims | Scores are not calibrated probabilities; modeled crop context is not measured crop location; road length is not travel time; missing documentation is not absence. |

## Real preparation, before any outcome analysis

- 369 AB/SK CCS units; 132 documented-positive CCS in 14 positive CAR blocks.
- 235 unlabeled CCS and two units requiring spatial review; unlabeled does not mean absent.
- 1,374 official CSD counts/geometries join uniquely. Nine CSD populations are missing, making
  seven CCS populations UNKNOWN; 362 CCS totals are known.
- Nine development production regions remain UNKNOWN.
- Basic complete-covariate availability is an upper bound of 197 CCS, including 74 positives in
  eight blocks. Road/catchment completeness can reduce this, potentially below the fitting gate.
- Sources are pinned in [the Phase 4 manifest](data/phase4-manifest.json). The local preparation
  artifacts are ignored by Git; [the aggregate preparation audit](audits/phase4-preparation.json)
  retains hashes and counts. No restricted licensing or private verification rows are exported.

## Checks

The Phase 4 synthetic suite covers draft-approval refusal, common-cohort exclusions, spatial
separation, training-only preprocessing, nearest-presence leakage, recall ties, Boyce undefined
cases, paired confidence rules, CSV duplicate-symbol columns, partial population unknowns,
road deduplication/topology, unsnapped source coverage, mass-proxy accounting, shared shipping
points, incomplete groups and transfer-outcome refusal. An offline end-to-end fixture exercises
preparation, an actual temporary Git registration, graph/features, feasibility failure, hindcast,
deterministic exports and both checksum and semantic tampering checks.

**125 tests pass**, including 11 new Phase 4 tests. Ruff lint/format, all eight Phase 1 smoke
cases, verification of all ten historical Phase 3 artifacts and a byte-identical repeat of real
Phase 4 preparation pass. These checks are recorded in the machine audit. Synthetic results
are not scientific performance estimates. Existing Phase 0–3 functionality remains covered by
the full suite; the Phase 3 real artifacts have not been rerun or overwritten.

## Remaining exit criteria

1. Human approval or revision of the [concrete draft protocol](spec/phase4-preregistration.md),
   especially replacing the unaudited crop raster with a coarse proxy and the road-distance
   settings. Required by `AGENTS.md`; approval is not inferred or fabricated.
2. Rebuild preparation with approved config, commit/tag preregistration, execute the real
   comparison without relaxing gates, and record outcome metrics or a feasibility failure.
3. Review those results and limitations before declaring Phase 4 complete. Complete district
   observations, independent expert choices, field verification and Manitoba transfer performance
   remain unavailable unless separately supplied/evaluated.

The [run guide](spec/phase4-experiment.md) lists exact commands. The proposal and reason for the
method amendment are in [decision 0006](decisions/0006-phase4-protocol-proposal.md).
