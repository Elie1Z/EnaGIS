# Phase 6 engine — execution and scientific boundary

Package: `src/enagis/science/`; version `phase6-v1`. This is a separate execution path from
the historical pipeline and registered CCS experiment. All runtime dependencies were already
pinned in `uv.lock`; no dependency update was needed.

## Reproduce the engineering acceptance run

From the repository root, after `uv sync --locked --cache-dir .uv-cache`:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis.science run --config tests/fixtures/phase6-synthetic-config.json --input tests/fixtures/phase6-synthetic-inputs.json --output outputs/phase6-synthetic --allow-fixture
uv run --offline --locked --cache-dir .uv-cache python -m enagis.science verify outputs/phase6-synthetic
```

Use a new output directory for another run. Existing nonempty output directories are refused.
Make equivalents: `make phase6-fixture` then `make verify-phase6`. Windows can use
`.venv/Scripts/python.exe` in place of the uv prefix.

The fixture has 13 invented sites, three production parents (one UNKNOWN), 14 invented road
ways and 700 known tonnes. Its coordinates lie inside the Canadian projection's area of use,
but its values are **not observations or recommended coefficients**. Four cases (two seasons ×
two allocation variants), each with 16 shared parameter draws, exercise all three tiers.
Seed 17, 80% tier threshold, 5–95% quantiles and all numeric ranges are fixture settings only.

Eight checksummed artifacts plus index are written: complete config and inputs, accessibility,
draws, ranking, shortlist JSON/CSV and ablations. Inputs preserve snapshots, field evidence,
dates, licence, precision and source hashes. Draws retain routes, assignments, origin balances,
parameters, technical values, signed gaps, ranking and unresolved reasons. Metadata declares
period, commodity, service, region, analysis CRS, seed, config/input/code/lock hashes and interpretation.
Replay checks hashes and regenerates every artifact byte. It does not certify scientific
validity. Replay uses a temporary sibling directory and removes only that generated directory.
Replay requires the matching source-code version. The original engineering acceptance run
is retained at commit `5953c5f`; the desk-review continuation uses a separate output directory
`outputs/phase6-review-fixture/` and records its own hashes in the desk-review audit.

## Audit real readiness without models or outcomes

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis.science audit
```

This verifies the consumed Phase 2 table hashes and all AB/SK way rows, then writes
`docs/audits/phase6-readiness.json`. It opens no delivery outcomes or Manitoba road files.
Road coverage counts refer to ways, not road length, and provincial extracts can overlap.
The report's `scientifically_ready_to_freeze` stays false while its review gates are pending.

`configs/scenarios/phase6-canada-v1.review.json` is a decision packet, not an executable
scientific configuration. Passing it to `run` stops before opening the supplied input file.
There is no `--force` switch for scientific approval.

## Calculation details

### Accessibility

Retain shared OSM node identities; geometric crossings do not create synthetic junctions.
Reject conflicting duplicate ways/node positions, minimize parallel-edge time rather than
summing it, and preserve direction. General access can be overridden by the appropriate
foot/bicycle/motorcycle/motorcar/HGV tag. Foot routing ignores a street's generic one-way tag;
ambiguous generic one-way paths are excluded. Numeric km/h and mph caps are recognized.
Conditional, directional-access, physical-dimension, seasonal and barrier tags needing richer
logic are counted and excluded. Missing access is an explicit profile choice. Missing surface
is excluded unless an explicit `UNKNOWN` surface scenario is configured.

Transform from declared longitude/latitude EPSG:4326 to an explicitly configured projected
two-dimensional metre CRS; check that CRS's area of use and finite values. Geographic, feet,
geocentric and Web Mercator CRSs are rejected for these distance calculations. Real Canadian
execution retains EPSG:3347. A CRS's area of use alone does not certify acceptable distortion;
each new region needs a local distance review. Travel time = metres × 60 / (1000 × km/h). Each endpoint snaps to
the closest retained vertex within the configured distance, with stable ID ties. Add explicit
connector times; return null for snap failures/unreachable/over-budget pairs. No zero-time
placeholder stands for an unreachable path. Vertex snapping remains an approximation needing
coverage review; it is not edge snapping or navigation. No turn/traffic/barrier completeness
claim is made.

### Allocation and physics

Parent production is disaggregated by supplied positive fractions summing to one. Unknown
parent mass stays unknown. Every origin/site pair must have one accessibility record.
For a parameter draw:

