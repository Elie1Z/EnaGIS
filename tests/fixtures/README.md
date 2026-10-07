# Phase 1 hand-computed examples

All quantities, coordinates, registries, source manifests, parameters and freezes here are **synthetic**. These CC0 test data establish interface arithmetic only. No data describe a real elevator, no real capacity constraint or scientific threshold is approved, and no model has produced these assignments or energy figures.

`phase1.json` is the committed test input. `scripts/write_phase1_fixture.py` only authors its repeated boilerplate; the smoke command reads the committed JSON directly. The expected values below are the independent worked specification. The script does not call a production allocator, energy method, classifier or ranking policy.

| Case | Input mass | Literal assignments | Unserved | Expected shipping-point prediction | Service interpretation |
|---|---:|---|---:|---:|---|
| single | 12 t | N1: 12 t | 0 t | SP1: 12 t | 6 kW capacity minus 4 kW central requirement = +2 kW; unflagged. |
| competing | 10 t | N1: 6 t; N2: 4 t | 0 t | SP1: 10 t | Two elevators share **one** 0.010 kT outcome (10 t). Never give each elevator 10 t. |
| known_capacity | 8 t | N1: 8 t | 0 t | SP1: 8 t | 3 kW minus 4 kW = −1 kW; toy undersized flag. |
| unknown_capacity | 8 t | N1: 8 t | 0 t | SP1: 8 t | Capacity and margin remain null/UNKNOWN; documented unknown capacity, toy verify-first flag. |
| overflow | 10 t | N1: 7 t | 3 t | SP1: 7 t | 7 + 3 = 10 t. Unserved is a named row, not deleted. This is a supplied assignment, not derived from electrical power. |
| logistics_only | 5 t | N1: 5 t | 0 t | SP1: 5 t | Product passes through a logistics node; stationary requirement remains UNKNOWN. |
| missing_facility | 5 t | candidate N1: 5 t | 0 t | No documented shipping-point group | Registry link, existence, eligibility and location remain UNKNOWN; P5. Assignment is a toy hypothesis. |
| unreachable | 10 t | None | 10 t | None | All production remains explicitly unserved; no zero-time route is invented. |

For the reachable examples the literal travel time is 10 minutes against a toy 20-minute limit. N1/N2 ties break by ID. Known service ranges are [3, 4, 5] kW and [30, 40, 50] kWh for a **toy** ten-hour cycle. The ranges are independent supplied fields; core code never divides period kWh by 24 to estimate peak kW. Unknown service examples keep both ranges null.

Toy uncertainty has 3 inclusions in 4 supplied draws, so frequency = 3/4 = 0.75. No Monte Carlo implementation or calibrated viability probability is implied. The tier is supplied by a named toy policy.

The synthetic snapshot SHA-256 and freeze/config hashes identify literal fixture markers, not downloaded files or a real ranking freeze. Source acquisition and file-integrity verification belong to Phase 2; a real freeze belongs to its later phase. The smoke report hashes each validated bundle's canonical JSON bytes so identical inputs give identical reports.

Tests deliberately corrupt these inputs to assert visible failure for units, dates, coordinates, references, duplicate IDs, mass loss, outcome duplication, invalid missingness, leakage and transfer partition violations. No invalid row is dropped or filled with zero.

## Phase 2 raw-source fixture

`tests/phase2_fixture.py` constructs tiny synthetic raw inputs, pins their actual byte hashes and passes them through the complete offline adapter path. Two Alberta elevators share shipping point ONE: its 2 kT outcome is stored once and linked twice. Manitoba point TWO has a separate 3 kT transfer outcome. An Amber Durum row is excluded. One source storage value is missing, another is a reported zero; a swapped point becomes P5 rather than an invented location. Three reporting-region totals each have 200 t all wheat and 50 t durum, except Manitoba's unpublished durum component (`F`), which produces UNKNOWN. Separate province controls do not enter regional mass sums.

`phase2-road.pbf.hex` encodes a **254-byte synthetic OSM PBF**, using the [published wire schema](https://github.com/openstreetmap/OSM-binary/tree/master/osmpbf). Header timestamp: 2024-01-01T00:00:00Z. Way blocks precede node blocks. Dense nodes 10/11 and ordinary node 12 use 1,000-nanodegree granularity, latitude offset +1,000,000,000 and longitude offset −1,000,000,000 nanodegrees. Their expected coordinates are (−113, 53), (−112.99, 53), and (−113, 53). Way 1/version 2 retains nodes [10, 11], `highway=primary` and `oneway=yes`; way 2 references [10, 99] and must appear in the rejected-way output. No road routing assumptions follow from these tags.

The expected values above are independently specified. Tests check dense/ordinary signed coordinates, offsets, timestamp, out-of-order source groups, missing-node rejection, corrupted PBF bytes, unknown required features, spatial ambiguity and province conflicts, immutable snapshots, maintained identity and deterministic rebuilding with network connections forbidden. National source files are not needed by CI.
