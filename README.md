# Cinescope Autotests

[![CI](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml/badge.svg)](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-v3-brightgreen)](https://allurereport.org/docs/v3/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://pre-commit.com/)

Automated API/UI tests for the Cinescope service.

## Stack

- Python 3.13+
- pytest
- requests
- pydantic
- uv
- Allure Report v3

## Quickstart

```bash
uv sync
cp .env.example .env
```

Edit `.env` with your credentials and base URLs.

## Run Tests

```bash
uv run pytest
```

```bash
make test-api
make test-ui
```

## Allure Report v3

Install (global or local):

```bash
npm install -g allure
allure --version
```

```bash
npm install allure
npx allure --version
```

Generate and view report:

```bash
allure serve allure-results
```

```bash
npx allure serve allure-results
```
