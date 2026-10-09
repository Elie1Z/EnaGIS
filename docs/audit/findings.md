# Pass 1 findings (read-only audit, 9 October 2026)

Audited state: HEAD `63579eb` (= `origin/main`) plus the uncommitted working-tree changes from
the earlier session. Evidence commands and raw outputs are in [audit-log.md](audit-log.md).
The status words used are DONE, PARTIAL and MISSING. "DONE" means the artifact exists and its
verifier passes. It does not mean the scientific claim is validated.

## A. Deliverable traceability matrix (before)

| # | Requirement | Artifact | Verify with | Evidence | Status |
|---|---|---|---|---|---|
| O1 | OSEAS: open ML/GeoAI pipeline that detects, classifies or predicts facilities | `src/enagis/siting.py`, `experiment*.py`; [phase-4-completion](../phase-4-completion.md); [phase4-evaluation.json](../audits/phase4-evaluation.json) | `python -m enagis verify-experiment outputs/phase4` | 6 artifacts verified; registered at tag `preregister-phase4-canada-v1.1`; verdict KILL | DONE (negative result) |
| O2 | OSEAS: interactive map of productive-use clusters or energy gaps | `app/index.html` | `python -m scripts.build_mvp --verify`; `node scripts/demo_preflight.mjs` | 43 artifacts verified; map shows *estimated requirement*. Gap is UNKNOWN for all 261 nodes (no documented electrical capacity) | PARTIAL |
| O3 | OSEAS: documentation of datasets, approach, validation, accuracy, scaling | `docs/data/manifest.json`, [licence-audit](../data/licence-audit.md), [method report](../phase8-method-report.md), Phase 4 report | read files | Datasets, method and validation exist across phase reports; no stand-alone scaling guide, data catalogue or validation page | PARTIAL |
| C1 | Open registry with source, date, licence, precision class, capacity with unit, status | `data/processed/phase2/registry.json` (rebuilt), `app/evidence/` | `python -m enagis verify-data data/processed/phase2` | 340 rows (AB 89, SK 172, MB 79), all P2, capacity OBSERVED in tonnes; 94 source rows excluded with reasons | DONE |
| C2 | Facility-siting experiment | as O1 | as O1 | Full model 35.71% vs B0 39.76% recall@top-20%; margin −4.05 pp [−39.29, −0.71] | DONE (KILL) |
| C3 | Throughput hindcast with stated fallback | `src/enagis/hindcast.py`; phase4 report | `verify-experiment` | 52 shipping-point groups, 7 blocks; absolute volume not validated | DONE |
| C4 | Capacity-constrained catchment allocation, one travel-time method, 2–3 variants | Phase 3 (admin equal share, real); Phase 6 engine (synthetic) | `make phase6-fixture verify-phase6` | Real product uses administrative equal-share only | PARTIAL |
| C5 | Physics-based energy requirement with ranges | `src/enagis/energy.py`, `science/energy.py` | `pytest tests/test_pipeline.py tests/test_science.py` | Real output is a single temporary scenario; range UNKNOWN | PARTIAL |
| C6 | Three supply states and gap buckets | `src/enagis/contracts.py`, `energy.py` | `pytest -k supply` | Implemented and tested; all real nodes `no_documented_asset` | PARTIAL |
| C7 | Monte Carlo tiers | `science/uncertainty.py` | `make phase6-fixture` | Synthetic only; real tiers not assessed | PARTIAL |
| C8 | Baselines B0, B1, B2, population, expert shortlist | phase4 report | `verify-experiment` | All except expert shortlist | PARTIAL |
| C9 | Wet/dry, peak/off-peak, best visit window | Phase 6 engine (synthetic); UI controls disabled | — | No real seasonal or visit-window output | MISSING |
| C10 | Frozen verification n ≥ 12 with failure modes and intervals | `src/enagis/verification/`; [phase-7-status](../phase-7-status.md) | `make phase7-fixture` | Tooling and synthetic rehearsal only; real n = 0; no `ranking-v1` | MISSING |
| C11 | Decisive top-10 plus pre-visit checklist | `app/shortlist.csv`, node card | `build_mvp --verify` | Top-10 exists; ranks 1–5 and 7–10 are exact ties; confidence UNKNOWN | PARTIAL |
| C12 | Static map, node card, shortlist file | `app/` (CSV + GeoJSON, not GeoPackage) | preflight | All present offline | DONE |
| C13 | Clean-machine rebuild, data manifest, CI smoke, limitations report | CI workflow, README, limitations page | CI run 37861220385 | CI green on clean runner; no rebuild by an independent person | PARTIAL |

