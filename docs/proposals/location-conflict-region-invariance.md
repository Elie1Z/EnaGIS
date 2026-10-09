# Proposal: assign region when conflicting coordinates agree on the region

**Status: PROPOSAL — awaiting human approval.** Nothing has been changed.

## Problem

Two development facilities are excluded with `spatial_review_required:location_conflict`
(2 nodes, 8 UNKNOWN fields). The AAFC 2024 elevator source gives a point geometry and separate
`Latitude`/`Longitude` attributes. These differ by more than the configured tolerance of
0.000001° (`configs/regions/ca-prairies.json`, `coordinate_attribute_tolerance_degrees`), so
`src/enagis/adapters/spatial.py` marks the match `location_conflict`.

## Evidence (read-only check, EPSG:4326 → EPSG:3347)

| Facility | Operator | Geometry vs attribute separation | Region (geometry) | Region (attribute) |
|---|---|---:|---|---|
| Rycroft, AB | G3 Canada Limited | 176 m | SADR 4870 | SADR 4870 |
| Woodrow, SK | Canada Direct Processing Inc. | 468 m | SADR 4703 | SADR 4703 |

Both candidate locations fall in the same reporting region. Production is assigned at
reporting-region level, so the conflict does not change the assignment input.

## Proposed rule

If both coordinates fall in the same reporting region, assign the node to that region for
region-level allocation. Keep `location_quality = conflict` visible and keep the facility
out of any finer-than-region analysis (routing, catchments). Leave the precision class
unchanged; consider downgrading it to P3 instead of P2.

## Impact

At most 2 nodes would gain ESTIMATED values in a new run ID. No registered artifact or verdict
changes. Phase 4 excluded 2 CCS for `spatial_review`; a future protocol would need a new
registration to use this rule.
