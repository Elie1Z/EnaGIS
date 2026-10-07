# 0005 — Phase 3 walking skeleton and temporary scenario boundary

Status: **implemented engineering integration**, 7 October 2026. The user authorized Phase 3. This follows its explicit permission for temporary scenario inputs; it does not assert human scientific approval or change decision 0003's benchmark.

## Executable method

Run the open Phase 2 spine through documented nodes → reporting-region production → administrative assignment → conserved throughput → inventory → fan duty → supply documentation → gap → deterministic ranking → CSV shortlist and typed traces. Only Alberta and Saskatchewan enter assignments and rankings. Manitoba is excluded from this development run; no model is fitted or selected.

Retain production at actual SADR resolution. Equal shares among eligible nodes in the same region are a **temporary administrative scenario**, not trade flows, farm locations, road catchments or travel times. Bound shares by configured inventory/storage constraints, redistribute remaining mass equally and record unresolved overflow as unserved. A node belongs to at most one origin. Do not use CCS overlaps as crop weights or add province controls or CGC delivery outcomes as production.

Coordinate-conflict and unresolved/ineligible nodes retain UNKNOWN modeled throughput and no rank. Missing production creates UNKNOWN balances, never zero or an invented fallback. Reconciliation covers only the known origin subset; unknown-origin unserved mass cannot be quantified.

## Approval boundary

`configs/scenarios/phase3-engineering-v1.json` declares all numbers, units and method choices. Every parameter and method approval is null. The command refuses that scenario without `--allow-temporary-scenario`; this flag permits the labelled integration exercise, not scientific approval.

A `scientific_reviewed` configuration instead requires recorded human method approval and sourced, approved parameters. Scenario-only provenance cannot establish scientific sourcing. Additional evidence must refer to pinned permitted snapshots. Source suitability, commercial applicability and verification gates still require human review.

Requirements are ESTIMATED conditional on hypothetical assumptions; rankings and gap buckets are INFERRED integration results. The warning survives in every trace/CSV row and the audit. No calibrated score, Monte Carlo interval, annual electricity-use estimate, operational finding, field validation or worldwide accuracy is established.

## Inventory and physical boundary

For assigned harvest tonnes `M`, residence days `r` and modeled operating days `D`:

```
inventory_tonnes = M * r / D
assignment_limit_tonnes = reported_storage_tonnes * wheat_fraction * D / r
Q_m3_s = inventory_tonnes * airflow_m3_s_per_tonne * simultaneous_fraction
electrical_kW = Q_m3_s * static_pressure_Pa / (1000 * fan_efficiency * motor_efficiency)
                + auxiliary_kW_when_inventory_is_positive
one_cycle_kWh = electrical_kW * cycle_hours
```

Steady-flow inventory is hypothetical, not peak harvest inventory. `D=365` is a denominator, not an operating-status observation. The 0.5 wheat fraction reserves half of all-commodity storage, not the entire reported storage. Unknown capacity imposes no numerical bound and remains UNKNOWN rather than zero. All real development storage values happen to be known.

Fan efficiency is defined consistently with static-pressure air power at the duty. The temporary boundary assumes direct motor drive, grain-plus-duct pressure and concurrent duty; simultaneous fraction defaults to one. It excludes startup current, other elevator machinery, drying heat and unmodeled drive/control losses. Auxiliary zero is an explicit fan-only scenario, not observed absence. Equal lower/central/upper values record one calculation, not an uncertainty interval.

For method review, [UMN fan guidance](https://extension.umn.edu/agriculture/crop-production/corn/selecting-fans-and-determining-airflow-for-grain-bins) describes flow, crop depth, resistance and efficiency, with a 60% impeller-efficiency example. The [DOE fan sourcebook](https://www.energy.gov/sites/default/files/2014/05/f16/fan_sourcebook.pdf) separates air power from motor input and discusses system losses. These support reviewing the equation and boundary, not commercial coefficients.

[UMN wheat-storage guidance](https://extension.umn.edu/agriculture/crop-production/small-grains/storing-wheat-and-barley) gives a farm-bin example of 150 cooling hours at 0.1 cfm/bushel and stresses measuring cooling completion. Temporary cycle duration borrows that example only to exercise integration. The configured 0.002 m³/s/tonne is hypothetical, not a conversion of that recommendation. Residence, storage share, pressure and motor efficiency are hypothetical too. Review actual inventory, bin geometry, fan curves, weather/cycles and commercial applicability before scientific use. Guidance URLs are review references, not pinned measurement inputs; no source text is redistributed.

## Supply and ranking

The consumed open registry documents storage, not fans or electrical infrastructure. Real run nodes have **no documented asset within that source scope**, with UNKNOWN electrical capacity and margin. Positive scenario requirements get `undocumented_supply`, never an assertion of absence. Storage tonnes cannot be compared with kW.

The implementation also supports documented known electrical capacity and documented unknown electrical capacity. Compatible known capacity gives `capacity − requirement`: negative is `undersized`, nonnegative is unflagged. Documented unknown capacity is `verify_first`. Missing requirement prevents an invented numerical deficit. The current snapshot supplies no electrical observations; those two documented states are tested with clearly synthetic records.

Order positive calculable nodes by descending scenario kW, then stable node ID; publish the first ten plus the full ranking. This is initial engineering ordering, not final scientific priority. Questions request location/licensing, wheat inventory/residence and actual fan duty. No participant has been contacted or committed.

## Reproducibility and later gates

Hash the input index, consumed table bytes, scenario, region configuration, manifest, source code and lockfile. Arithmetic mass tolerance is explicitly 10⁻⁶ tonnes, not scientific precision. No draws are used; seed is null. Preserve permitted source hashes, dates, licences, evidence labels, CRS and conservative precision. Private licensing/verification data and outcome labels do not enter this run.

Scientific routing/disaggregation, harvest profiles and commercial parameters remain human-owned. Resolve source/temporal inconsistencies and missing production before reliance on affected records. Phase 4 must preregister independent label-free features, spatial blocks and keep/kill rules. Shortlist outputs cannot be siting features.
