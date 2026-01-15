# Cinescope Autotests

[![CI](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml/badge.svg)](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-v3-brightgreen?logo=allure)](https://allurereport.org/docs/v3/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000?logo=ruff)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)

Automated API/UI tests for the Cinescope service.

## Stack

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-framework-0A0A0A?logo=pytest)](https://pytest.org/)
[![requests](https://img.shields.io/badge/requests-http-2CA5E0?logo=python)](https://requests.readthedocs.io/)
[![Pydantic](https://img.shields.io/badge/Pydantic-data-E92063?logo=pydantic)](https://docs.pydantic.dev/)
[![uv](https://img.shields.io/badge/uv-package%20manager-5C2D91?logo=rust)](https://github.com/astral-sh/uv)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-v3-1E90FF?logo=allure)](https://allurereport.org/docs/v3/)
[![Node.js](https://img.shields.io/badge/Node.js-required-339933?logo=nodedotjs)](https://nodejs.org/)

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
