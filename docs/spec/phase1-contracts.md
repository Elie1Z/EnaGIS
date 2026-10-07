# Phase 1 executable interface specification

Contract version: **1.0.0**. Python definitions in `src/enagis/contracts.py`; cross-record checks in `src/enagis/validation.py`; machine-readable bundle schema in [phase1-bundle.schema.json](phase1-bundle.schema.json). The [Phase 0 semantics](phase0-interfaces.md) and decision 0003 govern interpretation. These interfaces implement the foundation, without executing scientific modules.

## Serialization and common metadata

Use `Bundle.model_validate_json(bytes)` or `Bundle.model_validate(mapping)` at module boundaries. Invalid inputs raise `ValidationError`; the CLI reports them to stderr and exits 1. Additional fields are forbidden. An adapter must explicitly map source fields; the validator never repairs unknown values or drops records. `canonical_bytes(model)` sorts JSON keys and adds one LF for stable hashing.

A bundle contains one scenario/run and tables. All enclosed tables inherit its required `metadata`: schema version, run/region/commodity/service/scenario IDs, start/end dates, configuration SHA-256, source snapshot IDs and seed (explicit null if deterministic). A standalone table uses `Artifact[RowType]` with the same metadata; use bundle validation before integrating tables to check references and conservation. Never export bare rows without the metadata wrapper.

The schema JSON describes structure and local numeric constraints. Python validation also enforces cross-field and cross-table semantics; JSON Schema alone cannot prove conservation or compare foreign keys. Contract changes require updating the version according to compatibility and regenerating the schema, with tests and downstream consumer review.

## Evidence, identity and geography

Every uncertain domain value uses `Value[T]`: `value` plus `evidence`. Evidence requires a label, source snapshot references, as-of date, licence, derivation method and explicit `missing_reason` (null for known values). Null requires **UNKNOWN** and a nonempty reason; a known zero has a known label. OBSERVED, PREDICTED, ESTIMATED and INFERRED survive round trips. Manifest references resolve in a bundle, including those in embedded node cards. OBSERVED is a report from its source, not independently verified truth.

Source snapshots carry publisher, original URL, retrieval/effective dates, SHA-256, licence and licence URL, redistribution status and processing step. Phase 2 will check these hashes against actual input files and audit licences; presence of a valid manifest is not proof that the file or terms have been verified.

Internal facility/node IDs must be stable across adapters/vintages. Source record IDs have the format `<snapshot_id>:<source_key>`; unqualified row numbers/OBJECTIDs are rejected. Internal uniqueness and source-record uniqueness are asserted. Stability across years still requires the reviewed identity crosswalk in Phase 2.

`SpatialID` is country + geography type + boundary vintage + code, with the original geographic identifier retained. `Point` uses named longitude/latitude fields, `EPSG:4326`, declared longitude-first order, original CRS and transformation method. Ranges reject common Canadian axis swaps. When both swapped numbers are legal globally, an adapter must check the actual regional extent; range validation cannot infer an author's intent. P5 has a null point; P1–P4 have a representative point and retain their precision class.

`RegionConfig` declares adapter/boundary versions, disjoint development/transfer units, CRS and a projection-review reference. It is distinct from `pilot-scope.json`. Geographic unit mappings preserve the frozen split; Manitoba cannot enter development by changing its label. CRS validity and projected metre units are checked by pyproj; suitability for the study extent and routing distortion still require the region's projection review. The toy EPSG:3347 choice is not approval for real routing. PROJ network downloads remain disabled in CI.

## Row contracts and consumers

