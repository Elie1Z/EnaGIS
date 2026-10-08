# 0006 — Proposed Phase 4 comparison protocol

Status: **APPROVED as v1.1 before registration**, 8 October 2026. The user's conditional
approval was recorded after the 60-positive/seven-CAR counts gate, frozen-values check and
127 tests plus lint/format passed. See the [run log](../phase4-run-log.md) for the earlier STOP
and explicit resumption authority. The historical filename is retained for existing links.

The user authorized Phase 4 implementation. Decision 0003 remains the frozen benchmark: Canadian
Prairie non-durum wheat storage/aeration, AB/SK development and Manitoba transfer holdout.

## Evidence requiring a method decision

The pinned data spine has regional production and audited reporting boundaries but does not have
the planned Annual Crop Inventory 2024 raster or its crop-class audit. The intended fine-scale
production weighting therefore cannot honestly be claimed. Population is now pinned from the
official 2021 CSD table and full digital CSD geometry. Road ways support a topology-based distance
comparison, but audited driving speeds and full vehicle-routing restrictions remain unavailable.

## Approved exploratory comparison

Use the explicit coarse area-based production proxy and undirected road-distance experiment in
the [review protocol](../spec/phase4-preregistration.md), with all numerical settings in the
[approved v1.1 config](../../configs/experiments/phase4-canada-v1.1.json). This is an exploratory comparison,
not a completed crop-location audit or operational travel-time model. The alternative is to keep
execution gated until an audited crop raster and corresponding protocol are ready.

The user explicitly approved v1.1 with log polygon area in both models, an area-only arm,
proxy-specific interpretation, limited-power and documentation-bias clauses, descriptive
nonproduction cohort counts and remotely pushed registration. The original v1 numerical
thresholds, seed, folds and model hyperparameters remain fixed. Exact approval is recorded in
the config and protocol. Phase 3 temporary energy coefficients retain their separate status.

## Implementation boundary

The code implements population/production/road baselines, a regularized presence/background
model, leave-one-CAR-out validation, paired block uncertainty and a preregistered keep/kill gate.
Siting features never consume node allocations, capacities, energy, gaps or delivery outcomes.
The separate hindcast groups predictions at shipping point, counts each observed volume once,
and exposes incomplete data and the limited district-total fallback. The expert shortlist has
an input contract; no expert observations or approval are invented.

Synthetic tests may use explicitly synthetic approval metadata to exercise the implementation.
Those records are confined to temporary fixtures. Real data preparation may inspect source
coverage and label availability; real graph scoring/fitting/outcome evaluation requires an
approved, committed, hashed and locally tagged registration.

See [Phase 4 status](../phase-4-status.md) for checks and remaining exit criteria. Phase 4 is not
declared scientifically complete before a real result or a preregistered feasibility failure.
