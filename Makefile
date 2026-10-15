.PHONY: research-njombe scout-sites research-xgb hero-repro hero-geojson hero-build hero-verification live-test live-e2e live-siting setup test lint check smoke acquire ingest verify-data pipeline verify-run stress prepare-experiment demo verify-demo phase6-audit phase6-fixture verify-phase6 phase7-fixture mvp verify-mvp figures release preflight
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
live-test:
	node --test tests/live/engine.test.cjs tests/live/overture.test.cjs tests/live/siting.test.cjs tests/live/hero.test.cjs tests/live/scouting.test.mjs tests/live/phase4n.test.mjs
live-e2e:
	node tests/live/e2e.cjs outputs/live-e2e
	node scripts/demo_preflight_live.mjs outputs/demo-preflight-live
hero-repro:
	node live/tools/hero-repro.cjs
	node live/tools/export-hero-geojson.cjs --check
hero-geojson:
	node live/tools/export-hero-geojson.cjs
hero-build:
	node live/tools/hero-assumptions.cjs
	node live/tools/build-hero.cjs
hero-verification:
	node live/tools/check-hero-verification.cjs
live-siting:
	node live/tools/verify-siting.cjs
research-xgb:
	uv run --offline --locked --cache-dir .uv-cache --group research python -m research.phase4x.run
scout-sites:
	node scripts/scout-sites.mjs --offline
research-njombe:
	node research/phase4n/gather.mjs
	uv run --offline --locked --cache-dir .uv-cache --group research python -m research.phase4n.run
