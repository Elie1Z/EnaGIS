# EnaGIS architecture and interface lock (Phase 0)

Status: **Phase 0 complete**, 7 October 2026. [Decision 0003](docs/decisions/0003-benchmark-lock.md) freezes the first benchmark under the PRD's best-candidate fallback. This document translates the PRD and the user's global direction into module boundaries; scientific implementation and validation follow in later phases.

## Product boundary

The analysis unit is a candidate **aggregation node**, with a type and an existence status. EnaGIS estimates stationary technical energy requirement associated with product processed or stored there, compares it with *documented* capacity, and ranks locations for investigation. A candidate is not assumed to exist or to have no supply merely because a registry lacks a record. Transit-only locations remain logistics-only and their stationary requirement is UNKNOWN. The output is a top-10 screening shortlist with evidence, uncertainty and a pre-visit question. The pipeline must be runnable without a server or network after inputs are pinned.

The global direction is held in [decision 0002](docs/decisions/0002-global-transfer.md); the first benchmark is frozen in decision 0003. It models non-durum wheat storage and ambient-air aeration electricity at Canadian primary grain elevators, using Alberta/Saskatchewan for development and Manitoba for transfer evaluation. The source period is the retrospective 2024 harvest / 2024–2025 crop year. Capacity, service and location choices remain versioned configuration rather than country-specific constants in core code.

## Region adaptation

Each region package declares its boundary/version, source snapshots, source-to-contract adapters, administrative crosswalk, CRS, crop units/periods, road modes, local scenarios and evidence coverage. Adapters normalize local source formats into the same contracts below. Core modules consume those contracts rather than country-specific source columns.

The common siting feature schema must have consistent meanings and units across training and target regions. Administrative sectors in Rwanda are one example of a spatial unit; other countries use documented local units and spatial blocks. One source unit may aggregate multiple facilities: shipping-point outcomes, for example, must be evaluated at shipping-point level rather than falsely treated as per-facility truth.

A new region progresses through data coverage checks, an untouched transfer evaluation, and local recalibration if justified. Supported outcomes are an evaluated model, a documented baseline fallback, or an insufficient-data result. A point on the world map does not itself provide production, facility or energy evidence.

Model fitting applies to the facility-siting experiment. Allocation, physics-based energy requirement and gap rules remain explicit methods with sourced local parameters. Changing commodity requires a separate service model and unit/processing audit, even when the location adapters are reusable.

## Directed module map

```text
pinned raw sources + manifest
  ├─> registry + node candidates ─────────────────────────────┐
  ├─> production representation ──────────────────────────────┤
  ├─> roads / accessibility ───────────────────────────────────┤
  └─> label-free covariates ─> siting experiment ─> siting report / check flags
                           (parallel; no downstream inputs)

registry + production + accessibility
  -> catchment / capacity-constrained allocation
  -> throughput + explicitly unserved production
  -> technical energy requirement (range and service class)
  -> documented supply state + signed capacity margin
  -> gap bucket
  -> uncertainty + baselines / hindcast
  -> ranking -> freeze -> verification analysis
  -> static map + node cards + shortlist + report
```

Energy-context layers are a second display/filter axis; they cannot silently alter the rank. Baselines consume common upstream inputs and the same evaluation outcomes as the proposed method. Hindcast consumes reported volumes only as observations for evaluation/calibration under the recorded split; it cannot leak into held-out predictions. Verification is downstream of a frozen ranking and cannot modify that ranking.

## Major contracts

Phase 1 will implement machine-validated schemas from the [M01–M11 interface specification](docs/spec/phase0-interfaces.md). The table below summarizes those interfaces. IDs are stable strings; joins must assert uniqueness, cardinality and retained row counts. Nullable values are explicit, never filled with zero.

