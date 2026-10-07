# Phase 0 completion audit

Status: **COMPLETE — product and architecture lock**, 7 October 2026.

The user authorized any data-rich location and requested closure of this phase. [Decision 0003](decisions/0003-benchmark-lock.md) freezes the first development benchmark under the PRD best-candidate fallback. Completion means the scope, interfaces and evidence responsibilities are explicit; it does not mean model training, energy validation or field verification has happened.

## Exit questions

| Question | Recorded answer |
|---|---|
| What exactly are we modeling? | Non-durum wheat aggregation/storage and technical electricity requirement for ambient-air aeration. |
| In what geography? | Canadian Prairies: Alberta and Saskatchewan development, Manitoba transfer hold-out. Retrospective 2024 harvest / 2024–2025 crop year. |
| What is a node? | A licensed primary elevator with storage; separate facilities can belong to one shipping-point outcome group. Transit-only points remain logistics-only. |
| What is the service class? | Electric fan aeration of stored wheat; actual fan installation/capability stays unknown without evidence. |
| What enters/exits each module? | [design.md](../design.md) and the [interface specification](spec/phase0-interfaces.md) cover M01–M11 and shared metadata, units, missingness and provenance. |
| Which decisions are frozen? | First benchmark footprint, commodity, node class, service, source period, study units and transfer footprint; offline Python/static MapLibre architecture and independent siting branch. |
| Which decisions remain human-owned? | Scientific parameter ranges, site-specific applicability, gap definitions, uncertainty thresholds, source interpretation, verification protocol and conclusions. |
| How will it adapt? | Region adapters normalize into shared contracts; local parameters and an untouched transfer evaluation establish evidence for reuse. |

## Data-gate outcome

The 2024 source audit found 340 Prairie primary-elevator records, 339 with positive reported storage capacity, and a `Wheat` delivery slice covering 184 shipping points. Exact name/province matching covers 181 of those points and 264 elevator records. This establishes data availability, not registry correctness or per-facility throughput.

The verification and energy/value gates are not fully passed. A named public technical contact and a dated operator contact lead are documented, but neither is committed to verification. The PRD's best-candidate fallback is explicitly invoked; these unknowns have not been promoted to observed evidence. Scientific readiness remains conditional on the following later-phase gates.

## Handoff gates and owners

| Item | Owner | Required before |
|---|---|---|
| Deduplicate registry, check coordinates/classes and reconcile within-year openings/closures | R2 / R4 | Phase 2 real-data ingestion and scientific hindcast. |
| Pin source files/versions and verify redistribution terms separately for AAFC, CGC, Statistics Canada and OSM | R2 / R1 | Public offline rebuild; feasibility fingerprints are not pinned raw files. |
| Confirm crop/category mapping and production/boundary crosswalks | R2 / R3 | Real allocation and siting features. |
| Review inventory, occupancy, airflow/resistance, efficiency and operating-cycle ranges, and commercial applicability | R3 / R4 | Real energy calculations; otherwise report missing parameters. |
| Confirm energy tariff/product-value basis and report the plausibility screen without a bankability claim | R3 / R4 | Scientific interpretation of the energy opportunity. |
| Secure a named verification participant and approve sample/consent/failure protocol | R2 / R4 | Frozen verification and any field-validation claim. |
| Record development blocks, splits, metrics and thresholds before fitting | R4 / R1 | Phase 4 experiment; keep Manitoba untouched. |

These are explicit execution gates for subsequent phases, not unanswered Phase 0 scope choices. If a gate fails, follow the PRD fallback and limitations rules; do not fabricate inputs or validation.

## Checks completed

- Supplied PRD and UI reference copies matched their originals by SHA-256.
- Current decision precedence was checked: original PRD → user global direction → benchmark lock.
- Local document links and scope JSON were checked; source audit counts reconcile with province totals and outcome-group semantics.
- Module dependencies, siting leakage boundaries and storage/flow/power distinctions were reviewed.
- Scientific code, model fitting and UI were not implemented during Phase 0. Runtime tests/lint begin in Phase 1.

## Next phase

Phase 1: repository foundation, machine-validated contracts, hand-reviewed toy fixtures, deterministic smoke command, pinned environment and CI. Start with the shared metadata/capacity contracts and the two-elevators/one-shipping-point fixture. No further country-selection question is needed.
