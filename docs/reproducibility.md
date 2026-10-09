# Reproducibility

## Levels

| Level | Needs | Time (measured 9 Oct 2026, Windows 11 laptop) | Command |
|---|---|---|---|
| 1 Open the app | Browser only | instant | open `app/index.html` |
| 2 Install + tests + lint + smoke | Python 3.12, uv 0.12.5, network once | install ~35 s; checks ~40 s | see below |
| 3 Rebuild + verify the app from committed evidence | Level 2 | ~30 s | `make mvp verify-mvp` |
| 4 Synthetic Phase 6 / Phase 7 runs | Level 2 | < 1 min each | `make phase6-fixture verify-phase6`, `make phase7-fixture` |
| 5 Real data spine and pipeline | Level 2 + network for `acquire`; ~1 GB raw inputs incl. OSM extracts | minutes, network-bound | `make acquire ingest verify-data pipeline verify-run` |
| 6 Siting experiment verification | Level 5 + `prepare-experiment` | minutes | `python -m enagis verify-experiment outputs/phase4` |

Hardware: any 64-bit laptop with 8 GB RAM. No GPU, no server, no API key.

## Clean rebuild

```sh
git clone https://github.com/Elie1Z/EnaGIS.git && cd EnaGIS
uv sync --locked --cache-dir .uv-cache               # network once
uv run --offline --locked --cache-dir .uv-cache python -m pytest
uv run --offline --locked --cache-dir .uv-cache python -m ruff check .
uv run --offline --locked --cache-dir .uv-cache python -m ruff format --check .
uv run --offline --locked --cache-dir .uv-cache python -m enagis smoke --fixture tests/fixtures/phase1.json
uv run --offline --locked --cache-dir .uv-cache python -m scripts.build_mvp --verify
node --test tests/test_view_model.cjs                 # optional, Node 22+
node scripts/demo_preflight.mjs                       # optional, needs Edge or Chrome
```

`make setup` and `make check` wrap the same commands. Windows does not need Make.

## Expected checksums

| Item | SHA-256 |
|---|---|
| `uv.lock` | `d0f5f2429926afb378d153e9f5597a139b8bb1aa5e80e509f4d58cc5ccf53d92` |
| Scientific source (`enagis.pipeline.code_hash()`) | `f2b1f09541c263a23c0e2a89798956ffc72070272e253b8eeab68d6b8bf4e978`, unchanged since Phase 8 |
| Phase 2 input index | `bf077b5fe497e31324035fdd02934fd2c82496d67370f3ae1220c116c37fe61d` |
| Phase 4 protocol | `ccb98f6b1f4f90d0e93335d27b9adc8887eca1e18a3069c8041a82cea61f763f` |
| `app/manifest.json` at Phase 8 (`63579eb`) | `d7c8c5549549a85cdc1efe3f27c80bc61296b03aef48ee47eb5e23e1775a07de` |
| `app/manifest.json` after this audit | see [audit/changes.md](audit/changes.md) |

Raw inputs are pinned by SHA-256 in [data/manifest.json](data/manifest.json) and listed in the
[data catalogue](data-catalogue.md). Seeds: Phase 4 `20261008`; stress proposal `20261009`.

## Known pitfalls

- **Stale outputs:** `outputs/` is ignored by Git. A synthetic Phase 6 output from older code
  fails replay ("replay requires the recorded code and lockfile"). Regenerate it with
  `make phase6-fixture` before `make verify-phase6`.
- **Windows Application Control** may block a freshly created `.venv\Scripts\python.exe`
  (os error 4551). Use an allowed interpreter (`uv sync --python <path>`) or the GitHub CI run.
- `uv sync` needs network once; afterwards every command runs with `--offline`.
- `make ingest` needs the raw files from `make acquire`; the CGC licensing PDFs are restricted
  and skipped with `--skip-licensing`.

## Independent evidence

- GitHub-hosted clean Ubuntu runner: CI green on `63579eb`
  (https://github.com/Elie1Z/EnaGIS/actions/runs/37861220385).
- Author clean-room from a fresh clone: 227 tests passed and the rebuilt `app/manifest.json` was
  byte-identical to the Phase 8 record ([audit-log](audit/audit-log.md), entry 4).
- **Not yet done:** a rebuild by a person who did not write the pipeline (PRD §10).
