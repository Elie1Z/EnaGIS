# Scenario foundation release

6 November 2026. Implements the engine-foundation milestone following the global globe entry. This is partial delivery of the broader global-exploration plan, not completion of its flexible builder or worldwide evidence coverage.

## Delivered

- Separate commodity properties, process equations and explicitly supported recipes. The existing four activities remain available through a compiled compatibility view; unsupported combinations and incompatible versions fail before calculation.
- New recipe definitions require review metadata and parameter evidence. Existing assumptions remain labelled legacy screening assumptions. Metadata requirements do not constitute scientific review or independent source verification.
- Manual production entries require a nonnegative value, unit, source, valid source date, evidence label and licence/reuse note. The current unit is kg/person/year. Zero is valid; unknown remains unknown. User-supplied evidence is explicitly not independently verified.
- Old numeric-only overrides retain their numerical behaviour and are labelled INFERRED with missing provenance. New evidence survives worker execution, saved-file reopening and exports.
- Saved analyses now use `enagis-live-package-v2` with recipe and registry versions. Version 1 files remain readable. Unsupported registry versions are rejected before replacing the active analysis.
- The shipped Rwanda siting model cannot score an identified foreign country or an unidentified country. Its lens explains the unavailable prediction; supported demand calculations remain separate. Rwanda membership is a training-scope guard, not proof of local validity everywhere within Rwanda.
- Manual production is cleared when changing location. Late search, data-gathering and calculation responses cannot overwrite a newer analysis.

## Historical compatibility

`live/js/config.js` and `live/js/engine.js` are hash-pinned historical artifacts. Both remain byte-for-byte identical to baseline commit `30071bf`. The current application loads `config-v2.js` and `engine-v2.js`; the worker uses the same configuration factory.

The reproduction tool verifies the unchanged historical manifest, checks current output against the original expected ranking, and compares the current and archived engines. Frozen protocols, evaluation artifacts, model coefficients and expected outputs were not changed to accommodate this upgrade.

## Verification

| Check | Result |
| --- | --- |
| Python suite | 240 passed |
| Node suite, including 17 new foundation tests | 65 passed |
| Main application browser regression | 40 passed |
| Globe arrival browser checks | 27 passed |
| Production evidence, saved-file and stale-request browser checks | 20 passed |
| Archived offline demonstration acceptance | 24 passed |
| Four pre-refactor complete-result hashes | All match; elapsed time normalised |
| Nyabihu reproduction | 23 original checksums pass; repeated current rankings match original expectations and archived engine |
| Frozen GeoJSON export | Matches current verification logs and frozen ranking |
| Registered siting artifact verifier | Passed; frozen Rwanda and Canada artifacts unchanged |
| Python smoke fixture | 8 cases passed |
| Tracked Python Ruff lint and format | Passed; 86 tracked Python files checked |
| Changed JavaScript syntax and Git whitespace | Passed |

Browser tests use controlled synthetic inputs or the archived offline package. They do not establish accuracy in new regions or guarantee current availability of public data services. Desktop and mobile evidence-form screenshots were inspected.

The unfiltered repository-wide Ruff command also visits the pre-existing untracked `enagis-film/` directory and fails on its Python lint/format issues. Those unrelated files were not edited. The initial sandboxed Python run could not create test temporary directories; rerunning with the required filesystem access passed all 240 tests. The old offline browser harness needed to dismiss the new rotating globe before checking map readiness and count the four enabled activities instead of the new placeholder. Its scientific assertions remain intact.

Local verification outputs are under `outputs/scenario-foundation/`, including the Python/Node logs, browser screenshots, saved-file round trip and `preflight/report.json`. They are generated artifacts rather than new scientific observations.

## Remaining work

1. Build separate activity, commodity and operation controls with explicit readiness and missing-input explanations; the visible activity selector still has four supported presets.
2. Add a reviewed known-site throughput input path. This release validates the existing per-person production path only.
3. Add reviewed commodity parameters and location adapters with their own evidence and benchmarks. No new country pack or crop dataset was acquired here.
4. Add comparable scenario results and, later, load/supply comparisons with explicit objectives and required inputs. No optimal energy technology claim is enabled.

The next implementation milestone is the flexible scenario-builder interface over these registries. Geographic search remains global; analytical support remains conditional on suitable data and an applicable recipe/model.

## Commits

All implementation commits use the repository identity **Elie Mugisha <mugishaelie160@gmail.com>**.

- `0a48c23` — contract and four legacy baselines.
- `f96489e` — commodity/process/recipe registry separation.
- `dd64827` — production provenance and zero/unknown distinction.
- `1cd074d` — siting training-scope guard.
- `2cb1ddd` — versioned current runtime; immutable historical files preserved.
- `bcb5bd2` — browser integration, stale-request protection and acceptance checks.
- This release note is committed separately after verification.

These commits are local. No remote push, Netlify publication or deployment was performed for this milestone.
