# Phase 1 completion audit

Status: **COMPLETE — repository foundation and validated contracts**, 7 October 2026.

Phase 1 implements the engineering boundaries frozen in Phase 0. Decision 0003 and `configs/pilot-scope.json` are unchanged. No real source ingestion, scientific training, energy validation or field verification is claimed.

## Exit criteria

| Criterion | Delivered evidence |
|---|---|
| Core interfaces explicit | Pydantic contracts and bundle integrity validation; [interface guide](spec/phase1-contracts.md) and generated [JSON schema](spec/phase1-bundle.schema.json), version 1.0.0. |
| Hand-computable fixtures | Eight synthetic cases with [independent worked answers](../tests/fixtures/README.md): one node, competing nodes, known/unknown capacity, overflow, logistics-only, missing facility, all-unserved. |
| Tests run locally | **78 tests passed**, Python 3.12.14, Windows; offline, using the locked environment. |
| Lint/static checks run | Ruff check and format check both passed. Ruff checks imports, undefined names and selected static rules; no separate type checker is claimed. |
| Lightweight CI | `.github/workflows/ci.yml` installs the lockfile and runs `make check` on Ubuntu with PROJ networking disabled; action releases are pinned by commit. Local equivalent commands passed. Hosted CI has not run because the commits have not been pushed. |
| Stable downstream schema | Strict additional-field rejection, evidence/missingness/unit/CRS/ID rules, foreign-key and mass-conservation checks; committed-schema regression test. |
| Reproducibility | Committed `uv.lock`, Python 3.12 target, offline smoke command, preserved seed/config/input hashes, canonical bundle hashing and deterministic ID tie break. |

## What was checked

- Null capacity stays UNKNOWN with a reason; known zero remains known. Missing operator, existence, eligibility and location are retained.
- Storage tonnes, mass flow, airflow, electrical power and energy cannot substitute for one another; periods and explicit kT-to-tonne conversion are checked.
- Named longitude/latitude, normalized/source CRS and P1–P5 precision are required. Metric CRS resolves to a projected metre definition; configured projection must match travel records.
- Duplicate IDs, unqualified source row IDs, unresolved evidence/foreign keys, bad ranges, incorrect margin signs/arithmetic and conflicting scenario/service metadata fail visibly.
- Joins retain and count left rows, audit unmatched records and reject ambiguous right keys.
- Assigned plus unserved mass equals source mass. Two elevators share one shipping-point outcome; group prediction is summed once.
- Logistics-only and unknown-eligibility candidates keep stationary requirements UNKNOWN. Supply states and gap flags remain distinct; a compatible nonnegative margin is unflagged.
- Siting features use an explicit upstream allowlist. Processor-distance and optional night lights are deferred pending source/fold audits. Transfer cannot fit preprocessing, select models or be relabelled as development through the regional split.
- Uncertainty count/frequency/seed invariants, shortlist references, stable tie break, serialization and CLI failure exit codes are tested.
- The smoke command passes all eight worked examples and emits reproducible bundle hashes. The committed [smoke audit](audits/phase1-smoke.json) records those toy outputs.

## Environment and bootstrap choices

The supplied bootstrap was reviewed. There was no pre-existing executable infrastructure to preserve. Its Python/uv/pytest/Ruff/Make conventions were retained; its later-phase toy scientific algorithms were not installed as production science.

Direct locked packages: pydantic 2.13.5, pyproj 3.7.2; dev packages pytest 9.1.1 and Ruff 0.16.10. The build backend is pinned to hatchling 1.32.4. The runtime/dev transitive packages and platform wheels are resolved in `uv.lock`. The installed direct package metadata declares MIT licences; future geospatial/data additions need their own compatibility review. No national source datasets are dependencies of this phase.

Windows application control blocked pyproj 3.8.0's native library. The established 3.7.2 release line loaded and passed the CRS tests, so the project constrains pyproj to `>=3.7.2,<3.8`. Local tests use a workspace temporary directory. The supported CLI uses `python -m enagis` to avoid executable launcher restrictions. Make is absent on this Windows machine; its individual uv command equivalents were run directly. CI uses the same commands through Make.

CI action provenance: [checkout v7.0.0](https://github.com/actions/checkout/tree/v7.0.0) and [setup-uv v10.1.0](https://github.com/astral-sh/setup-uv/tree/v10.1.0) were verified against their official release tag commit IDs; uv is fixed to 0.12.5 and CI Python to 3.12.14. Initial environment setup requires package access; subsequent fixture checks explicitly use offline mode.

## Limits and Phase 2 handoff

These schemas validate structure and engineering invariants. They cannot establish scientific applicability, true facility absence, input-file authenticity, a feature's actual independence or worldwide accuracy. Plausible but incorrect coordinates whose swapped values both fall in legal ranges need regional extent/source checks in adapters. A projected CRS still needs suitability review. Synthetic source/freeze hashes identify fixture markers only.

Baseline modelling, real allocation variants, inventory physics, siting fitting, Monte Carlo, ranking policy and private verification remain their assigned later phases. Unknown/unapproved parameter values raise an explicit execution-gate error; no approved science configuration is invented here. Real source files, identity/administrative crosswalks, quality reports and licensing checks are Phase 2 work. All [Phase 0 execution gates](phase-0-completion.md) remain in force.

Phase 2 should consume the versioned contracts, put acquired raw files and private data in the ignored directories, audit counts after every join, and keep Manitoba untouched. Exported tables must carry run metadata and their source chain. Any contract extension must regenerate the JSON schema, add an independent fixture where needed, and pass the foundation checks.