**Counts (before): DONE 5, PARTIAL 9, MISSING 2** (16 rows).

## B. Clean-room reproduction (before)

- Fresh clone of `origin/main` (`63579eb`). README install `uv sync --locked --cache-dir .uv-cache`: OK in 35 s (needs network).
- **Host blocker:** this Windows host's Application Control policy blocks executing a newly created venv launcher (os error 4551). This is not a repository defect. Workaround: use the identically locked interpreter (same `uv.lock` SHA-256) with `PYTHONPATH` set to the clone.
- With that workaround: 227 tests passed, lint and format passed, smoke passed, MVP rebuild verified, `app/manifest.json` byte-identical to the recorded `d7c8c554…`, and the working tree was clean after the rebuild. Total 39 s.
- Independent confirmation: GitHub-hosted clean Ubuntu runner, run 37861220385, `success`.
- **Undocumented steps / tribal knowledge (FAIL items):**
  - README has no three-command quick start; the install and check commands are spread across sections.
  - Node.js ≥ 22 is needed for the JS tests and preflight, but the README does not list it as a prerequisite.
  - The real-data pipeline needs `enagis acquire` with network and ~GB of raw inputs; that is documented, but sizes and runtime are not.
  - `outputs/phase6-synthetic` must be regenerated (`make phase6-fixture`) before `make verify-phase6`; a stale output fails replay (F-02).

## C. UNKNOWN audit (summary; full table in [evidence-ledger.md](../evidence-ledger.md))

Development nodes (261 rows, the data the app embeds): UNKNOWN 562 fields.

| Class | Fields | Share | Cause |
|---|---:|---:|---|
| (i) avoidable: over-strict rule | 296 | 52.7% | 288: durum component suppressed (status F) although bounded by published province totals; 8: coordinate conflict that does not change the reporting region |
| (ii) irreducible with current open data | 261 | 46.4% | No open source documents installed fan / electrical capacity |
| (iii) correct and desirable | 5 | 0.9% | Source reports 0 t storage (Delisle) |

No class (i) item is an implementation bug: each follows the recorded method. Fixing them needs a method change, so they become proposals.

## D–G. Other findings

| ID | Finding | Severity | Fix in Pass 2 |
|---|---|---|---|
| F-01 | Earlier-session changes put new code in `src/enagis` and a new file in `configs/`, breaking the Phase 8 "no scientific source change" criterion; a new diagnostic result was displayed in the app without approval | High | Move to `scripts/` and `docs/proposals/`; remove from app pending approval |
| F-02 | Stale local `outputs/phase6-synthetic` fails replay | Low | Regenerate the synthetic fixture; document the order |
| F-03 | Clean-room blocked on this host by Application Control | Info | Document workaround; rely on CI for clean runner |
| F-04 | No LICENSE file (GitHub `license: null`) although evidence metadata states "scenario/code MIT" | High | Add MIT LICENSE consistent with recorded metadata; data licences separately |
| F-05 | README is a phase log, no 30-second explainer, screenshot, badges or three-command quick start | High | Rewrite README; preserve history in `docs/project-history.md` |
| F-06 | Missing: overview, data catalogue, validation, limitations page in docs, evidence ledger, reproducibility, scaling, architecture page, glossary, judge FAQ, CONTRIBUTING, CODE_OF_CONDUCT, CITATION.cff, CHANGELOG, AI-use disclosure, roadmap | High | Create |
| F-07 | No issue or PR templates; no drafted good-first-issue / data-wanted issues | Medium | Create templates and drafts |
| F-08 | Makefile targets are not documented in one place | Low | Document in CONTRIBUTING and reproducibility |
| F-09 | Phase 8 audit records the app manifest hash of `63579eb`; any front-end fix changes it | Info | Keep the record unchanged; record the new manifest hash in `changes.md` |
| F-10 | No secrets, phone numbers, private verification data or restricted files found in history | — | none |

Documentation suite check (F) before: **adequate 0, partial 11, missing 11** (22 items). See the
re-audit section of [changes.md](changes.md) for the item-by-item before/after table.
