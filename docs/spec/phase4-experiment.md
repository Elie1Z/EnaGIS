# Phase 4 preparation and execution

Read the [protocol for human review](phase4-preregistration.md) and [status](../phase-4-status.md).
Scientific execution is gated; there is deliberately no `--allow-temporary` bypass for Phase 4.

## Prepare sources without fitting

Install the updated locked environment once, then acquire the two new pinned open inputs:

```sh
uv sync --locked --cache-dir .uv-cache
uv run --offline --locked --cache-dir .uv-cache python -m enagis acquire --manifest docs/data/phase4-manifest.json
uv run --offline --locked --cache-dir .uv-cache python -m enagis prepare-experiment
```

Acquisition requires internet only for absent files. Preparation itself is offline, requires the
Phase 2 spine, and writes `data/processed/phase4`: typed units/labels, production, source geography,
population crosswalk, source manifest, audit and hashed index. It does not compute real baseline
scores, fit models or compare outcomes. The draft is valid for source preparation only.

## After actual human approval

Record `status: approved`, the reviewer's identity/date and the actual approval evidence in
`configs/experiments/phase4-canada-v1.json`. Update the review document and decision status to
reflect the approval. Do not enter synthetic or inferred approval. If assumptions change, review
the whole protocol before execution. Reprepare, then commit implementation/protocol/lock before
registration:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis prepare-experiment
# Commit reviewed configuration, protocol, code and lockfile before the next command.
uv run --offline --locked --cache-dir .uv-cache python -m enagis register-experiment
uv run --offline --locked --cache-dir .uv-cache python -m enagis evaluate-experiment
uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-experiment outputs/phase4
```

The first registration creates local Git tag `preregister-phase4-canada-v1` and
`data/manual/phase4-preregistration.json`. Preserve/commit that record. Registration also pins
the existing Phase 3 output index; do not rerun Phase 3 between registration and evaluation.
The runner checks hashes before any outcome analysis. A tag or config/code/input change is an
error; do not repair it by overwriting the registration. Disclose the change and version a new
protocol and registration instead.

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
