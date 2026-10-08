# Phase 4 preparation and execution

Read the [approved v1.1 protocol](phase4-preregistration.md) and [status](../phase-4-status.md).
Scientific execution is gated; there is deliberately no `--allow-temporary` bypass for Phase 4.

## Prepare sources without fitting

Install the locked environment once. A clean rebuild can acquire the existing pinned sources;
the v1.1 execution uses already acquired files and introduces no new source:

```sh
uv sync --locked --cache-dir .uv-cache
uv run --offline --locked --cache-dir .uv-cache python -m enagis acquire --manifest docs/data/phase4-manifest.json
uv run --offline --locked --cache-dir .uv-cache python -m enagis prepare-experiment --preparation data/processed/phase4-v1.1
```

Acquisition requires internet only for absent files. Preparation itself is offline, requires the
Phase 2 spine, and writes `data/processed/phase4-v1.1`: typed units/labels, production, source geography,
population crosswalk, source manifest, audit and hashed index. It does not compute real baseline
scores, fit models or compare outcomes. The earlier v1 preparation is preserved separately.

## Approved registration and evaluation

The actual user approval is recorded in `configs/experiments/phase4-canada-v1.1.json`. The
counts-only primary gate passed at 60 positive CCS in seven CARs; the frozen-values script and
127 tests plus lint/format passed. The method is committed and remotely registered at
`948cf2fddbb5a9f093883dd06b1a58a1d5a905fe`. These commands document the sequence already used;
**do not rerun registration or overwrite its record**:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis prepare-experiment --preparation data/processed/phase4-v1.1
# Commit reviewed configuration, protocol, code and lockfile before the next command.
uv run --offline --locked --cache-dir .uv-cache python -m enagis register-experiment --preparation data/processed/phase4-v1.1 --publish
uv run --offline --locked --cache-dir .uv-cache python -m enagis evaluate-experiment --preparation data/processed/phase4-v1.1
uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-experiment outputs/phase4
```

The registration publishes tag `preregister-phase4-canada-v1.1` to the configured remote and writes
`data/manual/phase4-preregistration.json`. Preserve/commit that record. Registration also pins
the existing Phase 3 output index; do not rerun Phase 3 between registration and evaluation.
The runner checks hashes before any outcome analysis. A tag or config/code/input change is an
error; do not repair it by overwriting the registration. The conditional run requires stopping
on an evaluation/verification error after registration, preserving the registered method.

Evaluation reads only AB/SK road extracts and can take substantial memory/time for the real
national road topology. It produces features, out-of-fold predictions, fitted fold parameters,
shipping-point groups, a report, protocol snapshot and index under `outputs/phase4`. If source
coverage fails the preregistered siting gate, prediction/fold lists are empty and the report
records `not_testable`; the independent hindcast still reports its available diagnostics.

No final all-development fit or Manitoba scoring occurs. Siting features cannot consume Phase 3
outputs: those are opened only in the separate hindcast branch after feature construction.
Exports retain OSM attribution/ODbL and the population/source licences. Local data and outputs
are ignored by Git and need preservation separately from the source repository.

## Tests and checks

```sh
uv run --offline --locked --cache-dir .uv-cache python -m pytest
uv run --offline --locked --cache-dir .uv-cache python -m ruff check .
uv run --offline --locked --cache-dir .uv-cache python -m ruff format --check .
```

`tests/test_experiment.py` uses explicitly synthetic approval metadata in temporary fixtures,
including a temporary Git repository. Those test approvals authorize no real scientific run.
Tests and CI require no national downloads. The population parser preserves repeated header
symbols, missing components and complete geometry joins; the common cohort excludes unknowns
rather than silently imputing zero. See the protocol for estimands, units and statistical limits.
