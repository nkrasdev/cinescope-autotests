# Cinescope Autotests

[![CI](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml/badge.svg)](https://github.com/nkrasdev/cinescope-autotests/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-000000?logo=ruff)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/type%20checked-ty-blue)](https://docs.astral.sh/ty/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)

Автотесты API и UI для сервиса Cinescope.

Проект ориентирован на воспроизводимый запуск в локальной среде и в CI: линтинг, проверка типов, security-проверки, отчёты покрытия и Allure-артефакты.

## Содержание

- [Технологии](#технологии)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Запуск тестов](#запуск-тестов)
- [Проверки качества](#проверки-качества)
- [Allure и отчёты](#allure-и-отчёты)
- [CI Pipeline](#ci-pipeline)
- [Структура проекта](#структура-проекта)
- [Документация](#документация)

## Технологии

- `pytest` — test runner
- `pytest-playwright` — UI тесты
- `requests` — HTTP-клиент
- `pydantic` / `pydantic-settings` — валидация и конфигурация
- `ruff` — линтинг и форматирование
- `ty` — статическая типизация
- `bandit` — security checks
- `pytest-cov` / `pytest-xdist` — coverage и параллельный запуск
- `pre-commit` — локальные хуки качества

## Требования

- Python `3.13+`
- `uv`
- Node.js (только для локального просмотра Allure отчёта)

## Быстрый старт

### 1. Установка зависимостей

```bash
make install
# или
uv sync --dev
```

### 2. Настройка окружения

```bash
cp .env.example .env
```

Минимальные переменные в `.env`:

- `BASE_URL`
- `BASE_UI_URL`
- `BASE_AUTH_URL`
- `BASE_PAYMENT_URL`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

### 3. Установка pre-commit хуков

```bash
make pre-commit-install
```

### 4. (Опционально) установка браузера для UI

```bash
make install-playwright
```

## Запуск тестов

### API

```bash
make test-api
```

### UI

```bash
make test-ui
```

### Все тесты

```bash
make test-all
```

### Smoke

```bash
make test-smoke
```

### Параллельный запуск API

```bash
make test-parallel
```

### Покрытие

```bash
make test-cov
make test-cov-ui
```

## Проверки качества

```bash
make lint           # ruff check
make format         # ruff format
make format-check   # ruff format --check
make type-check     # ty check
make security       # bandit
make check-all      # lint + format-check + type-check + security
```

Запуск всех pre-commit хуков вручную:

```bash
make pre-commit-run
# или
uv run pre-commit run --all-files
```

Локальный прогон, приближенный к CI:

```bash
make ci-local
```

## Allure и отчёты

Тесты пишут результаты в `allure-results/`.

Локальный просмотр:

```bash
allure serve allure-results
# или
npx allure serve allure-results
```

Coverage-отчёты:

- `htmlcov/index.html`
- `coverage.xml`

## CI Pipeline

GitHub Actions (`.github/workflows/ci.yml`) запускает:

1. `Lint & Format Check`
2. `Type Checking (ty)`
3. `Security Check (bandit)`
4. `API Tests` (с coverage)
5. `UI Tests`

Особенности:

- API/UI тесты пропускаются, если отсутствуют нужные secrets
- Allure результаты и артефакты логов/скриншотов сохраняются как artifacts

## Структура проекта

```text
.
├── tests/
│   ├── api/                # API тесты
│   ├── ui/                 # UI тесты и Page Object Model
│   ├── clients/            # API-клиенты
│   ├── models/             # Pydantic модели
│   ├── request/            # HTTP/request layer
│   ├── utils/              # утилиты и генераторы данных
│   └── conftest.py         # фикстуры и pytest hooks
├── .github/workflows/ci.yml
├── pyproject.toml
├── Makefile
└── README.md
```

## Документация

- Архитектура: [ARCHITECTURE.md](ARCHITECTURE.md)
- Рекомендации: [BEST_PRACTICES.md](BEST_PRACTICES.md)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
