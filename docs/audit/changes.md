# Pass 2 changes and Pass 3 re-audit (9 October 2026)

Rules followed: no scientific setting, registered protocol, config, hashed or registered file,
result or verdict was changed. No UNKNOWN was filled. Scientific changes went to
[docs/proposals/](../proposals/).

## Changes made

| Finding | Change | Files |
|---|---|---|
| F-01 | Stress diagnostic moved out of the scientific source; `src/enagis/cli.py` restored to HEAD; protocol moved out of `configs/`; result removed from the app pending approval; report re-run so its code hash is the unchanged source (`f2b1f095…`; numbers identical) | `scripts/sparse_data_stress.py`, `docs/proposals/sparse-data-stress-*`, `tests/test_stress.py`, `scripts/build_mvp.py`, `web/mvp/app.js`, `tests/test_mvp.py`, `Makefile` |
| F-02 | Synthetic Phase 6 fixture regenerated in a fresh folder; replay verified (8 artifacts); pitfall documented | `outputs/phase6-synthetic-audit` (ignored), [reproducibility](../reproducibility.md) |
| F-03 | Host Application Control workaround documented; CI cited as clean-runner evidence | [reproducibility](../reproducibility.md) |
| F-04 | MIT LICENSE (matches the licence already recorded for EnaGIS-authored scenario values); separate data licence file | `LICENSE`, `LICENSE-DATA.md` |
| F-05 | README rewritten: 30-second explainer, three-command quick start, screenshot, badges, status table; old README preserved | `README.md`, `docs/project-history.md` |
| F-06 | 25 documents created (see table below, plus proof of work, challenger Q&A, project history) | `docs/*`, root files |
| F-07 | Issue templates (bug, data wanted, good first issue), PR template, 20 drafted issues | `.github/`, [draft-issues](draft-issues.md) |
| F-08 | Makefile targets documented | `CONTRIBUTING.md` |
| F-09 | Phase 8 record left unchanged; new app manifest hash recorded here | this file |
| Demo bug | Presenter guide pointed at a stress panel that is no longer shown; fixed to reference the team guide | `docs/phase8-presenter-guide.md`, `scripts/demo_preflight.mjs` |
| Tools | Read-only generators for the evidence ledger and data catalogue; preflight captures all lenses | `scripts/evidence_ledger.py`, `scripts/data_catalogue.py`, `docs/screenshots/` |

Front-end changes kept from the earlier session (permitted): brand, pin layout, status-bar
region name, "Tied ×N" badges. **App manifest:** `d7c8c554…` (Phase 8, `63579eb`) →
`ed6d360ae53f38f97aca929f96e73df5adc9e5d82b71b7a42d192f70c9830648` (this pass). The change is
front-end only; the embedded evidence JSON is the same data (evidence-ledger counts identical).

<details><summary>Removed app code, for restoration if the stress proposal is approved</summary>

Inserted in `web/mvp/app.js` `renderLens()` after the hindcast `</details>` and before
`}else html+=`, with a `data["stress"]` summary added in `scripts/build_mvp.py` from the report
JSON. Logic: show `checks.abstention_violations_total`, then rows for production loss 25% and
facility undocumented 10% / 25% with `retention_among_surviving` and `max_kw_inflation`, labelled
"Robustness diagnostic of the temporary scenario, not accuracy evidence". The full prior
version is in this conversation's history and is easy to rewrite from the report fields.
</details>

## Re-audit A: traceability matrix, before → after