| Row model | Interface and main safeguards | Next consumer |
|---|---|---|
| `Facility` | Stable/source IDs, snapshot, sourced name/operator/class/status, effective date, precision/location. Unknown operator/location retained. | Registry adapter/node construction |
| `Node` | Linked facility or reason, type/origin, sourced existence/eligibility, location, question. Logistics-only cannot claim stationary eligibility. | Accessibility and downstream scenario modules |
| `Production` | Geographic/geometry refs and CRS, commodity, original mass/reporting period, optional reviewed conversion, separate ESTIMATED modeled tonnes and spatial method. | Production adapter/allocation |
| `Travel` | Origin/node/graph/scenario/mode, reachable state, sourced minutes, configured projected metric CRS. Unreachable or unknown travel stays null. | Catchment construction |
| `Catchment` | Origin/node/scenario, explicitly supplied travel limit, travel time, method/evidence. Time cannot exceed the supplied limit. | Allocation variants |
| `Allocation` | Source production, node or explicit unserved reason, scenario, assigned tonnes, inventory scenario. Per-source assignments plus unserved conserve input once. | Inventory/requirement |
| `Capacity` | Source quantity, service/node/facility, known/unknown, optional reviewed conversion. No generic `capacity` scalar. | Supply interpretation |
| `Inventory` | Stored tonnes, explicit residence and occupancy scenario references. May be UNKNOWN. No implicit annual-to-daily conversion. | Aeration physics |
| `Requirement` | ESTIMATED/UNKNOWN kW and kWh ranges, cycle/period, peak method, inventory/parameter refs. Ineligible nodes remain UNKNOWN. | Supply/gap policy |
| `Supply` | Three documentation states, evidence/scope, capacity ref even for documented unknown capacity. Known storage is not known electrical supply. | Gap policy |
| `Gap` | Electrical kW signed capacity-minus-central-requirement, separate flagged bucket/classification, evidence and policy ref. Known nonnegative margin can be unflagged. | Ranking/uncertainty |
| `Uncertainty` | Seed, count/inclusions/frequency, separate kW magnitude range, tier, joint scenario/policy refs. Frequency must equal supplied counts. | Ranking/node card |
| `NodeCard` | Node/rank/tier/location, exact requirement/supply/gap, evidence, question, version/freeze/hash. Embedded results must match the scenario tables. | Static export/UI later |
| `ShippingLink`, `Outcome` | One reviewed facility-to-group link; one OBSERVED grouped quantity per shipping point in a single run/period/commodity, original kT and converted t. Outcome rows stay separate from predictors. | Hindcast later |
| `SitingFeature`, `Partition` | Explicit upstream feature allowlist, source/unit/method, label-free declaration, spatial block and immutable region split. Transfer excludes fitting and model selection. | Siting experiment later |
| `ScientificParameter` | Sourced value/unit and human approval/date; `require_approved()` fails for missing or unapproved values. | Future runtime science configuration |

## Units, joins and invariant checks

Supported quantity pairs are `storage_mass` ↔ tonne/kilotonne, `mass_flow` ↔ tonne/day, `airflow` ↔ m³/s (serialized `m3/s`), `electric_power` ↔ kW, and `energy` ↔ kWh. Flow/energy require reporting periods. Production mass has its reporting period too. Negative/nonfinite capacities are invalid canonical quantities; Phase 2 must retain such raw source values in a quality report instead of silently coercing them.

`Conversion` retains source/converted quantities, factor, reviewer and evidence. Only same-unit identity and kT ↔ t conversions are currently supported (1000 or 0.001); other conversions need an explicit contract extension. A conversion cannot change dimensions or period. `compare_quantities` requires identical dimension/unit/period and known values. A gap margin uses matching electrical capacity and the modeled central kW, and retains its sign. Toy flags establish serialization cases only; meaningful scientific thresholds and classifiers remain later human-approved configuration.

`checked_many_to_one` rejects duplicate right-side IDs and returns every left row plus before/after counts and unmatched keys. Pipeline joins must call a cardinality checker and persist the audit. The foundation does not implement many-to-many spatial overlays. Bundle integrity checks reject duplicate table IDs, unresolved references, scenario/service mismatches, missing source mass and duplicate shipping-point outcomes.

`stable_order` orders externally supplied finite scores descending with stable ID ties. It is a mechanical helper, not the priority policy. Seed is mandatory for uncertainty, matches the run, and is preserved. No uncertainty draws or ML predictions are generated yet.

## Scientific boundary and remaining reviews

Fixture ranges, gap flags, assignments and ranks are supplied synthetic records. There is no allocator, energy physics, calibrated model, gap classifier, Monte Carlo engine, real ranking freeze or map in Phase 1. The validators cannot establish that an adapter's claimed label-free feature is scientifically independent; Phase 4 must review actual feature construction and enforce fold-local preprocessing. Private verification data have no public-output contract here.

Before real execution, resolve the [Phase 0 gates](../phase-0-completion.md), register each scenario's sourced inventory/physics/policy artifacts, and validate real source extent, units and crosswalks. Config/source/scenario reference IDs provide an interface; their scientific contents must be checked by the relevant module. Adapters for new regions produce these same contracts and report local coverage before any transfer claim.
