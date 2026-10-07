# 0006 — Proposed Phase 4 comparison protocol

Status: **PROPOSED; not scientifically approved**, 8 October 2026.

The user authorized Phase 4 implementation. Decision 0003 remains the frozen benchmark: Canadian
Prairie non-durum wheat storage/aeration, AB/SK development and Manitoba transfer holdout.

## Evidence requiring a method decision

The pinned data spine has regional production and audited reporting boundaries but does not have
the planned Annual Crop Inventory 2024 raster or its crop-class audit. The intended fine-scale
production weighting therefore cannot honestly be claimed. Population is now pinned from the
official 2021 CSD table and full digital CSD geometry. Road ways support a topology-based distance
comparison, but audited driving speeds and full vehicle-routing restrictions remain unavailable.

## Proposal awaiting human approval

Use the explicit coarse area-based production proxy and undirected road-distance experiment in
the [review protocol](../spec/phase4-preregistration.md), with all numerical settings in the
[draft config](../../configs/experiments/phase4-canada-v1.json). This is an exploratory comparison,
not a completed crop-location audit or operational travel-time model. The alternative is to keep
execution gated until an audited crop raster and corresponding protocol are ready.

No assumption from the draft has been promoted to approved configuration. The Phase 3 permission
to use marked temporary engineering coefficients is not treated as approval of a new scientific
experiment. `AGENTS.md` requires human-owned scientific approval, and the PRD requires thresholds
to be registered before results. Approval is the remaining action before preregistration and real
execution; it must be recorded faithfully rather than inferred from a request to develop the phase.

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
