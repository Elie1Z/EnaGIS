# How we build EnaGIS

## Who decides what

| The team owns | How it is recorded |
|---|---|
| Scope, commodity and geography | [PRD](reference/prd-2026-10-04.md), decisions [0002](decisions/0002-global-transfer.md) and [0003](decisions/0003-benchmark-lock.md) |
| Protocols, registered before any result is seen | `docs/spec/*-protocol.md` with SHA-256 files; Git tag `preregister-phase4-canada-v1.1` |
| Scientific parameters and thresholds | Versioned files in `configs/`; changes go through [proposals](proposals/) |
| Data choices and outreach | [Data catalogue](data-catalogue.md), [help wanted: data](help-wanted-data.md) |
| Review of every change | Pull requests against the [repository rules](../CONTRIBUTING.md#rules) |

## How a change gets in

1. Write the interface or protocol first (schemas in `docs/spec/`, decisions in `docs/decisions/`).
2. Write the test, then the code. One topic per change.
3. `make check` (lint, tests, smoke fixture) and, for the live tool, `make live-test hero-repro`.
4. A second team member reviews. Judgment calls go into a decision record.

## Checks that do not depend on trusting any single author

- Evidence labels on every value; UNKNOWN is never filled with a default.
- Units and CRS declared at interfaces, row counts asserted after joins, production conserved.
- Protocols hashed before evaluation; negative results kept (Canada KILL, XGBoost not better,
  Njombe KILL).
- Hash-pinned inputs and verifiers: `verify-data`, `verify-run`, `verify-experiment`,
  `build_mvp --verify`, `hero-repro`.
- CI on a clean runner for every push (`.github/workflows/ci.yml`).

## Tools

We used AI coding assistants as tools for drafting code and documentation. Every change passed
the tests and verifiers above and the team's review; scientific choices were made by the team.
