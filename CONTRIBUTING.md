# Contributing to EnaGIS

Thank you. The most valuable contributions are **data that turns an UNKNOWN into evidence**
([help-wanted-data](docs/help-wanted-data.md)), independent rebuilds, and careful reviews.
Code is welcome too.

## Set up (5 minutes)

```sh
git clone https://github.com/Elie1Z/EnaGIS.git && cd EnaGIS
uv sync --locked --cache-dir .uv-cache
make check            # or the uv commands in docs/reproducibility.md
```

Tiny end-to-end examples that run in under a minute, without national data:

| Command | What it runs |
|---|---|
| `make smoke` | Contract validation on `tests/fixtures/phase1.json` (8 cases) |
| `pytest tests/test_pipeline.py` | Phase 2 → 3 pipeline on a 3-node real-shaped fixture |
| `make phase6-fixture verify-phase6` | Phase 6 engine on synthetic inputs, then replay |
| `make phase7-fixture` | Synthetic verification rehearsal |
| `make mvp verify-mvp` | Rebuild and verify the app from committed evidence |
| `make preflight` | Drive the demo path in headless Edge/Chrome (Node 22+) |

## Makefile targets

`setup` install · `check` = `lint` + `test` + `smoke` · `acquire` / `ingest` / `verify-data`
real data spine (network for acquire) · `pipeline` / `verify-run` Phase 3 · `prepare-experiment`
Phase 4 inputs · `demo` / `verify-demo` historical Phase 5 archive · `phase6-audit`,
`phase6-fixture`, `verify-phase6` · `phase7-fixture` · `mvp`, `verify-mvp`, `figures`, `release`
app and defense archive · `stress` unapproved sparse-data diagnostic · `preflight` demo check.

## Rules (from [AGENTS.md](AGENTS.md); PRs that break them are not merged)

1. Every value keeps an evidence label with source, date, licence and precision. **Never fill
   UNKNOWN** with a default, mean, zero or guess.
2. Declare units and CRS at interfaces. Assert row counts after joins. Conserve production.
3. Keep storage mass, mass flow, airflow and electrical power as separate quantities.
4. Siting features only from upstream, label-free sources.
5. Scientific parameters and thresholds go in versioned config **with human approval**. Propose
   changes in `docs/proposals/<name>.md`.
6. Do not modify registered or hashed artifacts (`demo/evidence/`, `docs/audits/`,
   `data/manual/phase4-preregistration.json`, configs under a registration).
7. No private verification data, personal data or restricted sources in the repository.
8. Tests must not be weakened. Add a test with every behaviour change.

## Pull requests

Use the PR template. Run `make check` (and `node --test tests/test_view_model.cjs` for UI
changes). Say what evidence label your change affects. One topic per PR.

## Good first issues

Drafts are in [docs/audit/draft-issues.md](docs/audit/draft-issues.md): documentation, tests,
UI accessibility, adapter examples. Labels: `good first issue`, `data wanted`.

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
