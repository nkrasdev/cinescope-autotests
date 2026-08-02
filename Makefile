.PHONY: install install-playwright test-api test-ui test-all test-smoke test-parallel \
	test-cov test-cov-ui lint format format-check type-check security check-all \
	pre-commit-install pre-commit-run unit-tests ci-local

install:
	uv sync --dev

install-playwright:
	uv run playwright install chromium

test-api:
	uv run pytest tests/api -m "not ui" -n 4 --dist loadgroup

test-ui:
	uv run pytest tests/ui -m "ui" -n 2 --dist loadgroup

test-all:
	uv run pytest -n 4 --dist loadgroup

test-smoke:
	uv run pytest -m smoke -n 4 --dist loadgroup

test-parallel:
	uv run pytest tests/api -m "not ui" -n 4 --dist loadgroup

test-cov:
	uv run pytest tests/api -m "not ui" -n 4 --dist loadgroup --cov=tests --cov-report=term-missing --cov-report=html

test-cov-ui:
	uv run pytest tests/ui -m "ui" -n 2 --dist loadgroup --cov=tests --cov-report=term-missing --cov-report=html

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .
	uv run ruff format .

format-check:
	uv run ruff format --check .

type-check:
	uv run ty check

security:
	uv run bandit -c pyproject.toml -r tests

check-all: lint format-check type-check security

pre-commit-install:
	uv run pre-commit install

pre-commit-run:
	uv run pre-commit run --all-files

unit-tests:
	uv run pytest -n auto --dist loadgroup \
		tests/request tests/clients tests/models tests/utils tests/constants/test_payment_data_and_ui_data.py \
		tests/ui/test_auth_fallback.py tests/ui/test_base_page_utils.py tests/ui/test_payment_url_matching.py

ci-local: check-all unit-tests
