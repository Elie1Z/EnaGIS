.PHONY: setup test lint check smoke
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
