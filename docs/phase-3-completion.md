# Phase 3 completion audit

Status: **COMPLETE — walking skeleton with a temporary engineering scenario**, 7 October 2026.

The user authorized Phase 3. Its instructions explicitly allow marked temporary coefficients where human-owned values are unavailable. [Decision 0005](decisions/0005-phase3-walking-skeleton.md) records that boundary. This is completion of end-to-end engineering integration using real pilot sources, not scientific approval, a validated energy shortlist or field verification.

## Exit criteria

| Requirement | Result |
|---|---|
| Clean offline invocation | `uv run --offline --locked --cache-dir .uv-cache python -m enagis run --allow-temporary-scenario` reads the pinned Phase 2 spine and writes a ten-row real-data shortlist. |
| Complete vertical slice | Registry/node → regional production → administrative assignment → constrained allocation → inventory → concurrent fan duty → documented supply state → gap → deterministic rank → CSV and typed traces. |
| No double counting | One regional production origin is consumed once. Provincial controls, CGC outcome volumes, roads and private licensing data are unused. Multiple elevators remain distinct nodes. |
| Mass conservation | All 16 known development origins reconcile within 10⁻⁶ tonnes; maximum absolute residual 1.1641532182693481 × 10⁻¹⁰ tonnes. Unknown origins have null balances. |
| Capacity and units | Stored wheat remains within configured share of known all-commodity storage. Annual throughput and inventory are distinct; airflow, kW and one-cycle kWh have separate interfaces. Unknown storage is not zero. |
| Energy calculation | Parameterized inventory/flow/pressure/fan/motor/concurrency calculation; explicit temporary values and no scientific approval. No kWh/24 or actual-consumption inference. |
| Supply/gap | Three supply states implemented and tested. Real source scope documents storage only: electrical asset/capacity/margin remain undocumented/UNKNOWN. Undocumented does not mean absent. |
| Initial ranking | Scenario kW descending, stable ID tie-break, first ten. No final scientific score, uncertainty tier or siting model. |
| Traceability | `trace` returns source record, crop components, assignments, inventory, equations, configuration, supply/gap and rank, with source dates/hashes/licences and P2 precision. |
| Reproducibility | Typed exports, source/config/code/lock hashes, explicit null seed, deterministic byte-identical rerun and independent export verification. |

## Real development run

| Item | Result |
|---|---|
| Scope | Alberta/Saskatchewan, 2024 production; 79 Manitoba nodes excluded from run outputs. No fitting or hold-out evaluation. |
| Source nodes retained | 261 development nodes, all with source/quality traces. |
| Ranking | 186 calculable positive nodes; ten-row shortlist. |
| Missing/review dispositions | 72 nodes with UNKNOWN production, two coordinate-conflict records and one unresolved service-eligibility record stay unranked. |
| Production | 25 development SADR origins: 16 known, nine UNKNOWN. |
| Known mass only | Input 11,918,640 tonnes; assigned 11,918,640 tonnes; explicit unserved zero under this scenario. Missing-origin quantities are outside all these totals. |
| Supply | Scoped `no_documented_asset` at every real node; no fabricated fan/grid observations or numerical gap. Positive scenario requirements are `undocumented_supply`. |
| Exports | Ten indexed/verified artifacts plus index, including full production lineage, ranked/unranked traces, all assignments/balances, scenario and snapshots. |

The [machine audit](audits/phase3-pipeline-audit.json) records exact run/input/output hashes and local checks. Large normalized inputs and generated outputs remain ignored by Git; the pinned source manifest, scenario and implementation are committed. The [pipeline guide](spec/phase3-pipeline.md) explains rebuild and trace commands.

## Checks

- **114 tests pass**: 88 existing plus 26 Phase 3 tests/cases. These cover independent hand-calculated mass/energy results, bounded allocation/overflow, unknown storage/production, dimensions, scenario approval guards, three supply states, signed margins, spatial-conflict exclusions, source/order integrity, protected paths, offline end-to-end execution, hold-out exclusions and corrupted exports including checksum-updated semantic corruption.
- Ruff lint/format and all eight Phase 1 smoke cases pass. CI includes the complete small pipeline fixture with network access forbidden during the analytical run.
- The locked offline real-data command and `verify-run` pass; a repeated real run has identical artifact hashes. The first-ranked real node is traced successfully back through crop-component rows and source snapshots.

## Remaining gates and next phase

Human review of assignment, harvest/residence/occupancy profiles, airflow/resistance, efficiencies, cycles, gap policies and commercial applicability remains required before scientific use. The temporary configuration has no fabricated approvals. Scientific source/temporal reliability, production missingness, routing/disaggregation, tariff/value plausibility and verification participation/protocol gates from Phases 0/2 remain open. None is represented as completed by this engineering run.

Next is **Phase 4 — independent siting experiment**. Preregister upstream label-free features, development spatial blocks, metrics and keep/kill rules before fitting. Do not feed allocation, storage-capacity, energy or gap outputs into siting features. Preserve Manitoba for untouched evaluation and report local data coverage; this pilot does not establish worldwide accuracy.