| Output | Required content and units | Evidence / invariant |
|---|---|---|
| Source manifest | source ID, publisher, URL, retrieval and source dates, SHA-256, licence, redistributability, processing step | A retrieved file is pinned before use; unclear licence blocks public redistribution. |
| Registry record | facility ID, name/type, original source fields, status as stated, capacity value **with original unit and definition**, source/date/licence, precision P1–P5, geometry/CRS if available | OBSERVED means reported, not verified. No capacity inferred from facility count. |
| Node candidate | node ID, node type, existence status, stationary-service eligibility, location and precision, provenance | Distinguish documented facility, rule-based candidate and logistics-only point. Unknown existence stays UNKNOWN. |
| Production unit | spatial ID/geometry/CRS, commodity, time period, source value and original unit, conversion provenance, modeled volume in tonnes of input product per period | District statistics may be OBSERVED; finer spatial allocation is ESTIMATED. Do not relabel tree counts as observed tonnage. |
| Accessibility | graph snapshot ID, mode, season/scenario ID, travel time in minutes, reachable node IDs | File-based, dated OSM extract; speed and wet/dry multipliers configured and sourced. Distances use a declared projected CRS. |
| Allocation | production ID, node ID or unserved, scenario, assigned tonnes per period, source and capacity definition | Sum assigned plus unserved equals modeled input within tolerance; no double count; unknown capacity is not zero. |
| Energy requirement | node ID, scenario, throughput/inventory, energy distribution/range in kWh per period, service class, peak-power method and parameters | ESTIMATED technical requirement; no claim of actual usage or willingness to pay. Aeration power comes from fan duty; other service classes retain their appropriate batch method. |
| Supply/gap | node and service ID, one of three supply states, capacity dimension and comparable unit where known, signed margin, gap bucket, evidence | States: no documented asset; documented/known capacity; documented/unknown capacity. Buckets: undocumented supply, undersized, verify first. Known storage mass does not establish known fan capability. |
| Siting report | spatial unit, label provenance, approved label-free feature set, district-group split, score, top-fraction recall, Boyce index, intervals, baseline comparison | PREDICTED; unlabeled units are not negatives; no downstream leakage. |
| Ranking and shortlist | stable node ID, rank, tier, inclusion frequency under stated draws, source chain, unresolved question, scenario/version/hash | INFERRED screening priority, not calibrated viability probability. Freeze before verification. |
| Verification record | frozen shortlist ID, sampled node ID, contact/visit outcome, failure mode, date and consent status | Private person-level data; public reporting uses aggregates and intervals. |

Every spatial contract must declare input CRS and output CRS. Storage coordinates may use EPSG:4326 in longitude/latitude order; distance and area calculations require a suitable projected CRS selected in configuration. Every converted unit retains the original value and conversion method.

## Configuration and ownership

| Owner | Content |
|---|---|
| Versioned code | Parsing, validation, graph building, allocation, energy equations, evaluation, reporting and deterministic serialization. |
| Versioned configuration | Region ID and boundary/version, administrative crosswalk, commodity/service class, units and conversion rules, travel modes/speeds and seasons, parameter distributions and sources, thresholds, seeds, spatial blocks, scenarios. |
| Versioned source/manifest | Raw snapshots, hashes, licences and manual registry edits with who/when/how. Restricted sources remain outside the public rebuild and must have an open fallback or a documented limitation. |
| Human team | Scientific source suitability, parameter ranges, gap definitions, siting keep/kill threshold, verification protocol, field interpretation and release decisions. Scope changes follow a new decision record; the initial benchmark choice is already frozen under user authorization. |

## Scientific safeguards and phase boundary

- The siting study and a smaller pilot shortlist may have different footprints, but their exact footprints and spatial hold-outs must be recorded before fitting. Use the PRD's minimum positive count and at least six spatial blocks; no random row split to claim transfer skill.
- Preserve one geographic hold-out for transfer assessment. Compare the unadapted model, an approved local recalibration and applicable baselines on the same outcomes. Select thresholds before observing that hold-out. Do not report model scores as calibrated probabilities without calibration evidence.
- The siting branch may use accessibility-weighted production, population, road attributes, town status, processor distance and night lights only when sourced without downstream labels. Its output may flag undocumented facilities; it does not multiply demand for documented nodes.
- Capacity-constrained assignment must expose unserved production. `UNKNOWN` is never silently converted to zero. Supply states and gap buckets are separate fields.
- The ranking is an investigation priority; a high rank does not establish need, grid access, viability or an operating facility.
- Phase 0 defines scope and semantic interfaces. Executable validators, fixtures, CI and scientific implementation belong to later phases; unresolved execution gates are assigned in the [completion audit](docs/phase-0-completion.md).

## UI alignment

`docs/reference/design-original.md` proposes a dramatic static MapLibre presentation. The PRD commits to a clear static map and node card, with map polish late in the cut ladder. A pillar must not encode a numerical “energy gap” where only a gap bucket or unknown capacity is defensible. Animation, 2.5D pillars, Figma and Tailwind are optional presentation ideas, not pipeline dependencies or evidence of scientific validity. Evidence labels, source details, the top-10 and the single pre-visit question are useful concepts to carry forward.
