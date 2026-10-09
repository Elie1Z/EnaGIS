# Method

## One page

**Unit of analysis:** a documented aggregation node (here, a primary grain elevator).
**Service:** ambient-air aeration of stored non-durum wheat. **Period:** 2024 harvest /
2024–2025 crop year. **Area:** Alberta + Saskatchewan (development), Manitoba (untouched hold-out).
Scope decision: [0003](decisions/0003-benchmark-lock.md).

| Step | Input | Output | Unit | Label |
|---|---|---|---|---|
| 1 Registry | AAFC Grain Elevators 2024 | 261 development nodes, location P2, storage as reported | t (all commodities) | OBSERVED |
| 2 Production | StatCan 32-10-0002-01 (2024): Wheat, all − Wheat, durum per reporting region | 16 known regions, 9 UNKNOWN | t / year | ESTIMATED / UNKNOWN |
| 3 Assignment | Region production split equally among the region's eligible elevators, each capped at storage × 0.5 × 365 / 30 (annual throughput limit); excess kept as unserved tonnes | assigned tonnes per node | t / reporting period | ESTIMATED |
| 4 Inventory | assigned × residence (30 d) / operating days (365); ≤ 50% of storage by construction (checked) | stored tonnes | t | ESTIMATED |
| 5 Airflow | stored × 0.002 m³/s/t × simultaneous fraction (1) | airflow | m³/s | ESTIMATED |
| 6 Fan power | airflow × static pressure (500 Pa) / (fan 0.6 × motor 0.9) | electrical demand | kW | ESTIMATED |
| 7 Cycle energy | kW × 150 h | electricity per aeration cycle | kWh | ESTIMATED |
| 8 Supply | Documented electrical assets in consumed sources | `no_documented_asset` for all | — | INFERRED |
| 9 Gap | documented kW − required kW | UNKNOWN (no documented kW) | kW | UNKNOWN |
| 10 Rank | kW descending, stable node ID breaks ties | top 10 + question | — | INFERRED |

Parameters in steps 4–7 are **hypothetical and not human-approved**
(`configs/scenarios/phase3-engineering-v1.json`). Worked example, rank 1 (Dixon, SK):
184,751 t assigned → 15,185 t stored → 30.37 m³/s → **28.12 kW** → 4,218 kWh per cycle.
Five sites share exactly 28.12 kW, so their order is a tie, shown as "Tied ×5" in the app.

**Machine learning (separate branch).** Facility-siting experiment: does road-accessible
production predict where elevators are documented, beyond simpler baselines? Unit: census
consolidated subdivision (CCS). Folds: 7 census agricultural regions (spatial blocks). Metric:
mean recall of documented-presence CCS in the top 20% of scores per block. Keep/kill rule frozen
and remotely registered before evaluation. Result: KILL ([validation](validation.md)). Siting
outputs never feed the energy ranking, and allocation, capacity, energy and gap outputs never
feed siting features.

**Evidence rules.** Every value carries OBSERVED / PREDICTED / ESTIMATED / INFERRED / UNKNOWN
with source, date, licence and method ([decision 0001](decisions/0001-evidence.md)). UNKNOWN is
never defaulted. Joins assert row counts. Production is conserved through allocation (worst
residual in tests < 10⁻⁶ t). Storage mass, mass flow, airflow and electrical power are separate
types.

## Deep dives

| Topic | Document |
|---|---|
| Architecture and contracts | [design.md](../design.md), [spec/phase0-interfaces.md](spec/phase0-interfaces.md), [spec/phase1-contracts.md](spec/phase1-contracts.md) |
| Data ingestion and normalization | [spec/phase2-ingestion.md](spec/phase2-ingestion.md), [decision 0004](decisions/0004-source-normalization.md) |
| Pipeline formulas and traces | [spec/phase3-pipeline.md](spec/phase3-pipeline.md), [decision 0005](decisions/0005-phase3-walking-skeleton.md) |
| Siting experiment protocol | [spec/phase4-preregistration.md](spec/phase4-preregistration.md), [spec/phase4-experiment.md](spec/phase4-experiment.md) |
| Phase 6 engine (routing, capacity, uncertainty; synthetic so far) | [spec/phase6-science.md](spec/phase6-science.md), [phase6-desk-review.md](phase6-desk-review.md) |
| Verification protocol (not yet run) | [spec/phase7-verification.md](spec/phase7-verification.md) |
| Full method report | [phase8-method-report.md](phase8-method-report.md) |
