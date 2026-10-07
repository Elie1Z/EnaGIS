# Phase 0 module and interface specification

This is the semantic contract lock. Phase 1 implements validators, fixtures and CI for it; no scientific algorithms are implemented in Phase 0. Module IDs and human roles follow PRD §12.

## Module boundaries

| Module | Owner / reviewer | Inputs | Outputs / boundary |
|---|---|---|---|
| M01 Ingestion, manifest and reproducibility | R1 / R2 | Approved local source snapshots and adapter configuration | Manifest, parsed source tables, checksums and quality reports. Acquisition is separate from offline analysis. |
| M02 Registry and node construction | R2 / R4 | Source records, manual geocoding/crosswalks, scope | Stable facilities, node candidates, shipping-point groups, capacity observations, precision and provenance. |
| M03 Roads and accessibility | R3 / R1 | Pinned OSM graph, production origins, nodes, mode/scenario parameters | Reachability and minutes of travel; catchment scenario artifacts. No throughput or capacity fitting. |
| M04 Production and allocation | R2 / R3 | Production totals/proxies, nodes, accessibility, compatible capacity/inventory scenarios | Conserved assignments, modeled node throughput/inventory and explicit unserved mass. |
| M05 Technical requirement, supply and gap | R3 / R4 | M04 outputs, service physics, observed capacities, sourced parameters | Energy ranges, peak service class, service-specific supply state and comparable signed margin. Missing parameters are explicit. |
| M06 Baselines and hindcast | R4 / R3 | Common upstream inputs, model outputs and partitioned delivery outcomes | B0/B1/B2/population/expert comparisons, sample sizes and intervals. Held-out outcomes never tune the model. |
| M07 Siting experiment | R4 / R1 | CCS units, permitted upstream covariates, partitioned presence labels | Model artifacts, spatial metrics, intervals, baseline comparison and check flags. No M04–M05 outputs. |
| M08 Uncertainty | R1 / R3 | Upstream source data, approved joint parameter/scenario draws and pure M03–M05 functions | Per-draw results and rank-membership summaries, separate magnitude and ranking sensitivity. |
| M09 Frozen verification and analysis | R2 outreach; R4 analysis | Frozen ranking, sample design, real private verification observations | Frozen sample, outcomes, failure modes and evaluation reports. No rewrite of the frozen ranking. |
| M10 Ranking, export and static map | R1 / R2 | Scenario results, uncertainty summaries, evidence, permitted M07 flags | Top-10, node cards, CSV/GeoPackage/GeoJSON and static MapLibre assets. The map reads pipeline outputs. |
| M11 Documentation index and energy context | R3 / R1 | Approved upstream source-coverage/context layers | Labels and a separate display/filter axis. Does not silently change rank or demand. |

M08 and M10 share a pure, versioned priority policy; M08 does not import the map/export layer. Calibration can produce a new parameter artifact from training data only. Post-verification M06/M09 reports consume frozen predictions and outcomes and cannot feed them back into that ranking. M07 flags do not silently regenerate M02 nodes; any candidate-set change is a separate recorded scenario/version. This keeps the artifact dependencies acyclic.

## Shared metadata

All generated artifacts carry `schema_version`, `run_id`, `region_id`, `commodity_id`, `service_id`, `scenario_id`, `period_start`, `period_end`, configuration hash, input snapshot references and seed where randomness is used. A source snapshot has a publisher, original URL, retrieval date, source/effective date, file SHA-256, licence text/URL, permitted redistribution and processing step.

Evidence attaches to individual values or fields. A record containing observed capacity and estimated requirement must preserve both labels and source chains. `OBSERVED` means reported by the named source, not verified truth. Null values have an explicit missingness reason; no silent default, row deletion or capacity-zero substitution.

## Identity, geography and source joins

- Internal facility/node IDs are stable and independent of source row numbers. Source IDs include dataset and snapshot vintage; `OBJECTID` alone is not a cross-year facility ID.
- `shipping_point_id` identifies the outcome aggregation group, with an explicit facility-to-point crosswalk and match method. Aggregate predictions to that group before comparing with reported deliveries.
- Boundary IDs include country, geography type and boundary vintage. Keep source administrative codes and labels; names alone are insufficient join keys.
- Coordinates declare CRS and longitude/latitude order. Preserve source CRS; normalized point storage uses EPSG:4326. The Canadian boundary source uses NAD83 / Statistics Canada Lambert (EPSG:3347); metric calculations must declare and check the chosen projection and any datum conversion.
- Audit uniqueness and join cardinality. Record counts before/after every join; ambiguous/unmatched records go to an explicit review report. Crosswalks for Small Area Data Regions and CCS/Census Agricultural Regions are versioned, not assumed identical.

## Domain tables

