# EnaGIS repository instructions

- Read `docs/reference/prd-2026-10-04.md`, `design.md`, `docs/spec/phase0-interfaces.md` and relevant decisions before changing scientific behavior. The original UI concept is in `docs/reference/design-original.md`.
- Phase 0 is complete; decision 0003 freezes non-durum wheat storage/aeration at Canadian Prairie primary elevators, with AB/SK development and MB transfer hold-out. Do not reopen the scope without a concrete contradiction and a new decision record. The user's global direction is in decision 0002.
- `configs/pilot-scope.json` is scope metadata, not a runtime scientific parameter file. Unknown parameters and verification commitments remain explicit execution gates in `docs/phase-0-completion.md`.
- New regions enter through source adapters and region configuration. Evaluate transfer using untouched spatial blocks and report local data coverage; do not claim worldwide accuracy from a single pilot.
- Preserve OBSERVED, PREDICTED, ESTIMATED, INFERRED and UNKNOWN, including source, date, licence and precision. Missing documentation is not evidence of absence.
- Specify units and CRS at interfaces. Check row counts after joins and conserve production through allocation. Keep seed and input hashes for reproducibility.
- Separate storage mass, mass flow, airflow and electrical power. CGC deliveries are by shipping point and published in kilotonnes; a point's volume must not be duplicated across its elevators.
- Siting features must come only from upstream, label-free sources. Never feed allocation, capacity, energy or gap outputs into the siting experiment.
- Put sourced and human-approved scientific parameters, thresholds and scenario choices in versioned configuration. Code implements the recorded method; it does not silently choose scientific assumptions.
- Build offline from pinned, licence-compatible inputs. Keep private verification data outside public outputs.
