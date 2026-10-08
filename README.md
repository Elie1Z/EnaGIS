# EnaGIS

EnaGIS helps productive-use-energy teams decide which agricultural aggregation and processing locations to investigate first, and how confident to be in those choices. It is a screening shortlist for phone checks and site visits, not a feasibility study.

## Project state

**Phase 6 engineering is implemented; scientific completion remains gated.** The new
`enagis.science` engine covers directed mode/season routing, shared capacity, aeration ranges,
joint Sobol draws, stability tiers, top-10 exports and replay verification. Its demonstrated
end-to-end run is **synthetic**, not a replacement for the real demo. The real-data audit found
six outstanding scientific decisions. See the [Phase 6 status](docs/phase-6-status.md),
[review packet](docs/phase6-scientific-review.md) and [execution guide](docs/spec/phase6-science.md).
The final ranking has not been frozen.

**Phase 5 is complete:** open [the offline demo](demo/index.html) and click **Start guided demo**.
It presents ten real pipeline sites, a question-led node card, source/assumption traces and the
recorded baseline comparison. No sign-in, internet or runtime server is needed; keep the folder
together. The [demo guide](docs/phase-5-demo-guide.md) includes a three-minute presentation and
rebuild instructions. See [Phase 5 completion](docs/phase-5-completion.md) for verification and limits.

**Phase 4 is complete:** the approved v1.1 comparison was remotely registered, executed and verified. Its verdict is KILL / no demonstrated improvement from this proxy-based accessible-production feature. See the [completion report](docs/phase-4-completion.md) for all arms, uncertainty, hindcast and limitations.

**Phases 0–3 are complete at their recorded boundaries.** The development benchmark is non-durum wheat storage and electricity for ambient-air aeration at Canadian Prairie primary elevators. Alberta and Saskatchewan are the development footprint; Manitoba is reserved for transfer evaluation. The [benchmark lock](docs/decisions/0003-benchmark-lock.md), [architecture](design.md), [interfaces](docs/spec/phase0-interfaces.md) and [Phase 0 audit](docs/phase-0-completion.md) define scope. The [Phase 1 audit](docs/phase-1-completion.md) records the foundation; [Phase 2](docs/phase-2-completion.md) records normalized real inputs; [Phase 3](docs/phase-3-completion.md) records the complete pipeline and a real-data **temporary engineering shortlist**. Scientific use still requires human-reviewed parameters/methods and the recorded data/verification gates.

The user permits a pilot anywhere in the world, with adaptation through regional adapters/configuration: see [decision 0002](docs/decisions/0002-global-transfer.md). The benchmark follows the PRD best-candidate fallback. Its public inputs support the walking skeleton and completed spatial siting comparison; validated commercial energy parameters, field verification and measured transfer remain explicit gates.

The final consolidated project description and the supplied UI concept are retained verbatim in `docs/reference/`. The PRD governs scientific scope, with the user's geographic change recorded in decisions 0002–0003. The UI concept is a design proposal to evaluate when building the map; it does not change scientific claims.

## Development

Use Python **3.12** and uv (tested with Python 3.12.14 / uv 0.12.5). Install once with internet access:

```sh
uv sync --locked --cache-dir .uv-cache
```

Then run the checks and tiny fixture offline:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m pytest
uv run --offline --locked --cache-dir .uv-cache python -m ruff check .
uv run --offline --locked --cache-dir .uv-cache python -m ruff format --check .
uv run --offline --locked --cache-dir .uv-cache python -m enagis smoke --fixture tests/fixtures/phase1.json
```

On systems with Make, `make setup` and `make check` run these same commands. Windows PowerShell can use the uv commands directly; Make is not required locally. The bundled desktop Python can be selected explicitly using `uv sync --python <absolute-python-path> --locked --cache-dir .uv-cache` if Windows' `python` command is a Store alias. Workspace-local uv/pytest caches avoid restricted temporary-directory problems.

### Rebuild the presentation offline

The demo includes permitted, verified historical evidence and generalized map context. After the
environment setup above, rebuild and verify without acquiring data or fitting any model:

```sh
uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py
uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py --verify
```

On systems with Make, use `make demo` and `make verify-demo`. CSV and GeoJSON shortlist exports,
per-site JSON traces, original run artifacts, licences and checksums accompany the presentation.
The separate OSM major-road derivative is ODbL; roads and reporting outlines are display context,
not driving-time catchments. The interface preserves the temporary energy scenario and Phase 4
KILL verdict. No field validation or Manitoba transfer result is claimed.

For downstream modules:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis validate path/to/bundle.json
uv run --offline --locked --cache-dir .uv-cache python -m enagis schema --output docs/spec/phase1-bundle.schema.json
```