```text
flow_limit_tonnes = storage_tonnes × wheat_share × operating_days
                    / (residence_days × treated_fraction)
treated_tonnes = assigned_tonnes × treated_fraction
inventory_tonnes = treated_tonnes × residence_days / operating_days
active_inventory_tonnes = inventory_tonnes × simultaneous_fraction
airflow_m3_s = active_inventory_tonnes × airflow_per_tonne
fan_kW = airflow_m3_s × static_pressure_Pa / (1000 × fan_efficiency × motor_efficiency)
electrical_kW = fan_kW + auxiliary_kW (when active inventory is positive)
one_cycle_kWh = electrical_kW × cycle_hours
specific_cycle_kWh_per_active_tonne = one_cycle_kWh / active_inventory_tonnes
```

This is a steady-flow inventory scenario, not a reconstructed harvest peak. The last intensity
is derived, not an independent arbitrary coefficient, and is null when active inventory is zero.
Operating days describe the modeled period; they do not document operating status. Startup
current, drying heat, unrelated machinery, economic demand and annual cycle count are outside
this service boundary. Review commercial applicability before calling simultaneous duty a
useful planning requirement.

Maximum-served allocation uses two linear programs: first maximize assigned tonnes, then
minimize tonne-minutes at that total. Stable sorted identities and the pinned HiGHS dual-simplex
solver define repeatable ties, without a cost perturbation. Nearest-first sorts by minutes,
origin ID and node ID; it can leave avoidable unserved mass. The pending scientific policy
proposal names nearest-first as the PRD reference and maximum-served as its comparison.
Both enforce shared node capacity, source balances and total conservation. Unknown storage
either excludes the candidate with an explicit flag, or is unbounded with that same flag,
according to a reviewed scenario. Neither interpretation turns it into known zero storage.
An accessible UNKNOWN production origin makes a node's total requirement UNKNOWN, even when
the allocation artifact records a known partial mass.

Supply has the three existing states. Only documented electrical kW can produce
`capacity − requirement`. Negative known margins are undersized; positive margins remain
signed. Missing documentation produces no numeric deficit and makes final priority Verify-first.
Input fields are explicitly storage tonnes and electrical kW; arbitrary units are rejected.

### Uncertainty, tiers and ablations

Fixed/triangular inverse CDFs transform scrambled Sobol draws of size 2^m. Named joint groups
share quantiles; separate groups are independent. Coefficients are global within a draw.
All declared modes/speeds, seasons and assignments are crossed with the same draws. No case
is chosen after examining rankings. Summary intervals are configured **scenario quantiles**,
not confidence intervals. Top-k inclusion is stability under these cases and parameters,
not a probability of viability. Magnitudes retain known-draw counts; missing values are not
filled with zero. All-draw denominators remain visible even if a node is only sometimes eligible.

Per-draw ordering is technical kW descending then node ID. Ensemble ordering is inclusion
descending, median technical kW descending, node ID. Robust requires the configured inclusion
threshold in **every case**; unresolved evidence overrides it with Verify-first; others are
Contested. Unknown-only or zero-only sites have no rank. A shortlist can contain fewer than ten
eligible sites; it is never filled with invented values. Questions prioritize production,
storage, electrical supply and access evidence before the site's other unresolved question.

Ablations compare matched draws between cases differing in one factor. They report membership
symmetric difference (one replacement counts two), removals, additions, replacements
(`min(removed, added)`), common-site rank displacement and no automatic retain/drop verdict.
A shrinking shortlist alone is not a replacement. Comparisons identify whether they include
the named reference case. These are engineering
diagnostics until a real comparison and decision review have been approved.

## Real execution contract and remaining adapter work

A `scientific_reviewed` Dataset requires AB/SK scope, human data/network review, source
snapshots, conserved origins, locations/precision, compatible site capacities and pinned
provenance hashes. A scientific ScenarioConfig requires human method/parameter/transport/rank
approval and source applicability. All referenced source IDs must resolve. Restricted source
snapshots cannot enter this portable run bundle. The scientific budget is ten.

The separate `unit_review.convert_airflow` helper converts cfm/bushel to m³/s/tonne only with
known grain-specific kg/bushel, compatible explicitly identified bushel bases and a recorded
basis review. It retains the original evidence and dimensional factors; missing or mismatched
inputs produce UNKNOWN. This does not approve coefficients or insert them into a real scenario.

Synthetic geography tests exercise the full calculation in five non-Canadian settings. They
show software portability and conservation, not field validity or learned transfer. Real runs
still require `ca-prairies`, AB/SK and EPSG:3347. New real regions enter through a separately
reviewed adapter/configuration and evaluation protocol, as required by decision 0002.

The current engine accepts a reviewed prepared input bundle. Preparing real production origins
and a commodity-appropriate network is still gated by the review packet; it is not automated
using invented parameters. Large-area performance and full routing completeness remain to be
qualified on the approved real bundle. The engine does not create a frozen ranking or declare
its own scientific exit. Phase 4 baselines/hindcast are historical comparisons, not validation
of this new engine. Review real ablations and a prospectively specified comparison separately.
