# Cinescope Autotests

[![CI](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml/badge.svg)](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-v3-brightgreen?logo=allure)](https://allurereport.org/docs/v3/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000?logo=ruff)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)

Automated API/UI tests for the Cinescope service with modern tooling and best practices.

## Features

- ✅ **Type-safe** with mypy and Pydantic
- ✅ **Code quality** with Ruff linter/formatter
- ✅ **Security checks** with Bandit
- ✅ **Coverage reports** with pytest-cov
- ✅ **Parallel execution** with pytest-xdist
- ✅ **Pre-commit hooks** for quality assurance
- ✅ **Allure Report v3** for beautiful test reporting
- ✅ **CI/CD ready** with GitHub Actions

## Stack

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-framework-0A0A0A?logo=pytest)](https://pytest.org/)
[![requests](https://img.shields.io/badge/requests-http-2CA5E0?logo=python)](https://requests.readthedocs.io/)
[![Pydantic](https://img.shields.io/badge/Pydantic-data-E92063?logo=pydantic)](https://docs.pydantic.dev/)
[![Playwright](https://img.shields.io/badge/Playwright-UI-2EAD33?logo=playwright)](https://playwright.dev/)
[![uv](https://img.shields.io/badge/uv-package%20manager-5C2D91?logo=rust)](https://github.com/astral-sh/uv)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-v3-1E90FF?logo=allure)](https://allurereport.org/docs/v3/)

### Development Tools

- **Ruff** - Fast Python linter and formatter
- **mypy** - Static type checker
- **Bandit** - Security vulnerability scanner
- **pytest-cov** - Code coverage measurement
- **pytest-xdist** - Parallel test execution
- **pre-commit** - Git hooks for code quality

## Quickstart

### 1. Install dependencies

```bash
make install
# or
uv sync --dev
```

### 2. Setup environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Install pre-commit hooks (optional but recommended)

```bash
make pre-commit-install
```

### 4. Run tests

```bash
make test-api        # Run API tests
make test-ui         # Run UI tests
make test-cov        # Run tests with coverage
make test-parallel   # Run tests in parallel
```

## Available Commands

Run `make help` to see all available commands:

```bash
make help
```

### Development Commands

```bash
make install           # Install dependencies
make format            # Format code with Ruff
make lint              # Run linting checks
make type-check        # Run type checking with mypy
make security          # Run security checks with Bandit
make check-all         # Run all checks (lint, format, type-check, security)
```

### Testing Commands

```bash
make test              # Run API tests (default)
make test-api          # Run API tests
make test-ui           # Run UI tests
make test-all          # Run all tests
make test-cov          # Run tests with coverage report
make test-parallel     # Run tests in parallel
make test-smoke        # Run smoke tests only
```

### Utility Commands

```bash
make clean             # Clean up generated files
make ci-local          # Run CI checks locally
make pre-commit-run    # Run pre-commit on all files
```

## Project Structure

```
cinescope-autotests/
├── tests/
│   ├── api/              # API tests
│   ├── ui/               # UI tests with Page Object Model
│   ├── clients/          # API clients
│   ├── models/           # Pydantic models
│   ├── constants/        # Constants and endpoints
│   ├── utils/            # Utilities and helpers
│   └── conftest.py       # Pytest fixtures
├── .github/workflows/    # CI/CD configuration
├── ARCHITECTURE.md       # Architecture documentation
├── CONTRIBUTING.md       # Contribution guidelines
└── pyproject.toml        # Project configuration
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## Allure Report v3

### Install Allure

**Global installation:**
```bash
npm install -g allure
allure --version
```

**Local installation:**
```bash
npm install allure
npx allure --version
```

### Generate and view report

```bash
# After running tests
allure serve allure-results
# or
npx allure serve allure-results
```

### CI Artifacts

Allure results are automatically uploaded as artifacts in CI and can be downloaded from GitHub Actions.

## Coverage Reports

Coverage reports are generated automatically when running:

```bash
make test-cov
```

Reports are available in:
- Terminal output (summary)
- `htmlcov/index.html` (detailed HTML report)
- `coverage.xml` (for CI integration)

## Type Checking

This project uses mypy for static type checking:

```bash
make type-check
```

Type hints are enforced for:
- All API clients
- All models
- Test utilities

## Security

Security checks are performed using Bandit:

```bash
make security
```

Pre-commit hooks automatically check for:
- Private keys in code
- Known security vulnerabilities
- Insecure code patterns

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch
3. Install dependencies and pre-commit hooks
   ```bash
   make install
   make pre-commit-install
   ```
4. Make your changes
5. Run checks locally
   ```bash
   make ci-local
   ```
6. Submit a Pull Request

## CI/CD

The project uses GitHub Actions for continuous integration with the following jobs:

1. **Lint & Format Check** - Ruff code quality checks
2. **Type Checking** - mypy static type analysis
3. **Security Check** - Bandit vulnerability scanning
4. **API Tests** - Run tests with coverage reporting

All checks must pass before merging.

## Requirements

- Python 3.13+
- Node.js (for Allure Report)
- uv package manager

## License

This project is for internal testing purposes.

## Support

For questions or issues, please create an issue on GitHub.
