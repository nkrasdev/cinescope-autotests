PYTEST_API = uv run pytest tests/api -m "not ui"
PYTEST_UI = uv run pytest tests/ui -m "ui"
PYTEST_ALL = uv run pytest

.PHONY: help install install-playwright lint format type-check security test test-api test-ui test-cov test-parallel clean pre-commit-install pre-commit-run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	uv sync --dev

install-playwright: ## Install Playwright browser binaries (chromium)
	uv run playwright install chromium

lint: ## Run linting checks (ruff)
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff format .

format-check: ## Check code formatting without changes
	uv run ruff format --check .

type-check: ## Run type checking with mypy
	uv run mypy tests --exclude tests/ui/

security: ## Run security checks with bandit
	uv run bandit -c pyproject.toml -r tests

test: test-api ## Run API tests (default)

test-api: ## Run API tests
	$(PYTEST_API)

test-ui: install-playwright ## Run UI tests
	$(PYTEST_UI)

test-all: ## Run all tests
	$(PYTEST_ALL)

test-cov: ## Run tests with coverage report
	$(PYTEST_API) --cov=tests --cov-report=html --cov-report=term

test-cov-ui: ## Run UI tests with coverage
	$(PYTEST_UI) --cov=tests --cov-report=html --cov-report=term

test-parallel: ## Run tests in parallel (requires pytest-xdist)
	$(PYTEST_API) -n auto

test-smoke: ## Run smoke tests only
	uv run pytest -m smoke

check-all: lint format-check type-check security ## Run all checks (lint, format, type-check, security)

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf allure-results
	rm -rf allure-report
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	uv run pre-commit run --all-files

ci-local: check-all test-cov ## Run CI checks locally
