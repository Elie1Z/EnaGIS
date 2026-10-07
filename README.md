# EnaGIS

EnaGIS helps productive-use-energy teams decide which agricultural aggregation and processing locations to investigate first, and how confident to be in those choices. It is a screening shortlist for phone checks and site visits, not a feasibility study.

## Project state

**Phases 0 and 1 are complete.** The first development benchmark is non-durum wheat storage and electricity for ambient-air aeration at Canadian Prairie primary elevators. Alberta and Saskatchewan are the development footprint; Manitoba is reserved for transfer evaluation. The [benchmark lock](docs/decisions/0003-benchmark-lock.md), [architecture](design.md), [interfaces](docs/spec/phase0-interfaces.md) and [Phase 0 audit](docs/phase-0-completion.md) define the scientific scope. The [Phase 1 audit](docs/phase-1-completion.md) records the executable foundation and checks.

The user permits a pilot anywhere in the world, with adaptation to new regions as the product direction: see [decision 0002](docs/decisions/0002-global-transfer.md). The first benchmark is selected under the PRD's best-candidate fallback. It has strong public facility/capacity/delivery sources; validated energy parameters and committed verification participation remain explicit later-phase gates. No scientific model or field validation has been completed.

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

For downstream modules:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis validate path/to/bundle.json
uv run --offline --locked --cache-dir .uv-cache python -m enagis schema --output docs/spec/phase1-bundle.schema.json
```

Read [executable contracts](docs/spec/phase1-contracts.md), the [JSON schema](docs/spec/phase1-bundle.schema.json), and [worked fixtures](tests/fixtures/README.md). The CLI validates contracts and supplied toy results; it does not execute allocation, physics, training or a real shortlist. GitHub Actions installs the lockfile, then runs `make check` on these fixtures without national datasets.

## Next step

**Phase 2: data spine, registry and provenance.** Pin source snapshots, audit licences and source integrity, implement source adapters and reviewed crosswalks, and preserve quality exceptions explicitly. [pilot-scope.json](configs/pilot-scope.json) remains scope metadata, not a scientific parameter configuration. Energy parameters, verification commitments and the other [execution gates](docs/phase-0-completion.md) remain unresolved until their assigned phases.

Code will be developed with AI assistance under human specifications, scientific decisions and review, following the PRD protocol.
