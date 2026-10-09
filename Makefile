.PHONY: setup test lint check smoke acquire ingest verify-data pipeline verify-run stress prepare-experiment demo verify-demo phase6-audit phase6-fixture verify-phase6 phase7-fixture mvp verify-mvp figures release preflight
setup:
	uv sync --locked --cache-dir .uv-cache
test:
	uv run --offline --locked --cache-dir .uv-cache python -m pytest
lint:
	uv run --offline --locked --cache-dir .uv-cache python -m ruff check .
	uv run --offline --locked --cache-dir .uv-cache python -m ruff format --check .
check: lint test smoke
smoke:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis smoke --fixture tests/fixtures/phase1.json
acquire:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis acquire --skip-licensing
ingest:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis ingest --skip-licensing
verify-data:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-data data/processed/phase2
pipeline:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis run --allow-temporary-scenario
verify-run:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-run outputs/phase3
stress:
	uv run --offline --locked --cache-dir .uv-cache python -m scripts.sparse_data_stress --allow-temporary-scenario
prepare-experiment:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis prepare-experiment
demo:
	uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py
verify-demo:
	uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py --verify
phase6-audit:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis.science audit
phase6-fixture:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis.science run --config tests/fixtures/phase6-synthetic-config.json --input tests/fixtures/phase6-synthetic-inputs.json --output outputs/phase6-synthetic --allow-fixture
verify-phase6:
	uv run --offline --locked --cache-dir .uv-cache python -m enagis.science verify outputs/phase6-synthetic
phase7-fixture:
	uv run --offline --locked --cache-dir .uv-cache python scripts/phase7_rehearsal.py --output outputs/phase7-rehearsal
mvp:
	uv run --offline --locked --cache-dir .uv-cache python -m scripts.build_mvp
verify-mvp:
	uv run --offline --locked --cache-dir .uv-cache python -m scripts.build_mvp --verify
figures:
	uv run --offline --locked --cache-dir .uv-cache python -m scripts.generate_figures
release:
	uv run --offline --locked --cache-dir .uv-cache python -m scripts.release_mvp --check
preflight:
	node scripts/demo_preflight.mjs app/index.html outputs/demo-preflight