| # | Requirement | Before | After | Why |
|---|---|---|---|---|
| O1 | ML/GeoAI pipeline | DONE (KILL) | DONE (KILL) | unchanged |
| O2 | Interactive map of clusters / gaps | PARTIAL | PARTIAL | Gap still UNKNOWN (no capacity data) |
| O3 | Documentation: datasets, approach, validation, accuracy, scaling | PARTIAL | **DONE** | data catalogue, method, validation, scaling, scope and transfer |
| C1 | Open registry | DONE | DONE | |
| C2 | Siting experiment | DONE | DONE | |
| C3 | Hindcast | DONE | DONE | |
| C4 | Capacity-constrained catchment allocation | PARTIAL | PARTIAL | science unchanged by rule |
| C5 | Energy with ranges | PARTIAL | PARTIAL | |
| C6 | Three supply states, gap buckets | PARTIAL | PARTIAL | |
| C7 | Monte Carlo tiers | PARTIAL | PARTIAL | |
| C8 | Baselines incl. expert | PARTIAL | PARTIAL | expert shortlist missing |
| C9 | Wet/dry, peak/off-peak, visit window | MISSING | MISSING | |
| C10 | Frozen verification n ≥ 12 | MISSING | MISSING | n = 0 |
| C11 | Decisive top 10 + checklist | PARTIAL | PARTIAL | ties now visible; confidence UNKNOWN |
| C12 | Map, node card, shortlist file | DONE | DONE | |
| C13 | Clean-machine rebuild, manifest, CI, limitations | PARTIAL | PARTIAL | independent person rebuild still missing |
| **Totals** | | **5 / 9 / 2** | **6 / 8 / 2** | DONE / PARTIAL / MISSING |

## Re-audit F: documentation suite, before → after

| Item | Before | After |
|---|---|---|
| README (explainer, 3-command start, screenshot, badges) | partial | adequate |
| docs/overview | missing | [adequate](../overview.md) |
| docs/method (one page + deep dive) | partial (method report only) | [adequate](../method.md) |
| docs/data-catalogue | partial (JSON manifest) | [adequate, generated](../data-catalogue.md) |
| docs/validation | partial (phase report) | [adequate](../validation.md) |
| docs/limitations and non-claims | partial (in app) | [adequate](../limitations.md) |
| docs/evidence-ledger | missing | [adequate](../evidence-ledger.md) |
| docs/reproducibility | partial (README) | [adequate](../reproducibility.md) |
| docs/scaling | partial (decision 0002) | [adequate](../scaling.md) |
| docs/architecture diagram | partial (text in design.md) | [adequate, Mermaid](../architecture.md) |
| docs/glossary | missing | [adequate](../glossary.md) |
| docs/faq-for-judges | partial (presenter guide) | [adequate](../faq-for-judges.md) |
| CONTRIBUTING.md | missing | adequate |
| CODE_OF_CONDUCT.md | missing | adequate (Contributor Covenant 2.1 by reference) |
| LICENSE (code + data, ODbL) | missing | adequate (`LICENSE`, `LICENSE-DATA.md`) |
| CITATION.cff | missing | adequate |
| CHANGELOG.md | missing | adequate |
| AI-use disclosure | partial (one README line) | [adequate](../ai-use.md) |
| Roadmap | partial (phase docs) | [adequate](../roadmap.md) |
| Team guide | missing | [adequate](../TEAM_GUIDE.md) |
| Scope and transfer | missing | [adequate](../scope-and-transfer.md) |
| Help wanted: data | missing | [adequate](../help-wanted-data.md) |
| **Totals (22 items)** | **0 adequate / 11 partial / 11 missing** | **22 adequate / 0 / 0** |

## Re-audit G: contributor experience

| Check | Result |
|---|---|
| Tiny example runs end to end in minutes | Yes: `make smoke`, `pytest tests/test_pipeline.py`, `make phase6-fixture verify-phase6` (< 1 min each) |
| Schemas documented | `docs/spec/phase1-bundle.schema.json`, `phase2-data.schema.json`, linked from architecture |
| Makefile targets documented | `CONTRIBUTING.md` |
| Issue / PR templates | 3 issue templates + PR template |
| ≥ 10 good-first-issue and data-wanted drafts | 10 + 10 in [draft-issues](draft-issues.md) (not opened: public action left to maintainer) |
| CI on clean runner | Green on `63579eb`; re-checked after push (see audit log) |
| Secrets, phone numbers, private data, large or restricted files | None found (audit log entry 7) |

Re-audit B (clean room on the pushed commit), test counts and push verification are recorded in
the [audit log](audit-log.md).
