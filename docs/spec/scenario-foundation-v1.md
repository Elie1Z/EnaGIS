# Scenario foundation v1

Implementation contract, 6 November 2026. This is the next engine milestone, not a claim of worldwide analytical coverage.

## Compatibility boundary

Separate the existing commodity properties, process equations and recipe records. Keep `EnaConfig.MODELS` as a compiled compatibility view for existing callers. Preserve parameter iteration order, formulas, defaults, units, seeds and draws. Keep the configuration factory self-contained so workers and offline reproduction load the same definitions.

Before refactoring, capture full-result SHA-256 values for all four scenarios on the existing synthetic fixture (elapsed time normalised). Do not regenerate these expectations to accommodate a change. The Nyabihu reproduction manifest and frozen Rwanda/Canada artifacts remain unchanged.

## Registry contract

Commodities describe named material properties. Processes own equations, required parameter units and output boundaries. Recipes explicitly connect a commodity, process, operating assumptions and eligible site types. Only declared compatible recipes resolve. Unknown identifiers, unsupported combinations and incompatible registry versions fail before calculation.

The four existing recipes are labelled legacy screening assumptions, not independently reviewed parameter sets. A new recipe needs sourced parameter evidence and review metadata. Refactoring must not relabel old assumptions as reviewed or invent citations. There is no unrestricted custom equation execution or automatic pairing of every crop and process.

## Production evidence

New manual entries carry a finite nonnegative value, declared unit (`kg/person/year`), source, source date, licence/reuse note and evidence label. Zero is valid; missing is not zero. OBSERVED describes a sourced report and does not mean independently verified. Legacy numeric-only manual entries can reproduce their numeric estimates but must be labelled INFERRED with missing provenance disclosed. Missing-source entries cannot silently borrow a country default.

Store production records in calculation options and saved analyses; show the evidence in the assumptions and sources views. Validate again inside the engine, including the worker path. Existing registered outcomes are not recomputed or rewritten.

## Siting scope

The shipped model's training setting is Rwanda. Outside that setting, or without an identified country, do not score cells or attach siting percentiles. Return an explicit `not_validated` state and explain it in the lens. This guard is independent of demand estimation and preserves ordinary geography and supported energy calculations. Being inside the training setting is not a new claim of independent local validation.

## Exit checks

1. All four pre-refactor full-result hashes match with unchanged legacy inputs.
2. Registered artifact verification and the frozen Nyabihu reproduction pass.
3. Unsupported recipe combinations, missing/invalid evidence and cross-region siting are tested.
4. Browser changes preserve data reuse, worker calculations, provenance save/reopen and the globe entry flow.
5. Run the repository's existing test, lint and smoke checks; record any actual blockers.

New country packs, new crop parameters, multi-scenario rankings, supply optimisation and pumping remain separate milestones with their own evidence/review requirements.
