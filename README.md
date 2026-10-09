<p align="center"><img src="web/assets/brand/enagis-wordmark.png" alt="EnaGIS" height="64"></p>

<p align="center">
<a href="https://github.com/Elie1Z/EnaGIS/actions"><img alt="CI" src="https://github.com/Elie1Z/EnaGIS/actions/workflows/ci.yml/badge.svg"></a>
<a href="LICENSE"><img alt="Code: MIT" src="https://img.shields.io/badge/code-MIT-blue"></a>
<a href="LICENSE-DATA.md"><img alt="Data: OGL-Canada / ODbL" src="https://img.shields.io/badge/data-OGL--Canada%20%7C%20ODbL-lightgrey"></a>
<img alt="Field verification n=0" src="https://img.shields.io/badge/field%20verification-n%3D0-orange">
<img alt="Siting model verdict: KILL" src="https://img.shields.io/badge/siting%20model-KILL%20(registered)-red">
</p>

**EnaGIS tells productive-use-energy teams which agricultural storage sites to investigate
first, and how sure it is.** It is a screening shortlist for phone checks and site visits, not a
feasibility study. Submitted to OSEAS 2026, *Assessment and Mapping of Productive Uses of Energy
(Agriculture)*.

## In 30 seconds

After harvest, grain sits in storage that needs electricity for aeration fans. Nobody publishes
which sites need the most power or which have enough. EnaGIS takes open registries and statistics
(no private data), estimates a technical energy requirement for each documented site, compares it
with documented supply, and produces a ranked top 10. Each site comes with its sources, an evidence
label on every number, and the one question to ask before a visit. Where evidence is missing it
says **UNKNOWN**, never zero.

The pilot covers 261 primary grain elevators in Alberta and Saskatchewan (AAFC 2024 registry).
We also ran a preregistered machine-learning siting experiment. It **did not beat** a simple
production-only baseline, and we report that loss.

![EnaGIS: ranked investigation list, map and site card](docs/screenshots/1-where-first.png)

## Quick start (3 commands)

Needs Python 3.12, [uv](https://docs.astral.sh/uv/) 0.12+, and network for the first install.
Node.js 22+ is optional (JavaScript tests and demo preflight).

```sh
git clone https://github.com/Elie1Z/EnaGIS.git && cd EnaGIS
uv sync --locked --cache-dir .uv-cache
uv run --offline --locked --cache-dir .uv-cache python -m pytest
```

Then open **`app/index.html`** in Chrome, Edge or Firefox. It works offline, with no server.
`make check` runs lint, tests and the smoke fixture; `make mvp verify-mvp` rebuilds and verifies
the app. Everything else is in [docs/reproducibility.md](docs/reproducibility.md).

## What is done, what is not

| Area | Status | Evidence |
|---|---|---|
| Open registry: 340 records with source, date, licence, precision class (all P2) | Done | [data catalogue](docs/data-catalogue.md) |
| ML siting experiment, preregistered at Git tag `preregister-phase4-canada-v1.1` | Done; **verdict KILL**: full model 35.71% vs production-only 39.76% recall at top 20% | [validation](docs/validation.md) |
| Shipping-point hindcast (52 groups) | Done; absolute volumes not validated | [validation](docs/validation.md) |
| Energy requirement and top 10 | Temporary engineering scenario; parameters **not** human-approved; range UNKNOWN | [method](docs/method.md) |
| Energy *gap* | UNKNOWN for all sites: no open data on installed electrical capacity | [evidence ledger](docs/evidence-ledger.md) |
| Field verification | **Not done (n = 0)**; tooling tested on synthetic data | [limitations](docs/limitations.md) |
| Transfer to a new region | Not evaluated; Manitoba hold-out untouched | [scope and transfer](docs/scope-and-transfer.md) |

## Documentation

| Start here | For |
|---|---|
| [Overview](docs/overview.md) | What EnaGIS is, who it is for, the decision it supports |
| [Method](docs/method.md) | One-page method plus links to the deep dives |
| [Validation](docs/validation.md) | Metrics, intervals, n, protocol, verdict, and what it does not show |
| [Limitations and non-claims](docs/limitations.md) | What we never claim |
| [Evidence ledger](docs/evidence-ledger.md) | What we know, estimated and do not know, and how to close each gap |
| [Data catalogue](docs/data-catalogue.md) | Every dataset with source, date, licence, hash and how to fetch it |
| [Scope and transfer](docs/scope-and-transfer.md) / [Scaling guide](docs/scaling.md) | Why Canada, and how to apply EnaGIS to a new country or crop |
| [Architecture](docs/architecture.md) · [Glossary](docs/glossary.md) | How the pieces fit; terms |
| [Reproducibility](docs/reproducibility.md) | Clean rebuild, checksums, runtime, hardware |
| [FAQ for judges](docs/faq-for-judges.md) · [Challenger Q&A](docs/challenger-qa.md) | Hard questions, honest answers |
| [Proof of work](docs/proof-of-work.md) | Counts and hashes taken from the repository |
| [Team guide](docs/TEAM_GUIDE.md) | Learn, explain and demo EnaGIS |
| [Contributing](CONTRIBUTING.md) · [Help wanted: data](docs/help-wanted-data.md) | How to help |
| [Roadmap](docs/roadmap.md) · [Changelog](CHANGELOG.md) · [AI use](docs/ai-use.md) | Plans, history, how AI was used |
| [Proposals awaiting approval](docs/proposals/) | Scientific changes not yet adopted |
| [Project history](docs/project-history.md) | Phase-by-phase record |

## Licences and citation

Code is [MIT](LICENSE). Data keeps its source licence: Open Government Licence – Canada,
Statistics Canada Open Licence, and **ODbL 1.0 for OpenStreetMap-derived roads**. See
[LICENSE-DATA.md](LICENSE-DATA.md). Cite with [CITATION.cff](CITATION.cff). AI assistance is
disclosed in [docs/ai-use.md](docs/ai-use.md).