| Contract | Required fields / semantics |
|---|---|
| Registry | `facility_id`, source-record ID, snapshot, name/operator, facility class, status as stated, effective date, location, precision P1–P5 and per-field provenance. |
| Node | `node_id`, optional facility ID, type, documented/rule-based origin, existence status, stationary-service eligibility, location/precision and unresolved verification question. |
| Capacity observation | Node/facility, service, original value/unit, dimension (`storage_mass`, `mass_flow`, `airflow`, `electric_power`), definition, period if relevant, source/evidence, known/unknown status and reviewed conversion. |
| Production | Production-unit ID, commodity, original source quantity/unit, reporting period, geometry, source evidence; modeled tonnes and spatial allocation method are separate estimated fields. |
| Accessibility | Origin, candidate node, graph snapshot, scenario/mode, minutes and reachability status; unreachable is not a zero-time edge. |
| Allocation | Origin, node or explicit unserved outcome, scenario, assigned tonnes per period and inventory scenario references. Preserve source mass once; known constraints must match the modeled dimension. |
| Inventory | Node, commodity/service, period/scenario, stored tonnes, residence/turnover assumptions and competing-crop occupancy. Annual delivery does not become instantaneous inventory automatically. |
| Requirement | Node/service/scenario, modeled inventory/throughput, electrical kW and kWh per stated period/cycle, range/distribution summaries, parameter provenance and unknown reasons. |
| Supply / gap | Node/service, one of the PRD's three supply states, compatible documented capacity, signed `capacity_minus_requirement` in the same unit, gap bucket and classification status. Storage and aeration supply are separate. |
| Baseline prediction / outcome | Arm, node or shipping-point/group ID, period, predicted quantity/rank; observed outcomes stay in a separate partitioned table with source and unit. |
| Siting | Spatial unit and block, presence-label provenance, common upstream feature definitions/units, split, model version and score. Unlabeled/background is not confirmed absence. |
| Uncertainty | Draw and seed, joint parameter/scenario references, pure-policy version, per-node membership and magnitude summaries. Membership frequency describes stability under the stated draws. |
| Shortlist / freeze | Node ID, rank, tier, evidence references, service-specific requirement/supply, single question, run/version, file hash and freeze identifier. |
| Verification | Frozen sample/node ID, observation date/method, consent status, outcome/failure taxonomy, unknown/unreachable state. Person-level details stay private. |

### Supply and gap rules

The three supply states remain: no documented asset; documented asset with known capacity; documented asset with unknown capacity. The three flagged buckets remain undocumented supply, undersized and verify first. They are distinct fields, not interchangeable labels. A known storage asset with no fan-capability observation does not become known aeration supply. A compatible known capacity that is not below requirement is not forced into the undersized bucket; it can have a null bucket with an explicit unflagged classification status, without claiming adequacy in reality. Exact service gap definitions and thresholds remain human-owned before real classification.

### Benchmark input mapping

- CGC `deliveries_kT` is kilotonnes, converted explicitly to tonnes with original values retained. Filter `crop_year=2024-2025` and `grain=Wheat`; do not include `Amber Durum`, totals or duplicate outcomes.
- AAFC `Capacity_tonne` is reported storage tonnes. It is not processing/day capacity or fan power. Keep unknown/nonpositive source values for audit, with no silent interpretation.
- Production uses the matching non-durum wheat category from Statistics Canada; validate the category mapping, suppression flags and units before use. Annual Crop Inventory is a crop-location proxy, not measured cell-level production.
- Peak/seasonal allocation requires sourced harvest, residence-time and occupancy scenarios. No annual-total division by 365 as an undocumented daily estimate.

## Siting allowlist and leakage boundary

Candidate initial covariates are external production/accessibility, population, road class/junction structure and town status. Features must be constructed with the same meanings for development and transfer regions. Night lights remain optional. Processor-distance features are disabled until their source and fold construction are shown to be independent of withheld presence labels; a candidate's own facility record cannot reveal its label through a zero-distance feature.

No allocation, shared-capacity assignment, delivery outcome, technical energy requirement, supply state, gap or verification result is a siting feature. Fit preprocessing and feature selection inside development folds. Manitoba outcomes cannot influence normalization, model choice or thresholds. Separately label any later local adaptation experiment.

## Phase 1 acceptance plan

Implement hand-computable cases that exercise: missing capacity preserved; storage vs throughput vs power rejected at incompatible comparisons; kilotonne conversion; CRS/lon–lat misuse; stable identities and join-cardinality failures; one shipping-point outcome shared by two elevators without double counting; explicit unserved mass; conservation; deterministic ties/seeds; blocked siting features; and separation of development/transfer outcomes. Hand-reviewed expected answers are recorded with the fixtures.

Use the PRD stack: Python 3.12, uv and a committed lockfile, pydantic-validated configuration, pytest, ruff and GitHub Actions. Scientific modules and web implementation remain later-phase work.
