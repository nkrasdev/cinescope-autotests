PYTEST_API = uv run pytest tests/api -m "not ui"
PYTEST_UI = uv run pytest tests/ui -m "ui"

.PHONY: lint format test test-api test-ui

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

test: test-api

test-api:
	$(PYTEST_API)

test-ui:
	$(PYTEST_UI)
