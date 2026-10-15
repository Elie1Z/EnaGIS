# EnaGIS documentation

New here? Read the four pages under **Start here**, then go to the section you need.

## Start here

| Page | What it answers |
|---|---|
| [Overview](overview.md) | What EnaGIS is, who it is for, the decision it supports |
| [Method](method.md) | The method on one page, with links to the deep dives |
| [Limitations and non-claims](limitations.md) | What we never claim |
| [Architecture](architecture.md) · [Glossary](glossary.md) | How the pieces fit; terms |

## EnaGIS Live (the main tool)

| Page | What it answers |
|---|---|
| [Live engine method](live-engine.md) | Data gathering, road catchments, energy estimate, uncertainty |
| [Phase 4R results](phase4r-results.md) | The Rwanda siting model and its registered test (KEEP) |
| [Phase 4X results](phase4x-results.md) | XGBoost against the registered model (not better) |
| [Second site](second-site.md) · [Scouting](second-site-scouting.md) · [Phase 4N results](phase4n-results.md) | Can the suggested tools run elsewhere? (Njombe: KILL) |
| [Rwanda national screening](rwanda-national-screening.md) | All 30 districts, end to end |
| [Nyabihu assumptions](hero-assumptions.md) · [Data vintages](hero-data-freshness.md) · [Verification protocol](hero-verification-protocol.md) | The frozen Nyabihu case |

## Evidence, validation and data

| Page | What it answers |
|---|---|
| [Validation](validation.md) | Metrics, intervals, protocol, verdicts |
| [Evidence ledger](evidence-ledger.md) | What we know, estimated and do not know |
| [Rwanda data](../data/rwanda/README.md) · [Data catalogue](data-catalogue.md) · [Licence audit](data/licence-audit.md) | Every dataset: source, date, licence, hash (the catalogue covers the Canadian pilot) |
| [Reproducibility](reproducibility.md) · [Proof of work](proof-of-work.md) | Clean rebuild, checksums, counts |
| [Scope and transfer](scope-and-transfer.md) · [Scaling guide](scaling.md) | Applying EnaGIS to a new country or crop |
| [FAQ](faq-for-judges.md) | Hard questions, short answers |

## Specifications and decisions

- [`spec/`](spec/): interface contracts, schemas and registered protocols (`*.sha256` pins each protocol).
- [`decisions/`](decisions/): one record per decision, numbered 0001 to 0015.
- [`proposals/`](proposals/): scientific changes awaiting approval.
- [`reference/`](reference/README.md): the founding PRD and design concepts.
- [`audits/`](audits/): machine-readable audit and evaluation records (hash-registered; do not edit).

## Working on the project

- [How we build](development-process.md) · [Contributing](../CONTRIBUTING.md) · [Good first issues](good-first-issues.md) · [Help wanted: data](help-wanted-data.md) · [Roadmap](roadmap.md)

## Project history (Canadian pilot, Phases 0 to 8)

Kept as the record of how the method was built and tested. Start with [project history](project-history.md).

| Phase | Records |
|---|---|
| 0–3 | [Phase 0](phase-0-completion.md) · [Phase 1](phase-1-completion.md) · [Phase 2](phase-2-completion.md) · [Phase 3](phase-3-completion.md) |
| 4 (siting experiment, KILL) | [Status](phase-4-status.md) · [Completion](phase-4-completion.md) · [Run log](phase4-run-log.md) |
| 5 (offline demo) | [Completion](phase-5-completion.md) |
| 6 (scientific review) | [Status](phase-6-status.md) · [Desk review](phase6-desk-review.md) · [Review packet](phase6-scientific-review.md) |
| 7 (verification toolkit) | [Status](phase-7-status.md) · [Evidence requests](phase7-evidence-request.md) · [Field form](phase7-field-form.md) |
| 8 (MVP) | [Method report](phase8-method-report.md) · [Acceptance](phase8-acceptance.md) |