Read [executable contracts](docs/spec/phase1-contracts.md), the [JSON schema](docs/spec/phase1-bundle.schema.json), and [worked fixtures](tests/fixtures/README.md). Phase 1 commands validate supplied contract fixtures; the Phase 3 `run` command below executes allocation and fan calculations. GitHub Actions installs the lockfile, then runs `make check` including an offline pipeline fixture without national datasets.

## Pilot data spine

Prepare pinned open inputs once, then rebuild offline:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis acquire --skip-licensing
uv run --offline --locked --cache-dir .uv-cache python -m enagis ingest --skip-licensing
uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-data data/processed/phase2
```

See [ingestion instructions](docs/spec/phase2-ingestion.md), [manifest](docs/data/manifest.json), [licence audit](docs/data/licence-audit.md) and [source interpretation](docs/decisions/0004-source-normalization.md). The data spine covers registry/candidates/storage, full digital boundaries, production reporting regions, partitioned shipping-point outcomes, road source ways and quality audits. Original values and UNKNOWN states remain explicit. OSM derivatives retain ODbL; restricted licensing rows stay in private audit outputs. Raw files and large derived datasets are ignored by Git and must be prepared/preserved separately.

## First complete pipeline

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis run --allow-temporary-scenario
uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-run outputs/phase3
uv run --offline --locked --cache-dir .uv-cache python -m enagis trace outputs/phase3 --node-id NODE_ID
```

The real development run retains 261 nodes, ranks 186 with known production and emits `outputs/phase3/engineering-shortlist.csv` with ten rows. It conserves the 11,918,640-tonne **known subset**; nine development origins stay UNKNOWN. Administrative assignment and fan duty are hypothetical, explicitly configured and unapproved for scientific use. Installed electrical supply is undocumented in the consumed storage registry, not proven absent. [Decision 0005](docs/decisions/0005-phase3-walking-skeleton.md) and the [pipeline guide](docs/spec/phase3-pipeline.md) explain formulas, provenance, traces and gates. Output artifacts are ignored by Git and rebuilt locally.

## Phase 4: completed comparison

**Approved v1.1 registered, executed and verified.** The [completion report](docs/phase-4-completion.md) records 155 complete CCS, 60 positives and seven positive CARs. Full-model top-20% recall is 35.71%, versus B0 39.76%; the margin interval is [−39.29, −0.71] percentage points. Verdict: **KILL / no demonstrated improvement from this proxy-based accessible-production feature**. With few CARs, report intervals descriptively; this is not evidence against road-catchment logic. Hindcast completed on 52 common shipping-point groups; absolute-volume accuracy remains unvalidated.

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-experiment outputs/phase4
```

The [approved protocol](docs/spec/phase4-preregistration.md), [registration](data/manual/phase4-preregistration.json), [machine audit](docs/audits/phase4-evaluation.json) and [execution guide](docs/spec/phase4-experiment.md) preserve the method and results. All 127 tests and lint/format passed; six real artifacts verified. The committed/tagged method preceded evaluation and was not retuned. Manitoba remains untouched. Allocation/capacity/energy/gap outputs cannot enter siting features. Scientific energy/routing/verification gates remain open; [pilot-scope.json](configs/pilot-scope.json) remains scope metadata.

Code will be developed with AI assistance under human specifications, scientific decisions and review, following the PRD protocol.
